"""
Dependency injection for FastAPI endpoints.

Provides reusable dependencies for database access, configuration,
and other shared resources.
"""

import logging
from typing import Optional

from src.database.repository import TelemetryRepository
from src.config.settings import Settings

logger = logging.getLogger(__name__)

# Global repository instance
_repository: Optional[TelemetryRepository] = None
_settings: Optional[Settings] = None


def init_dependencies(
    db_connection_string: str = "sqlite:///telemetry.db",
    config_path: Optional[str] = None,
):
    """
    Initialize global dependencies.

    Should be called once during application startup.

    Args:
        db_connection_string: Database connection string
        config_path: Path to configuration file
    """
    global _repository, _settings

    _repository = TelemetryRepository(db_connection_string)
    _repository.create_tables()

    if config_path:
        _settings = Settings.from_yaml(config_path)
    else:
        _settings = Settings()

    logger.info("Dependencies initialized")


def get_repository() -> TelemetryRepository:
    """
    Get telemetry repository instance.

    Returns:
        TelemetryRepository instance

    Raises:
        RuntimeError: If repository not initialized
    """
    if _repository is None:
        raise RuntimeError(
            "Repository not initialized. Call init_dependencies() first."
        )
    return _repository


def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Settings instance

    Raises:
        RuntimeError: If settings not initialized
    """
    if _settings is None:
        raise RuntimeError("Settings not initialized. Call init_dependencies() first.")
    return _settings


# Dependency for connection status
_connection_active: bool = False


def set_connection_status(active: bool):
    """Set the connection status."""
    global _connection_active
    _connection_active = active


def get_connection_status() -> bool:
    """Get current connection status."""
    return _connection_active
