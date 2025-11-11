"""
Example: Using Streaming Overlay for OBS

This example demonstrates how to set up and use the streaming overlay
for displaying real-time telemetry data in OBS Studio.
"""

import time
from src.integrations import StreamingOverlay


def simulate_telemetry():
    """
    Simulate telemetry data updates.

    In a real application, this would be replaced with actual
    telemetry data from the InSim connection.
    """
    overlay = StreamingOverlay(port=5000)

    print("Starting streaming overlay server...")
    print("=" * 60)
    print("OBS Setup Instructions:")
    print("1. Open OBS Studio")
    print("2. Add a 'Browser' source to your scene")
    print("3. Set URL to: http://localhost:5000")
    print("4. Set Width: 1920, Height: 1080")
    print("5. Enable 'Shutdown source when not visible'")
    print("6. Adjust position and size as needed")
    print("=" * 60)

    # Start the overlay server
    overlay.start()

    print("\nServer started! Access the overlay at: http://localhost:5000")
    print("Simulating telemetry data...")
    print("Press Ctrl+C to stop\n")

    try:
        # Simulate a lap with varying telemetry data
        lap_time = 0.0
        speed = 0
        rpm = 1000
        gear = 0

        while True:
            # Simulate acceleration
            if speed < 200:
                speed += 2
                rpm = min(8000, rpm + 100)
                if rpm > 7500 and gear < 6:
                    gear += 1
                    rpm = 4000

            # Update telemetry data
            overlay.update_telemetry(
                {
                    "speed": speed,
                    "rpm": rpm,
                    "gear": gear if gear > 0 else "N",
                    "lap_time": lap_time,
                    "position": "2/10",
                }
            )

            lap_time += 0.1
            time.sleep(0.1)  # Update at 10Hz

            # Reset after completing a lap (98 seconds)
            if lap_time >= 98.0:
                print(f"Lap completed: {lap_time:.3f}s")
                lap_time = 0.0
                speed = 0
                rpm = 1000
                gear = 0
                time.sleep(2)  # Pause between laps

    except KeyboardInterrupt:
        print("\n\nStopping overlay server...")
        overlay.stop()
        print("Server stopped.")


if __name__ == "__main__":
    simulate_telemetry()
