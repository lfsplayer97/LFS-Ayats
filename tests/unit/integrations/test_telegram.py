"""
Tests for Telegram integration
"""

import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from src.integrations.telegram_integration import TelegramIntegration


@pytest.fixture
def telegram_client():
    """Create Telegram integration client for testing."""
    return TelegramIntegration(
        bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11", chat_id="123456789"
    )


@pytest.fixture
def sample_lap_data():
    """Sample lap data for testing."""
    return {
        "circuit": "Blackwood GP",
        "time": 98.456,
        "vehicle": "XF GTI",
        "improvement": 0.234,
    }


@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "circuit": "Blackwood GP",
        "total_laps": 25,
        "best_lap": 98.456,
        "duration": "45:30",
        "avg_lap": 99.234,
    }


class TestTelegramIntegration:
    """Test cases for Telegram integration."""

    def test_init(self, telegram_client):
        """Test Telegram client initialization."""
        assert telegram_client.bot_token == "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        assert telegram_client.chat_id == "123456789"
        assert "https://api.telegram.org/bot" in telegram_client.api_base_url

    @pytest.mark.asyncio
    async def test_send_message_success(self, telegram_client):
        """Test successful message sending."""
        with patch(
            "src.integrations.telegram_integration.aiohttp.ClientSession"
        ) as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()

            mock_session.post = MagicMock(return_value=mock_response)

            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            result = await telegram_client.send_message("Test message")

            assert result is True

    @pytest.mark.asyncio
    async def test_send_message_with_custom_chat_id(self, telegram_client):
        """Test message sending with custom chat ID."""
        with patch(
            "src.integrations.telegram_integration.aiohttp.ClientSession"
        ) as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()

            mock_session.post = MagicMock(return_value=mock_response)

            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            result = await telegram_client.send_message("Test", chat_id="987654321")

            assert result is True

    @pytest.mark.asyncio
    async def test_send_message_failure(self, telegram_client):
        """Test message sending failure."""
        with patch(
            "src.integrations.telegram_integration.aiohttp.ClientSession"
        ) as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 400
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()

            mock_session.post = MagicMock(return_value=mock_response)

            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            result = await telegram_client.send_message("Test message")

            assert result is False

    @pytest.mark.asyncio
    async def test_send_message_exception(self, telegram_client):
        """Test message sending with exception."""
        with patch(
            "src.integrations.telegram_integration.aiohttp.ClientSession"
        ) as mock_session:
            mock_session.return_value.__aenter__.side_effect = Exception(
                "Network error"
            )

            result = await telegram_client.send_message("Test message")

            assert result is False

    @pytest.mark.asyncio
    async def test_send_photo_success(self, telegram_client):
        """Test successful photo sending."""
        test_photo = "/tmp/test_photo.png"

        # Create a temporary file
        with open(test_photo, "w") as f:
            f.write("test image content")

        try:
            with patch(
                "src.integrations.telegram_integration.aiohttp.ClientSession"
            ) as mock_session_class:
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)

                mock_session = MagicMock()

                mock_session.post = MagicMock(return_value=mock_response)

                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock(return_value=None)

                mock_session_class.return_value = mock_session

                result = await telegram_client.send_photo(
                    test_photo, caption="Test photo"
                )

                assert result is True
        finally:
            # Clean up
            if os.path.exists(test_photo):
                os.remove(test_photo)

    @pytest.mark.asyncio
    async def test_send_photo_file_not_found(self, telegram_client):
        """Test photo sending when file doesn't exist."""
        result = await telegram_client.send_photo("/nonexistent/photo.png")

        assert result is False

    @pytest.mark.asyncio
    async def test_send_photo_exception(self, telegram_client):
        """Test photo sending with exception."""
        test_photo = "/tmp/test_photo2.png"

        # Create a temporary file
        with open(test_photo, "w") as f:
            f.write("test")

        try:
            with patch(
                "src.integrations.telegram_integration.aiohttp.ClientSession"
            ) as mock_session:
                mock_session.return_value.__aenter__.side_effect = Exception(
                    "Network error"
                )

                result = await telegram_client.send_photo(test_photo)

                assert result is False
        finally:
            if os.path.exists(test_photo):
                os.remove(test_photo)

    @pytest.mark.asyncio
    async def test_notify_personal_best(self, telegram_client, sample_lap_data):
        """Test personal best notification."""
        with patch(
            "src.integrations.telegram_integration.aiohttp.ClientSession"
        ) as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()

            mock_session.post = MagicMock(return_value=mock_response)

            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            result = await telegram_client.notify_personal_best(sample_lap_data)

            assert result is True

    @pytest.mark.asyncio
    async def test_notify_session_summary(self, telegram_client, sample_session_data):
        """Test session summary notification."""
        with patch(
            "src.integrations.telegram_integration.aiohttp.ClientSession"
        ) as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()

            mock_session.post = MagicMock(return_value=mock_response)

            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            result = await telegram_client.notify_session_summary(sample_session_data)

            assert result is True
