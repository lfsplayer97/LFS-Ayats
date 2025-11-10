"""
Configuration endpoints for system settings.

Provides endpoints for reading and updating system configuration.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, Body

from src.api.models import ConfigResponse, ConnectionConfig, CircuitInfo, VehicleInfo
from src.api.dependencies import get_repository, get_settings
from src.config.settings import Settings
from src.database.repository import TelemetryRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=ConfigResponse)
async def get_config(settings: Settings = Depends(get_settings)):
    """
    Get current configuration.

    Returns the current system configuration.

    Args:
        settings: Application settings

    Returns:
        ConfigResponse: Current configuration
    """
    logger.info("Getting current configuration")

    return ConfigResponse(
        connection=ConnectionConfig(
            host=getattr(settings, "host", "127.0.0.1"),
            port=getattr(settings, "port", 29999),
            app_name=getattr(settings, "app_name", "LFS-Ayats"),
        ),
        telemetry_rate=10,
        auto_export=False,
        export_format="csv",
    )


@router.put("/")
async def update_config(
    config: ConfigResponse = Body(...), settings: Settings = Depends(get_settings)
):
    """
    Update configuration.

    Updates the system configuration.

    Args:
        config: New configuration
        settings: Application settings

    Returns:
        dict: Update confirmation
    """
    logger.info("Updating configuration")

    # In a real implementation, this would persist the configuration
    return {
        "status": "updated",
        "message": "Configuration updated successfully",
        "config": config,
    }


@router.get("/circuits", response_model=List[CircuitInfo])
async def list_circuits(repo: TelemetryRepository = Depends(get_repository)):
    """
    List available circuits.

    Returns all circuits present in the database.

    Args:
        repo: Database repository

    Returns:
        List[CircuitInfo]: Available circuits
    """
    logger.info("Listing available circuits")

    # Get unique circuits from sessions
    sessions = repo.get_sessions(limit=1000)
    circuits_dict = {}

    for session in sessions:
        if session.circuit:
            circuits_dict[session.circuit.id] = CircuitInfo(
                name=session.circuit.name,
                short_name=session.circuit.short_name,
                length=session.circuit.length,
            )

    return list(circuits_dict.values())


@router.get("/vehicles", response_model=List[VehicleInfo])
async def list_vehicles(repo: TelemetryRepository = Depends(get_repository)):
    """
    List available vehicles.

    Returns all vehicles present in the database.

    Args:
        repo: Database repository

    Returns:
        List[VehicleInfo]: Available vehicles
    """
    logger.info("Listing available vehicles")

    # Get unique vehicles from sessions
    sessions = repo.get_sessions(limit=1000)
    vehicles_dict = {}

    for session in sessions:
        if session.vehicle:
            vehicles_dict[session.vehicle.id] = VehicleInfo(
                name=session.vehicle.name,
                short_name=session.vehicle.short_name,
                class_type=session.vehicle.class_type,
            )

    return list(vehicles_dict.values())
