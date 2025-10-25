"""Tests for the minimal InSim client helpers."""

import logging
import struct
from typing import Callable

from src.hud import HUDController
from src.insim_client import (
    ISB_CLICK,
    ISP_BTC,
    ISP_LAP,
    ISP_MCI,
    ISP_NPL,
    ISP_SPX,
    ISP_STA,
    ISP_VER,
    ISS_MULTI,
    MCI_ENTRY_SIZE,
    InSimClient,
    MultiCarInfoEvent,
    PacketValidator,
)

def _build_sta_packet(view_plid: int, track_code: bytes, *, flags2: int = 0) -> bytes:
    packet = bytearray(28)
    packet[0] = 28
    packet[1] = ISP_STA
    packet[10] = view_plid & 0xFF
    struct.pack_into("<H", packet, 16, flags2 & 0xFFFF)
    padded_track = track_code.ljust(6, b"\x00")[:6]
    packet[20:26] = padded_track
    return bytes(packet)


def test_process_buffer_accepts_version_handshake(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    client = insim_client_factory()
    handshake = bytes(
        [
            20,
            ISP_VER,
            0,
            0,
        ]
    ) + b"LFS\x00\x00\x000.7D\x00\x00\x00\x00v9"

    with caplog.at_level(logging.DEBUG):
        client._append_to_buffer(handshake)
        client._process_buffer()

    assert all(record.levelno < logging.WARNING for record in caplog.records)
    assert client._buffer == bytearray()
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


def test_handle_is_npl_preserves_multiplayer_flag(
    insim_client_factory: Callable[..., InSimClient],
) -> None:
    events = []
    client = insim_client_factory(state_listeners=[events.append])

    client._handle_is_sta(_build_sta_packet(12, b"SO1", flags2=ISS_MULTI))

    packet = bytearray(76)
    packet[0] = 76
    packet[1] = ISP_NPL
    packet[3] = 12  # PLID
    packet[40:44] = b"FXO "

    client._handle_is_npl(bytes(packet))

    assert events
    assert events[-1].flags2 & ISS_MULTI
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


def test_handle_packet_rejects_truncated_lap_packet(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    lap_events = []
    client = insim_client_factory(lap_listeners=[lap_events.append])
    packet = bytearray(12)
    packet[0] = 12  # smaller than minimum lap schema
    packet[1] = ISP_LAP
    packet[3] = 7

    with caplog.at_level(logging.WARNING):
        client._handle_packet(bytes(packet))

    assert not lap_events
    assert any("Rejecting IS_LAP packet" in record.message for record in caplog.records)


def _build_lap_packet_with_size(size: int) -> bytes:
    packet = bytearray(size)
    packet[0] = size
    packet[1] = ISP_LAP
    packet[3] = 5
    struct.pack_into("<II", packet, 4, 73_000, 74_000)
    struct.pack_into("<H", packet, 12, 0)
    packet[14] = 1
    packet[15] = 0
    packet[16] = 0
    packet[17] = 0
    return bytes(packet)


def test_lap_packet_with_truncated_name_is_rejected(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    lap_events = []
    client = insim_client_factory(lap_listeners=[lap_events.append])
    packet = bytearray(_build_lap_packet_with_size(30))

    with caplog.at_level(logging.WARNING):
        client._handle_packet(bytes(packet))

    assert not lap_events
    assert any(
        "smaller than minimum" in record.message and "IS_LAP" in record.message
        for record in caplog.records
    )


def test_split_packet_with_truncated_name_is_rejected(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    split_events = []
    client = insim_client_factory(split_listeners=[split_events.append])
    size = 30
    packet = bytearray(size)
    packet[0] = size
    packet[1] = ISP_SPX
    packet[3] = 5
    struct.pack_into("<II", packet, 4, 12_000, 13_000)
    struct.pack_into("<H", packet, 12, 0)
    packet[14] = 1
    packet[15] = 0
    packet[16] = 0
    packet[17] = 0

    with caplog.at_level(logging.WARNING):
        client._handle_packet(bytes(packet))

    assert not split_events
    assert any(
        "smaller than minimum" in record.message and "IS_SPX" in record.message
        for record in caplog.records
    )


def test_packet_validator_rejects_lap_below_minimum_size() -> None:
    validator = PacketValidator()
    size = 30
    packet = bytearray(size)
    packet[0] = size
    packet[1] = ISP_LAP

    is_valid, reason = validator.validate(bytes(packet))

    assert not is_valid
    assert reason and "smaller than minimum" in reason


def test_packet_validator_rejects_split_below_minimum_size() -> None:
    validator = PacketValidator()
    size = 30
    packet = bytearray(size)
    packet[0] = size
    packet[1] = ISP_SPX

    is_valid, reason = validator.validate(bytes(packet))

    assert not is_valid
    assert reason and "smaller than minimum" in reason


def test_packet_validator_rejects_truncated_version_packet() -> None:
    validator = PacketValidator()
    packet = bytes([20, ISP_VER, 0, 0, 0, 0, 0, 0, 0, 0])

    is_valid, reason = validator.validate(packet)

    assert not is_valid
    assert reason and "payload shorter" in reason


def test_truncated_button_packet_is_rejected(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    button_events = []
    client = insim_client_factory(button_listeners=[button_events.append])
    packet = bytes([6, ISP_BTC, 0, 0, 0, 0])

    with caplog.at_level(logging.WARNING):
        client._handle_packet(packet)

    assert not button_events
    assert any("Rejecting IS_BTC packet" in record.message for record in caplog.records)


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
    client = insim_client_factory(buffer_limit=12)
    packets = [
        bytes([4, 1, 0, 0]),
        bytes([4, 200, 0, 0]),
        bytes([8, ISP_BTC, 0, 0, 0, 0, 0, 0]),
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
    assert any("enforce limit" in message for message in messages)
    assert any("invalid packet header" in message for message in messages)


def test_buffer_limit_recovers_from_truncated_small_prefix(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    client = insim_client_factory(buffer_limit=9)
    truncated_packet = bytes([8, ISP_STA, 170, 4, 153, 136, 119, 102])
    valid_packet = bytes([8, ISP_BTC, 0, 0, 0, 0, 0, 0])
    processed: list[bytes] = []

    def recorder(packet: bytes) -> None:
        processed.append(packet)

    client._handle_packet = recorder  # type: ignore[method-assign]

    with caplog.at_level(logging.WARNING):
        client._append_to_buffer(truncated_packet)
        client._append_to_buffer(valid_packet)
        client._process_buffer()

    assert processed == [valid_packet]
    assert client._buffer == bytearray()
    messages = [record.message for record in caplog.records]
    assert "invalid packet header" in " ".join(messages)


def test_corrupted_size_header_is_skipped(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    lap_events: list = []
    client = insim_client_factory(lap_listeners=[lap_events.append])
    client._current_track = "BL1"
    client._plid_to_car[5] = "XFG"

    valid_size = 64
    valid_packet = bytearray(valid_size)
    valid_packet[0] = valid_size
    valid_packet[1] = ISP_LAP
    valid_packet[3] = 5
    struct.pack_into("<II", valid_packet, 4, 73_000, 74_000)
    struct.pack_into("<H", valid_packet, 12, 0)
    valid_packet[14] = 0
    valid_packet[15] = 0
    valid_packet[16] = 0
    valid_packet[17] = 0
    name = b"Driver\x00"
    valid_packet[18 : 18 + len(name)] = name

    corrupted_header = bytes([200, ISP_LAP])

    with caplog.at_level(logging.WARNING):
        client._append_to_buffer(corrupted_header + bytes(valid_packet))
        client._process_buffer()

    assert lap_events
    assert lap_events[-1].track == "BL1"
    assert lap_events[-1].car == "XFG"
    messages = [record.message for record in caplog.records]
    assert any("invalid IS_LAP header" in message for message in messages)


def test_corrupted_short_header_is_skipped_without_consuming_payload(
    insim_client_factory: Callable[..., InSimClient], caplog
) -> None:
    lap_events: list = []
    client = insim_client_factory(lap_listeners=[lap_events.append])
    client._current_track = "BL1"
    client._plid_to_car[5] = "XFG"

    valid_size = 64
    valid_packet = bytearray(valid_size)
    valid_packet[0] = valid_size
    valid_packet[1] = ISP_LAP
    valid_packet[3] = 5
    struct.pack_into("<II", valid_packet, 4, 73_000, 74_000)
    struct.pack_into("<H", valid_packet, 12, 0)
    valid_packet[14] = 0
    valid_packet[15] = 0
    valid_packet[16] = 0
    valid_packet[17] = 0
    name = b"Driver\x00"
    valid_packet[18 : 18 + len(name)] = name

    corrupted_header = bytes([3, ISP_LAP])

    with caplog.at_level(logging.WARNING):
        client._append_to_buffer(corrupted_header + bytes(valid_packet))
        client._process_buffer()

    assert lap_events
    assert lap_events[-1].track == "BL1"
    assert lap_events[-1].car == "XFG"
    messages = [record.message for record in caplog.records]
    assert any("invalid packet header" in message for message in messages)


def test_parse_mci_packet_returns_empty_event_when_no_cars(
    insim_client_factory: Callable[..., InSimClient]
) -> None:
    client = insim_client_factory()
    packet = bytes([4, ISP_MCI, 0, 0])

    event = client._parse_mci_packet(packet)

    assert isinstance(event, MultiCarInfoEvent)
    assert event.cars == []


def test_parse_mci_packet_handles_large_car_count(
    insim_client_factory: Callable[..., InSimClient]
) -> None:
    client = insim_client_factory()
    count = 12
    entry_size = 28
    packet_length = 4 + count * entry_size
    packet = bytearray(packet_length)
    packet[0] = packet_length & 0xFF
    packet[1] = ISP_MCI
    packet[2] = 0
    packet[3] = count

    for index in range(count):
        offset = 4 + index * entry_size
        struct.pack_into(
            "<HHBBBBiiiHHHh",
            packet,
            offset,
            index,
            index + 10,
            index + 1,
            index % 255,
            0,
            0,
            index * 100,
            index * 1_000,
            -index * 50,
            index * 2,
            index * 3,
            index * 4,
            index * 5,
        )

    event = client._parse_mci_packet(bytes(packet))

    assert isinstance(event, MultiCarInfoEvent)
    assert event.cars
    assert len(event.cars) == count
    last_car = event.cars[-1]
    assert last_car.node == count - 1
    assert last_car.lap == count - 1 + 10
    assert last_car.plid == count
    assert last_car.position == (count - 1) % 255


def test_parse_mci_packet_handles_wrapped_size_field(
    insim_client_factory: Callable[..., InSimClient]
) -> None:
    client = insim_client_factory()
    count = 9
    entry_size = 28
    packet_length = 4 + count * entry_size
    assert packet_length == 256
    packet = bytearray(packet_length)
    packet[0] = packet_length & 0xFF
    packet[1] = ISP_MCI
    packet[2] = 0
    packet[3] = count

    for index in range(count):
        offset = 4 + index * entry_size
        struct.pack_into(
            "<HHBBBBiiiHHHh",
            packet,
            offset,
            index,
            index + 5,
            index + 1,
            index % 32,
            0,
            0,
            index * 100,
            -index * 200,
            index * 50,
            index + 10,
            index + 20,
            index + 30,
            index - 5,
        )

    event = client._parse_mci_packet(bytes(packet))

    assert isinstance(event, MultiCarInfoEvent)
    assert event.cars
    assert len(event.cars) == count
    first_car = event.cars[0]
    last_car = event.cars[-1]
    assert first_car.plid == 1
    assert last_car.plid == count


def test_handle_packet_accepts_mci_with_wrapped_header(
    insim_client_factory: Callable[..., InSimClient],
) -> None:
    events: list[MultiCarInfoEvent] = []
    client = insim_client_factory(mci_listeners=[events.append])

    packet = bytearray(4 + MCI_ENTRY_SIZE)
    packet[0] = 0
    packet[1] = ISP_MCI
    packet[2] = 0
    packet[3] = 1
    struct.pack_into(
        "<HHBBBBiiiHHHh",
        packet,
        4,
        12,
        3,
        7,
        1,
        0,
        0,
        100,
        200,
        -300,
        400,
        500,
        600,
        -50,
    )

    client._handle_packet(bytes(packet))

    assert events
    assert events[-1].cars
    assert events[-1].cars[0].plid == 7
