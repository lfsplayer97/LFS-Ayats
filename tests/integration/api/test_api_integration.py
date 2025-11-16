"""
Integration tests for API endpoints.

Tests complete API functionality with real FastAPI test client.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.dependencies import init_dependencies


@pytest.fixture
def client():
    """Create test client with initialized dependencies."""
    # Initialize with in-memory database for testing
    init_dependencies(db_connection_string="sqlite:///:memory:")

    with TestClient(app) as test_client:
        yield test_client


class TestSystemEndpoints:
    """Test system endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_redirect(self, client):
        """Test root redirects to docs."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/api/docs" in response.headers["location"]

    def test_api_root(self, client):
        """Test API root endpoint."""
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "LFS-Ayats API"
        assert "docs" in data

    def test_get_status(self, client):
        """Test status endpoint."""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert "connected" in data
        assert "uptime" in data
        assert "sessions_count" in data

    def test_connect(self, client):
        """Test connect endpoint."""
        response = client.post(
            "/api/v1/connect",
            json={"host": "127.0.0.1", "port": 29999, "app_name": "TestApp"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "connected"

    def test_disconnect(self, client):
        """Test disconnect endpoint."""
        response = client.post("/api/v1/disconnect")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "disconnected"


class TestSessionEndpoints:
    """Test session endpoints."""

    def test_list_sessions_empty(self, client):
        """Test listing sessions when database is empty."""
        response = client.get("/api/v1/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_create_session(self, client):
        """Test creating a new session."""
        session_data = {
            "circuit": "Blackwood GP",
            "vehicle": "XF GTI",
            "driver": "TestDriver",
        }
        response = client.post("/api/v1/sessions/", json=session_data)
        assert response.status_code == 201
        data = response.json()
        assert data["driver"] == "TestDriver"
        assert data["circuit"] == "Blackwood GP"
        assert "id" in data

    def test_get_session_not_found(self, client):
        """Test getting non-existent session returns 404."""
        response = client.get("/api/v1/sessions/99999")
        assert response.status_code == 404

    def test_list_sessions_with_filters(self, client):
        """Test listing sessions with query filters."""
        response = client.get("/api/v1/sessions/?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestLapEndpoints:
    """Test lap endpoints."""

    def test_list_laps_session_not_found(self, client):
        """Test listing laps for non-existent session."""
        response = client.get("/api/v1/99999/laps")
        assert response.status_code == 404

    def test_get_lap_not_found(self, client):
        """Test getting non-existent lap returns 404."""
        response = client.get("/api/v1/99999")
        assert response.status_code == 404

    def test_compare_laps_invalid_count(self, client):
        """Test comparing laps with invalid count."""
        # Less than 2 laps
        response = client.get("/api/v1/compare?lap_ids=1")
        assert response.status_code == 422  # Validation error


class TestAnalysisEndpoints:
    """Test analysis endpoints."""

    def test_get_sector_analysis_not_found(self, client):
        """Test sector analysis for non-existent lap."""
        response = client.get("/api/v1/analysis/sectors/99999")
        assert response.status_code == 404

    def test_get_anomalies_not_found(self, client):
        """Test anomalies for non-existent session."""
        response = client.get("/api/v1/analysis/anomalies/99999")
        assert response.status_code == 404

    def test_get_predictions_not_found(self, client):
        """Test predictions for non-existent session."""
        response = client.get("/api/v1/analysis/predictions/99999")
        assert response.status_code == 404

    def test_compare_laps_endpoint(self, client):
        """Test lap comparison endpoint."""
        response = client.post(
            "/api/v1/analysis/compare",
            json={"lap_ids": [1, 2]},
        )
        # Will fail with 404 since laps don't exist, but validates endpoint
        assert response.status_code in [404, 422]


class TestStatsEndpoints:
    """Test statistics endpoints."""

    def test_get_best_laps(self, client):
        """Test getting best laps."""
        response = client.get("/api/v1/stats/best-laps?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_driver_stats(self, client):
        """Test getting driver statistics."""
        response = client.get("/api/v1/stats/driver/TestDriver")
        assert response.status_code == 200
        data = response.json()
        assert "driver_name" in data
        assert data["driver_name"] == "TestDriver"

    def test_get_circuit_stats(self, client):
        """Test getting circuit statistics."""
        response = client.get("/api/v1/stats/circuit/Blackwood")
        assert response.status_code == 200
        data = response.json()
        assert "circuit_name" in data
        assert data["circuit_name"] == "Blackwood"


class TestExportEndpoints:
    """Test export endpoints."""

    def test_export_lap_csv_not_found(self, client):
        """Test exporting non-existent lap to CSV."""
        response = client.get("/api/v1/export/csv/99999")
        assert response.status_code == 404

    def test_export_lap_json_not_found(self, client):
        """Test exporting non-existent lap to JSON."""
        response = client.get("/api/v1/export/json/99999")
        assert response.status_code == 404

    def test_export_session_not_found(self, client):
        """Test exporting non-existent session."""
        response = client.get("/api/v1/export/session/99999?format=csv")
        assert response.status_code == 404


class TestConfigEndpoints:
    """Test configuration endpoints."""

    def test_get_config(self, client):
        """Test getting current configuration."""
        response = client.get("/api/v1/config/")
        assert response.status_code == 200
        data = response.json()
        assert "connection" in data
        assert "telemetry_rate" in data

    def test_update_config(self, client):
        """Test updating configuration."""
        config_data = {
            "connection": {
                "host": "127.0.0.1",
                "port": 29999,
                "app_name": "LFS-Ayats",
            },
            "telemetry_rate": 10,
            "auto_export": False,
            "export_format": "csv",
        }
        response = client.put("/api/v1/config/", json=config_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"

    def test_list_circuits(self, client):
        """Test listing available circuits."""
        response = client.get("/api/v1/config/circuits")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_vehicles(self, client):
        """Test listing available vehicles."""
        response = client.get("/api/v1/config/vehicles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestOpenAPISchema:
    """Test OpenAPI schema generation."""

    def test_openapi_schema(self, client):
        """Test OpenAPI schema is available."""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "LFS-Ayats API"
