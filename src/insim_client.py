"""Client utilities for working with the Live for Speed InSim interface."""

from __future__ import annotations

import logging
import select
import socket
import struct
from dataclasses import dataclass
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


# -- InSim protocol helpers -------------------------------------------------

# InSim packet and flag constants.  Only the few flags that are relevant for
# enabling multiplayer-safe telemetry are included – additional flags can be
# added in the future as the prototype grows.
ISP_ISI = 1
ISP_VER = 2
ISP_STA = 5
ISP_MST = 11
ISP_NPL = 21
ISP_LAP = 28
ISP_SPX = 29
ISP_MCI = 38
ISP_BTN = 45
ISP_BFN = 46
ISP_BTC = 47

_KNOWN_PACKET_TYPES = {
    ISP_ISI,
    ISP_VER,
    ISP_STA,
    ISP_MST,
    ISP_NPL,
    ISP_LAP,
    ISP_SPX,
    ISP_MCI,
    ISP_BTN,
    ISP_BFN,
    ISP_BTC,
}

_PACKET_TYPE_NAMES = {
    ISP_ISI: "IS_ISI",
    ISP_VER: "IS_VER",
    ISP_STA: "IS_STA",
    ISP_MST: "IS_MST",
    ISP_NPL: "IS_NPL",
    ISP_LAP: "IS_LAP",
    ISP_SPX: "IS_SPX",
    ISP_MCI: "IS_MCI",
    ISP_BTN: "IS_BTN",
    ISP_BFN: "IS_BFN",
    ISP_BTC: "IS_BTC",
}


@dataclass(frozen=True)
class _PacketField:
    name: str
    offset: int
    length: int


@dataclass(frozen=True)
class _PacketSchema:
    name: str
    min_size: int
    fields: tuple[_PacketField, ...]
    exact_size: Optional[int] = None
    max_size: Optional[int] = None


