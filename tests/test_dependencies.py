"""Test to verify project dependencies are correctly specified."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


def test_python_version_requirement():
    """Verify Python version meets minimum requirement."""
    assert sys.version_info >= (3, 10), (
        f"Python 3.10+ required, but running {sys.version_info.major}.{sys.version_info.minor}"
    )


def test_standard_library_imports():
    """Verify all standard library modules can be imported."""
    # These should all be available in Python 3.10+
    standard_modules = [
        "__future__",
        "array",
        "asyncio",
        "base64",
        "contextlib",
        "dataclasses",
        "datetime",
        "hashlib",
        "inspect",
        "ipaddress",
        "json",
        "logging",
        "math",
        "pathlib",
        "select",
        "socket",
        "sqlite3",
        "struct",
        "sys",
        "threading",
        "time",
        "types",
        "typing",
    ]

    for module_name in standard_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            pytest.fail(
                f"Standard library module '{module_name}' not available: {e}\n"
                f"This should be included with Python 3.10+. "
                f"Current Python version: {sys.version}"
            )


def test_runtime_dependency_simpleaudio():
    """Verify simpleaudio can be imported (or fails gracefully)."""
    try:
        import simpleaudio  # noqa: F401
        # If we get here, simpleaudio is installed
        assert True
    except ImportError:
        # simpleaudio is optional - the app falls back to silent mode
        # But we should warn about it
        pytest.skip(
            "simpleaudio not installed - audio features will be disabled.\n"
            "To enable audio: pip install simpleaudio>=1.0\n"
            "On Linux, you may need: sudo apt-get install libasound2-dev"
        )


def test_pyproject_toml_exists():
    """Verify pyproject.toml exists and is readable."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml not found"

    content = pyproject_path.read_text()
    assert "simpleaudio" in content, "simpleaudio not listed in pyproject.toml"
    assert 'requires-python = ">=3.10"' in content, "Python version requirement not specified"


def test_requirements_dev_exists():
    """Verify requirements-dev.txt exists and contains expected tools."""
    req_path = Path(__file__).parent.parent / "requirements-dev.txt"
    assert req_path.exists(), "requirements-dev.txt not found"

    content = req_path.read_text()
    expected_tools = ["bandit", "black", "flake8", "isort", "mypy", "pylint", "pytest"]

    for tool in expected_tools:
        assert tool in content, f"Development tool '{tool}' not in requirements-dev.txt"


def test_dependencies_documentation_exists():
    """Verify DEPENDENCIES.md exists."""
    doc_path = Path(__file__).parent.parent / "DEPENDENCIES.md"
    assert doc_path.exists(), (
        "DEPENDENCIES.md not found. "
        "This file should document all project dependencies."
    )

    content = doc_path.read_text()
    # Verify key sections are present
    assert "## Runtime Dependencies" in content
    assert "## Development Dependencies" in content
    assert "## Standard Library Modules" in content
    assert "simpleaudio" in content


def test_no_unnecessary_dependencies():
    """Verify we don't have dependencies on packages that should be stdlib."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()

    # These should NOT be in dependencies as they're stdlib
    stdlib_modules = [
        "threading",
        "pathlib",
        "dataclasses",
        "json",
        "logging",
        "asyncio",
        "socket",
    ]

    for module in stdlib_modules:
        # Check if module appears in dependencies section
        # (it might appear in comments or other sections)
        lines = content.split("\n")
        in_dependencies = False
        for line in lines:
            if line.strip() == "dependencies = [":
                in_dependencies = True
            elif in_dependencies and line.strip() == "]":
                in_dependencies = False
            elif in_dependencies and module in line:
                pytest.fail(
                    f"'{module}' is in dependencies but it's a standard library module!\n"
                    f"Remove it from pyproject.toml - it's included with Python 3.10+"
                )


def test_main_imports():
    """Verify main.py can import without missing dependencies."""
    # This is an integration test - if main.py can be imported,
    # all dependencies are available
    try:
        import main  # noqa: F401
    except ImportError as e:
        pytest.fail(
            f"Failed to import main.py: {e}\n"
            f"This suggests a dependency is missing. "
            f"Check pyproject.toml and requirements-dev.txt"
        )


def test_src_modules_importable():
    """Verify all src modules can be imported."""
    src_modules = [
        "src.hud",
        "src.insim_client",
        "src.outsim_client",
        "src.persistence",
        "src.radar",
        "src.telemetry_ws",
        "src.audio.beep_driver",
    ]

    for module_name in src_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            pytest.fail(
                f"Failed to import {module_name}: {e}\n"
                f"This suggests a dependency issue in {module_name}"
            )
