# Contribution Guide

Thank you for your interest in contributing to LFS-Ayats! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and professional
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards other members

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:

1. **Descriptive title**
2. **Detailed description** of the problem
3. **Steps to reproduce** the bug
4. **Expected behavior** vs actual behavior
5. **Environment**: Python version, OS, LFS version
6. **Logs or screenshots** if applicable

### Suggesting Improvements

To suggest new features:

1. **Check** that a similar issue doesn't already exist
2. **Describe** the desired functionality
3. **Explain** the use case and benefits
4. **Propose** an implementation if possible

### Pull Requests

#### Preparation

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/feature-name
   # or
   git checkout -b fix/bug-name
   ```

#### Development

1. **Follow** coding conventions (PEP 8)
2. **Write tests** for your functionality
3. **Update documentation** if needed
4. **Ensure** all tests pass:
   ```bash
   pytest --cov=src
   ```

#### Format and Quality

```bash
# Format code
black src/ tests/ examples/

# Check style
flake8 src/ tests/ examples/ --max-line-length=100 --extend-ignore=E203,W503

# Type checking
mypy src/ --ignore-missing-imports

# Security scan (optional)
bandit -r src/ --skip B101
```

**Pre-commit Hooks (Recommended)**

To automatically check code quality before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

#### Continuous Integration

All pull requests automatically run through our CI/CD pipeline:

- **Tests Workflow**: Runs tests across Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Code Quality Workflow**: Checks formatting (Black), linting (Flake8), type checking (MyPy), and security (Bandit)
- **Coverage Report**: Uploaded to Codecov for Python 3.11

Your PR must pass all required checks before it can be merged. The workflows will automatically comment on your PR if issues are found.

#### Commit

Use descriptive commit messages:

```
feat: Add support for IS_NEW packet

- Implement parser for IS_NEW
- Add unit tests
- Update documentation

Refs: #123
```

Recommended prefixes:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Add or modify tests
- `refactor:` Code refactoring
- `style:` Format changes (don't affect functionality)
- `perf:` Performance improvements

#### Creating Pull Request

1. **Push** your branch to your fork
2. **Open** a Pull Request to `main`
3. **Describe** the changes made
4. **Reference** related issues
5. **Wait** for review

### Code Review

PRs will be reviewed for:

- **Code quality**: Following conventions
- **Tests**: Adequate coverage
- **Documentation**: Clear and complete
- **Functionality**: Works as expected
- **Impact**: Doesn't break existing functionality

## Coding Standards

### Python (PEP 8)

```python
# Best practices

# 1. Organized imports
import os
import sys
from typing import List, Optional

from src.connection import InSimClient
from src.telemetry import TelemetryCollector

# 2. Constants in uppercase
MAX_SPEED = 150.0
DEFAULT_PORT = 29999

# 3. Functions with type hints
def process_telemetry(data: List[CarTelemetry]) -> ProcessedTelemetry:
    """
    Process telemetry.
    
    Args:
        data: List of telemetry
        
    Returns:
        Processed data
    """
    pass

# 4. Classes with docstrings
class TelemetryProcessor:
    """
    Telemetry processor.
    
    Attributes:
        max_speed: Maximum allowed speed
    """
    
    def __init__(self, max_speed: float = 150.0):
        self.max_speed = max_speed
```

### Documentation

All public modules, classes, and functions must have docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description.

    Detailed description if needed. Can include multiple
    paragraphs to explain behavior.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
        ConnectionError: If connection fails

    Example:
        >>> function_name("test", 42)
        True
        
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#section
    """
    pass
```

### Tests

Write tests for:

- All public functions
- Edge cases and errors
- Integration between modules

```python
import pytest
from src.module import MyClass


class TestMyClass:
    """Test cases for MyClass"""

    @pytest.fixture
    def instance(self):
        """Fixture for MyClass instance"""
        return MyClass()

    def test_basic_functionality(self, instance):
        """Test basic functionality"""
        result = instance.method()
        assert result is not None

    def test_error_handling(self, instance):
        """Test error handling"""
        with pytest.raises(ValueError):
            instance.method_with_error()

    @pytest.mark.integration
    def test_integration(self, instance):
        """Test integration with other modules"""
        # Integration test
        pass
```

## Project Structure

When adding new functionality, follow this structure:

