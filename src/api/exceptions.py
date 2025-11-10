"""
Custom exceptions for the API.

Defines HTTP exceptions with appropriate status codes for API error handling.
"""

from fastapi import HTTPException, status


class SessionNotFoundError(HTTPException):
    """Session not found in database."""

    def __init__(self, session_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found",
        )


class LapNotFoundError(HTTPException):
    """Lap not found in database."""

    def __init__(self, lap_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lap with ID {lap_id} not found",
        )


class CircuitNotFoundError(HTTPException):
    """Circuit not found in database."""

    def __init__(self, circuit_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Circuit '{circuit_name}' not found",
        )


class VehicleNotFoundError(HTTPException):
    """Vehicle not found in database."""

    def __init__(self, vehicle_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle '{vehicle_name}' not found",
        )


class InvalidParameterError(HTTPException):
    """Invalid parameter provided."""

    def __init__(self, parameter: str, reason: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter '{parameter}': {reason}",
        )


class ConnectionError(HTTPException):
    """Error connecting to LFS server."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Connection error: {message}",
        )


class ExportError(HTTPException):
    """Error during export operation."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export error: {message}",
        )


class DatabaseError(HTTPException):
    """Database operation error."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {message}",
        )
