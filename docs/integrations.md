# External Integrations Guide

This guide covers all external integrations available in LFS-Ayats for notifications, streaming, and cloud backup.

## Table of Contents

1. [Discord Integration](#discord-integration)
2. [Telegram Integration](#telegram-integration)
3. [Streaming Overlay](#streaming-overlay)
4. [Cloud Storage](#cloud-storage)
5. [Configuration](#configuration)
6. [Examples](#examples)

## Discord Integration

Send real-time notifications to Discord channels using webhooks.

### Setup

1. **Create a Webhook:**
   - Go to your Discord server settings
   - Navigate to: `Server Settings` → `Integrations` → `Webhooks`
   - Click `New Webhook`
   - Choose the channel and copy the webhook URL

2. **Configure:**
   ```yaml
   integrations:
     discord:
       enabled: true
       webhook_url: "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN"
       notifications:
         personal_best: true
         session_summary: true
         anomalies: true
   ```

### Features

- **Personal Best Notifications**: Automatically notify when a new personal best lap is achieved
- **Session Summaries**: Send detailed session statistics after completion
- **Anomaly Alerts**: Receive warnings about detected anomalies (overheating, etc.)
- **Rich Embeds**: Beautiful formatted messages with color-coding

### Usage

```python
from src.integrations import DiscordIntegration

discord = DiscordIntegration(webhook_url="https://discord.com/api/webhooks/...")

# Send a personal best notification
await discord.notify_personal_best({
    'circuit': 'Blackwood GP',
    'time': 98.456,
    'vehicle': 'XF GTI',
    'improvement': 0.234,
    'timestamp': datetime.now().isoformat()
})
```

See `examples/discord_integration_example.py` for complete examples.

## Telegram Integration

Send notifications and receive commands through a Telegram bot.

### Setup

1. **Create a Bot:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow the instructions
   - Save your bot token

2. **Get Your Chat ID:**
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - It will reply with your chat ID

3. **Configure:**
   ```yaml
   integrations:
     telegram:
       enabled: true
       bot_token: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
       chat_id: "123456789"
   ```

### Features

- **Text Messages**: Send formatted messages with HTML/Markdown
- **Photo Sharing**: Send telemetry charts and graphs
- **Personal Best Notifications**: Automatic notifications for improvements
- **Session Summaries**: Detailed statistics after each session

### Usage

```python
from src.integrations import TelegramIntegration

telegram = TelegramIntegration(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)

# Send a formatted message
await telegram.send_message(
    "<b>System Status:</b> ✅ Online\n"
    "<i>Drivers connected:</i> 8"
)

# Send a photo
await telegram.send_photo(
    photo_path="telemetry_chart.png",
    caption="📊 Session telemetry"
)
```

See `examples/telegram_integration_example.py` for complete examples.

## Streaming Overlay

Display real-time telemetry data in OBS Studio or other streaming software.

### Setup

1. **Start the Overlay Server:**
   ```python
   from src.integrations import StreamingOverlay
   
   overlay = StreamingOverlay(port=5000)
   overlay.start()
   ```

2. **Configure OBS Studio:**
   - Add a `Browser` source to your scene
   - Set URL to: `http://localhost:5000`
   - Set Width: `1920`, Height: `1080`
   - Enable `Shutdown source when not visible`
   - Adjust position and size as needed

3. **Configuration:**
   ```yaml
   integrations:
     streaming:
       enabled: true
       overlay_port: 5000
       update_rate: 10  # Hz
   ```

### Features

- **Real-Time Updates**: WebSocket-based updates at configurable rates
- **Customizable Display**: HTML/CSS template can be modified
- **Low Latency**: Minimal delay for live streaming
- **OBS Compatible**: Works with OBS Browser Source

### Displayed Data

- Speed (km/h)
- RPM
- Current gear
- Position in race
- Current lap time

### Usage

```python
overlay = StreamingOverlay(port=5000)
overlay.start()

# Update telemetry data
overlay.update_telemetry({
    'speed': 120.5,
    'rpm': 6500,
    'gear': 4,
    'lap_time': 98.456,
    'position': '2/10'
})
```

See `examples/streaming_overlay_example.py` for a complete example.

## Cloud Storage

Automatically backup telemetry data to Google Drive or Dropbox.

### Google Drive Setup

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable Google Drive API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download credentials JSON file

2. **Install Dependencies:**
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

3. **Configure:**
   ```yaml
   integrations:
     cloud_backup:
       enabled: true
       provider: google_drive
       auto_backup: true
       backup_interval: 3600  # seconds
       credentials_path: ./credentials.json
       folder_id: null  # Optional: specify folder ID
   ```

### Dropbox Setup

1. **Create Dropbox App:**
   - Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
   - Create a new app
   - Generate an access token

2. **Install Dependencies:**
   ```bash
   pip install dropbox
   ```

3. **Configure:**
   ```yaml
   integrations:
     cloud_backup:
       enabled: true
       provider: dropbox
       auto_backup: true
       backup_interval: 3600
       credentials_path: null  # Not needed for Dropbox
   ```

### Features

- **Automatic Backup**: Schedule regular backups of telemetry data
- **Manual Upload**: Upload specific sessions on demand
- **Multiple Formats**: Supports JSON, CSV, and other formats
- **Folder Organization**: Organize backups in cloud folders

### Usage

```python
from src.integrations import GoogleDriveIntegration

# Upload a single file
gdrive = GoogleDriveIntegration('./credentials.json')
file_id = gdrive.upload_session('session_data.json')

# Auto-backup all files
count = gdrive.auto_backup(
    './data/',
    folder_id='optional_folder_id',
    file_extensions=['.json', '.csv']
)
```

See `examples/cloud_storage_example.py` for complete examples.

## Configuration

### Complete Configuration Example

```yaml
integrations:
  # Discord notifications
  discord:
    enabled: true
    webhook_url: "${DISCORD_WEBHOOK_URL}"  # Use environment variable
    bot_token: null  # Optional: for bot commands
    notifications:
      personal_best: true
      session_summary: true
      anomalies: true
  
  # Telegram bot
  telegram:
    enabled: false
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
  
  # Streaming overlay
  streaming:
    enabled: false
    overlay_port: 5000
    update_rate: 10  # Hz
  
  # Cloud backup
  cloud_backup:
    enabled: false
    provider: google_drive  # or dropbox
    auto_backup: true
    backup_interval: 3600  # seconds (1 hour)
    credentials_path: ./credentials.json
    folder_id: null  # Optional Google Drive folder ID
```

### Environment Variables

For security, use environment variables for sensitive data:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
export TELEGRAM_CHAT_ID="123456789"
```

Then reference them in `config.yaml`:

```yaml
integrations:
  discord:
    webhook_url: "${DISCORD_WEBHOOK_URL}"
```

## Examples

### Complete Integrated System

See `examples/integrated_system_example.py` for a complete example showing how to use all integrations together.

```python
from src.integrations import (
    DiscordIntegration,
    TelegramIntegration,
    StreamingOverlay,
    GoogleDriveIntegration
)

# Initialize all integrations
discord = DiscordIntegration(webhook_url="...")
telegram = TelegramIntegration(bot_token="...", chat_id="...")
overlay = StreamingOverlay(port=5000)
overlay.start()

# On personal best
await discord.notify_personal_best(lap_data)
await telegram.notify_personal_best(lap_data)

# Update streaming overlay in real-time
overlay.update_telemetry(telemetry_data)

# Backup session at end
gdrive.upload_session('session_data.json')
```

### Individual Examples

- **Discord**: `examples/discord_integration_example.py`
- **Telegram**: `examples/telegram_integration_example.py`
- **Streaming**: `examples/streaming_overlay_example.py`
- **Cloud Storage**: `examples/cloud_storage_example.py`
- **Integrated System**: `examples/integrated_system_example.py`

## Troubleshooting

### Discord

- **Webhook Not Working**: Verify the webhook URL is correct and the bot has permission to post in the channel
- **No Notifications**: Check that notifications are enabled in config

### Telegram

- **Bot Not Responding**: Make sure you've started a conversation with the bot first
- **Wrong Chat ID**: Use [@userinfobot](https://t.me/userinfobot) to verify your chat ID

### Streaming Overlay

- **Not Loading in OBS**: Check that the port is not blocked by a firewall
- **No Updates**: Verify the `update_rate` in config and that telemetry data is being sent

### Cloud Storage

- **Google Drive Auth Error**: Re-run the OAuth flow to refresh credentials
- **Dropbox Upload Failed**: Verify your access token is valid and not expired

## API Reference

For detailed API documentation, see:
- `src/integrations/discord_integration.py`
- `src/integrations/telegram_integration.py`
- `src/integrations/streaming_overlay.py`
- `src/integrations/cloud_storage.py`

Each module contains comprehensive docstrings with usage examples.
