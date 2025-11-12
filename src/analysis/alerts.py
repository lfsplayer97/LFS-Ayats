"""
Alert System
Sistema d'alertes en temps real per esdeveniments de telemetria.

Aquest mòdul gestiona la generació, distribució i historial d'alertes
basades en les dades d'anàlisi telemètric.
"""

from typing import List, Callable, Dict, Any, Optional
from abc import ABC, abstractmethod
import time

from src.utils import get_logger
from src.analysis.utils import Alert, AlertLevel

logger = get_logger(__name__)


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
        pass


class ConsoleAlertHandler(AlertHandler):
    """Gestor que imprimeix alertes a la consola."""

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
    """Gestor que registra alertes al sistema de logging."""

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
    """Gestor que crida una funció callback."""

    def __init__(self, callback: Callable[[Alert], None]):
        """
        Inicialitza el gestor amb un callback.

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
    Sistema de gestió d'alertes.

    Gestiona la creació, distribució i historial d'alertes
    del sistema d'anàlisi telemètric.

    Exemple:
        >>> system = AlertSystem()
        >>> system.register_handler(ConsoleAlertHandler())
        >>> alert = Alert(AlertLevel.WARNING, "Temperatura alta")
        >>> system.trigger_alert(alert)
    """

    def __init__(self, max_history: int = 1000, enable_filtering: bool = True):
        """
        Inicialitza el sistema d'alertes.

        Args:
            max_history: Nombre màxim d'alertes a l'historial
            enable_filtering: Habilitar filtratge d'alertes duplicades
        """
        self.alert_handlers: List[AlertHandler] = []
        self.alert_history: List[Alert] = []
        self.max_history = max_history
        self.enable_filtering = enable_filtering
        self.last_alert_time: Dict[str, float] = {}
        self.alert_counts: Dict[str, int] = {}

        # Registrar gestor de log per defecte
        self.register_handler(LogAlertHandler())

        logger.info("AlertSystem inicialitzat")

    def register_handler(self, handler: AlertHandler) -> None:
        """
        Registra un gestor d'alertes.

        Args:
            handler: Gestor a registrar

        Example:
            >>> system = AlertSystem()
            >>> system.register_handler(ConsoleAlertHandler())
        """
        if handler not in self.alert_handlers:
            self.alert_handlers.append(handler)
            logger.debug(f"Gestor d'alertes registrat: {type(handler).__name__}")

    def unregister_handler(self, handler: AlertHandler) -> None:
        """
        Desregistra un gestor d'alertes.

        Args:
            handler: Gestor a desregistrar
        """
        if handler in self.alert_handlers:
            self.alert_handlers.remove(handler)
            logger.debug(f"Gestor d'alertes desregistrat: {type(handler).__name__}")

    def trigger_alert(self, alert: Alert, min_interval: float = 0.0) -> bool:
        """
        Dispara una alerta.

        Args:
            alert: Alerta a disparar
            min_interval: Interval mínim entre alertes del mateix tipus (segons)

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

        # Afegir a l'historial
        self.alert_history.append(alert)

        # Mantenir mida màxima de l'historial
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
                logger.error(f"Error en gestor d'alertes: {e}")

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
            data: Dades addicionals
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
        Comprova condicions i genera alertes automàtiques.

        Aquest mètode pot ser utilitzat per integrar amb detectors
        d'anomalies i altres sistemes d'anàlisi.

        Args:
            telemetry_data: Dades telemètriques a analitzar

        Returns:
            Llista d'alertes generades

        Example:
            >>> system = AlertSystem()
            >>> data = {"engine_temp": 100.0, "fuel": 5.0}
            >>> alerts = system.check_conditions(data)
        """
        generated_alerts = []

        # Exemple de condicions automàtiques
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
                    message=f"Pneumàtics molt desgastats: {wear:.1f}%",
                    data={"wear": wear},
                )
                if self.trigger_alert(alert, min_interval=30.0):
                    generated_alerts.append(alert)

        return generated_alerts

    def get_history(
        self, level: Optional[AlertLevel] = None, limit: Optional[int] = None
    ) -> List[Alert]:
        """
        Obté l'historial d'alertes.

        Args:
            level: Filtrar per nivell (None = tots)
            limit: Nombre màxim d'alertes (None = totes)

        Returns:
            Llista d'alertes històriques

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
        Obté estadístiques del sistema d'alertes.

        Returns:
            Diccionari amb estadístiques

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
        Neteja l'historial d'alertes.

        Example:
            >>> system = AlertSystem()
            >>> system.clear_history()
        """
        self.alert_history.clear()
        self.last_alert_time.clear()
        self.alert_counts.clear()
        logger.debug("Historial d'alertes netejat")

    def set_filtering(self, enabled: bool) -> None:
        """
        Habilita o deshabilita el filtratge d'alertes.

        Args:
            enabled: True per habilitar filtratge
        """
        self.enable_filtering = enabled
        logger.debug(f"Filtratge d'alertes: {enabled}")
