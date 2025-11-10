"""
Lap endpoints for managing and comparing laps.

Provides operations for retrieving lap data and comparing performance.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, Query

from src.api.models import (
    LapResponse,
    LapListResponse,
    TelemetryResponse,
    TelemetryPoint,
    ComparisonRequest,
    ComparisonResponse,
)
from src.api.dependencies import get_repository
from src.api.exceptions import LapNotFoundError, SessionNotFoundError, InvalidParameterError
from src.database.repository import TelemetryRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{session_id}/laps", response_model=LapListResponse)
async def list_laps(
    session_id: int,
    repo: TelemetryRepository = Depends(get_repository),
):
    """
    List all laps in a session.

    Retrieves all laps recorded during a specific session.

    Args:
        session_id: Session ID
        repo: Database repository

    Returns:
        LapListResponse: List of laps

    Raises:
        SessionNotFoundError: If session not found
    """
    logger.info(f"Listing laps for session {session_id}")

    session = repo.get_session(session_id)
    if not session:
        raise SessionNotFoundError(session_id)

    laps = session.laps if session.laps else []

    lap_responses = []
    for lap in laps:
        lap_responses.append(
            LapResponse(
                id=lap.id,
                session_id=lap.session_id,
                lap_number=lap.lap_number,
                lap_time=lap.lap_time,
                sector1_time=lap.sector1_time,
                sector2_time=lap.sector2_time,
                sector3_time=lap.sector3_time,
                valid=True,  # Would check lap validity
            )
        )

    return LapListResponse(total=len(lap_responses), items=lap_responses)


@router.get("/{lap_id}", response_model=LapResponse)
async def get_lap(lap_id: int, repo: TelemetryRepository = Depends(get_repository)):
    """
    Get detailed lap information.

    Retrieves complete information about a specific lap.

    Args:
        lap_id: Lap ID
        repo: Database repository

    Returns:
        LapResponse: Lap details

    Raises:
        LapNotFoundError: If lap not found
    """
    logger.info(f"Getting lap {lap_id}")

    lap = repo.get_lap(lap_id)
    if not lap:
        raise LapNotFoundError(lap_id)

    return LapResponse(
        id=lap.id,
        session_id=lap.session_id,
        lap_number=lap.lap_number,
        lap_time=lap.lap_time,
        sector1_time=lap.sector1_time,
        sector2_time=lap.sector2_time,
        sector3_time=lap.sector3_time,
        valid=True,
    )


@router.get("/{lap_id}/telemetry", response_model=TelemetryResponse)
async def get_lap_telemetry(
    lap_id: int,
    sample_rate: int = Query(
        None, ge=1, le=100, description="Optional downsampling rate (Hz)"
    ),
    repo: TelemetryRepository = Depends(get_repository),
):
    """
    Get telemetry data for a lap.

    Retrieves all telemetry points recorded during a specific lap.
    Supports optional downsampling for reduced data transfer.

    Args:
        lap_id: Lap ID
        sample_rate: Optional downsampling rate (Hz)
        repo: Database repository

    Returns:
        TelemetryResponse: Telemetry data points

    Raises:
        LapNotFoundError: If lap not found
    """
    logger.info(f"Getting telemetry for lap {lap_id}, sample_rate={sample_rate}")

    lap = repo.get_lap(lap_id)
    if not lap:
        raise LapNotFoundError(lap_id)

    # Get telemetry points
    telemetry_points = lap.telemetry_points if lap.telemetry_points else []

    # Convert to response models
    points = []
    for i, point in enumerate(telemetry_points):
        # Apply downsampling if requested
        if sample_rate and i % (100 // sample_rate) != 0:
            continue

        points.append(
            TelemetryPoint(
                timestamp=point.timestamp,
                speed=point.speed,
                rpm=point.rpm,
                gear=point.gear,
                throttle=point.throttle,
                brake=point.brake,
                steering=point.steering,
                position_x=point.position_x,
                position_y=point.position_y,
                position_z=point.position_z,
            )
        )

    return TelemetryResponse(
        lap_id=lap_id, points=points, total_points=len(telemetry_points)
    )


@router.get("/compare", response_model=ComparisonResponse)
async def compare_laps(
    lap_ids: List[int] = Query(..., description="Lap IDs to compare"),
    repo: TelemetryRepository = Depends(get_repository),
):
    """
    Compare multiple laps.

    Analyzes and compares performance across multiple laps,
    providing time deltas and improvement suggestions.

    Args:
        lap_ids: List of lap IDs to compare (2-5 laps)
        repo: Database repository

    Returns:
        ComparisonResponse: Comparison results

    Raises:
        InvalidParameterError: If invalid number of laps
        LapNotFoundError: If any lap not found
    """
    if len(lap_ids) < 2 or len(lap_ids) > 5:
        raise InvalidParameterError("lap_ids", "Must compare between 2 and 5 laps")

    logger.info(f"Comparing laps: {lap_ids}")

    # Fetch all laps
    laps = []
    for lap_id in lap_ids:
        lap = repo.get_lap(lap_id)
        if not lap:
            raise LapNotFoundError(lap_id)
        laps.append(lap)

    # Convert to response models
    lap_responses = [
        LapResponse(
            id=lap.id,
            session_id=lap.session_id,
            lap_number=lap.lap_number,
            lap_time=lap.lap_time,
            sector1_time=lap.sector1_time,
            sector2_time=lap.sector2_time,
            sector3_time=lap.sector3_time,
            valid=True,
        )
        for lap in laps
    ]

    # Find fastest lap
    fastest_lap = min(laps, key=lambda l: l.lap_time)

    # Calculate deltas
    time_deltas = {}
    for lap in laps:
        time_deltas[lap.id] = {
            "total": lap.lap_time - fastest_lap.lap_time,
            "sector1": (lap.sector1_time or 0) - (fastest_lap.sector1_time or 0),
            "sector2": (lap.sector2_time or 0) - (fastest_lap.sector2_time or 0),
            "sector3": (lap.sector3_time or 0) - (fastest_lap.sector3_time or 0),
        }

    # Generate suggestions (simplified)
    suggestions = [
        "Analyze braking points in slower sectors",
        "Compare throttle application through corners",
        "Review racing line in sectors with largest delta",
    ]

    return ComparisonResponse(
        laps=lap_responses,
        fastest_lap_id=fastest_lap.id,
        time_deltas=time_deltas,
        suggestions=suggestions,
    )
