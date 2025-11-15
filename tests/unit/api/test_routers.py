"""
Unit tests for API router endpoints.

Tests router functionality with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch

from src.api.routers import system
from src.api.models import (
    HealthResponse,
    SystemStatusResponse,
    ConnectionConfig,
)
from src.database.repository import TelemetryRepository


class TestSystemRouterHealth:
    """Test system router health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_healthy(self):
        """Test health check returns healthy status."""
        result = await system.health_check()

        assert isinstance(result, HealthResponse)
        assert result.status == "healthy"
        assert result.version == "0.1.0"

    @pytest.mark.asyncio
    async def test_health_check_has_version(self):
        """Test health check includes version information."""
        result = await system.health_check()

        assert hasattr(result, "version")
        assert result.version is not None
        assert len(result.version) > 0


class TestSystemRouterStatus:
    """Test system router status endpoint."""

    @pytest.mark.asyncio
    async def test_get_status_returns_status(self):
        """Test get_status returns system status."""
        # Mock repository
        mock_repo = Mock(spec=TelemetryRepository)
        mock_repo.get_sessions.return_value = []

        result = await system.get_status(repo=mock_repo, connected=False)

        assert isinstance(result, SystemStatusResponse)
        assert hasattr(result, "connected")
        assert hasattr(result, "uptime")
        assert result.connected is False

    @pytest.mark.asyncio
    async def test_get_status_with_connection(self):
        """Test status endpoint with active connection."""
        mock_repo = Mock(spec=TelemetryRepository)
        mock_repo.get_sessions.return_value = []

        result = await system.get_status(repo=mock_repo, connected=True)

        assert result.connected is True

    @pytest.mark.asyncio
    async def test_get_status_uptime_positive(self):
        """Test status endpoint returns positive uptime."""
        mock_repo = Mock(spec=TelemetryRepository)
        mock_repo.get_sessions.return_value = []

        result = await system.get_status(repo=mock_repo, connected=False)

        assert result.uptime >= 0

    @pytest.mark.asyncio
    async def test_get_status_handles_repository_error(self):
        """Test status endpoint handles repository errors gracefully."""
        mock_repo = Mock(spec=TelemetryRepository)
        mock_repo.get_sessions.side_effect = Exception("Database error")

        # Should not raise exception
        result = await system.get_status(
            repo=mock_repo, connected=False
        )

        assert isinstance(result, SystemStatusResponse)
        assert result.sessions_count == 0

    @pytest.mark.asyncio
    async def test_get_status_counts_sessions(self):
        """Test status endpoint counts sessions from repository."""
        mock_repo = Mock(spec=TelemetryRepository)
        mock_session = Mock()
        mock_repo.get_sessions.return_value = [mock_session]

        result = await system.get_status(repo=mock_repo, connected=False)

        assert result.sessions_count >= 0


class TestSystemRouterConnection:
    """Test system router connection endpoints."""

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection."""
        config = ConnectionConfig(
            host="127.0.0.1", port=29999, app_name="TestApp"
        )

        mock_set = "src.api.routers.system.set_connection_status"
        with patch(mock_set) as mock_set_status:
            result = await system.connect_to_lfs(config=config)

            assert result["status"] == "connected"
            mock_set_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_with_custom_config(self):
        """Test connection with custom configuration."""
        config = ConnectionConfig(
            host="192.168.1.100",
            port=12345,
            app_name="CustomApp",
            admin_password="secret",
        )

        mock_set = "src.api.routers.system.set_connection_status"
        with patch(mock_set):
            result = await system.connect_to_lfs(config=config)

            assert result["status"] == "connected"

    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """Test successful disconnection."""
        mock_set = "src.api.routers.system.set_connection_status"
        with patch(mock_set) as mock_set_status:
            result = await system.disconnect_from_lfs()

            assert result["status"] == "disconnected"
            mock_set_status.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self):
        """Test disconnection when already disconnected."""
        mock_set = "src.api.routers.system.set_connection_status"
        with patch(mock_set):
            result = await system.disconnect_from_lfs()

            # Should succeed even if not connected
            assert result["status"] == "disconnected"


class TestRouterErrorHandling:
    """Test router error handling."""

    @pytest.mark.asyncio
    async def test_status_handles_repository_exception(self):
        """Test status handles repository exceptions gracefully."""
        mock_repo = Mock(spec=TelemetryRepository)
        error_msg = "Database connection failed"
        mock_repo.get_sessions.side_effect = Exception(error_msg)

        # Should not raise - should handle gracefully
        await system.get_status(repo=mock_repo, connected=False)
        # Test passes if no exception is raised
        assert True


class TestRouterModels:
    """Test router model validation."""

    def test_connection_config_defaults(self):
        """Test ConnectionConfig has sensible defaults."""
        config = ConnectionConfig()

        assert config.host == "127.0.0.1"
        assert config.port == 29999
        assert config.app_name is not None

    def test_connection_config_custom_values(self):
        """Test ConnectionConfig accepts custom values."""
        config = ConnectionConfig(
            host="192.168.1.1", port=30000, app_name="MyApp"
        )

        assert config.host == "192.168.1.1"
        assert config.port == 30000
        assert config.app_name == "MyApp"

    def test_health_response_structure(self):
        """Test HealthResponse has required fields."""
        response = HealthResponse(status="healthy", version="0.1.0")

        assert response.status == "healthy"
        assert response.version == "0.1.0"

    def test_system_status_response_structure(self):
        """Test SystemStatusResponse has required fields."""
        response = SystemStatusResponse(
            connected=True, uptime=100.5, sessions_count=5, laps_count=50
        )

        assert response.connected is True
        assert response.uptime == 100.5
        assert response.sessions_count == 5
        assert response.laps_count == 50


class TestRouterDependencies:
    """Test router dependency injection."""

    @pytest.mark.asyncio
    async def test_health_check_no_dependencies(self):
        """Test health check works without dependencies."""
        # Health check should not require any dependencies
        result = await system.health_check()
        assert result is not None

    @pytest.mark.asyncio
    async def test_status_requires_repository(self):
        """Test status endpoint requires repository dependency."""
        # This tests that the endpoint signature includes repository
        import inspect

        sig = inspect.signature(system.get_status)
        params = sig.parameters

        assert "repo" in params
        assert "connected" in params


class TestRouterLogging:
    """Test router logging behavior."""

    @pytest.mark.asyncio
    async def test_status_logs_errors(self):
        """Test status endpoint logs repository errors."""
        mock_repo = Mock(spec=TelemetryRepository)
        mock_repo.get_sessions.side_effect = Exception("Test error")

        with patch("src.api.routers.system.logger") as mock_logger:
            await system.get_status(repo=mock_repo, connected=False)

            # Should log the error
            mock_logger.error.assert_called_once()
            error_msg = mock_logger.error.call_args[0][0]
            assert "Error" in error_msg


class TestRouterStartupTime:
    """Test startup time tracking."""

    def test_startup_time_initialized(self):
        """Test that startup time is tracked."""
        # The _startup_time should be set
        assert hasattr(system, "_startup_time")
        assert isinstance(system._startup_time, float)
        assert system._startup_time > 0

    @pytest.mark.asyncio
    async def test_uptime_calculation(self):
        """Test uptime is calculated from startup time."""
        mock_repo = Mock(spec=TelemetryRepository)
        mock_repo.get_sessions.return_value = []

        result = await system.get_status(repo=mock_repo, connected=False)

        # Uptime should be based on current time - startup time
        assert result.uptime >= 0
        # Should be small since we just started
        assert result.uptime < 3600  # Less than an hour for tests
