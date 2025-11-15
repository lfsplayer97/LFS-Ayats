"""
Data Logger Example
Example of data logger with export functionality.

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connection import InSimClient
from telemetry import TelemetryCollector
from export import CSVExporter, JSONExporter
from utils import setup_logger

# Configure logging
logger = setup_logger("data_logger", "INFO")


def main():
    """Data logger example."""
    logger.info("=== LFS Data Logger ===")

    # Configuration
    HOST = "127.0.0.1"
    PORT = 29999
    DURATION = 60  # seconds

    # Create output directories
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        # Create client and connect
        logger.info(f"Connecting to {HOST}:{PORT}...")
        client = InSimClient(host=HOST, port=PORT, app_name="DataLogger")
        client.connect()

        # Create collector
        collector = TelemetryCollector(client)

        # Start collection
        logger.info(f"Collecting data for {DURATION} seconds...")
        collector.start(interval=100)

        # Wait
        time.sleep(DURATION)

        # Stop collection
        collector.stop()

        # Export data
        logger.info("\nExporting data...")

        for plid in collector.car_telemetry.keys():
            history = collector.get_telemetry_history(plid)

            if history:
                # Export to CSV
                csv_file = output_dir / f"telemetry_plid{plid}_{timestamp}.csv"
                csv_exporter = CSVExporter(str(csv_file))
                if csv_exporter.export(history):
                    logger.info(f"Data exported to {csv_file}")

                # Export to JSON
                json_file = output_dir / f"telemetry_plid{plid}_{timestamp}.json"
                json_exporter = JSONExporter(str(json_file))
                metadata = {
                    "plid": plid,
                    "duration": DURATION,
                    "sample_count": len(history),
                }
                if json_exporter.export(history, metadata):
                    logger.info(f"Data exported to {json_file}")

        # Disconnect
        client.disconnect()
        logger.info("Finished!")

    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return 1

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
