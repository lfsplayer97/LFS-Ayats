"""
Utility classes and data models for analysis module.

Aquest fitxer conté les estructures de dades i models utilitzats
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
        data: Dades addicionals relacionades amb l'alerta
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
    Comparació de temps de sector entre dues voltes.

    Attributes:
        sector_number: Número del sector (1, 2, 3, etc.)
        lap1_time: Temps del sector a la volta 1 (segons)
        lap2_time: Temps del sector a la volta 2 (segons)
        difference: Diferència de temps (lap1 - lap2, segons)
        percentage_diff: Diferència percentual
    """

    sector_number: int
    lap1_time: float
    lap2_time: float
    difference: float
    percentage_diff: float


@dataclass
class LapComparison:
    """
    Comparació completa entre dues voltes.

    Attributes:
        lap1_id: ID de la primera volta
        lap2_id: ID de la segona volta
        time_difference: Diferència de temps total (segons)
        sector_comparisons: Llista de comparacions per sector
        speed_trace_comparison: Comparació de traces de velocitat
        racing_line_difference: Diferència en la línia de carrera
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
    Punt de frenada detectat.

    Attributes:
        position: Posició del punt de frenada (x, y)
        lap: Número de volta
        distance: Distància des de l'inici del sector
        speed_before: Velocitat abans de frenar
        speed_after: Velocitat després de frenar
        brake_duration: Duració de la frenada (segons)
        consistency_score: Puntuació de consistència (0-1)
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
    Anàlisi d'aplicació de gas en corbes.

    Attributes:
        corner_id: Identificador de la corba
        entry_speed: Velocitat d'entrada
        apex_speed: Velocitat a l'apex
        exit_speed: Velocitat de sortida
        throttle_application_point: Punt on s'aplica gas (% de la corba)
        full_throttle_point: Punt de gas a fons (% de la corba)
        time_in_corner: Temps total a la corba (segons)
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
    Delta de temps punt a punt entre dues voltes.

    Attributes:
        distance_points: Llista de distàncies
        time_deltas: Llista de deltes de temps corresponents
        max_gain: Màxim guany de temps
        max_loss: Màxima pèrdua de temps
        average_delta: Delta mitjà
    """

    distance_points: List[float] = field(default_factory=list)
    time_deltas: List[float] = field(default_factory=list)
    max_gain: float = 0.0
    max_loss: float = 0.0
    average_delta: float = 0.0


@dataclass
class RacingLine:
    """
    Línia de carrera òptima.

    Attributes:
        points: Llista de punts (x, y) de la trajectòria
        speeds: Velocitats corresponents a cada punt
        sector: Número de sector
        lap_time: Temps de volta associat
    """

    points: List[Dict[str, float]] = field(default_factory=list)
    speeds: List[float] = field(default_factory=list)
    sector: Optional[int] = None
    lap_time: Optional[float] = None


@dataclass
class Sector:
    """
    Informació d'un sector.

    Attributes:
        number: Número del sector
        time: Temps del sector (segons)
        time_lost: Temps perdut respecte a l'òptim (segons)
        consistency: Consistència del sector (0-1)
        best_time: Millor temps del sector
    """

    number: int
    time: float
    time_lost: float = 0.0
    consistency: float = 1.0
    best_time: Optional[float] = None


def calculate_percentage_difference(value1: float, value2: float) -> float:
    """
    Calcula la diferència percentual entre dos valors.

    Args:
        value1: Primer valor
        value2: Segon valor (referència)

    Returns:
        Diferència percentual ((value1 - value2) / value2 * 100)
    """
    if value2 == 0:
        return 0.0
    return ((value1 - value2) / value2) * 100.0


def moving_average(data: List[float], window_size: int) -> List[float]:
    """
    Calcula la mitjana mòbil d'una sèrie de dades.

    Args:
        data: Llista de valors
        window_size: Mida de la finestra

    Returns:
        Llista amb les mitjanes mòbils
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
