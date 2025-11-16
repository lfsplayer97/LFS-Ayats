"""
Unit tests for InSim Client
"""

import pytest
import socket
from unittest.mock import Mock, patch
from src.connection.insim_client import InSimClient, PacketType


class TestInSimClient:
    """Test cases for InSimClient"""

    def test_init(self):
        """Test client initialization"""
        client = InSimClient(
            host="192.168.1.100", port=12345, admin_password="test", app_name="TestApp"
        )

        assert client.host == "192.168.1.100"
        assert client.port == 12345
        assert client.admin_password == "test"
        assert client.app_name == "TestApp"
        assert not client.connected
        assert client.socket is None

    def test_app_name_truncation(self):
        """Test that app name is truncated to 16 characters"""
        long_name = "A" * 20
        client = InSimClient(app_name=long_name)
        assert len(client.app_name) == 16

    @patch("socket.socket")
    def test_connect_tcp(self, mock_socket):
        """Test TCP connection"""
        client = InSimClient(udp=False)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        result = client.connect()

        assert result is True
        assert client.connected is True
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_sock_instance.connect.assert_called_once_with((client.host, client.port))

    @patch("socket.socket")
    def test_connect_udp(self, mock_socket):
        """Test UDP connection"""
        client = InSimClient(udp=True)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        result = client.connect()

        assert result is True
        assert client.connected is True
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)

    @patch("socket.socket")
    def test_connect_failure(self, mock_socket):
        """Test connection failure"""
        client = InSimClient()
        mock_socket.side_effect = socket.error("Connection refused")

        with pytest.raises(ConnectionError):
            client.connect()

    def test_initialize_not_connected(self):
        """Test initialize when not connected"""
        client = InSimClient()

        with pytest.raises(ConnectionError):
            client.initialize()

    @patch("socket.socket")
    def test_send_packet(self, mock_socket):
        """Test sending packet"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        test_packet = b"\x00\x01\x02\x03"
        client.send_packet(test_packet)

        mock_sock_instance.sendall.assert_called_once_with(test_packet)

    def test_send_packet_not_connected(self):
        """Test sending packet when not connected"""
        client = InSimClient()

        with pytest.raises(ConnectionError):
            client.send_packet(b"\x00\x01\x02\x03")

    @patch("socket.socket")
    def test_disconnect(self, mock_socket):
        """Test disconnection"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        client.disconnect()

        assert not client.connected
        assert client.socket is None
        mock_sock_instance.close.assert_called_once()

    @patch("socket.socket")
    def test_context_manager(self, mock_socket):
        """Test context manager usage"""
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        with InSimClient() as client:
            assert client.connected is True

        mock_sock_instance.close.assert_called_once()

    def test_register_callback(self):
        """Test callback registration"""
        client = InSimClient()
        callback = Mock()

        client.register_callback(PacketType.ISP_VER, callback)

        assert PacketType.ISP_VER in client.callbacks
        assert client.callbacks[PacketType.ISP_VER] == callback


