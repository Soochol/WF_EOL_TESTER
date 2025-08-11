#!/usr/bin/env python3
"""
Debug script to isolate import issues on Windows
"""

import sys
from pathlib import Path

def main():
    print("=== Import Debug Script ===")
    
    # Setup path like main.py does
    current_dir = Path(__file__).parent
    src_path = current_dir / "src"
    
    print(f"Current directory: {current_dir}")
    print(f"Source path: {src_path}")
    print(f"Source path exists: {src_path.exists()}")
    
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        print(f"Added {src_path} to sys.path")
    
    # Test imports step by step
    test_imports = [
        "application",
        "application.interfaces", 
        "application.interfaces.configuration",
        "application.interfaces.configuration.configuration",
    ]
    
    for import_path in test_imports:
        try:
            print(f"Testing import: {import_path}")
            __import__(import_path)
            print(f"  ✅ SUCCESS: {import_path}")
        except ImportError as e:
            print(f"  ❌ FAILED: {import_path} - {e}")
            break
    
    # Try specific problematic import
    print("\nTesting specific import:")
    try:
        from application.interfaces.configuration.configuration import Configuration
        print("✅ Configuration import successful!")
    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
        
        # Check file existence
        config_file = src_path / "application" / "interfaces" / "configuration" / "configuration.py"
        print(f"File exists: {config_file.exists()}")
        
        # List directory contents
        config_dir = src_path / "application" / "interfaces" / "configuration"
        if config_dir.exists():
            print(f"Contents of {config_dir}:")
            for item in config_dir.iterdir():
                print(f"  - {item.name}")

if __name__ == "__main__":
    main()