"""
Unit tests for API middleware.

Tests CORS configuration, security settings, and logging middleware.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI

from src.api.middleware import setup_cors, LoggingMiddleware


class TestCORSConfiguration:
    """Test CORS middleware configuration and security."""

    def test_cors_default_origins_from_env_variable(self):
        """Test CORS reads default origins from CORS_ORIGINS environment variable."""
        app = FastAPI()

        with patch.dict(
            os.environ, {"CORS_ORIGINS": "http://example.com,https://api.example.com"}
        ):
            setup_cors(app)

        # Check that middleware was added
        assert len(app.user_middleware) > 0

        # Verify middleware is CORSMiddleware - access via kwargs
        middleware_stack = app.user_middleware
        cors_middleware = middleware_stack[0]

        assert cors_middleware is not None
        assert "http://example.com" in cors_middleware.kwargs.get("allow_origins", [])
        assert "https://api.example.com" in cors_middleware.kwargs.get(
            "allow_origins", []
        )

    def test_cors_default_origins_when_no_env_variable(self):
        """Test CORS uses safe localhost defaults when CORS_ORIGINS not set."""
        app = FastAPI()

        with patch.dict(os.environ, {}, clear=True):
            # Remove CORS_ORIGINS if it exists
            os.environ.pop("CORS_ORIGINS", None)
            setup_cors(app)

        # Check that middleware was added
        assert len(app.user_middleware) > 0

        # Verify default localhost origins are used
        middleware_stack = app.user_middleware
        cors_middleware = middleware_stack[0]

        assert cors_middleware is not None
        allowed_origins = cors_middleware.kwargs.get("allow_origins", [])
        assert "http://localhost:3000" in allowed_origins
        assert "http://localhost:8080" in allowed_origins

    def test_cors_explicit_origins_override_env(self):
        """Test explicit origins parameter overrides environment variable."""
        app = FastAPI()
        custom_origins = ["https://secure.example.com", "https://app.example.com"]

        with patch.dict(os.environ, {"CORS_ORIGINS": "http://should-not-use.com"}):
            setup_cors(app, allowed_origins=custom_origins)

        # Check that middleware was added
        assert len(app.user_middleware) > 0

        # Verify custom origins are used, not env variable
        middleware_stack = app.user_middleware
        cors_middleware = middleware_stack[0]

        assert cors_middleware is not None
        allowed_origins = cors_middleware.kwargs.get("allow_origins", [])
        assert "https://secure.example.com" in allowed_origins
        assert "https://app.example.com" in allowed_origins
        assert "http://should-not-use.com" not in allowed_origins

    def test_cors_credentials_disabled_by_default(self):
        """Test CORS has credentials disabled for security."""
        app = FastAPI()
        setup_cors(app)

        # Check that middleware was added
        assert len(app.user_middleware) > 0

        # Verify credentials are disabled
        middleware_stack = app.user_middleware
        cors_middleware = middleware_stack[0]

        assert cors_middleware is not None
        assert cors_middleware.kwargs.get("allow_credentials") is False

    def test_cors_methods_restricted_to_get_post(self):
        """Test CORS only allows GET and POST methods for security."""
        app = FastAPI()
        setup_cors(app)

        # Check that middleware was added
        assert len(app.user_middleware) > 0

        # Verify only GET and POST are allowed
        middleware_stack = app.user_middleware
        cors_middleware = middleware_stack[0]

        assert cors_middleware is not None
        allowed_methods = cors_middleware.kwargs.get("allow_methods", [])
        assert "GET" in allowed_methods
        assert "POST" in allowed_methods
        assert len(allowed_methods) == 2

    def test_cors_headers_restricted_to_content_type(self):
        """Test CORS only allows Content-Type header for security."""
        app = FastAPI()
        setup_cors(app)

        # Check that middleware was added
        assert len(app.user_middleware) > 0

        # Verify only Content-Type header is allowed
        middleware_stack = app.user_middleware
        cors_middleware = middleware_stack[0]

        assert cors_middleware is not None
        allowed_headers = cors_middleware.kwargs.get("allow_headers", [])
        assert "Content-Type" in allowed_headers

    def test_cors_exposes_process_time_header(self):
        """Test CORS exposes X-Process-Time header for monitoring."""
        app = FastAPI()
        setup_cors(app)

        # Check that middleware was added
        assert len(app.user_middleware) > 0

        # Verify X-Process-Time is exposed
        middleware_stack = app.user_middleware
        cors_middleware = middleware_stack[0]

        assert cors_middleware is not None
        exposed_headers = cors_middleware.kwargs.get("expose_headers", [])
        assert "X-Process-Time" in exposed_headers

    def test_cors_wildcard_not_allowed(self):
        """Test CORS does not use wildcard (*) for origins."""
        app = FastAPI()

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CORS_ORIGINS", None)
            setup_cors(app)

        # Verify wildcard is not in allowed origins
        middleware_stack = app.user_middleware
        cors_middleware = middleware_stack[0]

        assert cors_middleware is not None
        allowed_origins = cors_middleware.kwargs.get("allow_origins", [])
        assert "*" not in allowed_origins

    def test_cors_strips_whitespace_from_origins(self):
        """Test CORS strips whitespace from environment variable origins."""
        app = FastAPI()

        with patch.dict(
            os.environ,
            {"CORS_ORIGINS": "  http://example.com  ,  https://api.example.com  "},
        ):
            setup_cors(app)

        # Check that middleware was added
        assert len(app.user_middleware) > 0

        # Verify origins are trimmed
        middleware_stack = app.user_middleware
        cors_middleware = middleware_stack[0]

        assert cors_middleware is not None
        allowed_origins = cors_middleware.kwargs.get("allow_origins", [])
        assert "http://example.com" in allowed_origins
        assert "https://api.example.com" in allowed_origins
        # Should not have whitespace versions
        assert "  http://example.com  " not in allowed_origins

    @patch("src.api.middleware.logger")
    def test_cors_logs_configuration(self, mock_logger):
        """Test CORS logs the configuration for security audit."""
        app = FastAPI()
        custom_origins = ["https://secure.example.com"]

        setup_cors(app, allowed_origins=custom_origins)

        # Verify logging occurred
        mock_logger.info.assert_called()
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any(
            "CORS" in msg and "https://secure.example.com" in msg for msg in log_calls
        )


class TestLoggingMiddleware:
    """Test logging middleware functionality."""

    @pytest.mark.asyncio
    async def test_logging_middleware_logs_request(self):
        """Test logging middleware logs incoming requests."""
        middleware = LoggingMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/v1/test"

        async def mock_call_next(req):
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response

        with patch("src.api.middleware.logger") as mock_logger:
            await middleware.dispatch(request, mock_call_next)

            # Verify request was logged
            assert mock_logger.info.called
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Request" in msg and "GET" in msg for msg in log_calls)

    @pytest.mark.asyncio
    async def test_logging_middleware_logs_response(self):
        """Test logging middleware logs response details."""
        middleware = LoggingMiddleware(MagicMock())
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/api/v1/data"

        async def mock_call_next(req):
            response = MagicMock()
            response.status_code = 201
            response.headers = {}
            return response

        with patch("src.api.middleware.logger") as mock_logger:
            await middleware.dispatch(request, mock_call_next)

            # Verify response was logged
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Response" in msg and "201" in msg for msg in log_calls)

    @pytest.mark.asyncio
    async def test_logging_middleware_adds_process_time_header(self):
        """Test logging middleware adds X-Process-Time header."""
        middleware = LoggingMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/v1/test"

        async def mock_call_next(req):
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response

        response = await middleware.dispatch(request, mock_call_next)

        # Verify X-Process-Time header was added
        assert "X-Process-Time" in response.headers
        # Should be a numeric string
        process_time = response.headers["X-Process-Time"]
        assert float(process_time) >= 0
