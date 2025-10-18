"""Client utilities for working with the Live for Speed InSim interface."""
from __future__ import annotations

import logging
import socket
import struct
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# -- InSim protocol helpers -------------------------------------------------

# InSim packet and flag constants.  Only the few flags that are relevant for
# enabling multiplayer-safe telemetry are included – additional flags can be
# added in the future as the prototype grows.
ISP_ISI = 1
ISP_MST = 11

ISF_MCI = 1 << 0  # receive multi car info packets
ISF_CON = 1 << 1  # receive contact packets
ISF_OBH = 1 << 2  # receive object hit packets


@dataclass
class InSimConfig:
    """Configuration values required to establish an InSim connection."""

    host: str
    port: int
    admin_password: str = ""
    interval_ms: int = 100
    timeout: Optional[float] = 5.0


class InSimClient:
    """Minimal TCP client for the Live for Speed InSim protocol."""

    def __init__(self, config: InSimConfig) -> None:
        self._config = config
        self._sock: Optional[socket.socket] = None

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

        size = 44
        reqi = 0
        udp_port = 0  # we are not using a UDP connection for InSim packets here
        flags = ISF_MCI | ISF_CON | ISF_OBH
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

    def __enter__(self) -> "InSimClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()


__all__ = ["InSimClient", "InSimConfig"]
