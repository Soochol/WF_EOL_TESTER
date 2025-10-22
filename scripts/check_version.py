#!/usr/bin/env python3
"""
Version Consistency Checker

Verifies that version is consistent across all project files.
"""

import re
import sys
from pathlib import Path


def read_version_from_pyproject() -> str:
    """Read version from pyproject.toml (source of truth)."""
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"

    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)

    if match:
        return match.group(1)
    return "UNKNOWN"


def read_version_from_installer_iss() -> str:
    """Read version from installer.iss."""
    project_root = Path(__file__).parent.parent
    installer_path = project_root / "installer.iss"

    if not installer_path.exists():
        return "FILE_NOT_FOUND"

    content = installer_path.read_text(encoding="utf-8")
    match = re.search(r'^#define\s+MyAppVersion\s+"([^"]+)"', content, re.MULTILINE)

    if match:
        return match.group(1)
    return "NOT_FOUND"


def read_version_from_application_yaml() -> str:
    """Read version from application.yaml."""
    project_root = Path(__file__).parent.parent
    yaml_path = project_root / "configuration" / "application.yaml"

    if not yaml_path.exists():
        return "FILE_NOT_FOUND"

    content = yaml_path.read_text(encoding="utf-8")
    match = re.search(r'^\s*version:\s*(.+)$', content, re.MULTILINE)

    if match:
        return match.group(1).strip()
    return "NOT_FOUND"


def read_version_from_main_gui() -> str:
    """Check if main_gui.py uses get_project_version()."""
    project_root = Path(__file__).parent.parent
    main_gui_path = project_root / "src" / "main_gui.py"

    if not main_gui_path.exists():
        return "FILE_NOT_FOUND"

    content = main_gui_path.read_text(encoding="utf-8")

    # Check if it imports and uses get_project_version
    has_import = bool(re.search(r'from utils\.version import get_project_version', content))
    has_usage = bool(re.search(r'APPLICATION_VERSION\s*=\s*get_project_version\(\)', content))

    if has_import and has_usage:
        return "DYNAMIC (pyproject.toml)"
    else:
        # Try to find hardcoded version
        match = re.search(r'APPLICATION_VERSION\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return f"HARDCODED ({match.group(1)})"
        return "NOT_FOUND"


def main():
    """Check version consistency across all files."""
    print("=" * 70)
    print("Version Consistency Check")
    print("=" * 70)
    print()

    # Read versions from all sources
    pyproject_version = read_version_from_pyproject()
    installer_version = read_version_from_installer_iss()
    yaml_version = read_version_from_application_yaml()
    main_gui_version = read_version_from_main_gui()

    # Display results
    print(f"pyproject.toml:         {pyproject_version} (SOURCE OF TRUTH)")
    print(f"installer.iss:          {installer_version}")
    print(f"application.yaml:       {yaml_version}")
    print(f"main_gui.py:            {main_gui_version}")
    print()

    # Check consistency
    all_match = True
    issues = []

    if installer_version != pyproject_version:
        if installer_version not in ["FILE_NOT_FOUND", "NOT_FOUND"]:
            all_match = False
            issues.append(f"installer.iss version mismatch: {installer_version} != {pyproject_version}")

    if yaml_version != pyproject_version:
        if yaml_version not in ["FILE_NOT_FOUND", "NOT_FOUND"]:
            all_match = False
            issues.append(f"application.yaml version mismatch: {yaml_version} != {pyproject_version}")

    if "HARDCODED" in main_gui_version:
        all_match = False
        issues.append(f"main_gui.py has hardcoded version instead of using get_project_version()")

    # Print results
    print("=" * 70)
    if all_match:
        print("[SUCCESS] All versions are consistent!")
        print(f"Current version: {pyproject_version}")
        print("=" * 70)
        return 0
    else:
        print("[FAILED] Version inconsistencies detected:")
        print()
        for issue in issues:
            print(f"  - {issue}")
        print()
        print("Run 'python scripts/sync_version.py' to fix inconsistencies.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
