# Development Environment Setup

Complete guide for setting up the LFS-Ayats development environment.

## Prerequisites

- **Python 3.8+** installed
- **Git** installed
- **Code editor** (VS Code recommended)
- **Live for Speed** (optional for real testing)

## Step 1: Fork and Clone

### 1.1 Fork the Repository

1. Go to https://github.com/lfsplayer97/LFS-Ayats
2. Click "Fork" in the upper right corner
3. Choose your GitHub account

### 1.2 Clone the Fork

```bash
git clone https://github.com/YOUR_USERNAME/LFS-Ayats.git
cd LFS-Ayats

# Add upstream to synchronize
git remote add upstream https://github.com/lfsplayer97/LFS-Ayats.git
```

## Step 2: Virtual Environment

### Linux/Mac

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify
which python  # Should show path inside venv/
```

### Windows

```powershell
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Verify
where python  # Should show path inside venv\
```

## Step 3: Install Dependencies

```bash
# Production and development dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .

# Verify installation
pip list | grep lfs-ayats
```

## Step 4: Editor Configuration

### VS Code (Recommended)

Install extensions:
```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter
code --install-extension ms-python.flake8
```

Configuration (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false
}
```

### PyCharm

1. Open the project
2. File > Settings > Project > Python Interpreter
3. Add interpreter: `venv/bin/python`
4. Configure Black as formatter
5. Enable Flake8 for linting

## Step 5: Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Configure hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Configuration (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.12
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

## Step 6: Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific tests
pytest tests/unit/
pytest tests/integration/

# Quick tests (without integration)
pytest -m "not integration"
```

## Step 7: Local Configuration

```bash
# Copy example configuration
cp config.example.yaml config.yaml

# Edit for your needs
nano config.yaml  # or vim, code, etc.
```

## Step 8: Verify Configuration

Run the verification script to ensure everything is configured correctly:

```bash
# From the project root directory
python scripts/verify_setup.py
```

This script verifies:
- ✓ Python version (3.8+)
- ✓ Virtual environment active
- ✓ Core dependencies installed
- ✓ Package installed in editable mode
- ✓ Complete project structure
- ✓ Configuration file exists
- ✓ Tests can be executed

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

If any verification fails, the script will show the steps to correct it.

## Development Workflow

### 1. Create Branch

```bash
# Synchronize with upstream
git fetch upstream
git merge upstream/main

# Create branch for feature
git checkout -b feature/new-functionality

# Or for bug fix
git checkout -b fix/fix-bug
```

### 2. Make Changes

```bash
# Edit files...

# Format code
black src/ tests/

# Verify style
flake8 src/ tests/

# Type checking
mypy src/
```

### 3. Run Tests

```bash
# Unit tests
pytest tests/unit/

# Complete tests
pytest --cov=src
```

### 4. Commit

```bash
# Add files
git add .

# Commit with descriptive message
git commit -m "feat: add new functionality X"

# Pre-commit hooks will run automatically
```

### 5. Push and Pull Request

```bash
# Push to fork
git push origin feature/new-functionality

# Create PR from GitHub web interface
```

## Troubleshooting

### Error: "pip: command not found"

```bash
# Install pip
python -m ensurepip --upgrade
```

### Error: "ModuleNotFoundError: No module named 'src'"

```bash
# Reinstall in editable mode
pip install -e .
```

### Tests fail with ImportError

```bash
# Verify PYTHONPATH
echo $PYTHONPATH

# Add if necessary
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Pre-commit hooks fail

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Update hooks
pre-commit autoupdate
```

## Additional Resources

- [Coding Standards](coding-standards.md)
- [Testing Guide](testing-guide.md)
- [Main Documentation](../README.md)
- [Architecture](../architecture.md)

## Tips

1. **Update regularly**: `git fetch upstream && git merge upstream/main`
2. **Run tests often**: Before commit and push
3. **Read existing code**: To maintain consistency
4. **Document changes**: Update docs if necessary
5. **Ask questions**: Open an issue if you have doubts

---

Now you're ready to contribute! 🚀
