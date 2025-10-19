"""OutSim UDP client utilities."""

from __future__ import annotations

import ipaddress
import logging
import math
import socket
import struct
from dataclasses import dataclass
from typing import Collection, Iterable, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# The classic OutSim packet layout used by the LFS public demo and retail
# releases.  The message is always little endian.
_OUTSIM_STRUCT = struct.Struct("<I3f3f3f3f3f")


@dataclass
class OutSimFrame:
    """A parsed OutSim telemetry frame."""

    time_ms: int
    ang_vel: Tuple[float, float, float]
    heading: Tuple[float, float, float]
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
        heading = tuple(values[3:6])
        acceleration = tuple(values[6:9])
        velocity = tuple(values[9:12])
        position = tuple(values[12:15])
        return cls(
            time_ms=time_ms,
            ang_vel=ang_vel,  # type: ignore[arg-type]
            heading=heading,  # type: ignore[arg-type]
            acceleration=acceleration,  # type: ignore[arg-type]
            velocity=velocity,  # type: ignore[arg-type]
            position=position,  # type: ignore[arg-type]
        )

    @property
    def speed(self) -> float:
        vx, vy, vz = self.velocity
        return (vx * vx + vy * vy + vz * vz) ** 0.5

    @property
    def yaw_pitch_roll(self) -> Tuple[float, float, float]:
        """Orientation expressed as yaw, pitch and roll angles in radians."""

        hx, hy, hz = self.heading
        horizontal_mag = math.hypot(hx, hy)

        if horizontal_mag < 1e-12:
            yaw = 0.0
        else:
            yaw = math.atan2(hx, hy)

        if horizontal_mag < 1e-12:
            pitch = math.copysign(math.pi / 2, hz) if hz else 0.0
        else:
            pitch = math.atan2(hz, horizontal_mag)

        roll = 0.0
        return yaw, pitch, roll

    @property
    def yaw_pitch_roll_degrees(self) -> Tuple[float, float, float]:
        """Orientation expressed as yaw, pitch and roll angles in degrees."""

        return tuple(math.degrees(angle) for angle in self.yaw_pitch_roll)


class OutSimClient:
    """UDP client that yields :class:`OutSimFrame` objects.

    Parameters
    ----------
    port:
        Port to bind the UDP socket to.
    host:
        Host interface to bind the UDP socket to.  Defaults to ``"0.0.0.0"``.
    buffer_size:
        Size of the UDP receive buffer.
    timeout:
        Optional socket timeout in seconds.  When provided, the client will
        periodically wake up even if no packets are received.
    allowed_sources:
        Optional collection of IP addresses or CIDR networks that are allowed to
        feed data into the client.  When present, packets from other sources are
        ignored.
    """

    def __init__(
        self,
        port: int,
        host: str = "0.0.0.0",
        buffer_size: int = 256,
        timeout: Optional[float] = None,
        allowed_sources: Optional[Collection[str]] = None,
    ) -> None:
        self._host = host
        self._port = port
        self._buffer_size = buffer_size
        self._timeout = timeout
        self._sock: Optional[socket.socket] = None
        self._allowed_source_strings: Optional[Tuple[str, ...]] = (
            tuple(allowed_sources) if allowed_sources else None
        )
        self._allowed_networks: Optional[
            Tuple[Union[ipaddress.IPv4Network, ipaddress.IPv6Network], ...]
        ] = (
            self._normalise_allowed_sources(allowed_sources)
            if allowed_sources
            else None
        )

    @staticmethod
    def _normalise_allowed_sources(
        allowed_sources: Collection[str],
    ) -> Tuple[Union[ipaddress.IPv4Network, ipaddress.IPv6Network], ...]:
        networks = []
        for entry in allowed_sources:
            text = entry.strip()
            if not text:
                continue
            try:
                network = ipaddress.ip_network(text, strict=False)
            except ValueError as exc:
                raise ValueError(f"Invalid OutSim allowed source '{entry}': {exc}")
            networks.append(network)
        return tuple(networks)

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

            source_ip = addr[0]
            logger.debug("Received OutSim packet from %s", addr)

            if not self._is_source_allowed(source_ip):
                logger.warning(
                    "Discarding OutSim packet from disallowed source %s", source_ip
                )
                continue

            try:
                yield OutSimFrame.from_packet(data)
            except ValueError as exc:
                logger.warning("Discarding invalid OutSim packet: %s", exc)

    def _is_source_allowed(self, source_ip: str) -> bool:
        if self._allowed_networks is None:
            return True

        try:
            ip_obj = ipaddress.ip_address(source_ip)
        except ValueError:
            logger.warning(
                "Discarding OutSim packet from malformed source address %s",
                source_ip,
            )
            return False

        return any(ip_obj in network for network in self._allowed_networks)

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
