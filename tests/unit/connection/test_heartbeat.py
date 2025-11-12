"""
Unit tests for HeartbeatManager
"""

import time
from unittest.mock import Mock, patch
from src.connection.heartbeat import HeartbeatManager
from src.connection.insim_client import InSimClient, TinySubtype


class TestHeartbeatManager:
    """Test cases for HeartbeatManager"""

    def test_init(self):
        """Test HeartbeatManager initialization"""
        client = Mock(spec=InSimClient)
        manager = HeartbeatManager(client, interval=15.0)

        assert manager.client is client
        assert manager.interval == 15.0
        assert manager.thread is None
        assert not manager._stop.is_set()

    def test_default_interval(self):
        """Test default interval is 30 seconds"""
        client = Mock(spec=InSimClient)
        manager = HeartbeatManager(client)

        assert manager.interval == 30.0

    @patch("threading.Thread")
    def test_start(self, mock_thread):
        """Test starting heartbeat thread"""
        client = Mock(spec=InSimClient)
        manager = HeartbeatManager(client, interval=10.0)

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        manager.start()

        # Check thread was created and started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        assert not manager._stop.is_set()

    @patch("threading.Thread")
    def test_start_stops_previous_thread(self, mock_thread):
        """Test that starting heartbeat stops previous thread"""
        client = Mock(spec=InSimClient)
        manager = HeartbeatManager(client)

        # Create a mock existing thread
        existing_thread = Mock()
        existing_thread.is_alive.return_value = True
        manager.thread = existing_thread

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        manager.start()

        # Previous thread should be stopped
        existing_thread.join.assert_called_once()

    def test_stop_no_thread(self):
        """Test stopping when no thread exists"""
        client = Mock(spec=InSimClient)
        manager = HeartbeatManager(client)

        # Should not raise an error
        manager.stop()
        assert manager.thread is None

    def test_stop_dead_thread(self):
        """Test stopping when thread is not alive"""
        client = Mock(spec=InSimClient)
        manager = HeartbeatManager(client)

        mock_thread = Mock()
        mock_thread.is_alive.return_value = False
        manager.thread = mock_thread

        manager.stop()

        # Thread join should not be called if not alive
        mock_thread.join.assert_not_called()

    def test_stop_active_thread(self):
        """Test stopping an active thread"""
        client = Mock(spec=InSimClient)
        manager = HeartbeatManager(client)

        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        manager.thread = mock_thread

        manager.stop()

        # Check that stop event was set and thread joined
        assert manager._stop.is_set()
        mock_thread.join.assert_called_once_with(timeout=2.0)
        assert manager.thread is None

    def test_heartbeat_loop_sends_tiny_none(self):
        """Test that heartbeat loop sends TINY_NONE packets"""
        client = Mock(spec=InSimClient)
        client.connected = True
        client.send_tiny = Mock()

        manager = HeartbeatManager(client, interval=0.1)

        # Start and quickly stop the heartbeat
        manager.start()
        time.sleep(0.2)  # Let it run for one iteration
        manager.stop()

        # Verify send_tiny was called with TINY_NONE
        assert client.send_tiny.call_count >= 1
        client.send_tiny.assert_called_with(TinySubtype.TINY_NONE)

    def test_heartbeat_loop_stops_when_disconnected(self):
        """Test that heartbeat loop stops when client disconnects"""
        client = Mock(spec=InSimClient)
        client.connected = False  # Not connected
        client.send_tiny = Mock()

        manager = HeartbeatManager(client, interval=0.1)

        # Start the heartbeat
        manager.start()
        time.sleep(0.2)
        manager.stop()

        # send_tiny should not be called when not connected
        client.send_tiny.assert_not_called()

    def test_heartbeat_loop_triggers_reconnect_on_failure(self):
        """Test that heartbeat loop triggers reconnect on send failure"""
        client = Mock(spec=InSimClient)
        client.connected = True
        client.reconnect_enabled = True
        client.send_tiny = Mock(side_effect=Exception("Connection lost"))
        client.trigger_reconnect = Mock()

        manager = HeartbeatManager(client, interval=0.1)

        # Start the heartbeat
        manager.start()
        time.sleep(0.2)
        manager.stop()

        # trigger_reconnect should be called
        client.trigger_reconnect.assert_called_once()

    def test_heartbeat_loop_no_reconnect_when_disabled(self):
        """Test that reconnect is not triggered when disabled"""
        client = Mock(spec=InSimClient)
        client.connected = True
        client.reconnect_enabled = False  # Disabled
        client.send_tiny = Mock(side_effect=Exception("Connection lost"))
        client.trigger_reconnect = Mock()

        manager = HeartbeatManager(client, interval=0.1)

        # Start the heartbeat
        manager.start()
        time.sleep(0.2)
        manager.stop()

        # trigger_reconnect should not be called
        client.trigger_reconnect.assert_not_called()

    def test_interval_can_be_changed(self):
        """Test that interval can be changed after initialization"""
        client = Mock(spec=InSimClient)
        manager = HeartbeatManager(client, interval=30.0)

        assert manager.interval == 30.0

        manager.interval = 60.0
        assert manager.interval == 60.0
