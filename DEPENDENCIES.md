# Dependencies Documentation

This document provides a comprehensive overview of all dependencies for the LFS-Ayats project.

## Python Version Requirement

**Minimum Python version: 3.10**

This is enforced in `pyproject.toml` with:
```toml
requires-python = ">=3.10"
```

## Runtime Dependencies

All runtime dependencies are specified in `pyproject.toml`:

```toml
dependencies = [
    "simpleaudio>=1.0",
]
```

### simpleaudio

- **Purpose**: Plays audio beeps for proximity alerts
- **Version**: 1.0 or higher
- **Platform notes**: 
  - On Linux, requires ALSA development libraries
  - Install with: `sudo apt-get install libasound2-dev` (Ubuntu/Debian)
  - The application gracefully falls back to silent mode if audio is unavailable

## Development Dependencies

Development dependencies are listed in `requirements-dev.txt`:

- **bandit** (>=1.7) - Security linter
- **black** (>=23.0) - Code formatter
- **flake8** (>=6.1) - Style checker
- **isort** (>=5.12) - Import sorter
- **mypy** (>=1.5) - Type checker
- **pylint** (>=3.0) - Code linter
- **pytest** (>=7.4) - Testing framework

## Standard Library Modules

The following modules are used but are part of Python's standard library and do NOT need to be installed separately:

### Python 3.10+ Standard Library
- `__future__` - Future statement definitions
- `array` - Efficient arrays of numeric values
- `asyncio` - Asynchronous I/O
- `base64` - Base64 encoding/decoding
- `contextlib` - Context manager utilities
- `dataclasses` - Data class decorator
- `datetime` - Date and time handling
- `hashlib` - Secure hashes and message digests
- `inspect` - Inspect live objects
- `ipaddress` - IP address manipulation
- `json` - JSON encoder and decoder
- `logging` - Logging facility
- `math` - Mathematical functions
- `pathlib` - Object-oriented filesystem paths
- `select` - I/O completion waiting
- `socket` - Low-level networking
- `sqlite3` - SQLite database
- `struct` - Binary data packing
- `sys` - System-specific parameters
- `threading` - Thread-based parallelism
- `time` - Time access and conversions
- `types` - Dynamic type creation
- `typing` - Type hints

## Installation

### End Users

```bash
# 1. Install system dependencies (Linux only)
sudo apt-get install libasound2-dev  # Ubuntu/Debian
sudo dnf install alsa-lib-devel      # Fedora/RHEL

# 2. Install the package
pip install -e .
```

### Developers

```bash
# 1. Install system dependencies (Linux only)
sudo apt-get install libasound2-dev  # Ubuntu/Debian

# 2. Install the package with dev dependencies
pip install -e .
pip install -r requirements-dev.txt

# 3. Run tests
pytest

# 4. Run linters
black --check src tests main.py
isort --check-only src tests main.py
flake8 src tests
pylint src
mypy src
bandit -c bandit.yaml -r src
```

## Why These Dependencies?

### Why is simpleaudio the only runtime dependency?

The project is designed to be lightweight and use Python's standard library wherever possible. The only external functionality needed is audio playback for proximity alerts, which `simpleaudio` provides in a cross-platform way.

### Why aren't threading, pathlib, dataclasses, etc. listed as dependencies?

These modules are part of Python's standard library starting from Python 3.10. When you install Python 3.10 or higher, these modules are automatically included. The `requires-python = ">=3.10"` constraint in `pyproject.toml` ensures users have a Python version that includes these modules.

### What about typing_extensions for Python < 3.10?

The project explicitly requires Python 3.10 or higher (`requires-python = ">=3.10"`), so `typing_extensions` is not needed. All typing features used are available in Python 3.10+.

## Dependency Verification

To verify all dependencies are correctly installed:

```bash
# Check Python version
python --version  # Should be 3.10 or higher

# Try importing the main dependencies
python -c "import simpleaudio; print('simpleaudio OK')"

# Try importing standard library modules
python -c "import threading, pathlib, dataclasses, json; print('stdlib OK')"

# Run the application
python main.py
```

## Troubleshooting

### simpleaudio fails to install on Linux

**Problem**: `fatal error: alsa/asoundlib.h: No such file or directory`

**Solution**: Install ALSA development libraries:
```bash
sudo apt-get install libasound2-dev  # Ubuntu/Debian
sudo dnf install alsa-lib-devel      # Fedora/RHEL
```

### Application runs but no audio

The application will automatically fall back to silent mode if `simpleaudio` cannot initialize the audio system. This is normal for:
- Headless servers without audio devices
- SSH sessions without audio forwarding
- Containers without audio support

The radar and telemetry features will still work normally.

## Updating Dependencies

### To update runtime dependencies

Edit `pyproject.toml` and modify the `dependencies` array, then:
```bash
pip install -e . --upgrade
```

### To update development dependencies

Edit `requirements-dev.txt`, then:
```bash
pip install -r requirements-dev.txt --upgrade
```

## Security Considerations

All dependencies are regularly checked for security vulnerabilities using:
- `bandit` for code security analysis
- GitHub Security Advisories for dependency vulnerabilities
- Dependabot for automated updates

See the CI configuration in `.github/workflows/ci.yml` for automated security checks.
