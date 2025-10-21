from __future__ import annotations

"""Asynchronous telemetry broadcaster that exposes a simple WebSocket feed."""

import asyncio
import base64
import contextlib
import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass
from typing import List, Optional

from .insim_client import CarInfo, MultiCarInfoEvent
from .outsim_client import OutSimFrame

logger = logging.getLogger(__name__)

_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


@dataclass
class TelemetrySnapshot:
    """Materialised view of the most recent telemetry samples."""

    timestamp: float
    outsim: Optional[dict]
    cars: List[dict]
    focused_car: Optional[dict]
    track: Optional[str]
    car: Optional[str]


def _outsim_to_dict(frame: OutSimFrame) -> dict:
    return {
        "time_ms": frame.time_ms,
        "ang_vel": list(frame.ang_vel),
        "heading": list(frame.heading),
        "acceleration": list(frame.acceleration),
        "velocity": list(frame.velocity),
        "position": list(frame.position),
        "speed": frame.speed,
    }


def _car_to_dict(car: CarInfo) -> dict:
    return {
        "plid": car.plid,
        "node": car.node,
        "lap": car.lap,
        "position": car.position,
        "info": car.info,
        "spare": car.spare,
        "x": car.x,
        "y": car.y,
        "z": car.z,
        "speed": car.speed,
        "direction": car.direction,
        "heading": car.heading,
        "angular_velocity": car.angular_velocity,
    }


def _encode_ws_frame(payload: bytes) -> bytes:
    header = bytearray()
    header.append(0x81)  # FIN bit set, text frame
    length = len(payload)
    if length < 126:
        header.append(length)
    elif length < 65536:
        header.append(126)
        header.extend(length.to_bytes(2, "big"))
    else:
        header.append(127)
        header.extend(length.to_bytes(8, "big"))
    return bytes(header) + payload


class TelemetryBroadcaster:
    """Broadcasts telemetry snapshots to WebSocket clients at a fixed cadence."""

    def __init__(self, host: str, port: int, *, update_hz: float = 15.0) -> None:
        if update_hz <= 0:
            raise ValueError("update_hz must be positive")
        capped_hz = min(update_hz, 60.0)
        self._interval = 1.0 / capped_hz
        self._host = host
        self._port = port
        self._latest_frame: Optional[OutSimFrame] = None
        self._latest_cars: List[CarInfo] = []
        self._focus_plid: Optional[int] = None
        self._track: Optional[str] = None
        self._car: Optional[str] = None
        self._lock = threading.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._shutdown_future: Optional[asyncio.Future[None]] = None
        self._server: Optional[asyncio.AbstractServer] = None
        self._broadcast_task: Optional[asyncio.Task[None]] = None
        self._clients: set[asyncio.StreamWriter] = set()

    # -- public API -----------------------------------------------------
    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        def runner() -> None:
            assert self._loop is not None
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_until_complete(self._run())
            finally:
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
                self._loop.close()
                self._loop = None

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=runner, name="telemetry-ws", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        loop = self._loop
        if loop is not None and not loop.is_closed():
            loop.call_soon_threadsafe(self._request_shutdown)
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

    def update_outsim(self, frame: OutSimFrame) -> None:
        with self._lock:
            self._latest_frame = frame

    def update_mci(self, event: MultiCarInfoEvent) -> None:
        with self._lock:
            self._latest_cars = list(event.cars)
            if event.view_plid is not None:
                self._focus_plid = event.view_plid

    def set_focus_plid(self, plid: Optional[int]) -> None:
        with self._lock:
            self._focus_plid = plid

    def update_track_context(self, track: Optional[str], car: Optional[str]) -> None:
        with self._lock:
            self._track = track
            self._car = car

    # -- asyncio internals ---------------------------------------------
    async def _run(self) -> None:
        self._shutdown_future = self._loop.create_future()
        try:
            self._server = await asyncio.start_server(self._handle_client, self._host, self._port)
        except OSError:
            logger.exception("Failed to bind telemetry WebSocket server on %s:%s", self._host, self._port)
            self._shutdown_future.set_result(None)
            return

        logger.info("Telemetry WebSocket listening on ws://%s:%s", self._host, self._port)
        self._broadcast_task = self._loop.create_task(self._broadcast_loop())
        try:
            await self._shutdown_future
        finally:
            if self._broadcast_task:
                self._broadcast_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._broadcast_task
            if self._server:
                self._server.close()
                await self._server.wait_closed()
            for writer in list(self._clients):
                writer.close()
                with contextlib.suppress(Exception):
                    await writer.wait_closed()
            self._loop.stop()

    def _request_shutdown(self) -> None:
        if self._shutdown_future and not self._shutdown_future.done():
            self._shutdown_future.set_result(None)

    async def _broadcast_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._interval)
                snapshot = self._build_snapshot()
                if snapshot is None:
                    continue
                payload = json.dumps(snapshot.__dict__, separators=(",", ":")).encode("utf-8")
                frame = _encode_ws_frame(payload)
                stale: List[asyncio.StreamWriter] = []
                for writer in list(self._clients):
                    try:
                        writer.write(frame)
                        await writer.drain()
                    except Exception:
                        stale.append(writer)
                for writer in stale:
                    self._clients.discard(writer)
                    writer.close()
                    with contextlib.suppress(Exception):
                        await writer.wait_closed()
        except asyncio.CancelledError:
            raise

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            request = await reader.readuntil(b"\r\n\r\n")
        except asyncio.IncompleteReadError:
            writer.close()
            await writer.wait_closed()
            return

        headers = self._parse_headers(request)
        key = headers.get("sec-websocket-key")
        if not key:
            writer.close()
            await writer.wait_closed()
            return

        accept = base64.b64encode(hashlib.sha1((key + _GUID).encode("ascii")).digest()).decode("ascii")
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
        )
        writer.write(response.encode("ascii"))
        try:
            await writer.drain()
        except ConnectionError:
            writer.close()
            await writer.wait_closed()
            return

        self._clients.add(writer)
        logger.info("Telemetry WebSocket client connected (%d active)", len(self._clients))
        await self._consume_client(reader, writer)

    async def _consume_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            while not reader.at_eof():
                data = await reader.read(2 ** 10)
                if not data:
                    break
        finally:
            self._clients.discard(writer)
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()
            logger.info("Telemetry WebSocket client disconnected (%d active)", len(self._clients))

    def _build_snapshot(self) -> Optional[TelemetrySnapshot]:
        with self._lock:
            frame = self._latest_frame
            cars = list(self._latest_cars)
            focus = self._focus_plid
            track = self._track
            car = self._car

        if frame is None and not cars:
            return None

        outsim_payload = _outsim_to_dict(frame) if frame is not None else None
        car_payloads = [_car_to_dict(entry) for entry in cars]
        focused_payload = None
        if focus is not None:
            for entry in cars:
                if entry.plid == focus:
                    focused_payload = _car_to_dict(entry)
                    break

        return TelemetrySnapshot(
            timestamp=time.time(),
            outsim=outsim_payload,
            cars=car_payloads,
            focused_car=focused_payload,
            track=track,
            car=car,
        )

    @staticmethod
    def _parse_headers(raw: bytes) -> dict:
        try:
            text = raw.decode("latin-1")
        except UnicodeDecodeError:
            return {}
        lines = text.split("\r\n")
        headers: dict[str, str] = {}
        for line in lines[1:]:
            if not line:
                continue
            if ":" not in line:
                continue
            name, value = line.split(":", 1)
            headers[name.strip().lower()] = value.strip()
        return headers


__all__ = ["TelemetryBroadcaster", "TelemetrySnapshot"]
