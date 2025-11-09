"""
InSim Client
Client per connectar-se al servidor LFS mitjançant el protocol InSim.

Referència: https://en.lfsmanual.net/wiki/InSim.txt
"""

import socket
import struct
import logging
from typing import Optional, Callable, Dict, Any
from enum import IntEnum

logger = logging.getLogger(__name__)


class InSimVersion(IntEnum):
    """Versions del protocol InSim"""
    INSIM_VERSION = 9  # Versió actual del protocol


class PacketType(IntEnum):
    """
    Tipus de paquets InSim
    Referència: https://en.lfsmanual.net/wiki/InSim.txt
    """
    ISP_NONE = 0        # Instruction packet
    ISP_ISI = 1         # InSim Init - Inicialitzar connexió
    ISP_VER = 2         # Version - Informació de versió
    ISP_TINY = 3        # Tiny - Paquets de control petit
    ISP_SMALL = 4       # Small - Paquets de dades petit
    ISP_STA = 5         # State - Estat del servidor
    ISP_SCH = 6         # Single Character - Un caràcter
    ISP_SFP = 7         # State Flags Pack
    ISP_SCC = 8         # Set Car Camera
    ISP_CPP = 9         # Camera Position Pack
    ISP_ISM = 10        # InSim Multi
    ISP_MSO = 11        # Message Out - Missatges del servidor
    ISP_III = 12        # InSim Info
    ISP_MST = 13        # MSg Type - Tipus de missatge
    ISP_MTC = 14        # Msg To Connection
    ISP_MOD = 15        # MODification
    ISP_VTN = 16        # VoTe Notification
    ISP_RST = 17        # Race STart
    ISP_NCN = 18        # New Connection
    ISP_CNL = 19        # Connection Leave
    ISP_CPR = 20        # Connection Player Rename
    ISP_NPL = 21        # New Player
    ISP_PLP = 22        # Player Leave Pits
    ISP_PLL = 23        # Player Leave
    ISP_LAP = 24        # LAP time
    ISP_SPX = 25        # SPlit X
    ISP_PIT = 26        # PIT stop
    ISP_PSF = 27        # Pit Stop Finish
    ISP_PLA = 28        # Pit LAne
    ISP_CCH = 29        # Camera CHange
    ISP_PEN = 30        # PENalty
    ISP_TOC = 31        # Take Over Car
    ISP_FLG = 32        # FLaG
    ISP_PFL = 33        # Player FLags
    ISP_FIN = 34        # FINished race
    ISP_RES = 35        # RESult
    ISP_REO = 36        # REOrder
    ISP_NLP = 37        # Node and Lap Packet
    ISP_MCI = 38        # Multi Car Info
    ISP_MSX = 39        # MSg eXtended
    ISP_MSL = 40        # MSg Local
    ISP_CRS = 41        # Car ReSet
    ISP_BFN = 42        # Button FunctioN
    ISP_AXI = 43        # Autocross Info
    ISP_AXO = 44        # Autocross Object
    ISP_BTN = 45        # BuTtoN
    ISP_BTC = 46        # Button Clear
    ISP_BTT = 47        # Button Type
    ISP_RIP = 48        # Replay Info Packet
    ISP_SSH = 49        # ScreenSHot
    ISP_CON = 50        # CONtact
    ISP_OBH = 51        # OBject Hit
    ISP_HLV = 52        # Hot Lap Validity
    ISP_PLC = 53        # Player Cars
    ISP_AXM = 54        # Autocross Multiple objects
    ISP_ACR = 55        # Admin Command Report