class TestInSimClientEnhanced:
    """Test cases for enhanced InSim client features"""

    def test_init_with_reconnection_params(self):
        """Test initialization with reconnection parameters"""
        client = InSimClient(
            max_retries=10,
            retry_delay=3.0,
            reconnect_enabled=False,
            heartbeat_interval=60.0,
        )

        assert client.max_retries == 10
        assert client.retry_delay == 3.0
        assert client.reconnect_enabled is False
        assert client.heartbeat.interval == 60.0

    def test_connection_state_initialization(self):
        """Test that connection state is initialized"""
        from src.connection.insim_client import ConnectionState

        client = InSimClient()
        assert client.state == ConnectionState.DISCONNECTED

    def test_on_state_change_callback(self):
        """Test registering state change callbacks"""
        from src.connection.insim_client import ConnectionState

        client = InSimClient()
        callback = Mock()

        client.on_state_change(ConnectionState.CONNECTED, callback)

        assert ConnectionState.CONNECTED in client.state_callbacks
        assert callback in client.state_callbacks[ConnectionState.CONNECTED]

    @patch("socket.socket")
    def test_state_changes_on_connect(self, mock_socket):
        """Test that state changes on connection"""
        from src.connection.insim_client import ConnectionState

        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        callback = Mock()
        client.on_state_change(ConnectionState.CONNECTED, callback)

        client.connect()

        assert client.state == ConnectionState.CONNECTED
        callback.assert_called_once()

    @patch("socket.socket")
    @patch("time.sleep")
    def test_connect_with_retry_success(self, mock_sleep, mock_socket):
        """Test successful connection with retry"""
        client = InSimClient(max_retries=3, retry_delay=1.0)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        result = client.connect_with_retry()

        assert result is True
        assert mock_sleep.call_count == 0  # No retries needed

    @patch("socket.socket")
    @patch("time.sleep")
    def test_connect_with_retry_eventual_success(self, mock_sleep, mock_socket):
        """Test connection succeeds after retries"""
        client = InSimClient(max_retries=3, retry_delay=1.0)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        # Fail twice, then succeed
        mock_sock_instance.connect.side_effect = [
            socket.error("Connection refused"),
            socket.error("Connection refused"),
            None,  # Success
        ]

        result = client.connect_with_retry()

        assert result is True
        assert mock_sleep.call_count == 2  # Slept twice

    @patch("socket.socket")
    @patch("time.sleep")
    def test_connect_with_retry_max_retries(self, mock_sleep, mock_socket):
        """Test connection fails after max retries"""
        client = InSimClient(max_retries=3, retry_delay=1.0)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        # Always fail
        mock_sock_instance.connect.side_effect = socket.error("Connection refused")

        result = client.connect_with_retry()

        assert result is False
        assert (
            mock_sleep.call_count == 2
        )  # Sleep happens after 1st and 2nd failure (not after 3rd)

    @patch("socket.socket")
    @patch("time.sleep")
    def test_exponential_backoff(self, mock_sleep, mock_socket):
        """Test exponential backoff in retries"""
        client = InSimClient(max_retries=3, retry_delay=2.0)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.connect.side_effect = socket.error("Connection refused")

        client.connect_with_retry()

        # Check sleep calls use exponential backoff
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls == [2.0, 4.0]  # 2 * 2^0, 2 * 2^1 (stops at max_retries=3)

    def test_validate_packet_valid(self):
        """Test packet validation with valid packet"""
        client = InSimClient()

        # Create valid packet: size=1 (means 4 bytes), type=ISP_VER, reqId=0, zero=0
        packet = bytes([1, 2, 0, 0])

        result = client.validate_packet(packet)

        assert result is True

    def test_validate_packet_too_short(self):
        """Test packet validation rejects short packets"""
        client = InSimClient()

        packet = bytes([1, 2])  # Only 2 bytes

        result = client.validate_packet(packet)

        assert result is False

    def test_validate_packet_size_mismatch(self):
        """Test packet validation detects size mismatch"""
        client = InSimClient()

        # Declare size 2 (means 8 bytes) but only have 4 bytes
        packet = bytes([2, 2, 0, 0])

        result = client.validate_packet(packet)

        assert result is False

    def test_validate_packet_unknown_type(self):
        """Test packet validation with unknown type (should still pass)"""
        client = InSimClient()

        # Use unknown packet type 255, size=1 (4 bytes total)
        packet = bytes([1, 255, 0, 0])

        result = client.validate_packet(packet)

        assert result is True  # Unknown types are allowed

    @patch("socket.socket")
    def test_send_tiny_packet(self, mock_socket):
        """Test sending TINY packet"""
        from src.connection.insim_client import TinySubtype

        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        client.send_tiny(TinySubtype.TINY_NONE)

        # Check that packet was sent
        assert mock_sock_instance.sendall.call_count == 1
        sent_packet = mock_sock_instance.sendall.call_args[0][0]

        # Verify packet structure: size=4, type=ISP_TINY, reqId=0, subtype=TINY_NONE
        assert len(sent_packet) == 4
        assert sent_packet[0] == 4
        assert sent_packet[1] == 3  # ISP_TINY
        assert sent_packet[3] == TinySubtype.TINY_NONE

    @patch("socket.socket")
    @patch("threading.Thread")
    def test_start_heartbeat(self, mock_thread, mock_socket):
        """Test starting heartbeat thread"""
        client = InSimClient(heartbeat_interval=10.0)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        client.start_heartbeat()

        # Check thread was created and started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    @patch("socket.socket")
    def test_stop_heartbeat(self, mock_socket):
        """Test stopping heartbeat thread"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Create mock thread
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        client.heartbeat.thread = mock_thread

        client.stop_heartbeat()

        # Check that stop event was set and thread joined
        assert client.heartbeat._stop.is_set()
        mock_thread.join.assert_called_once()

    @patch("socket.socket")
    def test_disconnect_stops_heartbeat(self, mock_socket):
        """Test that disconnect stops heartbeat"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Create mock heartbeat thread
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        client.heartbeat.thread = mock_thread

        client.disconnect()

        # Heartbeat should be stopped
        assert client.heartbeat._stop.is_set()

    @patch("socket.socket")
    def test_receive_packet_validates(self, mock_socket):
        """Test that receive_packet validates packets"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Return valid packet: size=1 (means 4 bytes), type=2, reqId=0, zero=0
        mock_sock_instance.recv.side_effect = [
            bytes(
                [1, 2, 0, 0]
            )  # Header (size=1 means 1*4=4 bytes total, no additional data needed)
        ]

        packet = client.receive_packet(timeout=1.0)

        assert packet is not None
        assert len(packet) == 4

    @patch("socket.socket")
    def test_receive_packet_rejects_invalid(self, mock_socket):
        """Test that receive_packet rejects invalid packets"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()

        # Return packet where size=3 (means 12 bytes) but we only return 4 bytes
        mock_sock_instance.recv.side_effect = [
            bytes([3, 2, 0, 0]),  # Header says 12 bytes
            bytes([]),  # No additional data (should have 8 more bytes)
        ]

        packet = client.receive_packet(timeout=1.0)

        # Should return None for invalid packet
        assert packet is None


