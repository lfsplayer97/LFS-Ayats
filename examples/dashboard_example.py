"""
Dashboard Example
Example of running the LFS telemetry dashboard.

This example demonstrates:
- Starting the real-time telemetry dashboard
- Connecting to LFS server
- Viewing live telemetry data
- Using interactive visualizations

Usage:
    1. Start Live for Speed
    2. Enable InSim: /insim 29999
    3. Run this script: python examples/dashboard_example.py
    4. Open browser to http://localhost:8050
    5. Click "Connect" button in the dashboard

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from visualization import TelemetryDashboard
from utils import setup_logger

# Configure logging
logger = setup_logger("dashboard_example", "INFO")


def main():
    """Run the telemetry dashboard."""
    logger.info("=== LFS Telemetry Dashboard Example ===")

    # Configuration
    LFS_HOST = "127.0.0.1"
    LFS_PORT = 29999
    DASHBOARD_PORT = 8050
    UPDATE_INTERVAL = 100  # milliseconds

    logger.info(f"LFS Server: {LFS_HOST}:{LFS_PORT}")
    logger.info(f"Dashboard URL: http://localhost:{DASHBOARD_PORT}")
    logger.info(f"Update interval: {UPDATE_INTERVAL}ms")
    logger.info("")
    logger.info("Instructions:")
    logger.info("1. Make sure LFS is running with InSim enabled (/insim 29999)")
    logger.info("2. Open browser to http://localhost:8050")
    logger.info("3. Click 'Connect' button in the dashboard")
    logger.info("4. Select a player from the dropdown")
    logger.info("5. Watch real-time telemetry data!")
    logger.info("")

    try:
        # Create and run dashboard
        dashboard = TelemetryDashboard(
            host=LFS_HOST,
            port=LFS_PORT,
            app_name="LFS-Ayats Dashboard",
            update_interval=UPDATE_INTERVAL,
        )

        # Run dashboard (blocking call)
        dashboard.run(
            debug=True,  # Enable debug mode for development
            port=DASHBOARD_PORT,
            host="0.0.0.0",  # Allow external connections
        )

    except KeyboardInterrupt:
        logger.info("\nShutting down dashboard...")
        dashboard.shutdown()
        logger.info("Dashboard stopped")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
