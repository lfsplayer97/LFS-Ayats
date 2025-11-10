"""
Example: Using Telegram Integration for Notifications

This example demonstrates how to use the Telegram integration to send
notifications and photos.
"""

import asyncio
from datetime import datetime
from src.integrations import TelegramIntegration


async def main():
    """Main example function."""

    # Initialize Telegram integration
    # 1. Create a bot via @BotFather on Telegram
    # 2. Get your bot token from BotFather
    # 3. Get your chat ID by messaging @userinfobot
    telegram = TelegramIntegration(
        bot_token="YOUR_BOT_TOKEN_HERE",  # e.g., "123456:ABC-DEF..."
        chat_id="YOUR_CHAT_ID_HERE",  # e.g., "123456789"
    )

    # Example 1: Send a simple message
    print("Sending simple message...")
    await telegram.send_message("LFS-Ayats telemetry system is online!")

    # Example 2: Send a message with HTML formatting
    print("\nSending formatted message...")
    await telegram.send_message(
        "<b>System Status:</b> ✅ Online\n"
        "<i>Server:</i> Blackwood GP\n"
        "<code>Drivers connected: 8</code>"
    )

    # Example 3: Notify about a new personal best
    print("\nSending personal best notification...")
    lap_data = {
        "circuit": "Blackwood GP",
        "time": 98.456,
        "vehicle": "XF GTI",
        "improvement": 0.234,
    }
    await telegram.notify_personal_best(lap_data)

    # Example 4: Send session summary
    print("\nSending session summary...")
    session_data = {
        "circuit": "Blackwood GP",
        "total_laps": 25,
        "best_lap": 98.456,
        "duration": "45:30",
        "avg_lap": 99.234,
    }
    await telegram.notify_session_summary(session_data)

    # Example 5: Send a photo (e.g., telemetry chart)
    # Uncomment and update the path to an actual image file
    # print("\nSending telemetry chart...")
    # await telegram.send_photo(
    #     photo_path="/path/to/telemetry_chart.png",
    #     caption="📊 Session telemetry analysis"
    # )

    print("\nAll notifications sent!")


if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())
