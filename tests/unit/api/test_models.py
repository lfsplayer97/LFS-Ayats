"""
Unit tests for API models.

Tests Pydantic model validation and serialization.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.api.models import (
    SessionCreate,
    SessionResponse,
    LapResponse,
    TelemetryPoint,
    ComparisonRequest,
    HealthResponse,
    ConnectionConfig,
)


class TestSessionModels:
    """Test session-related models."""

    def test_session_create_valid(self):
        """Test creating valid session data."""
        session = SessionCreate(
            circuit="Blackwood GP",
            vehicle="XF GTI",
            driver="TestDriver",
        )
        assert session.circuit == "Blackwood GP"
        assert session.vehicle == "XF GTI"
        assert session.driver == "TestDriver"

    def test_session_response_valid(self):
        """Test session response model."""
        session = SessionResponse(
            id=1,
            circuit="Blackwood GP",
            vehicle="XF GTI",
            driver="TestDriver",
            datetime=datetime.now(),
            duration=300,
            total_laps=5,
            best_lap_time=85.5,
        )
        assert session.id == 1
        assert session.total_laps == 5
        assert session.best_lap_time == 85.5


class TestLapModels:
    """Test lap-related models."""

    def test_lap_response_valid(self):
        """Test lap response model."""
        lap = LapResponse(
            id=1,
            session_id=1,
            lap_number=3,
            lap_time=85.5,
            sector1_time=28.5,
            sector2_time=27.0,
            sector3_time=30.0,
            valid=True,
        )
        assert lap.lap_number == 3
        assert lap.lap_time == 85.5
        assert lap.valid is True

    def test_lap_number_validation(self):
        """Test lap number must be positive."""
        with pytest.raises(ValidationError):
            LapResponse(
                id=1,
                session_id=1,
                lap_number=0,  # Invalid: must be >= 1
                lap_time=85.5,
            )


class TestTelemetryModels:
    """Test telemetry-related models."""

    def test_telemetry_point_valid(self):
        """Test telemetry point model."""
        point = TelemetryPoint(
            timestamp=123.45,
            speed=180.5,
            rpm=7500,
            gear=4,
            throttle=0.8,
            brake=0.0,
            position_x=100.0,
            position_y=200.0,
            position_z=10.0,
        )
        assert point.speed == 180.5
        assert point.rpm == 7500
        assert point.gear == 4

    def test_telemetry_point_throttle_validation(self):
        """Test throttle must be between 0 and 1."""
        with pytest.raises(ValidationError):
            TelemetryPoint(
                timestamp=123.45,
                speed=180.5,
                rpm=7500,
                gear=4,
                throttle=1.5,  # Invalid: must be <= 1
                brake=0.0,
                position_x=100.0,
                position_y=200.0,
                position_z=10.0,
            )

    def test_telemetry_point_gear_validation(self):
        """Test gear must be between -1 and 7."""
        with pytest.raises(ValidationError):
            TelemetryPoint(
                timestamp=123.45,
                speed=180.5,
                rpm=7500,
                gear=10,  # Invalid: must be <= 7
                throttle=0.8,
                brake=0.0,
                position_x=100.0,
                position_y=200.0,
                position_z=10.0,
            )


class TestComparisonModels:
    """Test comparison-related models."""

    def test_comparison_request_valid(self):
        """Test comparison request model."""
        request = ComparisonRequest(lap_ids=[1, 2, 3])
        assert len(request.lap_ids) == 3

    def test_comparison_request_min_laps(self):
        """Test comparison requires at least 2 laps."""
        with pytest.raises(ValidationError):
            ComparisonRequest(lap_ids=[1])  # Invalid: need at least 2

    def test_comparison_request_max_laps(self):
        """Test comparison allows max 5 laps."""
        with pytest.raises(ValidationError):
            ComparisonRequest(lap_ids=[1, 2, 3, 4, 5, 6])  # Invalid: max 5


class TestSystemModels:
    """Test system-related models."""

    def test_health_response(self):
        """Test health response model."""
        health = HealthResponse(status="healthy", version="0.1.0")
        assert health.status == "healthy"
        assert health.version == "0.1.0"

    def test_connection_config_valid(self):
        """Test connection configuration model."""
        config = ConnectionConfig(
            host="192.168.1.100",
            port=30000,
            app_name="MyApp",
        )
        assert config.host == "192.168.1.100"
        assert config.port == 30000

    def test_connection_config_port_validation(self):
        """Test port must be valid."""
        with pytest.raises(ValidationError):
            ConnectionConfig(
                host="127.0.0.1",
                port=70000,  # Invalid: must be <= 65535
            )
