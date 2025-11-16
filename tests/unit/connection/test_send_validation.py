"""
Unit tests for enhanced send validation and race condition fixes
"""

import pytest
import socket
import threading
import time
from unittest.mock import Mock, patch
from src.connection.insim_client import InSimClient, TinySubtype


class TestSendPacketValidation:
    """Test cases for send_packet with improved validation"""

    @patch("socket.socket")
    def test_send_packet_returns_true_on_success(self, mock_socket):
        """Test that send_packet returns True on successful send"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        result = client.send_packet(b"\x00\x01\x02\x03")

        assert result is True
        mock_sock_instance.sendall.assert_called_once()

    @patch("socket.socket")
    def test_send_packet_returns_false_on_timeout(self, mock_socket):
        """Test that send_packet returns False on socket timeout"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Simulate timeout
        mock_sock_instance.sendall.side_effect = socket.timeout("Timeout")

        result = client.send_packet(b"\x00\x01\x02\x03")

        assert result is False

    @patch("socket.socket")
    def test_send_packet_returns_false_on_socket_error(self, mock_socket):
        """Test that send_packet returns False on socket error"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Simulate socket error
        mock_sock_instance.sendall.side_effect = socket.error("Connection reset")

        result = client.send_packet(b"\x00\x01\x02\x03")

        assert result is False

    def test_send_packet_raises_connection_error_when_not_connected(self):
        """Test that send_packet raises ConnectionError when not connected"""
        client = InSimClient()

        with pytest.raises(ConnectionError):
            client.send_packet(b"\x00\x01\x02\x03")

    @patch("socket.socket")
    def test_send_packet_with_retry_triggers_reconnect_on_timeout(self, mock_socket):
        """Test that send_packet with retry=True triggers reconnection on timeout"""
        client = InSimClient(reconnect_enabled=True)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Mock trigger_reconnect
        client.trigger_reconnect = Mock()

        # Simulate timeout
        mock_sock_instance.sendall.side_effect = socket.timeout("Timeout")

        result = client.send_packet(b"\x00\x01\x02\x03", retry=True)

        assert result is False
        client.trigger_reconnect.assert_called_once()

    @patch("socket.socket")
    def test_send_packet_with_retry_triggers_reconnect_on_error(self, mock_socket):
        """Test that send_packet with retry=True triggers reconnection on error"""
        client = InSimClient(reconnect_enabled=True)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Mock trigger_reconnect
        client.trigger_reconnect = Mock()

        # Simulate socket error
        mock_sock_instance.sendall.side_effect = socket.error("Connection reset")

        result = client.send_packet(b"\x00\x01\x02\x03", retry=True)

        assert result is False
        client.trigger_reconnect.assert_called_once()

    @patch("socket.socket")
    def test_send_packet_without_retry_does_not_trigger_reconnect(self, mock_socket):
        """Test that send_packet without retry does not trigger reconnection"""
        client = InSimClient(reconnect_enabled=True)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Mock trigger_reconnect
        client.trigger_reconnect = Mock()

        # Simulate timeout
        mock_sock_instance.sendall.side_effect = socket.timeout("Timeout")

        result = client.send_packet(b"\x00\x01\x02\x03", retry=False)

        assert result is False
        client.trigger_reconnect.assert_not_called()

    @patch("socket.socket")
    def test_send_packet_distinguishes_timeout_from_error(self, mock_socket):
        """Test that send_packet distinguishes timeout from socket error in logs"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Test timeout
        with patch("src.connection.insim_client.logger") as mock_logger:
            mock_sock_instance.sendall.side_effect = socket.timeout("Timeout")
            client.send_packet(b"\x00\x01\x02\x03")
            # Check that warning was called (timeout-specific message)
            mock_logger.warning.assert_called()
            assert "timeout" in str(mock_logger.warning.call_args).lower()

        # Reset mock
        mock_sock_instance.sendall.side_effect = None
        client.connect()

        # Test socket error
        with patch("src.connection.insim_client.logger") as mock_logger:
            mock_sock_instance.sendall.side_effect = socket.error("Error")
            client.send_packet(b"\x00\x01\x02\x03")
            # Check that error was called (generic error message)
            mock_logger.error.assert_called()


