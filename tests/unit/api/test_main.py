"""
Unit tests for FastAPI main application.

Tests app initialization, lifespan, and middleware setup.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from src.api.main import app, lifespan


class TestAppConfiguration:
    """Test FastAPI application configuration."""

    def test_app_title(self):
        """Test application has correct title."""
        assert app.title == "LFS-Ayats API"

    def test_app_description(self):
        """Test application has description."""
        assert app.description is not None
        assert len(app.description) > 0

    def test_app_version(self):
        """Test application has version."""
        assert app.version == "0.1.0"

    def test_app_docs_url(self):
        """Test documentation URLs are configured."""
        assert app.docs_url == "/api/docs"
        assert app.redoc_url == "/api/redoc"
        assert app.openapi_url == "/api/openapi.json"


class TestMiddleware:
    """Test middleware configuration."""

    @patch('src.api.dependencies.init_dependencies')
    def test_cors_middleware_configured(self, mock_init_deps):
        """Test CORS middleware is properly configured."""
        # Create client which will trigger middleware setup
        with TestClient(app) as client:
            # Test CORS headers by making request
            response = client.get("/api/v1/health")
            
            # CORS middleware should be present
            # The app should respond successfully
            assert response.status_code == 200

    @patch('src.api.dependencies.init_dependencies')
    def test_logging_middleware_attached(self, mock_init_deps):
        """Test logging middleware is attached to app."""
        # Check that middleware is in the app
        middleware_types = [type(m).__name__ for m in app.user_middleware]
        
        # Should have CORS and potentially logging middleware
        assert len(app.user_middleware) > 0


class TestRouters:
    """Test router registration."""

    def test_system_router_registered(self):
        """Test system router is registered."""
        routes = [route.path for route in app.routes]
        assert "/api/v1/health" in routes
        assert "/api/v1/status" in routes

    def test_sessions_router_registered(self):
        """Test sessions router is registered."""
        routes = [route.path for route in app.routes]
        assert "/api/v1/sessions/" in routes

    def test_laps_router_registered(self):
        """Test laps router is registered."""
        routes = [route.path for route in app.routes]
        # Check for lap-related routes
        lap_routes = [r for r in routes if 'lap' in r.lower()]
        assert len(lap_routes) > 0

    def test_telemetry_router_registered(self):
        """Test telemetry router is registered."""
        routes = [route.path for route in app.routes]
        telemetry_routes = [r for r in routes if 'telemetry' in r.lower()]
        assert len(telemetry_routes) > 0

    def test_analysis_router_registered(self):
        """Test analysis router is registered."""
        routes = [route.path for route in app.routes]
        analysis_routes = [r for r in routes if 'analysis' in r.lower()]
        assert len(analysis_routes) > 0

    def test_stats_router_registered(self):
        """Test stats router is registered."""
        routes = [route.path for route in app.routes]
        stats_routes = [r for r in routes if 'stats' in r.lower()]
        assert len(stats_routes) > 0

    def test_export_router_registered(self):
        """Test export router is registered."""
        routes = [route.path for route in app.routes]
        export_routes = [r for r in routes if 'export' in r.lower()]
        assert len(export_routes) > 0

    def test_config_router_registered(self):
        """Test config router is registered."""
        routes = [route.path for route in app.routes]
        config_routes = [r for r in routes if 'config' in r.lower()]
        assert len(config_routes) > 0


class TestRootEndpoints:
    """Test root endpoint behavior."""

    @patch('src.api.dependencies.init_dependencies')
    def test_root_redirects_to_docs(self, mock_init_deps):
        """Test root path redirects to documentation."""
        with TestClient(app) as client:
            response = client.get("/", follow_redirects=False)
            assert response.status_code == 307
            assert "/api/docs" in response.headers["location"]

    @patch('src.api.dependencies.init_dependencies')
    def test_api_root_returns_info(self, mock_init_deps):
        """Test /api endpoint returns API information."""
        with TestClient(app) as client:
            response = client.get("/api")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "LFS-Ayats API"
            assert "docs" in data
            assert "version" in data


@pytest.mark.asyncio
class TestLifespan:
    """Test application lifespan management."""

    @patch('src.api.main.logger')
    async def test_lifespan_startup_logging(self, mock_logger):
        """Test lifespan startup logging."""
        mock_app = MagicMock()
        
        async with lifespan(mock_app):
            pass
        
        # Verify startup logging occurred
        assert mock_logger.info.called
        startup_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Starting" in msg for msg in startup_calls)

    @patch('src.api.main.logger')
    async def test_lifespan_shutdown_logging(self, mock_logger):
        """Test lifespan shutdown logging."""
        mock_app = MagicMock()
        
        async with lifespan(mock_app):
            pass  # Exit context to trigger shutdown
        
        # Verify shutdown logging
        shutdown_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Shutting down" in msg for msg in shutdown_calls)

    async def test_lifespan_context_manager(self):
        """Test lifespan is a proper async context manager."""
        mock_app = MagicMock()
        
        # Should not raise any exceptions
        async with lifespan(mock_app):
            assert True  # Successfully entered context
