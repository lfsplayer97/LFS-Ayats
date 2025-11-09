"""
Telemetry Processor
Processament i validació de dades telemètriques.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class ProcessedTelemetry:
    """
    Dades telemètriques processades amb estadístiques.
    
    Attributes:
        avg_speed: Velocitat mitjana
        max_speed: Velocitat màxima
        min_speed: Velocitat mínima
        total_distance: Distància total recorreguda
        sample_count: Nombre de mostres
    """
    avg_speed: float = 0.0
    max_speed: float = 0.0
    min_speed: float = 0.0
    total_distance: float = 0.0
    sample_count: int = 0


class TelemetryProcessor:
    """
    Processa i valida dades telemètriques.
    
    Aquesta classe proporciona:
    - Validació de dades telemètriques
    - Càlcul d'estadístiques
    - Filtratge de dades
    - Detecció d'anomalies
    
    Exemple:
        >>> processor = TelemetryProcessor()
        >>> processed = processor.process_telemetry(telemetry_data)
        >>> stats = processor.calculate_statistics(telemetry_data)
    """

    def __init__(self, max_speed: float = 150.0):
        """
        Inicialitza el processador de telemetria.

        Args:
            max_speed: Velocitat màxima vàlida en m/s (per defecte 150 m/s)
        """
        self.max_speed = max_speed
        self.validation_errors: List[str] = []
        logger.info("TelemetryProcessor inicialitzat")

    def validate_telemetry(self, telemetry) -> bool:
        """
        Valida les dades telemètriques.

        Args:
            telemetry: Objecte CarTelemetry

        Returns:
            bool: True si les dades són vàlides, False altrament
        """
        self.validation_errors.clear()
        is_valid = True

        # Validar velocitat
        if telemetry.speed < 0:
            self.validation_errors.append("Velocitat negativa")
            is_valid = False
        elif telemetry.speed > self.max_speed:
            self.validation_errors.append(f"Velocitat massa alta: {telemetry.speed}")
            is_valid = False

        # Validar posició
        if not telemetry.position:
            self.validation_errors.append("Posició buida")
            is_valid = False

        # Validar player ID
        if telemetry.plid < 0 or telemetry.plid > 255:
            self.validation_errors.append(f"Player ID invàlid: {telemetry.plid}")
            is_valid = False

        if not is_valid:
            logger.warning(f"Telemetria invàlida: {', '.join(self.validation_errors)}")

        return is_valid

    def process_telemetry(self, telemetry_list: List) -> ProcessedTelemetry:
        """
        Processa una llista de telemetria i calcula estadístiques.

        Args:
            telemetry_list: Llista d'objectes CarTelemetry

        Returns:
            ProcessedTelemetry: Dades processades amb estadístiques
        """
        if not telemetry_list:
            return ProcessedTelemetry()

        # Filtrar dades vàlides
        valid_telemetry = [t for t in telemetry_list if self.validate_telemetry(t)]

        if not valid_telemetry:
            logger.warning("Cap telemetria vàlida per processar")
            return ProcessedTelemetry()

        # Calcular estadístiques
        speeds = [t.speed for t in valid_telemetry]
        
        # Calcular distància (aproximació simple)
        total_distance = 0.0
        for i in range(1, len(valid_telemetry)):
            prev = valid_telemetry[i-1]
            curr = valid_telemetry[i]
            
            # Distància euclidiana entre dos punts
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
        Calcula estadístiques detallades de la telemetria.

        Args:
            telemetry_list: Llista d'objectes CarTelemetry

        Returns:
            Dict amb estadístiques detallades
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
        Filtra telemetria per rang de velocitat.

        Args:
            telemetry_list: Llista de telemetria
            min_speed: Velocitat mínima
            max_speed: Velocitat màxima (None = sense límit)

        Returns:
            Llista filtrada de telemetria
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
        Detecta anomalies en la telemetria utilitzant desviació estàndard.

        Args:
            telemetry_list: Llista de telemetria
            threshold_stdev: Threshold en desviacions estàndard

        Returns:
            Llista d'índexs amb anomalies
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
                logger.debug(f"Anomalia detectada a índex {i}: speed={speed}, z-score={z_score:.2f}")

        return anomalies

    def get_validation_errors(self) -> List[str]:
        """
        Obté els errors de validació de l'última validació.

        Returns:
            Llista d'errors
        """
        return self.validation_errors.copy()
