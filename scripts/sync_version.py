#!/usr/bin/env python3
"""
Version Synchronization Script

Reads version from pyproject.toml (single source of truth) and updates:
- installer.iss
- configuration/application.yaml

This ensures version consistency across all project files.
"""

import re
import sys
from pathlib import Path


def read_version_from_pyproject() -> str:
    """Read version from pyproject.toml."""
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        print(f"ERROR: pyproject.toml not found at {pyproject_path}")
        sys.exit(1)

    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)

    if not match:
        print("ERROR: Version not found in pyproject.toml")
        sys.exit(1)

    version = match.group(1)
    print(f"[OK] Read version from pyproject.toml: {version}")
    return version


def update_installer_iss(version: str) -> bool:
    """Update version in installer.iss."""
    project_root = Path(__file__).parent.parent
    installer_path = project_root / "installer.iss"

    if not installer_path.exists():
        print(f"WARNING: installer.iss not found at {installer_path}")
        return False

    content = installer_path.read_text(encoding="utf-8")

    # Update #define MyAppVersion "x.x.x"
    pattern = r'^(#define\s+MyAppVersion\s+")[^"]+(")'
    replacement = rf'\g<1>{version}\g<2>'
    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

    if count == 0:
        print("WARNING: MyAppVersion not found in installer.iss")
        return False

    installer_path.write_text(new_content, encoding="utf-8")
    print(f"[OK] Updated installer.iss: MyAppVersion = {version}")
    return True


def update_application_yaml(version: str) -> bool:
    """Update version in configuration/application.yaml."""
    project_root = Path(__file__).parent.parent
    yaml_path = project_root / "configuration" / "application.yaml"

    if not yaml_path.exists():
        print(f"WARNING: application.yaml not found at {yaml_path}")
        return False

    content = yaml_path.read_text(encoding="utf-8")

    # Update version: x.x.x (must preserve indentation)
    pattern = r'^(\s*version:\s*)[^\n]+$'
    replacement = rf'\g<1>{version}'
    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

    if count == 0:
        print("WARNING: version field not found in application.yaml")
        return False

    yaml_path.write_text(new_content, encoding="utf-8")
    print(f"[OK] Updated application.yaml: version = {version}")
    return True


def main():
    """Main entry point."""
    print("=" * 60)
    print("Version Synchronization")
    print("=" * 60)
    print()

    # Read version from pyproject.toml (single source of truth)
    version = read_version_from_pyproject()
    print()

    # Update all files
    print("Updating files...")
    success_count = 0

    if update_installer_iss(version):
        success_count += 1

    if update_application_yaml(version):
        success_count += 1

    print()
    print("=" * 60)

    if success_count == 2:
        print(f"[SUCCESS] All files synchronized to version {version}")
        print("=" * 60)
        return 0
    else:
        print(f"[WARNING] Only {success_count}/2 files updated")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
