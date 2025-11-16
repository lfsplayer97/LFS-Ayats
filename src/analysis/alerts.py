"""
Alert System
Real-time alert system for telemetry events.

This module manages alert generation, distribution, and history
based on telemetry analysis data.
"""

import logging
from typing import List, Callable, Dict, Any, Optional
from abc import ABC, abstractmethod
import time

from src.analysis.utils import Alert, AlertLevel

logger = logging.getLogger(__name__)


class AlertHandler(ABC):
    """
    Classe base per gestors d'alertes.

    Els gestors personalitzats han d'heretar d'aquesta classe
    i implementar el mètode handle().
    """

    @abstractmethod
    def handle(self, alert: Alert) -> None:
        """
        Gestiona una alerta.

        Args:
            alert: Alerta a gestionar
        """


class ConsoleAlertHandler(AlertHandler):
    """Handler that prints alerts to console."""

    def handle(self, alert: Alert) -> None:
        """Imprimeix l'alerta a la consola."""
        color_codes = {
            AlertLevel.INFO: "\033[94m",  # Blue
            AlertLevel.WARNING: "\033[93m",  # Yellow
            AlertLevel.ERROR: "\033[91m",  # Red
            AlertLevel.CRITICAL: "\033[95m",  # Magenta
        }
        reset = "\033[0m"

        color = color_codes.get(alert.level, "")
        print(f"{color}[{alert.level.value.upper()}]{reset} {alert.message}")


class LogAlertHandler(AlertHandler):
    """Handler that logs alerts to the logging system."""

    def handle(self, alert: Alert) -> None:
        """Registra l'alerta al sistema de logging."""
        log_methods = {
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.ERROR: logger.error,
            AlertLevel.CRITICAL: logger.critical,
        }

        log_method = log_methods.get(alert.level, logger.info)
        log_method(alert.message)


class CallbackAlertHandler(AlertHandler):
    """Handler that calls a callback function."""

    def __init__(self, callback: Callable[[Alert], None]):
        """
        Initialize the handler with a callback.

        Args:
            callback: Funció a cridar amb l'alerta
        """
        self.callback = callback

    def handle(self, alert: Alert) -> None:
        """Crida el callback amb l'alerta."""
        try:
            self.callback(alert)
        except Exception as e:
            logger.error(f"Error en callback d'alerta: {e}")


