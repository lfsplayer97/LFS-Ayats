"""
Unit tests for InSim Client
"""

import pytest
import socket
from unittest.mock import Mock, patch, MagicMock
from src.connection.insim_client import InSimClient, PacketType, InSimVersion


class TestInSimClient:
    """Test cases for InSimClient"""

    def test_init(self):
        """Test client initialization"""
        client = InSimClient(
            host="192.168.1.100",
            port=12345,
            admin_password="test",
            app_name="TestApp"
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

    @patch('socket.socket')
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

    @patch('socket.socket')
    def test_connect_udp(self, mock_socket):
        """Test UDP connection"""
        client = InSimClient(udp=True)
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        result = client.connect()
        
        assert result is True
        assert client.connected is True
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)

    @patch('socket.socket')
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

    @patch('socket.socket')
    def test_send_packet(self, mock_socket):
        """Test sending packet"""
        client = InSimClient()
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        client.connect()
        
        test_packet = b'\x00\x01\x02\x03'
        client.send_packet(test_packet)
        
        mock_sock_instance.sendall.assert_called_once_with(test_packet)

    def test_send_packet_not_connected(self):
        """Test sending packet when not connected"""
        client = InSimClient()
        
        with pytest.raises(ConnectionError):
            client.send_packet(b'\x00\x01\x02\x03')

    @patch('socket.socket')
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

    @patch('socket.socket')
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
