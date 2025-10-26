"""Entry point for the telemetry radar prototype."""

from __future__ import annotations

import inspect
import json
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.audio.beep_driver import BeepDriver, select_beep_driver
from src.hud import HUDController
from src.insim_client import (
    ISS_MULTI,
    ButtonClickEvent,
    InSimClient,
    InSimConfig,
    MultiCarInfoEvent,
    LapEvent,
    SplitEvent,
    StateEvent,
)
from src.outsim_client import OutSimClient, OutSimFrame
from src.persistence import PersonalBestRecord, load_personal_best, record_lap
from src.radar import RadarRenderer
from src.telemetry_ws import TelemetryBroadcaster

logger = logging.getLogger(__name__)


def clear_session_timing(lap_state: Dict[str, Any]) -> None:
    """Reset timing-related session fields in ``lap_state``."""

    lap_state["current_lap_start_ms"] = None
    lap_state["best_lap_ms"] = None
    lap_state["current_split_times"] = {}
    lap_state["last_lap_split_fractions"] = []
    lap_state["pb_split_fractions"] = []
    lap_state["latest_estimated_total_ms"] = None


def update_session_best(lap_state: Dict[str, Any], lap_time_ms: int) -> bool:
    """Update the session best lap time if ``lap_time_ms`` is an improvement."""

    if lap_time_ms <= 0:
        return False

    best_lap = lap_state.get("best_lap_ms")
    if best_lap is None or lap_time_ms < best_lap:
        lap_state["best_lap_ms"] = lap_time_ms
        return True

    return False


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@dataclass
class ModeConfig:
    radar_enabled: bool = True
    beeps_enabled: bool = True


@dataclass
class TelemetryConfig:
    enabled: bool = True
    host: str = "127.0.0.1"
    port: int = 30333
    update_hz: float = 15.0


@dataclass
class BeepConfig:
    mode: str = "standard"
    volume: float = 0.5
    base_frequency_hz: float = 880.0
    intervals_ms: List[int] = field(default_factory=lambda: [400])


