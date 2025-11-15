"""
Tests for Streaming Overlay
"""

import pytest
from unittest.mock import patch, MagicMock
from src.integrations.streaming_overlay import StreamingOverlay


@pytest.fixture
def overlay():
    """Create StreamingOverlay instance for testing."""
    return StreamingOverlay(port=5001, host="127.0.0.1")


@pytest.fixture
def sample_telemetry():
    """Sample telemetry data for testing."""
    return {
        "speed": 120.5,
        "rpm": 6500,
        "gear": 4,
        "lap_time": 98.456,
        "position": "2/10",
    }


class TestStreamingOverlay:
    """Test cases for StreamingOverlay."""

    def test_init(self, overlay):
        """Test overlay initialization."""
        assert overlay.port == 5001
        assert overlay.host == "127.0.0.1"
        assert overlay.debug is False
        assert overlay.current_data == {}
        assert overlay._running is False

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        overlay = StreamingOverlay()
        assert overlay.port == 5000
        assert overlay.host == "0.0.0.0"
        assert overlay.debug is False

    def test_update_telemetry(self, overlay, sample_telemetry):
        """Test telemetry data update."""
        overlay.update_telemetry(sample_telemetry)

        assert overlay.current_data["speed"] == 120.5
        assert overlay.current_data["rpm"] == 6500
        assert overlay.current_data["gear"] == 4
        assert overlay.current_data["lap_time"] == 98.456
        assert overlay.current_data["position"] == "2/10"

    def test_update_telemetry_partial(self, overlay):
        """Test partial telemetry data update."""
        overlay.update_telemetry({"speed": 100})
        assert overlay.current_data["speed"] == 100

        overlay.update_telemetry({"rpm": 5000})
        assert overlay.current_data["speed"] == 100
        assert overlay.current_data["rpm"] == 5000

    def test_update_telemetry_when_running(self, overlay, sample_telemetry):
        """Test telemetry update broadcasts when server is running."""
        overlay._running = True

        with patch.object(overlay.socketio, "emit") as mock_emit:
            overlay.update_telemetry(sample_telemetry)

            mock_emit.assert_called_once_with("telemetry_update", sample_telemetry)

    def test_update_telemetry_when_not_running(self, overlay, sample_telemetry):
        """Test telemetry update doesn't broadcast when server is stopped."""
        overlay._running = False

        with patch.object(overlay.socketio, "emit") as mock_emit:
            overlay.update_telemetry(sample_telemetry)

            # Should not emit when not running
            mock_emit.assert_not_called()

    def test_routes_setup(self, overlay):
        """Test that Flask routes are properly set up."""
        # Get the Flask app's URL map
        rules = list(overlay.app.url_map.iter_rules())
        endpoints = [rule.endpoint for rule in rules]

        # Check if our custom endpoints exist
        assert "index" in endpoints
        assert "get_telemetry" in endpoints
        assert "health" in endpoints

    def test_health_endpoint(self, overlay):
        """Test health check endpoint."""
        with overlay.app.test_client() as client:
            response = client.get("/health")
            data = response.get_json()

            assert response.status_code == 200
            assert data["status"] == "ok"
            assert data["running"] is False

    def test_telemetry_endpoint(self, overlay, sample_telemetry):
        """Test telemetry API endpoint."""
        overlay.update_telemetry(sample_telemetry)

        with overlay.app.test_client() as client:
            response = client.get("/api/telemetry")
            data = response.get_json()

            assert response.status_code == 200
            assert data["speed"] == 120.5
            assert data["rpm"] == 6500

    def test_index_endpoint(self, overlay):
        """Test index endpoint returns HTML."""
        with overlay.app.test_client() as client:
            response = client.get("/")

            assert response.status_code == 200
            assert b"<!DOCTYPE html>" in response.data
            assert b"LFS Telemetry Overlay" in response.data

    def test_start_server(self, overlay):
        """Test starting the server."""
        with patch.object(overlay.socketio, "run") as mock_run:
            with patch("threading.Thread") as mock_thread:
                overlay.start()

                assert overlay._running is True
                mock_thread.assert_called_once()

    def test_start_server_already_running(self, overlay):
        """Test starting server when already running."""
        overlay._running = True

        with patch("threading.Thread") as mock_thread:
            overlay.start()

            # Should not create a new thread
            mock_thread.assert_not_called()

    def test_stop_server(self, overlay):
        """Test stopping the server."""
        overlay._running = True
        overlay.stop()

        assert overlay._running is False

    def test_is_running(self, overlay):
        """Test is_running method."""
        assert overlay.is_running() is False

        overlay._running = True
        assert overlay.is_running() is True

        overlay._running = False
        assert overlay.is_running() is False
