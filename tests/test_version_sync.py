"""Tests for version synchronization script."""

import json
from pathlib import Path


def test_get_version_from_pyproject(tmp_path: Path) -> None:
    """Test extracting version from pyproject.toml."""
    # Import the sync_version module
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from sync_version import get_version_from_pyproject

    # Create a temporary pyproject.toml
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(
        """
[project]
name = "test-project"
version = "1.2.3"
description = "Test project"
"""
    )

    version = get_version_from_pyproject(pyproject_path)
    assert version == "1.2.3"


def test_get_version_from_package_json(tmp_path: Path) -> None:
    """Test extracting version from package.json."""
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from sync_version import get_version_from_package_json

    # Create a temporary package.json
    package_json_path = tmp_path / "package.json"
    package_json_path.write_text(json.dumps({"name": "test-project", "version": "2.3.4"}))

    version = get_version_from_package_json(package_json_path)
    assert version == "2.3.4"


def test_update_package_json_version(tmp_path: Path) -> None:
    """Test updating version in package.json."""
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from sync_version import get_version_from_package_json, update_package_json_version

    # Create a temporary package.json
    package_json_path = tmp_path / "package.json"
    original_data = {
        "name": "test-project",
        "version": "1.0.0",
        "description": "Test",
    }
    package_json_path.write_text(json.dumps(original_data, indent=4))

    # Update version
    update_package_json_version(package_json_path, "3.0.0")

    # Verify update
    new_version = get_version_from_package_json(package_json_path)
    assert new_version == "3.0.0"

    # Verify other fields are preserved
    data = json.loads(package_json_path.read_text())
    assert data["name"] == "test-project"
    assert data["description"] == "Test"


def test_version_sync_integration(tmp_path: Path) -> None:
    """Test version synchronization integration."""
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from sync_version import (
        get_version_from_package_json,
        get_version_from_pyproject,
        update_package_json_version,
    )

    # Create test files with different versions
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(
        """
[project]
version = "2.0.0"
"""
    )

    package_json_path = tmp_path / "package.json"
    package_json_path.write_text(json.dumps({"version": "1.5.0"}))

    # Verify versions are different
    pyproject_version = get_version_from_pyproject(pyproject_path)
    package_json_version = get_version_from_package_json(package_json_path)
    assert pyproject_version == "2.0.0"
    assert package_json_version == "1.5.0"

    # Sync versions
    update_package_json_version(package_json_path, pyproject_version)

    # Verify versions are now the same
    new_package_json_version = get_version_from_package_json(package_json_path)
    assert new_package_json_version == pyproject_version
