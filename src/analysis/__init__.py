"""
Analysis Module
Real-time analysis and anomaly detection module for LFS-Ayats.

This module provides:
- Anomaly detection in telemetry data
- Performance and lap time prediction
- Sector and trajectory analysis
- Advanced lap comparison
- Real-time alert system
- Performance metrics calculation

Example:
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