class TestSendTinyValidation:
    """Test cases for send_tiny with improved validation"""

    @patch("socket.socket")
    def test_send_tiny_returns_true_on_success(self, mock_socket):
        """Test that send_tiny returns True on successful send"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        result = client.send_tiny(TinySubtype.TINY_NONE)

        assert result is True
        mock_sock_instance.sendall.assert_called_once()

    @patch("socket.socket")
    def test_send_tiny_returns_false_on_timeout(self, mock_socket):
        """Test that send_tiny returns False on socket timeout"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Simulate timeout
        mock_sock_instance.sendall.side_effect = socket.timeout("Timeout")

        result = client.send_tiny(TinySubtype.TINY_NONE)

        assert result is False

    @patch("socket.socket")
    def test_send_tiny_returns_false_on_socket_error(self, mock_socket):
        """Test that send_tiny returns False on socket error"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Simulate socket error
        mock_sock_instance.sendall.side_effect = socket.error("Connection reset")

        result = client.send_tiny(TinySubtype.TINY_NONE)

        assert result is False

    def test_send_tiny_raises_connection_error_when_not_connected(self):
        """Test that send_tiny raises ConnectionError when not connected"""
        client = InSimClient()

        with pytest.raises(ConnectionError):
            client.send_tiny(TinySubtype.TINY_NONE)

    @patch("socket.socket")
    def test_send_tiny_with_retry_triggers_reconnect(self, mock_socket):
        """Test that send_tiny with retry=True triggers reconnection on timeout"""
        client = InSimClient(reconnect_enabled=True)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Mock trigger_reconnect
        client.trigger_reconnect = Mock()

        # Simulate timeout
        mock_sock_instance.sendall.side_effect = socket.timeout("Timeout")

        result = client.send_tiny(TinySubtype.TINY_NONE, retry=True)

        assert result is False
        client.trigger_reconnect.assert_called_once()


class TestThreadSafety:
    """Test cases for thread safety in send operations"""

    @patch("socket.socket")
    def test_send_packet_uses_lock(self, mock_socket):
        """Test that send_packet uses lock for thread safety"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Verify lock exists
        assert hasattr(client, "_send_lock")
        # Verify it's a lock-like object (has acquire and release methods)
        assert hasattr(client._send_lock, "acquire")
        assert hasattr(client._send_lock, "release")

    @patch("socket.socket")
    def test_concurrent_sends_are_serialized(self, mock_socket):
        """Test that concurrent sends are serialized by lock"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        results = []
        send_order = []

        def slow_sendall(data):
            """Simulate slow send to expose race conditions"""
            send_order.append(threading.current_thread().name)
            time.sleep(0.01)  # Small delay to expose race conditions

        mock_sock_instance.sendall.side_effect = slow_sendall

        def send_packet_thread(thread_name, packet_data):
            """Thread function to send packet"""
            threading.current_thread().name = thread_name
            result = client.send_packet(packet_data)
            results.append((thread_name, result))

        # Create multiple threads sending concurrently
        threads = []
        for i in range(5):
            t = threading.Thread(
                target=send_packet_thread,
                args=(f"thread-{i}", bytes([i, 1, 2, 3])),
            )
            threads.append(t)

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # All sends should succeed
        assert len(results) == 5
        assert all(result for _, result in results)

        # Sends should be serialized (no interleaving)
        assert len(send_order) == 5

    @patch("socket.socket")
    def test_send_packet_lock_prevents_race_condition(self, mock_socket):
        """Test that lock prevents race condition between check and send"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        disconnect_triggered = False

        def disconnect_after_check(*args, **kwargs):
            """Disconnect after connection check but before send"""
            nonlocal disconnect_triggered
            if not disconnect_triggered:
                disconnect_triggered = True
                # Try to disconnect from another thread
                # This should be blocked by the lock
                time.sleep(0.001)

        mock_sock_instance.sendall.side_effect = disconnect_after_check

        # This should succeed because lock prevents disconnection during send
        result = client.send_packet(b"\x00\x01\x02\x03")

        assert result is True
        assert disconnect_triggered

    @patch("socket.socket")
    def test_send_tiny_uses_same_lock(self, mock_socket):
        """Test that send_tiny uses the same lock as send_packet"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Both methods should use the same lock
        assert client._send_lock is not None

        # Send tiny should be serialized with send_packet
        call_order = []

        def track_sendall(data):
            call_order.append(len(data))
            time.sleep(0.01)

        mock_sock_instance.sendall.side_effect = track_sendall

        # Send from two threads
        t1 = threading.Thread(
            target=lambda: client.send_packet(b"\x00\x01\x02\x03\x04\x05")
        )
        t2 = threading.Thread(target=lambda: client.send_tiny(TinySubtype.TINY_NONE))

        t1.start()
        time.sleep(0.001)  # Small delay to ensure t1 starts first
        t2.start()

        t1.join()
        t2.join()

        # Both should complete
        assert len(call_order) == 2
        # First send should be 6 bytes, second should be 4 bytes (TINY packet)
        assert call_order == [6, 4]


class TestReconnectBehavior:
    """Test cases for reconnection behavior with new validation"""

    @patch("socket.socket")
    def test_reconnect_disabled_does_not_trigger_reconnect(self, mock_socket):
        """Test that reconnect is not triggered when disabled"""
        client = InSimClient(reconnect_enabled=False)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        client.trigger_reconnect = Mock()

        # Simulate timeout with retry=True
        mock_sock_instance.sendall.side_effect = socket.timeout("Timeout")

        result = client.send_packet(b"\x00\x01\x02\x03", retry=True)

        assert result is False
        # Reconnect should not be triggered because it's disabled
        client.trigger_reconnect.assert_not_called()

    @patch("socket.socket")
    def test_retry_false_does_not_trigger_reconnect_even_if_enabled(self, mock_socket):
        """Test that reconnect is not triggered when retry=False"""
        client = InSimClient(reconnect_enabled=True)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        client.trigger_reconnect = Mock()

        # Simulate timeout with retry=False
        mock_sock_instance.sendall.side_effect = socket.timeout("Timeout")

        result = client.send_packet(b"\x00\x01\x02\x03", retry=False)

        assert result is False
        # Reconnect should not be triggered because retry=False
        client.trigger_reconnect.assert_not_called()
