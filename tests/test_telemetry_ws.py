from __future__ import annotations

import json

import pytest

from src.insim_client import CarInfo, MultiCarInfoEvent
from src.telemetry_ws import TelemetryBroadcaster


def test_snapshot_converts_car_coordinates_to_metres() -> None:
    broadcaster = TelemetryBroadcaster("127.0.0.1", 8765)

    car = CarInfo(
        node=0,
        lap=1,
        plid=42,
        position=3,
        info=0,
        x=65_536,
        y=-131_072,
        z=32_768,
        speed=450,
        direction=0,
        heading=0,
        angular_velocity=0,
    )

    event = MultiCarInfoEvent(cars=[car], view_plid=car.plid)
    broadcaster.update_mci(event)

    snapshot = broadcaster._build_snapshot()
    assert snapshot is not None

    payload = json.loads(json.dumps(snapshot.__dict__, separators=(",", ":")))
    [car_payload] = payload["cars"]
    assert car_payload["x"] == pytest.approx(1.0)
    assert car_payload["y"] == pytest.approx(-2.0)
    assert car_payload["z"] == pytest.approx(0.5)
    assert car_payload["speed"] == pytest.approx(4.5)

    focused = payload["focused_car"]
    assert focused["plid"] == car.plid
    assert focused["x"] == pytest.approx(1.0)
    assert focused["y"] == pytest.approx(-2.0)
    assert focused["z"] == pytest.approx(0.5)
