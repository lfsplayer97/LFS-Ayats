"""
Database Exporter
Exportació de dades telemètriques a base de dades.

Provides efficient database export functionality with support for
SQLite and PostgreSQL databases.

Reference:
    https://docs.sqlalchemy.org/en/20/
"""

import logging
from typing import List, Any, Dict, Optional
from datetime import datetime
from pathlib import Path

from src.database.repository import TelemetryRepository, _mask_connection_string_password

logger = logging.getLogger(__name__)


class DatabaseExporter:
    """
    Exporta dades telemètriques a base de dades.

    Supports SQLite (development) and PostgreSQL (production) with
    connection pooling and batch inserts for optimal performance.

    Example:
        >>> exporter = DatabaseExporter("sqlite:///data/telemetry.db")
        >>> exporter.export_session(session_data, telemetry_data)
    """

    def __init__(
        self,
        connection_string: str,
        echo: bool = False,
        pool_size: int = 5,
        create_tables: bool = True,
    ):
        """
        Inicialitza l'exportador de base de dades.

        Args:
            connection_string: Database connection string
                Examples:
                    - SQLite: "sqlite:///data/telemetry.db"
                    - PostgreSQL: "postgresql://user:pass@localhost/dbname"
            echo: Enable SQL query logging (for debugging)
            pool_size: Connection pool size (ignored for SQLite)
            create_tables: Automatically create tables if they don't exist
        """
        self.repository = TelemetryRepository(
            connection_string=connection_string, echo=echo, pool_size=pool_size
        )

        if create_tables:
            self.repository.create_tables()

        logger.info(
            f"DatabaseExporter inicialitzat: "
            f"{_mask_connection_string_password(connection_string)}"
        )

    @staticmethod
    def from_config(config: Dict[str, Any]) -> "DatabaseExporter":
        """
        Create exporter from configuration dictionary.

        Args:
            config: Configuration dictionary with database settings

        Returns:
            DatabaseExporter instance

        Example:
            >>> config = {
            ...     "type": "sqlite",
            ...     "sqlite": {"path": "./data/telemetry.db"},
            ...     "echo": False
            ... }
            >>> exporter = DatabaseExporter.from_config(config)
        """
        db_type = config.get("type", "sqlite")
        echo = config.get("echo", False)
        pool_size = config.get("pool_size", 5)

        if db_type == "sqlite":
            db_path = config.get("sqlite", {}).get("path", "./data/telemetry.db")
            # Ensure directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            connection_string = f"sqlite:///{db_path}"
        elif db_type == "postgresql":
            pg_config = config.get("postgresql", {})
            host = pg_config.get("host", "localhost")
            port = pg_config.get("port", 5432)
            database = pg_config.get("database", "lfs_telemetry")
            user = pg_config.get("user", "lfs_user")
            password = pg_config.get("password", "")
            connection_string = (
                f"postgresql://{user}:{password}@{host}:{port}/{database}"
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        return DatabaseExporter(
            connection_string=connection_string, echo=echo, pool_size=pool_size
        )

    def export_session(
        self,
        session_data: Dict[str, Any],
        laps_data: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """
        Export a complete session to database.

        Args:
            session_data: Session metadata dictionary
                Required keys: datetime
                Optional keys: circuit_name, vehicle_name, driver_name, duration
            laps_data: Optional list of lap dictionaries
                Each lap dict should contain: lap_number, lap_time, etc.

        Returns:
            int: Session ID

        Example:
            >>> session_data = {
            ...     "datetime": datetime.now(),
            ...     "circuit_name": "BL1",
            ...     "vehicle_name": "XFG",
            ...     "driver_name": "Player1",
            ...     "duration": 600
            ... }
            >>> laps_data = [
            ...     {"lap_number": 1, "lap_time": 95000, "valid": True},
            ...     {"lap_number": 2, "lap_time": 93000, "valid": True},
            ... ]
            >>> session_id = exporter.export_session(session_data, laps_data)
        """
        try:
            # Save session
            session_id = self.repository.save_session(
                datetime_start=session_data.get("datetime", datetime.now()),
                circuit_name=session_data.get("circuit_name"),
                vehicle_name=session_data.get("vehicle_name"),
                driver_name=session_data.get("driver_name"),
                duration=session_data.get("duration"),
            )

            # Save laps if provided
            if laps_data:
                for lap_data in laps_data:
                    self.repository.save_lap(
                        session_id=session_id,
                        lap_number=lap_data.get("lap_number", 1),
                        lap_time=lap_data.get("lap_time"),
                        sector1_time=lap_data.get("sector1_time"),
                        sector2_time=lap_data.get("sector2_time"),
                        sector3_time=lap_data.get("sector3_time"),
                        valid=lap_data.get("valid", True),
                    )

            logger.info(
                f"Session exportada amb ID {session_id} "
                f"({len(laps_data) if laps_data else 0} voltes)"
            )
            return session_id

        except Exception as e:
            logger.error(f"Error exportant sessió: {e}")
            raise

    def export_telemetry(
        self, telemetry_data: List[Any], lap_id: Optional[int] = None
    ) -> int:
        """
        Export telemetry data points to database.

        Args:
            telemetry_data: List of telemetry objects or dictionaries
            lap_id: Optional lap ID (if None, creates a new session and lap)

        Returns:
            int: Number of telemetry points saved

        Example:
            >>> telemetry = [
            ...     MockCarTelemetry(timestamp=0.0, speed=0.0, rpm=1000),
            ...     MockCarTelemetry(timestamp=0.1, speed=10.0, rpm=2000),
            ... ]
            >>> count = exporter.export_telemetry(telemetry, lap_id=1)
        """
        if not telemetry_data:
            logger.warning("No hi ha dades per exportar")
            return 0

        try:
            # Create default session/lap if not provided
            if lap_id is None:
                session_id = self.repository.save_session(datetime.now())
                lap_id = self.repository.save_lap(session_id, lap_number=1)
                logger.info(
                    f"Created default session {session_id} and lap {lap_id} for telemetry"
                )

            # Convert telemetry objects to dictionaries
            telemetry_points = []
            for i, item in enumerate(telemetry_data):
                # Handle both object and dict formats
                if isinstance(item, dict):
                    point = item
                else:
                    # Convert object to dict
                    point = {
                        "timestamp": int(getattr(item, "timestamp", i * 100)),
                        "speed": float(getattr(item, "speed", 0.0)),
                        "rpm": getattr(item, "rpm", None),
                        "gear": getattr(item, "gear", None),
                        "throttle": getattr(item, "throttle", None),
                        "brake": getattr(item, "brake", None),
                        "clutch": getattr(item, "clutch", None),
                        "steering_angle": getattr(item, "steering_angle", None),
                        "position_x": (
                            item.position.get("x")
                            if hasattr(item, "position")
                            else None
                        ),
                        "position_y": (
                            item.position.get("y")
                            if hasattr(item, "position")
                            else None
                        ),
                        "position_z": (
                            item.position.get("z")
                            if hasattr(item, "position")
                            else None
                        ),
                        "engine_temp": getattr(item, "engine_temp", None),
                    }

                # Remove None values for efficiency
                point = {k: v for k, v in point.items() if v is not None}
                telemetry_points.append(point)

            # Batch save
            count = self.repository.save_telemetry_points(lap_id, telemetry_points)

            logger.info(f"Exportades {count} mostres telemètriques a lap {lap_id}")
            return count

        except Exception as e:
            logger.error(f"Error exportant telemetria: {e}")
            raise

    def export_complete_session(
        self,
        session_data: Dict[str, Any],
        laps_with_telemetry: List[Dict[str, Any]],
    ) -> int:
        """
        Export a complete session with laps and telemetry data.

        Args:
            session_data: Session metadata
            laps_with_telemetry: List of dictionaries containing:
                - lap_metadata: Lap timing information
                - telemetry_points: List of telemetry data points

        Returns:
            int: Session ID

        Example:
            >>> laps = [
            ...     {
            ...         "lap_metadata": {"lap_number": 1, "lap_time": 95000},
            ...         "telemetry_points": [{"timestamp": 0, "speed": 0.0}, ...]
            ...     }
            ... ]
            >>> session_id = exporter.export_complete_session(session_data, laps)
        """
        try:
            # Save session
            session_id = self.repository.save_session(
                datetime_start=session_data.get("datetime", datetime.now()),
                circuit_name=session_data.get("circuit_name"),
                vehicle_name=session_data.get("vehicle_name"),
                driver_name=session_data.get("driver_name"),
                duration=session_data.get("duration"),
            )

            total_telemetry = 0

            # Save each lap with its telemetry
            for lap_data in laps_with_telemetry:
                lap_metadata = lap_data.get("lap_metadata", {})
                telemetry_points = lap_data.get("telemetry_points", [])

                # Save lap
                lap_id = self.repository.save_lap(
                    session_id=session_id,
                    lap_number=lap_metadata.get("lap_number", 1),
                    lap_time=lap_metadata.get("lap_time"),
                    sector1_time=lap_metadata.get("sector1_time"),
                    sector2_time=lap_metadata.get("sector2_time"),
                    sector3_time=lap_metadata.get("sector3_time"),
                    valid=lap_metadata.get("valid", True),
                )

                # Save telemetry for this lap
                if telemetry_points:
                    count = self.repository.save_telemetry_points(
                        lap_id, telemetry_points
                    )
                    total_telemetry += count

            logger.info(
                f"Session completa exportada: ID {session_id}, "
                f"{len(laps_with_telemetry)} voltes, "
                f"{total_telemetry} punts de telemetria"
            )
            return session_id

        except Exception as e:
            logger.error(f"Error exportant sessió completa: {e}")
            raise

    def setup_circuits_and_vehicles(
        self,
        circuits: Optional[List[Dict[str, Any]]] = None,
        vehicles: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Setup initial circuits and vehicles in database.

        Args:
            circuits: List of circuit dictionaries
            vehicles: List of vehicle dictionaries

        Example:
            >>> circuits = [
            ...     {"name": "Blackwood GP", "short_name": "BL1", "length": 3290.0}
            ... ]
            >>> vehicles = [
            ...     {"name": "XF GTI", "short_name": "XFG", "class_type": "TBO"}
            ... ]
            >>> exporter.setup_circuits_and_vehicles(circuits, vehicles)
        """
        try:
            if circuits:
                for circuit in circuits:
                    self.repository.create_circuit(
                        name=circuit.get("name"),
                        short_name=circuit.get("short_name"),
                        length=circuit.get("length"),
                    )

            if vehicles:
                for vehicle in vehicles:
                    self.repository.create_vehicle(
                        name=vehicle.get("name"),
                        short_name=vehicle.get("short_name"),
                        class_type=vehicle.get("class_type"),
                    )

            logger.info(
                f"Setup completat: {len(circuits or [])} circuits, "
                f"{len(vehicles or [])} vehicles"
            )

        except Exception as e:
            logger.error(f"Error en setup inicial: {e}")
            raise

    def get_session_statistics(self, session_id: int) -> Dict[str, Any]:
        """
        Get statistics for a session.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with session statistics
        """
        return self.repository.get_statistics(session_id)

    def close(self) -> None:
        """Close database connections."""
        self.repository.close()
        logger.info("DatabaseExporter tancat")
