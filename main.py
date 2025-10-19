"""Entry point for the telemetry radar prototype."""
from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.insim_client import ISS_MULTI, InSimClient, InSimConfig, LapEvent, SplitEvent, StateEvent
from src.outsim_client import OutSimClient, OutSimFrame
from src.radar import RadarRenderer
from src.persistence import PersonalBestRecord, load_personal_best, record_lap

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
class AppConfig:
    insim: InSimConfig
    outsim_port: int
    beep_mode: str
    sp: ModeConfig
    mp: ModeConfig

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "AppConfig":
        insim_cfg_raw = raw.get("insim", {})
        outsim_cfg_raw = raw.get("outsim", {})

        insim_cfg = InSimConfig(
            host=insim_cfg_raw.get("host", "127.0.0.1"),
            port=int(insim_cfg_raw.get("port", 29999)),
            admin_password=insim_cfg_raw.get("admin_password", ""),
            interval_ms=int(insim_cfg_raw.get("interval_ms", 100)),
        )

        outsim_port = int(outsim_cfg_raw.get("port", 30000))
        beep_mode = str(raw.get("beep_mode", "standard"))

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
            beep_mode=beep_mode,
            sp=sp_cfg,
            mp=mp_cfg,
        )


class BeepSubsystem:
    """Tiny placeholder for a configurable beep system."""

    def __init__(self, mode: str) -> None:
        self._mode = mode
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_mode(self, mode: str) -> None:
        if mode == self._mode:
            return
        logger.info("Updating beep mode to %s", mode)
        self._mode = mode

    def set_enabled(self, enabled: bool) -> None:
        if self._enabled == enabled:
            return

        self._enabled = enabled
        state = "enabled" if enabled else "disabled"
        logger.info("Beep subsystem %s (mode=%s)", state, self._mode)

    def process_frame(self, frame: OutSimFrame) -> None:  # pragma: no cover - placeholder
        if not self._enabled:
            return
        logger.debug("Processing OutSim frame for beep subsystem at %sms", frame.time_ms)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")

    config_path = Path(__file__).resolve().parent / "config.json"
    config = AppConfig.from_dict(load_config(config_path))

    radar = RadarRenderer()
    beep_system = BeepSubsystem(config.beep_mode)

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
        fractions = resolve_reference_fractions()
        if not fractions:
            estimate_total = lap_state.get("latest_estimated_total_ms")
            if not estimate_total or estimate_total <= 0:
                return None

            progress = min(max(current_ms / estimate_total, 0.0), 1.0)
            reference_time = int(round(pb_total * progress))
            return min(reference_time, pb_total)

        boundaries = fractions + [1.0]

        current_splits: Dict[int, int] = lap_state.get("current_split_times", {})
        sorted_split_times = [current_splits[idx] for idx in sorted(current_splits)]
        passed_split_times = [t for t in sorted_split_times if t <= current_ms]

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
        nonlocal pending_lap_start

        normalised_track = track.strip() if track else None
        normalised_car = car.strip() if car else None

        track_changed = bool(normalised_track and normalised_track != current_track)
        car_changed = bool(normalised_car and normalised_car != current_car)

        if track_changed:
            current_track = normalised_track
        if car_changed:
            current_car = normalised_car

        if track_changed or car_changed:
            tracked_plid = None
            tracked_driver = None
            clear_session_timing(lap_state)
            pending_lap_start = True
            if current_track and current_car:
                persistent_best = load_personal_best(current_track, current_car)
                reset_split_tracking()
                if persistent_best is None:
                    logger.info(
                        "No stored personal best for %s / %s", current_track, current_car
                    )
                else:
                    logger.info(
                        "Loaded personal best for %s / %s: %s ms (recorded %s)",
                        current_track,
                        current_car,
                        persistent_best.laptime_ms,
                        persistent_best.recorded_at.isoformat(),
                    )

    def handle_state(event: StateEvent) -> None:
        nonlocal current_mode, radar_enabled

        update_track_context(event.track, event.car)

        new_mode = "mp" if event.flags2 & ISS_MULTI else "sp"
        if new_mode == current_mode:
            return

        with config_lock:
            current_mode = new_mode
            settings = mode_settings[new_mode]
            radar_enabled = settings.radar_enabled
            beep_system.set_enabled(settings.beeps_enabled)
            radar_state = radar_enabled
            beeps_state = settings.beeps_enabled

        logger.info(
            "Detected %splayer mode: radar=%s beeps=%s",
            "multi" if new_mode == "mp" else "single ",
            "on" if radar_state else "off",
            "on" if beeps_state else "off",
        )

    def handle_lap(event: LapEvent) -> None:
        nonlocal tracked_plid, tracked_driver, last_frame_time_ms, pending_lap_start, persistent_best

        update_track_context(event.track, event.car)

        if tracked_plid is None:
            tracked_plid = event.plid
            tracked_driver = event.player_name or f"PLID {event.plid}"
            logger.info("Tracking lap data for %s (PLID %s)", tracked_driver, event.plid)
            reset_split_tracking()
            lap_state["last_lap_split_fractions"] = []

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
        nonlocal config, mode_settings, radar_enabled

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

            with config_lock:
                config = new_config
                mode_settings = {"sp": config.sp, "mp": config.mp}
                beep_system.set_mode(config.beep_mode)
                mode_name = current_mode
                settings = mode_settings[mode_name]
                radar_enabled = settings.radar_enabled
                beep_system.set_enabled(settings.beeps_enabled)
                radar_state = radar_enabled
                beeps_state = settings.beeps_enabled
                beep_mode_state = config.beep_mode

            logger.info(
                "Reloaded configuration (mode=%s, radar=%s, beeps=%s, beep_mode=%s)",
                mode_name,
                "on" if radar_state else "off",
                "on" if beeps_state else "off",
                beep_mode_state,
            )

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

        lap_state.setdefault("current_split_times", {})[event.split_index] = (
            event.split_time_ms
        )
        if event.estimate_time_ms > 0:
            lap_state["latest_estimated_total_ms"] = event.estimate_time_ms

    watcher_thread = threading.Thread(target=watch_config, name="config-watcher", daemon=True)
    watcher_thread.start()

    try:
        with InSimClient(
            config.insim,
            state_listeners=[handle_state],
            lap_listeners=[handle_lap],
            split_listeners=[handle_split],
        ) as insim, OutSimClient(
            config.outsim_port
        ) as outsim:
            logger.info("Telemetry clients initialised; awaiting OutSim frames")
            for frame in outsim.frames():
                last_frame_time_ms = frame.time_ms
                if pending_lap_start:
                    lap_state["current_lap_start_ms"] = frame.time_ms
                    pending_lap_start = False
                insim.poll()
                with config_lock:
                    render_radar = radar_enabled

                if render_radar:
                    radar.draw(frame)
                beep_system.process_frame(frame)

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
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down")
    finally:
        stop_event.set()
        watcher_thread.join()
        if last_status_line:
            print()


if __name__ == "__main__":
    main()
