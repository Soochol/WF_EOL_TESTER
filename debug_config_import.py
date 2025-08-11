#!/usr/bin/env python3
"""
Debug the specific configuration import issue on Windows
"""

import sys
from pathlib import Path

def test_configuration_import():
    print("=== Configuration Import Debug ===")
    
    # Setup path like main.py does
    current_dir = Path(__file__).parent
    src_path = current_dir / "src"
    sys.path.insert(0, str(src_path))
    
    # Test the import chain that's failing
    test_steps = [
        ("domain", "import domain"),
        ("domain.value_objects", "import domain.value_objects"),
        ("hardware_configuration", "from domain.value_objects.hardware_configuration import HardwareConfiguration"),
        ("test_configuration", "from domain.value_objects.test_configuration import TestConfiguration"),
        ("hardware_model", "from domain.value_objects.hardware_model import HardwareModel"),
        ("configuration_file", "from application.interfaces.configuration.configuration import Configuration")
    ]
    
    for step_name, import_code in test_steps:
        try:
            print(f"Testing {step_name}...")
            exec(import_code)
            print(f"  ✅ SUCCESS: {step_name}")
        except Exception as e:
            print(f"  ❌ FAILED: {step_name}")
            print(f"     Error: {e}")
            print(f"     Error type: {type(e).__name__}")
            
            # If this is the configuration file import, try a simpler approach
            if step_name == "configuration_file":
                print("  Trying alternative approach...")
                try:
                    import application.interfaces.configuration.configuration as config_module
                    print("  ✅ Alternative import successful")
                    print(f"     Module: {config_module}")
                    print(f"     File: {config_module.__file__}")
                except Exception as e2:
                    print(f"  ❌ Alternative import failed: {e2}")
            break
    
    print("\n=== Testing application.interfaces import directly ===")
    try:
        import application.interfaces
        print("✅ application.interfaces imported successfully")
    except Exception as e:
        print(f"❌ application.interfaces import failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Try to see what's in the interfaces directory
        interfaces_dir = src_path / "application" / "interfaces"
        print(f"\nContents of {interfaces_dir}:")
        if interfaces_dir.exists():
            for item in sorted(interfaces_dir.iterdir()):
                print(f"  - {item.name}")

if __name__ == "__main__":
    test_configuration_import()