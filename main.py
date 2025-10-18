"""Entry point for the telemetry radar prototype."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from src.insim_client import InSimClient, InSimConfig
from src.outsim_client import OutSimClient
from src.radar import RadarRenderer

logger = logging.getLogger(__name__)


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")

    config_path = Path(__file__).resolve().parent / "config.json"
    config = load_config(config_path)

    insim_cfg_raw = config.get("insim", {})
    outsim_cfg_raw = config.get("outsim", {})

    insim_cfg = InSimConfig(
        host=insim_cfg_raw.get("host", "127.0.0.1"),
        port=int(insim_cfg_raw.get("port", 29999)),
        admin_password=insim_cfg_raw.get("admin_password", ""),
        interval_ms=int(insim_cfg_raw.get("interval_ms", 100)),
    )

    outsim_port = int(outsim_cfg_raw.get("port", 30000))
    radar = RadarRenderer()

    try:
        with InSimClient(insim_cfg) as insim, OutSimClient(outsim_port) as outsim:
            logger.info("Telemetry clients initialised; awaiting OutSim frames")
            for frame in outsim.frames():
                radar.draw(frame)
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down")


if __name__ == "__main__":
    main()
