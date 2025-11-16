"""
Telemetry Monitor Example
Real-time telemetry monitoring example.

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connection import InSimClient
from telemetry import TelemetryCollector, TelemetryProcessor
from utils import setup_logger

# Configure logging
logger = setup_logger("telemetry_monitor", "INFO")


def display_telemetry(telemetry):
    """Display telemetry on console."""
    print(f"\n=== Telemetry - PLID {telemetry.plid} ===")
    print(f"Lap: {telemetry.lap}")
    print(f"Node: {telemetry.node}")
    print(f"Speed: {telemetry.speed:.2f} m/s ({telemetry.speed * 3.6:.2f} km/h)")
    print(
        f"Position: X={telemetry.position.get('x', 0)}, "
        f"Y={telemetry.position.get('y', 0)}, "
        f"Z={telemetry.position.get('z', 0)}"
    )


def main():
    """Telemetry monitor example."""
    logger.info("=== LFS Telemetry Monitor ===")

    # Configuration
    HOST = "127.0.0.1"
    PORT = 29999
    DURATION = 30  # seconds

    try:
        # Create client and connect
        logger.info(f"Connecting to {HOST}:{PORT}...")
        client = InSimClient(host=HOST, port=PORT, app_name="TelemetryMon")
        client.connect()

        # Create telemetry collector
        collector = TelemetryCollector(client)

        # Register callback for car updates
        collector.register_callback("car_update", display_telemetry)

        # Start collection
        logger.info(f"Collecting telemetry for {DURATION} seconds...")
        collector.start(interval=100)  # 10 Hz

        # Wait
        time.sleep(DURATION)

        # Stop collection
        collector.stop()

        # Show statistics
        stats = collector.get_statistics()
        logger.info("\n=== Statistics ===")
        logger.info(f"Players tracked: {stats['total_players']}")
        logger.info(f"Total samples: {stats['total_samples']}")

        for plid, count in stats["players"].items():
            logger.info(f"  PLID {plid}: {count} samples")

            # Process telemetry
            processor = TelemetryProcessor()
            history = collector.get_telemetry_history(plid)
            processed = processor.process_telemetry(history)

            logger.info(f"    Average speed: {processed.avg_speed:.2f} m/s")
            logger.info(f"    Maximum speed: {processed.max_speed:.2f} m/s")
            logger.info(f"    Total distance: {processed.total_distance:.2f} m")

        # Disconnect
        client.disconnect()
        logger.info("Completed!")

    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        logger.info("Make sure LFS is running with InSim enabled")
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
