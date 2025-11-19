"""
Unit tests for api.exceptions module.

Tests for custom HTTP exception classes.
"""

import pytest
from fastapi import status
from src.api.exceptions import (
    SessionNotFoundError,
    LapNotFoundError,
    CircuitNotFoundError,
    VehicleNotFoundError,
    InvalidParameterError,
    ConnectionError,
    ExportError,
    DatabaseError,
)


class TestSessionNotFoundError:
    """Test cases for SessionNotFoundError exception."""

    def test_exception_creation(self):
        """Test exception creation with session ID."""
        exception = SessionNotFoundError(session_id=123)
        assert exception.status_code == status.HTTP_404_NOT_FOUND
        assert "123" in exception.detail
        assert "Session" in exception.detail

    def test_exception_can_be_raised(self):
        """Test exception can be raised."""
        with pytest.raises(SessionNotFoundError) as exc_info:
            raise SessionNotFoundError(session_id=456)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestLapNotFoundError:
    """Test cases for LapNotFoundError exception."""

    def test_exception_creation(self):
        """Test exception creation with lap ID."""
        exception = LapNotFoundError(lap_id=789)
        assert exception.status_code == status.HTTP_404_NOT_FOUND
        assert "789" in exception.detail
        assert "Lap" in exception.detail

    def test_exception_can_be_raised(self):
        """Test exception can be raised."""
        with pytest.raises(LapNotFoundError) as exc_info:
            raise LapNotFoundError(lap_id=101)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestCircuitNotFoundError:
    """Test cases for CircuitNotFoundError exception."""

    def test_exception_creation(self):
        """Test exception creation with circuit name."""
        exception = CircuitNotFoundError(circuit_name="Blackwood")
        assert exception.status_code == status.HTTP_404_NOT_FOUND
        assert "Blackwood" in exception.detail
        assert "Circuit" in exception.detail

    def test_exception_with_short_name(self):
        """Test exception with short circuit code."""
        exception = CircuitNotFoundError(circuit_name="BL1")
        assert "BL1" in exception.detail

    def test_exception_can_be_raised(self):
        """Test exception can be raised."""
        with pytest.raises(CircuitNotFoundError) as exc_info:
            raise CircuitNotFoundError(circuit_name="FE2")
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestVehicleNotFoundError:
    """Test cases for VehicleNotFoundError exception."""

    def test_exception_creation(self):
        """Test exception creation with vehicle name."""
        exception = VehicleNotFoundError(vehicle_name="XFG")
        assert exception.status_code == status.HTTP_404_NOT_FOUND
        assert "XFG" in exception.detail
        assert "Vehicle" in exception.detail

    def test_exception_with_full_name(self):
        """Test exception with full vehicle name."""
        exception = VehicleNotFoundError(vehicle_name="XF GTI")
        assert "XF GTI" in exception.detail

    def test_exception_can_be_raised(self):
        """Test exception can be raised."""
        with pytest.raises(VehicleNotFoundError) as exc_info:
            raise VehicleNotFoundError(vehicle_name="FBM")
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestInvalidParameterError:
    """Test cases for InvalidParameterError exception."""

    def test_exception_creation(self):
        """Test exception creation with parameter and reason."""
        exception = InvalidParameterError(
            parameter="lap_count", reason="must be positive"
        )
        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert "lap_count" in exception.detail
        assert "must be positive" in exception.detail

    def test_exception_with_different_parameters(self):
        """Test exception with various parameters."""
        exception = InvalidParameterError(
            parameter="speed", reason="exceeds maximum allowed value"
        )
        assert "speed" in exception.detail
        assert "exceeds maximum" in exception.detail

    def test_exception_can_be_raised(self):
        """Test exception can be raised."""
        with pytest.raises(InvalidParameterError) as exc_info:
            raise InvalidParameterError(parameter="page", reason="out of range")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestConnectionError:
    """Test cases for ConnectionError exception."""

    def test_exception_creation(self):
        """Test exception creation with message."""
        exception = ConnectionError(message="Failed to connect to LFS server")
        assert exception.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Failed to connect" in exception.detail
        assert "Connection error" in exception.detail

    def test_exception_with_timeout_message(self):
        """Test exception with timeout message."""
        exception = ConnectionError(message="Connection timeout after 5 seconds")
        assert "timeout" in exception.detail

    def test_exception_with_refused_message(self):
        """Test exception with connection refused message."""
        exception = ConnectionError(message="Connection refused by server")
        assert "refused" in exception.detail

    def test_exception_can_be_raised(self):
        """Test exception can be raised."""
        with pytest.raises(ConnectionError) as exc_info:
            raise ConnectionError(message="Network unreachable")
        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestExportError:
    """Test cases for ExportError exception."""

    def test_exception_creation(self):
        """Test exception creation with message."""
        exception = ExportError(message="Failed to write CSV file")
        assert exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to write" in exception.detail
        assert "Export error" in exception.detail

    def test_exception_with_permission_error(self):
        """Test exception with permission error message."""
        exception = ExportError(message="Permission denied")
        assert "Permission denied" in exception.detail

    def test_exception_with_format_error(self):
        """Test exception with format error message."""
        exception = ExportError(message="Unsupported export format")
        assert "Unsupported" in exception.detail

    def test_exception_can_be_raised(self):
        """Test exception can be raised."""
        with pytest.raises(ExportError) as exc_info:
            raise ExportError(message="Disk full")
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestDatabaseError:
    """Test cases for DatabaseError exception."""

    def test_exception_creation(self):
        """Test exception creation with message."""
        exception = DatabaseError(message="Connection pool exhausted")
        assert exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Connection pool" in exception.detail
        assert "Database error" in exception.detail

    def test_exception_with_query_error(self):
        """Test exception with query error message."""
        exception = DatabaseError(message="Invalid SQL syntax")
        assert "Invalid SQL" in exception.detail

    def test_exception_with_constraint_violation(self):
        """Test exception with constraint violation message."""
        exception = DatabaseError(message="Foreign key constraint violation")
        assert "constraint" in exception.detail

    def test_exception_can_be_raised(self):
        """Test exception can be raised."""
        with pytest.raises(DatabaseError) as exc_info:
            raise DatabaseError(message="Table does not exist")
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestAllExceptionsInheritFromHTTPException:
    """Test that all custom exceptions inherit from HTTPException."""

    def test_session_not_found_inheritance(self):
        """Test SessionNotFoundError inherits from HTTPException."""
        from fastapi import HTTPException

        exception = SessionNotFoundError(session_id=1)
        assert isinstance(exception, HTTPException)

    def test_lap_not_found_inheritance(self):
        """Test LapNotFoundError inherits from HTTPException."""
        from fastapi import HTTPException

        exception = LapNotFoundError(lap_id=1)
        assert isinstance(exception, HTTPException)

    def test_circuit_not_found_inheritance(self):
        """Test CircuitNotFoundError inherits from HTTPException."""
        from fastapi import HTTPException

        exception = CircuitNotFoundError(circuit_name="BL1")
        assert isinstance(exception, HTTPException)

    def test_vehicle_not_found_inheritance(self):
        """Test VehicleNotFoundError inherits from HTTPException."""
        from fastapi import HTTPException

        exception = VehicleNotFoundError(vehicle_name="XFG")
        assert isinstance(exception, HTTPException)

    def test_invalid_parameter_inheritance(self):
        """Test InvalidParameterError inherits from HTTPException."""
        from fastapi import HTTPException

        exception = InvalidParameterError(parameter="test", reason="test")
        assert isinstance(exception, HTTPException)

    def test_connection_error_inheritance(self):
        """Test ConnectionError inherits from HTTPException."""
        from fastapi import HTTPException

        exception = ConnectionError(message="test")
        assert isinstance(exception, HTTPException)

    def test_export_error_inheritance(self):
        """Test ExportError inherits from HTTPException."""
        from fastapi import HTTPException

        exception = ExportError(message="test")
        assert isinstance(exception, HTTPException)

    def test_database_error_inheritance(self):
        """Test DatabaseError inherits from HTTPException."""
        from fastapi import HTTPException

        exception = DatabaseError(message="test")
        assert isinstance(exception, HTTPException)