class AlertSystem:
    """
    Alert management system.

    Manages creation, distribution and alert history
    del sistema d'anàlisi telemètric.

    Exemple:
        >>> system = AlertSystem()
        >>> system.register_handler(ConsoleAlertHandler())
        >>> alert = Alert(AlertLevel.WARNING, "Temperatura alta")
        >>> system.trigger_alert(alert)
    """

    def __init__(self, max_history: int = 1000, enable_filtering: bool = True):
        """
        Initialize the alert system.

        Args:
            max_history: Maximum number of alerts in history
            enable_filtering: Habilitar filtratge d'alertes duplicades
        """
        self.alert_handlers: List[AlertHandler] = []
        self.alert_history: List[Alert] = []
        self.max_history = max_history
        self.enable_filtering = enable_filtering
        self.last_alert_time: Dict[str, float] = {}
        self.alert_counts: Dict[str, int] = {}

        # Register default log handler
        self.register_handler(LogAlertHandler())

        logger.info("AlertSystem initialized")

    def register_handler(self, handler: AlertHandler) -> None:
        """
        Register an alert handler.

        Args:
            handler: Handler to register

        Example:
            >>> system = AlertSystem()
            >>> system.register_handler(ConsoleAlertHandler())
        """
        if handler not in self.alert_handlers:
            self.alert_handlers.append(handler)
            logger.debug(f"Alert handler registered: {type(handler).__name__}")

    def unregister_handler(self, handler: AlertHandler) -> None:
        """
        Unregister an alert handler.

        Args:
            handler: Handler to unregister
        """
        if handler in self.alert_handlers:
            self.alert_handlers.remove(handler)
            logger.debug(f"Alert handler unregistered: {type(handler).__name__}")

    def trigger_alert(self, alert: Alert, min_interval: float = 0.0) -> bool:
        """
        Dispara una alerta.

        Args:
            alert: Alerta a disparar
            min_interval: Minimum interval between alerts of the same type (seconds)

        Returns:
            True si l'alerta s'ha processat, False si s'ha filtrat

        Example:
            >>> system = AlertSystem()
            >>> alert = Alert(AlertLevel.WARNING, "Test")
            >>> system.trigger_alert(alert)
            True
        """
        # Filtrar alertes duplicades si està habilitat
        if self.enable_filtering and min_interval > 0:
            alert_key = f"{alert.level.value}:{alert.message}"
            current_time = time.time()

            if alert_key in self.last_alert_time:
                time_since_last = current_time - self.last_alert_time[alert_key]
                if time_since_last < min_interval:
                    logger.debug(f"Alerta filtrada: {alert.message}")
                    return False

            self.last_alert_time[alert_key] = current_time

        # Add to history
        self.alert_history.append(alert)

        # Maintain maximum history size
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)

        # Actualitzar comptador
        alert_type = f"{alert.level.value}"
        self.alert_counts[alert_type] = self.alert_counts.get(alert_type, 0) + 1

        # Notificar tots els gestors
        for handler in self.alert_handlers:
            try:
                handler.handle(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

        return True

    def create_and_trigger(
        self,
        level: AlertLevel,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        min_interval: float = 0.0,
    ) -> bool:
        """
        Crea i dispara una alerta en un sol pas.

        Args:
            level: Nivell de l'alerta
            message: Missatge de l'alerta
            data: Additional data
            min_interval: Interval mínim entre alertes

        Returns:
            True si l'alerta s'ha processat

        Example:
            >>> system = AlertSystem()
            >>> system.create_and_trigger(
            ...     AlertLevel.WARNING,
            ...     "Temperatura elevada",
            ...     {"temp": 95.5}
            ... )
        """
        alert = Alert(level=level, message=message, data=data or {})
        return self.trigger_alert(alert, min_interval)

    def check_conditions(self, telemetry_data: Dict[str, Any]) -> List[Alert]:
        """
        Check conditions and generate automatic alerts.

        This method can be used to integrate with detectors
        d'anomalies i altres sistemes d'anàlisi.

        Args:
            telemetry_data: Telemetry data to analyze

        Returns:
            List of generated alerts

        Example:
            >>> system = AlertSystem()
            >>> data = {"engine_temp": 100.0, "fuel": 5.0}
            >>> alerts = system.check_conditions(data)
        """
        generated_alerts = []

        # Example of automatic conditions
        # En una implementació real, aquests serien més complexos

        # Check engine temperature
        if "engine_temp" in telemetry_data:
            temp = telemetry_data["engine_temp"]
            if temp > 105:
                alert = Alert(
                    level=AlertLevel.CRITICAL,
                    message=f"Sobreescalfament crític: {temp}°C",
                    data={"temperature": temp},
                )
                if self.trigger_alert(alert, min_interval=10.0):
                    generated_alerts.append(alert)
            elif temp > 95:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    message=f"Temperatura elevada: {temp}°C",
                    data={"temperature": temp},
                )
                if self.trigger_alert(alert, min_interval=30.0):
                    generated_alerts.append(alert)

        # Check fuel level
        if "fuel" in telemetry_data:
            fuel = telemetry_data["fuel"]
            if fuel < 5.0:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    message=f"Combustible baix: {fuel:.1f}%",
                    data={"fuel": fuel},
                )
                if self.trigger_alert(alert, min_interval=20.0):
                    generated_alerts.append(alert)

        # Check tire wear
        if "tire_wear" in telemetry_data:
            wear = telemetry_data["tire_wear"]
            if wear > 80:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    message=f"Tires very worn: {wear:.1f}%",
                    data={"wear": wear},
                )
                if self.trigger_alert(alert, min_interval=30.0):
                    generated_alerts.append(alert)

        return generated_alerts

    def get_history(
        self, level: Optional[AlertLevel] = None, limit: Optional[int] = None
    ) -> List[Alert]:
        """
        Get alert history.

        Args:
            level: Filtrar per nivell (None = tots)
            limit: Maximum number of alerts (None = all)

        Returns:
            List of historical alerts

        Example:
            >>> system = AlertSystem()
            >>> warnings = system.get_history(level=AlertLevel.WARNING, limit=10)
        """
        history = self.alert_history

        # Filtrar per nivell si s'especifica
        if level is not None:
            history = [a for a in history if a.level == level]

        # Aplicar límit si s'especifica
        if limit is not None:
            history = history[-limit:]

        return history

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get alert system statistics.

        Returns:
            Dictionary with statistics

        Example:
            >>> system = AlertSystem()
            >>> stats = system.get_statistics()
            >>> print(f"Total alertes: {stats['total_alerts']}")
        """
        return {
            "total_alerts": len(self.alert_history),
            "total_handlers": len(self.alert_handlers),
            "alert_counts": self.alert_counts.copy(),
            "max_history": self.max_history,
            "filtering_enabled": self.enable_filtering,
        }

    def clear_history(self) -> None:
        """
        Clear alert history.

        Example:
            >>> system = AlertSystem()
            >>> system.clear_history()
        """
        self.alert_history.clear()
        self.last_alert_time.clear()
        self.alert_counts.clear()
        logger.debug("Alert history cleared")

    def set_filtering(self, enabled: bool) -> None:
        """
        Habilita o deshabilita el filtratge d'alertes.

        Args:
            enabled: True per habilitar filtratge
        """
        self.enable_filtering = enabled
        logger.debug(f"Filtratge d'alertes: {enabled}")