@dataclass
class AppConfig:
    insim: InSimConfig
    outsim_port: int
    outsim_allowed_sources: Optional[List[str]]
    outsim_rate_limit: Optional[float]
    outsim_update_hz: Optional[float]
    beep: BeepConfig
    sp: ModeConfig
    mp: ModeConfig
    telemetry: TelemetryConfig

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "AppConfig":
        insim_cfg_raw = raw.get("insim", {})
        outsim_cfg_raw = raw.get("outsim", {})
        telemetry_raw = raw.get("telemetry_ws", {})

        insim_cfg = InSimConfig(
            host=insim_cfg_raw.get("host", "127.0.0.1"),
            port=int(insim_cfg_raw.get("port", 29999)),
            admin_password=insim_cfg_raw.get("admin_password", ""),
            interval_ms=int(insim_cfg_raw.get("interval_ms", 100)),
        )

        outsim_port = int(outsim_cfg_raw.get("port", 30000))
        allowed_sources_raw = outsim_cfg_raw.get("allowed_sources")
        outsim_allowed_sources: Optional[List[str]]
        if allowed_sources_raw is None:
            outsim_allowed_sources = None
        elif isinstance(allowed_sources_raw, str):
            outsim_allowed_sources = [allowed_sources_raw]
        else:
            outsim_allowed_sources = [str(value) for value in allowed_sources_raw]
        rate_limit_raw = outsim_cfg_raw.get("max_packets_per_second")
        outsim_rate_limit: Optional[float]
        if rate_limit_raw is None:
            outsim_rate_limit = None
        else:
            try:
                outsim_rate_limit = float(rate_limit_raw)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "OutSim max_packets_per_second must be a number"
                ) from exc
            if outsim_rate_limit <= 0:
                raise ValueError(
                    "OutSim max_packets_per_second must be greater than zero"
                )
        update_hz_raw = outsim_cfg_raw.get("update_hz")
        if update_hz_raw is None:
            outsim_update_hz: Optional[float] = None
        else:
            try:
                outsim_update_hz = float(update_hz_raw)
            except (TypeError, ValueError) as exc:
                raise ValueError("OutSim update_hz must be numeric") from exc
            if outsim_update_hz <= 0:
                raise ValueError("OutSim update_hz must be greater than zero")
        beep_raw = raw.get("beep", {})
        mode_value = str(beep_raw.get("mode", "standard"))
        volume_raw = beep_raw.get("volume", 0.5)
        try:
            volume_value = float(volume_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("Beep volume must be numeric") from exc
        if not 0.0 <= volume_value <= 1.0:
            raise ValueError("Beep volume must be within [0.0, 1.0]")

        base_frequency_raw = beep_raw.get("base_frequency_hz", 880.0)
        try:
            base_frequency_value = float(base_frequency_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("Beep base_frequency_hz must be numeric") from exc
        if base_frequency_value <= 0:
            raise ValueError("Beep base_frequency_hz must be greater than zero")

        intervals_raw = beep_raw.get("intervals_ms", [400])
        if not isinstance(intervals_raw, (list, tuple)):
            raise ValueError("Beep intervals_ms must be a list of positive integers")
        intervals: List[int] = []
        for entry in intervals_raw:
            try:
                interval_value = int(entry)
            except (TypeError, ValueError) as exc:
                raise ValueError("Beep intervals_ms must contain integers") from exc
            if interval_value <= 0:
                raise ValueError("Beep intervals_ms entries must be greater than zero")
            intervals.append(interval_value)
        if not intervals:
            raise ValueError("Beep intervals_ms must not be empty")
        beep_cfg = BeepConfig(
            mode=mode_value,
            volume=volume_value,
            base_frequency_hz=base_frequency_value,
            intervals_ms=intervals,
        )

        telemetry_enabled = bool(telemetry_raw.get("enabled", True))
        telemetry_host = str(telemetry_raw.get("host", "127.0.0.1"))
        telemetry_port = int(telemetry_raw.get("port", 30333))
        update_hz_raw = telemetry_raw.get("update_hz", 15.0)
        try:
            telemetry_update_hz = float(update_hz_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("Telemetry update_hz must be numeric") from exc
        if telemetry_update_hz <= 0:
            raise ValueError("Telemetry update_hz must be greater than zero")
        telemetry_cfg = TelemetryConfig(
            enabled=telemetry_enabled,
            host=telemetry_host,
            port=telemetry_port,
            update_hz=telemetry_update_hz,
        )

        sp_cfg = ModeConfig(
            radar_enabled=bool(raw.get("sp_radar_enabled", True)),
            beeps_enabled=bool(raw.get("sp_beeps_enabled", True)),
        )

        mp_cfg = ModeConfig(
            radar_enabled=bool(raw.get("mp_radar_enabled", True)),
            beeps_enabled=bool(raw.get("mp_beeps_enabled", False)),
        )

        return cls(
            insim=insim_cfg,
            outsim_port=outsim_port,
            outsim_allowed_sources=outsim_allowed_sources,
            outsim_rate_limit=outsim_rate_limit,
            outsim_update_hz=outsim_update_hz,
            beep=beep_cfg,
            sp=sp_cfg,
            mp=mp_cfg,
            telemetry=telemetry_cfg,
        )


class BeepSubsystem:
    """Generate audible beeps based on OutSim frames."""

    _MODE_SCALE = {"standard": 1.0, "calm": 0.75, "aggressive": 1.3}
    _DEFAULT_SCALE = 1.0

    def __init__(self, config: BeepConfig, driver: Optional[BeepDriver] = None) -> None:
        self._driver = driver or select_beep_driver()
        intervals = list(config.intervals_ms) or [400]
        self._config = BeepConfig(
            mode=config.mode,
            volume=config.volume,
            base_frequency_hz=config.base_frequency_hz,
            intervals_ms=list(intervals),
        )
        self._mode = config.mode
        self._enabled = False
        self._interval_pattern: List[int] = list(intervals)
        self._next_interval_index = 0
        self._next_beep_time_ms: Optional[int] = None
        try:
            self._driver.set_volume(self._config.volume)
            self._driver.set_enabled(False)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to initialise beep driver state")

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def mode(self) -> str:
        return self._mode

    def update_config(self, config: BeepConfig) -> None:
        if config == self._config:
            return

        intervals = list(config.intervals_ms) or [400]
        self._config = BeepConfig(
            mode=config.mode,
            volume=config.volume,
            base_frequency_hz=config.base_frequency_hz,
            intervals_ms=list(intervals),
        )
        self._interval_pattern = list(intervals)
        self._next_interval_index = 0
        self._next_beep_time_ms = None
        self.set_mode(config.mode)
        try:
            self._driver.set_volume(self._config.volume)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to apply beep configuration volume")

    def set_mode(self, mode: str) -> None:
        if mode == self._mode:
            return
        logger.info("Updating beep mode to %s", mode)
        self._mode = mode
        self._config.mode = mode
        try:
            self._driver.set_volume(self._config.volume)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to refresh beep driver volume when changing mode")

    def set_enabled(self, enabled: bool) -> None:
        if self._enabled == enabled:
            return

        self._enabled = enabled
        state = "enabled" if enabled else "disabled"
        logger.info("Beep subsystem %s (mode=%s)", state, self._mode)
        if not enabled:
            self._next_beep_time_ms = None
            self._next_interval_index = 0
        try:
            self._driver.set_enabled(enabled)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to update beep driver enabled state")

    def process_frame(self, frame: OutSimFrame) -> None:
        if not self._enabled:
            return
        if not self._interval_pattern:
            return

        current_time = frame.time_ms
        if self._next_beep_time_ms is None:
            self._next_beep_time_ms = current_time + self._interval_pattern[self._next_interval_index]
            return

        if current_time < self._next_beep_time_ms:
            return

        interval = self._interval_pattern[self._next_interval_index]
        duration = max(30, min(interval // 2, 250))
        frequency = self._calculate_frequency(frame)
        try:
            self._driver.play_beep(frequency, duration)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Beep driver raised an error during playback")

        self._next_interval_index = (self._next_interval_index + 1) % len(self._interval_pattern)
        next_interval = self._interval_pattern[self._next_interval_index]
        self._next_beep_time_ms = current_time + next_interval

    def _calculate_frequency(self, frame: OutSimFrame) -> float:
        speed = frame.speed
        scale = self._MODE_SCALE.get(self._mode, self._DEFAULT_SCALE)
        speed_factor = 1.0 + min(max(speed, 0.0) / 50.0, 2.0)
        return self._config.base_frequency_hz * scale * speed_factor


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")

    config_path = Path(__file__).resolve().parent / "config.json"
    config = AppConfig.from_dict(load_config(config_path))

    radar = RadarRenderer()
    beep_system = BeepSubsystem(config.beep)
    telemetry_server: Optional[TelemetryBroadcaster] = None
    active_telemetry_config: Optional[TelemetryConfig] = None

    def apply_telemetry_config(settings: TelemetryConfig) -> None:
        nonlocal telemetry_server, active_telemetry_config

        if active_telemetry_config == settings and telemetry_server is not None:
            return

        if telemetry_server is not None:
            telemetry_server.stop()
            telemetry_server = None

        if not settings.enabled:
            active_telemetry_config = settings
            return

        try:
            telemetry_server = TelemetryBroadcaster(
                settings.host, settings.port, update_hz=settings.update_hz
            )
        except Exception:  # pragma: no cover - defensive logging
            logger.exception(
                "Failed to initialise telemetry broadcaster on %s:%s",
                settings.host,
                settings.port,
            )
            active_telemetry_config = settings
            return

        telemetry_server.start()
        active_telemetry_config = TelemetryConfig(
            enabled=settings.enabled,
            host=settings.host,
            port=settings.port,
            update_hz=settings.update_hz,
        )

    apply_telemetry_config(config.telemetry)

    lap_state = {
        "current_lap_start_ms": None,  # type: Optional[int]
        "best_lap_ms": None,  # type: Optional[int]
        "current_split_times": {},  # type: Dict[int, int]
        "last_lap_split_fractions": [],  # type: List[float]
        "pb_split_fractions": [],  # type: List[float]
        "latest_estimated_total_ms": None,  # type: Optional[int]
    }
    tracked_plid: Optional[int] = None
    tracked_driver: Optional[str] = None
    current_track: Optional[str] = None
    current_car: Optional[str] = None
    persistent_best: Optional[PersonalBestRecord] = None
    last_frame_time_ms: Optional[int] = None
    pending_lap_start = False
    last_status_line: str = ""

    current_mode = "sp"
    mode_settings = {"sp": config.sp, "mp": config.mp}

    config_lock = threading.RLock()
    hud_controller: Optional[HUDController] = None

    def normalise_fractions(values: List[float]) -> List[float]:
        cleaned: List[float] = []
        last_value = 0.0
        for value in values:
            if value <= 0.0:
                continue
            clamped = max(last_value, min(value, 1.0))
            if clamped >= 1.0:
                break
            if clamped > last_value:
                cleaned.append(clamped)
                last_value = clamped
        return cleaned

    def resolve_reference_fractions() -> List[float]:
        fractions = lap_state.get("pb_split_fractions") or []
        if fractions:
            return normalise_fractions(list(fractions))

        fallback = lap_state.get("last_lap_split_fractions") or []
        if fallback:
            return normalise_fractions(list(fallback))

        current_splits: Dict[int, int] = lap_state.get("current_split_times", {})
        estimate = lap_state.get("latest_estimated_total_ms")
        if current_splits and estimate and estimate > 0:
            ordered = [current_splits[idx] for idx in sorted(current_splits)]
            derived = [split / estimate for split in ordered if split < estimate]
            return normalise_fractions(derived)

        return []

    def estimate_reference_time(current_ms: Optional[int]) -> Optional[int]:
        if current_ms is None:
            return None
        if persistent_best is None or persistent_best.laptime_ms <= 0:
            return None

        pb_total = persistent_best.laptime_ms

        def estimate_from_progress() -> Optional[int]:
            estimate_total = lap_state.get("latest_estimated_total_ms")
            if not estimate_total or estimate_total <= 0:
                return None

            progress = min(max(current_ms / estimate_total, 0.0), 1.0)
            reference_time = int(round(pb_total * progress))
            return min(reference_time, pb_total)

        fractions = resolve_reference_fractions()
        if not fractions:
            return estimate_from_progress()

        boundaries = fractions + [1.0]

        current_splits: Dict[int, int] = lap_state.get("current_split_times", {})
        sorted_split_times = [current_splits[idx] for idx in sorted(current_splits)]
        passed_split_times = [t for t in sorted_split_times if t <= current_ms]

        if not passed_split_times:
            return estimate_from_progress()

        segment_index = min(len(passed_split_times), len(boundaries) - 1)
        start_fraction = boundaries[segment_index - 1] if segment_index > 0 else 0.0
        end_fraction = boundaries[segment_index]

        pb_start = int(round(pb_total * start_fraction))
        pb_end = int(round(pb_total * end_fraction))
        pb_segment_duration = max(pb_end - pb_start, 1)

        segment_start_time = (
            passed_split_times[segment_index - 1]
            if segment_index > 0 and segment_index - 1 < len(passed_split_times)
            else 0
        )
        segment_elapsed = max(current_ms - segment_start_time, 0)
        progress_within_segment = min(segment_elapsed / pb_segment_duration, 1.0)
        reference_time = pb_start + int(round(progress_within_segment * pb_segment_duration))
        return min(reference_time, pb_total)

    def reset_split_tracking() -> None:
        lap_state["current_split_times"] = {}
        lap_state["latest_estimated_total_ms"] = None

    with config_lock:
        radar_enabled = mode_settings[current_mode].radar_enabled
        beep_system.set_enabled(mode_settings[current_mode].beeps_enabled)

    stop_event = threading.Event()

    def update_track_context(track: Optional[str], car: Optional[str]) -> None:
        nonlocal current_track, current_car, persistent_best, tracked_plid, tracked_driver
        nonlocal pending_lap_start, telemetry_server

        normalised_track = track.strip() if track else None
        normalised_car = car.strip() if car else None

        track_changed = bool(normalised_track and normalised_track != current_track)
        car_changed = bool(normalised_car and normalised_car != current_car)

        if track_changed:
            current_track = normalised_track
        if car_changed:
            current_car = normalised_car

        server = telemetry_server
        if server is not None:
            server.update_track_context(current_track, current_car)

        if track_changed or car_changed:
            tracked_plid = None
            tracked_driver = None
            clear_session_timing(lap_state)
            pending_lap_start = True
            if current_track and current_car:
                persistent_best = load_personal_best(current_track, current_car)
                reset_split_tracking()
                if persistent_best is None:
                    logger.info("No stored personal best for %s / %s", current_track, current_car)
                else:
                    logger.info(
                        "Loaded personal best for %s / %s: %s ms (recorded %s)",
                        current_track,
                        current_car,
                        persistent_best.laptime_ms,
                        persistent_best.recorded_at.isoformat(),
                    )

    def handle_state(event: StateEvent) -> None:
        nonlocal current_mode, radar_enabled, telemetry_server

        update_track_context(event.track, event.car)

        server = telemetry_server
        if server is not None:
            server.set_focus_plid(event.view_plid)

        new_mode = "mp" if event.flags2 & ISS_MULTI else "sp"
        if new_mode == current_mode:
            return

        with config_lock:
            current_mode = new_mode
            settings = mode_settings[new_mode]
            radar_enabled = settings.radar_enabled
            beep_system.set_enabled(settings.beeps_enabled)
            radar_state = radar_enabled
            beeps_state = beep_system.enabled

        logger.info(
            "Detected %splayer mode: radar=%s beeps=%s",
            "multi" if new_mode == "mp" else "single ",
            "on" if radar_state else "off",
            "on" if beeps_state else "off",
        )

        hud = hud_controller
        if hud is not None:
            hud.update(radar_state, beeps_state)

    def handle_lap(event: LapEvent) -> None:
        nonlocal tracked_plid, tracked_driver, last_frame_time_ms, pending_lap_start, persistent_best
        nonlocal telemetry_server

        update_track_context(event.track, event.car)

        if tracked_plid is None:
            tracked_plid = event.plid
            tracked_driver = event.player_name or f"PLID {event.plid}"
            logger.info("Tracking lap data for %s (PLID %s)", tracked_driver, event.plid)
            reset_split_tracking()
            lap_state["last_lap_split_fractions"] = []

        server = telemetry_server
        if server is not None and tracked_plid is not None:
            server.set_focus_plid(tracked_plid)

        if event.plid != tracked_plid:
            logger.debug(
                "Ignoring lap event for PLID %s while tracking %s",
                event.plid,
                tracked_plid,
            )
            return

        lap_time = event.lap_time_ms
        estimate_hint: Optional[int] = None
        if event.estimate_time_ms > 0:
            lap_state["latest_estimated_total_ms"] = event.estimate_time_ms
            if lap_time <= 0:
                estimate_hint = event.estimate_time_ms

        current_splits: Dict[int, int] = lap_state.get("current_split_times", {})
        sorted_indices = sorted(current_splits)
        split_times = [current_splits[idx] for idx in sorted_indices]

        if lap_time > 0:
            if update_session_best(lap_state, lap_time):
                logger.info("New session best lap: %s ms", lap_time)
            else:
                best_lap = lap_state.get("best_lap_ms")
                best_display = best_lap if best_lap is not None else "n/a"
                logger.info("Lap completed: %s ms (best %s ms)", lap_time, best_display)

            if split_times:
                fractions: List[float] = []
                last_fraction = 0.0
                for split_time in split_times:
                    if lap_time <= 0:
                        break
                    fraction = max(last_fraction, min(split_time / lap_time, 1.0))
                    if fraction >= 1.0:
                        break
                    if fraction > last_fraction:
                        fractions.append(fraction)
                        last_fraction = fraction
                lap_state["last_lap_split_fractions"] = fractions
            else:
                lap_state["last_lap_split_fractions"] = []

            if current_track and current_car:
                pb_record, improved = record_lap(current_track, current_car, lap_time)
                persistent_best = pb_record
                if improved:
                    logger.info(
                        "New personal best for %s / %s: %s ms (recorded %s)",
                        current_track,
                        current_car,
                        lap_time,
                        pb_record.recorded_at.isoformat(),
                    )
                    lap_state["pb_split_fractions"] = list(
                        lap_state.get("last_lap_split_fractions", [])
                    )
                elif (
                    lap_state.get("pb_split_fractions") in (None, [])
                    and persistent_best.laptime_ms == lap_time
                    and split_times
                ):
                    lap_state["pb_split_fractions"] = list(
                        lap_state.get("last_lap_split_fractions", [])
                    )

        if last_frame_time_ms is None:
            pending_lap_start = True
            logger.debug("Lap start timestamp unavailable; awaiting OutSim frame data")
        else:
            lap_state["current_lap_start_ms"] = last_frame_time_ms
            pending_lap_start = False

        reset_split_tracking()
        if estimate_hint is not None:
            lap_state["latest_estimated_total_ms"] = estimate_hint

    def watch_config() -> None:
        nonlocal config, mode_settings, radar_enabled, telemetry_server, active_telemetry_config
        nonlocal current_track, current_car

        try:
            last_mtime = config_path.stat().st_mtime_ns
        except FileNotFoundError:
            logger.warning("Configuration file %s not found; waiting for it to appear", config_path)
            last_mtime = None

        while not stop_event.wait(1.0):
            try:
                current_mtime = config_path.stat().st_mtime_ns
            except FileNotFoundError:
                if last_mtime is not None:
                    logger.warning(
                        "Configuration file %s missing; retaining previous settings", config_path
                    )
                    last_mtime = None
                continue

            if last_mtime is not None and current_mtime == last_mtime:
                continue

            last_mtime = current_mtime

            try:
                new_config = AppConfig.from_dict(load_config(config_path))
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Failed to reload configuration from %s", config_path)
                continue

            apply_telemetry_config(new_config.telemetry)
            server = telemetry_server
            if server is not None:
                server.update_track_context(current_track, current_car)

            with config_lock:
                config = new_config
                mode_settings = {"sp": config.sp, "mp": config.mp}
                beep_system.update_config(config.beep)
                mode_name = current_mode
                settings = mode_settings[mode_name]
                radar_enabled = settings.radar_enabled
                beep_system.set_enabled(settings.beeps_enabled)
                radar_state = radar_enabled
                beeps_state = beep_system.enabled
                beep_mode_state = beep_system.mode

            logger.info(
                "Reloaded configuration (mode=%s, radar=%s, beeps=%s, beep_mode=%s)",
                mode_name,
                "on" if radar_state else "off",
                "on" if beeps_state else "off",
                beep_mode_state,
            )

            hud = hud_controller
            if hud is not None:
                hud.update(radar_state, beeps_state)

    def handle_split(event: SplitEvent) -> None:
        nonlocal tracked_plid, tracked_driver

        update_track_context(event.track, event.car)

        if tracked_plid is None:
            tracked_plid = event.plid
            tracked_driver = event.player_name or f"PLID {event.plid}"
            reset_split_tracking()
            lap_state["last_lap_split_fractions"] = []

        if event.plid != tracked_plid:
            return

        lap_state.setdefault("current_split_times", {})[event.split_index] = event.split_time_ms
        if event.estimate_time_ms > 0:
            lap_state["latest_estimated_total_ms"] = event.estimate_time_ms

    def handle_button(event: ButtonClickEvent) -> None:
        nonlocal radar_enabled

        if not (event.flags & 0x01):
            return

        updated = False
        with config_lock:
            settings = mode_settings[current_mode]
            if event.click_id == HUDController.RADAR_BUTTON_ID:
                settings.radar_enabled = not settings.radar_enabled
                radar_enabled = settings.radar_enabled
                updated = True
            elif event.click_id == HUDController.BEEPS_BUTTON_ID:
                settings.beeps_enabled = not settings.beeps_enabled
                beep_system.set_enabled(settings.beeps_enabled)
                updated = True

            new_radar = radar_enabled
            new_beeps = beep_system.enabled

        if not updated:
            return

        logger.info(
            "HUD toggle applied: radar=%s beeps=%s",
            "on" if new_radar else "off",
            "on" if new_beeps else "off",
        )

        hud = hud_controller
        if hud is not None:
            hud.update(new_radar, new_beeps)

    def handle_mci(event: MultiCarInfoEvent) -> None:
        server = telemetry_server
        if server is not None:
            server.update_mci(event)

    watcher_thread = threading.Thread(target=watch_config, name="config-watcher", daemon=True)
    watcher_thread.start()

    try:
        insim_kwargs = {
            "state_listeners": [handle_state],
            "lap_listeners": [handle_lap],
            "split_listeners": [handle_split],
        }
        insim_signature = inspect.signature(InSimClient)
        if "mci_listeners" in insim_signature.parameters:
            insim_kwargs["mci_listeners"] = [handle_mci]

        with (
            InSimClient(
                config.insim,
                **insim_kwargs,
            ) as insim,
            OutSimClient(
                config.outsim_port,
                timeout=(
                    1.0 / config.outsim_update_hz
                    if config.outsim_update_hz is not None
                    else None
                ),
                allowed_sources=config.outsim_allowed_sources,
                max_packets_per_second=config.outsim_rate_limit,
            ) as outsim,
        ):
            hud_controller = HUDController(insim)
            add_button_listener = getattr(insim, "add_button_listener", None)
            if callable(add_button_listener):
                add_button_listener(handle_button)
            with config_lock:
                initial_radar = radar_enabled
                initial_beeps = beep_system.enabled
            hud_controller.show(initial_radar, initial_beeps)

            logger.info("Telemetry clients initialised; awaiting OutSim frames")
            try:
                for frame in outsim.frames():
                    last_frame_time_ms = frame.time_ms
                    if pending_lap_start:
                        lap_state["current_lap_start_ms"] = frame.time_ms
                        pending_lap_start = False
                    insim.poll()
                    if not getattr(insim, "connected", True):
                        logger.info("InSim connection closed; stopping frame loop")
                        break
                    with config_lock:
                        render_radar = radar_enabled

                    if render_radar:
                        radar.draw(frame)

                    beep_system.process_frame(frame)

                    server = telemetry_server
                    if server is not None:
                        server.update_outsim(frame)

                    current_start = lap_state["current_lap_start_ms"]
                    best_lap_ms = lap_state["best_lap_ms"]
                    current_lap_ms: Optional[int]
                    if current_start is None:
                        current_lap_ms = None
                    else:
                        current_lap_ms = max(0, frame.time_ms - current_start)

                    current_display = (
                        f"{current_lap_ms:>7} ms" if current_lap_ms is not None else "-- ms"
                    )
                    best_display = (
                        f"{best_lap_ms:>7} ms" if best_lap_ms is not None else "-- ms"
                    )
                    pb_display = (
                        f"{persistent_best.laptime_ms:>7} ms" if persistent_best else "-- ms"
                    )
                    reference_time = estimate_reference_time(current_lap_ms)
                    if reference_time is not None and current_lap_ms is not None:
                        delta_ms = current_lap_ms - reference_time
                    else:
                        delta_ms = None

                    lap_progress: Optional[float] = None
                    if (
                        reference_time is not None
                        and persistent_best
                        and persistent_best.laptime_ms > 0
                    ):
                        lap_progress = min(
                            max(reference_time / persistent_best.laptime_ms, 0.0),
                            1.0,
                        )
                    elif current_lap_ms is not None:
                        estimated_total = lap_state.get("latest_estimated_total_ms")
                        if estimated_total and estimated_total > 0:
                            lap_progress = min(
                                max(current_lap_ms / estimated_total, 0.0), 1.0
                            )

                    if server is not None:
                        server.update_player_lap(
                            progress=lap_progress,
                            current_lap_ms=current_lap_ms,
                            reference_lap_ms=reference_time,
                            delta_ms=delta_ms,
                        )
                    delta_display = (
                        f"{delta_ms:+7} ms" if delta_ms is not None else "  -- ms"
                    )
                    status_line = (
                        "Current lap: "
                        f"{current_display} | Session best: {best_display} | Personal best: {pb_display}"
                        f" | Δ vs PB: {delta_display}"
                    )
                    if status_line != last_status_line:
                        padded_line = status_line
                        if len(last_status_line) > len(status_line):
                            padded_line = status_line.ljust(len(last_status_line))
                        print(padded_line, end="\r", flush=True)
                        last_status_line = status_line
            finally:
                hud_controller.remove()
                hud_controller = None
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down")
    finally:
        stop_event.set()
        watcher_thread.join()
        if telemetry_server is not None:
            telemetry_server.stop()
        if last_status_line:
            print()


if __name__ == "__main__":
    main()