class PacketValidator:
    """Validate known InSim packets against predefined schemas."""

    def __init__(self) -> None:
        # Conservative packet size bounds (inclusive) that allow the validator to
        # reject obviously corrupted headers before attempting to parse payloads.
        self._size_bounds: dict[int, tuple[int, int]] = {
            ISP_VER: (20, 20),
            ISP_STA: (28, 28),
            ISP_NPL: (44, 120),
            ISP_LAP: (42, 96),
            ISP_SPX: (42, 96),
            ISP_BTC: (8, 12),
        }
        self._schemas: dict[int, _PacketSchema] = {
            ISP_VER: _PacketSchema(
                name="IS_VER",
                min_size=20,
                exact_size=20,
                max_size=20,
                fields=(
                    _PacketField(name="header", offset=0, length=4),
                    _PacketField(name="version_region", offset=4, length=16),
                ),
            ),
            ISP_STA: _PacketSchema(
                name="IS_STA",
                min_size=28,
                exact_size=28,
                max_size=28,
                fields=(
                    _PacketField(name="header", offset=0, length=4),
                    _PacketField(name="flags2", offset=16, length=2),
                ),
            ),
            ISP_NPL: _PacketSchema(
                name="IS_NPL",
                min_size=44,
                max_size=120,
                fields=(
                    _PacketField(name="header", offset=0, length=4),
                    _PacketField(name="plid", offset=3, length=1),
                    _PacketField(name="car", offset=40, length=4),
                ),
            ),
            ISP_LAP: _PacketSchema(
                name="IS_LAP",
                min_size=42,
                max_size=96,
                fields=(
                    _PacketField(name="header", offset=0, length=4),
                    _PacketField(name="lap_time", offset=4, length=8),
                    _PacketField(name="flags", offset=12, length=2),
                    _PacketField(name="sp0", offset=14, length=1),
                    _PacketField(name="penalty", offset=15, length=1),
                    _PacketField(name="num_stops", offset=16, length=1),
                    _PacketField(name="fuel_200", offset=17, length=1),
                    _PacketField(name="player_name", offset=18, length=24),
                ),
            ),
            ISP_SPX: _PacketSchema(
                name="IS_SPX",
                min_size=42,
                max_size=96,
                fields=(
                    _PacketField(name="header", offset=0, length=4),
                    _PacketField(name="split_time", offset=4, length=8),
                    _PacketField(name="flags", offset=12, length=2),
                    _PacketField(name="split", offset=14, length=1),
                    _PacketField(name="penalty", offset=15, length=1),
                    _PacketField(name="num_stops", offset=16, length=1),
                    _PacketField(name="fuel_200", offset=17, length=1),
                    _PacketField(name="player_name", offset=18, length=24),
                ),
            ),
            ISP_BTC: _PacketSchema(
                name="IS_BTC",
                min_size=8,
                max_size=12,
                fields=(
                    _PacketField(name="header", offset=0, length=4),
                    _PacketField(name="flags", offset=6, length=2),
                ),
            ),
            ISP_MCI: _PacketSchema(
                name="IS_MCI",
                min_size=4,
                max_size=None,
                fields=(
                    _PacketField(name="header", offset=0, length=4),
                ),
            ),
        }

    def validate_header(self, size: int, packet_type: int) -> tuple[bool, Optional[str]]:
        if size < 4:
            return False, f"size field {size} smaller than minimum header length 4"

        bounds = self._size_bounds.get(packet_type)
        if bounds is not None:
            min_size, max_size = bounds
            if size < min_size:
                return False, f"size field {size} is smaller than minimum {min_size}"
            if size > max_size:
                return False, f"size field {size} exceeds maximum {max_size}"

        return True, None

    def validate(self, packet: bytes) -> tuple[bool, Optional[str]]:
        if len(packet) < 2:
            return False, "packet shorter than minimum header"

        size = packet[0]
        packet_type = packet[1]

        header_valid, header_reason = self.validate_header(size, packet_type)
        if not header_valid:
            return False, header_reason

        if len(packet) < size:
            return False, f"packet payload shorter than declared size (len={len(packet)}, size={size})"

        schema = self._schemas.get(packet_type)
        if schema is None:
            return True, None

        if size < schema.min_size:
            return False, f"size field {size} is smaller than minimum {schema.min_size}"

        if schema.exact_size is not None and size != schema.exact_size:
            return False, f"expected size {schema.exact_size} but received {size}"

        if schema.max_size is not None and size > schema.max_size:
            return False, f"size field {size} exceeds maximum {schema.max_size}"

        for field in schema.fields:
            end = field.offset + field.length
            if end > size:
                return False, f"field '{field.name}' exceeds packet size (requires {end}, size={size})"

        return True, None

    def get_type_name(self, packet_type: int) -> str:
        return _PACKET_TYPE_NAMES.get(packet_type, f"0x{packet_type:02X}")

# InSim button style flags
ISB_CLICK = 1 << 2  # emits IS_BTC when the button is clicked

ISF_MCI = 1 << 0  # receive multi car info packets
ISF_CON = 1 << 1  # receive contact packets
ISF_OBH = 1 << 2  # receive object hit packets
ISF_NLP = 1 << 3  # receive IS_NPL packets containing player load info


# InSim state flags (Flags2 field of ``IS_STA``)
ISS_MULTI = 1 << 0


@dataclass
class InSimConfig:
    """Configuration values required to establish an InSim connection."""

    host: str
    port: int
    admin_password: str = ""
    interval_ms: int = 100
    timeout: Optional[float] = 5.0


@dataclass
class LapEvent:
    """Represents the data contained within an ``IS_LAP`` packet."""

    plid: int
    lap_time_ms: int
    estimate_time_ms: int
    flags: int
    penalty: int
    num_pit_stops: int
    fuel_percent: int
    player_name: str
    spare: int = 0
    raw_sp0: int = 0
    track: Optional[str] = None
    car: Optional[str] = None


