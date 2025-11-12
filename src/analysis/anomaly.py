"""
Anomaly Detector
Detecció d'anomalies en dades telemètriques de Live for Speed.

Aquest mòdul implementa diversos algorismes de detecció d'anomalies
per identificar comportaments anòmals del vehicle que poden indicar
problemes mecànics, errors del pilot o situacions perilloses.
"""

import statistics
from typing import List, Dict, Any, Optional, Tuple

from src.utils import get_logger
from src.analysis.utils import Alert, AlertLevel, moving_average

logger = get_logger(__name__)


# Constants per detecció d'anomalies
TEMP_WARNING_THRESHOLD = 95.0  # Celsius
TEMP_CRITICAL_THRESHOLD = 105.0  # Celsius
WHEEL_SPIN_THRESHOLD = 0.15  # 15% de diferència
STEERING_ROTATION_THRESHOLD = 0.3  # 30% de diferència
FLAT_SPOT_WEAR_THRESHOLD = 0.2  # 20% de desgast irregular
BRAKING_CONSISTENCY_THRESHOLD = 0.1  # 10% de variació
FUEL_WARNING_LAPS = 3  # Avís amb 3 voltes de marge


class AnomalyDetector:
    """
    Detector d'anomalies en telemetria de carreres.

    Aquesta classe utilitza tècniques estadístiques i umbral per detectar
    comportaments anòmals en les dades telemètriques.

    Exemple:
        >>> detector = AnomalyDetector()
        >>> if detector.detect_overheating(engine_temp):
        ...     print("Motor sobreescalfat!")
    """

    def __init__(
        self,
        temp_warning: float = TEMP_WARNING_THRESHOLD,
        temp_critical: float = TEMP_CRITICAL_THRESHOLD,
        z_score_threshold: float = 3.0,
    ):
        """
        Inicialitza el detector d'anomalies.

        Args:
            temp_warning: Temperatura d'avís (Celsius)
            temp_critical: Temperatura crítica (Celsius)
            z_score_threshold: Llindar per z-score (desviacions estàndard)
        """
        self.temp_warning = temp_warning
        self.temp_critical = temp_critical
        self.z_score_threshold = z_score_threshold
        self.anomaly_history: List[Alert] = []
        logger.info("AnomalyDetector inicialitzat")

    def detect_overheating(self, engine_temp: float) -> Tuple[bool, Optional[Alert]]:
        """
        Detecta sobreescalfament del motor.

        Args:
            engine_temp: Temperatura del motor (Celsius)

        Returns:
            Tuple amb (bool de detecció, Alert opcional)

        Example:
            >>> detector = AnomalyDetector()
            >>> detected, alert = detector.detect_overheating(100.0)
            >>> if detected:
            ...     print(alert.message)
        """
        if engine_temp >= self.temp_critical:
            alert = Alert(
                level=AlertLevel.CRITICAL,
                message=f"Sobreescalfament crític del motor: {engine_temp:.1f}°C",
                data={"temperature": engine_temp, "threshold": self.temp_critical},
            )
            self.anomaly_history.append(alert)
            logger.critical(alert.message)
            return True, alert
        elif engine_temp >= self.temp_warning:
            alert = Alert(
                level=AlertLevel.WARNING,
                message=f"Temperatura del motor elevada: {engine_temp:.1f}°C",
                data={"temperature": engine_temp, "threshold": self.temp_warning},
            )
            self.anomaly_history.append(alert)
            logger.warning(alert.message)
            return True, alert

        return False, None

    def detect_wheel_spin(
        self, linear_speed: float, wheel_speed: float
    ) -> Tuple[bool, Optional[Alert]]:
        """
        Detecta pèrdua de grip (rodes patinen).

        Compara la velocitat lineal del vehicle amb la velocitat de rotació
        de les rodes per detectar patinatge.

        Args:
            linear_speed: Velocitat lineal del vehicle (m/s)
            wheel_speed: Velocitat de rotació de les rodes (m/s equivalent)

        Returns:
            Tuple amb (bool de detecció, Alert opcional)
        """
        if linear_speed == 0:
            return False, None

        # Calcular diferència relativa
        speed_diff = abs(wheel_speed - linear_speed) / max(linear_speed, 0.001)

        if speed_diff > WHEEL_SPIN_THRESHOLD:
            alert = Alert(
                level=AlertLevel.WARNING,
                message=f"Pèrdua de grip detectada: {speed_diff*100:.1f}% de patinatge",
                data={
                    "linear_speed": linear_speed,
                    "wheel_speed": wheel_speed,
                    "difference": speed_diff,
                },
            )
            self.anomaly_history.append(alert)
            logger.warning(alert.message)
            return True, alert

        return False, None

    def detect_understeer(
        self, steering_angle: float, actual_rotation: float
    ) -> Tuple[bool, Optional[Alert]]:
        """
        Detecta subviratge.

        El subviratge ocorre quan l'angle de direcció és major que
        la rotació real del vehicle.

        Args:
            steering_angle: Angle del volant (radiants)
            actual_rotation: Rotació real del vehicle (radiants)

        Returns:
            Tuple amb (bool de detecció, Alert opcional)
        """
        if steering_angle == 0:
            return False, None

        # Normalitzar i comparar
        ratio = actual_rotation / max(abs(steering_angle), 0.001)

        if ratio < (1.0 - STEERING_ROTATION_THRESHOLD) and abs(steering_angle) > 0.1:
            alert = Alert(
                level=AlertLevel.INFO,
                message=f"Subviratge detectat: rotació {ratio*100:.1f}% de l'esperat",
                data={
                    "steering_angle": steering_angle,
                    "actual_rotation": actual_rotation,
                    "ratio": ratio,
                },
            )
            self.anomaly_history.append(alert)
            logger.info(alert.message)
            return True, alert

        return False, None

    def detect_oversteer(
        self, steering_angle: float, actual_rotation: float
    ) -> Tuple[bool, Optional[Alert]]:
        """
        Detecta sobreviratge.

        El sobreviratge ocorre quan la rotació real del vehicle és major
        que l'angle de direcció aplicat.

        Args:
            steering_angle: Angle del volant (radiants)
            actual_rotation: Rotació real del vehicle (radiants)

        Returns:
            Tuple amb (bool de detecció, Alert opcional)
        """
        if steering_angle == 0:
            return False, None

        # Normalitzar i comparar
        ratio = actual_rotation / max(abs(steering_angle), 0.001)

        if ratio > (1.0 + STEERING_ROTATION_THRESHOLD) and abs(steering_angle) > 0.1:
            alert = Alert(
                level=AlertLevel.WARNING,
                message=f"Sobreviratge detectat: rotació {ratio*100:.1f}% de l'esperat",
                data={
                    "steering_angle": steering_angle,
                    "actual_rotation": actual_rotation,
                    "ratio": ratio,
                },
            )
            self.anomaly_history.append(alert)
            logger.warning(alert.message)
            return True, alert

        return False, None

    def detect_flat_spot(
        self, wheel_wear_pattern: List[float]
    ) -> Tuple[bool, Optional[Alert]]:
        """
        Detecta flat spots als pneumàtics.

        Analitza el patró de desgast de les rodes per detectar zones
        amb desgast excessiu (flat spots).

        Args:
            wheel_wear_pattern: Llista de valors de desgast al voltant de la roda

        Returns:
            Tuple amb (bool de detecció, Alert opcional)
        """
        if not wheel_wear_pattern or len(wheel_wear_pattern) < 3:
            return False, None

        # Calcular estadístiques del desgast
        mean_wear = statistics.mean(wheel_wear_pattern)
        if mean_wear == 0:
            return False, None

        # Detectar pics de desgast
        for wear in wheel_wear_pattern:
            relative_wear = abs(wear - mean_wear) / mean_wear
            if relative_wear > FLAT_SPOT_WEAR_THRESHOLD:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    message=f"Flat spot detectat: desgast irregular de {relative_wear*100:.1f}%",
                    data={
                        "wear_pattern": wheel_wear_pattern,
                        "mean_wear": mean_wear,
                        "max_deviation": relative_wear,
                    },
                )
                self.anomaly_history.append(alert)
                logger.warning(alert.message)
                return True, alert

        return False, None

    def detect_inconsistent_braking(
        self, lap_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detecta frenades inconsistents entre voltes.

        Analitza els punts de frenada a través de múltiples voltes
        per identificar inconsistències.

        Args:
            lap_data: Llista de dades de voltes amb informació de frenades

        Returns:
            Llista de punts de frenada inconsistents

        Example:
            >>> detector = AnomalyDetector()
            >>> laps = [{"braking_points": [100, 250]}, {"braking_points": [100, 270]}]
            >>> inconsistent = detector.detect_inconsistent_braking(laps)
        """
        if len(lap_data) < 2:
            return []

        inconsistent_points = []

        # Agrupar punts de frenada per posició aproximada
        braking_zones: Dict[int, List[float]] = {}

        for lap in lap_data:
            if "braking_points" not in lap:
                continue

            for point in lap["braking_points"]:
                # Agrupar per zones de 50 metres
                zone = int(point / 50) * 50
                if zone not in braking_zones:
                    braking_zones[zone] = []
                braking_zones[zone].append(point)

        # Analitzar consistència de cada zona
        for zone, points in braking_zones.items():
            if len(points) < 2:
                continue

            mean_point = statistics.mean(points)
            stdev_point = statistics.stdev(points)

            if stdev_point / mean_point > BRAKING_CONSISTENCY_THRESHOLD:
                inconsistent_points.append(
                    {
                        "zone": zone,
                        "mean": mean_point,
                        "stdev": stdev_point,
                        "coefficient_variation": stdev_point / mean_point,
                        "samples": len(points),
                    }
                )
                logger.info(
                    f"Frenada inconsistent a zona {zone}m: "
                    f"CV={stdev_point/mean_point:.2%}"
                )

        return inconsistent_points

    def detect_fuel_warning(
        self, fuel_level: float, fuel_per_lap: float, laps_remaining: int
    ) -> Tuple[bool, Optional[Alert]]:
        """
        Detecta si el combustible és insuficient.

        Args:
            fuel_level: Nivell actual de combustible (%)
            fuel_per_lap: Consum mitjà per volta (%)
            laps_remaining: Voltes restants a la cursa

        Returns:
            Tuple amb (bool de detecció, Alert opcional)
        """
        if laps_remaining <= 0 or fuel_per_lap <= 0:
            return False, None

        # Calcular voltes possibles amb el combustible actual
        laps_possible = fuel_level / fuel_per_lap

        # Afegir marge de seguretat
        if laps_possible < (laps_remaining + FUEL_WARNING_LAPS):
            shortage = (laps_remaining + FUEL_WARNING_LAPS) - laps_possible
            level = AlertLevel.CRITICAL if shortage > 5 else AlertLevel.WARNING

            alert = Alert(
                level=level,
                message=f"Combustible insuficient: {laps_possible:.1f} voltes possibles, "
                f"{laps_remaining} necessàries",
                data={
                    "fuel_level": fuel_level,
                    "fuel_per_lap": fuel_per_lap,
                    "laps_possible": laps_possible,
                    "laps_remaining": laps_remaining,
                },
            )
            self.anomaly_history.append(alert)
            logger.warning(alert.message)
            return True, alert

        return False, None

    def detect_outliers_zscore(
        self, data: List[float], threshold: Optional[float] = None
    ) -> List[int]:
        """
        Detecta outliers utilitzant z-score.

        Args:
            data: Llista de valors a analitzar
            threshold: Llindar personalitzat (None per usar el per defecte)

        Returns:
            Llista d'índexs que són outliers
        """
        if len(data) < 3:
            return []

        threshold = threshold or self.z_score_threshold
        mean = statistics.mean(data)
        stdev = statistics.stdev(data)

        if stdev == 0:
            return []

        outliers = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / stdev)
            if z_score > threshold:
                outliers.append(i)

        return outliers

    def detect_outliers_iqr(self, data: List[float]) -> List[int]:
        """
        Detecta outliers utilitzant el mètode IQR (Interquartile Range).

        Args:
            data: Llista de valors a analitzar

        Returns:
            Llista d'índexs que són outliers
        """
        if len(data) < 4:
            return []

        sorted_data = sorted(data)
        n = len(sorted_data)

        # Calcular quartils
        q1_idx = n // 4
        q3_idx = 3 * n // 4
        q1 = sorted_data[q1_idx]
        q3 = sorted_data[q3_idx]

        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Identificar outliers
        outliers = []
        for i, value in enumerate(data):
            if value < lower_bound or value > upper_bound:
                outliers.append(i)

        return outliers

    def detect_sudden_changes(
        self, data: List[float], window_size: int = 5, sensitivity: float = 2.0
    ) -> List[int]:
        """
        Detecta canvis sobtats en les dades utilitzant mitjanes mòbils.

        Args:
            data: Llista de valors a analitzar
            window_size: Mida de la finestra per la mitjana mòbil
            sensitivity: Sensibilitat de detecció (múltiple de desviació)

        Returns:
            Llista d'índexs on es detecten canvis sobtats
        """
        if len(data) < window_size + 1:
            return []

        # Calcular mitjana mòbil
        ma = moving_average(data, window_size)

        # Calcular desviacions
        deviations = [abs(data[i] - ma[i]) for i in range(len(data))]

        if len(deviations) < 2:
            return []

        mean_dev = statistics.mean(deviations)
        stdev_dev = statistics.stdev(deviations) if len(deviations) > 1 else 0

        if stdev_dev == 0:
            return []

        # Detectar canvis sobtats
        sudden_changes = []
        threshold = mean_dev + sensitivity * stdev_dev

        for i, dev in enumerate(deviations):
            if dev > threshold:
                sudden_changes.append(i)

        return sudden_changes

    def check_telemetry(self, telemetry_data: Dict[str, Any]) -> List[Alert]:
        """
        Comprova múltiples condicions en dades telemètriques.

        Args:
            telemetry_data: Diccionari amb dades telemètriques

        Returns:
            Llista d'alertes detectades

        Example:
            >>> detector = AnomalyDetector()
            >>> data = {"engine_temp": 100.0, "linear_speed": 50.0, "wheel_speed": 60.0}
            >>> alerts = detector.check_telemetry(data)
            >>> for alert in alerts:
            ...     print(alert)
        """
        alerts = []

        # Check engine temperature
        if "engine_temp" in telemetry_data:
            detected, alert = self.detect_overheating(telemetry_data["engine_temp"])
            if detected and alert:
                alerts.append(alert)

        # Check wheel spin
        if "linear_speed" in telemetry_data and "wheel_speed" in telemetry_data:
            detected, alert = self.detect_wheel_spin(
                telemetry_data["linear_speed"], telemetry_data["wheel_speed"]
            )
            if detected and alert:
                alerts.append(alert)

        # Check steering
        if "steering_angle" in telemetry_data and "actual_rotation" in telemetry_data:
            detected, alert = self.detect_understeer(
                telemetry_data["steering_angle"], telemetry_data["actual_rotation"]
            )
            if detected and alert:
                alerts.append(alert)

            detected, alert = self.detect_oversteer(
                telemetry_data["steering_angle"], telemetry_data["actual_rotation"]
            )
            if detected and alert:
                alerts.append(alert)

        return alerts

    def get_anomaly_history(self) -> List[Alert]:
        """
        Retorna l'historial d'anomalies detectades.

        Returns:
            Llista d'alertes històriques
        """
        return self.anomaly_history.copy()

    def clear_history(self) -> None:
        """Neteja l'historial d'anomalies."""
        self.anomaly_history.clear()
        logger.debug("Historial d'anomalies netejat")
