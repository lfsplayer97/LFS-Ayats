"""
Heartbeat Manager
Manages connection heartbeat independently for InSim connections.

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import logging
import threading
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .insim_client import InSimClient

logger = logging.getLogger(__name__)


class HeartbeatManager:
    """Manages connection heartbeat independently."""

    def __init__(self, client: "InSimClient", interval: float = 30.0):
        """
        Initialize the HeartbeatManager.

        Args:
            client: InSimClient instance to send heartbeats for
            interval: Interval between heartbeats in seconds
        """
        self.client = client
        self.interval = interval
        self.thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def start(self) -> None:
        """Start the heartbeat thread."""
        self.stop()
        self._stop.clear()
        self.thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True, name="InSimHeartbeat"
        )
        self.thread.start()
        logger.info(f"Heartbeat started (interval={self.interval}s)")

    def stop(self) -> None:
        """Stop the heartbeat thread."""
        if self.thread and self.thread.is_alive():
            logger.info("Stopping heartbeat...")
            self._stop.set()
            self.thread.join(timeout=2.0)
            self.thread = None

    def _heartbeat_loop(self) -> None:
        """Internal heartbeat loop."""
        from .insim_client import TinySubtype

        while not self._stop.is_set() and self.client.connected:
            try:
                self.client.send_tiny(TinySubtype.TINY_NONE)
                logger.debug("Heartbeat sent")
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                if self.client.reconnect_enabled:
                    self.client.trigger_reconnect()
                break
            self._stop.wait(timeout=self.interval)

        logger.info("Heartbeat stopped")
