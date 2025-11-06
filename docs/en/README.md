# LFS-Ayats

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

Prototype telemetry radar for Live for Speed (LFS).

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
