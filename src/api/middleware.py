"""
Middleware for the API.

Provides CORS, logging, and other cross-cutting concerns.
"""

import os
import time
import logging
from typing import Callable, List, Optional
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Logs request method, path, duration, and status code.
    """

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

        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"Duration: {duration:.3f}s - "
            f"{request.method} {request.url.path}"
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)

        return response


def setup_cors(app: FastAPI, allowed_origins: Optional[List[str]] = None) -> None:
    """
    Configure CORS middleware with secure defaults.

    Reads allowed origins from CORS_ORIGINS environment variable if not provided.
    Uses strict security defaults: no credentials, limited methods.

    Args:
        app: FastAPI application instance
        allowed_origins: Optional list of allowed origins. If None, reads from
                        CORS_ORIGINS environment variable. Defaults to
                        localhost:3000 and localhost:8080 if not set.

    Example:
        # Using environment variable
        CORS_ORIGINS=http://localhost:3000,https://myapp.com

        # Using parameter
        setup_cors(app, ["http://localhost:3000", "https://myapp.com"])

    Security:
        - allow_credentials=False: Prevents credential leaks
        - allow_methods limited to GET, POST: Restricts to necessary operations
        - allow_headers limited to Content-Type: Minimizes attack surface
    """
    if allowed_origins is None:
        # Read from environment variable, default to localhost for development
        cors_origins_env = os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:8080"
        )
        allowed_origins = [origin.strip() for origin in cors_origins_env.split(",")]

    logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,  # Security: prevent credential leaks
        allow_methods=["GET", "POST"],  # Security: only necessary methods
        allow_headers=["Content-Type"],  # Security: minimal headers
        expose_headers=["X-Process-Time"],
    )
