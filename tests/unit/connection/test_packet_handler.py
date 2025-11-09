"""
Unit tests for PacketHandler
"""

import pytest
import struct
from src.connection.packet_handler import PacketHandler, PacketInfo, TinySubtype


class TestPacketHandler:
    """Test cases for PacketHandler"""

    def test_init(self):
        """Test handler initialization"""
        handler = PacketHandler()
        assert handler.handlers == {}
        assert handler.packet_count == {}

    def test_register_handler(self):
        """Test handler registration"""
        handler = PacketHandler()
        callback = lambda x: None
        
        handler.register_handler(1, callback)
        
        assert 1 in handler.handlers
        assert handler.handlers[1] == callback

    def test_parse_packet_valid(self):
        """Test parsing valid packet"""
        handler = PacketHandler()
        
        # Create a simple packet: size=4, type=1, req_id=0, sub_type=0
        packet = struct.pack("=4B", 1, 1, 0, 0)  # size is in multiples of 4
        
        info = handler.parse_packet(packet)
        
        assert info is not None
        assert info.size == 4  # 1 * 4
        assert info.type == 1
        assert info.req_id == 0

    def test_parse_packet_empty(self):
        """Test parsing empty packet"""
        handler = PacketHandler()
        
        info = handler.parse_packet(b'')
        
        assert info is None

    def test_parse_packet_too_short(self):
        """Test parsing packet that's too short"""
        handler = PacketHandler()
        
        info = handler.parse_packet(b'\x00\x01')
        
        assert info is None

    def test_parse_packet_incomplete(self):
        """Test parsing incomplete packet"""
        handler = PacketHandler()
        
        # Say size is 8 bytes but only provide 4
        packet = struct.pack("=4B", 2, 1, 0, 0)  # size=2*4=8 bytes
        
        info = handler.parse_packet(packet)
        
        assert info is None

    def test_process_packet_with_handler(self):
        """Test processing packet with registered handler"""
        handler = PacketHandler()
        called = []
        
        def test_handler(packet_info):
            called.append(packet_info)
        
        handler.register_handler(1, test_handler)
        
        packet = struct.pack("=4B", 1, 1, 0, 0)
        result = handler.process_packet(packet)
        
        assert result is True
        assert len(called) == 1
        assert called[0].type == 1

    def test_process_packet_without_handler(self):
        """Test processing packet without handler"""
        handler = PacketHandler()
        
        packet = struct.pack("=4B", 1, 1, 0, 0)
        result = handler.process_packet(packet)
        
        assert result is False

    def test_parse_version_packet(self):
        """Test parsing IS_VER packet"""
        handler = PacketHandler()
        
        # struct IS_VER: Size(1), Type(1), ReqI(1), Zero(1), Version(8), Product(6), InSimVer(2)
        packet = struct.pack(
            "=4B8s6sH",
            5,  # Size (5*4=20 bytes)
            2,  # Type (ISP_VER)
            0,  # ReqI
            0,  # Zero
            b'0.6V\x00\x00\x00\x00',  # Version
            b'S2\x00\x00\x00\x00',     # Product
            9   # InSimVer
        )
        
        info = handler.parse_version_packet(packet)
        
        assert info is not None
        assert info['version'] == '0.6V'
        assert info['product'] == 'S2'
        assert info['insim_version'] == 9

    def test_get_packet_stats(self):
        """Test getting packet statistics"""
        handler = PacketHandler()
        
        # Process some packets
        handler.parse_packet(struct.pack("=4B", 1, 1, 0, 0))
        handler.parse_packet(struct.pack("=4B", 1, 2, 0, 0))
        handler.parse_packet(struct.pack("=4B", 1, 1, 0, 0))
        
        stats = handler.get_packet_stats()
        
        assert stats[1] == 2
        assert stats[2] == 1

    def test_reset_stats(self):
        """Test resetting statistics"""
        handler = PacketHandler()
        
        handler.parse_packet(struct.pack("=4B", 1, 1, 0, 0))
        handler.reset_stats()
        
        stats = handler.get_packet_stats()
        assert stats == {}
