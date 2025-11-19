#!/usr/bin/env python3
"""
LFS-Ayats Setup Verification Script

This script verifies that your development environment is properly configured.
Run this after installation to ensure everything is set up correctly.

Usage:
    python scripts/verify_setup.py

Note: This script should be run from the project root directory or directly with
      python scripts/verify_setup.py from the root.
"""

import sys
import subprocess
from pathlib import Path

# Ensure project root is in sys.path for proper imports
# This handles the case when script is run from scripts/ directory
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_check(success: bool, message: str, detail: str = "") -> None:
    """Print a check result with formatting."""
    symbol = "✓" if success else "✗"
    status = "PASS" if success else "FAIL"
    color = "\033[92m" if success else "\033[91m"
    reset = "\033[0m"

    print(f"{color}{symbol} [{status}]{reset} {message}")
    if detail:
        print(f"         {detail}")


def check_python_version() -> bool:
    """Verify Python version is 3.8 or higher."""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 8

    version_str = f"{version.major}.{version.minor}.{version.micro}"
    if is_valid:
        print_check(True, f"Python version: {version_str}", "Required: Python 3.8+")
    else:
        print_check(
            False, f"Python version: {version_str}", "ERROR: Python 3.8+ required"
        )

    return is_valid


def check_virtual_environment() -> bool:
    """Check if running in a virtual environment."""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print_check(True, "Virtual environment detected", f"Location: {sys.prefix}")
    else:
        print_check(
            False,
            "Not in virtual environment",
            "WARNING: Consider using a virtual environment",
        )

    return in_venv


def check_core_dependencies() -> bool:
    """Verify core dependencies are installed."""
    required_packages = [
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("plotly", "Plotly"),
        ("dash", "Dash"),
        ("pytest", "Pytest"),
        ("fastapi", "FastAPI"),
    ]

    missing = []
    for module_name, display_name in required_packages:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(display_name)

    if not missing:
        print_check(
            True,
            "Core dependencies installed",
            f"Verified {len(required_packages)} packages",
        )
        return True
    else:
        print_check(False, "Missing dependencies", f"Missing: {', '.join(missing)}")
        return False


def check_package_installed() -> bool:
    """Verify LFS-Ayats package is installed in editable mode."""
    # First check if pip package is installed
    result = subprocess.run(
        ["pip", "show", "lfs-ayats"], capture_output=True, text=True, check=False
    )

    if result.returncode != 0:
        print_check(False, "Package 'lfs-ayats' not installed", "Run: pip install -e .")
        return False

    # Check if it's in editable mode
    is_editable = "Editable project location" in result.stdout

    # Try to import the src package
    try:
        import src

        location = Path(src.__file__).parent.parent

        if is_editable:
            print_check(
                True, "Package installed in editable mode", f"Location: {location}"
            )
            return True
        else:
            print_check(
                False,
                "Package installed but not in editable mode",
                "Run: pip install -e . to enable auto-reload",
            )
            return False

    except ImportError as e:
        print_check(
            False, "Cannot import 'src' module", f"ERROR: {e}. Try: pip install -e ."
        )
        return False


def check_config_file() -> bool:
    """Check if configuration file exists."""
    config_path = Path("config.yaml")
    example_path = Path("config.example.yaml")

    if config_path.exists():
        print_check(
            True, "Configuration file exists", f"Location: {config_path.absolute()}"
        )
        return True
    elif example_path.exists():
        print_check(
            False,
            "Configuration file not found",
            f"Copy {example_path} to {config_path}",
        )
        return False
    else:
        print_check(
            False, "Configuration files missing", "Cannot find config.example.yaml"
        )
        return False


def check_tests_can_run() -> bool:
    """Verify that tests can be executed."""
    result = subprocess.run(
        ["pytest", "--collect-only", "-q"], capture_output=True, text=True, check=False
    )

    if result.returncode == 0:
        # Extract number of tests from output
        lines = result.stdout.strip().split("\n")
        last_line = lines[-1] if lines else ""
        print_check(True, "Tests can be executed", f"Found tests: {last_line}")
        return True
    else:
        print_check(False, "Cannot execute tests", "ERROR: pytest failed")
        return False


def check_project_structure() -> bool:
    """Verify project structure is intact."""
    required_dirs = [
        "src",
        "tests",
        "docs",
        "examples",
    ]

    required_files = [
        "setup.py",
        "requirements.txt",
        "pytest.ini",
        "README.md",
    ]

    missing_dirs = [d for d in required_dirs if not Path(d).is_dir()]
    missing_files = [f for f in required_files if not Path(f).is_file()]

    if not missing_dirs and not missing_files:
        print_check(
            True,
            "Project structure is complete",
            f"Verified {len(required_dirs)} directories and {len(required_files)} files",
        )
        return True
    else:
        errors = []
        if missing_dirs:
            errors.append(f"Missing directories: {', '.join(missing_dirs)}")
        if missing_files:
            errors.append(f"Missing files: {', '.join(missing_files)}")
        print_check(False, "Project structure incomplete", "; ".join(errors))
        return False


def print_summary(checks: dict) -> None:
    """Print summary of all checks."""
    print_header("Summary")

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)

    print(f"Checks passed: {passed}/{total}")
    print()

    if passed == total:
        print(
            "\033[92m✓ All checks passed! Your environment is properly configured.\033[0m"
        )
        print()
        print("You can now:")
        print("  • Run examples: python examples/basic_connection.py")
        print("  • Run tests: pytest")
        print("  • Start developing: See docs/contributing/development-setup.md")
        return True
    else:
        print("\033[91m✗ Some checks failed. Please fix the issues above.\033[0m")
        print()
        print("Common solutions:")

        if not checks.get("package_installed"):
            print("  • Install package: pip install -e .")
        if not checks.get("dependencies"):
            print("  • Install dependencies: pip install -r requirements.txt")
        if not checks.get("venv"):
            print("  • Create virtual environment: python -m venv venv")
            print(
                "  • Activate it: source venv/bin/activate (Linux/Mac) "
                "or venv\\Scripts\\activate (Windows)"
            )

        print()
        print("For more help, see: docs/troubleshooting.md")
        return False


def main() -> int:
    """Run all verification checks."""
    print_header("LFS-Ayats Setup Verification")

    print("Verifying your development environment setup...")
    print("This will check Python version, dependencies, and configuration.")

    # Run all checks
    checks = {
        "python_version": check_python_version(),
        "venv": check_virtual_environment(),
        "dependencies": check_core_dependencies(),
        "package_installed": check_package_installed(),
        "project_structure": check_project_structure(),
        "config_file": check_config_file(),
        "tests": check_tests_can_run(),
    }

    # Print summary
    success = print_summary(checks)

    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\033[91mERROR: Unexpected error occurred: {e}\033[0m")
        sys.exit(1)
