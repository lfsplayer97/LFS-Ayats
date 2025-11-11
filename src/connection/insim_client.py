"""
InSim Client
Client to connect to the LFS server using the InSim protocol.

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import socket
import struct
import logging
import time
import threading
from typing import Optional, Callable, Dict
from enum import IntEnum, Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class InSimVersion(IntEnum):
    """InSim protocol versions"""

    INSIM_VERSION = 9  # Current protocol version


class ConnectionState(Enum):
    """Connection states for InSim client"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class TinySubtype(IntEnum):
    """TINY packet subtypes for keepalive and control"""

    TINY_NONE = 0  # No subtype (keepalive)
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


class PacketType(IntEnum):
    """
    InSim packet types
    Reference: https://en.lfsmanual.net/wiki/InSim.txt
    """

    ISP_NONE = 0  # Instruction packet
    ISP_ISI = 1  # InSim Init - Initialize connection
    ISP_VER = 2  # Version - Version information
    ISP_TINY = 3  # Tiny - Small control packets
    ISP_SMALL = 4  # Small - Small data packets
    ISP_STA = 5  # State - Server state
    ISP_SCH = 6  # Single Character - One character
    ISP_SFP = 7  # State Flags Pack
    ISP_SCC = 8  # Set Car Camera
    ISP_CPP = 9  # Camera Position Pack
    ISP_ISM = 10  # InSim Multi
    ISP_MSO = 11  # Message Out - Server messages
    ISP_III = 12  # InSim Info
    ISP_MST = 13  # MSg Type - Message type
    ISP_MTC = 14  # Msg To Connection
    ISP_MOD = 15  # MODification
    ISP_VTN = 16  # VoTe Notification
    ISP_RST = 17  # Race STart
    ISP_NCN = 18  # New Connection
    ISP_CNL = 19  # Connection Leave
    ISP_CPR = 20  # Connection Player Rename
    ISP_NPL = 21  # New Player
    ISP_PLP = 22  # Player Leave Pits
    ISP_PLL = 23  # Player Leave
    ISP_LAP = 24  # LAP time
    ISP_SPX = 25  # SPlit X
    ISP_PIT = 26  # PIT stop
    ISP_PSF = 27  # Pit Stop Finish
    ISP_PLA = 28  # Pit LAne
    ISP_CCH = 29  # Camera CHange
    ISP_PEN = 30  # PENalty
    ISP_TOC = 31  # Take Over Car
    ISP_FLG = 32  # FLaG
    ISP_PFL = 33  # Player FLags
    ISP_FIN = 34  # FINished race
    ISP_RES = 35  # RESult
    ISP_REO = 36  # REOrder
    ISP_NLP = 37  # Node and Lap Packet
    ISP_MCI = 38  # Multi Car Info
    ISP_MSX = 39  # MSg eXtended
    ISP_MSL = 40  # MSg Local
    ISP_CRS = 41  # Car ReSet
    ISP_BFN = 42  # Button FunctioN
    ISP_AXI = 43  # Autocross Info
    ISP_AXO = 44  # Autocross Object
    ISP_BTN = 45  # BuTtoN
    ISP_BTC = 46  # Button Clear
    ISP_BTT = 47  # Button Type
    ISP_RIP = 48  # Replay Info Packet
    ISP_SSH = 49  # ScreenSHot
    ISP_CON = 50  # CONtact
    ISP_OBH = 51  # OBject Hit
    ISP_HLV = 52  # Hot Lap Validity
    ISP_PLC = 53  # Player Cars
    ISP_AXM = 54  # Autocross Multiple objects
    ISP_ACR = 55  # Admin Command Report


