"""
Export endpoints for data export operations.

Provides endpoints for exporting lap and session data in various formats.
"""

import tempfile
import os
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse

from src.utils import get_logger
from src.api.models import ExportResponse
from src.api.dependencies import get_repository
from src.api.exceptions import LapNotFoundError, SessionNotFoundError, ExportError
from src.database.repository import TelemetryRepository
from src.export.csv_exporter import CSVExporter
from src.export.json_exporter import JSONExporter

logger = get_logger(__name__)

router = APIRouter()


@router.get("/csv/{lap_id}", response_class=FileResponse)
async def export_lap_csv(
    lap_id: int, repo: TelemetryRepository = Depends(get_repository)
):
    """
    Export lap data as CSV.

    Exports telemetry data for a lap to CSV format.

    Args:
        lap_id: Lap ID
        repo: Database repository

    Returns:
        FileResponse: CSV file download

    Raises:
        LapNotFoundError: If lap not found
        ExportError: If export fails
    """
    logger.info(f"Exporting lap {lap_id} to CSV")

    lap = repo.get_lap(lap_id)
    if not lap:
        raise LapNotFoundError(lap_id)

    try:
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        filename = f"lap_{lap_id}.csv"
        filepath = os.path.join(temp_dir, filename)

        # Export using CSVExporter
        exporter = CSVExporter(filepath)
        telemetry_data = lap.telemetry_points if lap.telemetry_points else []

        # Convert to dict format expected by exporter
        data_dicts = []
        for point in telemetry_data:
            data_dicts.append(
                {
                    "timestamp": point.timestamp,
                    "speed": point.speed,
                    "rpm": point.rpm,
                    "gear": point.gear,
                    "throttle": point.throttle,
                    "brake": point.brake,
                    "position_x": point.position_x,
                    "position_y": point.position_y,
                    "position_z": point.position_z,
                }
            )

        exporter.export(data_dicts)

        return FileResponse(
            path=filepath,
            media_type="text/csv",
            filename=filename,
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise ExportError(str(e))


@router.get("/json/{lap_id}", response_class=FileResponse)
async def export_lap_json(
    lap_id: int, repo: TelemetryRepository = Depends(get_repository)
):
    """
    Export lap data as JSON.

    Exports telemetry data for a lap to JSON format.

    Args:
        lap_id: Lap ID
        repo: Database repository

    Returns:
        FileResponse: JSON file download

    Raises:
        LapNotFoundError: If lap not found
        ExportError: If export fails
    """
    logger.info(f"Exporting lap {lap_id} to JSON")

    lap = repo.get_lap(lap_id)
    if not lap:
        raise LapNotFoundError(lap_id)

    try:
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        filename = f"lap_{lap_id}.json"
        filepath = os.path.join(temp_dir, filename)

        # Export using JSONExporter
        exporter = JSONExporter(filepath)
        telemetry_data = lap.telemetry_points if lap.telemetry_points else []

        # Convert to dict format expected by exporter
        data_dicts = []
        for point in telemetry_data:
            data_dicts.append(
                {
                    "timestamp": point.timestamp,
                    "speed": point.speed,
                    "rpm": point.rpm,
                    "gear": point.gear,
                    "throttle": point.throttle,
                    "brake": point.brake,
                    "position_x": point.position_x,
                    "position_y": point.position_y,
                    "position_z": point.position_z,
                }
            )

        exporter.export(data_dicts)

        return FileResponse(
            path=filepath,
            media_type="application/json",
            filename=filename,
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise ExportError(str(e))


@router.get("/session/{session_id}")
async def export_session(
    session_id: int,
    format: str = Query("csv", description="Export format (csv, json)"),
    repo: TelemetryRepository = Depends(get_repository),
):
    """
    Export complete session.

    Exports all data from a session including laps and telemetry.

    Args:
        session_id: Session ID
        format: Export format (csv, json)
        repo: Database repository

    Returns:
        dict: Export information with download details

    Raises:
        SessionNotFoundError: If session not found
        ExportError: If export fails
    """
    logger.info(f"Exporting session {session_id} as {format}")

    session = repo.get_session(session_id)
    if not session:
        raise SessionNotFoundError(session_id)

    # In a real implementation, this would export the entire session
    # For now, return metadata
    return {
        "session_id": session_id,
        "format": format,
        "laps_count": len(session.laps) if session.laps else 0,
        "message": "Session export would be generated here",
    }
