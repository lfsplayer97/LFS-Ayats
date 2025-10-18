"""Tests for the minimal InSim client helpers."""

import struct
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.insim_client import (  # noqa: E402
    ISP_NPL,
    ISP_STA,
    ISP_LAP,
    InSimClient,
    InSimConfig,
)


def _make_client(**kwargs) -> InSimClient:
    config = InSimConfig(host="127.0.0.1", port=12345)
    return InSimClient(config, **kwargs)


def _build_sta_packet(view_plid: int, track_code: bytes) -> bytes:
    packet = bytearray(28)
    packet[0] = 28
    packet[1] = ISP_STA
    packet[10] = view_plid & 0xFF
    struct.pack_into("<H", packet, 16, 0)
    padded_track = track_code.ljust(6, b"\x00")[:6]
    packet[20:26] = padded_track
    return bytes(packet)


def test_handle_is_sta_extracts_track_and_resolves_car() -> None:
    events = []
    client = _make_client(state_listeners=[events.append])
    client._plid_to_car[7] = "FXO"

    packet = _build_sta_packet(7, b"BL1")
    client._handle_is_sta(packet)

    assert events
    event = events[-1]
    assert event.track == "BL1"
    assert event.car == "FXO"


def test_handle_is_npl_populates_car_mapping() -> None:
    events = []
    client = _make_client(state_listeners=[events.append])

    # Establish view PLID to simulate an active driver context.
    client._handle_is_sta(_build_sta_packet(12, b"SO1"))

    packet = bytearray(76)
    packet[0] = 76
    packet[1] = ISP_NPL
    packet[3] = 12  # PLID
    packet[40:44] = b"FXO "

    client._handle_is_npl(bytes(packet))

    assert client._plid_to_car[12] == "FXO"
    assert events
    # The latest notification should include the resolved car.
    assert events[-1].car == "FXO"


def test_lap_events_inherit_track_and_car_context() -> None:
    lap_events = []
    client = _make_client(lap_listeners=[lap_events.append])
    client._current_track = "BL1"
    client._plid_to_car[5] = "XFG"

    size = 64
    packet = bytearray(size)
    packet[0] = size
    packet[1] = ISP_LAP
    packet[3] = 5  # PLID
    struct.pack_into("<II", packet, 4, 73_000, 74_000)
    struct.pack_into("<H", packet, 12, 0)
    packet[14] = 0
    packet[15] = 0
    packet[16] = 0
    packet[17] = 0
    name = b"Driver\x00"
    packet[18 : 18 + len(name)] = name

    client._handle_packet(bytes(packet))

    assert lap_events
    event = lap_events[-1]
    assert event.track == "BL1"
    assert event.car == "XFG"

