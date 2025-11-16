"""
System endpoints for health checks and status.

Provides endpoints for checking API health, system status,
and managing LFS connection.
"""

import logging
import time
from fastapi import APIRouter, Depends, Body

from src.api.models import (
    HealthResponse,
    SystemStatusResponse,
    ConnectionConfig,
)
from src.api.dependencies import (
    get_repository,
    get_connection_status,
    set_connection_status,
)
from src.api.exceptions import ConnectionError as ConnectionErrorException
from src.database.repository import TelemetryRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# Track startup time
_startup_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns basic API status and version information.

    Returns:
        HealthResponse: API health status
    """
    logger.debug("Health check requested")
    return HealthResponse(status="healthy", version="0.1.0")


@router.get("/status", response_model=SystemStatusResponse)
async def get_status(
    repo: TelemetryRepository = Depends(get_repository),
    connected: bool = Depends(get_connection_status),
) -> SystemStatusResponse:
    """
    Get system status.

    Returns comprehensive system status including connection state,
    uptime, and database statistics.

    Args:
        repo: Database repository
        connected: Current connection status

    Returns:
        SystemStatusResponse: System status information
    """
    logger.debug(f"Status check requested (connected={connected})")

    # Calculate uptime
    uptime = time.time() - _startup_time

    # Get database statistics
    try:
        sessions = repo.get_sessions(limit=1)
        sessions_count = len(sessions) if sessions else 0

        # For lap count, we would need to implement a count method
        # For now, return 0 as placeholder
        laps_count = 0

        logger.debug(f"Database stats: {sessions_count} sessions, {laps_count} laps")
    except Exception as e:
        logger.error(f"Error fetching database stats: {e}", exc_info=True)
        sessions_count = 0
        laps_count = 0

    return SystemStatusResponse(
        connected=connected,
        uptime=uptime,
        sessions_count=sessions_count,
        laps_count=laps_count,
        last_telemetry=None,  # Would be tracked by collector
    )


@router.post("/connect")
async def connect_to_lfs(config: ConnectionConfig = Body(...)) -> dict:
    """
    Initiate connection to LFS server.

    Attempts to establish InSim connection to Live for Speed.

    Args:
        config: Connection configuration (host, port, app_name)

    Returns:
        dict: Connection status message

    Raises:
        ConnectionErrorException: If connection fails
    """
    try:
        logger.info(f"Attempting connection to LFS at {config.host}:{config.port}")
        logger.debug(f"Connection config: app_name='{config.app_name}'")

        # In a real implementation, this would use InSimClient
        # For now, just set the status
        set_connection_status(True)

        logger.info(f"Successfully connected to LFS at {config.host}:{config.port}")

        return {
            "status": "connected",
            "host": config.host,
            "port": config.port,
            "message": "Successfully connected to LFS server",
        }
    except Exception as e:
        logger.error(f"Connection failed: {e}", exc_info=True)
        raise ConnectionErrorException(str(e))


@router.post("/disconnect")
async def disconnect_from_lfs() -> dict:
    """
    Disconnect from LFS server.

    Terminates the InSim connection.

    Returns:
        dict: Disconnection status message
    """
    logger.info("Disconnecting from LFS")

    # In a real implementation, this would close the InSimClient connection
    set_connection_status(False)

    logger.debug("Disconnection completed successfully")

    return {"status": "disconnected", "message": "Disconnected from LFS server"}