```
src/
└── new_module/
    ├── __init__.py          # Export public API
    ├── main_class.py        # Main class
    ├── helpers.py           # Helper functions
    └── constants.py         # Module constants

tests/
└── unit/
    └── new_module/
        ├── __init__.py
        ├── test_main_class.py
        └── test_helpers.py

docs/
└── new_module.md            # Module documentation

examples/
└── new_module_example.py    # Usage example
```

## InSim-Specific Aspects

### Implementing New Packet Type

1. **Consult InSim.txt**: https://en.lfsmanual.net/wiki/InSim.txt
2. **Add the type** to `PacketType` enum
3. **Implement the parser** in `PacketHandler`
4. **Write tests** with test packets
5. **Document** structure and usage

### Telemetry

- Consider performance (high data frequency)
- Validate received data
- Handle network errors
- Document units of measurement

### References

Always include references to official documentation:

```python
"""
Implementation of IS_MCI packet.

Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_MCI
"""
```

## Changelog and Versioning

### Updating the CHANGELOG

All notable changes must be documented in `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com/) format.

#### When to Update

Update the CHANGELOG when:
- Adding new features
- Changing existing functionality
- Deprecating features
- Removing features
- Fixing bugs
- Addressing security vulnerabilities

#### How to Update

Add your changes to the `[Unreleased]` section under the appropriate category:

```markdown
## [Unreleased]

### Added
- New TelemetryAnalyzer class for advanced data analysis
- WebSocket support for real-time streaming

### Changed
- Improved InSimClient connection handling
- Updated documentation with more examples

### Deprecated
- `export_csv()` method (use `CSVExporter` class instead)

### Fixed
- Fixed socket timeout issue on slow connections
- Fixed memory leak in telemetry buffer

### Security
- Updated dependencies to patch vulnerabilities
```

**Categories:**
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Features soon to be removed
- **Removed**: Features removed in this version
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

### Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

**Format:** `MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`

Examples:
- `0.1.0` → `0.1.1`: Bug fix (PATCH)
- `0.1.0` → `0.2.0`: New feature (MINOR)
- `0.1.0` → `1.0.0`: Breaking changes (MAJOR)
- `1.0.0-rc.1`: Release candidate
- `1.0.0-beta.1`: Beta version

**Version Increments:**
- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

### Release Process

When preparing a release, follow this checklist:

1. **Verify Completion**
   - [ ] All issues for milestone are closed
   - [ ] All tests pass
   - [ ] Code coverage is acceptable
   - [ ] No breaking changes (or documented if MAJOR)

2. **Update Documentation**
   - [ ] Move `[Unreleased]` changes to new version section in CHANGELOG.md
   - [ ] Update version in `setup.py`
   - [ ] Update version in `src/__init__.py`
   - [ ] Update README if needed

3. **Version the Changes**
   ```bash
   # Example for version 1.2.0
   VERSION="1.2.0"
   
   # Update version in files
   sed -i "s/__version__ = .*/__version__ = \"$VERSION\"/" src/__init__.py
   sed -i "s/version=.*/version='$VERSION',/" setup.py
   
   # Update CHANGELOG.md manually with release date
   # Change ## [Unreleased] to ## [1.2.0] - 2025-11-15
   ```

4. **Commit and Tag**
   ```bash
   git add src/__init__.py setup.py CHANGELOG.md
   git commit -m "chore: bump version to $VERSION"
   git tag -a "v$VERSION" -m "Release version $VERSION"
   git push origin main
   git push origin "v$VERSION"
   ```

5. **Create GitHub Release**
   - GitHub Actions will create a release from the tag
   - Add release notes from CHANGELOG.md
   - Attach any relevant assets

### Version File Locations

Ensure version is updated in these files:
- `setup.py` - Line 16: `version='0.1.0'`
- `src/__init__.py` - Line 6: `__version__ = "0.1.0"`
- `CHANGELOG.md` - New section with version and date

**Note:** Keep all version numbers in sync to avoid confusion.

## License

By contributing, you agree that your contributions will be licensed under the project's MIT license.

## Questions?

If you have questions:

1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/lfsplayer97/LFS-Ayats/issues)
3. Open a new issue with "question" label

## Acknowledgments

Contributions will be acknowledged:

- In README.md
- In release notes
- In the AUTHORS file (if it exists)

Thank you for helping improve LFS-Ayats! 🏎️
