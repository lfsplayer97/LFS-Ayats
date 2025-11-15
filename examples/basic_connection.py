"""
Basic Connection Example
Basic example of connecting to LFS via InSim.

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connection import InSimClient, PacketHandler
from utils import setup_logger

# Configure logging
logger = setup_logger("basic_connection", "DEBUG")


def main():
    """Basic connection example."""
    logger.info("=== Basic InSim Connection Example ===")

    # Configuration
    HOST = "127.0.0.1"  # Localhost
    PORT = 29999  # Default InSim port

    try:
        # Create InSim client
        logger.info(f"Connecting to {HOST}:{PORT}...")
        client = InSimClient(
            host=HOST, port=PORT, admin_password="", app_name="BasicExample"
        )

        # Connect
        client.connect()
        logger.info("Connection established!")

        # Initialize InSim
        client.initialize()
        logger.info("InSim initialized!")

        # Receive some packets
        logger.info("Receiving packets for 10 seconds...")
        handler = PacketHandler()

        start_time = time.time()
        while time.time() - start_time < 10:
            packet = client.receive_packet(timeout=1.0)
            if packet:
                info = handler.parse_packet(packet)
                if info:
                    logger.info(
                        f"Packet received - Type: {info.type}, Size: {info.size}"
                    )

        # Disconnect
        client.disconnect()
        logger.info("Disconnected!")

    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        logger.info("Make sure LFS is running and InSim is enabled")
        logger.info("To enable InSim: /insim 29999 in LFS")
        return 1

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
