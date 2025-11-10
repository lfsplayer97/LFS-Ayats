"""
Tests for Discord integration
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from src.integrations.discord_integration import DiscordIntegration


@pytest.fixture
def discord_client():
    """Create Discord integration client for testing."""
    return DiscordIntegration(
        webhook_url="https://discord.com/api/webhooks/test/webhook",
        bot_token="test_token"
    )


@pytest.fixture
def sample_lap_data():
    """Sample lap data for testing."""
    return {
        'circuit': 'Blackwood GP',
        'time': 98.456,
        'vehicle': 'XF GTI',
        'improvement': 0.234,
        'timestamp': datetime.now().isoformat()
    }


@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        'circuit': 'Blackwood GP',
        'total_laps': 25,
        'best_lap': 98.456,
        'duration': '45:30',
        'avg_lap': 99.234
    }


@pytest.fixture
def sample_anomaly_data():
    """Sample anomaly data for testing."""
    return {
        'type': 'overheating',
        'severity': 'warning',
        'description': 'Engine temperature too high',
        'timestamp': datetime.now().isoformat()
    }


class TestDiscordIntegration:
    """Test cases for Discord integration."""
    
    def test_init(self, discord_client):
        """Test Discord client initialization."""
        assert discord_client.webhook_url == "https://discord.com/api/webhooks/test/webhook"
        assert discord_client.bot_token == "test_token"
    
    def test_init_without_bot_token(self):
        """Test initialization without bot token."""
        client = DiscordIntegration(webhook_url="https://test.com")
        assert client.webhook_url == "https://test.com"
        assert client.bot_token is None
    
    @pytest.mark.asyncio
    async def test_send_notification_success(self, discord_client):
        """Test successful notification sending."""
        with patch('src.integrations.discord_integration.aiohttp.ClientSession') as mock_session_class:
            # Create mock response
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            # Create mock session
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session
            
            result = await discord_client.send_notification("Test message")
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_send_notification_with_embed(self, discord_client):
        """Test notification sending with embed."""
        embed = {
            "title": "Test Title",
            "description": "Test Description",
            "color": 0x00ff00,
            "fields": [{"name": "Field1", "value": "Value1"}]
        }
        
        with patch('src.integrations.discord_integration.aiohttp.ClientSession') as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session
            
            result = await discord_client.send_notification("", embed=embed)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_send_notification_failure(self, discord_client):
        """Test notification sending failure."""
        with patch('src.integrations.discord_integration.aiohttp.ClientSession') as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 500
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session
            
            result = await discord_client.send_notification("Test message")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_send_notification_exception(self, discord_client):
        """Test notification sending with exception."""
        with patch('src.integrations.discord_integration.aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.side_effect = Exception("Network error")
            
            result = await discord_client.send_notification("Test message")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_notify_personal_best(self, discord_client, sample_lap_data):
        """Test personal best notification."""
        with patch('src.integrations.discord_integration.aiohttp.ClientSession') as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session
            
            result = await discord_client.notify_personal_best(sample_lap_data)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_notify_session_summary(self, discord_client, sample_session_data):
        """Test session summary notification."""
        with patch('src.integrations.discord_integration.aiohttp.ClientSession') as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session
            
            result = await discord_client.notify_session_summary(sample_session_data)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_notify_anomaly_warning(self, discord_client, sample_anomaly_data):
        """Test anomaly notification with warning severity."""
        with patch('src.integrations.discord_integration.aiohttp.ClientSession') as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session
            
            result = await discord_client.notify_anomaly(sample_anomaly_data)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_notify_anomaly_critical(self, discord_client):
        """Test anomaly notification with critical severity."""
        anomaly_data = {
            'type': 'crash',
            'severity': 'critical',
            'description': 'Critical system error',
            'timestamp': datetime.now().isoformat()
        }
        
        with patch('src.integrations.discord_integration.aiohttp.ClientSession') as mock_session_class:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session
            
            result = await discord_client.notify_anomaly(anomaly_data)
            
            assert result is True
