"""
Packet Handler
InSim packet handling and processing.

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import struct
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import IntEnum

from src.utils import get_logger

logger = get_logger(__name__)


class TinySubtype(IntEnum):
    """TINY packet subtypes"""

    TINY_NONE = 0  # No subtype
    TINY_VER = 1  # Request version
    TINY_CLOSE = 2  # Close InSim
    TINY_PING = 3  # Ping
    TINY_REPLY = 4  # Ping reply
    TINY_VTC = 5  # Vote cancel
    TINY_SCP = 6  # Send camera pos
    TINY_SST = 7  # Send state
    TINY_GTH = 8  # Get time in hundredths
    TINY_MPE = 9  # Multi player end
    TINY_ISM = 10  # InSim multi
    TINY_REN = 11  # Rename
    TINY_NCN = 12  # New connection
    TINY_NPL = 13  # New player
    TINY_RES = 14  # Result
    TINY_NLP = 15  # Node and lap
    TINY_MCI = 16  # Multi car info
    TINY_REO = 17  # Reorder
    TINY_RST = 18  # Race start
    TINY_AXI = 19  # Autocross info
    TINY_AXC = 20  # Autocross clear
    TINY_RIP = 21  # Replay info


@dataclass
class PacketInfo:
    """Information about an InSim packet"""

    size: int
    type: int
    req_id: int
    data: bytes


class PacketHandler:
    """
    Handles processing of InSim packets.

    This class is responsible for:
    - Parsing received InSim packets
    - Validating packet structure
    - Extracting data from packets
    - Managing callbacks for packet types

    Example:
        >>> handler = PacketHandler()
        >>> handler.register_handler(PacketType.ISP_VER, handle_version)
        >>> handler.process_packet(packet_data)
    """

    def __init__(self):
        """Initialize the packet handler."""
        self.handlers: Dict[int, Callable] = {}
        self.packet_count: Dict[int, int] = {}
        logger.info("PacketHandler initialized")

    def register_handler(self, packet_type: int, handler: Callable) -> None:
        """
        Register a handler for a specific packet type.

        Args:
            packet_type: Packet type (see PacketType)
            handler: Function to call when packet is received
        """
        self.handlers[packet_type] = handler
        logger.debug(f"Handler registered for type {packet_type}")

    def parse_packet(self, data: bytes) -> Optional[PacketInfo]:
        """
        Parse an InSim packet and extract basic information.

        Args:
            data: Packet data in bytes

        Returns:
            PacketInfo: Packet information or None if invalid
        """
        if not data or len(data) < 4:
            logger.warning("Packet too short")
            return None

        try:
            # Basic structure of all InSim packets:
            # byte Size;   # Size in bytes divided by 4
            # byte Type;   # Packet type (PacketType)
            # byte ReqI;   # Request ID (0 normally)
            # byte SubT;   # Subtype (depends on type)

            size, pkt_type, req_id, sub_type = struct.unpack("=4B", data[:4])

            # Actual size is size * 4
            actual_size = size * 4

            if len(data) < actual_size:
                logger.warning(
                    f"Incomplete packet: expected {actual_size}, received {len(data)}"
                )
                return None

            # Packet counter
            self.packet_count[pkt_type] = self.packet_count.get(pkt_type, 0) + 1

            return PacketInfo(
                size=actual_size, type=pkt_type, req_id=req_id, data=data[:actual_size]
            )

        except struct.error as e:
            logger.error(f"Error parsing packet: {e}")
            return None

    def process_packet(self, data: bytes) -> bool:
        """
        Process an InSim packet and call corresponding handler.

        Args:
            data: Packet data in bytes

        Returns:
            bool: True if processed successfully, False otherwise
        """
        packet_info = self.parse_packet(data)
        if not packet_info:
            return False

        # Call handler if exists
        handler = self.handlers.get(packet_info.type)
        if handler:
            try:
                handler(packet_info)
                logger.debug(f"Packet type {packet_info.type} processed")
                return True
            except Exception as e:
                logger.error(f"Error processing packet type {packet_info.type}: {e}")
                return False
        else:
            logger.debug(f"No handler for packet type {packet_info.type}")
            return False

    def parse_version_packet(self, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse an IS_VER (version) packet.

        Args:
            data: Packet data

        Returns:
            Dict with version information or None on error

        Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_VER
        """
        try:
            # struct IS_VER {
            #     byte Size;       # 20
            #     byte Type;       # ISP_VER
            #     byte ReqI;       # Request ID
            #     byte Zero;       # 0
            #     char Version[8]; # LFS version
            #     char Product[6]; # Product
            #     word InSimVer;   # InSim version
            # }

            if len(data) < 20:
                return None

            _, _, req_id, _, version, product, insim_ver = struct.unpack(
                "=4B8s6sH", data[:20]
            )

            return {
                "req_id": req_id,
                "version": version.decode("utf-8").strip("\x00"),
                "product": product.decode("utf-8").strip("\x00"),
                "insim_version": insim_ver,
            }

        except struct.error as e:
            logger.error(f"Error parsing IS_VER: {e}")
            return None

    def parse_state_packet(self, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse an IS_STA (server state) packet.

        Args:
            data: Packet data

        Returns:
            Dict with state information or None on error

        Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_STA
        """
        try:
            # struct IS_STA {
            #     byte Size;           # 28
            #     byte Type;           # ISP_STA
            #     byte ReqI;           # Request ID
            #     byte Zero;           # 0
            #     float ReplaySpeed;   # Replay speed (1.0 = normal)
            #     word Flags;          # State flags
            #     byte InGameCam;      # In-game camera
            #     byte ViewPLID;       # Player ID of view
            #     byte NumP;           # Number of players
            #     byte NumConns;       # Number of connections
            #     byte NumFinished;    # Number finished
            #     byte RaceInProg;     # 0 = no race, 1 = race, 2 = qualifying
            #     byte QualMins;       # Qualifying minutes
            #     byte RaceLaps;       # Race laps (0 = endless)
            #     byte Spare2;         # 0
            #     byte Spare3;         # 0
            #     char Track[6];       # Short track name
            #     byte Weather;        # Weather
            #     byte Wind;           # Wind
            # }

            if len(data) < 28:
                return None

            unpacked = struct.unpack("=4BfH6B6s2B", data[:28])

            return {
                "req_id": unpacked[2],
                "replay_speed": unpacked[4],
                "flags": unpacked[5],
                "ingame_cam": unpacked[6],
                "view_plid": unpacked[7],
                "num_players": unpacked[8],
                "num_connections": unpacked[9],
                "num_finished": unpacked[10],
                "race_in_progress": unpacked[11],
                "qual_mins": unpacked[12],
                "race_laps": unpacked[13],
                "track": unpacked[16].decode("utf-8").strip("\x00"),
                "weather": unpacked[17],
                "wind": unpacked[18],
            }

        except struct.error as e:
            logger.error(f"Error parsing IS_STA: {e}")
            return None

    def parse_mci_packet(self, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse an IS_MCI (Multi Car Info) packet - vehicle telemetry.

        Args:
            data: Packet data

        Returns:
            Dict with vehicle information or None on error

        Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_MCI
        """
        try:
            # struct IS_MCI {
            #     byte Size;      # 4 + NumC * 28
            #     byte Type;      # ISP_MCI
            #     byte ReqI;      # Request ID
            #     byte NumC;      # Number of cars (max 8)
            #     CompCar Info[NumC]; # Info for each car
            # }

            if len(data) < 4:
                return None

            size, pkt_type, req_id, num_cars = struct.unpack("=4B", data[:4])

            cars = []
            offset = 4

            for i in range(num_cars):
                if offset + 28 > len(data):
                    break

                # struct CompCar (28 bytes) - compact car information
                car_data = struct.unpack("=2H4i2H4B", data[offset : offset + 28])

                cars.append(
                    {
                        "node": car_data[0],
                        "lap": car_data[1],
                        "plid": car_data[2],
                        "position": {
                            "x": car_data[3],
                            "y": car_data[4],
                            "z": car_data[5],
                        },
                        "speed": car_data[6],
                        "direction": car_data[7],
                        "heading": car_data[8],
                        "angular_vel": car_data[9],
                    }
                )

                offset += 28

            return {
                "req_id": req_id,
                "num_cars": num_cars,
                "cars": cars,
            }

        except struct.error as e:
            logger.error(f"Error parsing IS_MCI: {e}")
            return None

    def get_packet_stats(self) -> Dict[int, int]:
        """
        Get statistics of processed packets.

        Returns:
            Dict with number of packets by type
        """
        return self.packet_count.copy()

    def reset_stats(self) -> None:
        """Reset packet statistics."""
        self.packet_count.clear()
        logger.info("Packet statistics reset")
