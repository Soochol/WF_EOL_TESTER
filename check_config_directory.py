#!/usr/bin/env python3
"""
Check the configuration directory structure on Windows
"""

import sys
from pathlib import Path

def check_config_directory():
    print("=== Configuration Directory Check ===")
    
    current_dir = Path(__file__).parent
    src_path = current_dir / "src"
    sys.path.insert(0, str(src_path))
    
    # Check the exact directory structure
    config_dir = src_path / "application" / "interfaces" / "configuration"
    
    print(f"Configuration directory: {config_dir}")
    print(f"Directory exists: {config_dir.exists()}")
    print(f"Is directory: {config_dir.is_dir()}")
    
    if config_dir.exists():
        print(f"\nDirectory contents:")
        items = list(config_dir.iterdir())
        if not items:
            print("  ❌ Directory is EMPTY!")
        else:
            for item in sorted(items):
                size = item.stat().st_size if item.is_file() else 'DIR'
                print(f"  - {item.name} ({size} bytes)")
        
        # Check specific required files
        required_files = ['__init__.py', 'configuration.py', 'profile_preference.py']
        print(f"\nRequired files check:")
        for filename in required_files:
            filepath = config_dir / filename
            exists = filepath.exists()
            if exists:
                size = filepath.stat().st_size
                print(f"  ✅ {filename} ({size} bytes)")
            else:
                print(f"  ❌ {filename} - MISSING")
        
        # Try to read the __init__.py content
        init_file = config_dir / "__init__.py"
        if init_file.exists():
            print(f"\n__init__.py content:")
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"Size: {len(content)} bytes")
                lines = content.splitlines()
                for i, line in enumerate(lines[:10], 1):
                    print(f"  {i:2d}: {line}")
            except Exception as e:
                print(f"  ❌ Error reading __init__.py: {e}")
        
        # Test import manually
        print(f"\n=== Manual Import Test ===")
        try:
            import application.interfaces.configuration as config_pkg
            print(f"✅ Import successful")
            print(f"   __file__: {getattr(config_pkg, '__file__', 'None')}")
            print(f"   __path__: {getattr(config_pkg, '__path__', 'None')}")
            print(f"   __all__: {getattr(config_pkg, '__all__', 'None')}")
            
            # Check what's actually in the package
            print(f"   dir(): {[x for x in dir(config_pkg) if not x.startswith('_')]}")
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    else:
        print(f"\n❌ Configuration directory does not exist!")
        
        # Check parent directories
        interfaces_dir = src_path / "application" / "interfaces"
        app_dir = src_path / "application"
        
        print(f"\nParent directories:")
        print(f"  application/: {app_dir.exists()}")
        print(f"  interfaces/: {interfaces_dir.exists()}")
        
        if interfaces_dir.exists():
            print(f"\ninterfaces/ contents:")
            for item in sorted(interfaces_dir.iterdir()):
                print(f"  - {item.name}")

if __name__ == "__main__":
    check_config_directory()