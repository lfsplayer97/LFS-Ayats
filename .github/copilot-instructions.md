# LFS-Ayats: Repository Custom Instructions

## Repository Overview

LFS-Ayats is a professional Python-based telemetry system for Live for Speed (LFS) racing simulator using the InSim protocol. The project enables real-time data collection, processing, visualization, and export of telemetry data from LFS servers.

- **Project Type**: Python package (modular telemetry system)
- **Primary Language**: Python 3.8+ (tested with Python 3.12.3)
- **Package Name**: lfs-ayats (version 0.1.0)
- **Repository Size**: ~15 Python source files across 6 main modules
- **Test Coverage**: 40 unit tests with 58% code coverage
- **Main Features**: InSim protocol communication, telemetry collection, data processing, visualization (Dash/Plotly), CSV/JSON export

## Architecture & Project Layout

### Directory Structure
```
LFS-Ayats/
├── src/                           # Source code (package root)
│   ├── __init__.py               # Package initialization
│   ├── connection/               # InSim protocol client
│   │   ├── insim_client.py      # TCP/UDP client (147 lines, 76% coverage)
│   │   └── packet_handler.py    # Packet parsing (113 lines, 66% coverage)
│   ├── telemetry/               # Data collection and processing
│   │   ├── collector.py         # Telemetry collector (132 lines, 29% coverage)
│   │   └── processor.py         # Data validation/processing (78 lines, 91% coverage)
│   ├── export/                  # Data export modules
│   │   ├── csv_exporter.py      # CSV export (46 lines, 87% coverage)
│   │   └── json_exporter.py     # JSON export (54 lines, 18% coverage)
│   ├── visualization/           # Real-time dashboards (Dash/Plotly)
│   ├── config/                  # Configuration management (YAML)
│   │   └── settings.py          # Settings loader (94 lines)
│   └── utils/                   # Utilities (logging, helpers)
│       └── logger.py            # Colorlog-based logger
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests (organized by module)
│   │   ├── connection/          # Connection tests (11 tests)
│   │   ├── telemetry/           # Telemetry tests (11 tests)
│   │   └── export/              # Export tests (6 tests)
│   └── integration/             # Integration tests
├── docs/                        # Documentation
│   ├── insim_protocol.md        # InSim protocol documentation
│   ├── packet_reference.md      # Packet structure reference
│   ├── api_reference.md         # API documentation
│   └── development.md           # Developer guide
├── examples/                    # Usage examples
│   ├── basic_connection.py      # Basic InSim connection
│   ├── telemetry_monitor.py    # Real-time monitoring
│   └── data_logger.py           # Data logging example
├── scripts/                     # Utility scripts
│   └── delete-branches.sh       # Branch cleanup script
├── setup.py                     # Package setup configuration
├── requirements.txt             # All dependencies (dev + prod)
├── pytest.ini                   # Pytest configuration
├── config.example.yaml          # Example configuration file
└── .gitignore                   # Standard Python gitignore
```

## Build, Test & Development Workflow

### Environment Setup

**ALWAYS follow these steps in order:**

1. **Install dependencies** (REQUIRED before any other operation):
   ```bash
   pip install -r requirements.txt
   ```
   - Includes ALL dependencies (dev, test, prod)
   - Takes ~60-120 seconds
   - Required packages: numpy, pandas, matplotlib, plotly, dash, pytest, black, flake8, mypy, pylint

2. **Install package in development mode** (REQUIRED after dependency install):
   ```bash
   pip install -e .
   ```
   - Makes `src/` modules importable
   - Creates entry point: `lfs-ayats` command
   - Takes ~30-60 seconds

### Testing

**Test commands (in order of frequency):**

```bash
# Run all tests (ALWAYS run before committing)
pytest

# Run with coverage report (recommended for validation)
pytest --cov=src --cov-report=html
# Coverage report: htmlcov/index.html
# Current baseline: 58% coverage

# Run specific test categories
pytest tests/unit/connection/        # Connection tests
pytest tests/unit/telemetry/         # Telemetry tests  
pytest tests/unit/export/            # Export tests
pytest tests/integration/            # Integration tests

# Run tests with markers
pytest -m unit                       # Unit tests only
pytest -m integration                # Integration tests only
pytest -m network                    # Network-dependent tests
pytest -m slow                       # Slow tests

# Verbose output
pytest -v                            # Verbose
pytest -vv                           # Extra verbose
pytest --tb=short                    # Short traceback
```

**Test execution time**: ~0.4-0.5 seconds for full suite (40 tests)

**Test framework configuration**: See `pytest.ini` for markers, coverage settings, and options.

### Code Quality & Linting

**ALWAYS run these tools before committing:**

