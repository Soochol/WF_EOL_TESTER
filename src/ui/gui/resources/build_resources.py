#!/usr/bin/env python3
"""
Resource Builder Script

Builds Qt resource files from .qrc definitions.
Run this script when adding new icons or updating resources.
"""

import subprocess
import sys
from pathlib import Path


def build_resources():
    """Build Qt resources from .qrc file"""
    resources_dir = Path(__file__).parent
    qrc_file = resources_dir / "resources.qrc"
    output_file = resources_dir / "resources_rc.py"

    if not qrc_file.exists():
        print(f"Error: {qrc_file} not found")
        return False

    try:
        # Use pyside6-rcc to compile resources
        cmd = ["pyside6-rcc", str(qrc_file), "-o", str(output_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Successfully built resources: {output_file}")
            return True
        else:
            print(f"Error building resources: {result.stderr}")
            return False

    except FileNotFoundError:
        print("Error: pyside6-rcc not found. Please install PySide6:")
        print("pip install PySide6")
        return False


if __name__ == "__main__":
    success = build_resources()
    sys.exit(0 if success else 1)