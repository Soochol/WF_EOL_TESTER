#!/usr/bin/env python3
"""
Debug the exact import chain that's failing in main.py
"""

import sys
from pathlib import Path

def test_import_chain():
    print("=== Import Chain Debug ===")
    
    # Setup path like main.py does
    current_dir = Path(__file__).parent
    src_path = current_dir / "src"
    sys.path.insert(0, str(src_path))
    
    # Follow the exact same import path as the error
    import_steps = [
        "1. Import application.services.button_monitoring_service",
        "2. This triggers application.services.__init__.py", 
        "3. Which imports application.services.repository_service",
        "4. Which imports application.interfaces.repository.test_result_repository",
        "5. Which triggers application.interfaces.__init__.py",
        "6. Which imports application.interfaces.configuration.configuration (FAILS HERE)"
    ]
    
    print("Import chain that should execute:")
    for step in import_steps:
        print(f"  {step}")
    
    print("\n=== Testing step by step ===")
    
    try:
        print("Step 1: Testing direct configuration import...")
        from application.interfaces.configuration.configuration import Configuration
        print("  ✅ Direct config import works")
    except Exception as e:
        print(f"  ❌ Direct config import failed: {e}")
        return
    
    try:
        print("Step 2: Testing application.interfaces import...")
        import application.interfaces
        print("  ✅ application.interfaces works")
    except Exception as e:
        print(f"  ❌ application.interfaces failed: {e}")
        print(f"     Error type: {type(e).__name__}")
        
        # Check if the problem is in the __init__.py file
        print("\n=== Checking application.interfaces.__init__.py ===")
        init_file = src_path / "application" / "interfaces" / "__init__.py"
        with open(init_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("Contents of __init__.py:")
        for i, line in enumerate(lines, 1):
            print(f"  {i:2d}: {line.rstrip()}")
        
        return
    
    try:
        print("Step 3: Testing repository service import...")
        from application.services.repository_service import RepositoryService
        print("  ✅ repository_service works")
    except Exception as e:
        print(f"  ❌ repository_service failed: {e}")
        return
    
    try:
        print("Step 4: Testing button monitoring service import...")
        from application.services.button_monitoring_service import ButtonMonitoringService
        print("  ✅ button_monitoring_service works")
    except Exception as e:
        print(f"  ❌ button_monitoring_service failed: {e}")
        return
    
    print("\n✅ All imports in the chain work!")

if __name__ == "__main__":
    test_import_chain()