# LFS-Ayats

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

Prototype telemetry radar for Live for Speed (LFS).

## Requirements

- **Python**: 3.10 or higher
- **System dependencies** (Linux): ALSA development libraries for audio support
  - Ubuntu/Debian: `sudo apt-get install libasound2-dev`
  - Fedora/RHEL: `sudo dnf install alsa-lib-devel`
- **Python dependencies**: 
  - Runtime: `simpleaudio>=1.0` (installed automatically with pip)
  - Development: See `requirements-dev.txt`

All standard library modules (`threading`, `pathlib`, `dataclasses`, `json`, etc.) are included with Python 3.10+ and require no additional installation.

## Installation

### For End Users

1. **Install system dependencies** (Linux only):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libasound2-dev
   
   # Fedora/RHEL
   sudo dnf install alsa-lib-devel
   ```

2. **Install the package**:
   ```bash
   pip install -e .
   ```
   
   This will automatically install `simpleaudio` and make the project available.

### For Developers

1. **Install system dependencies** (Linux only - see above)

2. **Install the package with development dependencies**:
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

   This installs the project along with development tools:
   - `bandit` - Security linter
   - `black` - Code formatter
   - `flake8` - Style checker
   - `isort` - Import sorter
   - `mypy` - Type checker
   - `pylint` - Code linter
   - `pytest` - Testing framework

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Run linters**:
   ```bash
   black --check src tests main.py
   isort --check-only src tests main.py
   flake8 src tests
   pylint src
   mypy src
   bandit -c bandit.yaml -r src
   ```

## Version Management

This project follows [Semantic Versioning](https://semver.org/). The single source of truth for the version is `pyproject.toml`.

To synchronize versions across all configuration files:

```bash
make version-sync
```

To check if versions are synchronized:

```bash
make version-check
```

Alternatively, you can run the script directly:

```bash
python scripts/sync_version.py          # Synchronize versions
python scripts/sync_version.py --check  # Check only
```

## Quick Start

### Initial Configuration

Before the first run, copy the example configuration file:

```bash
cp config.example.json config.json
```

Then edit `config.json` to match your LFS installation.

> **Security Note:** The `config.json` file contains local configurations and should 
> not be shared in version control. Always use `config.example.json` as a reference 
> and copy it to `config.json` for your local configuration.

### InSim Configuration

- **Standard Port:** The default InSim port is `29999`. The `config.example.json` file 
  uses this port. If LFS is configured with a different port, adjust it in `config.json`.
- **Admin Password:** Leave `insim.admin_password` empty if you don't need administrator 
  privileges. If you need administrative access, set a secure password.

### Running

1. Enable OutSim and InSim in LFS, pointing OutSim to the port defined in `config.json`.
2. Review and adjust the values in `config.json` to match your local configuration.
3. Run the radar from the project root with **`python main.py`**.
4. Keep the terminal open: the client will wait for OutSim telemetry and continuously 
   display the ASCII radar until you press `Ctrl+C`.

For complete documentation, see [Catalan README](../ca/README.md).
