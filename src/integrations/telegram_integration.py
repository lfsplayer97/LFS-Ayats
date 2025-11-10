"""
Telegram Integration
Send messages and interact with Telegram bot API
"""

import aiohttp
from typing import Optional, Dict, Any
import os


class TelegramIntegration:
    """
    Telegram integration for sending notifications via bot API.

    This class provides methods to send text messages and photos to
    Telegram channels or users using the Telegram Bot API.

    Args:
        bot_token: Telegram bot token from BotFather
        chat_id: Default chat ID for sending messages

    Example:
        >>> telegram = TelegramIntegration(
        ...     bot_token="123456:ABC-DEF...",
        ...     chat_id="123456789"
        ... )
        >>> await telegram.send_message("Hello from LFS-Ayats!")

    Reference:
        https://core.telegram.org/bots/api
    """

    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram integration.

        Args:
            bot_token: Bot token from BotFather
            chat_id: Chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send_message(
        self, text: str, chat_id: Optional[str] = None, parse_mode: str = "HTML"
    ) -> bool:
        """
        Send text message to Telegram.

        Args:
            text: Message text to send
            chat_id: Optional chat ID (uses default if not provided)
            parse_mode: Message formatting (HTML or Markdown)

        Returns:
            True if successful, False otherwise

        Example:
            >>> await telegram.send_message("<b>Bold text</b> and normal text")
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/sendMessage"
                payload = {
                    "chat_id": chat_id or self.chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                }

                async with session.post(
                    url, json=payload, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200

        except Exception as e:
            print(f"Telegram send_message failed: {e}")
            return False

    async def send_photo(
        self,
        photo_path: str,
        caption: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> bool:
        """
        Send photo to Telegram.

        Args:
            photo_path: Path to photo file
            caption: Optional photo caption
            chat_id: Optional chat ID (uses default if not provided)

        Returns:
            True if successful, False otherwise

        Example:
            >>> await telegram.send_photo(
            ...     "telemetry_graph.png",
            ...     caption="Session telemetry"
            ... )
        """
        try:
            if not os.path.exists(photo_path):
                print(f"Photo file not found: {photo_path}")
                return False

            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/sendPhoto"

                with open(photo_path, "rb") as photo_file:
                    data = aiohttp.FormData()
                    data.add_field("chat_id", chat_id or self.chat_id)
                    data.add_field(
                        "photo", photo_file, filename=os.path.basename(photo_path)
                    )

                    if caption:
                        data.add_field("caption", caption)

                    async with session.post(
                        url, data=data, timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        return response.status == 200

        except Exception as e:
            print(f"Telegram send_photo failed: {e}")
            return False

    async def notify_personal_best(self, lap_data: Dict[str, Any]) -> bool:
        """
        Notify about new personal best lap time.

        Args:
            lap_data: Dictionary containing lap information

        Returns:
            True if notification sent successfully
        """
        message = (
            f"🏆 <b>New Personal Best!</b>\n\n"
            f"Circuit: {lap_data['circuit']}\n"
            f"Lap Time: {lap_data['time']:.3f}s\n"
            f"Vehicle: {lap_data['vehicle']}\n"
            f"Improvement: -{lap_data['improvement']:.3f}s"
        )

        return await self.send_message(message)

    async def notify_session_summary(self, session_data: Dict[str, Any]) -> bool:
        """
        Send session summary notification.

        Args:
            session_data: Dictionary containing session information

        Returns:
            True if notification sent successfully
        """
        message = (
            f"🏎️ <b>Session Summary</b>\n\n"
            f"Circuit: {session_data['circuit']}\n"
            f"Total Laps: {session_data['total_laps']}\n"
            f"Best Lap: {session_data['best_lap']:.3f}s\n"
            f"Duration: {session_data['duration']}\n"
            f"Average: {session_data['avg_lap']:.3f}s"
        )

        return await self.send_message(message)