```bash
# Format code (automatically fixes formatting)
black src/ tests/
# Uses PEP 8 style, line length 88 (default)

# Check code style (reports issues)
flake8 src/ tests/
# Enforces PEP 8, checks for common errors

# Type checking (static analysis)
mypy src/
# Checks type hints consistency

# Linting (comprehensive checks)
pylint src/
# Code quality, potential bugs, style issues
```

**Note**: No linting failures in baseline code. All tools should pass cleanly.

### Common Build Issues & Workarounds

1. **Import errors**: Always run `pip install -e .` after cloning or changing dependencies
2. **Module not found**: Ensure you're in the repository root and venv is activated
3. **Test failures**: Check if dependencies are installed (`pip list | grep -E "pytest|numpy|pandas"`)
4. **Coverage report not generated**: Install `pytest-cov` package

## Key Dependencies & Versions

### Core Dependencies (production)
- `asyncio-dgram>=2.1.2` - Async UDP communication
- `numpy>=1.24.0` - Numerical processing
- `pandas>=2.0.0` - Data manipulation
- `matplotlib>=3.7.0` - Plotting
- `plotly>=5.14.0` - Interactive plots
- `dash>=2.10.0` - Web dashboards
- `pyyaml>=6.0` - Configuration files
- `colorlog>=6.7.0` - Colored logging
- `sqlalchemy>=2.0.0` - Database support (optional)

### Development Dependencies
- `pytest>=7.3.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-mock>=3.10.0` - Mocking utilities
- `black>=23.3.0` - Code formatter
- `flake8>=6.0.0` - Linter
- `mypy>=1.3.0` - Type checker
- `pylint>=2.17.0` - Code quality

**Python version**: Requires Python 3.8+, tested with Python 3.12.3

## Code Style & Conventions

