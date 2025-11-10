"""
Statistics endpoints for performance metrics.

Provides endpoints for best laps, driver stats, and circuit stats.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from src.api.models import (
    BestLapStats,
    DriverStats,
    CircuitStats,
    LapResponse,
)
from src.api.dependencies import get_repository
from src.database.repository import TelemetryRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/best-laps", response_model=List[BestLapStats])
async def get_best_laps(
    circuit: Optional[str] = Query(None, description="Filter by circuit"),
    vehicle: Optional[str] = Query(None, description="Filter by vehicle"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    repo: TelemetryRepository = Depends(get_repository),
):
    """
    Get best laps by circuit/vehicle.

    Returns the fastest laps, optionally filtered by circuit and vehicle.

    Args:
        circuit: Optional circuit name filter
        vehicle: Optional vehicle name filter
        limit: Maximum number of results
        repo: Database repository

    Returns:
        List[BestLapStats]: Best lap statistics
    """
    logger.info(f"Getting best laps: circuit={circuit}, vehicle={vehicle}, limit={limit}")

    # Get sessions with filters
    sessions = repo.get_sessions(circuit=circuit, vehicle=vehicle, limit=100)

    # Extract and sort laps
    all_laps = []
    for session in sessions:
        if session.laps:
            for lap in session.laps:
                all_laps.append((lap, session))

    # Sort by lap time
    all_laps.sort(key=lambda x: x[0].lap_time)

    # Take top N
    best_laps = []
    for lap, session in all_laps[:limit]:
        best_laps.append(
            BestLapStats(
                lap=LapResponse(
                    id=lap.id,
                    session_id=lap.session_id,
                    lap_number=lap.lap_number,
                    lap_time=lap.lap_time,
                    sector1_time=lap.sector1_time,
                    sector2_time=lap.sector2_time,
                    sector3_time=lap.sector3_time,
                    valid=True,
                ),
                driver=session.driver_name,
                circuit=session.circuit.name if session.circuit else "Unknown",
                vehicle=session.vehicle.name if session.vehicle else "Unknown",
                session_date=session.datetime,
            )
        )

    return best_laps


@router.get("/driver/{driver_name}", response_model=DriverStats)
async def get_driver_stats(
    driver_name: str, repo: TelemetryRepository = Depends(get_repository)
):
    """
    Get driver statistics.

    Provides comprehensive statistics for a specific driver.

    Args:
        driver_name: Driver name
        repo: Database repository

    Returns:
        DriverStats: Driver statistics
    """
    logger.info(f"Getting stats for driver {driver_name}")

    # Get all sessions for driver
    sessions = repo.get_sessions(driver=driver_name, limit=1000)

    total_sessions = len(sessions)
    total_laps = 0
    lap_times = []

    for session in sessions:
        if session.laps:
            total_laps += len(session.laps)
            lap_times.extend([lap.lap_time for lap in session.laps])

    best_lap_time = min(lap_times) if lap_times else None
    avg_lap_time = sum(lap_times) / len(lap_times) if lap_times else None

    return DriverStats(
        driver_name=driver_name,
        total_sessions=total_sessions,
        total_laps=total_laps,
        best_lap_time=best_lap_time,
        avg_lap_time=avg_lap_time,
        total_distance=None,  # Would calculate from telemetry
    )


@router.get("/circuit/{circuit_name}", response_model=CircuitStats)
async def get_circuit_stats(
    circuit_name: str, repo: TelemetryRepository = Depends(get_repository)
):
    """
    Get circuit statistics.

    Provides comprehensive statistics for a specific circuit.

    Args:
        circuit_name: Circuit name
        repo: Database repository

    Returns:
        CircuitStats: Circuit statistics
    """
    logger.info(f"Getting stats for circuit {circuit_name}")

    # Get all sessions for circuit
    sessions = repo.get_sessions(circuit=circuit_name, limit=1000)

    total_sessions = len(sessions)
    total_laps = 0
    best_lap = None
    best_driver = None

    for session in sessions:
        if session.laps:
            total_laps += len(session.laps)
            session_best = min(session.laps, key=lambda l: l.lap_time, default=None)
            if session_best and (best_lap is None or session_best.lap_time < best_lap):
                best_lap = session_best.lap_time
                best_driver = session.driver_name

    return CircuitStats(
        circuit_name=circuit_name,
        total_sessions=total_sessions,
        total_laps=total_laps,
        best_lap_time=best_lap,
        best_lap_driver=best_driver,
    )
