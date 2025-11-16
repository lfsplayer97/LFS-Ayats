"""
Middleware for the API.

Provides CORS, logging, error handling, rate limiting, and other cross-cutting concerns.
"""

import time
import logging
import uuid
import asyncio
from typing import Callable, Dict, Optional
from collections import defaultdict
from datetime import datetime
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive error handling and request tracking.

    Adds request IDs, catches unhandled exceptions, and provides consistent
    error responses with proper logging.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with error handling and request ID tracking.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response with error handling
        """
        # Generate unique request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            # Process request
            response = await call_next(request)

            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Log unhandled exception with full traceback
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path} "
                f"[request_id={request_id}]: {exc}",
                exc_info=True,
            )

            # Return formatted error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": (
                        "An unexpected error occurred while "
                        "processing your request"
                    ),
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Logs request method, path, duration, status code, and request ID.
    Includes slow request warnings.
    """

    def __init__(self, app, slow_request_threshold: float = 5.0):
        """
        Initialize logging middleware.

        Args:
            app: FastAPI application
            slow_request_threshold: Seconds after which to log warning for slow requests
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        start_time = time.time()

        # Get request ID if available (set by ErrorHandlingMiddleware)
        request_id = getattr(request.state, "request_id", "unknown")

        # Log incoming request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"[request_id={request_id}]"
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response with appropriate level
        log_message = (
            f"Response: {response.status_code} - "
            f"Duration: {duration:.3f}s - "
            f"{request.method} {request.url.path} "
            f"[request_id={request_id}]"
        )

        if duration > self.slow_request_threshold:
            logger.warning(f"SLOW REQUEST: {log_message}")
        else:
            logger.info(log_message)

        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        if hasattr(request.state, "request_id"):
            response.headers["X-Request-ID"] = request.state.request_id

        return response


class TimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce request timeout limits.

    Prevents requests from running indefinitely and logs slow requests.
    """

    def __init__(self, app, timeout_seconds: float = 30.0):
        """
        Initialize timeout middleware.

        Args:
            app: FastAPI application
            timeout_seconds: Maximum request duration in seconds
        """
        super().__init__(app)
        self.timeout_seconds = timeout_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with timeout enforcement.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response or timeout error

        Raises:
            asyncio.TimeoutError: If request exceeds timeout
        """
        request_id = getattr(request.state, "request_id", "unknown")

        try:
            # Execute request with timeout
            response = await asyncio.wait_for(
                call_next(request), timeout=self.timeout_seconds
            )
            return response

        except asyncio.TimeoutError:
            # Log timeout
            logger.error(
                f"Request timeout after {self.timeout_seconds}s: "
                f"{request.method} {request.url.path} "
                f"[request_id={request_id}]"
            )

            # Return timeout error
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "error": "Request Timeout",
                    "message": (
                        f"Request exceeded maximum duration of "
                        f"{self.timeout_seconds} seconds"
                    ),
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting API requests.

    Implements token bucket algorithm for rate limiting by IP address.
    Configurable limits per endpoint or global.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute per IP
            burst_size: Maximum burst size (defaults to requests_per_minute)
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute
        self.rate_limit_data: Dict[str, Dict] = defaultdict(
            lambda: {"tokens": self.burst_size, "last_update": datetime.now()}
        )

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Args:
            request: Incoming HTTP request

        Returns:
            Client IP address
        """
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Use direct client IP
        return request.client.host if request.client else "unknown"

    def _refill_tokens(self, client_data: Dict) -> None:
        """
        Refill tokens based on time elapsed since last update.

        Args:
            client_data: Dictionary containing token count and last update time
        """
        now = datetime.now()
        time_passed = (now - client_data["last_update"]).total_seconds()

        # Calculate tokens to add based on rate
        tokens_to_add = time_passed * (self.requests_per_minute / 60.0)

        # Refill tokens up to burst size
        client_data["tokens"] = min(
            self.burst_size, client_data["tokens"] + tokens_to_add
        )
        client_data["last_update"] = now

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response or rate limit error
        """
        # Skip rate limiting for health check and docs
        if request.url.path in [
            "/api/v1/health",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
        ]:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        client_data = self.rate_limit_data[client_ip]

        # Refill tokens
        self._refill_tokens(client_data)

        # Check if request can proceed
        if client_data["tokens"] >= 1.0:
            # Consume token
            client_data["tokens"] -= 1.0

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(int(client_data["tokens"]))

            return response
        else:
            # Rate limit exceeded
            request_id = getattr(request.state, "request_id", "unknown")

            logger.warning(
                f"Rate limit exceeded for {client_ip}: "
                f"{request.method} {request.url.path} "
                f"[request_id={request_id}]"
            )

            # Calculate retry after time
            retry_after = int(
                (1.0 - client_data["tokens"]) * 60 / self.requests_per_minute
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate Limit Exceeded",
                    "message": (
                        f"Too many requests. Limit: "
                        f"{self.requests_per_minute} per minute"
                    ),
                    "retry_after": retry_after,
                    "request_id": request_id,
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(retry_after),
                    "X-Request-ID": request_id,
                },
            )


def setup_cors(app):
    """
    Configure CORS middleware.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"],
    )
