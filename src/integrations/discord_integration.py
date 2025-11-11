"""
Discord Integration
Send notifications and interact with Discord via webhooks
"""

import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime


class DiscordIntegration:
    """
    Discord integration for sending notifications via webhooks.

    This class provides methods to send notifications to Discord channels
    using webhooks for events like personal bests, session summaries, etc.

    Args:
        webhook_url: Discord webhook URL for sending messages
        bot_token: Optional Discord bot token for advanced features

    Example:
        >>> discord = DiscordIntegration(webhook_url="https://discord.com/api/webhooks/...")
        >>> await discord.notify_personal_best({
        ...     'circuit': 'Blackwood GP',
        ...     'time': 98.456,
        ...     'vehicle': 'XF GTI',
        ...     'improvement': 0.234,
        ...     'timestamp': datetime.now().isoformat()
        ... })
    """

    def __init__(self, webhook_url: str, bot_token: Optional[str] = None):
        """
        Initialize Discord integration.

        Args:
            webhook_url: Discord webhook URL
            bot_token: Optional bot token for advanced features
        """
        self.webhook_url = webhook_url
        self.bot_token = bot_token

    async def send_notification(
        self, message: str, embed: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification via webhook.

        Args:
            message: Text message to send
            embed: Optional embed object with rich formatting

        Returns:
            True if successful, False otherwise

        Raises:
            aiohttp.ClientError: If request fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"content": message}

                if embed:
                    # Convert dict to Discord embed format
                    embed_obj = {
                        "title": embed.get("title", ""),
                        "description": embed.get("description", ""),
                        "color": embed.get("color", 0x00FF00),
                        "fields": embed.get("fields", []),
                    }

                    if "timestamp" in embed:
                        embed_obj["timestamp"] = embed["timestamp"]

                    payload["embeds"] = [embed_obj]

                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    return response.status in (200, 204)

        except Exception as e:
            # Log error but don't raise to prevent integration failures
            # from affecting main application
            print(f"Discord notification failed: {e}")
            return False

    async def notify_personal_best(self, lap_data: Dict[str, Any]) -> bool:
        """
        Notify about new personal best lap time.

        Args:
            lap_data: Dictionary containing lap information
                - circuit: Circuit name
                - time: Lap time in seconds
                - vehicle: Vehicle name
                - improvement: Time improvement in seconds
                - timestamp: ISO format timestamp

        Returns:
            True if notification sent successfully

        Example:
            >>> await discord.notify_personal_best({
            ...     'circuit': 'Blackwood GP',
            ...     'time': 98.456,
            ...     'vehicle': 'XF GTI',
            ...     'improvement': 0.234,
            ...     'timestamp': datetime.now().isoformat()
            ... })
        """
        embed = {
            "title": "🏆 New Personal Best!",
            "description": f"Circuit: {lap_data['circuit']}",
            "color": 0x00FF00,
            "fields": [
                {
                    "name": "Lap Time",
                    "value": f"{lap_data['time']:.3f}s",
                    "inline": True,
                },
                {"name": "Vehicle", "value": lap_data["vehicle"], "inline": True},
                {
                    "name": "Improvement",
                    "value": f"-{lap_data['improvement']:.3f}s",
                    "inline": True,
                },
            ],
            "timestamp": lap_data.get("timestamp", datetime.now().isoformat()),
        }

        return await self.send_notification("", embed=embed)

    async def notify_session_summary(self, session_data: Dict[str, Any]) -> bool:
        """
        Send session summary notification.

        Args:
            session_data: Dictionary containing session information
                - circuit: Circuit name
                - total_laps: Number of laps completed
                - best_lap: Best lap time in seconds
                - duration: Session duration string
                - avg_lap: Average lap time in seconds

        Returns:
            True if notification sent successfully

        Example:
            >>> await discord.notify_session_summary({
            ...     'circuit': 'Blackwood GP',
            ...     'total_laps': 25,
            ...     'best_lap': 98.456,
            ...     'duration': '45:30',
            ...     'avg_lap': 99.234
            ... })
        """
        embed = {
            "title": "🏎️ Session Summary",
            "description": f"Circuit: {session_data['circuit']}",
            "color": 0x3498DB,
            "fields": [
                {
                    "name": "Total Laps",
                    "value": str(session_data["total_laps"]),
                    "inline": True,
                },
                {
                    "name": "Best Lap",
                    "value": f"{session_data['best_lap']:.3f}s",
                    "inline": True,
                },
                {"name": "Duration", "value": session_data["duration"], "inline": True},
                {
                    "name": "Average",
                    "value": f"{session_data['avg_lap']:.3f}s",
                    "inline": True,
                },
            ],
        }

        return await self.send_notification("", embed=embed)

    async def notify_anomaly(self, anomaly_data: Dict[str, Any]) -> bool:
        """
        Send anomaly detection notification.

        Args:
            anomaly_data: Dictionary containing anomaly information
                - type: Type of anomaly detected
                - severity: Severity level (warning, error, critical)
                - description: Description of the anomaly
                - timestamp: ISO format timestamp

        Returns:
            True if notification sent successfully
        """
        severity_colors = {
            "warning": 0xFFA500,  # Orange
            "error": 0xFF6B6B,  # Red
            "critical": 0xFF0000,  # Dark red
        }

        severity_emoji = {"warning": "⚠️", "error": "❌", "critical": "🚨"}

        severity = anomaly_data.get("severity", "warning")

        embed = {
            "title": f"{severity_emoji.get(severity, '⚠️')} Anomaly Detected",
            "description": anomaly_data["description"],
            "color": severity_colors.get(severity, 0xFFA500),
            "fields": [
                {"name": "Type", "value": anomaly_data["type"], "inline": True},
                {"name": "Severity", "value": severity.capitalize(), "inline": True},
            ],
            "timestamp": anomaly_data.get("timestamp", datetime.now().isoformat()),
        }

        return await self.send_notification("", embed=embed)
