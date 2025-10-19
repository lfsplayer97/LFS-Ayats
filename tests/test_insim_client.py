"""Tests for the minimal InSim client helpers."""

import logging
import struct
from typing import Callable

from src.hud import HUDController
from src.insim_client import ISB_CLICK, ISP_LAP, ISP_NPL, ISP_STA, InSimClient

def _build_sta_packet(view_plid: int, track_code: bytes) -> bytes:
    packet = bytearray(28)
    packet[0] = 28
    packet[1] = ISP_STA
    packet[10] = view_plid & 0xFF
    struct.pack_into("<H", packet, 16, 0)
    padded_track = track_code.ljust(6, b"\x00")[:6]
    packet[20:26] = padded_track
    return bytes(packet)
def test_handle_is_sta_extracts_track_and_resolves_car(
    insim_client_factory: Callable[..., InSimClient],
) -> None:
    events = []
    client = insim_client_factory(state_listeners=[events.append])
    client._plid_to_car[7] = "FXO"

    packet = _build_sta_packet(7, b"BL1")
    client._handle_is_sta(packet)

    assert events
    event = events[-1]
    assert event.track == "BL1"
    assert event.car == "FXO"
def test_handle_is_npl_populates_car_mapping(
    insim_client_factory: Callable[..., InSimClient],
) -> None:
    events = []
    client = insim_client_factory(state_listeners=[events.append])

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
def test_lap_events_inherit_track_and_car_context(
    insim_client_factory: Callable[..., InSimClient],
) -> None:
    lap_events = []
    client = insim_client_factory(lap_listeners=[lap_events.append])
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


class _RecordingInSim:
    connected = True

    def __init__(self) -> None:
        self.styles: list[int] = []

    def show_button(self, *, style: int, **kwargs) -> None:
        self.styles.append(style)

    def delete_button(self, **kwargs) -> None:  # pragma: no cover - unused in test
        pass


def test_hud_buttons_request_clickable_style() -> None:
    insim = _RecordingInSim()
    controller = HUDController(insim)

    controller.show(radar_enabled=True, beeps_enabled=False)

    assert insim.styles == [ISB_CLICK, ISB_CLICK]


def test_buffer_limit_discards_old_bytes(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    client = insim_client_factory(buffer_limit=8)

    with caplog.at_level(logging.WARNING):
        client._append_to_buffer(b"1234")
        assert bytes(client._buffer) == b"1234"
        assert caplog.records == []

        caplog.clear()

        client._append_to_buffer(b"abcdefghijk")

        assert bytes(client._buffer) == b""
        assert caplog.records
        messages = [record.message for record in caplog.records]
        assert "Discarded 7 bytes from InSim buffer to enforce limit" in messages
        assert any("buffer" in message for message in messages)


def test_buffer_limit_preserves_latest_packet_after_overflow(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    client = insim_client_factory(buffer_limit=7)
    packets = [
        bytes([4, 1, 0, 0]),
        bytes([4, 200, 0, 0]),
        bytes([4, 2, 0, 0]),
    ]
    processed: list[bytes] = []

    def recorder(packet: bytes) -> None:
        processed.append(packet)

    client._handle_packet = recorder  # type: ignore[method-assign]

    with caplog.at_level(logging.WARNING):
        client._append_to_buffer(b"".join(packets))
        client._process_buffer()

    assert processed == [packets[-1]]
    assert client._buffer == bytearray()
    messages = [record.message for record in caplog.records]
    assert "Discarded 5 bytes from InSim buffer to enforce limit" in messages
    assert any("invalid packet header" in message for message in messages)
