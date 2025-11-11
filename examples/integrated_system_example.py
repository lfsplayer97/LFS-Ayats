"""
Example: Complete Integration Setup

This example demonstrates how to use all external integrations together
in a complete telemetry monitoring setup.
"""

import asyncio
import yaml
from datetime import datetime
from src.integrations import (
    DiscordIntegration,
    TelegramIntegration,
    StreamingOverlay,
    GoogleDriveIntegration,
)


class IntegratedTelemetrySystem:
    """
    Complete telemetry system with all integrations enabled.

    This class demonstrates how to combine Discord notifications,
    Telegram alerts, streaming overlay, and cloud backup in a
    unified system.
    """

    def __init__(self, config_path="config.yaml"):
        """Initialize the integrated system."""
        self.config = self._load_config(config_path)
        self.discord = None
        self.telegram = None
        self.overlay = None
        self.cloud_storage = None

        self._setup_integrations()

    def _load_config(self, config_path):
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found, using defaults")
            return {}

    def _setup_integrations(self):
        """Initialize all enabled integrations."""
        integrations_config = self.config.get("integrations", {})

        # Setup Discord
        discord_config = integrations_config.get("discord", {})
        if discord_config.get("enabled", False):
            self.discord = DiscordIntegration(
                webhook_url=discord_config["webhook_url"],
                bot_token=discord_config.get("bot_token"),
            )
            print("✓ Discord integration enabled")

        # Setup Telegram
        telegram_config = integrations_config.get("telegram", {})
        if telegram_config.get("enabled", False):
            self.telegram = TelegramIntegration(
                bot_token=telegram_config["bot_token"],
                chat_id=telegram_config["chat_id"],
            )
            print("✓ Telegram integration enabled")

        # Setup Streaming Overlay
        streaming_config = integrations_config.get("streaming", {})
        if streaming_config.get("enabled", False):
            self.overlay = StreamingOverlay(
                port=streaming_config.get("overlay_port", 5000)
            )
            self.overlay.start()
            print("✓ Streaming overlay enabled")

        # Setup Cloud Storage
        cloud_config = integrations_config.get("cloud_backup", {})
        if cloud_config.get("enabled", False):
            provider = cloud_config.get("provider", "google_drive")
            if provider == "google_drive":
                try:
                    self.cloud_storage = GoogleDriveIntegration(
                        cloud_config["credentials_path"]
                    )
                    print("✓ Google Drive backup enabled")
                except Exception as e:
                    print(f"✗ Failed to enable Google Drive: {e}")

    async def on_personal_best(self, lap_data):
        """
        Handle new personal best event.

        Sends notifications to all configured platforms.
        """
        print(f"\n🏆 New personal best: {lap_data['time']:.3f}s")

        # Send Discord notification
        if self.discord:
            await self.discord.notify_personal_best(lap_data)
            print("  ✓ Discord notification sent")

        # Send Telegram notification
        if self.telegram:
            await self.telegram.notify_personal_best(lap_data)
            print("  ✓ Telegram notification sent")

    async def on_session_end(self, session_data):
        """
        Handle session end event.

        Sends summary and performs backup if enabled.
        """
        print(f"\n🏁 Session ended: {session_data['total_laps']} laps completed")

        # Send Discord summary
        if self.discord:
            await self.discord.notify_session_summary(session_data)
            print("  ✓ Discord summary sent")

        # Send Telegram summary
        if self.telegram:
            await self.telegram.notify_session_summary(session_data)
            print("  ✓ Telegram summary sent")

        # Backup to cloud storage
        if self.cloud_storage:
            # In a real implementation, this would backup the session file
            print("  ✓ Session backed up to cloud storage")

    def update_telemetry(self, telemetry_data):
        """
        Update real-time telemetry display.

        Updates the streaming overlay with current telemetry data.
        """
        if self.overlay:
            self.overlay.update_telemetry(telemetry_data)

    async def on_anomaly_detected(self, anomaly_data):
        """
        Handle anomaly detection event.

        Sends immediate alerts to all configured platforms.
        """
        severity = anomaly_data.get("severity", "warning")
        print(f"\n⚠️ Anomaly detected ({severity}): {anomaly_data['type']}")

        # Send Discord alert
        if self.discord:
            await self.discord.notify_anomaly(anomaly_data)
            print("  ✓ Discord alert sent")

        # Send Telegram alert (for critical issues)
        if self.telegram and severity in ["error", "critical"]:
            message = (
                f"🚨 <b>ALERT</b>: {anomaly_data['type']}\n"
                f"Severity: {severity.upper()}\n"
                f"{anomaly_data['description']}"
            )
            await self.telegram.send_message(message)
            print("  ✓ Telegram alert sent")

    def shutdown(self):
        """Cleanup and shutdown all integrations."""
        print("\n\nShutting down integrations...")

        if self.overlay:
            self.overlay.stop()
            print("  ✓ Streaming overlay stopped")


async def main():
    """
    Main example demonstrating the integrated system.

    In a real application, this would connect to the InSim server
    and process actual telemetry data.
    """
    print("Starting Integrated Telemetry System")
    print("=" * 60)

    # Initialize the system
    # Note: This will look for config.yaml in the current directory
    # You can also pass a custom config path
    system = IntegratedTelemetrySystem()

    print("\nSimulating telemetry events...\n")

    try:
        # Simulate personal best event
        lap_data = {
            "circuit": "Blackwood GP",
            "time": 98.456,
            "vehicle": "XF GTI",
            "improvement": 0.234,
            "timestamp": datetime.now().isoformat(),
        }
        await system.on_personal_best(lap_data)

        await asyncio.sleep(2)

        # Simulate some telemetry updates
        for i in range(10):
            telemetry_data = {
                "speed": 120 + i * 5,
                "rpm": 6000 + i * 100,
                "gear": min(6, i // 2 + 1),
                "lap_time": i * 10.0,
                "position": "2/10",
            }
            system.update_telemetry(telemetry_data)
            await asyncio.sleep(0.5)

        # Simulate anomaly detection
        anomaly_data = {
            "type": "overheating",
            "severity": "warning",
            "description": "Engine temperature reached 110°C",
            "timestamp": datetime.now().isoformat(),
        }
        await system.on_anomaly_detected(anomaly_data)

        await asyncio.sleep(2)

        # Simulate session end
        session_data = {
            "circuit": "Blackwood GP",
            "total_laps": 25,
            "best_lap": 98.456,
            "duration": "45:30",
            "avg_lap": 99.234,
        }
        await system.on_session_end(session_data)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        system.shutdown()


if __name__ == "__main__":
    # Run the integrated example
    asyncio.run(main())
