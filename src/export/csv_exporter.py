"""
CSV Exporter
Export telemetry data to CSV format.
"""

import csv
import logging
from typing import List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class CSVExporter:
    """
    Export telemetry data to CSV format.

    Example:
        >>> exporter = CSVExporter('telemetry.csv')
        >>> exporter.export(telemetry_data)
    """

    def __init__(self, filename: str, delimiter: str = ","):
        """
        Initialize the CSV exporter.

        Args:
            filename: Output file name
            delimiter: CSV delimiter (by default ',')
        """
        self.filename = Path(filename)
        self.delimiter = delimiter
        logger.info(f"CSVExporter initialized: {filename}")

    def export(self, telemetry_data: List[Any], overwrite: bool = True) -> bool:
        """
        Export telemetry data to CSV.

        Args:
            telemetry_data: List of CarTelemetry objects
            overwrite: Overwrite existing file

        Returns:
            bool: True if export is successful
        """
        if not telemetry_data:
            logger.warning("No data to export")
            return False

        try:
            mode = "w" if overwrite else "a"
            file_exists = self.filename.exists() and not overwrite

            with open(self.filename, mode, newline="", encoding="utf-8") as f:
                # Get fields from first object
                telemetry_data[0]

                # Basic fields
                fieldnames = [
                    "timestamp",
                    "plid",
                    "node",
                    "lap",
                    "position_x",
                    "position_y",
                    "position_z",
                    "speed",
                    "direction",
                    "heading",
                    "angular_velocity",
                ]

                writer = csv.DictWriter(
                    f, fieldnames=fieldnames, delimiter=self.delimiter
                )

                # Write header if new file
                if not file_exists:
                    writer.writeheader()

                # Write data
                for item in telemetry_data:
                    row = {
                        "timestamp": item.timestamp,
                        "plid": item.plid,
                        "node": item.node,
                        "lap": item.lap,
                        "position_x": item.position.get("x", 0),
                        "position_y": item.position.get("y", 0),
                        "position_z": item.position.get("z", 0),
                        "speed": item.speed,
                        "direction": item.direction,
                        "heading": item.heading,
                        "angular_velocity": item.angular_velocity,
                    }
                    writer.writerow(row)

            logger.info(f"Exported {len(telemetry_data)} samples to {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    def export_processed(self, processed_data: Any) -> bool:
        """
        Export processed data to CSV.

        Args:
            processed_data: ProcessedTelemetry object

        Returns:
            bool: True if export is successful
        """
        try:
            with open(self.filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=self.delimiter)

                # Write statistics
                writer.writerow(["Metric", "Value"])
                writer.writerow(
                    ["Average Speed (m/s)", f"{processed_data.avg_speed:.2f}"]
                )
                writer.writerow(["Max Speed (m/s)", f"{processed_data.max_speed:.2f}"])
                writer.writerow(["Min Speed (m/s)", f"{processed_data.min_speed:.2f}"])
                writer.writerow(
                    ["Total Distance (m)", f"{processed_data.total_distance:.2f}"]
                )
                writer.writerow(["Sample Count", processed_data.sample_count])

            logger.info(f"Processed data exported to {self.filename}")
            return True

        except Exception as e:
            logger.error(f"Error exporting processed data: {e}")
            return False
