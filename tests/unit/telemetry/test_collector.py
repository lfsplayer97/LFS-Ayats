"""
Unit tests for Telemetry Collector
"""

import pytest
from unittest.mock import Mock, patch
from src.telemetry.collector import (
    TelemetryCollector,
    CarTelemetry,
    LapTelemetry,
    PlayerInfo,
)
from src.connection.insim_client import PacketType


class TestCarTelemetry:
    """Test CarTelemetry dataclass"""

    def test_default_values(self):
        """Test default initialization"""
        telemetry = CarTelemetry()

        assert telemetry.plid == 0
        assert telemetry.node == 0
        assert telemetry.lap == 0
        assert telemetry.speed == 0.0
        assert telemetry.timestamp > 0

    def test_custom_values(self):
        """Test initialization with custom values"""
        telemetry = CarTelemetry(
            timestamp=1234567890.0,
            plid=1,
            node=10,
            lap=2,
            speed=150.5,
            position={"x": 100.0, "y": 200.0, "z": 5.0},
        )

        assert telemetry.timestamp == 1234567890.0
        assert telemetry.plid == 1
        assert telemetry.speed == 150.5
        assert telemetry.position["x"] == 100.0


class TestLapTelemetry:
    """Test LapTelemetry dataclass"""

    def test_default_values(self):
        """Test default initialization"""
        lap = LapTelemetry()

        assert lap.plid == 0
        assert lap.lap == 0
        assert lap.lap_time == 0
        assert lap.elapsed_time == 0
        assert lap.split_times == []

    def test_with_split_times(self):
        """Test lap telemetry with split times"""
        lap = LapTelemetry(
            plid=1, lap=3, lap_time=90000, split_times=[30000, 30000, 30000]
        )

        assert lap.lap == 3
        assert lap.lap_time == 90000
        assert len(lap.split_times) == 3


class TestPlayerInfo:
    """Test PlayerInfo dataclass"""

    def test_default_values(self):
        """Test default initialization"""
        player = PlayerInfo()

        assert player.plid == 0
        assert player.player_name == ""
        assert player.car_name == ""

    def test_custom_values(self):
        """Test initialization with custom values"""
        player = PlayerInfo(
            plid=1,
            ucid=1,
            player_name="TestPlayer",
            car_name="XRG",
            team_name="TestTeam",
        )

        assert player.plid == 1
        assert player.player_name == "TestPlayer"
        assert player.car_name == "XRG"


