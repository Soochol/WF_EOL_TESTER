#!/usr/bin/env python3
"""
Debug the specific application.interfaces import issue by testing each submodule individually
"""

import sys
from pathlib import Path

def test_interface_imports():
    print("=== Interface Imports Debug ===")
    
    # Setup path like main.py does
    current_dir = Path(__file__).parent
    src_path = current_dir / "src"
    sys.path.insert(0, str(src_path))
    
    # Test each import from application.interfaces.__init__.py individually
    interface_imports = [
        ("hardware.loadcell", "from application.interfaces.hardware.loadcell import LoadCellService"),
        ("hardware.power", "from application.interfaces.hardware.power import PowerService"),
        ("hardware.robot", "from application.interfaces.hardware.robot import RobotService"),
        ("hardware.mcu", "from application.interfaces.hardware.mcu import MCUService"),
        ("hardware.digital_io", "from application.interfaces.hardware.digital_io import DigitalIOService"),
        ("config.configuration", "from application.interfaces.configuration.configuration import Configuration"),
        ("config.preference", "from application.interfaces.configuration.profile_preference import ProfilePreference"),
        ("repository", "from application.interfaces.repository.test_result_repository import TestResultRepository"),
    ]
    
    print("Testing individual interface imports...")
    failed_imports = []
    
    for import_name, import_statement in interface_imports:
        try:
            print(f"  Testing {import_name}...")
            exec(import_statement)
            print(f"    ✅ SUCCESS: {import_name}")
        except Exception as e:
            print(f"    ❌ FAILED: {import_name}")
            print(f"       Error: {e}")
            print(f"       Error type: {type(e).__name__}")
            failed_imports.append((import_name, str(e)))
    
    if failed_imports:
        print(f"\n=== Found {len(failed_imports)} failed imports ===")
        for import_name, error in failed_imports:
            print(f"- {import_name}: {error}")
    else:
        print("\n✅ All individual imports successful!")
    
    # Now test the problematic application.interfaces import
    print("\n=== Testing application.interfaces as a whole ===")
    try:
        import application.interfaces
        print("✅ application.interfaces imported successfully!")
    except Exception as e:
        print(f"❌ application.interfaces import failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # The issue is in the __init__.py file
        print("\n=== Analyzing application.interfaces.__init__.py ===")
        init_file = src_path / "application" / "interfaces" / "__init__.py"
        if init_file.exists():
            print(f"File exists: {init_file}")
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"File size: {len(content)} characters")
                print(f"Number of lines: {len(content.splitlines())}")
                
                # Check for any problematic characters
                if '\r' in content:
                    print("⚠️  File still contains carriage returns!")
                else:
                    print("✅ File has clean line endings")
                    
            except Exception as read_error:
                print(f"Error reading file: {read_error}")
        else:
            print("❌ __init__.py file does not exist!")

if __name__ == "__main__":
    test_interface_imports()