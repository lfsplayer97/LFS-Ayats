"""
Pydantic models for API request and response validation.

Defines data models for all API endpoints with automatic validation
and serialization.

Reference:
    https://docs.pydantic.dev/
"""

from datetime import datetime as DateTime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


# Session models
class SessionBase(BaseModel):
    """Base session data."""

    circuit: str = Field(..., description="Circuit name or short name")
    vehicle: str = Field(..., description="Vehicle name or short name")
    driver: str = Field(..., description="Driver name")


class SessionCreate(SessionBase):
    """Data for creating a new session."""

    datetime: Optional[DateTime] = Field(
        default=None, description="Session datetime (defaults to now)"
    )


class SessionResponse(SessionBase):
    """Session response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Session ID")
    datetime: DateTime = Field(..., description="Session datetime")
    duration: int = Field(..., description="Session duration in seconds")
    total_laps: int = Field(0, description="Total number of laps")
    best_lap_time: Optional[float] = Field(default=None, description="Best lap time in seconds")


class SessionListResponse(BaseModel):
    """Paginated session list response."""

    total: int = Field(..., description="Total number of sessions")
    items: List[SessionResponse] = Field(..., description="Session items")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")


# Lap models
class LapBase(BaseModel):
    """Base lap data."""

    lap_number: int = Field(..., ge=1, description="Lap number")
    lap_time: float = Field(..., gt=0, description="Lap time in seconds")


class LapResponse(LapBase):
    """Lap response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Lap ID")
    session_id: int = Field(..., description="Parent session ID")
    sector1_time: Optional[float] = Field(default=None, description="Sector 1 time in seconds")
    sector2_time: Optional[float] = Field(default=None, description="Sector 2 time in seconds")
    sector3_time: Optional[float] = Field(default=None, description="Sector 3 time in seconds")
    valid: bool = Field(True, description="Whether lap is valid")


class LapListResponse(BaseModel):
    """Paginated lap list response."""

    total: int = Field(..., description="Total number of laps")
    items: List[LapResponse] = Field(..., description="Lap items")


# Telemetry models
class TelemetryPoint(BaseModel):
    """Single telemetry data point."""

    timestamp: float = Field(..., description="Timestamp in seconds")
    speed: float = Field(..., ge=0, description="Speed in km/h")
    rpm: int = Field(..., ge=0, description="Engine RPM")
    gear: int = Field(..., ge=-1, le=7, description="Current gear (-1=R, 0=N)")
    throttle: float = Field(..., ge=0, le=1, description="Throttle position (0-1)")
    brake: float = Field(..., ge=0, le=1, description="Brake position (0-1)")
    steering: Optional[float] = Field(
        None, ge=-1, le=1, description="Steering input (-1 to 1)"
    )
    position_x: float = Field(..., description="X position")
    position_y: float = Field(..., description="Y position")
    position_z: float = Field(..., description="Z position")


class TelemetryResponse(BaseModel):
    """Telemetry data response."""

    lap_id: int = Field(..., description="Lap ID")
    points: List[TelemetryPoint] = Field(..., description="Telemetry data points")
    total_points: int = Field(..., description="Total number of points")


# Analysis models
class SectorAnalysis(BaseModel):
    """Sector performance analysis."""

    sector_number: int = Field(..., ge=1, le=3, description="Sector number")
    time: float = Field(..., description="Sector time in seconds")
    delta: Optional[float] = Field(default=None, description="Delta to best sector time")
    speed_avg: float = Field(..., description="Average speed in sector")
    speed_max: float = Field(..., description="Maximum speed in sector")


class LapAnalysisResponse(BaseModel):
    """Complete lap analysis."""

    lap_id: int = Field(..., description="Lap ID")
    sectors: List[SectorAnalysis] = Field(..., description="Sector analysis")
    total_time: float = Field(..., description="Total lap time")
    theoretical_best: Optional[float] = Field(
        None, description="Theoretical best lap time"
    )


class AnomalyDetection(BaseModel):
    """Detected anomaly in telemetry data."""

    timestamp: float = Field(..., description="Anomaly timestamp")
    type: str = Field(..., description="Anomaly type (temperature, rpm, etc)")
    severity: str = Field(..., description="Severity level (low, medium, high)")
    message: str = Field(..., description="Anomaly description")
    value: float = Field(..., description="Value that triggered anomaly")


