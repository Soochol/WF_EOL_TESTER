#!/usr/bin/env python3
"""
Debug the specific configuration.configuration module that keeps failing on Windows
"""

import sys
from pathlib import Path

def debug_configuration_module():
    print("=== Configuration Module Debug ===")
    
    # Setup path
    current_dir = Path(__file__).parent
    src_path = current_dir / "src"
    sys.path.insert(0, str(src_path))
    
    # Check if the file exists
    config_file = src_path / "application" / "interfaces" / "configuration" / "configuration.py"
    print(f"Configuration file path: {config_file}")
    print(f"File exists: {config_file.exists()}")
    
    if config_file.exists():
        try:
            # Try to read the file
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"File size: {len(content)} bytes")
            print(f"Number of lines: {len(content.splitlines())}")
            
            # Check for any problematic content
            if '\r\n' in content:
                print("⚠️  File has Windows line endings (CRLF)")
            elif '\r' in content:
                print("⚠️  File has old Mac line endings (CR)")  
            else:
                print("✅ File has Unix line endings (LF)")
                
            # Show first few lines
            lines = content.splitlines()
            print("\nFirst 10 lines of the file:")
            for i, line in enumerate(lines[:10], 1):
                print(f"  {i:2d}: {repr(line)}")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return
    else:
        print("❌ Configuration file does not exist!")
        
        # Check what's in the configuration directory
        config_dir = src_path / "application" / "interfaces" / "configuration"
        if config_dir.exists():
            print(f"\nContents of {config_dir}:")
            for item in config_dir.iterdir():
                print(f"  - {item.name} ({'file' if item.is_file() else 'directory'})")
        else:
            print(f"❌ Configuration directory does not exist: {config_dir}")
        return
    
    # Try to import the specific problematic module
    print("\n=== Testing Direct Import ===")
    try:
        # Test the exact import that's failing
        from application.interfaces.configuration.configuration import Configuration
        print("✅ Direct import successful!")
        print(f"Configuration class: {Configuration}")
    except Exception as e:
        print(f"❌ Direct import failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Try alternative import approaches
        print("\n=== Trying Alternative Import Methods ===")
        
        # Method 1: Import module first, then get class
        try:
            import application.interfaces.configuration.configuration as config_module
            Configuration = getattr(config_module, 'Configuration', None)
            if Configuration:
                print("✅ Alternative method 1 successful!")
            else:
                print("❌ Configuration class not found in module")
        except Exception as e2:
            print(f"❌ Alternative method 1 failed: {e2}")
        
        # Method 2: Import using importlib
        try:
            import importlib
            config_module = importlib.import_module('application.interfaces.configuration.configuration')
            Configuration = getattr(config_module, 'Configuration', None)
            if Configuration:
                print("✅ Alternative method 2 (importlib) successful!")
            else:
                print("❌ Configuration class not found via importlib")
        except Exception as e3:
            print(f"❌ Alternative method 2 failed: {e3}")

if __name__ == "__main__":
    debug_configuration_module()