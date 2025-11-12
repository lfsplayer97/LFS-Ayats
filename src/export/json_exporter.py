"""
JSON Exporter
Exportació de dades telemètriques a format JSON.
"""

import json
from typing import List, Any, Dict
from pathlib import Path
from datetime import datetime

from src.utils import get_logger

logger = get_logger(__name__)


class JSONExporter:
    """
    Exporta dades telemètriques a format JSON.
    
    Exemple:
        >>> exporter = JSONExporter('telemetry.json')
        >>> exporter.export(telemetry_data)
    """

    def __init__(self, filename: str, indent: int = 2):
        """
        Inicialitza l'exportador JSON.

        Args:
            filename: Nom del fitxer de sortida
            indent: Indentació del JSON (per defecte 2)
        """
        self.filename = Path(filename)
        self.indent = indent
        logger.info(f"JSONExporter inicialitzat: {filename}")

    def export(self, telemetry_data: List[Any], metadata: Dict[str, Any] = None) -> bool:
        """
        Exporta dades telemètriques a JSON.

        Args:
            telemetry_data: Llista d'objectes CarTelemetry
            metadata: Metadades opcionals

        Returns:
            bool: True si l'exportació és exitosa
        """
        if not telemetry_data:
            logger.warning("No hi ha dades per exportar")
            return False

        try:
            # Convertir objectes a diccionaris
            data_list = []
            for item in telemetry_data:
                data_list.append({
                    'timestamp': item.timestamp,
                    'plid': item.plid,
                    'node': item.node,
                    'lap': item.lap,
                    'position': item.position,
                    'speed': item.speed,
                    'direction': item.direction,
                    'heading': item.heading,
                    'angular_velocity': item.angular_velocity,
                })

            # Estructura final
            output = {
                'metadata': metadata or {
                    'export_time': datetime.now().isoformat(),
                    'sample_count': len(telemetry_data),
                },
                'telemetry': data_list
            }

            # Escriure a fitxer
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=self.indent, ensure_ascii=False)

            logger.info(f"Exportades {len(telemetry_data)} mostres a {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error exportant a JSON: {e}")
            return False

    def export_processed(self, processed_data: Any, metadata: Dict[str, Any] = None) -> bool:
        """
        Exporta dades processades a JSON.

        Args:
            processed_data: Objecte ProcessedTelemetry
            metadata: Metadades opcionals

        Returns:
            bool: True si l'exportació és exitosa
        """
        try:
            output = {
                'metadata': metadata or {
                    'export_time': datetime.now().isoformat(),
                },
                'statistics': {
                    'avg_speed': processed_data.avg_speed,
                    'max_speed': processed_data.max_speed,
                    'min_speed': processed_data.min_speed,
                    'total_distance': processed_data.total_distance,
                    'sample_count': processed_data.sample_count,
                }
            }

            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=self.indent, ensure_ascii=False)

            logger.info(f"Dades processades exportades a {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error exportant dades processades: {e}")
            return False

    def append(self, telemetry_data: List[Any]) -> bool:
        """
        Afegeix dades a un fitxer JSON existent.

        Args:
            telemetry_data: Llista d'objectes CarTelemetry

        Returns:
            bool: True si l'operació és exitosa
        """
        try:
            # Llegir dades existents
            if self.filename.exists():
                with open(self.filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            else:
                existing_data = {'metadata': {}, 'telemetry': []}

            # Afegir noves dades
            for item in telemetry_data:
                existing_data['telemetry'].append({
                    'timestamp': item.timestamp,
                    'plid': item.plid,
                    'node': item.node,
                    'lap': item.lap,
                    'position': item.position,
                    'speed': item.speed,
                    'direction': item.direction,
                    'heading': item.heading,
                    'angular_velocity': item.angular_velocity,
                })

            # Actualitzar metadades
            existing_data['metadata']['last_update'] = datetime.now().isoformat()
            existing_data['metadata']['sample_count'] = len(existing_data['telemetry'])

            # Escriure de nou
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=self.indent, ensure_ascii=False)

            logger.info(f"Afegides {len(telemetry_data)} mostres a {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error afegint a JSON: {e}")
            return False