@dataclass
class SplitEvent:
    """Represents the data contained within an ``IS_SPX`` packet."""

    plid: int
    split_time_ms: int
    estimate_time_ms: int
    split_index: int
    flags: int
    penalty: int
    num_pit_stops: int
    fuel_percent: int
    player_name: str
    spare: int = 0
    track: Optional[str] = None
    car: Optional[str] = None


@dataclass
class StateEvent:
    """Represents high level state changes reported via ``IS_STA``."""

    flags2: int
    track: Optional[str] = None
    car: Optional[str] = None
    view_plid: Optional[int] = None


@dataclass
class CarInfo:
    """Summary of a single car entry contained within an ``IS_MCI`` packet."""

    node: int
    lap: int
    plid: int
    position: int
    info: int
    x: int
    y: int
    z: int
    speed: int
    direction: int
    heading: int
    angular_velocity: int
    spare: int = 0


@dataclass
class MultiCarInfoEvent:
    """Aggregated multi-car information parsed from ``IS_MCI`` packets."""

    cars: List[CarInfo]
    view_plid: Optional[int] = None


@dataclass
class ButtonClickEvent:
    """Represents a click interaction from an ``IS_BTC`` packet."""

    req_id: int
    ucid: int
    click_id: int
    inst: int
    flags: int


