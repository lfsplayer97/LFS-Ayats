"""
Repository layer for database operations.

Provides a clean abstraction for database access with common queries
and operations on telemetry data.

Reference:
    https://docs.sqlalchemy.org/en/20/orm/session_basics.html
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import create_engine, select, func, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from src.database.models import Base, Session, Lap, TelemetryPoint, Vehicle, Circuit

logger = logging.getLogger(__name__)


def _mask_connection_string_password(connection_string: str) -> str:
    """
    Mask password in database connection string for safe logging.
    
    Args:
        connection_string: Original connection string
        
    Returns:
        Connection string with password masked as '***'
    """
    # Handle PostgreSQL/MySQL connection strings: protocol://user:pass@host:port/db
    if "://" in connection_string and "@" in connection_string:
        try:
            parts = connection_string.split("://", 1)
            if len(parts) == 2 and "@" in parts[1]:
                credentials, rest = parts[1].split("@", 1)
                if ":" in credentials:
                    user, _ = credentials.split(":", 1)
                    return f"{parts[0]}://{user}:***@{rest}"
        except (ValueError, IndexError):
            pass
    # For SQLite or if masking fails, return as-is (no password)
    return connection_string


class TelemetryRepository:
    """
    Repository for telemetry data access.

    Provides high-level operations for storing and querying telemetry data
    with proper connection management and error handling.

    Example:
        >>> repo = TelemetryRepository("sqlite:///telemetry.db")
        >>> session_id = repo.save_session(session_data)
        >>> session = repo.get_session(session_id)
    """

    def __init__(self, connection_string: str, echo: bool = False, pool_size: int = 5):
        """
        Initialize the repository.

        Args:
            connection_string: Database connection string (e.g., "sqlite:///data.db")
            echo: Enable SQL query logging
            pool_size: Connection pool size (for non-SQLite databases)
        """
        # SQLite needs special handling for connection pooling
        if connection_string.startswith("sqlite"):
            # Use StaticPool for in-memory databases
            if ":memory:" in connection_string:
                self.engine = create_engine(
                    connection_string,
                    echo=echo,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                )
            else:
                # Use NullPool for file-based SQLite to avoid locking issues
                self.engine = create_engine(
                    connection_string,
                    echo=echo,
                    connect_args={"check_same_thread": False},
                    poolclass=NullPool,
                )
        else:
            # PostgreSQL, MySQL, etc. use standard pooling
            self.engine = create_engine(
                connection_string,
                echo=echo,
                pool_size=pool_size,
                max_overflow=10,
            )

        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        logger.info(
            f"TelemetryRepository initialized with "
            f"{_mask_connection_string_password(connection_string)}"
        )

    def create_tables(self) -> None:
        """
        Create all database tables.

        Should be called once during initial setup.
        Use Alembic migrations for production environments.
        """
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")

    def drop_tables(self) -> None:
        """
        Drop all database tables.

        WARNING: This will delete all data. Use with caution.
        """
        Base.metadata.drop_all(self.engine)
        logger.warning("Database tables dropped")

    def save_session(
        self,
        datetime_start: datetime,
        circuit_name: Optional[str] = None,
        vehicle_name: Optional[str] = None,
        driver_name: Optional[str] = None,
        duration: Optional[int] = None,
    ) -> int:
        """
        Save a new session to the database.

        Args:
            datetime_start: Session start time
            circuit_name: Circuit short name (e.g., "BL1")
            vehicle_name: Vehicle short name (e.g., "XFG")
            driver_name: Driver name
            duration: Session duration in seconds

        Returns:
            int: Session ID

        Example:
            >>> session_id = repo.save_session(
            ...     datetime.now(),
            ...     circuit_name="BL1",
            ...     vehicle_name="XFG",
            ...     driver_name="Player1"
            ... )
        """
        with self.SessionLocal() as db:
            # Get or create circuit
            circuit_id = None
            if circuit_name:
                circuit = db.execute(
                    select(Circuit).where(Circuit.short_name == circuit_name)
                ).scalar_one_or_none()
                if circuit:
                    circuit_id = circuit.id

            # Get or create vehicle
            vehicle_id = None
            if vehicle_name:
                vehicle = db.execute(
                    select(Vehicle).where(Vehicle.short_name == vehicle_name)
                ).scalar_one_or_none()
                if vehicle:
                    vehicle_id = vehicle.id

            # Create session
            session = Session(
                datetime=datetime_start,
                circuit_id=circuit_id,
                vehicle_id=vehicle_id,
                driver_name=driver_name,
                duration=duration,
                total_laps=0,
            )
            db.add(session)
            db.commit()
            db.refresh(session)

            logger.info(f"Session {session.id} saved")
            return session.id

    def get_session(self, session_id: int) -> Optional[Session]:
        """
        Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session object or None if not found
        """
        with self.SessionLocal() as db:
            session = db.get(Session, session_id)
            if session:
                # Eagerly load relationships to avoid detached instance errors
                _ = session.laps  # Force load laps
                _ = session.circuit  # Force load circuit
                _ = session.vehicle  # Force load vehicle
                db.expunge(session)  # Detach from session
                return session
            return None

    def get_sessions_by_circuit(self, circuit_name: str) -> List[Session]:
        """
        Get all sessions for a specific circuit.

        Args:
            circuit_name: Circuit short name

        Returns:
            List of Session objects
        """
        with self.SessionLocal() as db:
            circuit = db.execute(
                select(Circuit).where(Circuit.short_name == circuit_name)
            ).scalar_one_or_none()

            if not circuit:
                return []

            sessions = (
                db.execute(
                    select(Session)
                    .where(Session.circuit_id == circuit.id)
                    .order_by(Session.datetime.desc())
                )
                .scalars()
                .all()
            )

            return list(sessions)

    def save_lap(
        self,
        session_id: int,
        lap_number: int,
        lap_time: Optional[int] = None,
        sector1_time: Optional[int] = None,
        sector2_time: Optional[int] = None,
        sector3_time: Optional[int] = None,
        valid: bool = True,
    ) -> int:
        """
        Save a lap to the database.

        Args:
            session_id: Session ID
            lap_number: Lap number (1-indexed)
            lap_time: Total lap time in milliseconds
            sector1_time: Sector 1 time in milliseconds
            sector2_time: Sector 2 time in milliseconds
            sector3_time: Sector 3 time in milliseconds
            valid: Whether lap is valid

        Returns:
            int: Lap ID
        """
        with self.SessionLocal() as db:
            lap = Lap(
                session_id=session_id,
                lap_number=lap_number,
                lap_time=lap_time,
                sector1_time=sector1_time,
                sector2_time=sector2_time,
                sector3_time=sector3_time,
                valid=valid,
            )
            db.add(lap)

            # Update session total laps
            session = db.get(Session, session_id)
            if session:
                session.total_laps = max(session.total_laps, lap_number)

            db.commit()
            db.refresh(lap)

            logger.debug(f"Lap {lap.id} saved for session {session_id}")
            return lap.id

    def get_best_lap(self, session_id: int) -> Optional[Lap]:
        """
        Get the best (fastest) valid lap in a session.

        Args:
            session_id: Session ID

        Returns:
            Lap object or None if no valid laps found
        """
        with self.SessionLocal() as db:
            lap = db.execute(
                select(Lap)
                .where(and_(Lap.session_id == session_id, Lap.valid.is_(True)))
                .where(Lap.lap_time.is_not(None))
                .order_by(Lap.lap_time)
                .limit(1)
            ).scalar_one_or_none()

            return lap

    def save_telemetry_points(
        self, lap_id: int, telemetry_points: List[Dict[str, Any]]
    ) -> int:
        """
        Save telemetry points in batch for a lap.

        Args:
            lap_id: Lap ID
            telemetry_points: List of telemetry point dictionaries

        Returns:
            int: Number of points saved

        Example:
            >>> points = [
            ...     {"timestamp": 0, "speed": 0.0, "rpm": 1000},
            ...     {"timestamp": 100, "speed": 10.5, "rpm": 2000},
            ... ]
            >>> count = repo.save_telemetry_points(lap_id, points)
        """
        if not telemetry_points:
            return 0

        with self.SessionLocal() as db:
            # Batch insert for performance
            objects = [
                TelemetryPoint(lap_id=lap_id, **point) for point in telemetry_points
            ]
            db.bulk_save_objects(objects)
            db.commit()

            count = len(objects)
            logger.debug(f"Saved {count} telemetry points for lap {lap_id}")
            return count

    def get_telemetry_points(self, lap_id: int) -> List[TelemetryPoint]:
        """
        Get all telemetry points for a lap.

        Args:
            lap_id: Lap ID

        Returns:
            List of TelemetryPoint objects ordered by timestamp
        """
        with self.SessionLocal() as db:
            points = (
                db.execute(
                    select(TelemetryPoint)
                    .where(TelemetryPoint.lap_id == lap_id)
                    .order_by(TelemetryPoint.timestamp)
                )
                .scalars()
                .all()
            )

            return list(points)

    def compare_laps(self, lap_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple laps.

        Args:
            lap_ids: List of lap IDs to compare

        Returns:
            Dictionary with comparison data
        """
        with self.SessionLocal() as db:
            laps = db.execute(select(Lap).where(Lap.id.in_(lap_ids))).scalars().all()

            comparison = {
                "laps": [],
                "fastest_lap_id": None,
                "average_time": None,
            }

            if not laps:
                return comparison

            valid_times = []
            for lap in laps:
                lap_data = {
                    "id": lap.id,
                    "lap_number": lap.lap_number,
                    "lap_time": lap.lap_time,
                    "sector1_time": lap.sector1_time,
                    "sector2_time": lap.sector2_time,
                    "sector3_time": lap.sector3_time,
                    "valid": lap.valid,
                }
                comparison["laps"].append(lap_data)

                if lap.lap_time and lap.valid:
                    valid_times.append((lap.id, lap.lap_time))

            # Find fastest lap
            if valid_times:
                fastest = min(valid_times, key=lambda x: x[1])
                comparison["fastest_lap_id"] = fastest[0]
                comparison["average_time"] = sum(t for _, t in valid_times) / len(
                    valid_times
                )

            return comparison

    def get_statistics(self, session_id: int) -> Dict[str, Any]:
        """
        Get statistical summary for a session.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with session statistics
        """
        with self.SessionLocal() as db:
            session = db.get(Session, session_id)
            if not session:
                return {}

            # Lap statistics
            lap_stats = db.execute(
                select(
                    func.count(Lap.id).label("total_laps"),
                    func.count(Lap.id).filter(Lap.valid.is_(True)).label("valid_laps"),
                    func.min(Lap.lap_time)
                    .filter(Lap.valid.is_(True))
                    .label("best_time"),
                    func.avg(Lap.lap_time)
                    .filter(Lap.valid.is_(True))
                    .label("avg_time"),
                ).where(Lap.session_id == session_id)
            ).one()

            # Telemetry statistics
            telemetry_count = db.execute(
                select(func.count(TelemetryPoint.id))
                .join(Lap)
                .where(Lap.session_id == session_id)
            ).scalar()

            return {
                "session_id": session_id,
                "datetime": session.datetime.isoformat() if session.datetime else None,
                "driver_name": session.driver_name,
                "duration": session.duration,
                "total_laps": lap_stats.total_laps or 0,
                "valid_laps": lap_stats.valid_laps or 0,
                "best_lap_time": lap_stats.best_time,
                "average_lap_time": lap_stats.avg_time,
                "telemetry_points": telemetry_count or 0,
            }

    def create_circuit(
        self, name: str, short_name: str, length: Optional[float] = None
    ) -> int:
        """
        Create a new circuit.

        Args:
            name: Full circuit name
            short_name: Short code (e.g., "BL1")
            length: Circuit length in meters

        Returns:
            int: Circuit ID
        """
        with self.SessionLocal() as db:
            circuit = Circuit(name=name, short_name=short_name, length=length)
            db.add(circuit)
            db.commit()
            db.refresh(circuit)
            logger.info(f"Circuit {circuit.id} created: {name}")
            return circuit.id

    def create_vehicle(
        self, name: str, short_name: str, class_type: Optional[str] = None
    ) -> int:
        """
        Create a new vehicle.

        Args:
            name: Full vehicle name
            short_name: Short code (e.g., "XFG")
            class_type: Vehicle class (e.g., "TBO")

        Returns:
            int: Vehicle ID
        """
        with self.SessionLocal() as db:
            vehicle = Vehicle(name=name, short_name=short_name, class_type=class_type)
            db.add(vehicle)
            db.commit()
            db.refresh(vehicle)
            logger.info(f"Vehicle {vehicle.id} created: {name}")
            return vehicle.id

    def close(self) -> None:
        """Close the database connection pool."""
        self.engine.dispose()
        logger.info("Database connection pool closed")
