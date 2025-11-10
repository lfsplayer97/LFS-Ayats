"""
Telemetry endpoints for real-time data streaming.

Provides WebSocket endpoint for live telemetry and range queries.
"""

import logging
import asyncio
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query

from src.api.models import LiveTelemetryMessage, WebSocketError, TelemetryPoint
from src.api.dependencies import get_repository
from src.database.repository import TelemetryRepository

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for live telemetry."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")


manager = ConnectionManager()


@router.websocket("/live")
async def telemetry_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for live telemetry streaming.

    Streams real-time telemetry data to connected clients at ~10Hz.
    Clients receive JSON messages with current telemetry data.

    Protocol:
        - Connect to: ws://host:port/api/v1/telemetry/live
        - Receive: JSON messages with telemetry data
        - Send: No messages needed (receive-only)

    Example message:
        {
            "type": "telemetry",
            "data": {
                "timestamp": 123.45,
                "speed": 180.5,
                "rpm": 7500,
                ...
            },
            "session_id": 42
        }
    """
    await manager.connect(websocket)

    try:
        while True:
            # In a real implementation, this would get data from TelemetryCollector
            # For now, send a mock message
            await asyncio.sleep(0.1)  # 10Hz update rate

            # Mock telemetry data
            telemetry_data = TelemetryPoint(
                timestamp=datetime.now().timestamp(),
                speed=120.0,
                rpm=5000,
                gear=3,
                throttle=0.8,
                brake=0.0,
                steering=0.1,
                position_x=100.0,
                position_y=200.0,
                position_z=10.0,
            )

            message = LiveTelemetryMessage(
                type="telemetry", data=telemetry_data, session_id=None
            )

            await websocket.send_json(message.model_dump())

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        error_message = WebSocketError(type="error", error=str(e), code=500)
        try:
            await websocket.send_json(error_message.model_dump())
        except:
            pass


@router.get("/range")
async def get_telemetry_range(
    session_id: int = Query(..., description="Session ID"),
    start_time: float = Query(..., description="Start timestamp"),
    end_time: float = Query(..., description="End timestamp"),
    repo: TelemetryRepository = Depends(get_repository),
):
    """
    Get telemetry data for a time range.

    Retrieves telemetry points within a specific time range for a session.

    Args:
        session_id: Session ID
        start_time: Start timestamp (seconds)
        end_time: End timestamp (seconds)
        repo: Database repository

    Returns:
        dict: Telemetry data points in range
    """
    logger.info(
        f"Getting telemetry range for session {session_id}: "
        f"{start_time} to {end_time}"
    )

    # In a real implementation, this would query the database
    # For now, return a simple response
    return {
        "session_id": session_id,
        "start_time": start_time,
        "end_time": end_time,
        "points": [],
        "count": 0,
    }