class InSimClient:
    """Minimal TCP client for the Live for Speed InSim protocol."""

    def __init__(
        self,
        config: InSimConfig,
        *,
        state_listeners: Optional[List[Callable[["StateEvent"], None]]] = None,
        lap_listeners: Optional[List[Callable[["LapEvent"], None]]] = None,
        split_listeners: Optional[List[Callable[["SplitEvent"], None]]] = None,
        button_listeners: Optional[List[Callable[["ButtonClickEvent"], None]]] = None,
        mci_listeners: Optional[List[Callable[["MultiCarInfoEvent"], None]]] = None,
        buffer_limit: int = 65_536,
    ) -> None:
        self._config = config
        self._sock: Optional[socket.socket] = None
        self._buffer = bytearray()
        self._buffer_limit = buffer_limit
        self._state_listeners: List[Callable[["StateEvent"], None]] = []
        self._lap_listeners: List[Callable[["LapEvent"], None]] = []
        self._split_listeners: List[Callable[["SplitEvent"], None]] = []
        self._button_listeners: List[Callable[["ButtonClickEvent"], None]] = []
        self._mci_listeners: List[Callable[["MultiCarInfoEvent"], None]] = []
        self._plid_to_car: dict[int, str] = {}
        self._current_track: Optional[str] = None
        self._current_car: Optional[str] = None
        self._view_plid: Optional[int] = None
        self._last_flags2: int = 0
        self._validator = PacketValidator()
        if state_listeners:
            self._state_listeners.extend(state_listeners)
        if lap_listeners:
            self._lap_listeners.extend(lap_listeners)
        if split_listeners:
            self._split_listeners.extend(split_listeners)
        if button_listeners:
            self._button_listeners.extend(button_listeners)
        if mci_listeners:
            self._mci_listeners.extend(mci_listeners)

    # -- socket lifecycle --------------------------------------------------
    def connect(self) -> None:
        """Open a TCP socket, connect to the server and send ``IS_ISI``."""

        if self._sock is not None:
            logger.debug("Reconnecting: closing existing socket")
            self.close()

        logger.info("Connecting to InSim at %s:%s", self._config.host, self._config.port)
        sock = socket.create_connection(
            (self._config.host, self._config.port), timeout=self._config.timeout
        )
        self._sock = sock
        self._buffer.clear()
        self._plid_to_car.clear()
        self._current_track = None
        self._current_car = None
        self._view_plid = None
        self._last_flags2 = 0
        sock.setblocking(False)

        size = 44
        reqi = 0
        udp_port = 0  # we are not using a UDP connection for InSim packets here
        flags = ISF_MCI | ISF_CON | ISF_OBH | ISF_NLP
        sp0 = 0
        prefix = ord("/")
        interval = max(1, self._config.interval_ms)
        admin = self._config.admin_password.encode("ascii", errors="ignore")[:16]
        admin = admin.ljust(16, b"\x00")
        iname = b"LFS-Ayats Prototype"
        iname = iname[:16].ljust(16, b"\x00")

        packet = struct.pack(
            "<BBBBHHBBH16s16s",
            size,
            ISP_ISI,
            reqi,
            0,
            udp_port,
            flags,
            sp0,
            prefix,
            interval,
            admin,
            iname,
        )
        logger.debug("Sending IS_ISI initialisation packet: %s", packet)
        sock.sendall(packet)

    def close(self) -> None:
        """Close the underlying TCP socket."""

        if self._sock is not None:
            try:
                self._sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                self._sock.close()
                self._sock = None

    @property
    def connected(self) -> bool:
        """Return ``True`` if the client currently has an active socket."""

        return self._sock is not None

    # -- messaging ---------------------------------------------------------
    def send_command(self, message: str, req_id: int = 0) -> None:
        """Send a plain text command via an ``IS_MST`` packet."""

        if not message:
            raise ValueError("Command message must not be empty")
        if self._sock is None:
            raise RuntimeError("InSim socket is not connected")

        payload = message.encode("ascii", errors="ignore")[:63]
        payload = payload.ljust(64, b"\x00")
        packet = struct.pack(
            "<BBBBBBBB64s",
            68,  # packet size
            ISP_MST,
            req_id & 0xFF,
            0,
            0,
            0,
            0,
            0,
            payload,
        )
        logger.debug("Sending IS_MST command packet: %s", packet)
        self._sock.sendall(packet)

    def show_button(
        self,
        *,
        button_id: int,
        text: str,
        left: int,
        top: int,
        width: int,
        height: int,
        req_id: int = 0,
        ucid: int = 0,
        inst: int = 0,
        style: int = 0,
        type_in: int = 0,
    ) -> None:
        """Display or update an on-screen button using ``IS_BTN``."""

        if self._sock is None:
            raise RuntimeError("InSim socket is not connected")

        encoded_text = text.encode("latin-1", errors="ignore")[:239]
        payload = encoded_text + b"\x00"
        size = 12 + len(payload)
        if size > 255:
            raise ValueError("Button text is too long for an IS_BTN packet")

        packet = struct.pack(
            "<BBBBBBHBBBBB",
            size,
            ISP_BTN,
            req_id & 0xFF,
            ucid & 0xFF,
            button_id & 0xFF,
            inst & 0xFF,
            style & 0xFFFF,
            type_in & 0xFF,
            left & 0xFF,
            top & 0xFF,
            width & 0xFF,
            height & 0xFF,
        )
        logger.debug("Sending IS_BTN packet: %s (text=%r)", packet, text)
        self._sock.sendall(packet + payload)

    def delete_button(
        self,
        *,
        button_id: int = 0,
        req_id: int = 0,
        ucid: int = 0,
        inst: int = 0,
        clear_all: bool = False,
    ) -> None:
        """Remove a previously displayed button using ``IS_BFN``."""

        if self._sock is None:
            return

        bfn_type = 2 if clear_all else 0
        packet = struct.pack(
            "<BBBBBBBB",
            8,
            ISP_BFN,
            req_id & 0xFF,
            ucid & 0xFF,
            button_id & 0xFF,
            inst & 0xFF,
            bfn_type & 0xFF,
            0,
        )
        logger.debug("Sending IS_BFN packet: %s", packet)
        self._sock.sendall(packet)

    def add_state_listener(self, listener: Callable[["StateEvent"], None]) -> None:
        """Register a callback invoked for ``IS_STA`` packets."""

        self._state_listeners.append(listener)

    def add_lap_listener(self, listener: Callable[["LapEvent"], None]) -> None:
        """Register a callback invoked when an ``IS_LAP`` packet is received."""

        self._lap_listeners.append(listener)

    def add_split_listener(self, listener: Callable[["SplitEvent"], None]) -> None:
        """Register a callback invoked when an ``IS_SPX`` packet is received."""

        self._split_listeners.append(listener)

    def add_button_listener(self, listener: Callable[["ButtonClickEvent"], None]) -> None:
        """Register a callback invoked when an ``IS_BTC`` packet is received."""

        self._button_listeners.append(listener)

    def add_mci_listener(self, listener: Callable[["MultiCarInfoEvent"], None]) -> None:
        """Register a callback invoked when an ``IS_MCI`` packet is received."""

        self._mci_listeners.append(listener)

    def poll(self) -> None:
        """Poll the socket for incoming packets and dispatch them."""

        if self._sock is None:
            return

        ready, _, _ = select.select([self._sock], [], [], 0)
        if not ready:
            return

        try:
            data = self._sock.recv(4096)
        except BlockingIOError:
            return

        if not data:
            logger.info("InSim connection closed by remote host")
            self.close()
            return

        self._append_to_buffer(data)
        self._process_buffer()

    # -- internal helpers ------------------------------------------------
    def _append_to_buffer(self, data: bytes) -> None:
        if self._buffer_limit <= 0:
            self._buffer.clear()
            return

        if not data:
            return

        total_len = len(self._buffer) + len(data)
        if total_len <= self._buffer_limit:
            self._buffer.extend(data)
            return

        discard = total_len - self._buffer_limit
        logger.warning("Discarded %d bytes from InSim buffer to enforce limit", discard)

        if discard >= len(self._buffer):
            discard_from_data = discard - len(self._buffer)
            self._buffer.clear()
            if discard_from_data >= len(data):
                self._buffer.extend(data[-self._buffer_limit :])
            else:
                self._buffer.extend(data[discard_from_data:])
        else:
            del self._buffer[:discard]
            self._buffer.extend(data)

        if self._buffer:
            self._discard_until_valid_header(require_complete=True)

    def _process_buffer(self) -> None:
        while self._buffer:
            if not self._discard_until_valid_header(require_complete=False):
                return

            if len(self._buffer) < 2:
                return

            packet_size = self._buffer[0]
            if packet_size == 0:
                logger.warning("Encountered zero-length packet in InSim buffer")
                self._buffer.clear()
                return

            if packet_size > len(self._buffer):
                return

            packet = bytes(self._buffer[:packet_size])
            del self._buffer[:packet_size]
            self._handle_packet(packet)

    def _discard_until_valid_header(self, *, require_complete: bool) -> bool:
        while self._buffer:
            offset = self._scan_for_valid_packet_start(require_complete=require_complete)
            if offset is None:
                dropped = len(self._buffer)
                if dropped:
                    logger.warning(
                        "Cleared InSim buffer after discarding %d bytes with no valid packet header",
                        dropped,
                    )
                self._buffer.clear()
                return False

            if offset:
                del self._buffer[:offset]
                logger.warning(
                    "Discarded %d additional bytes from InSim buffer due to invalid packet header",
                    offset,
                )
                continue

            if len(self._buffer) < 2:
                return False

            packet_size = self._buffer[0]
            packet_type = self._buffer[1]
            header_valid, reason = self._validator.validate_header(packet_size, packet_type)
            if not header_valid:
                discard = 2 if len(self._buffer) >= 2 else 1
                type_name = self._validator.get_type_name(packet_type)
                logger.warning(
                    "Discarded %d byte(s) from InSim buffer due to invalid %s header: %s",
                    discard,
                    type_name,
                    reason,
                )
                del self._buffer[:discard]
                continue

            if require_complete and packet_size > len(self._buffer):
                # No complete packet is available yet.
                return False

            return True

        return False

    def _scan_for_valid_packet_start(self, *, require_complete: bool) -> Optional[int]:
        buffer_len = len(self._buffer)
        for offset in range(buffer_len):
            packet_size = self._buffer[offset]
            if packet_size == 0:
                continue

            remaining = buffer_len - offset
            if remaining < 2:
                break

            packet_type = self._buffer[offset + 1]
            if packet_type not in _KNOWN_PACKET_TYPES:
                continue

            if packet_size < 4:
                continue

            if require_complete and packet_size > remaining:
                continue

            if not require_complete and packet_size > self._buffer_limit:
                continue

            return offset

        return None

    def _handle_packet(self, packet: bytes) -> None:
        if len(packet) < 2:
            logger.debug("Dropping truncated InSim packet: %s", packet)
            return

        packet_type = packet[1]
        is_valid, reason = self._validator.validate(packet)
        if not is_valid:
            type_name = self._validator.get_type_name(packet_type)
            logger.warning("Rejecting %s packet: %s", type_name, reason)
            return
        if packet_type == ISP_VER:
            self._handle_is_ver(packet)
        elif packet_type == ISP_STA:
            self._handle_is_sta(packet)
        elif packet_type == ISP_NPL:
            self._handle_is_npl(packet)
        elif packet_type == ISP_LAP:
            event = self._parse_lap_packet(packet)
            if event:
                event.track = self._current_track
                car = self._plid_to_car.get(event.plid)
                if car is None and self._view_plid is not None and event.plid == self._view_plid:
                    car = self._current_car
                event.car = car
                for listener in list(self._lap_listeners):
                    try:
                        listener(event)
                    except Exception:  # pragma: no cover - defensive logging
                        logger.exception("Error while handling InSim lap listener")
        elif packet_type == ISP_SPX:
            event = self._parse_split_packet(packet)
            if event:
                event.track = self._current_track
                car = self._plid_to_car.get(event.plid)
                if car is None and self._view_plid is not None and event.plid == self._view_plid:
                    car = self._current_car
                event.car = car
                for listener in list(self._split_listeners):
                    try:
                        listener(event)
                    except Exception:  # pragma: no cover - defensive logging
                        logger.exception("Error while handling InSim split listener")
        elif packet_type == ISP_BTC:
            event = self._parse_button_click_packet(packet)
            if event:
                for listener in list(self._button_listeners):
                    try:
                        listener(event)
                    except Exception:  # pragma: no cover - defensive logging
                        logger.exception("Error while handling InSim button listener")
        elif packet_type == ISP_MCI:
            event = self._parse_mci_packet(packet)
            if event and self._mci_listeners:
                event.view_plid = self._view_plid
                for listener in list(self._mci_listeners):
                    try:
                        listener(event)
                    except Exception:  # pragma: no cover - defensive logging
                        logger.exception("Error while handling InSim MCI listener")

    def _handle_is_ver(self, packet: bytes) -> None:
        payload = packet[4:20]
        try:
            decoded = payload.decode("ascii", errors="ignore").rstrip("\x00")
        except Exception:
            decoded = ""

        if decoded:
            logger.debug("Received IS_VER handshake: %s", decoded)
        else:
            logger.debug("Received IS_VER handshake payload: %s", payload)

    def _handle_is_sta(self, packet: bytes) -> None:
        # IS_STA packets are 28 bytes long in current protocol versions.
        if len(packet) < 20:
            logger.debug("Dropping incomplete IS_STA packet: %s", packet)
            return

        # Flags2 is stored as a 16-bit little endian value starting at offset 16.
        flags2 = struct.unpack_from("<H", packet, 16)[0]
        self._last_flags2 = flags2

        view_plid = packet[10] if len(packet) > 10 else 0
        self._view_plid = view_plid or None

        track: Optional[str] = None
        if len(packet) >= 26:
            track_bytes = packet[20:26]
            track = (
                track_bytes.split(b"\x00", 1)[0].decode("ascii", errors="ignore").strip() or None
            )

        if track:
            self._current_track = track

        car: Optional[str] = None
        if self._view_plid is not None:
            car = self._plid_to_car.get(self._view_plid)

        if car:
            self._current_car = car

        event = StateEvent(
            flags2=flags2,
            track=self._current_track,
            car=self._current_car,
            view_plid=self._view_plid,
        )
        for listener in list(self._state_listeners):
            try:
                listener(event)
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Error while handling InSim state listener")

    def _handle_is_npl(self, packet: bytes) -> None:
        if len(packet) < 44:
            logger.debug("Dropping incomplete IS_NPL packet: %s", packet)
            return

        plid = packet[3]
        car_bytes = packet[40:44]
        car = car_bytes.split(b"\x00", 1)[0].decode("ascii", errors="ignore").strip()

        if not car:
            return

        self._plid_to_car[plid] = car
        if self._view_plid is not None and plid == self._view_plid:
            self._current_car = car

        event = StateEvent(
            flags2=self._last_flags2,
            track=self._current_track,
            car=self._current_car,
            view_plid=self._view_plid,
        )
        for listener in list(self._state_listeners):
            try:
                listener(event)
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Error while handling InSim state listener")

    def _parse_lap_packet(self, packet: bytes) -> Optional["LapEvent"]:
        if len(packet) < 4 + 8 + 2:
            logger.debug("Dropping incomplete IS_LAP packet: %s", packet)
            return None

        size = packet[0]
        if len(packet) < size:
            logger.debug("Dropping truncated IS_LAP packet: %s", packet)
            return None

        _, _, _, plid = struct.unpack_from("<BBBB", packet)
        lap_time, est_time = struct.unpack_from("<II", packet, 4)
        flags = struct.unpack_from("<H", packet, 12)[0]

        offset = 14
        sp0 = packet[offset]
        offset += 1
        penalty = packet[offset]
        offset += 1
        num_stops = packet[offset]
        offset += 1
        fuel_200 = packet[offset]
        offset += 1

        remaining = size - offset
        if remaining <= 0:
            logger.error("IS_LAP packet missing player name segment")
            return None

        spare = 0
        if remaining < 24:
            logger.error(
                "IS_LAP packet contains truncated player name segment (%d bytes)",
                remaining,
            )
            return None

        if remaining > 24:
            spare = packet[offset]
            offset += 1
            remaining -= 1
            if remaining < 24:
                logger.error(
                    "IS_LAP packet missing player name after spare byte (remaining=%d)",
                    remaining,
                )
                return None

        name_bytes = packet[offset : offset + 24]
        player_name = name_bytes.split(b"\x00", 1)[0].decode("latin-1", errors="ignore").strip()

        return LapEvent(
            plid=plid,
            lap_time_ms=lap_time,
            estimate_time_ms=est_time,
            flags=flags,
            penalty=penalty,
            num_pit_stops=num_stops,
            fuel_percent=fuel_200,
            player_name=player_name,
            spare=spare,
            raw_sp0=sp0,
        )

    def _parse_split_packet(self, packet: bytes) -> Optional["SplitEvent"]:
        if len(packet) < 4 + 8 + 2:
            logger.debug("Dropping incomplete IS_SPX packet: %s", packet)
            return None

        size = packet[0]
        if len(packet) < size:
            logger.debug("Dropping truncated IS_SPX packet: %s", packet)
            return None

        _, _, _, plid = struct.unpack_from("<BBBB", packet)
        split_time, est_time = struct.unpack_from("<II", packet, 4)
        flags = struct.unpack_from("<H", packet, 12)[0]

        offset = 14
        split = packet[offset]
        offset += 1
        penalty = packet[offset]
        offset += 1
        num_stops = packet[offset]
        offset += 1
        fuel_200 = packet[offset]
        offset += 1

        remaining = size - offset
        if remaining <= 0:
            logger.error("IS_SPX packet missing player name segment")
            return None

        spare = 0
        if remaining < 24:
            logger.error(
                "IS_SPX packet contains truncated player name segment (%d bytes)",
                remaining,
            )
            return None

        if remaining > 24:
            spare = packet[offset]
            offset += 1
            remaining -= 1
            if remaining < 24:
                logger.error(
                    "IS_SPX packet missing player name after spare byte (remaining=%d)",
                    remaining,
                )
                return None

        name_bytes = packet[offset : offset + 24]
        player_name = name_bytes.split(b"\x00", 1)[0].decode("latin-1", errors="ignore").strip()

        return SplitEvent(
            plid=plid,
            split_time_ms=split_time,
            estimate_time_ms=est_time,
            split_index=split,
            flags=flags,
            penalty=penalty,
            num_pit_stops=num_stops,
            fuel_percent=fuel_200,
            player_name=player_name,
            spare=spare,
        )

    def _parse_button_click_packet(self, packet: bytes) -> Optional["ButtonClickEvent"]:
        if len(packet) < 8:
            logger.debug("Dropping incomplete IS_BTC packet: %s", packet)
            return None

        size = packet[0]
        if len(packet) < size:
            logger.debug("Dropping truncated IS_BTC packet: %s", packet)
            return None

        req_id = packet[2]
        ucid = packet[3]
        click_id = packet[4]
        inst = packet[5]
        flags = struct.unpack_from("<H", packet, 6)[0]

        return ButtonClickEvent(
            req_id=req_id,
            ucid=ucid,
            click_id=click_id,
            inst=inst,
            flags=flags,
        )

    def _parse_mci_packet(self, packet: bytes) -> Optional["MultiCarInfoEvent"]:
        if len(packet) < 4:
            logger.debug("Dropping incomplete IS_MCI packet: %s", packet)
            return None

        count = packet[3]
        if count == 0:
            return MultiCarInfoEvent(cars=[])
        entry_size = 28
        required = 4 + count * entry_size
        if len(packet) < required:
            logger.debug(
                "Dropping truncated IS_MCI packet: expected at least %d bytes, got %d",
                required,
                len(packet),
            )
            return None

        cars: List[CarInfo] = []
        offset = 4
        for _ in range(count):
            if offset + entry_size > len(packet):
                logger.debug("Stopping IS_MCI parse due to truncated entry")
                break

            try:
                (
                    node,
                    lap,
                    plid,
                    position,
                    info,
                    spare,
                    x,
                    y,
                    z,
                    speed,
                    direction,
                    heading,
                    ang_vel,
                ) = struct.unpack_from("<HHBBBBiiiHHHh", packet, offset)
            except struct.error:
                logger.debug("Failed to unpack IS_MCI entry at offset %d", offset)
                break

            cars.append(
                CarInfo(
                    node=node,
                    lap=lap,
                    plid=plid,
                    position=position,
                    info=info,
                    spare=spare,
                    x=x,
                    y=y,
                    z=z,
                    speed=speed,
                    direction=direction,
                    heading=heading,
                    angular_velocity=ang_vel,
                )
            )
            offset += entry_size

        if not cars:
            return None

        return MultiCarInfoEvent(cars=cars)

    def __enter__(self) -> "InSimClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()


__all__ = [
    "InSimClient",
    "InSimConfig",
    "LapEvent",
    "SplitEvent",
    "StateEvent",
    "ButtonClickEvent",
    "CarInfo",
    "MultiCarInfoEvent",
    "PacketValidator",
    "ISS_MULTI",
    "ISP_NPL",
    "ISP_STA",
    "ISP_LAP",
    "ISP_SPX",
    "ISP_BTN",
    "ISP_BFN",
    "ISP_BTC",
    "ISP_MCI",
]
