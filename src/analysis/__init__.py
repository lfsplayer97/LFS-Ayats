"""
Analysis Module
Mòdul d'anàlisi en temps real i detecció d'anomalies per LFS-Ayats.

Aquest mòdul proporciona:
- Detecció d'anomalies en dades telemètriques
- Predicció de rendiment i temps de volta
- Anàlisi de sectors i trajectòries
- Comparació avançada de voltes
- Sistema d'alertes en temps real
- Càlcul de mètriques de rendiment

Exemple:
    >>> from src.analysis import AnomalyDetector, PerformancePredictor
    >>> detector = AnomalyDetector()
    >>> predictor = PerformancePredictor()
"""

from src.analysis.anomaly import AnomalyDetector
from src.analysis.predictor import PerformancePredictor
from src.analysis.sectors import SectorAnalyzer
from src.analysis.comparator import AdvancedComparator
from src.analysis.alerts import AlertSystem, Alert, AlertLevel, AlertHandler
from src.analysis.metrics import MetricsCalculator
from src.analysis.utils import (
    SectorComparison,
    LapComparison,
    BrakingPoint,
    ThrottleAnalysis,
    TimeDelta,
)

__all__ = [
    # Anomaly detection
    "AnomalyDetector",
    # Performance prediction
    "PerformancePredictor",
    # Sector analysis
    "SectorAnalyzer",
    # Lap comparison
    "AdvancedComparator",
    # Alert system
    "AlertSystem",
    "Alert",
    "AlertLevel",
    "AlertHandler",
    # Metrics
    "MetricsCalculator",
    # Data models
    "SectorComparison",
    "LapComparison",
    "BrakingPoint",
    "ThrottleAnalysis",
    "TimeDelta",
]

__version__ = "0.1.0"
