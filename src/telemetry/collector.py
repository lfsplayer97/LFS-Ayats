"""
Telemetry Collector
Recollida de dades telemètriques de Live for Speed mitjançant InSim.

Referència: https://en.lfsmanual.net/wiki/InSim.txt
"""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from threading import Thread, Event

logger = logging.getLogger(__name__)


@dataclass
class CarTelemetry:
    """
    Dades telemètriques d'un vehicle.
    
    Attributes:
        timestamp: Marca temporal de la mostra
        plid: Player ID
        node: Node actual a la pista
        lap: Volta actual
        position: Posició 3D (x, y, z)
        speed: Velocitat en m/s
        direction: Direcció del vehicle
        heading: Orientació
        angular_velocity: Velocitat angular
    """
    timestamp: float = field(default_factory=time.time)
    plid: int = 0
    node: int = 0
    lap: int = 0
    position: Dict[str, float] = field(default_factory=dict)
    speed: float = 0.0
    direction: int = 0
    heading: int = 0
    angular_velocity: int = 0


@dataclass
class LapTelemetry:
    """
    Dades telemètriques d'una volta.
    
    Attributes:
        timestamp: Marca temporal
        plid: Player ID
        lap: Número de volta
        lap_time: Temps de volta (ms)
        elapsed_time: Temps total (ms)
        split_times: Temps de sectors
        flags: Flags de la volta
    """
    timestamp: float = field(default_factory=time.time)
    plid: int = 0
    lap: int = 0
    lap_time: int = 0
    elapsed_time: int = 0
    split_times: List[int] = field(default_factory=list)
    flags: int = 0


@dataclass
class PlayerInfo:
    """
    Informació d'un jugador.
    
    Attributes:
        plid: Player ID
        ucid: Unique Connection ID
        player_name: Nom del jugador
        car_name: Nom del cotxe
        team_name: Nom de l'equip
        plate: Matrícula
        flags: Flags del jugador
    """
    plid: int = 0
    ucid: int = 0
    player_name: str = ""
    car_name: str = ""
    team_name: str = ""
    plate: str = ""
    flags: int = 0


