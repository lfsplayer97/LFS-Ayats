# Installation Guide

Complete installation guide for LFS-Ayats telemetry system for Live for Speed.

## Overview

This guide provides step-by-step instructions for installing LFS-Ayats on different operating systems. The installation process takes approximately 5-10 minutes.

## Prerequisites

Before installing LFS-Ayats, ensure you have the following:

### Required Software

- **Python 3.8 or higher** (tested with Python 3.8-3.12)
- **pip** (Python package manager, usually included with Python)
- **Live for Speed** (demo or full version)
- **Git** (optional, for cloning the repository)

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 2 GB | 4 GB+ |
| Disk Space | 500 MB | 1 GB+ |
| Network | TCP port 29999 | - |

### Supported Operating Systems

- ✅ **Windows** 10/11 (64-bit)
- ✅ **Linux** (Ubuntu 20.04+, Debian, Fedora, Arch)
- ✅ **macOS** 10.15+ (Catalina or newer)

## Installation Steps

### Step 1: Install Python

#### Windows

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip
python3 --version
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
python --version
```

#### macOS

**Using Homebrew (recommended):**
```bash
brew install python@3.11
python3 --version
```

**Or download from [python.org](https://www.python.org/downloads/macos/)**

### Step 2: Download LFS-Ayats

#### Option A: Clone with Git (Recommended)

```bash
# Clone the repository
git clone https://github.com/lfsplayer97/LFS-Ayats.git
cd LFS-Ayats
```

#### Option B: Download ZIP

1. Go to [LFS-Ayats Repository](https://github.com/lfsplayer97/LFS-Ayats)
2. Click **Code** → **Download ZIP**
3. Extract the ZIP file to your desired location
4. Open terminal/command prompt in the extracted folder

### Step 3: Create Virtual Environment

Creating a virtual environment isolates project dependencies from your system Python installation.

#### Windows

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt
```

#### Linux/macOS

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 4: Install Dependencies

With the virtual environment activated:

```bash
# Upgrade pip (recommended)
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install approximately 40+ packages
# Expected time: 2-5 minutes depending on internet speed
```

**Expected output:**
```
Collecting asyncio-dgram>=2.1.2
Collecting numpy>=1.24.0
Collecting pandas>=2.0.0
...
Successfully installed asyncio-dgram-2.1.2 numpy-1.26.0 pandas-2.1.0 ...
```

### Step 5: Install Package in Development Mode

**⚠️ CRITICAL STEP - Do not skip this!**

```bash
# Install LFS-Ayats as editable package
pip install -e .
```

**What this does:**
- Installs the package in "editable" or "development" mode
- Makes the `src` module importable throughout your code
- Creates a symbolic link to your source code
- Allows changes to be reflected immediately without reinstalling

**Why is this needed?**

Without this step, Python cannot import modules from `src/`:
```python
# Without 'pip install -e .', this fails:
from src.connection import InSimClient  # ❌ ModuleNotFoundError
```

After installation, imports work correctly:
```python
from src.connection import InSimClient  # ✅ Works!
```

**Verification:**

```bash
# Check package is installed
pip show lfs-ayats

# Should display:
# Name: lfs-ayats
# Version: 0.1.0
# Location: <path>/LFS-Ayats/src
# Editable project location: <path>/LFS-Ayats/src

# Test import
python -c "import src; print('✓ Installation successful')"
```

**Expected output:**
```
✓ Installation successful
```

If you see `ModuleNotFoundError`, the installation failed. See [Troubleshooting](#troubleshooting-installation).

### Step 6: Configure LFS-Ayats

```bash
# Copy example configuration
cp config.example.yaml config.yaml

# Edit configuration if needed (optional)
# Default settings work for local LFS installation
```

**Default configuration:**
- Host: `127.0.0.1` (localhost)
- Port: `29999` (standard InSim port)
- No admin password required

### Step 7: Configure Live for Speed

1. **Launch Live for Speed**
2. **Enable InSim:**
   - Go to **Options** → **Misc**
   - Find the **InSim** section
   - Check the **InSim** checkbox
   - Set port to: `29999`
   - Leave admin password blank (for local use)
   - Click **OK**

3. **Start a driving session:**
   - Select any track (e.g., Blackwood GP - BL1)
   - Select any car (e.g., XF GTI)
   - Click **Drive** or **Practice**

**Note:** InSim only works during active driving sessions, not in menus.

### Step 8: Verify Installation

**Option A: Run Verification Script (Recommended)**

```bash
# Run the setup verification script
python scripts/verify_setup.py
```

This script checks:
- ✓ Python version
- ✓ Virtual environment status
- ✓ Core dependencies installed
- ✓ Package installed in editable mode
- ✓ Project structure intact
- ✓ Configuration file exists
- ✓ Tests can execute

**Expected output:**
```
============================================================
  LFS-Ayats Setup Verification
============================================================

✓ [PASS] Python version: 3.12.3
✓ [PASS] Virtual environment detected
✓ [PASS] Core dependencies installed
✓ [PASS] Package installed in editable mode
✓ [PASS] Project structure is complete
✓ [PASS] Configuration file exists
✓ [PASS] Tests can be executed

============================================================
  Summary
============================================================

Checks passed: 7/7
✓ All checks passed! Your environment is properly configured.
```

**Option B: Test Basic Connection**

If you have LFS running, test with a basic connection:

```bash
# Run basic connection example
python examples/basic_connection.py
```

**Expected output:**
```
INFO - === Basic InSim Connection Example ===
INFO - Connecting to 127.0.0.1:29999...
INFO - Connection established!
INFO - InSim initialized!
INFO - Receiving packets for 10 seconds...
INFO - Packet received: IS_VER
INFO - Packet received: IS_ISM
INFO - Disconnecting...
INFO - Connection closed.
```

✅ **If verification script passes or you see basic connection output, installation is successful!**

## Platform-Specific Notes

### Windows

**Firewall:** You may need to allow Python through Windows Firewall:
1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Add Python to allowed apps

**PowerShell Execution Policy:**
If activation script fails, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux

**Permissions:** Ensure you have read/write access to the installation directory:
```bash
chmod +x scripts/*.sh
```

**Port Access:** Port 29999 should be available. Check with:
```bash
sudo netstat -tlnp | grep 29999
```

### macOS

**Xcode Command Line Tools:** May be required for some dependencies:
```bash
xcode-select --install
```

**Security:** You may need to allow Python in System Preferences → Security & Privacy.

## Verification Checklist

After installation, verify these items:

- [ ] Python 3.8+ installed and accessible
- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] Package installed in development mode (`pip install -e .`)
- [ ] Configuration file created (`config.yaml`)
- [ ] LFS running with InSim enabled (port 29999)
- [ ] Basic connection example runs successfully
- [ ] No firewall blocking port 29999

