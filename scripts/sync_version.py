#!/usr/bin/env python3
"""
Script to synchronize version across project files.

This script reads the version from pyproject.toml (single source of truth)
and updates it in package.json to maintain consistency.

Usage:
    python scripts/sync_version.py
    python scripts/sync_version.py --check  # Check only, no modifications
"""

import argparse
import json
import re
import sys
from pathlib import Path


def get_version_from_pyproject(pyproject_path: Path) -> str:
    """Extract version from pyproject.toml file."""
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def get_version_from_package_json(package_json_path: Path) -> str:
    """Extract version from package.json file."""
    data = json.loads(package_json_path.read_text(encoding="utf-8"))
    return data.get("version", "")


def update_package_json_version(package_json_path: Path, version: str) -> None:
    """Update version in package.json file."""
    data = json.loads(package_json_path.read_text(encoding="utf-8"))
    data["version"] = version
    package_json_path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Synchronize version across project files")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if versions are synchronized without making changes",
    )
    args = parser.parse_args()

    # Define paths
    root_dir = Path(__file__).parent.parent
    pyproject_path = root_dir / "pyproject.toml"
    package_json_path = root_dir / "package.json"

    # Validate files exist
    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found", file=sys.stderr)
        return 1

    if not package_json_path.exists():
        print(f"Error: {package_json_path} not found", file=sys.stderr)
        return 1

    # Get versions
    try:
        pyproject_version = get_version_from_pyproject(pyproject_path)
        package_json_version = get_version_from_package_json(package_json_path)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error reading version: {e}", file=sys.stderr)
        return 1

    print(f"pyproject.toml version: {pyproject_version}")
    print(f"package.json version:   {package_json_version}")

    # Check if synchronized
    if pyproject_version == package_json_version:
        print("✓ Versions are synchronized")
        return 0

    if args.check:
        print("✗ Versions are NOT synchronized", file=sys.stderr)
        return 1

    # Update package.json
    print(f"Updating package.json to version {pyproject_version}...")
    try:
        update_package_json_version(package_json_path, pyproject_version)
        print("✓ package.json updated successfully")
        return 0
    except Exception as e:
        print(f"Error updating package.json: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
