"""
Example: Enhanced InSim Client with Reconnection and Heartbeat

This example demonstrates the new error handling and reconnection features
of the InSim client.
"""

import time
from src.connection import InSimClient, ConnectionState
from src.telemetry import TelemetryBuffer
from src.utils.logger import setup_logger

# Setup colored logging
logger = setup_logger("example", "INFO", use_colors=True)


def on_connected(old_state, new_state):
    """Callback when connection is established"""
    logger.info(
        f"🟢 Connected! Transitioned from {old_state.value} to {new_state.value}"
    )


def on_reconnecting(old_state, new_state):
    """Callback when reconnection starts"""
    logger.warning(f"🔄 Reconnecting... Previous state: {old_state.value}")


def on_error(old_state, new_state):
    """Callback when connection error occurs"""
    logger.error(f"🔴 Connection error! Previous state: {old_state.value}")


def main():
    """Main example function"""

    # Create InSim client with enhanced features
    client = InSimClient(
        host="127.0.0.1",
        port=29999,
        app_name="LFS-Ayats-Demo",
        max_retries=5,  # Retry up to 5 times
        retry_delay=2.0,  # Start with 2s delay (exponential backoff)
        reconnect_enabled=True,  # Enable automatic reconnection
        heartbeat_interval=30.0,  # Send heartbeat every 30 seconds
    )

    # Create telemetry buffer for data preservation during reconnections
    telemetry_buffer = TelemetryBuffer(max_size=1000)

    # Register state change callbacks
    client.on_state_change(ConnectionState.CONNECTED, on_connected)
    client.on_state_change(ConnectionState.RECONNECTING, on_reconnecting)
    client.on_state_change(ConnectionState.ERROR, on_error)

    logger.info("Attempting to connect to LFS...")

    # Try to connect with automatic retries
    if client.connect_with_retry():
        logger.info("✓ Successfully connected to LFS server")

        # Initialize InSim connection
        try:
            client.initialize(
                flags=1,  # Enable information packets
                interval=100,  # MCI/NLP interval (centiseconds)
            )
            logger.info("✓ InSim initialized")

            # Start heartbeat to keep connection alive
            client.start_heartbeat()
            logger.info("✓ Heartbeat started")

            # Simulate collecting telemetry data
            logger.info("Collecting telemetry data for 60 seconds...")
            logger.info("Press Ctrl+C to stop")

            try:
                for i in range(60):
                    # Simulate receiving telemetry data
                    telemetry_data = {
                        "timestamp": time.time(),
                        "iteration": i,
                        "speed": 100 + i,
                        "rpm": 5000 + i * 10,
                    }

                    # Buffer the data (useful during reconnections)
                    telemetry_buffer.add(telemetry_data)

                    # Check if packet is available (non-blocking)
                    packet = client.receive_packet(timeout=1.0)
                    if packet:
                        logger.debug(f"Received packet: {len(packet)} bytes")

                    time.sleep(1)

                    # Display buffer stats every 10 seconds
                    if i % 10 == 0 and i > 0:
                        stats = telemetry_buffer.get_stats()
                        logger.info(
                            f"Buffer stats: {stats['size']}/{stats['max_size']} items "
                            f"({stats['utilization']*100:.1f}% full)"
                        )

            except KeyboardInterrupt:
                logger.info("Interrupted by user")

            # Display final statistics
            stats = telemetry_buffer.get_stats()
            logger.info(
                f"\nFinal buffer stats:\n"
                f"  - Items buffered: {stats['size']}\n"
                f"  - Items dropped: {stats['dropped_count']}\n"
                f"  - Buffer utilization: {stats['utilization']*100:.1f}%"
            )

        except Exception as e:
            logger.error(f"Error during operation: {e}")
        finally:
            # Clean shutdown
            logger.info("Shutting down...")
            client.stop_heartbeat()
            client.disconnect()
            logger.info("✓ Disconnected cleanly")
    else:
        logger.error("✗ Failed to connect after all retries")
        logger.info("Make sure LFS is running with InSim enabled:")
        logger.info("  /insim 29999")


if __name__ == "__main__":
    main()
