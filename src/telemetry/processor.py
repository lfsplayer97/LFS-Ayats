"""
Telemetry Processor
Processing and validation of telemetry data.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class ProcessedTelemetry:
    """
    Processed telemetry data with statistics.
    
    Attributes:
        avg_speed: Average speed
        max_speed: Maximum speed
        min_speed: Minimum speed
        total_distance: Total distance traveled
        sample_count: Number of samples
    """
    avg_speed: float = 0.0
    max_speed: float = 0.0
    min_speed: float = 0.0
    total_distance: float = 0.0
    sample_count: int = 0


class TelemetryProcessor:
    """
    Processes and validates telemetry data.
    
    This class provides:
    - Telemetry data validation
    - Statistics calculation
    - Data filtering
    - Anomaly detection
    
    Example:
        >>> processor = TelemetryProcessor()
        >>> processed = processor.process_telemetry(telemetry_data)
        >>> stats = processor.calculate_statistics(telemetry_data)
    """

    def __init__(self, max_speed: float = 150.0):
        """
        Initialize the telemetry processor.

        Args:
            max_speed: Maximum valid speed in m/s (default 150 m/s)
        """
        self.max_speed = max_speed
        self.validation_errors: List[str] = []
        logger.info("TelemetryProcessor initialized")

    def validate_telemetry(self, telemetry) -> bool:
        """
        Validate telemetry data.

        Args:
            telemetry: CarTelemetry object

        Returns:
            bool: True if data is valid, False otherwise
        """
        self.validation_errors.clear()
        is_valid = True

        # Validate speed
        if telemetry.speed < 0:
            self.validation_errors.append("Negative speed")
            is_valid = False
        elif telemetry.speed > self.max_speed:
            self.validation_errors.append(f"Speed too high: {telemetry.speed}")
            is_valid = False

        # Validate position
        if not telemetry.position:
            self.validation_errors.append("Empty position")
            is_valid = False

        # Validate player ID
        if telemetry.plid < 0 or telemetry.plid > 255:
            self.validation_errors.append(f"Invalid Player ID: {telemetry.plid}")
            is_valid = False

        if not is_valid:
            logger.warning(f"Invalid telemetry: {', '.join(self.validation_errors)}")

        return is_valid

    def process_telemetry(self, telemetry_list: List) -> ProcessedTelemetry:
        """
        Process a list of telemetry and calculate statistics.

        Args:
            telemetry_list: List of CarTelemetry objects

        Returns:
            ProcessedTelemetry: Processed data with statistics
        """
        if not telemetry_list:
            return ProcessedTelemetry()

        # Filter valid data
        valid_telemetry = [t for t in telemetry_list if self.validate_telemetry(t)]

        if not valid_telemetry:
            logger.warning("No valid telemetry to process")
            return ProcessedTelemetry()

        # Calculate statistics
        speeds = [t.speed for t in valid_telemetry]
        
        # Calculate distance (simple approximation)
        total_distance = 0.0
        for i in range(1, len(valid_telemetry)):
            prev = valid_telemetry[i-1]
            curr = valid_telemetry[i]
            
            # Euclidean distance between two points
            if prev.position and curr.position:
                dx = curr.position.get('x', 0) - prev.position.get('x', 0)
                dy = curr.position.get('y', 0) - prev.position.get('y', 0)
                distance = (dx**2 + dy**2)**0.5
                total_distance += distance

        return ProcessedTelemetry(
            avg_speed=statistics.mean(speeds),
            max_speed=max(speeds),
            min_speed=min(speeds),
            total_distance=total_distance,
            sample_count=len(valid_telemetry)
        )

    def calculate_statistics(self, telemetry_list: List) -> Dict[str, Any]:
        """
        Calculate detailed telemetry statistics.

        Args:
            telemetry_list: List of CarTelemetry objects

        Returns:
            Dict with detailed statistics
        """
        if not telemetry_list:
            return {}

        speeds = [t.speed for t in telemetry_list if self.validate_telemetry(t)]

        if not speeds:
            return {}

        return {
            "speed": {
                "mean": statistics.mean(speeds),
                "median": statistics.median(speeds),
                "stdev": statistics.stdev(speeds) if len(speeds) > 1 else 0,
                "min": min(speeds),
                "max": max(speeds),
            },
            "sample_count": len(telemetry_list),
            "valid_samples": len(speeds),
        }

    def filter_by_speed_range(
        self, 
        telemetry_list: List,
        min_speed: float = 0.0,
        max_speed: Optional[float] = None
    ) -> List:
        """
        Filter telemetry by speed range.

        Args:
            telemetry_list: List of telemetry
            min_speed: Minimum speed
            max_speed: Maximum speed (None = no limit)

        Returns:
            Filtered list of telemetry
        """
        max_spd = max_speed if max_speed is not None else float('inf')
        
        return [
            t for t in telemetry_list
            if min_speed <= t.speed <= max_spd
        ]

    def detect_anomalies(
        self, 
        telemetry_list: List,
        threshold_stdev: float = 3.0
    ) -> List[int]:
        """
        Detect anomalies in telemetry using standard deviation.

        Args:
            telemetry_list: List of telemetry
            threshold_stdev: Threshold in standard deviations

        Returns:
            List of indices with anomalies
        """
        if len(telemetry_list) < 3:
            return []

        speeds = [t.speed for t in telemetry_list]
        mean_speed = statistics.mean(speeds)
        stdev_speed = statistics.stdev(speeds)

        anomalies = []
        for i, speed in enumerate(speeds):
            z_score = abs((speed - mean_speed) / stdev_speed) if stdev_speed > 0 else 0
            if z_score > threshold_stdev:
                anomalies.append(i)
                logger.debug(f"Anomaly detected at index {i}: speed={speed}, z-score={z_score:.2f}")

        return anomalies

    def get_validation_errors(self) -> List[str]:
        """
        Get validation errors from the last validation.

        Returns:
            List of errors
        """
        return self.validation_errors.copy()
