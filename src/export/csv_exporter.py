"""
CSV Exporter
Exportació de dades telemètriques a format CSV.
"""

import csv
from typing import List, Any
from pathlib import Path

from src.utils import get_logger

logger = get_logger(__name__)


class CSVExporter:
    """
    Exporta dades telemètriques a format CSV.
    
    Exemple:
        >>> exporter = CSVExporter('telemetry.csv')
        >>> exporter.export(telemetry_data)
    """

    def __init__(self, filename: str, delimiter: str = ','):
        """
        Inicialitza l'exportador CSV.

        Args:
            filename: Nom del fitxer de sortida
            delimiter: Delimitador CSV (per defecte ',')
        """
        self.filename = Path(filename)
        self.delimiter = delimiter
        logger.info(f"CSVExporter inicialitzat: {filename}")

    def export(self, telemetry_data: List[Any], overwrite: bool = True) -> bool:
        """
        Exporta dades telemètriques a CSV.

        Args:
            telemetry_data: Llista d'objectes CarTelemetry
            overwrite: Sobreescriure fitxer existent

        Returns:
            bool: True si l'exportació és exitosa
        """
        if not telemetry_data:
            logger.warning("No hi ha dades per exportar")
            return False

        try:
            mode = 'w' if overwrite else 'a'
            file_exists = self.filename.exists() and not overwrite

            with open(self.filename, mode, newline='', encoding='utf-8') as f:
                # Obtenir camps del primer objecte
                first_item = telemetry_data[0]
                
                # Camps bàsics
                fieldnames = [
                    'timestamp', 'plid', 'node', 'lap',
                    'position_x', 'position_y', 'position_z',
                    'speed', 'direction', 'heading', 'angular_velocity'
                ]

                writer = csv.DictWriter(
                    f, 
                    fieldnames=fieldnames,
                    delimiter=self.delimiter
                )

                # Escriure encapçalament si és fitxer nou
                if not file_exists:
                    writer.writeheader()

                # Escriure dades
                for item in telemetry_data:
                    row = {
                        'timestamp': item.timestamp,
                        'plid': item.plid,
                        'node': item.node,
                        'lap': item.lap,
                        'position_x': item.position.get('x', 0),
                        'position_y': item.position.get('y', 0),
                        'position_z': item.position.get('z', 0),
                        'speed': item.speed,
                        'direction': item.direction,
                        'heading': item.heading,
                        'angular_velocity': item.angular_velocity,
                    }
                    writer.writerow(row)

            logger.info(f"Exportades {len(telemetry_data)} mostres a {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error exportant a CSV: {e}")
            return False

    def export_processed(self, processed_data: Any) -> bool:
        """
        Exporta dades processades a CSV.

        Args:
            processed_data: Objecte ProcessedTelemetry

        Returns:
            bool: True si l'exportació és exitosa
        """
        try:
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                
                # Escriure estadístiques
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Average Speed (m/s)', f"{processed_data.avg_speed:.2f}"])
                writer.writerow(['Max Speed (m/s)', f"{processed_data.max_speed:.2f}"])
                writer.writerow(['Min Speed (m/s)', f"{processed_data.min_speed:.2f}"])
                writer.writerow(['Total Distance (m)', f"{processed_data.total_distance:.2f}"])
                writer.writerow(['Sample Count', processed_data.sample_count])

            logger.info(f"Dades processades exportades a {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error exportant dades processades: {e}")
            return False
