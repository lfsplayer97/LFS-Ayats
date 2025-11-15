# Changelog

All notable changes to LFS-Ayats will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite in English
  - Installation guide with OS-specific instructions
  - Troubleshooting guide for common issues
  - Beginner tutorial for InSim basics
  - Intermediate tutorial for advanced features
  - API usage examples with REST and WebSocket
- Documentation cross-references and navigation

### Changed
- Documentation structure reorganized for better accessibility
- Code examples updated with error handling best practices

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

---

## [0.1.0] - 2024

### Added
- **Core Features**
  - InSim protocol client with TCP/UDP support
  - Real-time telemetry collection system
  - Multi-car telemetry tracking (IS_MCI packets)
  - Lap time recording and analysis
  - Node and lap packet processing
  
- **Connection Module** (`src/connection/`)
  - `InSimClient` - TCP/UDP connection management
  - `PacketHandler` - InSim packet parsing and validation
  - Connection lifecycle management
  - Automatic reconnection support
  - Error handling and recovery
  
- **Telemetry Module** (`src/telemetry/`)
  - `TelemetryCollector` - Real-time data collection
  - `TelemetryProcessor` - Data validation and processing
  - Configurable history buffer
  - Callback system for event handling
  - Data filtering and validation
  
- **Visualization Module** (`src/visualization/`)
  - Real-time web dashboard using Dash/Plotly
  - Interactive telemetry graphs
  - Speed vs distance plots
  - Track map visualization
  - Lap comparison tools
  - Customizable dashboard components
  
- **Export Module** (`src/export/`)
  - CSV export functionality
  - JSON export functionality
  - Database export support
  - Configurable output formats
  - Automatic file naming
  
- **Database Module** (`src/database/`)
  - SQLAlchemy ORM models
  - Session management
  - Lap and telemetry point storage
  - Repository pattern for data access
  - SQLite and PostgreSQL support
  - Database migration support (Alembic)
  
- **API Module** (`src/api/`)
  - FastAPI REST API server
  - WebSocket support for real-time streaming
  - Session and lap endpoints
  - Statistics and analytics endpoints
  - Automatic API documentation (Swagger/ReDoc)
  - CORS support
  - Rate limiting
  
- **Configuration Module** (`src/config/`)
  - YAML-based configuration
  - Environment variable support
  - Settings validation
  - Example configuration file
  
- **Utilities** (`src/utils/`)
  - Colorlog-based logging system
  - Configurable log levels
  - File and console logging
  
- **Testing**
  - Comprehensive unit test suite (40+ tests)
  - Integration tests
  - Test coverage reporting (58% baseline)
  - Pytest configuration with markers
  - Mock objects for InSim testing
  
- **Documentation**
  - README with project overview
  - InSim protocol documentation
  - Packet reference guide
  - API reference
  - Development guide
  - Contributing guidelines
  - Code of conduct
  
- **Examples** (`examples/`)
  - Basic connection example
  - Telemetry monitor
  - Data logger
  - Dashboard example
  - API client example
  - Database integration
  - Analysis examples
  - Visualization examples
  
- **Development Tools**
  - Black code formatter configuration
  - Flake8 linter configuration
  - MyPy type checking
  - Pylint code quality checks
  - Pre-commit hooks support
  - Git workflow scripts

### Technical Details

**Supported Python Versions:**
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12 (tested)

**Key Dependencies:**
- `asyncio-dgram>=2.1.2` - Async UDP support
- `numpy>=1.24.0` - Numerical processing
- `pandas>=2.0.0` - Data manipulation
- `matplotlib>=3.7.0` - Plotting
- `plotly>=5.14.0` - Interactive visualizations
- `dash>=2.10.0` - Web dashboards
- `fastapi>=0.104.0` - REST API framework
- `uvicorn>=0.24.0` - ASGI server
- `websockets>=12.0` - WebSocket support
- `sqlalchemy>=2.0.0` - ORM
- `pyyaml>=6.0` - Configuration
- `colorlog>=6.7.0` - Logging

**Development Dependencies:**
- `pytest>=7.3.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-asyncio>=0.21.0` - Async test support
- `black>=23.3.0` - Code formatter
- `flake8>=6.0.0` - Linter
- `mypy>=1.3.0` - Type checker
- `pylint>=2.17.0` - Code quality

**System Requirements:**
- OS: Windows 10+, Linux (Ubuntu 20.04+), macOS 10.15+
- RAM: 2 GB minimum, 4 GB recommended
- Disk: 500 MB minimum
- Network: TCP port 29999 for InSim

**InSim Protocol Support:**
- Protocol version: Compatible with LFS 0.6V and newer
- Packet types supported:
  - IS_ISI - Initialize InSim
  - IS_VER - Version information
  - IS_MCI - Multi Car Info (telemetry)
  - IS_NLP - Node and Lap
  - IS_LAP - Lap time
  - IS_SPX - Split time
  - IS_STA - State
  - IS_MSO - Message out
  - Additional packet types (see documentation)

**Configuration Options:**
- InSim connection settings (host, port, password)
- Telemetry collection interval
- Data export formats and paths
- Database connection strings
- API server settings
- Logging configuration
- Integration settings (Discord, Telegram, etc.)

### Architecture

**Design Patterns:**
- Observer Pattern (callback system)
- Repository Pattern (database access)
- Factory Pattern (exporters)
- Strategy Pattern (packet handlers)
- Singleton Pattern (configuration)

**Performance Characteristics:**
- Telemetry collection: Up to 100 Hz
- Memory usage: ~50-200 MB (depends on history size)
- API response time: <50ms typical
- WebSocket latency: <10ms
- Database write performance: 1000+ points/second

### Known Limitations

- InSim only works during active LFS sessions (not in menus)
- Maximum 8 simultaneous InSim connections per LFS instance
- SQLite not recommended for high-concurrency scenarios
- UDP packet loss possible on unreliable networks
- Memory usage grows with telemetry history size

### Migration Guide

N/A - Initial release

---

## Version Numbering

LFS-Ayats follows [Semantic Versioning](https://semver.org/):

- **MAJOR version** (X.0.0): Incompatible API changes
- **MINOR version** (0.X.0): New features, backward compatible
- **PATCH version** (0.0.X): Bug fixes, backward compatible

**Pre-release versions:**
- **Alpha** (0.X.0-alpha.Y): Early development, unstable
- **Beta** (0.X.0-beta.Y): Feature complete, testing phase
- **RC** (0.X.0-rc.Y): Release candidate, final testing

---

## Change Categories

### Added
New features and functionality.

### Changed
Changes to existing functionality.

### Deprecated
Features that will be removed in future versions.

### Removed
Features that have been removed.

### Fixed
Bug fixes.

### Security
Security vulnerability fixes.

---

## How to Contribute

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting enhancements
- Submitting pull requests
- Code style and standards

---

## Links

- **Repository:** https://github.com/lfsplayer97/LFS-Ayats
- **Issues:** https://github.com/lfsplayer97/LFS-Ayats/issues
- **Discussions:** https://github.com/lfsplayer97/LFS-Ayats/discussions
- **Documentation:** [docs/README.md](README.md)
- **License:** [MIT License](../LICENSE)

---

## Release History Summary

| Version | Date | Type | Highlights |
|---------|------|------|------------|
| 0.1.0 | 2024 | Initial | First public release with core features |

---

**Note:** This changelog will be updated with each release. Check the repository for the latest changes.