## Common Installation Issues

### Issue: "Python not found" or "command not found"

**Cause:** Python not in system PATH

**Solution:**

**Windows:**
- Reinstall Python with "Add to PATH" checked
- Or manually add Python to PATH in System Environment Variables

**Linux/macOS:**
- Use `python3` instead of `python`
- Or create alias: `alias python=python3`

### Issue: "pip: command not found"

**Cause:** pip not installed or not in PATH

**Solution:**
```bash
# Windows
python -m ensurepip --upgrade

# Linux/macOS
sudo apt install python3-pip  # Ubuntu/Debian
python3 -m ensurepip --upgrade
```

### Issue: "Permission denied" when installing packages

**Cause:** Insufficient permissions or system Python being modified

**Solution:**
- Use virtual environment (recommended)
- Or use `--user` flag: `pip install --user -r requirements.txt`
- Avoid using `sudo pip` (not recommended)

### Issue: Virtual environment activation fails

**Cause:** Different shell or execution policy

**Solution:**

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS (different shells):**
```bash
source venv/bin/activate      # bash/zsh
source venv/bin/activate.fish # fish
source venv/bin/activate.csh  # csh/tcsh
```

### Issue: Dependency installation fails

**Cause:** Missing system libraries or compiler

**Solution:**

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Fedora
sudo dnf install gcc gcc-c++ python3-devel
```

**macOS:**
```bash
xcode-select --install
```

### Issue: "Connection refused" when running examples

**Cause:** LFS not running or InSim not enabled

**Solution:**
1. Verify LFS is running
2. Check InSim is enabled (Options → Misc)
3. Confirm port is 29999
4. Ensure you're in an active driving session (not menu)
5. Check firewall isn't blocking connection

### Issue: Import errors after installation

**Cause:** Package not installed in development mode

**Solution:**
```bash
# Reinstall in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows
```

## Upgrading

To upgrade to the latest version:

```bash
# Navigate to LFS-Ayats directory
cd LFS-Ayats

# Pull latest changes (if using Git)
git pull origin main

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Upgrade dependencies
pip install --upgrade -r requirements.txt

# Reinstall package
pip install -e .
```

## Uninstallation

To completely remove LFS-Ayats:

```bash
# Deactivate virtual environment
deactivate

# Remove installation directory
rm -rf LFS-Ayats  # Linux/macOS
rmdir /s LFS-Ayats  # Windows
```

## Next Steps

After successful installation:

1. ✅ Complete the [Quick Start Guide](quick-start.md) (5-10 minutes)
2. ✅ Try the [Beginner Tutorial](tutorial-beginner.md) (30 minutes)
3. ✅ Review the [FAQ](faq.md) for common questions
4. ✅ Explore [Example Scripts](../examples/)

## Additional Resources

- **Documentation:** [Full Documentation](README.md)
- **Troubleshooting:** [Troubleshooting Guide](troubleshooting.md)
- **API Reference:** [API Documentation](api_reference.md)
- **GitHub Issues:** [Report Problems](https://github.com/lfsplayer97/LFS-Ayats/issues)

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [FAQ](faq.md)
2. Review the [Troubleshooting Guide](troubleshooting.md)
3. Search existing [GitHub Issues](https://github.com/lfsplayer97/LFS-Ayats/issues)
4. Open a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Full error message
   - Steps you've already tried

---

**Installation complete!** 🎉 You're ready to start collecting telemetry data from Live for Speed.
