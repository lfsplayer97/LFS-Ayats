"""
InSim Client
Client per connectar-se al servidor LFS mitjançant el protocol InSim.

Referència: https://en.lfsmanual.net/wiki/InSim.txt
"""

import socket
import struct
import logging
import time
import threading
from typing import Optional, Callable, Dict, Any
from enum import IntEnum, Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class InSimVersion(IntEnum):
    """Versions del protocol InSim"""
    INSIM_VERSION = 9  # Versió actual del protocol


class ConnectionState(Enum):
    """Connection states for InSim client"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class TinySubtype(IntEnum):
    """Subtipus de paquets TINY per keepalive i control"""
    TINY_NONE = 0       # No subtype (keepalive)
    TINY_VER = 1        # Request version
    TINY_CLOSE = 2      # Close InSim
    TINY_PING = 3       # Ping
    TINY_REPLY = 4      # Ping reply
    TINY_VTC = 5        # Vote cancel
    TINY_SCP = 6        # Send camera pos
    TINY_SST = 7        # Send state
    TINY_GTH = 8        # Get time in hundredths
    TINY_MPE = 9        # Multi player end
    TINY_ISM = 10       # InSim multi
    TINY_REN = 11       # Rename
    TINY_NCN = 12       # New connection
    TINY_NPL = 13       # New player
    TINY_RES = 14       # Result
    TINY_NLP = 15       # Node and lap
    TINY_MCI = 16       # Multi car info
    TINY_REO = 17       # Reorder
    TINY_RST = 18       # Race start
    TINY_AXI = 19       # Autocross info
    TINY_AXC = 20       # Autocross clear
    TINY_RIP = 21       # Replay info


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
    
    Inclou sistema de reconnexió automàtica, circuit breaker, heartbeat,
    i validació de paquets per garantir fiabilitat.
    
    Attributes:
        host (str): Adreça IP del servidor LFS
        port (int): Port InSim del servidor (per defecte 29999)
        admin_password (str): Contrasenya d'administrador
        app_name (str): Nom de l'aplicació (màx 16 caràcters)
        max_retries (int): Nombre màxim d'intents de reconnexió
        retry_delay (float): Retard inicial entre intents (segons)
        reconnect_enabled (bool): Habilitar reconnexió automàtica
        heartbeat_interval (float): Interval entre heartbeats (segons)
    
    Exemple:
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
        Inicialitza el client InSim.

        Args:
            host: Adreça IP del servidor LFS
            port: Port InSim (per defecte 29999)
            admin_password: Contrasenya d'administrador (si cal)
            app_name: Nom de l'aplicació (màx 16 caràcters)
            udp: Utilitzar UDP en lloc de TCP
            max_retries: Nombre màxim d'intents de reconnexió
            retry_delay: Retard inicial entre intents (exponencial backoff)
            reconnect_enabled: Habilitar reconnexió automàtica
            heartbeat_interval: Interval entre heartbeats (segons)
        """
        self.host = host
        self.port = port
        self.admin_password = admin_password
        self.app_name = app_name[:16]  # Limitar a 16 caràcters
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
            f"InSim client creat per {host}:{port} ({'UDP' if udp else 'TCP'}), "
            f"max_retries={max_retries}, heartbeat={heartbeat_interval}s"
        )

    def on_state_change(self, state: ConnectionState, callback: Callable) -> None:
        """
        Registra un callback per canvis d'estat de connexió.
        
        Args:
            state: Estat que dispara el callback
            callback: Funció a cridar (rep old_state, new_state)
        """
        self.state_callbacks[state].append(callback)
        logger.debug(f"Callback registrat per estat {state.value}")

    def _change_state(self, new_state: ConnectionState) -> None:
        """
        Canvia l'estat de connexió i notifica callbacks.
        
        Args:
            new_state: Nou estat de connexió
        """
        old_state = self.state
        self.state = new_state
        logger.info(f"Estat de connexió: {old_state.value} -> {new_state.value}")
        
        # Notificar callbacks
        for callback in self.state_callbacks[new_state]:
            try:
                callback(old_state, new_state)
            except Exception as e:
                logger.error(f"Error en callback d'estat: {e}")

    def connect(self) -> bool:
        """
        Estableix la connexió amb el servidor LFS.

        Returns:
            bool: True si la connexió és exitosa, False altrament

        Raises:
            ConnectionError: Si no es pot connectar al servidor
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
            logger.info(f"Connectat a {self.host}:{self.port}")
            return True
            
        except socket.error as e:
            self._change_state(ConnectionState.ERROR)
            logger.error(f"Error de connexió: {e}")
            raise ConnectionError(f"No es pot connectar a {self.host}:{self.port}") from e

    def connect_with_retry(self) -> bool:
        """
        Intenta connectar amb retries exponencials.
        
        Implementa exponential backoff per evitar sobrecàrrega del servidor.
        
        Returns:
            bool: True si la connexió és exitosa, False després de max_retries
        """
        self.retry_count = 0
        
        while self.retry_count < self.max_retries:
            try:
                self.connect()
                self.retry_count = 0  # Reset on success
                logger.info("Connexió establerta amb èxit")
                return True
            except ConnectionError as e:
                self.retry_count += 1
                
                if self.retry_count >= self.max_retries:
                    logger.error(
                        f"Màxim d'intents de connexió assolit ({self.max_retries})"
                    )
                    return False
                
                # Exponential backoff: delay * (2 ^ retry_count)
                delay = self.retry_delay * (2 ** (self.retry_count - 1))
                logger.warning(
                    f"Intent {self.retry_count}/{self.max_retries} fallit. "
                    f"Reintentant en {delay:.1f}s..."
                )
                time.sleep(delay)
        
        return False

    def trigger_reconnect(self) -> None:
        """
        Dispara una reconnexió automàtica.
        
        Executa la reconnexió en un fil separat per no bloquejar.
        """
        if not self.reconnect_enabled:
            logger.info("Reconnexió deshabilitada")
            return
        
        self._change_state(ConnectionState.RECONNECTING)
        logger.info("Disparant reconnexió automàtica...")
        
        # Disconnect first
        self.disconnect()
        
        # Try to reconnect
        if self.connect_with_retry():
            logger.info("Reconnexió exitosa")
            # Reiniciar heartbeat si estava actiu
            if self.heartbeat_thread and not self._stop_heartbeat.is_set():
                self.start_heartbeat(self.heartbeat_interval)
        else:
            logger.error("Reconnexió fallida després de tots els intents")
            self._change_state(ConnectionState.ERROR)

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
            if self.reconnect_enabled:
                self.trigger_reconnect()
            raise

    def send_tiny(self, subtype: int) -> None:
        """
        Envia un paquet TINY (control petit).
        
        Els paquets TINY s'utilitzen per keepalive i control bàsic.
        
        Args:
            subtype: Subtipus del paquet TINY (TinySubtype)
            
        Referència: https://en.lfsmanual.net/wiki/InSim.txt#IS_TINY
        """
        if not self.connected or not self.socket:
            raise ConnectionError("No connectat al servidor")
        
        # struct IS_TINY {
        #     byte Size;   // 4
        #     byte Type;   // ISP_TINY
        #     byte ReqI;   // 0
        #     byte SubT;   // Subtype
        # }
        packet = struct.pack("=4B", 4, PacketType.ISP_TINY, 0, subtype)
        
        try:
            self.socket.sendall(packet)
            logger.debug(f"Paquet TINY enviat: subtype={subtype}")
        except socket.error as e:
            logger.error(f"Error enviant paquet TINY: {e}")
            if self.reconnect_enabled:
                self.trigger_reconnect()
            raise

    def validate_packet(self, packet: bytes) -> bool:
        """
        Valida la integritat d'un paquet InSim.
        
        Comprova:
        - Longitud mínima (4 bytes)
        - Coherència entre mida declarada i real
        - Tipus de paquet vàlid
        
        Args:
            packet: Paquet a validar
            
        Returns:
            bool: True si el paquet és vàlid
        """
        if not packet or len(packet) < 4:
            logger.error("Paquet massa curt (< 4 bytes)")
            return False
        
        # El primer byte és la mida en múltiples de 4
        # Per exemple: size=1 significa 4 bytes, size=2 significa 8 bytes
        declared_size_multiplier = packet[0]
        declared_size = declared_size_multiplier * 4 if declared_size_multiplier > 0 else 4
        actual_size = len(packet)
        
        if declared_size != actual_size:
            logger.error(
                f"Incoherència de mida: declarat={declared_size} (multiplier={declared_size_multiplier}), "
                f"real={actual_size}"
            )
            return False
        
        packet_type = packet[1]
        try:
            # Comprovar si el tipus és vàlid
            PacketType(packet_type)
        except ValueError:
            logger.warning(f"Tipus de paquet desconegut: {packet_type}")
            # No retornem False aquí perquè poden haver-hi nous tipus
        
        return True

    def receive_packet(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Rep un paquet del servidor LFS amb validació.

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
            
            # El primer byte és la mida del paquet (en múltiples de 4)
            packet_size = header[0] * 4 if header[0] > 0 else 4
            
            # Llegir la resta del paquet
            remaining = packet_size - 4
            if remaining > 0:
                data = self.socket.recv(remaining)
                packet = header + data
            else:
                packet = header
            
            # Validar paquet
            if not self.validate_packet(packet):
                logger.warning("Paquet invàlid rebut i descartat")
                return None
            
            logger.debug(
                f"Paquet rebut: {len(packet)} bytes, "
                f"tipus: {header[1] if len(header) > 1 else 'unknown'}"
            )
            return packet
            
        except socket.timeout:
            return None
        except socket.error as e:
            logger.error(f"Error rebent paquet: {e}")
            if self.reconnect_enabled:
                self.trigger_reconnect()
            raise

    def start_heartbeat(self, interval: Optional[float] = None) -> None:
        """
        Inicia el sistema de heartbeat.
        
        Envia paquets TINY_NONE periòdicament per mantenir la connexió viva
        i detectar connexions mortes.
        
        Args:
            interval: Interval entre heartbeats (segons). Si None, usa self.heartbeat_interval
        """
        if interval is not None:
            self.heartbeat_interval = interval
        
        # Parar heartbeat anterior si existeix
        self.stop_heartbeat()
        
        self._stop_heartbeat.clear()
        
        def heartbeat_loop():
            logger.info(f"Heartbeat iniciat (interval={self.heartbeat_interval}s)")
            
            while not self._stop_heartbeat.is_set() and self.connected:
                try:
                    self.send_tiny(TinySubtype.TINY_NONE)
                    logger.debug("Heartbeat enviat")
                except Exception as e:
                    logger.error(f"Heartbeat fallit: {e}")
                    if self.reconnect_enabled:
                        self.trigger_reconnect()
                    break
                
                # Esperar interval o fins que s'aturi
                self._stop_heartbeat.wait(timeout=self.heartbeat_interval)
            
            logger.info("Heartbeat aturat")
        
        self.heartbeat_thread = threading.Thread(
            target=heartbeat_loop,
            daemon=True,
            name="InSimHeartbeat"
        )
        self.heartbeat_thread.start()

    def stop_heartbeat(self) -> None:
        """Atura el sistema de heartbeat."""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            logger.info("Aturant heartbeat...")
            self._stop_heartbeat.set()
            self.heartbeat_thread.join(timeout=2.0)
            self.heartbeat_thread = None

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
        # Stop heartbeat first
        self.stop_heartbeat()
        
        if self.socket:
            try:
                self.socket.close()
                logger.info("Desconnectat del servidor")
            except socket.error as e:
                logger.error(f"Error tancant connexió: {e}")
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
        """Assegura que la connexió es tanca."""
        if self.connected:
            self.disconnect()
