"""OutSim UDP client utilities."""
from __future__ import annotations

import logging
import socket
import struct
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

logger = logging.getLogger(__name__)

# The classic OutSim packet layout used by the LFS public demo and retail
# releases.  The message is always little endian.
_OUTSIM_STRUCT = struct.Struct("<I3f3f3f3f3f")


@dataclass
class OutSimFrame:
    """A parsed OutSim telemetry frame."""

    time_ms: int
    ang_vel: Tuple[float, float, float]
    orientation: Tuple[float, float, float]  # heading, pitch, roll
    acceleration: Tuple[float, float, float]
    velocity: Tuple[float, float, float]
    position: Tuple[float, float, float]

    @classmethod
    def from_packet(cls, packet: bytes) -> "OutSimFrame":
        if len(packet) < _OUTSIM_STRUCT.size:
            raise ValueError(
                f"OutSim packet too small: expected {_OUTSIM_STRUCT.size} bytes, got {len(packet)}"
            )

        (time_ms, *values) = _OUTSIM_STRUCT.unpack_from(packet)
        ang_vel = tuple(values[0:3])  # type: ignore[assignment]
        orientation = tuple(values[3:6])  # heading, pitch, roll
        acceleration = tuple(values[6:9])
        velocity = tuple(values[9:12])
        position = tuple(values[12:15])
        return cls(
            time_ms=time_ms,
            ang_vel=ang_vel,  # type: ignore[arg-type]
            orientation=orientation,  # type: ignore[arg-type]
            acceleration=acceleration,  # type: ignore[arg-type]
            velocity=velocity,  # type: ignore[arg-type]
            position=position,  # type: ignore[arg-type]
        )

    @property
    def speed(self) -> float:
        vx, vy, vz = self.velocity
        return (vx * vx + vy * vy + vz * vz) ** 0.5


class OutSimClient:
    """UDP client that yields :class:`OutSimFrame` objects."""

    def __init__(self, port: int, host: str = "0.0.0.0", buffer_size: int = 256, timeout: Optional[float] = None) -> None:
        self._host = host
        self._port = port
        self._buffer_size = buffer_size
        self._timeout = timeout
        self._sock: Optional[socket.socket] = None

    def start(self) -> None:
        if self._sock is not None:
            logger.debug("Rebinding OutSim socket")
            self.close()

        logger.info("Binding OutSim UDP listener on %s:%s", self._host, self._port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self._host, self._port))
        if self._timeout is not None:
            sock.settimeout(self._timeout)
        self._sock = sock

    def frames(self) -> Iterable[OutSimFrame]:
        if self._sock is None:
            raise RuntimeError("OutSim socket has not been started")

        while True:
            try:
                data, addr = self._sock.recvfrom(self._buffer_size)
            except socket.timeout:
                logger.debug("OutSim socket timed out waiting for data")
                continue
            except OSError as exc:
                logger.debug("OutSim socket error: %s", exc)
                raise

            logger.debug("Received OutSim packet from %s", addr)
            try:
                yield OutSimFrame.from_packet(data)
            except ValueError as exc:
                logger.warning("Discarding invalid OutSim packet: %s", exc)

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            finally:
                self._sock = None

    def __enter__(self) -> "OutSimClient":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()


__all__ = ["OutSimClient", "OutSimFrame"]