class TestSocketCreation:
    """Test cases for socket creation refactoring"""

    @patch("socket.socket")
    def test_create_socket_tcp(self, mock_socket):
        """Test TCP socket creation with default timeout"""
        client = InSimClient(udp=False)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        sock = client._create_socket()

        # Verify socket was created with correct parameters
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        # Verify timeout was set (default 5.0)
        mock_sock_instance.settimeout.assert_called_once_with(5.0)
        assert sock == mock_sock_instance

    @patch("socket.socket")
    def test_create_socket_tcp_custom_timeout(self, mock_socket):
        """Test TCP socket creation with custom timeout"""
        client = InSimClient(udp=False, socket_timeout=10.0)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        sock = client._create_socket()

        # Verify socket was created with correct parameters
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        # Verify custom timeout was set
        mock_sock_instance.settimeout.assert_called_once_with(10.0)
        assert sock == mock_sock_instance

    @patch("socket.socket")
    def test_create_socket_udp(self, mock_socket):
        """Test UDP socket creation"""
        client = InSimClient(udp=True)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        sock = client._create_socket()

        # Verify socket was created with correct parameters
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        # UDP socket should NOT have timeout set
        mock_sock_instance.settimeout.assert_not_called()
        assert sock == mock_sock_instance

    def test_socket_timeout_attribute(self):
        """Test that socket_timeout attribute is set correctly"""
        # Test with default value
        client = InSimClient()
        assert client.socket_timeout == 5.0

        # Test with custom value
        client = InSimClient(socket_timeout=15.0)
        assert client.socket_timeout == 15.0

    @patch("socket.socket")
    def test_connect_uses_create_socket(self, mock_socket):
        """Test that connect method uses _create_socket"""
        client = InSimClient(udp=False, socket_timeout=7.5)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance

        client.connect()

        # Verify socket was created with correct parameters
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        # Verify custom timeout was applied
        mock_sock_instance.settimeout.assert_called_once_with(7.5)
        # Verify connection was made
        mock_sock_instance.connect.assert_called_once_with((client.host, client.port))
        assert client.connected is True
