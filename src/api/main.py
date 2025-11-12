"""
FastAPI application for LFS-Ayats telemetry system.

Main application setup with routers, middleware, and configuration.

Usage:
    # Development
    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

    # Production
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

API Documentation:
    - Swagger UI: http://localhost:8000/api/docs
    - ReDoc: http://localhost:8000/api/redoc
    - OpenAPI JSON: http://localhost:8000/api/openapi.json
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.utils import get_logger, configure_root_logger
from src.api import __version__
from src.api.middleware import LoggingMiddleware, setup_cors
from src.api.dependencies import init_dependencies
from src.api.routers import (
    system,
    sessions,
    laps,
    telemetry,
    analysis,
    stats,
    export,
    config,
)

# Configure logging
configure_root_logger()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting LFS-Ayats API...")
    init_dependencies(db_connection_string="sqlite:///telemetry.db")
    logger.info("API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down LFS-Ayats API...")


# Create FastAPI application
app = FastAPI(
    title="LFS-Ayats API",
    description=(
        "REST API for Live for Speed Telemetry System. "
        "Provides access to telemetry data, session management, "
        "real-time data streaming, and analysis tools."
    ),
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Setup middleware
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(system.router, prefix="/api/v1", tags=["System"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["Sessions"])
app.include_router(laps.router, prefix="/api/v1", tags=["Laps"])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["Telemetry"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["Statistics"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])
app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])


@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint - redirects to API documentation.
    """
    return RedirectResponse(url="/api/docs")


@app.get("/api", include_in_schema=False)
async def api_root():
    """
    API root endpoint - returns basic information.
    """
    return {
        "name": "LFS-Ayats API",
        "version": __version__,
        "description": "REST API for Live for Speed Telemetry System",
        "docs": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc",
            "openapi": "/api/openapi.json",
        },
        "endpoints": {
            "system": "/api/v1/health, /api/v1/status, /api/v1/connect, /api/v1/disconnect",
            "sessions": "/api/v1/sessions",
            "laps": "/api/v1/{session_id}/laps, /api/v1/{lap_id}",
            "telemetry": "/api/v1/telemetry/live (WebSocket), /api/v1/telemetry/range",
            "analysis": "/api/v1/analysis/sectors, /api/v1/analysis/anomalies, /api/v1/analysis/compare",
            "statistics": "/api/v1/stats/best-laps, /api/v1/stats/driver, /api/v1/stats/circuit",
            "export": "/api/v1/export/csv, /api/v1/export/json, /api/v1/export/session",
            "config": "/api/v1/config, /api/v1/config/circuits, /api/v1/config/vehicles",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
