"""
Telemetry Buffer
Thread-safe buffer for telemetry data during reconnections.
"""

import threading
from collections import deque
from typing import Any, Optional, Callable
from datetime import datetime

from src.utils import get_logger

logger = get_logger(__name__)


class TelemetryBuffer:
    """
    Thread-safe buffer for telemetry data.

    This buffer stores telemetry data during connection interruptions
    to prevent data loss during reconnection attempts.

    Args:
        max_size: Maximum number of items to buffer (older items dropped)

    Example:
        >>> buffer = TelemetryBuffer(max_size=1000)
        >>> buffer.add(telemetry_data)
        >>> buffer.flush_to_exporter(exporter)
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize telemetry buffer.

        Args:
            max_size: Maximum buffer size (uses deque with maxlen)
        """
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.Lock()
        self.max_size = max_size
        self.dropped_count = 0
        logger.info(f"TelemetryBuffer initialized with max_size={max_size}")

    def add(self, data: Any) -> bool:
        """
        Add telemetry data to buffer.

        Args:
            data: Telemetry data to buffer

        Returns:
            bool: True if added successfully
        """
        with self.lock:
            if len(self.buffer) >= self.max_size:
                self.dropped_count += 1
                logger.debug(
                    f"Buffer full, dropping oldest item "
                    f"(total dropped: {self.dropped_count})"
                )

            # Add timestamp if not present
            if isinstance(data, dict) and "buffered_at" not in data:
                data["buffered_at"] = datetime.now().isoformat()

            self.buffer.append(data)
            return True

    def get(self) -> Optional[Any]:
        """
        Get and remove one item from buffer (FIFO).

        Returns:
            Data item or None if buffer is empty
        """
        with self.lock:
            if self.buffer:
                return self.buffer.popleft()
            return None

    def flush_to_exporter(self, exporter: Any) -> int:
        """
        Flush all buffered data to an exporter.

        Args:
            exporter: Exporter object with export() method or callable

        Returns:
            Number of items flushed
        """
        flushed_count = 0

        with self.lock:
            while self.buffer:
                data = self.buffer.popleft()
                try:
                    # Try export method first, then try callable
                    if hasattr(exporter, "export") and callable(
                        getattr(exporter, "export")
                    ):
                        exporter.export(data)
                    elif callable(exporter):
                        exporter(data)
                    else:
                        raise TypeError(
                            "Exporter must have export() method or be callable"
                        )
                    flushed_count += 1
                except Exception as e:
                    logger.error(f"Error flushing data to exporter: {e}")
                    # Put item back at front if export failed
                    self.buffer.appendleft(data)
                    break

        if flushed_count > 0:
            logger.info(f"Flushed {flushed_count} items from buffer")

        return flushed_count

    def flush_to_callback(self, callback: Callable[[Any], None]) -> int:
        """
        Flush all buffered data using a callback function.

        Args:
            callback: Function to call for each buffered item

        Returns:
            Number of items flushed
        """
        flushed_count = 0

        with self.lock:
            while self.buffer:
                data = self.buffer.popleft()
                try:
                    callback(data)
                    flushed_count += 1
                except Exception as e:
                    logger.error(f"Error in flush callback: {e}")
                    self.buffer.appendleft(data)
                    break

        if flushed_count > 0:
            logger.info(f"Flushed {flushed_count} items via callback")

        return flushed_count

    def clear(self) -> int:
        """
        Clear all buffered data.

        Returns:
            Number of items cleared
        """
        with self.lock:
            count = len(self.buffer)
            self.buffer.clear()
            self.dropped_count = 0

        if count > 0:
            logger.info(f"Cleared {count} items from buffer")

        return count

    def size(self) -> int:
        """
        Get current buffer size.

        Returns:
            Number of items in buffer
        """
        with self.lock:
            return len(self.buffer)

    def is_empty(self) -> bool:
        """
        Check if buffer is empty.

        Returns:
            True if buffer is empty
        """
        with self.lock:
            return len(self.buffer) == 0

    def is_full(self) -> bool:
        """
        Check if buffer is at capacity.

        Returns:
            True if buffer is full
        """
        with self.lock:
            return len(self.buffer) >= self.max_size

    def get_stats(self) -> dict:
        """
        Get buffer statistics.

        Returns:
            Dict with buffer statistics
        """
        with self.lock:
            return {
                "size": len(self.buffer),
                "max_size": self.max_size,
                "dropped_count": self.dropped_count,
                "utilization": (
                    len(self.buffer) / self.max_size if self.max_size > 0 else 0
                ),
            }
