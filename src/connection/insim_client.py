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

from .heartbeat import HeartbeatManager

logger = logging.getLogger(__name__)

# Maximum packet size in bytes (InSim packets are typically small)
# This prevents buffer overflow from malformed packets
MAX_PACKET_SIZE = 4096


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
        socket_timeout: float = 5.0,
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
            socket_timeout: TCP socket timeout in seconds (default 5.0)
        """
        self.host = host
        self.port = port
        self.admin_password = admin_password
        self.app_name = app_name[:16]  # Limit to 16 characters
        self.udp = udp
        self.socket_timeout = socket_timeout

        # Reconnection settings
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.reconnect_enabled = reconnect_enabled

        # Heartbeat manager
        self.heartbeat = HeartbeatManager(self, heartbeat_interval)

        # Connection state
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.state = ConnectionState.DISCONNECTED
        self.state_callbacks: Dict[ConnectionState, list] = defaultdict(list)

        # Thread safety for send operations
        self._send_lock = threading.Lock()

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

    def _create_socket(self) -> socket.socket:
        """
        Create and configure socket based on protocol type.

        Handles both TCP and UDP socket creation with appropriate
        configuration for each protocol.

        Returns:
            Configured socket instance
        """
        if self.udp:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            logger.debug("UDP socket created")
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.socket_timeout)
            logger.debug(f"TCP socket created (timeout={self.socket_timeout}s)")

        return sock

    def connect(self) -> bool:
        """
        Establish connection with the LFS server.

        Returns:
            bool: True if connection is successful

        Raises:
            ConnectionError: If unable to connect to the server
        """
        try:
            self._change_state(ConnectionState.CONNECTING)
            self.socket = self._create_socket()
            self.socket.connect((self.host, self.port))
            self.connected = True
            self._change_state(ConnectionState.CONNECTED)
            logger.info(f"Connected to {self.host}:{self.port}")
            return True

        except socket.error as e:
            self._change_state(ConnectionState.ERROR)
            logger.error(f"Connection error: {e}")
            raise ConnectionError(f"Cannot connect to {self.host}:{self.port}") from e

    def connect_with_retry(self) -> bool:
        """
        Attempt to connect with exponential backoff retries.

        Implements exponential backoff to avoid server overload.

        Returns:
            bool: True if connection is successful, False after max_retries
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                self.connect()
                logger.info("Connection established successfully")
                return True

            except ConnectionError:
                if attempt == self.max_retries:
                    logger.error(
                        f"Maximum connection attempts reached ({self.max_retries})"
                    )
                    return False

                # Exponential backoff: delay * (2 ^ (attempt - 1))
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.warning(
                    f"Attempt {attempt}/{self.max_retries} failed. "
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
            if self.heartbeat.thread and not self.heartbeat._stop.is_set():
                self.start_heartbeat(self.heartbeat.interval)
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
            "=4BHHBBH16s16s",
            44,  # Size
            PacketType.ISP_ISI,  # Type
            0,  # ReqI
            0,  # Zero
            0 if not self.udp else self.port,  # UDPPort (word/H)
            flags,  # Flags (word/H)
            InSimVersion.INSIM_VERSION,  # InSimVer (byte/B)
            ord("!"),  # Prefix (byte/B)
            interval,  # Interval (word/H)
            self.admin_password.encode("utf-8").ljust(16, b"\x00"),
            self.app_name.encode("utf-8").ljust(16, b"\x00"),
        )

        success = self.send_packet(packet, retry=True)
        if success:
            logger.info("IS_ISI packet sent")
        else:
            logger.error("Failed to send IS_ISI initialization packet")
            raise ConnectionError("Failed to initialize InSim connection")

    def send_packet(self, packet: bytes, retry: bool = False) -> bool:
        """
        Send a packet to the LFS server with atomic connection check.

        Uses a lock to prevent race conditions between connection check
        and actual send operation. Distinguishes between timeout and
        connection errors for better error handling.

        Args:
            packet: Packet in bytes format
            retry: If True, trigger reconnection on errors

        Returns:
            bool: True if packet was sent successfully, False otherwise

        Raises:
            ConnectionError: If no active connection
        """
        with self._send_lock:
            if not self.connected or not self.socket:
                raise ConnectionError("Not connected to server")

            try:
                self.socket.sendall(packet)
                logger.debug(f"Packet sent: {len(packet)} bytes")
                return True
            except socket.timeout:
                logger.warning("Send timeout - connection may be slow or unresponsive")
                if retry and self.reconnect_enabled:
                    self.trigger_reconnect()
                return False
            except socket.error as e:
                logger.error(f"Error sending packet: {e}")
                if retry and self.reconnect_enabled:
                    self.trigger_reconnect()
                return False

    def send_tiny(self, subtype: int, retry: bool = False) -> bool:
        """
        Send a TINY packet (small control) with atomic connection check.

        TINY packets are used for keepalive and basic control.
        Uses a lock to prevent race conditions.

        Args:
            subtype: TINY packet subtype (TinySubtype)
            retry: If True, trigger reconnection on errors

        Returns:
            bool: True if packet was sent successfully, False otherwise

        Raises:
            ConnectionError: If no active connection

        Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_TINY
        """
        # struct IS_TINY {
        #     byte Size;   # 4
        #     byte Type;   # ISP_TINY
        #     byte ReqI;   # 0
        #     byte SubT;   # Subtype
        # }
        packet = struct.pack("=4B", 4, PacketType.ISP_TINY, 0, subtype)

        with self._send_lock:
            if not self.connected or not self.socket:
                raise ConnectionError("Not connected to server")

            try:
                self.socket.sendall(packet)
                logger.debug(f"TINY packet sent: subtype={subtype}")
                return True
            except socket.timeout:
                logger.warning(
                    f"TINY packet send timeout (subtype={subtype}) - "
                    "connection may be slow or unresponsive"
                )
                if retry and self.reconnect_enabled:
                    self.trigger_reconnect()
                return False
            except socket.error as e:
                logger.error(f"Error sending TINY packet: {e}")
                if retry and self.reconnect_enabled:
                    self.trigger_reconnect()
                return False

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

    def _recv_exact(self, size: int) -> bytes:
        """
        Read exact number of bytes from socket.

        TCP recv() may return fewer bytes than requested, so we need to loop
        until we have all the data or connection is closed.

        Args:
            size: Exact number of bytes to receive

        Returns:
            bytes: Exactly 'size' bytes of data

        Raises:
            ConnectionError: If connection closed before receiving all data
            socket.error: If socket error occurs
        """
        data = b""
        while len(data) < size:
            chunk = self.socket.recv(size - len(data))
            if not chunk:
                # Connection closed
                raise ConnectionError("Connection closed while reading packet")
            data += chunk
        return data

    def receive_packet(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Receive a packet from the LFS server with validation.

        Handles incomplete reads, validates packet size, and restores
        socket timeout after reading.

        Args:
            timeout: Maximum wait time in seconds (None = blocking)

        Returns:
            bytes: Received packet or None if no data or timeout

        Raises:
            ConnectionError: If no active connection or connection closed
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to server")

        # Store original timeout to restore later
        original_timeout = self.socket.gettimeout()

        try:
            if timeout is not None:
                self.socket.settimeout(timeout)

            # First, read the header (4 bytes) - use exact read
            header = self._recv_exact(4)

            # First byte is packet size (in multiples of 4)
            packet_size = header[0] * 4 if header[0] > 0 else 4

            # Validate packet size to prevent buffer overflow
            if packet_size > MAX_PACKET_SIZE:
                logger.error(
                    f"Packet size {packet_size} exceeds maximum {MAX_PACKET_SIZE}, "
                    "discarding packet"
                )
                return None

            # Read the rest of the packet if needed
            remaining = packet_size - 4
            if remaining > 0:
                data = self._recv_exact(remaining)
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
        except ConnectionError as e:
            logger.error(f"Connection error receiving packet: {e}")
            if self.reconnect_enabled:
                self.trigger_reconnect()
            raise
        except socket.error as e:
            logger.error(f"Socket error receiving packet: {e}")
            if self.reconnect_enabled:
                self.trigger_reconnect()
            raise
        finally:
            # Restore original timeout
            if timeout is not None and self.socket:
                try:
                    self.socket.settimeout(original_timeout)
                except (OSError, AttributeError):
                    # Socket may be closed or invalid, ignore
                    pass

    def start_heartbeat(self, interval: Optional[float] = None) -> None:
        """
        Start the heartbeat system.

        Sends TINY_NONE packets periodically to keep the connection alive
        and detect dead connections.

        Args:
            interval: Interval between heartbeats (seconds).
                     If None, uses current interval
        """
        if interval is not None:
            self.heartbeat.interval = interval
        self.heartbeat.start()

    def stop_heartbeat(self) -> None:
        """Stop the heartbeat system."""
        self.heartbeat.stop()

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
