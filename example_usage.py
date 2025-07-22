"""
Example Usage of Clean Architecture EOL Tester

This file demonstrates how to use the Clean Architecture implementation
of the EOL Tester system.
"""

import asyncio
from loguru import logger

from src.integration.application_factory import ApplicationFactory
from src.domain.enums.test_types import TestType


async def example_basic_test_execution():
    """Example: Basic EOL test execution"""
    print("\n" + "="*60)
    print("Example: Basic EOL Test Execution")
    print("="*60)
    
    # Create application with development configuration
    config = ApplicationFactory.create_development_configuration()
    container = ApplicationFactory.create_application(config_dict=config)
    
    try:
        # Get EOL test controller
        from src.presentation.controllers.eol_test_controller import EOLTestController
        eol_test_controller = container.resolve(EOLTestController)
        
        # Execute a comprehensive test
        result = await eol_test_controller.execute_test(
            dut_id="DUT_001",
            test_type="COMPREHENSIVE",
            operator_id="OP_001",
            dut_model_number="Model_X1",
            dut_serial_number="SN123456",
            dut_manufacturer="ACME Corp",
            test_configuration={
                "force_samples": 5,
                "force_interval_ms": 200,
                "target_voltage": 12.0,
                "current_limit": 2.0
            },
            pass_criteria={
                "force_average": {"min": 8.0, "max": 15.0},
                "voltage_average": {"min": 11.5, "max": 12.5}
            },
            operator_notes="Example test execution"
        )
        
        # Display result
        if result['success']:
            print(f"✓ Test completed successfully!")
            print(f"  Test ID: {result['test_id']}")
            print(f"  Status: {result['status']}")
            print(f"  Passed: {result['passed']}")
            print(f"  Duration: {result['execution_duration_ms']:.1f} ms")
            print(f"  Measurements: {result['measurement_count']}")
        else:
            print(f"✗ Test failed: {result['error']['message']}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        container.shutdown()


async def example_hardware_operations():
    """Example: Hardware management operations"""
    print("\n" + "="*60)
    print("Example: Hardware Management Operations")
    print("="*60)
    
    # Create application
    config = ApplicationFactory.create_development_configuration()
    container = ApplicationFactory.create_application(config_dict=config)
    
    try:
        # Get hardware controller
        from src.presentation.controllers.hardware_controller import HardwareController
        hardware_controller = container.resolve(HardwareController)
        
        # Check hardware status
        print("1. Checking hardware status...")
        status_result = await hardware_controller.get_hardware_status()
        if status_result['success']:
            loadcell_connected = status_result['data']['loadcell']['connected']
            power_connected = status_result['data']['power_supply']['connected']
            print(f"   LoadCell: {'Connected' if loadcell_connected else 'Disconnected'}")
            print(f"   Power Supply: {'Connected' if power_connected else 'Disconnected'}")
        
        # Connect hardware if needed
        print("2. Connecting to hardware...")
        if not loadcell_connected:
            connect_result = await hardware_controller.connect_hardware("loadcell")
            print(f"   LoadCell connection: {'Success' if connect_result['success'] else 'Failed'}")
        
        if not power_connected:
            connect_result = await hardware_controller.connect_hardware("power_supply")
            print(f"   Power supply connection: {'Success' if connect_result['success'] else 'Failed'}")
        
        # Perform measurements
        print("3. Taking force measurement...")
        force_result = await hardware_controller.read_loadcell_force(num_samples=3)
        if force_result['success']:
            stats = force_result['data'].get('statistics', {})
            if stats:
                avg = stats['average']
                print(f"   Average force: {avg['value']} {avg['unit']}")
        
        print("4. Configuring power output...")
        power_config_result = await hardware_controller.set_power_output(
            voltage=12.0,
            current_limit=1.5,
            enabled=False  # Keep disabled for safety
        )
        if power_config_result['success']:
            print("   Power configuration: Success")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        container.shutdown()


async def example_cli_usage():
    """Example: Using CLI interfaces programmatically"""
    print("\n" + "="*60)
    print("Example: CLI Interface Usage")
    print("="*60)
    
    # Create CLI application
    eol_test_cli, hardware_cli, container = ApplicationFactory.create_cli_application()
    
    try:
        # Example CLI operations would go here
        # Note: These are typically used interactively, but can be scripted
        
        print("CLI interfaces created successfully")
        print(f"  EOL Test CLI: {type(eol_test_cli).__name__}")
        print(f"  Hardware CLI: {type(hardware_cli).__name__}")
        
        # CLI methods can be called programmatically if needed
        # await hardware_cli.hardware_status_interactive()
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        container.shutdown()


async def example_api_usage():
    """Example: Using API interfaces"""
    print("\n" + "="*60)
    print("Example: API Interface Usage")
    print("="*60)
    
    # Create API application
    eol_test_api, hardware_api, container = ApplicationFactory.create_api_application()
    
    try:
        # Example API request data
        test_request = {
            "dut_id": "API_DUT_001",
            "test_type": "FORCE_ONLY",
            "operator_id": "API_OP_001",
            "test_configuration": {
                "force_samples": 3,
                "force_interval_ms": 100
            }
        }
        
        # Execute test via API
        response_body, status_code, headers = await eol_test_api.execute_test(test_request)
        
        print(f"API Test Execution:")
        print(f"  Status Code: {status_code}")
        print(f"  Success: {response_body['success']}")
        
        if response_body['success']:
            test_data = response_body['data']
            print(f"  Test ID: {test_data['test_id']}")
            print(f"  Test Status: {test_data['status']}")
        
        # Get hardware status via API
        response_body, status_code, headers = await hardware_api.get_hardware_status()
        print(f"API Hardware Status:")
        print(f"  Status Code: {status_code}")
        print(f"  Success: {response_body['success']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        container.shutdown()


async def example_configuration_management():
    """Example: Configuration management"""
    print("\n" + "="*60)
    print("Example: Configuration Management")
    print("="*60)
    
    # Create different configurations
    print("1. Creating development configuration...")
    dev_config = ApplicationFactory.create_development_configuration()
    print(f"   Debug mode: {dev_config['application']['debug_mode']}")
    print(f"   Test timeout: {dev_config['application']['test_timeout']}s")
    
    print("2. Creating production configuration...")
    prod_config = ApplicationFactory.create_production_configuration()
    print(f"   Debug mode: {prod_config['application']['debug_mode']}")
    print(f"   Test timeout: {prod_config['application']['test_timeout']}s")
    
    print("3. Creating test configuration...")
    test_config = ApplicationFactory.create_test_configuration()
    print(f"   Hardware type: {test_config['hardware']['loadcell']['type']}")
    print(f"   Test timeout: {test_config['application']['test_timeout']}s")
    
    # Save configuration example
    try:
        ApplicationFactory.save_configuration(dev_config, "example_dev_config.json")
        print("4. Development configuration saved to example_dev_config.json")
    except Exception as e:
        print(f"   Error saving configuration: {e}")


def example_domain_objects():
    """Example: Using domain objects directly"""
    print("\n" + "="*60)
    print("Example: Domain Objects Usage")
    print("="*60)
    
    # Import domain objects
    from src.domain.entities.eol_test import EOLTest
    from src.domain.entities.dut import DUT
    from src.domain.value_objects.identifiers import TestId, DUTId, OperatorId
    from src.domain.value_objects.measurements import ForceValue, VoltageValue
    from src.domain.enums.measurement_units import MeasurementUnit
    from src.domain.enums.test_types import TestType
    
    try:
        # Create DUT
        dut = DUT(
            dut_id=DUTId("EXAMPLE_DUT_001"),
            model_number="ExampleModel",
            serial_number="EX123456",
            manufacturer="Example Corp"
        )
        print(f"1. Created DUT: {dut.dut_id}")
        
        # Create test
        test_id = TestId.generate()
        eol_test = EOLTest(
            test_id=test_id,
            dut=dut,
            test_type=TestType.COMPREHENSIVE,
            operator_id=OperatorId("EXAMPLE_OP_001")
        )
        print(f"2. Created EOL Test: {eol_test.test_id}")
        print(f"   Test Type: {eol_test.test_type.value}")
        print(f"   Status: {eol_test.status.value}")
        
        # Create measurements
        force_value = ForceValue(12.5, MeasurementUnit.NEWTON)
        voltage_value = VoltageValue(12.0, MeasurementUnit.VOLT)
        
        print(f"3. Created measurements:")
        print(f"   Force: {force_value}")
        print(f"   Voltage: {voltage_value}")
        
        # Convert units
        force_in_kg = force_value.to_kilogram_force()
        voltage_in_mv = voltage_value.to_millivolts()
        
        print(f"4. Unit conversions:")
        print(f"   Force in kgf: {force_in_kg:.3f}")
        print(f"   Voltage in mV: {voltage_in_mv:.1f}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


async def main():
    """Run all examples"""
    print("Clean Architecture EOL Tester - Example Usage")
    print("=" * 80)
    
    # Domain objects example (synchronous)
    example_domain_objects()
    
    # Configuration management example (synchronous)  
    await example_configuration_management()
    
    # Async examples
    await example_basic_test_execution()
    await example_hardware_operations()
    await example_cli_usage()
    await example_api_usage()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == "__main__":
    # Setup basic logging
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<level>{level}: {message}</level>\n"
    )
    
    # Run examples
    asyncio.run(main())