class TelemetryCollector:
    """
    Recull dades telemètriques del servidor LFS.
    
    Aquesta classe gestiona la recollida contínua de telemetria:
    - Dades de posició i moviment dels vehicles (IS_MCI)
    - Temps de voltes i sectors (IS_LAP, IS_SPX)
    - Informació de jugadors (IS_NPL)
    - Esdeveniments de pista (IS_PIT, IS_FIN, etc.)
    
    Exemple:
        >>> from src.connection import InSimClient
        >>> client = InSimClient('127.0.0.1', 29999)
        >>> client.connect()
        >>> collector = TelemetryCollector(client)
        >>> collector.start()
        >>> # Obtenir dades
        >>> telemetry = collector.get_latest_telemetry()
        >>> collector.stop()
    """

    def __init__(self, client):
        """
        Inicialitza el col·lector de telemetria.

        Args:
            client: Client InSim connectat
        """
        self.client = client
        self.running = False
        self.collection_thread: Optional[Thread] = None
        self.stop_event = Event()
        
        # Emmagatzematge de dades
        self.car_telemetry: Dict[int, List[CarTelemetry]] = {}
        self.lap_telemetry: Dict[int, List[LapTelemetry]] = {}
        self.player_info: Dict[int, PlayerInfo] = {}
        
        # Callbacks personalitzats
        self.callbacks: Dict[str, List[Callable]] = {
            'car_update': [],
            'lap_complete': [],
            'split_time': [],
            'player_join': [],
            'player_leave': [],
        }
        
        logger.info("TelemetryCollector inicialitzat")

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Registra un callback per a un tipus d'esdeveniment.

        Args:
            event_type: Tipus d'esdeveniment ('car_update', 'lap_complete', etc.)
            callback: Funció a cridar quan ocorre l'esdeveniment
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            logger.debug(f"Callback registrat per '{event_type}'")
        else:
            logger.warning(f"Tipus d'esdeveniment desconegut: {event_type}")

    def _trigger_callbacks(self, event_type: str, data: Any) -> None:
        """Dispara els callbacks per un tipus d'esdeveniment."""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error en callback {event_type}: {e}")

    def handle_mci_packet(self, packet_data: bytes) -> None:
        """
        Gestiona un paquet IS_MCI (Multi Car Info).

        Args:
            packet_data: Dades del paquet
        """
        from src.connection.packet_handler import PacketHandler
        
        handler = PacketHandler()
        mci_info = handler.parse_mci_packet(packet_data)
        
        if mci_info:
            for car in mci_info['cars']:
                telemetry = CarTelemetry(
                    timestamp=time.time(),
                    plid=car['plid'],
                    node=car['node'],
                    lap=car['lap'],
                    position=car['position'],
                    speed=car['speed'] / 32768.0,  # Convertir a m/s
                    direction=car['direction'],
                    heading=car['heading'],
                    angular_velocity=car['angular_vel'],
                )
                
                # Emmagatzemar telemetria
                plid = car['plid']
                if plid not in self.car_telemetry:
                    self.car_telemetry[plid] = []
                self.car_telemetry[plid].append(telemetry)
                
                # Disparar callbacks
                self._trigger_callbacks('car_update', telemetry)

    def handle_lap_packet(self, packet_data: bytes) -> None:
        """
        Gestiona un paquet IS_LAP (temps de volta).

        Args:
            packet_data: Dades del paquet
        """
        # Implementació simplificada
        # En una implementació completa, parsejar el paquet IS_LAP
        logger.debug("Paquet IS_LAP rebut")

    def start(self, interval: int = 100) -> None:
        """
        Inicia la recollida de telemetria.

        Args:
            interval: Interval de recollida en ms (per defecte 100ms = 10Hz)
        """
        if self.running:
            logger.warning("La recollida ja està en marxa")
            return

        self.running = True
        self.stop_event.clear()
        
        # Inicialitzar InSim amb interval de telemetria
        self.client.initialize(flags=0, interval=interval)
        
        # Registrar handlers de paquets
        from src.connection.insim_client import PacketType
        self.client.register_callback(PacketType.ISP_MCI, self.handle_mci_packet)
        self.client.register_callback(PacketType.ISP_LAP, self.handle_lap_packet)
        
        # Iniciar thread de recollida
        self.collection_thread = Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        
        logger.info(f"Recollida de telemetria iniciada (interval: {interval}ms)")

    def _collection_loop(self) -> None:
        """Bucle principal de recollida de telemetria."""
        while self.running and not self.stop_event.is_set():
            try:
                # Rebre paquets del servidor
                packet = self.client.receive_packet(timeout=0.1)
                if packet:
                    # Processar paquet amb PacketHandler
                    from src.connection.packet_handler import PacketHandler
                    handler = PacketHandler()
                    handler.process_packet(packet)
                    
            except Exception as e:
                logger.error(f"Error en bucle de recollida: {e}")
                time.sleep(0.1)

    def stop(self) -> None:
        """Atura la recollida de telemetria."""
        if not self.running:
            logger.warning("La recollida no està en marxa")
            return

        self.running = False
        self.stop_event.set()
        
        if self.collection_thread:
            self.collection_thread.join(timeout=2.0)
        
        logger.info("Recollida de telemetria aturada")

    def get_latest_telemetry(self, plid: Optional[int] = None) -> Dict[int, CarTelemetry]:
        """
        Obté la telemetria més recent dels vehicles.

        Args:
            plid: Player ID específic (None per tots els jugadors)

        Returns:
            Dict amb telemetria per player ID
        """
        result = {}
        
        if plid is not None:
            if plid in self.car_telemetry and self.car_telemetry[plid]:
                result[plid] = self.car_telemetry[plid][-1]
        else:
            for player_id, telemetry_list in self.car_telemetry.items():
                if telemetry_list:
                    result[player_id] = telemetry_list[-1]
        
        return result

    def get_telemetry_history(
        self, 
        plid: int, 
        limit: Optional[int] = None
    ) -> List[CarTelemetry]:
        """
        Obté l'historial de telemetria d'un jugador.

        Args:
            plid: Player ID
            limit: Nombre màxim de mostres (None = totes)

        Returns:
            Llista de telemetria ordenada cronològicament
        """
        if plid not in self.car_telemetry:
            return []
        
        history = self.car_telemetry[plid]
        
        if limit:
            return history[-limit:]
        return history

    def clear_history(self, plid: Optional[int] = None) -> None:
        """
        Neteja l'historial de telemetria.

        Args:
            plid: Player ID específic (None per netejar tot)
        """
        if plid is not None:
            if plid in self.car_telemetry:
                self.car_telemetry[plid].clear()
                logger.debug(f"Historial netejat per PLID {plid}")
        else:
            self.car_telemetry.clear()
            self.lap_telemetry.clear()
            logger.info("Tot l'historial de telemetria netejat")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Obté estadístiques de la recollida de telemetria.

        Returns:
            Dict amb estadístiques
        """
        total_samples = sum(len(t) for t in self.car_telemetry.values())
        
        return {
            "running": self.running,
            "total_players": len(self.car_telemetry),
            "total_samples": total_samples,
            "players": {
                plid: len(telemetry)
                for plid, telemetry in self.car_telemetry.items()
            }
        }
