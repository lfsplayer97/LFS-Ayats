"""
JSON Exporter
Export telemetry data to JSON format.
"""

import json
import logging
from typing import List, Any, Dict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONExporter:
    """
    Export telemetry data to JSON format.

    Example:
        >>> exporter = JSONExporter('telemetry.json')
        >>> exporter.export(telemetry_data)
    """

    def __init__(self, filename: str, indent: int = 2):
        """
        Initialize the JSON exporter.

        Args:
            filename: Output file name
            indent: JSON indentation (by default 2)
        """
        self.filename = Path(filename)
        self.indent = indent
        logger.info(f"JSONExporter initialized: {filename}")

    def export(
        self, telemetry_data: List[Any], metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Export telemetry data to JSON.

        Args:
            telemetry_data: List of CarTelemetry objects
            metadata: Optional metadata

        Returns:
            bool: True if export is successful
        """
        if not telemetry_data:
            logger.warning("No data to export")
            return False

        try:
            # Convert objects to dictionaries
            data_list = []
            for item in telemetry_data:
                data_list.append(
                    {
                        "timestamp": item.timestamp,
                        "plid": item.plid,
                        "node": item.node,
                        "lap": item.lap,
                        "position": item.position,
                        "speed": item.speed,
                        "direction": item.direction,
                        "heading": item.heading,
                        "angular_velocity": item.angular_velocity,
                    }
                )

            # Final structure
            output = {
                "metadata": metadata
                or {
                    "export_time": datetime.now().isoformat(),
                    "sample_count": len(telemetry_data),
                },
                "telemetry": data_list,
            }

            # Write to file
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=self.indent, ensure_ascii=False)

            logger.info(f"Exported {len(telemetry_data)} samples to {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False

    def export_processed(
        self, processed_data: Any, metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Export processed data to JSON.

        Args:
            processed_data: ProcessedTelemetry object
            metadata: Optional metadata

        Returns:
            bool: True if export is successful
        """
        try:
            output = {
                "metadata": metadata
                or {
                    "export_time": datetime.now().isoformat(),
                },
                "statistics": {
                    "avg_speed": processed_data.avg_speed,
                    "max_speed": processed_data.max_speed,
                    "min_speed": processed_data.min_speed,
                    "total_distance": processed_data.total_distance,
                    "sample_count": processed_data.sample_count,
                },
            }

            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=self.indent, ensure_ascii=False)

            logger.info(f"Processed data exported to {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error exporting processed data: {e}")
            return False

    def append(self, telemetry_data: List[Any]) -> bool:
        """
        Append data to an existing JSON file.

        Args:
            telemetry_data: List of CarTelemetry objects

        Returns:
            bool: True if operation is successful
        """
        try:
            # Read existing data
            if self.filename.exists():
                with open(self.filename, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            else:
                existing_data = {"metadata": {}, "telemetry": []}

            # Add new data
            for item in telemetry_data:
                existing_data["telemetry"].append(
                    {
                        "timestamp": item.timestamp,
                        "plid": item.plid,
                        "node": item.node,
                        "lap": item.lap,
                        "position": item.position,
                        "speed": item.speed,
                        "direction": item.direction,
                        "heading": item.heading,
                        "angular_velocity": item.angular_velocity,
                    }
                )

            # Update metadata
            existing_data["metadata"]["last_update"] = datetime.now().isoformat()
            existing_data["metadata"]["sample_count"] = len(existing_data["telemetry"])

            # Write again
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=self.indent, ensure_ascii=False)

            logger.info(f"Added {len(telemetry_data)} samples to {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error appending to JSON: {e}")
            return False
