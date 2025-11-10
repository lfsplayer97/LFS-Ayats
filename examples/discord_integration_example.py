"""
Example: Using Discord Integration for Notifications

This example demonstrates how to use the Discord integration to send
notifications about lap times and session summaries.
"""

import asyncio
from datetime import datetime
from src.integrations import DiscordIntegration


async def main():
    """Main example function."""

    # Initialize Discord integration with your webhook URL
    # Get webhook URL from Discord: Server Settings -> Integrations -> Webhooks
    discord = DiscordIntegration(
        webhook_url="https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE"
    )

    # Example 1: Send a simple notification
    print("Sending simple notification...")
    await discord.send_notification("LFS-Ayats telemetry system is online!")

    # Example 2: Notify about a new personal best
    print("\nSending personal best notification...")
    lap_data = {
        "circuit": "Blackwood GP",
        "time": 98.456,
        "vehicle": "XF GTI",
        "improvement": 0.234,
        "timestamp": datetime.now().isoformat(),
    }
    await discord.notify_personal_best(lap_data)

    # Example 3: Send session summary
    print("\nSending session summary...")
    session_data = {
        "circuit": "Blackwood GP",
        "total_laps": 25,
        "best_lap": 98.456,
        "duration": "45:30",
        "avg_lap": 99.234,
    }
    await discord.notify_session_summary(session_data)

    # Example 4: Send anomaly alert
    print("\nSending anomaly alert...")
    anomaly_data = {
        "type": "overheating",
        "severity": "warning",
        "description": "Engine temperature reached 110°C",
        "timestamp": datetime.now().isoformat(),
    }
    await discord.notify_anomaly(anomaly_data)

    print("\nAll notifications sent!")


if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())
