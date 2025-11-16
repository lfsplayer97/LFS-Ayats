"""
Telemetry Collector
Collection of telemetry data from Live for Speed using InSim.

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import logging
import time
from typing import Dict, Any, List, Optional, Callable, Deque
from dataclasses import dataclass, field
from threading import Thread, Event
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class CarTelemetry:
    """
    Telemetry data for a vehicle.

    Attributes:
        timestamp: Sample timestamp
        plid: Player ID
        node: Current node on track
        lap: Current lap
        position: 3D position (x, y, z)
        speed: Speed in m/s
        direction: Vehicle direction
        heading: Orientation
        angular_velocity: Angular velocity
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
    Telemetry data for a lap.

    Attributes:
        timestamp: Timestamp
        plid: Player ID
        lap: Lap number
        lap_time: Lap time (ms)
        elapsed_time: Total time (ms)
        split_times: Sector times
        flags: Lap flags
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
    Player information.

    Attributes:
        plid: Player ID
        ucid: Unique Connection ID
        player_name: Player name
        car_name: Car name
        team_name: Team name
        plate: License plate
        flags: Player flags
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
    Collects telemetry data from the LFS server.

    This class handles continuous telemetry collection:
    - Position and movement data for vehicles (IS_MCI)
    - Lap and sector times (IS_LAP, IS_SPX)
    - Player information (IS_NPL)
    - Track events (IS_PIT, IS_FIN, etc.)

    Example:
        >>> from src.connection import InSimClient
        >>> client = InSimClient('127.0.0.1', 29999)
        >>> client.connect()
        >>> collector = TelemetryCollector(client)
        >>> collector.start()
        >>> # Get data
        >>> telemetry = collector.get_latest_telemetry()
        >>> collector.stop()
    """

    def __init__(self, client, max_samples_per_player: int = 10000):
        """
        Initialize the telemetry collector.

        Args:
            client: Connected InSim client
            max_samples_per_player: Maximum number of telemetry samples to
                store per player. Older samples are automatically removed
                when limit is reached. Default: 10000 samples
        """
        self.client = client
        self.running = False
        self.collection_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.max_samples_per_player = max_samples_per_player

        # Data storage - using deque with maxlen to prevent unbounded memory growth
        self.car_telemetry: Dict[int, Deque[CarTelemetry]] = {}
        self.lap_telemetry: Dict[int, Deque[LapTelemetry]] = {}
        self.player_info: Dict[int, PlayerInfo] = {}

        # Custom callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "car_update": [],
            "lap_complete": [],
            "split_time": [],
            "player_join": [],
            "player_leave": [],
        }

        logger.info(
            f"TelemetryCollector initialized "
            f"(max_samples_per_player={max_samples_per_player})"
        )

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Register a callback for an event type.

        Args:
            event_type: Event type ('car_update', 'lap_complete', etc.)
            callback: Function to call when event occurs
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            logger.debug(f"Callback registered for '{event_type}'")
        else:
            logger.warning(f"Unknown event type: {event_type}")

    def _trigger_callbacks(self, event_type: str, data: Any) -> None:
        """Trigger callbacks for an event type."""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in {event_type} callback: {e}")

    def handle_mci_packet(self, packet_data: bytes) -> None:
        """
        Handle an IS_MCI (Multi Car Info) packet.

        Args:
            packet_data: Packet data
        """
        from src.connection.packet_handler import PacketHandler

        handler = PacketHandler()
        mci_info = handler.parse_mci_packet(packet_data)

        if mci_info:
            for car in mci_info["cars"]:
                telemetry = CarTelemetry(
                    timestamp=time.time(),
                    plid=car["plid"],
                    node=car["node"],
                    lap=car["lap"],
                    position=car["position"],
                    speed=car["speed"] / 32768.0,  # Convert to m/s
                    direction=car["direction"],
                    heading=car["heading"],
                    angular_velocity=car["angular_vel"],
                )

                # Store telemetry with automatic size limiting
                plid = car["plid"]
                if plid not in self.car_telemetry:
                    self.car_telemetry[plid] = deque(maxlen=self.max_samples_per_player)
                self.car_telemetry[plid].append(telemetry)

                # Trigger callbacks
                self._trigger_callbacks("car_update", telemetry)

    def handle_lap_packet(self, packet_data: bytes) -> None:
        """
        Handle an IS_LAP (lap time) packet.

        Args:
            packet_data: Packet data
        """
        # Simplified implementation
        # In a full implementation, parse the IS_LAP packet
        logger.debug("IS_LAP packet received")

    def start(self, interval: int = 100) -> None:
        """
        Start telemetry collection.

        Args:
            interval: Collection interval in ms (default 100ms = 10Hz)
        """
        if self.running:
            logger.warning("Collection is already running")
            return

        self.running = True
        self.stop_event.clear()

        # Initialize InSim with telemetry interval
        self.client.initialize(flags=0, interval=interval)

        # Register packet handlers
        from src.connection.insim_client import PacketType

        self.client.register_callback(PacketType.ISP_MCI, self.handle_mci_packet)
        self.client.register_callback(PacketType.ISP_LAP, self.handle_lap_packet)

        # Start collection thread
        self.collection_thread = Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()

        logger.info(f"Telemetry collection started (interval: {interval}ms)")

    def _collection_loop(self) -> None:
        """Main telemetry collection loop."""
        while self.running and not self.stop_event.is_set():
            try:
                # Receive packets from server
                packet = self.client.receive_packet(timeout=0.1)
                if packet:
                    # Process packet with PacketHandler
                    from src.connection.packet_handler import PacketHandler

                    handler = PacketHandler()
                    handler.process_packet(packet)

            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                time.sleep(0.1)

    def stop(self) -> None:
        """Stop telemetry collection."""
        if not self.running:
            logger.warning("Collection is not running")
            return

        self.running = False
        self.stop_event.set()

        if self.collection_thread:
            self.collection_thread.join(timeout=2.0)

        logger.info("Telemetry collection stopped")

    def get_latest_telemetry(
        self, plid: Optional[int] = None
    ) -> Dict[int, CarTelemetry]:
        """
        Get the most recent vehicle telemetry.

        Args:
            plid: Specific Player ID (None for all players)

        Returns:
            Dict with telemetry by player ID
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
        self, plid: int, limit: Optional[int] = None
    ) -> List[CarTelemetry]:
        """
        Get telemetry history for a player.

        Args:
            plid: Player ID
            limit: Maximum number of samples (None = all)

        Returns:
            List of telemetry ordered chronologically
        """
        if plid not in self.car_telemetry:
            return []

        history = self.car_telemetry[plid]

        if limit:
            return history[-limit:]
        return history

    def clear_history(self, plid: Optional[int] = None) -> None:
        """
        Clear telemetry history.

        Args:
            plid: Specific Player ID (None to clear all)
        """
        if plid is not None:
            if plid in self.car_telemetry:
                self.car_telemetry[plid].clear()
                logger.debug(f"History cleared for PLID {plid}")
        else:
            self.car_telemetry.clear()
            self.lap_telemetry.clear()
            logger.info("All telemetry history cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get telemetry collection statistics.

        Returns:
            Dict with statistics including memory limits
        """
        total_samples = sum(len(t) for t in self.car_telemetry.values())

        return {
            "running": self.running,
            "total_players": len(self.car_telemetry),
            "total_samples": total_samples,
            "max_samples_per_player": self.max_samples_per_player,
            "players": {
                plid: len(telemetry) for plid, telemetry in self.car_telemetry.items()
            },
        }