class InSimClient:
    """
    Client to connect and communicate with the LFS server via InSim.

    Includes automatic reconnection system, circuit breaker, heartbeat,
    and packet validation to ensure reliability.

    Attributes:
        host (str): IP address of the LFS server
        port (int): InSim port of the server (default 29999)
        admin_password (str): Administrator password
        app_name (str): Application name (max 16 characters)
        max_retries (int): Maximum number of reconnection attempts
        retry_delay (float): Initial delay between attempts (seconds)
        reconnect_enabled (bool): Enable automatic reconnection
        heartbeat_interval (float): Interval between heartbeats (seconds)

    Example:
        >>> client = InSimClient('127.0.0.1', 29999, '', 'LFS-Ayats')
        >>> client.connect_with_retry()
        >>> client.initialize()
        >>> client.start_heartbeat()
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 29999,
        admin_password: str = "",
        app_name: str = "LFS-Ayats",
        udp: bool = False,
        max_retries: int = 5,
        retry_delay: float = 2.0,
        reconnect_enabled: bool = True,
        heartbeat_interval: float = 30.0,
    ):
        """
        Initialize the InSim client.

        Args:
            host: IP address of the LFS server
            port: InSim port (default 29999)
            admin_password: Administrator password (if required)
            app_name: Application name (max 16 characters)
            udp: Use UDP instead of TCP
            max_retries: Maximum number of reconnection attempts
            retry_delay: Initial delay between attempts (exponential backoff)
            reconnect_enabled: Enable automatic reconnection
            heartbeat_interval: Interval between heartbeats (seconds)
        """
        self.host = host
        self.port = port
        self.admin_password = admin_password
        self.app_name = app_name[:16]  # Limit to 16 characters
        self.udp = udp

        # Reconnection settings
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_count = 0
        self.reconnect_enabled = reconnect_enabled

        # Heartbeat settings
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_thread: Optional[threading.Thread] = None
        self._stop_heartbeat = threading.Event()

        # Connection state
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.state = ConnectionState.DISCONNECTED
        self.state_callbacks: Dict[ConnectionState, list] = defaultdict(list)

        # Packet handling
        self.callbacks: Dict[int, Callable] = {}

        logger.info(
            f"InSim client created for {host}:{port} ({'UDP' if udp else 'TCP'}), "
            f"max_retries={max_retries}, heartbeat={heartbeat_interval}s"
        )

    def on_state_change(self, state: ConnectionState, callback: Callable) -> None:
        """
        Register a callback for connection state changes.

        Args:
            state: State that triggers the callback
            callback: Function to call (receives old_state, new_state)
        """
        self.state_callbacks[state].append(callback)
        logger.debug(f"Callback registered for state {state.value}")

    def _change_state(self, new_state: ConnectionState) -> None:
        """
        Change connection state and notify callbacks.

        Args:
            new_state: New connection state
        """
        old_state = self.state
        self.state = new_state
        logger.info(f"Connection state: {old_state.value} -> {new_state.value}")

        # Notify callbacks
        for callback in self.state_callbacks[new_state]:
            try:
                callback(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state callback: {e}")

    def connect(self) -> bool:
        """
        Establish connection with the LFS server.

        Returns:
            bool: True if connection is successful, False otherwise

        Raises:
            ConnectionError: If unable to connect to the server
        """
        try:
            self._change_state(ConnectionState.CONNECTING)

            if self.udp:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.connect((self.host, self.port))
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.socket.settimeout(5.0)

            self.connected = True
            self._change_state(ConnectionState.CONNECTED)
            logger.info(f"Connected to {self.host}:{self.port}")
            return True

        except socket.error as e:
            self._change_state(ConnectionState.ERROR)
            logger.error(f"Connection error: {e}")
            raise ConnectionError(
                f"Cannot connect to {self.host}:{self.port}"
            ) from e

    def connect_with_retry(self) -> bool:
        """
        Attempt to connect with exponential retries.

        Implements exponential backoff to avoid server overload.

        Returns:
            bool: True if connection is successful, False after max_retries
        """
        self.retry_count = 0

        while self.retry_count < self.max_retries:
            try:
                self.connect()
                self.retry_count = 0  # Reset on success
                logger.info("Connection established successfully")
                return True
            except ConnectionError:  # noqa: F841
                self.retry_count += 1

                if self.retry_count >= self.max_retries:
                    logger.error(
                        f"Maximum connection attempts reached ({self.max_retries})"
                    )
                    return False

                # Exponential backoff: delay * (2 ^ retry_count)
                delay = self.retry_delay * (2 ** (self.retry_count - 1))
                logger.warning(
                    f"Attempt {self.retry_count}/{self.max_retries} failed. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)

        return False

    def trigger_reconnect(self) -> None:
        """
        Trigger automatic reconnection.

        Executes reconnection in a separate thread to avoid blocking.
        """
        if not self.reconnect_enabled:
            logger.info("Reconnection disabled")
            return

        self._change_state(ConnectionState.RECONNECTING)
        logger.info("Triggering automatic reconnection...")

        # Disconnect first
        self.disconnect()

        # Try to reconnect
        if self.connect_with_retry():
            logger.info("Reconnection successful")
            # Restart heartbeat if it was active
            if self.heartbeat_thread and not self._stop_heartbeat.is_set():
                self.start_heartbeat(self.heartbeat_interval)
        else:
            logger.error("Reconnection failed after all attempts")
            self._change_state(ConnectionState.ERROR)

    def initialize(self, flags: int = 0, interval: int = 0) -> None:
        """
        Initialize InSim connection by sending IS_ISI packet.

        Args:
            flags: InSim flags (see InSim.txt)
            interval: Interval for MCI/NLP packets (hundredths of a second)

        Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_ISI
        """
        if not self.connected:
            raise ConnectionError("Not connected to server")

        # Build IS_ISI packet
        # struct IS_ISI {
        #     byte Size;      # 44
        #     byte Type;      # ISP_ISI
        #     byte ReqI;      # Request ID
        #     byte Zero;      # 0
        #     word UDPPort;   # UDP port (0 for TCP)
        #     word Flags;     # Flags
        #     byte InSimVer;  # InSim version
        #     byte Prefix;    # Prefix for commands (0 = none)
        #     word Interval;  # MCI/NLP interval
        #     char Admin[16]; # Admin password
        #     char IName[16]; # Application name
        # }

        packet = struct.pack(
            "=4BH2BH16s16s",
            44,  # Size
            PacketType.ISP_ISI,  # Type
            0,  # ReqI
            0,  # Zero
            0 if not self.udp else self.port,  # UDPPort
            flags,  # Flags
            InSimVersion.INSIM_VERSION,  # InSimVer
            ord("!"),  # Prefix (!)
            interval,  # Interval
            self.admin_password.encode("utf-8").ljust(16, b"\x00"),
            self.app_name.encode("utf-8").ljust(16, b"\x00"),
        )

        self.send_packet(packet)
        logger.info("IS_ISI packet sent")

    def send_packet(self, packet: bytes) -> None:
        """
        Send a packet to the LFS server.

        Args:
            packet: Packet in bytes format

        Raises:
            ConnectionError: If no active connection
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to server")

        try:
            self.socket.sendall(packet)
            logger.debug(f"Packet sent: {len(packet)} bytes")
        except socket.error as e:
            logger.error(f"Error sending packet: {e}")
            if self.reconnect_enabled:
                self.trigger_reconnect()
            raise

    def send_tiny(self, subtype: int) -> None:
        """
        Send a TINY packet (small control).

        TINY packets are used for keepalive and basic control.

        Args:
            subtype: TINY packet subtype (TinySubtype)

        Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_TINY
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to server")

        # struct IS_TINY {
        #     byte Size;   # 4
        #     byte Type;   # ISP_TINY
        #     byte ReqI;   # 0
        #     byte SubT;   # Subtype
        # }
        packet = struct.pack("=4B", 4, PacketType.ISP_TINY, 0, subtype)

        try:
            self.socket.sendall(packet)
            logger.debug(f"TINY packet sent: subtype={subtype}")
        except socket.error as e:
            logger.error(f"Error sending TINY packet: {e}")
            if self.reconnect_enabled:
                self.trigger_reconnect()
            raise

    def validate_packet(self, packet: bytes) -> bool:
        """
        Validate integrity of an InSim packet.

        Checks:
        - Minimum length (4 bytes)
        - Consistency between declared and actual size
        - Valid packet type

        Args:
            packet: Packet to validate

        Returns:
            bool: True if packet is valid
        """
        if not packet or len(packet) < 4:
            logger.error("Packet too short (< 4 bytes)")
            return False

        # First byte is size in multiples of 4
        # For example: size=1 means 4 bytes, size=2 means 8 bytes
        declared_size_multiplier = packet[0]
        declared_size = (
            declared_size_multiplier * 4 if declared_size_multiplier > 0 else 4
        )
        actual_size = len(packet)

        if declared_size != actual_size:
            logger.error(
                f"Size inconsistency: declared={declared_size} "
                f"(multiplier={declared_size_multiplier}), actual={actual_size}"
            )
            return False

        packet_type = packet[1]
        try:
            # Check if type is valid
            PacketType(packet_type)
        except ValueError:
            logger.warning(f"Unknown packet type: {packet_type}")
            # Don't return False here as there may be new types

        return True

    def receive_packet(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Receive a packet from the LFS server with validation.

        Args:
            timeout: Maximum wait time in seconds (None = blocking)

        Returns:
            bytes: Received packet or None if no data

        Raises:
            ConnectionError: If no active connection
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to server")

        try:
            if timeout is not None:
                self.socket.settimeout(timeout)

            # First, read the header (4 bytes)
            header = self.socket.recv(4)
            if not header or len(header) < 1:
                return None

            # First byte is packet size (in multiples of 4)
            packet_size = header[0] * 4 if header[0] > 0 else 4

            # Read the rest of the packet
            remaining = packet_size - 4
            if remaining > 0:
                data = self.socket.recv(remaining)
                packet = header + data
            else:
                packet = header

            # Validate packet
            if not self.validate_packet(packet):
                logger.warning("Invalid packet received and discarded")
                return None

            logger.debug(
                f"Packet received: {len(packet)} bytes, "
                f"type: {header[1] if len(header) > 1 else 'unknown'}"
            )
            return packet

        except socket.timeout:
            return None
        except socket.error as e:
            logger.error(f"Error receiving packet: {e}")
            if self.reconnect_enabled:
                self.trigger_reconnect()
            raise

    def start_heartbeat(self, interval: Optional[float] = None) -> None:
        """
        Start the heartbeat system.

        Sends TINY_NONE packets periodically to keep the connection alive
        and detect dead connections.

        Args:
            interval: Interval between heartbeats (seconds).
                     If None, uses self.heartbeat_interval
        """
        if interval is not None:
            self.heartbeat_interval = interval

        # Stop previous heartbeat if exists
        self.stop_heartbeat()

        self._stop_heartbeat.clear()

        def heartbeat_loop():
            logger.info(f"Heartbeat started (interval={self.heartbeat_interval}s)")

            while not self._stop_heartbeat.is_set() and self.connected:
                try:
                    self.send_tiny(TinySubtype.TINY_NONE)
                    logger.debug("Heartbeat sent")
                except Exception as e:
                    logger.error(f"Heartbeat failed: {e}")
                    if self.reconnect_enabled:
                        self.trigger_reconnect()
                    break

                # Wait for interval or until stopped
                self._stop_heartbeat.wait(timeout=self.heartbeat_interval)

            logger.info("Heartbeat stopped")

        self.heartbeat_thread = threading.Thread(
            target=heartbeat_loop, daemon=True, name="InSimHeartbeat"
        )
        self.heartbeat_thread.start()

    def stop_heartbeat(self) -> None:
        """Stop the heartbeat system."""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            logger.info("Stopping heartbeat...")
            self._stop_heartbeat.set()
            self.heartbeat_thread.join(timeout=2.0)
            self.heartbeat_thread = None

    def register_callback(self, packet_type: int, callback: Callable) -> None:
        """
        Register a callback for a specific packet type.

        Args:
            packet_type: Packet type (PacketType)
            callback: Function to call when packet is received
        """
        self.callbacks[packet_type] = callback
        logger.debug(f"Callback registered for packet type {packet_type}")

    def disconnect(self) -> None:
        """Close connection with the LFS server."""
        # Stop heartbeat first
        self.stop_heartbeat()

        if self.socket:
            try:
                self.socket.close()
                logger.info("Disconnected from server")
            except socket.error as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self.socket = None
                self.connected = False
                self._change_state(ConnectionState.DISCONNECTED)

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def __del__(self):
        """Ensure connection is closed."""
        if self.connected:
            self.disconnect()
