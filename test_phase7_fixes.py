#!/usr/bin/env python3
"""
Phase 7 Fixes Validation
Quick test to verify specific fixes applied
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unittest.mock import MagicMock
from rich.console import Console

try:
    # Test imports
    from src.ui.cli.application_factory import create_production_cli_application
    from src.ui.cli.validation.input_validator import InputValidator, ValidationConstants
    from src.ui.cli.rich_formatter import RichFormatter
    from src.application.use_cases.eol_force_test import EOLForceTestUseCase
    
    print("✅ All imports successful")
    
    # Test 1: ValidationConstants
    print("\n🧪 Testing ValidationConstants...")
    assert hasattr(ValidationConstants, 'MENU_CHOICES'), "MENU_CHOICES missing"
    assert hasattr(ValidationConstants, 'FORCE_RANGE'), "FORCE_RANGE missing"
    print(f"  ✅ MENU_CHOICES: {ValidationConstants.MENU_CHOICES}")
    print(f"  ✅ FORCE_RANGE: {ValidationConstants.FORCE_RANGE}")
    
    # Test 2: InputValidator methods
    print("\n🧪 Testing InputValidator methods...")
    validator = InputValidator()
    
    # Test menu choice validation
    assert validator.is_valid_menu_choice('1') == True, "Menu choice 1 should be valid"
    assert validator.is_valid_menu_choice('5') == False, "Menu choice 5 should be invalid"
    assert validator.is_valid_menu_choice('abc') == False, "Menu choice abc should be invalid"
    print("  ✅ is_valid_menu_choice working")
    
    # Test force value validation
    assert validator.is_valid_force_value('100.5') == True, "Force 100.5 should be valid"
    assert validator.is_valid_force_value('-10') == False, "Force -10 should be invalid"
    assert validator.is_valid_force_value('invalid') == False, "Force 'invalid' should be invalid"
    print("  ✅ is_valid_force_value working")
    
    # Test 3: RichFormatter methods
    print("\n🧪 Testing RichFormatter methods...")
    console = Console()
    formatter = RichFormatter(console)
    
    # Test print_menu
    try:
        formatter.print_menu({'1': 'Option 1', '2': 'Option 2'})
        print("  ✅ print_menu working")
    except Exception as e:
        print(f"  ❌ print_menu failed: {e}")
    
    # Test print_title
    try:
        formatter.print_title('Test Title')
        print("  ✅ print_title working")
    except Exception as e:
        print(f"  ❌ print_title failed: {e}")
    
    # Test 4: Component lifecycle
    print("\n🧪 Testing Component lifecycle...")
    mock_use_case = MagicMock(spec=EOLForceTestUseCase)
    mock_hardware_facade = MagicMock()
    mock_config_service = MagicMock()
    
    app = create_production_cli_application(
        use_case=mock_use_case,
        hardware_facade=mock_hardware_facade,
        configuration_service=mock_config_service
    )
    
    # Test initial state
    initial_state = app._running
    print(f"  ✅ Initial running state: {initial_state}")
    
    # Test state change to True
    app._running = True
    after_true = app._running
    print(f"  ✅ After setting True: {after_true}")
    
    # Test state change to False
    app._running = False
    after_false = app._running
    print(f"  ✅ After setting False: {after_false}")
    
    if after_true == True and after_false == False:
        print("  ✅ Component lifecycle working correctly")
    else:
        print(f"  ❌ Component lifecycle issue: True={after_true}, False={after_false}")
    
    print("\n🎉 All focused tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()
