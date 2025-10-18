"""Entry point for the telemetry radar prototype."""
from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from src.insim_client import ISS_MULTI, InSimClient, InSimConfig
from src.outsim_client import OutSimClient, OutSimFrame
from src.radar import RadarRenderer

logger = logging.getLogger(__name__)


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

    current_mode = "sp"
    mode_settings = {"sp": config.sp, "mp": config.mp}

    config_lock = threading.RLock()
    with config_lock:
        radar_enabled = mode_settings[current_mode].radar_enabled
        beep_system.set_enabled(mode_settings[current_mode].beeps_enabled)

    stop_event = threading.Event()

    def handle_state(flags2: int) -> None:
        nonlocal current_mode, radar_enabled

        new_mode = "mp" if flags2 & ISS_MULTI else "sp"
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

    watcher_thread = threading.Thread(target=watch_config, name="config-watcher", daemon=True)
    watcher_thread.start()

    try:
        with InSimClient(config.insim, state_listeners=[handle_state]) as insim, OutSimClient(
            config.outsim_port
        ) as outsim:
            logger.info("Telemetry clients initialised; awaiting OutSim frames")
            for frame in outsim.frames():
                insim.poll()
                with config_lock:
                    render_radar = radar_enabled

                if render_radar:
                    radar.draw(frame)
                beep_system.process_frame(frame)
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down")
    finally:
        stop_event.set()
        watcher_thread.join()


if __name__ == "__main__":
    main()
