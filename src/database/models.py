"""
SQLAlchemy models for LFS telemetry data.

This module defines the database schema for storing Live for Speed
telemetry sessions, laps, and telemetry points.

Reference:
    https://docs.sqlalchemy.org/en/20/
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""


class Circuit(Base):
    """
    Circuit information.

    Stores track configuration details for racing circuits.

    Attributes:
        id: Primary key
        name: Circuit name (e.g., "Blackwood GP")
        short_name: Short code (e.g., "BL1")
        length: Circuit length in meters
        sector_count: Number of sectors (typically 3)
        sessions: Related sessions on this circuit
    """

    __tablename__ = "circuits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    length: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sector_count: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Relationships
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="circuit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Circuit(id={self.id}, name='{self.name}', short_name='{self.short_name}')>"


class Vehicle(Base):
    """
    Vehicle configuration information.

    Stores car setup and configuration details.

    Attributes:
        id: Primary key
        name: Vehicle name (e.g., "XF GTI")
        short_name: Short code (e.g., "XFG")
        class_type: Vehicle class (e.g., "TBO", "GTR")
        sessions: Related sessions using this vehicle
    """

    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    class_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationships
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="vehicle", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, name='{self.name}', short_name='{self.short_name}')>"


class Session(Base):
    """
    Driving session information.

    Stores metadata about a complete telemetry recording session.

    Attributes:
        id: Primary key
        datetime: Session start time
        circuit_id: Foreign key to circuit
        vehicle_id: Foreign key to vehicle
        driver_name: Name of the driver
        duration: Session duration in seconds
        total_laps: Total number of laps completed
        circuit: Related circuit
        vehicle: Related vehicle
        laps: Related laps in this session
    """

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    datetime: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    circuit_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("circuits.id"), nullable=True
    )
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("vehicles.id"), nullable=True
    )
    driver_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_laps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    circuit: Mapped[Optional["Circuit"]] = relationship(
        "Circuit", back_populates="sessions"
    )
    vehicle: Mapped[Optional["Vehicle"]] = relationship(
        "Vehicle", back_populates="sessions"
    )
    laps: Mapped[List["Lap"]] = relationship(
        "Lap", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, datetime={self.datetime}, driver='{self.driver_name}')>"


# Create index for common queries
Index("idx_sessions_circuit", Session.circuit_id)
Index("idx_sessions_datetime", Session.datetime)


class Lap(Base):
    """
    Individual lap data.

    Stores timing information for each lap in a session.

    Attributes:
        id: Primary key
        session_id: Foreign key to session
        lap_number: Lap number in session (1-indexed)
        lap_time: Total lap time in milliseconds
        sector1_time: Sector 1 time in milliseconds
        sector2_time: Sector 2 time in milliseconds
        sector3_time: Sector 3 time in milliseconds
        valid: Whether the lap is valid (no cuts/collisions)
        session: Related session
        telemetry_points: Related telemetry data points
    """

    __tablename__ = "laps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id"), nullable=False
    )
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sector1_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sector2_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sector3_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="laps")
    telemetry_points: Mapped[List["TelemetryPoint"]] = relationship(
        "TelemetryPoint", back_populates="lap", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Lap(id={self.id}, session_id={self.session_id}, "
            f"lap_number={self.lap_number}, lap_time={self.lap_time})>"
        )


# Create index for lap queries
Index("idx_laps_session", Lap.session_id)


class TelemetryPoint(Base):
    """
    Individual telemetry data point.

    Stores high-frequency telemetry data captured during a lap.
    Data points are typically captured at 10-100Hz frequency.

    Attributes:
        id: Primary key
        lap_id: Foreign key to lap
        timestamp: Milliseconds from lap start
        speed: Speed in m/s
        rpm: Engine RPM
        gear: Current gear (-1=reverse, 0=neutral, 1+=forward)
        throttle: Throttle position (0.0-1.0)
        brake: Brake pressure (0.0-1.0)
        clutch: Clutch position (0.0-1.0)
        steering_angle: Steering angle in degrees (-90 to +90)
        position_x: X coordinate in game units
        position_y: Y coordinate in game units
        position_z: Z coordinate in game units
        engine_temp: Engine temperature in Celsius
        lap: Related lap
    """

    __tablename__ = "telemetry_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lap_id: Mapped[int] = mapped_column(Integer, ForeignKey("laps.id"), nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    speed: Mapped[float] = mapped_column(Float, nullable=False)
    rpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gear: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    throttle: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    brake: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    clutch: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    steering_angle: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position_z: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    engine_temp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    lap: Mapped["Lap"] = relationship("Lap", back_populates="telemetry_points")

    def __repr__(self) -> str:
        return (
            f"<TelemetryPoint(id={self.id}, lap_id={self.lap_id}, "
            f"timestamp={self.timestamp}, speed={self.speed})>"
        )


# Create index for telemetry queries
Index("idx_telemetry_lap", TelemetryPoint.lap_id)