class ComparisonRequest(BaseModel):
    """Request to compare multiple laps."""

    lap_ids: List[int] = Field(
        ..., min_length=2, max_length=5, description="Lap IDs to compare (2-5 laps)"
    )


class ComparisonResponse(BaseModel):
    """Lap comparison response."""

    laps: List[LapResponse] = Field(..., description="Laps being compared")
    fastest_lap_id: int = Field(..., description="ID of fastest lap")
    time_deltas: dict = Field(
        ..., description="Time differences between laps by sector"
    )
    suggestions: List[str] = Field(..., description="Improvement suggestions")


# Statistics models
class BestLapStats(BaseModel):
    """Best lap statistics."""

    lap: LapResponse = Field(..., description="Lap details")
    driver: str = Field(..., description="Driver name")
    circuit: str = Field(..., description="Circuit name")
    vehicle: str = Field(..., description="Vehicle name")
    session_date: DateTime = Field(..., description="Session date")


class DriverStats(BaseModel):
    """Driver statistics."""

    driver_name: str = Field(..., description="Driver name")
    total_sessions: int = Field(..., description="Total sessions")
    total_laps: int = Field(..., description="Total laps driven")
    best_lap_time: Optional[float] = Field(default=None, description="Best lap time overall")
    avg_lap_time: Optional[float] = Field(default=None, description="Average lap time")
    total_distance: Optional[float] = Field(default=None, description="Total distance in km")


class CircuitStats(BaseModel):
    """Circuit statistics."""

    circuit_name: str = Field(..., description="Circuit name")
    total_sessions: int = Field(..., description="Total sessions on circuit")
    total_laps: int = Field(..., description="Total laps on circuit")
    best_lap_time: Optional[float] = Field(default=None, description="Best lap time on circuit")
    best_lap_driver: Optional[str] = Field(default=None, description="Driver with best lap")


# Configuration models
class ConnectionConfig(BaseModel):
    """Connection configuration."""

    host: str = Field("127.0.0.1", description="LFS server host")
    port: int = Field(29999, ge=1, le=65535, description="InSim port")
    app_name: str = Field("LFS-Ayats", max_length=16, description="Application name")


class ConfigResponse(BaseModel):
    """Current system configuration."""

    connection: ConnectionConfig = Field(..., description="Connection settings")
    telemetry_rate: int = Field(
        10, ge=1, le=100, description="Telemetry collection rate (Hz)"
    )
    auto_export: bool = Field(False, description="Auto-export sessions")
    export_format: str = Field("csv", description="Export format (csv, json, excel)")


class CircuitInfo(BaseModel):
    """Circuit information."""

    name: str = Field(..., description="Circuit full name")
    short_name: str = Field(..., description="Circuit short code")
    length: Optional[float] = Field(default=None, description="Circuit length in meters")


class VehicleInfo(BaseModel):
    """Vehicle information."""

    name: str = Field(..., description="Vehicle full name")
    short_name: str = Field(..., description="Vehicle short code")
    class_type: Optional[str] = Field(default=None, description="Vehicle class")


# System models
class HealthResponse(BaseModel):
    """API health check response."""

    status: str = Field("healthy", description="Health status")
    version: str = Field(default="0.1.0", description="API version")


class SystemStatusResponse(BaseModel):
    """System status response."""

    connected: bool = Field(..., description="LFS connection status")
    uptime: float = Field(..., description="System uptime in seconds")
    sessions_count: int = Field(..., description="Total sessions in database")
    laps_count: int = Field(..., description="Total laps in database")
    last_telemetry: Optional[DateTime] = Field(
        None, description="Last telemetry timestamp"
    )


# Export models
class ExportFormat(BaseModel):
    """Export format specification."""

    format: str = Field(..., description="Export format (csv, json, excel)")
    include_telemetry: bool = Field(
        True, description="Include telemetry data points"
    )


class ExportResponse(BaseModel):
    """Export operation response."""

    filename: str = Field(..., description="Generated filename")
    size: int = Field(..., description="File size in bytes")
    records: int = Field(..., description="Number of records exported")


# WebSocket models
class LiveTelemetryMessage(BaseModel):
    """Live telemetry WebSocket message."""

    type: str = Field("telemetry", description="Message type")
    data: TelemetryPoint = Field(..., description="Telemetry data")
    session_id: Optional[int] = Field(default=None, description="Current session ID")


class WebSocketError(BaseModel):
    """WebSocket error message."""

    type: str = Field("error", description="Message type")
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
