"""
Visualization Examples
Examples of using the visualization module for telemetry analysis.

This example demonstrates:
- Creating various plots and charts
- Using the lap comparator
- Generating track maps
- Analyzing telemetry data

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connection import InSimClient
from telemetry import TelemetryCollector
from visualization import (
    create_speed_vs_distance_plot,
    create_track_map,
    create_heatmap_plot,
    LapComparator,
)
from utils import setup_logger

# Configure logging
logger = setup_logger("visualization_example", "INFO")


def main():
    """Run visualization examples."""
    logger.info("=== LFS Visualization Examples ===")

    # Configuration
    HOST = "127.0.0.1"
    PORT = 29999
    COLLECTION_TIME = 30  # seconds

    try:
        # Connect to LFS
        logger.info(f"Connecting to {HOST}:{PORT}...")
        client = InSimClient(host=HOST, port=PORT, app_name="VisualizationEx")
        client.connect()
        logger.info("Connected!")

        # Start collecting telemetry
        collector = TelemetryCollector(client)
        logger.info(f"Collecting telemetry for {COLLECTION_TIME} seconds...")
        collector.start(interval=100)

        # Wait for data collection
        time.sleep(COLLECTION_TIME)

        # Stop collection
        collector.stop()
        logger.info("Collection stopped")

        # Get collected data
        stats = collector.get_statistics()
        logger.info(f"Statistics: {stats}")

        if stats["total_players"] == 0:
            logger.warning("No players detected. Make sure you're driving in LFS!")
            client.disconnect()
            return 1

        # Get first player's data
        first_player = list(stats["players"].keys())[0]
        telemetry = collector.get_telemetry_history(first_player)
        logger.info(
            f"Retrieved {len(telemetry)} telemetry samples for Player {first_player}"
        )

        # Example 1: Speed vs Distance Plot
        logger.info("\n=== Creating Speed vs Distance Plot ===")
        fig = create_speed_vs_distance_plot(telemetry, title="Speed Analysis")
        output_file = Path(__file__).parent / "speed_vs_distance.html"
        fig.write_html(str(output_file))
        logger.info(f"Saved to: {output_file}")

        # Example 2: Track Map
        logger.info("\n=== Creating Track Map ===")
        fig = create_track_map(telemetry, show_speed_colors=True)
        output_file = Path(__file__).parent / "track_map.html"
        fig.write_html(str(output_file))
        logger.info(f"Saved to: {output_file}")

        # Example 3: Speed Heatmap
        logger.info("\n=== Creating Speed Heatmap ===")
        fig = create_heatmap_plot(telemetry)
        output_file = Path(__file__).parent / "speed_heatmap.html"
        fig.write_html(str(output_file))
        logger.info(f"Saved to: {output_file}")

        # Example 4: Lap Comparison (if enough data)
        if len(telemetry) > 100:
            logger.info("\n=== Creating Lap Comparison ===")
            comparator = LapComparator()

            # Split data into two "laps" for comparison
            mid_point = len(telemetry) // 2
            lap1 = telemetry[:mid_point]
            lap2 = telemetry[mid_point:]

            comparator.add_lap("First Half", lap1)
            comparator.add_lap("Second Half", lap2)

            # Create comparison plot
            fig = comparator.create_comparison_plot()
            output_file = Path(__file__).parent / "lap_comparison.html"
            fig.write_html(str(output_file))
            logger.info(f"Saved to: {output_file}")

            # Create trajectory overlay
            fig = comparator.create_trajectory_overlay()
            output_file = Path(__file__).parent / "trajectory_overlay.html"
            fig.write_html(str(output_file))
            logger.info(f"Saved to: {output_file}")

            # Get comparison statistics
            comparison_stats = comparator.get_statistics()
            logger.info(f"Comparison stats: {comparison_stats}")

        # Disconnect
        client.disconnect()
        logger.info("\n=== Examples Complete! ===")
        logger.info(
            "Open the generated HTML files in your browser to view the visualizations"
        )

    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        logger.info("Make sure LFS is running with InSim enabled (/insim 29999)")
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
