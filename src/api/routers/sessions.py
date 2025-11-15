"""
Session endpoints for managing telemetry sessions.

Provides CRUD operations for telemetry sessions.
"""

import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query

from src.api.models import SessionResponse, SessionCreate, SessionListResponse
from src.api.dependencies import get_repository
from src.api.exceptions import SessionNotFoundError, InvalidParameterError
from src.database.repository import TelemetryRepository
from src.database import models as db_models

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    circuit: Optional[str] = Query(None, description="Filter by circuit name"),
    vehicle: Optional[str] = Query(None, description="Filter by vehicle name"),
    driver: Optional[str] = Query(None, description="Filter by driver name"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset for pagination"),
    repo: TelemetryRepository = Depends(get_repository),
):
    """
    List telemetry sessions with optional filters.

    Supports pagination and filtering by circuit, vehicle, driver, and date range.

    Args:
        circuit: Optional circuit name filter
        vehicle: Optional vehicle name filter
        driver: Optional driver name filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        limit: Maximum number of results (1-100)
        offset: Offset for pagination
        repo: Database repository

    Returns:
        SessionListResponse: Paginated list of sessions
    """
    logger.info(
        f"Listing sessions: circuit={circuit}, vehicle={vehicle}, "
        f"driver={driver}, limit={limit}, offset={offset}"
    )

    # Get sessions from repository
    sessions = repo.get_sessions(
        circuit=circuit, vehicle=vehicle, driver=driver, limit=limit, offset=offset
    )

    # Convert to response models
    session_responses = []
    for session in sessions:
        session_responses.append(
            SessionResponse(
                id=session.id,
                circuit=session.circuit.name if session.circuit else "Unknown",
                vehicle=session.vehicle.name if session.vehicle else "Unknown",
                driver=session.driver_name,
                datetime=session.datetime,
                duration=session.duration,
                total_laps=len(session.laps) if session.laps else 0,
                best_lap_time=(
                    min(lap.lap_time for lap in session.laps) if session.laps else None
                ),
            )
        )

    return SessionListResponse(
        total=len(session_responses),
        items=session_responses,
        page=offset // limit,
        page_size=limit,
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int, repo: TelemetryRepository = Depends(get_repository)
):
    """
    Get detailed session information.

    Retrieves complete information about a specific session.

    Args:
        session_id: Session ID
        repo: Database repository

    Returns:
        SessionResponse: Session details

    Raises:
        SessionNotFoundError: If session not found
    """
    logger.info(f"Getting session {session_id}")

    session = repo.get_session(session_id)
    if not session:
        raise SessionNotFoundError(session_id)

    return SessionResponse(
        id=session.id,
        circuit=session.circuit.name if session.circuit else "Unknown",
        vehicle=session.vehicle.name if session.vehicle else "Unknown",
        driver=session.driver_name,
        datetime=session.datetime,
        duration=session.duration,
        total_laps=len(session.laps) if session.laps else 0,
        best_lap_time=(
            min(lap.lap_time for lap in session.laps) if session.laps else None
        ),
    )


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate, repo: TelemetryRepository = Depends(get_repository)
):
    """
    Create new telemetry session.

    Creates a new session for manual data import or initialization.

    Args:
        session_data: Session creation data
        repo: Database repository

    Returns:
        SessionResponse: Created session details
    """
    logger.info(f"Creating session for driver {session_data.driver}")

    # Get or create circuit and vehicle
    circuit = repo.get_or_create_circuit(
        name=session_data.circuit, short_name=session_data.circuit[:10]
    )
    vehicle = repo.get_or_create_vehicle(
        name=session_data.vehicle, short_name=session_data.vehicle[:10]
    )

    # Create session using repository method
    session_id = repo.save_session(
        datetime_start=session_data.datetime or datetime.now(),
        circuit_name=circuit.short_name,
        vehicle_name=vehicle.short_name,
        driver_name=session_data.driver,
        duration=0,
    )

    created_session = repo.get_session(session_id)

    return SessionResponse(
        id=created_session.id,
        circuit=created_session.circuit.name if created_session.circuit else "Unknown",
        vehicle=created_session.vehicle.name if created_session.vehicle else "Unknown",
        driver=created_session.driver_name or "Unknown",
        datetime=created_session.datetime,
        duration=created_session.duration or 0,
        total_laps=0,
        best_lap_time=None,
    )


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: int, repo: TelemetryRepository = Depends(get_repository)
):
    """
    Delete a session.

    Removes a session and all associated data from the database.

    Args:
        session_id: Session ID to delete
        repo: Database repository

    Raises:
        SessionNotFoundError: If session not found
    """
    logger.info(f"Deleting session {session_id}")

    session = repo.get_session(session_id)
    if not session:
        raise SessionNotFoundError(session_id)

    repo.delete_session(session_id)
    return None
