"""
Version management utility.

Reads version from pyproject.toml as the single source of truth.
"""

import re
import sys
from pathlib import Path
from typing import Optional


def get_project_version() -> str:
    """
    Get project version from pyproject.toml.

    This is the single source of truth for version information.
    Falls back to hardcoded version if pyproject.toml is not accessible.

    Returns:
        Version string (e.g., "0.1.0")
    """
    # Try to locate pyproject.toml
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running in PyInstaller bundle - version should be embedded
        # Fall back to package metadata or hardcoded value
        return _get_frozen_version()

    # Running in development - read from pyproject.toml
    return _read_version_from_pyproject()


def _read_version_from_pyproject() -> str:
    """Read version from pyproject.toml using regex (no external dependencies)."""
    try:
        # Find pyproject.toml (should be in project root)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"

        if not pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

        # Read and parse version using regex
        content = pyproject_path.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)

        if match:
            version = match.group(1)
            return version
        else:
            raise ValueError("Version not found in pyproject.toml")

    except Exception as e:
        print(f"Warning: Failed to read version from pyproject.toml: {e}")
        return _get_fallback_version()


def _get_frozen_version() -> str:
    """
    Get version for frozen (PyInstaller) application.

    In frozen builds, we embed the version at build time.
    """
    # This will be replaced by build script with actual version
    # For now, use fallback
    return _get_fallback_version()


def _get_fallback_version() -> str:
    """Fallback version if pyproject.toml is not accessible."""
    return "0.1.0"


def get_version_info() -> dict:
    """
    Get detailed version information.

    Returns:
        Dictionary with version details
    """
    version = get_project_version()
    parts = version.split(".")

    return {
        "version": version,
        "major": int(parts[0]) if len(parts) > 0 else 0,
        "minor": int(parts[1]) if len(parts) > 1 else 0,
        "patch": int(parts[2]) if len(parts) > 2 else 0,
    }


# Convenience constant
__version__ = get_project_version()


if __name__ == "__main__":
    # Test version reading
    print(f"Project version: {get_project_version()}")
    print(f"Version info: {get_version_info()}")
