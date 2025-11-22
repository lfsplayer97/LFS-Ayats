"""
Utility classes and data models for analysis module.

This file contains les data structures and models used
pels diferents components del mòdul d'anàlisi.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import time


class AlertLevel(Enum):
    """Nivells d'alerta del sistema."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """
    Alerta generada pel sistema d'anàlisi.

    Attributes:
        level: Nivell de gravetat de l'alerta
        timestamp: Marca temporal de l'alerta
        message: Missatge descriptiu
        data: Additional data related amb l'alerta
    """

    level: AlertLevel
    message: str
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.level.value.upper()}] {self.message}"


@dataclass
class SectorComparison:
    """
    Sector time comparison between two laps.

    Attributes:
        sector_number: Número del sector (1, 2, 3, etc.)
        lap1_time: Sector time on lap 1 (seconds)
        lap2_time: Sector time on lap 2 (seconds)
        difference: Time difference (lap1 - lap2, seconds)
        percentage_diff: Percentage difference
    """

    sector_number: int
    lap1_time: float
    lap2_time: float
    difference: float
    percentage_diff: float


@dataclass
class LapComparison:
    """
    Complete comparison between two laps.

    Attributes:
        lap1_id: ID of the first lap
        lap2_id: ID de la segona lap
        time_difference: Time difference total (seconds)
        sector_comparisons: List of comparisons per sector
        speed_trace_comparison: Comparació de traces de velocitat
        racing_line_difference: Difference in racing line
        suggestions: Suggeriments de millora
    """

    lap1_id: int
    lap2_id: int
    time_difference: float
    sector_comparisons: List[SectorComparison] = field(default_factory=list)
    speed_trace_comparison: Dict[str, Any] = field(default_factory=dict)
    racing_line_difference: float = 0.0
    suggestions: List[str] = field(default_factory=list)


@dataclass
class BrakingPoint:
    """
    Detected braking point.

    Attributes:
        position: Braking point position (x, y)
        lap: Número de lap
        distance: Distància des de l'inici del sector
        speed_before: Speed before braking
        speed_after: Speed after braking
        brake_duration: Braking duration (seconds)
        consistency_score: Consistency score (0-1)
    """

    position: Dict[str, float]
    lap: int
    distance: float
    speed_before: float
    speed_after: float
    brake_duration: float
    consistency_score: float = 1.0


@dataclass
class ThrottleAnalysis:
    """
    Anàlisi d'throttle application en corbes.

    Attributes:
        corner_id: Corner identifier
        entry_speed: Entry speed
        apex_speed: Apex speed
        exit_speed: Exit speed
        throttle_application_point: Throttle application point (% of corner)
        full_throttle_point: Full throttle point (% of corner)
        time_in_corner: Total time in corner (seconds)
    """

    corner_id: int
    entry_speed: float
    apex_speed: float
    exit_speed: float
    throttle_application_point: float
    full_throttle_point: float
    time_in_corner: float


@dataclass
class TimeDelta:
    """
    Point-to-point time delta between two laps.

    Attributes:
        distance_points: List of distances
        time_deltas: List of corresponding time deltas
        max_gain: Maximum time gain
        max_loss: Maximum time loss
        average_delta: Average delta
    """

    distance_points: List[float] = field(default_factory=list)
    time_deltas: List[float] = field(default_factory=list)
    max_gain: float = 0.0
    max_loss: float = 0.0
    average_delta: float = 0.0


@dataclass
class RacingLine:
    """
    Racing line optimala.

    Attributes:
        points: List of points (x, y) of the trajectory
        speeds: Velocitats corresponents a cada punt
        sector: Número de sector
        lap_time: Associated lap time
    """

    points: List[Dict[str, float]] = field(default_factory=list)
    speeds: List[float] = field(default_factory=list)
    sector: Optional[int] = None
    lap_time: Optional[float] = None


@dataclass
class Sector:
    """
    Sector information.

    Attributes:
        number: Número del sector
        time: Sector time (seconds)
        time_lost: Time lost relative to optimal (seconds)
        consistency: Sector consistency (0-1)
        best_time: Best sector time
    """

    number: int
    time: float
    time_lost: float = 0.0
    consistency: float = 1.0
    best_time: Optional[float] = None


def calculate_percentage_difference(value1: float, value2: float) -> float:
    """
    Calculate the percentage difference between two values.

    Args:
        value1: Primer valor
        value2: Segon valor (referència)

    Returns:
        Percentage difference ((value1 - value2) / value2 * 100)
    """
    if value2 == 0:
        return 0.0
    return ((value1 - value2) / value2) * 100.0


def moving_average(data: List[float], window_size: int) -> List[float]:
    """
    Calculate the moving average of a data series.

    Args:
        data: List of values
        window_size: Mida de la finestra

    Returns:
        List with moving averages
    """
    if window_size <= 0 or window_size > len(data):
        return data.copy()

    result = []
    for i in range(len(data)):
        start = max(0, i - window_size + 1)
        end = i + 1
        window = data[start:end]
        result.append(sum(window) / len(window))

    return result
