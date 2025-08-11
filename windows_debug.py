#!/usr/bin/env python3
"""
Windows-specific debugging script to find the root cause
"""

import sys
import os
from pathlib import Path

def debug_windows_import_issue():
    print("=== Windows Import Issue Diagnosis ===")
    
    # Setup path exactly like main.py
    current_dir = Path(__file__).parent
    src_path = current_dir / "src"
    
    print(f"Current directory: {current_dir}")
    print(f"Source path: {src_path}")
    print(f"Source path exists: {src_path.exists()}")
    
    # Add to sys.path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        print(f"Added to sys.path: {src_path}")
    
    print(f"\nFirst 5 sys.path entries:")
    for i, path in enumerate(sys.path[:5]):
        print(f"  {i}: {path}")
    
    # Test the exact file path that's failing
    config_file = src_path / "application" / "interfaces" / "configuration" / "configuration.py"
    print(f"\nConfiguration file: {config_file}")
    print(f"Exists: {config_file.exists()}")
    
    if config_file.exists():
        print(f"Size: {config_file.stat().st_size} bytes")
        
        # Check the entire directory structure
        print(f"\nDirectory structure check:")
        app_dir = src_path / "application"
        print(f"  application/: {app_dir.exists()}")
        
        interfaces_dir = app_dir / "interfaces" 
        print(f"  interfaces/: {interfaces_dir.exists()}")
        
        config_dir = interfaces_dir / "configuration"
        print(f"  configuration/: {config_dir.exists()}")
        
        # Check __init__.py files
        files_to_check = [
            app_dir / "__init__.py",
            interfaces_dir / "__init__.py", 
            config_dir / "__init__.py"
        ]
        
        print(f"\n__init__.py files:")
        for init_file in files_to_check:
            exists = init_file.exists()
            size = init_file.stat().st_size if exists else 0
            print(f"  {init_file.relative_to(src_path)}: {exists} ({size} bytes)")
    
    # Try different import methods step by step
    print(f"\n=== Step-by-step import testing ===")
    
    # Test 1: Can we import the application package?
    try:
        import application
        print(f"✅ Step 1: import application - SUCCESS")
        print(f"   application.__file__: {getattr(application, '__file__', 'N/A')}")
    except Exception as e:
        print(f"❌ Step 1: import application - FAILED: {e}")
        return
    
    # Test 2: Can we import application.interfaces?
    try:
        import application.interfaces
        print(f"✅ Step 2: import application.interfaces - SUCCESS")
        print(f"   interfaces.__file__: {getattr(application.interfaces, '__file__', 'N/A')}")
    except Exception as e:
        print(f"❌ Step 2: import application.interfaces - FAILED: {e}")
        print(f"   This might be where the issue is!")
        return
    
    # Test 3: Can we import the configuration package?
    try:
        import application.interfaces.configuration
        print(f"✅ Step 3: import application.interfaces.configuration - SUCCESS")
        print(f"   config.__file__: {getattr(application.interfaces.configuration, '__file__', 'N/A')}")
    except Exception as e:
        print(f"❌ Step 3: import application.interfaces.configuration - FAILED: {e}")
        return
    
    # Test 4: Can we import the specific module?
    try:
        import application.interfaces.configuration.configuration
        print(f"✅ Step 4: import application.interfaces.configuration.configuration - SUCCESS")
        print(f"   module.__file__: {getattr(application.interfaces.configuration.configuration, '__file__', 'N/A')}")
    except Exception as e:
        print(f"❌ Step 4: import specific configuration module - FAILED: {e}")
        return
    
    # Test 5: Can we import the Configuration class?
    try:
        from application.interfaces.configuration.configuration import Configuration
        print(f"✅ Step 5: from ... import Configuration - SUCCESS")
        print(f"   Configuration: {Configuration}")
    except Exception as e:
        print(f"❌ Step 5: from ... import Configuration - FAILED: {e}")
        return
    
    print(f"\n🎉 All imports work! The issue might be intermittent or environment-specific.")

if __name__ == "__main__":
    debug_windows_import_issue()