class InSimClient:
    """
    Client per connectar-se i comunicar-se amb el servidor LFS mitjançant InSim.
    
    Attributes:
        host (str): Adreça IP del servidor LFS
        port (int): Port InSim del servidor (per defecte 29999)
        admin_password (str): Contrasenya d'administrador
        app_name (str): Nom de l'aplicació (màx 16 caràcters)
    
    Exemple:
        >>> client = InSimClient('127.0.0.1', 29999, '', 'LFS-Ayats')
        >>> client.connect()
        >>> client.initialize()
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 29999,
        admin_password: str = "",
        app_name: str = "LFS-Ayats",
        udp: bool = False,
    ):
        """
        Inicialitza el client InSim.

        Args:
            host: Adreça IP del servidor LFS
            port: Port InSim (per defecte 29999)
            admin_password: Contrasenya d'administrador (si cal)
            app_name: Nom de l'aplicació (màx 16 caràcters)
            udp: Utilitzar UDP en lloc de TCP
        """
        self.host = host
        self.port = port
        self.admin_password = admin_password
        self.app_name = app_name[:16]  # Limitar a 16 caràcters
        self.udp = udp
        
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.callbacks: Dict[int, Callable] = {}
        
        logger.info(f"InSim client creat per {host}:{port} ({'UDP' if udp else 'TCP'})")

    def connect(self) -> bool:
        """
        Estableix la connexió amb el servidor LFS.

        Returns:
            bool: True si la connexió és exitosa, False altrament

        Raises:
            ConnectionError: Si no es pot connectar al servidor
        """
        try:
            if self.udp:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.connect((self.host, self.port))
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.socket.settimeout(5.0)
            
            self.connected = True
            logger.info(f"Connectat a {self.host}:{self.port}")
            return True
            
        except socket.error as e:
            logger.error(f"Error de connexió: {e}")
            raise ConnectionError(f"No es pot connectar a {self.host}:{self.port}") from e

    def initialize(self, flags: int = 0, interval: int = 0) -> None:
        """
        Inicialitza la connexió InSim enviant el paquet IS_ISI.
        
        Args:
            flags: Flags d'InSim (veure InSim.txt)
            interval: Interval per paquets MCI/NLP (centèssimes de segon)
        
        Referència: https://en.lfsmanual.net/wiki/InSim.txt#IS_ISI
        """
        if not self.connected:
            raise ConnectionError("No connectat al servidor")

        # Construir paquet IS_ISI
        # struct IS_ISI {
        #     byte Size;      // 44
        #     byte Type;      // ISP_ISI
        #     byte ReqI;      // Request ID
        #     byte Zero;      // 0
        #     word UDPPort;   // Port UDP (0 per TCP)
        #     word Flags;     // Flags
        #     byte InSimVer;  // Versió InSim
        #     byte Prefix;    // Prefix per comandaments (0 = none)
        #     word Interval;  // Interval MCI/NLP
        #     char Admin[16]; // Admin password
        #     char IName[16]; // Application name
        # }
        
        packet = struct.pack(
            "=4BH2BH16s16s",
            44,  # Size
            PacketType.ISP_ISI,  # Type
            0,   # ReqI
            0,   # Zero
            0 if not self.udp else self.port,  # UDPPort
            flags,  # Flags
            InSimVersion.INSIM_VERSION,  # InSimVer
            ord('!'),  # Prefix (!)
            interval,  # Interval
            self.admin_password.encode('utf-8').ljust(16, b'\x00'),
            self.app_name.encode('utf-8').ljust(16, b'\x00'),
        )
        
        self.send_packet(packet)
        logger.info("Paquet IS_ISI enviat")

    def send_packet(self, packet: bytes) -> None:
        """
        Envia un paquet al servidor LFS.

        Args:
            packet: Paquet en format bytes

        Raises:
            ConnectionError: Si no hi ha connexió activa
        """
        if not self.connected or not self.socket:
            raise ConnectionError("No connectat al servidor")
        
        try:
            self.socket.sendall(packet)
            logger.debug(f"Paquet enviat: {len(packet)} bytes")
        except socket.error as e:
            logger.error(f"Error enviant paquet: {e}")
            raise

    def receive_packet(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Rep un paquet del servidor LFS.

        Args:
            timeout: Temps d'espera màxim en segons (None = bloqueig)

        Returns:
            bytes: Paquet rebut o None si no hi ha dades

        Raises:
            ConnectionError: Si no hi ha connexió activa
        """
        if not self.connected or not self.socket:
            raise ConnectionError("No connectat al servidor")

        try:
            if timeout is not None:
                self.socket.settimeout(timeout)
            
            # Primer, llegir l'encapçalament (4 bytes)
            header = self.socket.recv(4)
            if not header or len(header) < 1:
                return None
            
            # El primer byte és la mida del paquet
            packet_size = header[0]
            
            # Llegir la resta del paquet
            remaining = packet_size - 4
            if remaining > 0:
                data = self.socket.recv(remaining)
                packet = header + data
            else:
                packet = header
            
            logger.debug(f"Paquet rebut: {len(packet)} bytes, tipus: {header[1] if len(header) > 1 else 'unknown'}")
            return packet
            
        except socket.timeout:
            return None
        except socket.error as e:
            logger.error(f"Error rebent paquet: {e}")
            raise

    def register_callback(self, packet_type: int, callback: Callable) -> None:
        """
        Registra un callback per un tipus de paquet específic.

        Args:
            packet_type: Tipus de paquet (PacketType)
            callback: Funció a cridar quan es rep el paquet
        """
        self.callbacks[packet_type] = callback
        logger.debug(f"Callback registrat per paquet tipus {packet_type}")

    def disconnect(self) -> None:
        """Tanca la connexió amb el servidor LFS."""
        if self.socket:
            try:
                self.socket.close()
                logger.info("Desconnectat del servidor")
            except socket.error as e:
                logger.error(f"Error tancant connexió: {e}")
            finally:
                self.socket = None
                self.connected = False

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def __del__(self):
        """Assegura que la connexió es tanca."""
        if self.connected:
            self.disconnect()
