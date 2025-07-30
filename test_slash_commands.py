#!/usr/bin/env python3
"""
Test Script for Slash Command System

This script tests the slash command functionality with mock hardware
to ensure everything is working properly before integration.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ui.cli.slash_command_executor import create_slash_executor_from_config


async def test_basic_commands():
    """Test basic slash command functionality"""
    print("Creating slash command executor...")
    executor = await create_slash_executor_from_config()
    
    test_commands = [
        "/help",
        "/all status", 
        "/robot status",
        "/robot connect",
        "/mcu status",
        "/mcu connect",
        "/mcu temp",
        "/loadcell status",
        "/power status"
    ]
    
    print("\nTesting basic commands...")
    results = await executor.execute_command_list(test_commands)
    
    print(f"\nTest Results:")
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    print(f"Successful commands: {successful}/{total}")
    
    if successful == total:
        print("✓ All tests passed!")
        return True
    else:
        print("✗ Some tests failed!")
        return False


async def test_invalid_commands():
    """Test invalid command handling"""
    print("\nTesting invalid command handling...")
    executor = await create_slash_executor_from_config()
    
    invalid_commands = [
        "/invalid command",
        "/robot badsubcommand", 
        "/mcu temp invalid_number",
        "not a slash command"
    ]
    
    for cmd in invalid_commands:
        print(f"Testing invalid command: {cmd}")
        result = await executor.execute_single_command(cmd)
        if result:
            print(f"  ✗ Command should have failed but didn't: {cmd}")
            return False
        else:
            print(f"  ✓ Command properly failed: {cmd}")
    
    print("✓ Invalid command handling works correctly!")
    return True


async def main():
    """Main test function"""
    print("Slash Command System Test")
    print("=" * 40)
    
    try:
        # Test basic functionality
        basic_test_passed = await test_basic_commands()
        
        # Test invalid command handling
        invalid_test_passed = await test_invalid_commands()
        
        # Overall result
        if basic_test_passed and invalid_test_passed:
            print("\n🎉 All tests passed! Slash command system is working correctly.")
            return 0
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test execution failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)