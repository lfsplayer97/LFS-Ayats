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
ISP_STA = 5
ISP_MST = 11
ISP_NPL = 21
ISP_LAP = 28
ISP_SPX = 29

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


class InSimClient:
    """Minimal TCP client for the Live for Speed InSim protocol."""

    def __init__(
        self,
        config: InSimConfig,
        *,
        state_listeners: Optional[List[Callable[["StateEvent"], None]]] = None,
        lap_listeners: Optional[List[Callable[["LapEvent"], None]]] = None,
        split_listeners: Optional[List[Callable[["SplitEvent"], None]]] = None,
    ) -> None:
        self._config = config
        self._sock: Optional[socket.socket] = None
        self._buffer = bytearray()
        self._state_listeners: List[Callable[["StateEvent"], None]] = []
        self._lap_listeners: List[Callable[["LapEvent"], None]] = []
        self._split_listeners: List[Callable[["SplitEvent"], None]] = []
        self._plid_to_car: dict[int, str] = {}
        self._current_track: Optional[str] = None
        self._current_car: Optional[str] = None
        self._view_plid: Optional[int] = None
        if state_listeners:
            self._state_listeners.extend(state_listeners)
        if lap_listeners:
            self._lap_listeners.extend(lap_listeners)
        if split_listeners:
            self._split_listeners.extend(split_listeners)

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

    def add_state_listener(self, listener: Callable[["StateEvent"], None]) -> None:
        """Register a callback invoked for ``IS_STA`` packets."""

        self._state_listeners.append(listener)

    def add_lap_listener(self, listener: Callable[["LapEvent"], None]) -> None:
        """Register a callback invoked when an ``IS_LAP`` packet is received."""

        self._lap_listeners.append(listener)

    def add_split_listener(self, listener: Callable[["SplitEvent"], None]) -> None:
        """Register a callback invoked when an ``IS_SPX`` packet is received."""

        self._split_listeners.append(listener)

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

        self._buffer.extend(data)
        self._process_buffer()

    # -- internal helpers ------------------------------------------------
    def _process_buffer(self) -> None:
        while len(self._buffer) >= 1:
            packet_size = self._buffer[0]
            if packet_size == 0:
                # Avoid infinite loops if malformed data is received.
                logger.warning("Encountered zero-length packet in InSim buffer")
                self._buffer.clear()
                return

            if len(self._buffer) < packet_size:
                return

            packet = bytes(self._buffer[:packet_size])
            del self._buffer[:packet_size]
            self._handle_packet(packet)

    def _handle_packet(self, packet: bytes) -> None:
        if len(packet) < 2:
            logger.debug("Dropping truncated InSim packet: %s", packet)
            return

        packet_type = packet[1]
        if packet_type == ISP_STA:
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

    def _handle_is_sta(self, packet: bytes) -> None:
        # IS_STA packets are 28 bytes long in current protocol versions.
        if len(packet) < 20:
            logger.debug("Dropping incomplete IS_STA packet: %s", packet)
            return

        # Flags2 is stored as a 16-bit little endian value starting at offset 16.
        flags2 = struct.unpack_from("<H", packet, 16)[0]

        view_plid = packet[10] if len(packet) > 10 else 0
        self._view_plid = view_plid or None

        track: Optional[str] = None
        if len(packet) >= 26:
            track_bytes = packet[20:26]
            track = track_bytes.split(b"\x00", 1)[0].decode("ascii", errors="ignore").strip() or None

        if track:
            self._current_track = track

        car: Optional[str] = None
        if self._view_plid is not None:
            car = self._plid_to_car.get(self._view_plid)

        if car:
            self._current_car = car

        event = StateEvent(flags2=flags2, track=self._current_track, car=self._current_car)
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

        event = StateEvent(flags2=0, track=self._current_track, car=self._current_car)
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
        sp0 = packet[offset] if size > offset else 0
        offset += 1
        penalty = packet[offset] if size > offset else 0
        offset += 1
        num_stops = packet[offset] if size > offset else 0
        offset += 1
        fuel_200 = packet[offset] if size > offset else 0
        offset += 1

        remaining = size - offset
        spare = 0
        if remaining > 24:
            spare = packet[offset]
            offset += 1
            remaining -= 1

        name_length = min(24, max(0, size - offset))
        name_bytes = packet[offset : offset + name_length]
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
        split = packet[offset] if size > offset else 0
        offset += 1
        penalty = packet[offset] if size > offset else 0
        offset += 1
        num_stops = packet[offset] if size > offset else 0
        offset += 1
        fuel_200 = packet[offset] if size > offset else 0
        offset += 1

        remaining = size - offset
        spare = 0
        if remaining > 24:
            spare = packet[offset]
            offset += 1
            remaining -= 1

        name_length = min(24, max(0, size - offset))
        name_bytes = packet[offset : offset + name_length]
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
    "ISS_MULTI",
    "ISP_NPL",
    "ISP_STA",
    "ISP_LAP",
    "ISP_SPX",
]
