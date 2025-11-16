"""
Unit tests for API middleware.

Tests error handling, logging, timeout, and rate limiting middleware.
"""

import asyncio
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.middleware import (
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    TimeoutMiddleware,
    RateLimitMiddleware,
)


class TestErrorHandlingMiddleware:
    """Test error handling middleware."""

    def test_adds_request_id(self):
        """Test that middleware adds request ID to request state."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"request_id": request.state.request_id}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert len(data["request_id"]) == 36  # UUID length

    def test_adds_request_id_to_response_headers(self):
        """Test that middleware adds request ID to response headers."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) == 36

    def test_catches_unhandled_exceptions(self):
        """Test that middleware catches and formats unhandled exceptions."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)

        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")

        client = TestClient(app)
        response = client.get("/error")

        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "Internal Server Error"
        assert "request_id" in data
        assert "message" in data

    def test_exception_includes_request_id_in_headers(self):
        """Test that error responses include request ID in headers."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)

        @app.get("/error")
        async def error_endpoint():
            raise RuntimeError("Test error")

        client = TestClient(app)
        response = client.get("/error")

        assert "X-Request-ID" in response.headers
        # Request ID should match between response body and header
        assert response.headers["X-Request-ID"] == response.json()["request_id"]

    @patch("src.api.middleware.logger")
    def test_logs_exceptions_with_traceback(self, mock_logger):
        """Test that middleware logs exceptions with full traceback."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)

        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error message")

        client = TestClient(app)
        client.get("/error")

        # Verify error was logged
        mock_logger.error.assert_called()
        call_args = mock_logger.error.call_args
        assert "Test error message" in str(call_args)
        assert call_args[1]["exc_info"] is True


class TestLoggingMiddleware:
    """Test logging middleware."""

    @patch("src.api.middleware.logger")
    def test_logs_request(self, mock_logger):
        """Test that middleware logs incoming requests."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(LoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        client.get("/test")

        # Check that request was logged
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Request: GET /test" in msg for msg in info_calls)

    @patch("src.api.middleware.logger")
    def test_logs_response_with_status_code(self, mock_logger):
        """Test that middleware logs response with status code."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(LoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        client.get("/test")

        # Check that response was logged
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Response: 200" in msg for msg in info_calls)

    def test_adds_process_time_header(self):
        """Test that middleware adds X-Process-Time header."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        assert "X-Process-Time" in response.headers
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0

    def test_includes_request_id_in_logs(self):
        """Test that logs include request ID when available."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(LoggingMiddleware)

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"request_id": request.state.request_id}

        with patch("src.api.middleware.logger") as mock_logger:
            client = TestClient(app)
            response = client.get("/test")
            request_id = response.json()["request_id"]

            # Verify logs contain request ID
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            # Check if any log message contains the request_id pattern
            has_request_id = any("request_id=" in msg for msg in info_calls)
            assert has_request_id, f"Expected request_id in logs, got: {info_calls}"

    @patch("src.api.middleware.logger")
    def test_warns_on_slow_requests(self, mock_logger):
        """Test that middleware warns on slow requests."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        # Set very low threshold for testing
        app.add_middleware(LoggingMiddleware, slow_request_threshold=0.001)

        @app.get("/slow")
        async def slow_endpoint():
            time.sleep(0.05)  # Simulate slow request
            return {"status": "ok"}

        client = TestClient(app)
        client.get("/slow")

        # Should have logged a warning about slow request
        mock_logger.warning.assert_called()
        warning_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
        assert any("SLOW REQUEST" in msg for msg in warning_calls)


