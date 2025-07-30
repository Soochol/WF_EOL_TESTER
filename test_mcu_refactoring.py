#!/usr/bin/env python3
"""
Test script for Phase 3 MCU refactoring verification
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_mcu_config():
    """Test updated MCUConfig with new parameters"""
    from domain.value_objects.hardware_configuration import MCUConfig
    
    print("Testing MCUConfig with new parameters...")
    
    # Test default configuration
    default_config = MCUConfig()
    print(f"Default config: {default_config}")
    
    # Test custom configuration
    custom_config = MCUConfig(
        model="LMA",
        port="COM5",
        baudrate=9600,
        timeout=3.0,
        default_temperature=30.0,
        default_fan_speed=75.0,
        temperature_drift_rate=0.2,
        response_delay=0.05,
        connection_delay=0.15,
        max_temperature=200.0,
        min_temperature=-50.0,
        max_fan_speed=100.0
    )
    print(f"Custom config: {custom_config}")
    
    return True

def test_hardware_configuration():
    """Test HardwareConfiguration to_dict with new MCU parameters"""
    from domain.value_objects.hardware_configuration import HardwareConfiguration
    
    print("\nTesting HardwareConfiguration.to_dict()...")
    
    config = HardwareConfiguration()
    config_dict = config.to_dict()
    
    # Check that MCU section has all new parameters
    mcu_dict = config_dict["mcu"]
    required_params = [
        "model", "port", "baudrate", "timeout",
        "default_temperature", "default_fan_speed",
        "temperature_drift_rate", "response_delay", "connection_delay",
        "max_temperature", "min_temperature", "max_fan_speed"
    ]
    
    for param in required_params:
        if param not in mcu_dict:
            print(f"ERROR: Missing parameter {param} in MCU config dict")
            return False
        print(f"  {param}: {mcu_dict[param]}")
    
    return True

def test_mcu_services():
    """Test MCU service creation with Dict config"""
    from infrastructure.factory import ServiceFactory
    
    print("\nTesting MCU service creation...")
    
    # Test Mock MCU service
    mock_config = {
        "model": "MOCK",
        "port": "COM4",
        "baudrate": 115200,
        "timeout": 2.0,
        "default_temperature": 25.0,
        "default_fan_speed": 50.0,
        "temperature_drift_rate": 0.1,
        "response_delay": 0.1,
        "connection_delay": 0.1,
        "max_temperature": 150.0,
        "min_temperature": -40.0,
        "max_fan_speed": 100.0
    }
    
    try:
        mock_service = ServiceFactory.create_mcu_service(mock_config)
        print(f"Mock MCU service created: {type(mock_service).__name__}")
    except Exception as e:
        print(f"ERROR creating Mock MCU service: {e}")
        return False
    
    # Test LMA MCU service
    lma_config = {
        "model": "LMA",
        "port": "COM5",
        "baudrate": 9600,
        "timeout": 3.0,
        "default_temperature": 30.0,
        "default_fan_speed": 75.0,
        "max_temperature": 200.0,
        "min_temperature": -50.0,
        "max_fan_speed": 100.0
    }
    
    try:
        lma_service = ServiceFactory.create_mcu_service(lma_config)
        print(f"LMA MCU service created: {type(lma_service).__name__}")
    except Exception as e:
        print(f"ERROR creating LMA MCU service: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=== Phase 3 MCU Refactoring Verification ===\n")
    
    tests = [
        ("MCUConfig", test_mcu_config),
        ("HardwareConfiguration", test_hardware_configuration),
        ("MCU Services", test_mcu_services),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"{test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print(f"\n=== Results ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Phase 3 refactoring is successful.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())