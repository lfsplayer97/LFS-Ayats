"""Security and rate limiting tests for :mod:`src.outsim_client`."""

from __future__ import annotations

import logging
import struct
from typing import Sequence, Tuple

import pytest

from src.outsim_client import OutSimClient

_OUTSIM_STRUCT = struct.Struct("<I3f3f3f3f3f")


def _build_outsim_packet(time_ms: int) -> bytes:
    """Create a minimal but valid OutSim packet for the given timestamp."""

    return _OUTSIM_STRUCT.pack(
        time_ms,
        0.0,
        0.0,
        0.0,  # angular velocity
        0.0,
        1.0,
        0.0,  # heading (forward)
        0.0,
        0.0,
        0.0,  # acceleration
        0.0,
        0.0,
        0.0,  # velocity
        0.0,
        0.0,
        0.0,  # position
    )


class _FakeSocket:
    """Socket double that feeds predetermined packets to the client."""

    def __init__(self, packets: Sequence[Tuple[bytes, Tuple[str, int]]]):
        self._packets = list(packets)
        self._recv_calls = 0
        self.bound_to: Tuple[str, int] | None = None
        self.timeout: float | None = None
        self.closed = False

    def bind(self, address: Tuple[str, int]) -> None:
        self.bound_to = address

    def settimeout(self, timeout: float) -> None:
        self.timeout = timeout

    def recvfrom(self, buffer_size: int) -> Tuple[bytes, Tuple[str, int]]:
        if self._recv_calls >= len(self._packets):
            raise OSError("fake socket depleted")

        packet = self._packets[self._recv_calls]
        self._recv_calls += 1
        return packet

    def close(self) -> None:
        self.closed = True


class _FakeTime:
    """Deterministic substitute for :mod:`time` used in rate limit tests."""

    def __init__(self, monotonic_values: Sequence[float]):
        self._values = iter(monotonic_values)
        self._last_value = 0.0

    def monotonic(self) -> float:
        try:
            value = next(self._values)
        except StopIteration:
            return self._last_value

        self._last_value = value
        return value


def test_outsim_client_rejects_disallowed_sources(monkeypatch, caplog) -> None:
    """Packets from IPs outside the whitelist are ignored and logged."""

    packet = _build_outsim_packet(1337)
    fake_socket = _FakeSocket(
        [
            (packet, ("10.0.0.1", 1111)),
            (packet, ("192.168.0.42", 2222)),
        ]
    )

    monkeypatch.setattr("src.outsim_client.socket.socket", lambda *args, **kwargs: fake_socket)

    client = OutSimClient(port=29999, allowed_sources=["192.168.0.0/24"])
    client.start()

    caplog.set_level(logging.WARNING)
    frame_iter = client.frames()

    frame = next(frame_iter)
    assert frame.time_ms == 1337

    warning_messages = [record.getMessage() for record in caplog.records]
    assert any("disallowed source" in message for message in warning_messages)

    client.close()


def test_outsim_client_validates_allowed_source_entries() -> None:
    """Misconfigured allowed sources raise early errors."""

    with pytest.raises(ValueError, match="Invalid OutSim allowed source"):
        OutSimClient(port=30100, allowed_sources=["this-is-not-an-ip"])

    with pytest.raises(ValueError, match="No valid OutSim allowed sources"):
        OutSimClient(port=30101, allowed_sources=["   ", "\t\n"])


def test_outsim_client_rejects_empty_allowed_sources() -> None:
    """Explicit empty whitelists should fail fast instead of disabling checks."""

    with pytest.raises(ValueError, match="No valid OutSim allowed sources"):
        OutSimClient(port=30104, allowed_sources=[])


def test_outsim_client_rejects_invalid_rate_limits() -> None:
    """Zero or negative rate limits are rejected."""

    with pytest.raises(ValueError, match="rate limit must be positive"):
        OutSimClient(port=30102, max_packets_per_second=0)

    with pytest.raises(ValueError, match="rate limit must be positive"):
        OutSimClient(port=30103, max_packets_per_second=-5)


def test_outsim_client_enforces_packet_rate_limit(monkeypatch, caplog) -> None:
    """Packets beyond the configured rate are dropped and reported."""

    packet = _build_outsim_packet(42)
    fake_socket = _FakeSocket(
        [
            (packet, ("192.168.1.10", 3333)),
            (packet, ("192.168.1.10", 3333)),
        ]
    )

    fake_time = _FakeTime([0.0, 0.0, 0.1])

    monkeypatch.setattr("src.outsim_client.socket.socket", lambda *args, **kwargs: fake_socket)
    monkeypatch.setattr("src.outsim_client.time", fake_time)

    client = OutSimClient(
        port=30000,
        allowed_sources=["192.168.1.0/24"],
        max_packets_per_second=1.0,
    )
    client.start()

    caplog.set_level(logging.WARNING)
    frame_iter = client.frames()

    first_frame = next(frame_iter)
    assert first_frame.time_ms == 42

    with pytest.raises(OSError):
        next(frame_iter)

    warning_messages = [record.getMessage() for record in caplog.records]
    assert any("rate limit" in message for message in warning_messages)

    client.close()