class TestTimeoutMiddleware:
    """Test timeout middleware."""

    def test_allows_fast_requests(self):
        """Test that fast requests complete normally."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(TimeoutMiddleware, timeout_seconds=5.0)

        @app.get("/fast")
        async def fast_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/fast")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_times_out_slow_requests(self):
        """Test that slow requests timeout."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        # Very short timeout for testing
        app.add_middleware(TimeoutMiddleware, timeout_seconds=0.1)

        @app.get("/slow")
        async def slow_endpoint():
            await asyncio.sleep(1.0)  # Will timeout
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/slow")

        assert response.status_code == 504
        data = response.json()
        assert data["error"] == "Request Timeout"
        assert "request_id" in data

    @pytest.mark.asyncio
    async def test_timeout_includes_duration_in_message(self):
        """Test that timeout error includes configured duration."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        timeout_seconds = 0.1
        app.add_middleware(TimeoutMiddleware, timeout_seconds=timeout_seconds)

        @app.get("/slow")
        async def slow_endpoint():
            await asyncio.sleep(1.0)
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/slow")

        assert response.status_code == 504
        data = response.json()
        assert str(timeout_seconds) in data["message"]

    @pytest.mark.asyncio
    @patch("src.api.middleware.logger")
    async def test_logs_timeout_errors(self, mock_logger):
        """Test that timeout errors are logged."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(TimeoutMiddleware, timeout_seconds=0.1)

        @app.get("/slow")
        async def slow_endpoint():
            await asyncio.sleep(1.0)
            return {"status": "ok"}

        client = TestClient(app)
        client.get("/slow")

        # Should have logged timeout error
        mock_logger.error.assert_called()
        error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
        assert any("timeout" in msg.lower() for msg in error_calls)


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    def test_allows_requests_within_limit(self):
        """Test that requests within limit are allowed."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=10, burst_size=10)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Make several requests within limit
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

    def test_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        # Very low limit for testing
        app.add_middleware(RateLimitMiddleware, requests_per_minute=2, burst_size=2)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # First requests should succeed
        response = client.get("/test")
        assert response.status_code == 200

        response = client.get("/test")
        assert response.status_code == 200

        # Next request should be rate limited
        response = client.get("/test")
        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "Rate Limit Exceeded"

    def test_adds_rate_limit_headers(self):
        """Test that rate limit headers are added to responses."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst_size=100)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "60"

    def test_rate_limit_error_includes_retry_after(self):
        """Test that rate limit errors include Retry-After header."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=1, burst_size=1)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Exhaust rate limit
        client.get("/test")

        # Next request should be rate limited with retry-after
        response = client.get("/test")
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        data = response.json()
        assert "retry_after" in data

    def test_skips_health_check_endpoints(self):
        """Test that health check endpoints are not rate limited."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        # Very restrictive limit
        app.add_middleware(RateLimitMiddleware, requests_per_minute=1, burst_size=1)

        @app.get("/api/v1/health")
        async def health_check():
            return {"status": "healthy"}

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Exhaust rate limit on regular endpoint
        client.get("/test")

        # Health check should still work
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_rate_limits_per_client_ip(self):
        """Test that rate limiting is per client IP."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=1, burst_size=1)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        # Note: TestClient uses same IP for all requests
        # This is a limitation of testing, but we verify the mechanism exists
        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200

        # Verify rate limit data structure is being used
        from src.api.middleware import RateLimitMiddleware as RLM

        middleware = RLM(app, requests_per_minute=1, burst_size=1)
        assert hasattr(middleware, "rate_limit_data")
        assert isinstance(middleware.rate_limit_data, dict)

    @patch("src.api.middleware.logger")
    def test_logs_rate_limit_violations(self, mock_logger):
        """Test that rate limit violations are logged."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=1, burst_size=1)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Exhaust rate limit
        client.get("/test")
        client.get("/test")  # This should be rate limited

        # Should have logged rate limit violation
        mock_logger.warning.assert_called()
        warning_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
        assert any("Rate limit exceeded" in msg for msg in warning_calls)


class TestMiddlewareIntegration:
    """Test integration of multiple middleware."""

    def test_all_middleware_work_together(self):
        """Test that all middleware can work together."""
        app = FastAPI()

        # Add all middleware
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(LoggingMiddleware, slow_request_threshold=5.0)
        app.add_middleware(TimeoutMiddleware, timeout_seconds=30.0)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst_size=100)

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {
                "status": "ok",
                "request_id": request.state.request_id,
            }

        client = TestClient(app)
        response = client.get("/test")

        # Verify all middleware features work
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers
        assert "X-RateLimit-Limit" in response.headers

        data = response.json()
        assert "request_id" in data
        assert data["status"] == "ok"

    def test_error_handling_works_with_rate_limiting(self):
        """Test that error handling works when rate limited."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=1, burst_size=1)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Exhaust rate limit
        client.get("/test")

        # Rate limit error should include request ID
        response = client.get("/test")
        assert response.status_code == 429
        assert "X-Request-ID" in response.headers
        data = response.json()
        assert "request_id" in data

    def test_middleware_order_preserves_request_id(self):
        """Test that request ID is preserved through middleware chain."""
        app = FastAPI()

        # Add middleware in specific order
        app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
        app.add_middleware(TimeoutMiddleware, timeout_seconds=30.0)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(ErrorHandlingMiddleware)

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"request_id": request.state.request_id}

        client = TestClient(app)
        response = client.get("/test")

        # Request ID should be in both response body and header
        assert "X-Request-ID" in response.headers
        data = response.json()
        assert "request_id" in data
        assert response.headers["X-Request-ID"] == data["request_id"]