### Python Style (PEP 8)
- **Classes**: `PascalCase` (e.g., `InSimClient`, `TelemetryProcessor`)
- **Functions/methods**: `snake_case` (e.g., `send_packet`, `process_telemetry`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_SPEED`, `DEFAULT_PORT`)
- **Private members**: `_leading_underscore` (e.g., `_internal_method`)
- **Formatting**: Use Black formatter (line length 88)

### Docstrings (Google Style)
All public functions, classes, and modules MUST have docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Detailed description if needed. Include references to InSim.txt
    when implementing protocol features.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
        ConnectionError: When connection fails
    
    Example:
        >>> function_name("test", 42)
        True
        
    Reference:
        https://en.lfsmanual.net/wiki/InSim.txt#IS_PACKET
    """
```

### Type Hints
Use type hints for all function signatures:

```python
from typing import List, Optional, Dict, Any

def process_data(
    data: List[CarTelemetry],
    filter_speed: Optional[float] = None
) -> Dict[str, Any]:
    """Process telemetry data."""
    pass
```

## InSim Protocol Specifics

### Key InSim Concepts
- **InSim**: Internet Simulator protocol for LFS communication
- **Packets**: Binary data structures (min 4 bytes: size, type, reqId, sub)
- **Connection**: TCP (default port 29999) or UDP
- **Initialization**: Send `IS_ISI` packet, receive `IS_VER` response

### Common Packet Types
- `IS_ISI` (1): Initialize InSim connection
- `IS_VER` (2): Version information
- `IS_MCI` (38): Multi Car Info (telemetry data)
- `IS_NLP` (37): Node and Lap packet
- `IS_MSO` (11): Message Out
- `IS_STA` (6): Server state

### Adding New Packet Support
When implementing a new packet type:

1. Consult official documentation: https://en.lfsmanual.net/wiki/InSim.txt
2. Add packet type to `PacketType` enum in `src/connection/insim_client.py`
3. Implement parser in `src/connection/packet_handler.py`
4. Add unit tests with mock packet data in `tests/unit/connection/`
5. Include reference URL in docstring

### Telemetry Data Units
- Speed: km/h (from m/s * 3.6)
- RPM: revolutions per minute
- Temperature: Celsius
- Position: game units (X, Y, Z coordinates)
- Time: milliseconds or seconds (context-dependent)

## Testing Guidelines

### Test Structure
```python
import pytest
from src.module import MyClass

class TestMyClass:
    """Test cases for MyClass."""
    
    @pytest.fixture
    def instance(self):
        """Create MyClass instance for testing."""
        return MyClass()
    
    def test_basic_functionality(self, instance):
        """Test basic functionality."""
        result = instance.method()
        assert result is not None
    
    def test_error_handling(self, instance):
        """Test error handling."""
        with pytest.raises(ValueError):
            instance.invalid_method()
```

### Test Markers
Use markers to categorize tests (defined in `pytest.ini`):
- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.network` - Requires network/LFS server
- `@pytest.mark.slow` - Long-running tests

### Coverage Expectations
- Aim for >80% coverage on new code
- Current baseline: 58% overall
- Critical modules (processor.py): 91% coverage
- Acceptable lower coverage for UI/visualization modules

## Configuration

### Configuration File
- Location: `config.example.yaml` (example), `config.yaml` (user config, gitignored)
- Format: YAML
- Sections: connection, telemetry, export, visualization, logging
- Loaded by: `src/config/settings.py`

### Default Connection Settings
- Host: `127.0.0.1`
- Port: `29999` (standard InSim port)
- Protocol: TCP (UDP optional)
- Timeout: 5.0 seconds
- App name: Max 16 characters

## Validation & CI/CD

**Note**: No GitHub Actions workflows are currently configured.

### Pre-commit Validation
Before committing, ALWAYS run:
```bash
# 1. Format code
black src/ tests/

# 2. Run linters
flake8 src/ tests/
mypy src/

# 3. Run tests with coverage
pytest --cov=src

# 4. Verify coverage report
# Target: maintain or improve 58% baseline
```

### Manual Validation
When making changes:
1. Run relevant test subset first (e.g., `pytest tests/unit/connection/`)
2. Fix any failures before running full test suite
3. Check coverage report for new code
4. Manually test with examples if changing core functionality

## Important Files & References

### Key Source Files
- `src/connection/insim_client.py` - Main InSim client implementation
- `src/connection/packet_handler.py` - Packet parsing logic
- `src/telemetry/processor.py` - Data validation and processing (highest coverage)
- `src/config/settings.py` - Configuration management

### Documentation Files
- `README.md` - Main project documentation (265 lines)
- `CONTRIBUTING.md` - Contribution guidelines (300 lines)
- `docs/insim_protocol.md` - InSim protocol details
- `docs/development.md` - Developer guide (430 lines)

### Configuration Files
- `setup.py` - Package metadata and entry points
- `requirements.txt` - All dependencies (42 lines)
- `pytest.ini` - Test configuration with markers
- `.gitignore` - Ignores: `__pycache__/`, `venv/`, `.pytest_cache/`, `htmlcov/`, `*.log`, `*.db`, `*.zip`

## Special Notes & Gotchas

### Module Imports
- Use absolute imports: `from src.connection import InSimClient`
- Package is installed as: `import lfs_ayats` or `from src import ...`

### Network Testing
- Tests use mocking for network operations (no real LFS server needed)
- Use `@pytest.mark.network` for tests requiring actual LFS connection
- Mock server example available in `docs/development.md`

### Async Code
- Some modules use `asyncio` for async I/O
- Use `@pytest.mark.asyncio` for async test functions
- Use `asyncio-dgram` for UDP async operations

### Binary Packet Handling
- InSim packets are binary (use `struct.pack/unpack`)
- Packet structure: `struct.pack("=4B", size, type, reqId, sub)`
- Always validate packet size before unpacking

### Performance Considerations
- Telemetry data arrives at high frequency (10-100Hz typical)
- Use efficient data structures (numpy arrays, pandas DataFrames)
- Consider memory limits when storing history (default: 10000 samples)

## Common Development Tasks

### Adding a New Module
1. Create module directory under `src/`
2. Add `__init__.py` with public API exports
3. Implement main functionality with type hints and docstrings
4. Create test directory under `tests/unit/`
5. Write comprehensive unit tests (aim for >80% coverage)
6. Update `README.md` if module is user-facing
7. Add usage example to `examples/` if applicable

### Adding a New Packet Type
1. Reference: https://en.lfsmanual.net/wiki/InSim.txt
2. Update `PacketType` enum in `insim_client.py`
3. Add parser method in `packet_handler.py`
4. Include URL reference in docstring
5. Add unit test with mock packet data
6. Document packet structure in code comments

### Debugging Connection Issues
1. Enable DEBUG logging: `logger.setLevel(logging.DEBUG)`
2. Use packet inspection utility (see `docs/development.md`)
3. Verify LFS is running with InSim enabled (`/insim 29999`)
4. Check firewall settings for port 29999
5. Test with mock server for isolation

## Trust These Instructions

These instructions have been validated against the actual repository structure and test suite. When working on this codebase:

1. **Follow the build order**: Dependencies → Package install → Tests
2. **Run tests frequently**: Fast test suite (~0.4s) enables quick feedback
3. **Use type hints**: Already established pattern throughout codebase
4. **Reference InSim.txt**: Always link to official docs when implementing protocol features
5. **Maintain test coverage**: Current baseline is 58%, aim to maintain or improve

Only perform additional searches if:
- Information here is incomplete or contradicts actual code
- Working on undocumented areas (e.g., visualization module)
- Implementing entirely new functionality not covered here
- Debugging specific issues not covered in common problems section

These instructions are accurate as of the current repository state and should significantly reduce exploration time.