class TestTelemetryCollector:
    """Test cases for TelemetryCollector"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock InSim client"""
        client = Mock()
        client.connected = True
        client.initialize = Mock()
        client.register_callback = Mock()
        client.receive_packet = Mock(return_value=None)
        return client

    def test_init(self, mock_client):
        """Test collector initialization"""
        collector = TelemetryCollector(mock_client)

        assert collector.client == mock_client
        assert collector.running is False
        assert collector.collection_thread is None
        assert collector.car_telemetry == {}
        assert collector.lap_telemetry == {}
        assert collector.player_info == {}
        assert "car_update" in collector.callbacks
        assert "lap_complete" in collector.callbacks

    def test_register_callback(self, mock_client):
        """Test callback registration"""
        collector = TelemetryCollector(mock_client)
        callback_fn = Mock()

        collector.register_callback("car_update", callback_fn)

        assert callback_fn in collector.callbacks["car_update"]

    def test_register_invalid_callback(self, mock_client):
        """Test registration of invalid callback type"""
        collector = TelemetryCollector(mock_client)
        callback_fn = Mock()

        # Should not raise error, just log warning
        collector.register_callback("invalid_event", callback_fn)

        assert callback_fn not in collector.callbacks.get("invalid_event", [])

    def test_trigger_callbacks(self, mock_client):
        """Test callback triggering"""
        collector = TelemetryCollector(mock_client)
        callback_fn = Mock()
        collector.register_callback("car_update", callback_fn)

        test_data = {"test": "data"}
        collector._trigger_callbacks("car_update", test_data)

        callback_fn.assert_called_once_with(test_data)

    def test_trigger_callbacks_with_error(self, mock_client):
        """Test callback error handling"""
        collector = TelemetryCollector(mock_client)

        # Callback that raises exception
        def error_callback(data):
            raise ValueError("Test error")

        collector.register_callback("car_update", error_callback)

        # Should not raise, just log error
        collector._trigger_callbacks("car_update", {})

    @patch("src.connection.packet_handler.PacketHandler")
    def test_handle_mci_packet(self, mock_handler_class, mock_client):
        """Test MCI packet handling"""
        collector = TelemetryCollector(mock_client)
        callback_fn = Mock()
        collector.register_callback("car_update", callback_fn)

        # Mock packet handler
        mock_handler = Mock()
        mock_handler.parse_mci_packet.return_value = {
            "cars": [
                {
                    "plid": 1,
                    "node": 10,
                    "lap": 2,
                    "position": {"x": 100.0, "y": 200.0, "z": 5.0},
                    "speed": 15000,  # Raw speed value
                    "direction": 16384,
                    "heading": 16384,
                    "angular_vel": 100,
                }
            ]
        }
        mock_handler_class.return_value = mock_handler

        # Handle packet
        packet_data = b"\x00" * 32
        collector.handle_mci_packet(packet_data)

        # Verify telemetry stored
        assert 1 in collector.car_telemetry
        assert len(collector.car_telemetry[1]) == 1

        telemetry = collector.car_telemetry[1][0]
        assert telemetry.plid == 1
        assert telemetry.node == 10
        assert telemetry.lap == 2
        assert abs(telemetry.speed - (15000 / 32768.0)) < 0.01

        # Verify callback triggered
        assert callback_fn.called

    def test_handle_lap_packet(self, mock_client):
        """Test LAP packet handling"""
        collector = TelemetryCollector(mock_client)

        # Just verify it doesn't crash (simplified implementation)
        packet_data = b"\x00" * 20
        collector.handle_lap_packet(packet_data)

    def test_start_collection(self, mock_client):
        """Test starting telemetry collection"""
        collector = TelemetryCollector(mock_client)

        with patch("src.telemetry.collector.Thread") as mock_thread:
            collector.start(interval=100)

            assert collector.running is True
            mock_client.initialize.assert_called_once_with(flags=0, interval=100)
            mock_client.register_callback.assert_any_call(
                PacketType.ISP_MCI, collector.handle_mci_packet
            )
            mock_client.register_callback.assert_any_call(
                PacketType.ISP_LAP, collector.handle_lap_packet
            )
            mock_thread.assert_called_once()

    def test_start_already_running(self, mock_client):
        """Test starting collection when already running"""
        collector = TelemetryCollector(mock_client)
        collector.running = True

        with patch("src.telemetry.collector.Thread"):
            collector.start()

            # Should not initialize again
            mock_client.initialize.assert_not_called()

    def test_stop_collection(self, mock_client):
        """Test stopping telemetry collection"""
        collector = TelemetryCollector(mock_client)

        # Start first
        with patch("src.telemetry.collector.Thread"):
            collector.start()

        # Mock the thread
        mock_thread = Mock()
        collector.collection_thread = mock_thread

        # Stop
        collector.stop()

        assert collector.running is False
        assert collector.stop_event.is_set()
        mock_thread.join.assert_called_once_with(timeout=2.0)

    def test_stop_not_running(self, mock_client):
        """Test stopping when not running"""
        collector = TelemetryCollector(mock_client)

        # Should not crash
        collector.stop()

        assert collector.running is False

    def test_get_latest_telemetry_all(self, mock_client):
        """Test getting latest telemetry for all players"""
        collector = TelemetryCollector(mock_client)

        # Add some telemetry data
        collector.car_telemetry[1] = [
            CarTelemetry(plid=1, speed=100.0, timestamp=1.0),
            CarTelemetry(plid=1, speed=110.0, timestamp=2.0),
        ]
        collector.car_telemetry[2] = [
            CarTelemetry(plid=2, speed=120.0, timestamp=1.0),
        ]

        latest = collector.get_latest_telemetry()

        assert len(latest) == 2
        assert latest[1].speed == 110.0  # Latest for player 1
        assert latest[2].speed == 120.0

    def test_get_latest_telemetry_specific_player(self, mock_client):
        """Test getting latest telemetry for specific player"""
        collector = TelemetryCollector(mock_client)

        collector.car_telemetry[1] = [
            CarTelemetry(plid=1, speed=100.0),
            CarTelemetry(plid=1, speed=110.0),
        ]

        latest = collector.get_latest_telemetry(plid=1)

        assert len(latest) == 1
        assert latest[1].speed == 110.0

    def test_get_latest_telemetry_no_data(self, mock_client):
        """Test getting latest telemetry with no data"""
        collector = TelemetryCollector(mock_client)

        latest = collector.get_latest_telemetry()

        assert latest == {}

    def test_get_telemetry_history(self, mock_client):
        """Test getting telemetry history"""
        collector = TelemetryCollector(mock_client)

        # Add history
        collector.car_telemetry[1] = [
            CarTelemetry(plid=1, speed=100.0 + i) for i in range(10)
        ]

        history = collector.get_telemetry_history(plid=1)

        assert len(history) == 10
        assert history[0].speed == 100.0
        assert history[9].speed == 109.0

    def test_get_telemetry_history_with_limit(self, mock_client):
        """Test getting limited telemetry history"""
        collector = TelemetryCollector(mock_client)

        collector.car_telemetry[1] = [
            CarTelemetry(plid=1, speed=100.0 + i) for i in range(10)
        ]

        history = collector.get_telemetry_history(plid=1, limit=5)

        assert len(history) == 5
        assert history[0].speed == 105.0  # Last 5 entries

    def test_get_telemetry_history_no_data(self, mock_client):
        """Test getting history for non-existent player"""
        collector = TelemetryCollector(mock_client)

        history = collector.get_telemetry_history(plid=999)

        assert history == []

    def test_clear_history_specific_player(self, mock_client):
        """Test clearing history for specific player"""
        collector = TelemetryCollector(mock_client)

        collector.car_telemetry[1] = [CarTelemetry(plid=1)]
        collector.car_telemetry[2] = [CarTelemetry(plid=2)]

        collector.clear_history(plid=1)

        assert len(collector.car_telemetry[1]) == 0
        assert len(collector.car_telemetry[2]) == 1

    def test_clear_history_all(self, mock_client):
        """Test clearing all history"""
        collector = TelemetryCollector(mock_client)

        collector.car_telemetry[1] = [CarTelemetry(plid=1)]
        collector.car_telemetry[2] = [CarTelemetry(plid=2)]
        collector.lap_telemetry[1] = [LapTelemetry(plid=1)]

        collector.clear_history()

        assert collector.car_telemetry == {}
        assert collector.lap_telemetry == {}

    def test_get_statistics(self, mock_client):
        """Test getting collection statistics"""
        collector = TelemetryCollector(mock_client)
        collector.running = True

        # Add some data
        collector.car_telemetry[1] = [CarTelemetry(plid=1)] * 10
        collector.car_telemetry[2] = [CarTelemetry(plid=2)] * 5

        stats = collector.get_statistics()

        assert stats["running"] is True
        assert stats["total_players"] == 2
        assert stats["total_samples"] == 15
        assert stats["players"][1] == 10
        assert stats["players"][2] == 5

    def test_get_statistics_empty(self, mock_client):
        """Test statistics with no data"""
        collector = TelemetryCollector(mock_client)

        stats = collector.get_statistics()

        assert stats["running"] is False
        assert stats["total_players"] == 0
        assert stats["total_samples"] == 0
        assert stats["players"] == {}

    @patch("src.connection.packet_handler.PacketHandler")
    def test_collection_loop_error_handling(self, mock_handler_class, mock_client):
        """Test error handling in collection loop"""
        collector = TelemetryCollector(mock_client)

        # Make receive_packet raise an error once, then return None to exit loop
        mock_client.receive_packet.side_effect = [Exception("Test error"), None]

        collector.running = True
        collector.stop_event.clear()

        # Mock sleep to avoid actual waiting
        with patch("time.sleep") as mock_sleep:
            # Run loop - it should handle error and try again
            collector._collection_loop()

            # Verify sleep was called after error
            assert mock_sleep.called

        # Should handle error gracefully
        collector.running = False
