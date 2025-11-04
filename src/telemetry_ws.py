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
from dataclasses import dataclass, field
from typing import List, Optional

from .insim_client import CarInfo, MultiCarInfoEvent
from .outsim_client import OutSimFrame
from .radar import RadarTarget, compute_radar_targets

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
    player: Optional[dict]
    radar_targets: List[dict] = field(default_factory=list)


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


_INSIM_DISTANCE_SCALE = 65_536.0
_INSIM_SPEED_SCALE = 100.0


def _car_to_dict(car: CarInfo) -> dict:
    x = car.x / _INSIM_DISTANCE_SCALE
    y = car.y / _INSIM_DISTANCE_SCALE
    z = car.z / _INSIM_DISTANCE_SCALE
    speed = car.speed / _INSIM_SPEED_SCALE

    return {
        "plid": car.plid,
        "node": car.node,
        "lap": car.lap,
        "position": car.position,
        "info": car.info,
        "spare": car.spare,
        "x": x,
        "y": y,
        "z": z,
        "speed": speed,
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
        self._player_lap_progress: Optional[float] = None
        self._player_current_lap_ms: Optional[int] = None
        self._player_reference_lap_ms: Optional[int] = None
        self._player_delta_ms: Optional[int] = None
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

    def update_player_lap(
        self,
        *,
        progress: Optional[float],
        current_lap_ms: Optional[int],
        reference_lap_ms: Optional[int],
        delta_ms: Optional[int],
    ) -> None:
        with self._lock:
            self._player_lap_progress = progress
            self._player_current_lap_ms = current_lap_ms
            self._player_reference_lap_ms = reference_lap_ms
            self._player_delta_ms = delta_ms

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
            lap_progress = self._player_lap_progress
            lap_time_ms = self._player_current_lap_ms
            lap_reference_ms = self._player_reference_lap_ms
            lap_delta_ms = self._player_delta_ms

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

        player_payload: Optional[dict]
        radar_targets_payload: List[dict] = []
        if (
            focused_payload is None
            and frame is None
            and lap_progress is None
            and lap_time_ms is None
            and lap_reference_ms is None
            and lap_delta_ms is None
        ):
            player_payload = None
        else:
            player_payload = {}
            if frame is not None:
                px, py, pz = frame.position
                yaw, pitch, roll = frame.yaw_pitch_roll
                player_payload.update(
                    {
                        "x": px,
                        "y": py,
                        "z": pz,
                        "position": {"x": px, "y": py, "z": pz},
                        "heading_vector": list(frame.heading),
                        "velocity": list(frame.velocity),
                        "speed": frame.speed,
                    }
                )
                player_payload["heading"] = yaw
                player_payload["orientation"] = {
                    "yaw": yaw,
                    "pitch": pitch,
                    "roll": roll,
                }
                player_payload["time_ms"] = frame.time_ms

                other_positions: List[tuple[float, float]] = []
                for entry in cars:
                    if focus is not None and entry.plid == focus:
                        continue
                    other_positions.append(
                        (
                            entry.x / _INSIM_DISTANCE_SCALE,
                            entry.y / _INSIM_DISTANCE_SCALE,
                        )
                    )
                if other_positions:
                    targets: List[RadarTarget] = compute_radar_targets(
                        (px, py),
                        yaw,
                        other_positions,
                    )
                    radar_targets_payload = [
                        {
                            "distance": target.distance,
                            "bearing": target.bearing,
                            "offset": {"x": target.offset_x, "y": target.offset_y},
                        }
                        for target in targets
                    ]
                    if radar_targets_payload:
                        player_payload["radar_targets"] = radar_targets_payload
            if focused_payload is not None:
                for key in ("plid", "lap", "position"):
                    value = focused_payload.get(key)
                    if value is not None:
                        player_payload[key] = value
                for coord_key in ("x", "y", "z"):
                    if coord_key not in player_payload or not isinstance(
                        player_payload[coord_key], (int, float)
                    ):
                        value = focused_payload.get(coord_key)
                        if value is not None:
                            player_payload[coord_key] = value
                if "heading" not in player_payload:
                    heading_value = focused_payload.get("heading")
                    if heading_value is not None:
                        player_payload["heading"] = heading_value
                fallback_speed = focused_payload.get("speed")
                if fallback_speed is not None and "speed" not in player_payload:
                    player_payload["speed"] = fallback_speed

            lap_section: dict[str, object] = {}
            if focused_payload is not None:
                lap_value = focused_payload.get("lap")
                if lap_value is not None:
                    lap_section["number"] = lap_value
                race_pos = focused_payload.get("position")
                if race_pos is not None:
                    lap_section["race_position"] = race_pos
            if lap_progress is not None:
                clamped_progress = max(0.0, min(lap_progress, 1.0))
                lap_section["progress"] = clamped_progress
                player_payload["lap_progress"] = clamped_progress
            if lap_time_ms is not None:
                lap_section["current_ms"] = lap_time_ms
                player_payload["lap_time_ms"] = lap_time_ms
            if lap_reference_ms is not None:
                lap_section["reference_ms"] = lap_reference_ms
            if lap_delta_ms is not None:
                lap_section["delta_ms"] = lap_delta_ms
                player_payload["delta_ms"] = lap_delta_ms
                player_payload["delta"] = lap_delta_ms / 1000.0

            if lap_section:
                player_payload["lap"] = lap_section

            if not player_payload:
                player_payload = None

        return TelemetrySnapshot(
            timestamp=time.time(),
            outsim=outsim_payload,
            cars=car_payloads,
            focused_car=focused_payload,
            track=track,
            car=car,
            player=player_payload,
            radar_targets=radar_targets_payload,
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
