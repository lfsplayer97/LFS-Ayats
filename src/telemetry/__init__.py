"""
Telemetry Module
Recollida i processament de dades telemètriques de Live for Speed
"""

__version__ = "0.1.0"

from .collector import TelemetryCollector
from .processor import TelemetryProcessor

__all__ = ["TelemetryCollector", "TelemetryProcessor"]
