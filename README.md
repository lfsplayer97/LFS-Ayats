# LFS-Ayats: Live for Speed InSim Telemetry System

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/lfsplayer97/LFS-Ayats/actions/workflows/tests.yml/badge.svg)](https://github.com/lfsplayer97/LFS-Ayats/actions/workflows/tests.yml)
[![Code Quality](https://github.com/lfsplayer97/LFS-Ayats/actions/workflows/code-quality.yml/badge.svg)](https://github.com/lfsplayer97/LFS-Ayats/actions/workflows/code-quality.yml)
[![codecov](https://codecov.io/gh/lfsplayer97/LFS-Ayats/branch/main/graph/badge.svg)](https://codecov.io/gh/lfsplayer97/LFS-Ayats)

**A professional, modular telemetry collection system for Live for Speed racing simulator.**

A modular and complete system for collecting, processing, and visualizing telemetry data from the Live for Speed racing simulator using the InSim protocol.

## 📋 Description

This repository provides a professional implementation of the Live for Speed InSim protocol, enabling:

- **Connection and communication** with the LFS server via TCP/UDP sockets
- **Real-time telemetry collection** (speed, RPM, temperature, position, etc.)
- **InSim packet processing** with validation and error handling
- **Real-time data visualization** with interactive dashboards
- **Data export** to CSV, JSON, and database formats
- **REST API** for programmatic access and integration with other tools
- **WebSocket** for real-time telemetry streaming
- **Automated tests** to validate telemetry inputs/outputs

## 🏗️ Repository Structure

```
LFS-Ayats/
├── src/                          # Main source code
│   ├── api/                      # REST API (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Pydantic models
│   │   ├── dependencies.py      # Dependency injection
│   │   ├── middleware.py        # CORS and logging
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── routers/             # API endpoints
│   ├── connection/               # InSim connection module
│   │   ├── __init__.py
│   │   ├── insim_client.py      # InSim TCP/UDP client
│   │   └── packet_handler.py    # InSim packet handling
│   ├── telemetry/               # Telemetry module
│   │   ├── __init__.py
│   │   ├── collector.py         # Telemetry data collection
│   │   └── processor.py         # Data processing and validation
│   ├── database/                # Database module
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy models
│   │   └── repository.py        # Data access layer
│   ├── visualization/           # Visualization module
│   │   ├── __init__.py
│   │   ├── dashboard.py         # Real-time web dashboard (Dash)
│   │   ├── plots.py             # Analysis plots
│   │   ├── map_view.py          # Circuit map visualization
│   │   ├── comparator.py        # Lap comparison
│   │   └── components/          # Reusable components
│   ├── export/                  # Export module
│   │   ├── __init__.py
│   │   ├── csv_exporter.py     # CSV export
│   │   ├── json_exporter.py    # JSON export
│   │   └── db_exporter.py      # Database export
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py         # Application configuration
│   └── utils/                   # Common utilities
│       ├── __init__.py
│       └── logger.py           # Logging system
├── tests/                       # Automated tests
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test data
├── examples/                    # Usage examples
│   ├── basic_connection.py     # Basic connection
│   ├── telemetry_monitor.py   # Telemetry monitor
│   ├── data_logger.py         # Data logger
│   └── api_client_example.py  # REST API client
├── docs/                       # Documentation
│   ├── insim_protocol.md      # InSim protocol documentation
│   ├── packet_reference.md    # Packet reference
│   ├── api_reference.md       # API reference
│   ├── api_documentation.md   # REST API documentation
│   └── development.md         # Development guide
├── scripts/                    # Utility scripts
│   └── delete-branches.sh     # Branch management
├── .gitignore                 # Git ignored files
├── requirements.txt           # Python dependencies
├── setup.py                   # Package installation
├── pytest.ini                 # pytest configuration
└── README.md                  # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Live for Speed (demo or full version)
- pip (Python package manager)

### Installing Dependencies

```bash
# Clone the repository
git clone https://github.com/lfsplayer97/LFS-Ayats.git
cd LFS-Ayats

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## 📚 Complete Documentation

LFS-Ayats has extensive documentation for all user levels:

### 🚀 Getting Started

- **[Quick Start Guide](docs/quick-start.md)** - Get the system running in 5-10 minutes
- **[FAQ](docs/faq.md)** - Frequently asked questions and troubleshooting

### 🎓 Interactive Tutorials

| Tutorial | Description | Time | Level |
|----------|-------------|------|-------|
| **[01 - First Session](docs/tutorials/01-first-session.md)** | Collect and export basic telemetry | 30 min | Beginner |
| **[02 - Lap Analysis](docs/tutorials/02-lap-analysis.md)** | Compare laps and find improvements | 45 min | Intermediate |
| **[03 - Real-time Dashboard](docs/tutorials/03-real-time-dashboard.md)** | Create interactive web dashboard | 30 min | Intermediate |
| **[04 - Advanced Analysis](docs/tutorials/04-advanced-analysis.md)** | Machine learning and predictions | 60 min | Advanced |
| **[05 - Database](docs/tutorials/05-database-integration.md)** | Store historical data | 45 min | Advanced |

### 💡 Use Cases

- **[League Racing](docs/use-cases/league-racing.md)** - Configuration for leagues with multiple drivers
- **[Driver Coaching](docs/use-cases/driver-coaching.md)** - Data-driven coaching system

### 🏗️ Technical Documentation

- **[System Architecture](docs/architecture.md)** - Components and design patterns
- **[InSim Protocol](docs/insim_protocol.md)** - Communication protocol details
- **[REST API](docs/api_documentation.md)** - Complete API documentation
- **[API Reference](docs/api_reference.md)** - Class and method reference
- **[Visualization](docs/visualization.md)** - Charts and dashboards
- **[Analysis Module](docs/analysis_module.md)** - Advanced analysis

### 👨‍💻 For Developers

- **[Environment Setup](docs/contributing/development-setup.md)** - Setup for contributing
- **[Coding Standards](docs/contributing/coding-standards.md)** - Conventions and best practices
- **[Testing Guide](docs/contributing/testing-guide.md)** - Writing and running tests
- **[Contribution Guide](CONTRIBUTING.md)** - How to contribute to the project

**📖 [Complete Documentation Index](docs/README.md)**

## 📖 Basic Usage

### Connecting to LFS

```python
from src.connection import InSimClient
from src.telemetry import TelemetryCollector

# Create InSim client
client = InSimClient(
    host='127.0.0.1',
    port=29999,
    admin_password='',
    app_name='LFS-Ayats'
)

# Connect
client.connect()

# Create telemetry collector
collector = TelemetryCollector(client)

# Start data collection
collector.start()
```

### Data Export

```python
from src.export import CSVExporter, JSONExporter

# Export to CSV
csv_exporter = CSVExporter('telemetry_data.csv')
csv_exporter.export(telemetry_data)

# Export to JSON
json_exporter = JSONExporter('telemetry_data.json')
json_exporter.export(telemetry_data)
```

### REST API

The system includes a complete REST API built with FastAPI for programmatic access:

```bash
# Start the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Automatic Documentation:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

**Client usage example:**

```python
import requests

# List sessions
response = requests.get("http://localhost:8000/api/v1/sessions")
sessions = response.json()

# Get lap telemetry
response = requests.get("http://localhost:8000/api/v1/1/telemetry")
telemetry = response.json()

# WebSocket for real-time telemetry
import websockets
import asyncio

async def receive_telemetry():
    uri = "ws://localhost:8000/api/v1/telemetry/live"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print(f"Telemetry: {data}")

asyncio.run(receive_telemetry())
```

**Available endpoints:**
- `/api/v1/health` - Health check
- `/api/v1/sessions` - Session management
- `/api/v1/{lap_id}` - Lap information
- `/api/v1/telemetry/live` - WebSocket streaming
- `/api/v1/stats/best-laps` - Best laps
- `/api/v1/export/csv/{lap_id}` - CSV export
- and many more...

See [docs/api_documentation.md](docs/api_documentation.md) for complete API documentation.

## 🔌 External Integrations

LFS-Ayats offers integrations with external services for notifications, streaming, and automatic backup.

### Discord

Send automatic notifications to Discord channels:

```python
from src.integrations import DiscordIntegration

discord = DiscordIntegration(webhook_url="https://discord.com/api/webhooks/...")

# Notify personal best
await discord.notify_personal_best({
    'circuit': 'Blackwood GP',
    'time': 98.456,
    'vehicle': 'XF GTI',
    'improvement': 0.234
})
```

### Telegram

Send messages and images via a Telegram bot:

```python
from src.integrations import TelegramIntegration

telegram = TelegramIntegration(bot_token="YOUR_TOKEN", chat_id="YOUR_CHAT_ID")
await telegram.send_message("<b>System online!</b>")
```

### Streaming Overlay (OBS)

Display real-time telemetry in OBS Studio:

```python
from src.integrations import StreamingOverlay

overlay = StreamingOverlay(port=5000)
overlay.start()  # Access at http://localhost:5000

# Update telemetry data
overlay.update_telemetry({
    'speed': 120.5,
    'rpm': 6500,
    'gear': 4,
    'lap_time': 98.456
})
```

### Cloud Storage (Google Drive / Dropbox)

Automatic backup to Google Drive or Dropbox:

```python
from src.integrations import GoogleDriveIntegration

gdrive = GoogleDriveIntegration('./credentials.json')
gdrive.auto_backup('./data/', folder_id='optional_folder_id')
```

**Configuration:**

Add to `config.yaml`:

```yaml
integrations:
  discord:
    enabled: true
    webhook_url: "${DISCORD_WEBHOOK_URL}"
    notifications:
      personal_best: true
      session_summary: true
      anomalies: true
  
  telegram:
    enabled: false
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
  
  streaming:
    enabled: false
    overlay_port: 5000
    update_rate: 10  # Hz
  
  cloud_backup:
    enabled: false
    provider: google_drive
    auto_backup: true
    backup_interval: 3600  # seconds
    credentials_path: ./credentials.json
```

**Complete examples:**
- `examples/discord_integration_example.py`
- `examples/telegram_integration_example.py`
- `examples/streaming_overlay_example.py`
- `examples/cloud_storage_example.py`
- `examples/integrated_system_example.py`

See [docs/integrations.md](docs/integrations.md) for complete integration documentation.

### Real-time Visualization

```python
from src.visualization import TelemetryDashboard

# Create real-time web dashboard
dashboard = TelemetryDashboard(
    host='127.0.0.1',
    port=29999,
    update_interval=100  # update every 100ms
)

# Run the dashboard server
dashboard.run(debug=True, port=8050)
# Open browser at http://localhost:8050
```

### Lap Analysis and Comparison

```python
from src.visualization import (
    LapComparator,
    create_speed_vs_distance_plot,
    create_track_map,
    create_heatmap_plot
)

# Compare laps
comparator = LapComparator()
comparator.add_lap("Lap 1", lap1_telemetry)
comparator.add_lap("Lap 2", lap2_telemetry)

# Create comparison plots
fig = comparator.create_comparison_plot()
fig.write_html("lap_comparison.html")

# Create track map with speeds
track_fig = create_track_map(telemetry, show_speed_colors=True)
track_fig.write_html("track_map.html")

# Create heatmap
heatmap_fig = create_heatmap_plot(telemetry)
heatmap_fig.write_html("speed_heatmap.html")
```

For more information on visualization, see [docs/visualization.md](docs/visualization.md)

## 🧪 Automated Tests

The project includes comprehensive automated tests to ensure code quality:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/connection/
pytest tests/integration/
```

## 📚 InSim Protocol

InSim (Internet Simulator) is Live for Speed's communication protocol that allows external applications to interact with the simulator.

### Main InSim Packets

| Packet | Description | Usage |
|--------|-------------|-------|
| `IS_ISI` | InSim Init | Initialize InSim connection |
| `IS_VER` | Version | InSim protocol version |
| `IS_TINY` | Tiny | Small control packets |
| `IS_SMALL` | Small | Small data packets |
| `IS_MCI` | Multi Car Info | Multiple car information |
| `IS_NLP` | Node and Lap | Node and lap information |
| `IS_MSO` | Message Out | Server messages |
| `IS_III` | InSim Info | Server information |
| `IS_STA` | State | Server state |
| `IS_NCN` | New Connection | New player connection |
| `IS_CNL` | Connection Leave | Player disconnect |
| `IS_CPR` | Connection Player Rename | Player name change |
| `IS_NPL` | New Player | New player on track |
| `IS_PLP` | Player Leave | Player leaves track |
| `IS_PIT` | Pit Stop | Pit stop |
| `IS_PSF` | Pit Stop Finish | Pit stop finish |
| `IS_LAP` | Lap Time | Lap time |
| `IS_SPX` | Split Time | Sector time |
| `IS_PEN` | Penalty | Penalty |
| `IS_TOC` | Take Over Car | Car control change |
| `IS_FLG` | Flag | Flag |
| `IS_RES` | Result | Results |
| `IS_REO` | Reorder | Car reordering |
| `IS_BTN` | Button | Interface buttons |
| `IS_BFN` | Button Function | Button functions |
| `IS_AXI` | Autocross Info | Autocross information |
| `IS_RIP` | Replay Info | Replay information |

### Available Telemetry

Telemetry that can be collected includes:

- **Vehicle data**: speed, RPM, gear, steering angle
- **Engine data**: temperature, fuel consumption, force
- **Position data**: X/Y/Z coordinates, orientation, altitude
- **Lap data**: lap time, best time, sectors
- **Track data**: surface type, distance traveled
- **Player data**: name, team, car, setup
- **Events**: start, finish, pit stops, penalties

## 📖 References

### Official Documentation

- **LFS Manual**: https://en.lfsmanual.net/wiki/Main_Page
- **InSim Protocol**: https://en.lfsmanual.net/wiki/InSim.txt
- **Outgauge Protocol**: https://en.lfsmanual.net/wiki/OutGauge
- **Outsim Protocol**: https://en.lfsmanual.net/wiki/OutSim

### Additional Resources

- **LFS Forum**: https://www.lfs.net/forum
- **LFS World**: https://www.lfs.net/
- **Project Documentation**:
  - [Detailed InSim Protocol](docs/insim_protocol.md)
  - [Packet Reference](docs/packet_reference.md)
  - [System Architecture](docs/architecture.md)
  - [FAQ](docs/faq.md)
  - [Documentation Index](docs/README.md)
- **API Reference**: See `docs/api_reference.md`

## 🤝 Contributing

Contributions are welcome! If you want to contribute:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

### Developer Guides

To start contributing, see:

- **[Contribution Guide](CONTRIBUTING.md)** - Complete contribution process
- **[Environment Setup](docs/contributing/development-setup.md)** - Setup your environment
- **[Coding Standards](docs/contributing/coding-standards.md)** - Conventions to follow
- **[Testing Guide](docs/contributing/testing-guide.md)** - How to write and run tests

### Best Practices

- Follow PEP 8 coding conventions
- Write tests for all new features
- Document code with docstrings (Google style)
- Update documentation as needed
- Maintain modularity and separation of concerns

## 🔄 Continuous Integration

This project uses GitHub Actions for automated testing and quality checks:

### Workflows

- **Tests**: Runs on every push and PR to `main` and `develop`
  - Tests across Python 3.8, 3.9, 3.10, 3.11, 3.12
  - Generates coverage reports and uploads to Codecov
  - Must pass before merging

- **Code Quality**: Runs on every push and PR
  - Black formatting check
  - Flake8 linting
  - MyPy type checking
  - Bandit security scanning

- **Release**: Triggers on version tags (v*.*.*)
  - Runs full test suite
  - Builds Python package
  - Creates GitHub release with artifacts

### Pre-commit Hooks

Install pre-commit hooks for local development:

```bash
pip install pre-commit
pre-commit install
```

This will automatically check your code before each commit.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## ✨ Authors

- **lfsplayer97** - Main developer

## 🙏 Acknowledgments

- Scawen Roberts and the Live for Speed team for the simulator and InSim protocol
- The LFS community for documentation and support
- Contributors and beta testers

## 📞 Contact

For questions, suggestions, or issues, please open an issue on the GitHub repository.

---

**Note**: This project is under active development. Check the documentation and examples for more information on usage and available features.
