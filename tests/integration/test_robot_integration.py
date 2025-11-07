"""
Integration Test for Robot Integration in Heating Cooling Time Test

Tests the new robot functionality with mock hardware.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from application.containers.simple_reloadable_container import SimpleReloadableContainer
from application.use_cases.heating_cooling_time_test.input import HeatingCoolingTimeTestInput
from domain.value_objects.heating_cooling_configuration import HeatingCoolingConfiguration
from domain.value_objects.dut_command_info import DUTCommandInfo
import yaml


async def run_integration_test():
    """Run integration test with mock hardware"""

    print("=" * 80)
    print("INTEGRATION TEST: Robot Integration in Heating Cooling Time Test")
    print("=" * 80)
    print()

    # Step 1: Load configuration
    print("Step 1: Loading configuration from YAML...")
    with open("configuration/heating_cooling_time_test.yaml", "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # Override for quick testing - only 2 cycles
    config_data["repeat_count"] = 2
    config_data["heating_wait_time"] = 0.5  # Shorter wait times for testing
    config_data["cooling_wait_time"] = 0.5
    config_data["power_monitoring_enabled"] = True
    config_data["power_monitoring_interval"] = 0.1

    hc_config = HeatingCoolingConfiguration.from_dict(config_data)

    print(f"  [OK] Configuration loaded")
    print(f"    - Enable Robot: {hc_config.enable_robot}")
    print(f"    - Enable Force Measurement: {hc_config.enable_force_measurement}")
    print(f"    - Measurement Positions: {hc_config.measurement_positions}")
    print(f"    - Repeat Count: {hc_config.repeat_count} (overridden for testing)")
    print()

    # Step 2: Initialize container with mock hardware
    print("Step 2: Initializing dependency injection container...")
    print("  (Using mock hardware for testing)")
    container = SimpleReloadableContainer.create()
    print("  [OK] Container created with mock hardware")
    print()

    # Step 3: Get use case
    print("Step 3: Getting HeatingCoolingTimeTestUseCase...")
    use_case = container.heating_cooling_time_test_use_case()
    print("  [OK] Use case retrieved")
    print()

    # Step 4: Execute test
    print("Step 4: Executing Heating Cooling Time Test...")
    print("  Expected sequence per cycle:")
    print("    1. Heating (38°C → 52°C)")
    print("    2. Force Measurement at positions:")
    for pos in hc_config.measurement_positions:
        print(f"       - {pos} μm")
    print("    3. Robot return to initial position")
    print("    4. Cooling (52°C → 38°C)")
    print()

    try:
        # Create DUT info for test
        dut_info = DUTCommandInfo(
            dut_id="TEST_DEVICE_001",
            model_number="HC_TEST_ROBOT",
            serial_number="SN_INTEGRATION_TEST",
            manufacturer="Test Manufacturer",
        )

        # Create input
        test_input = HeatingCoolingTimeTestInput(
            dut_info=dut_info,
            operator_id="TEST_OPERATOR",
            repeat_count=2,  # Quick test
        )

        # Execute test
        result = await use_case.execute(test_input)

        # Step 5: Verify results
        print()
        print("=" * 80)
        print("TEST EXECUTION COMPLETED")
        print("=" * 80)
        print()

        print(f"Status: {result.test_status}")
        print(f"Success: {result.is_success}")

        if result.error_message:
            print(f"Error Message: {result.error_message}")

        print()
        print("=== Measurements Summary ===")
        measurements = result.measurements

        # Heating/Cooling counts
        heating_count = len(measurements.get("heating_measurements", []))
        cooling_count = len(measurements.get("cooling_measurements", []))
        force_count = len(measurements.get("force_measurements", []))

        print(f"Heating cycles completed: {heating_count}")
        print(f"Cooling cycles completed: {cooling_count}")
        print(f"Force measurements taken: {force_count}")

        # Force measurements detail
        if force_count > 0:
            print()
            print("=== Force Measurements ===")
            force_measurements = measurements.get("force_measurements", [])
            for i, fm in enumerate(force_measurements[:6], 1):  # Show first 6
                print(
                    f"  [{i}] Cycle {fm['cycle']}, "
                    f"Position: {fm['position_um']:.0f} μm, "
                    f"Force: {fm['force_kgf']:.3f} kgf ({fm['force_n']:.3f} N)"
                )
            if force_count > 6:
                print(f"  ... and {force_count - 6} more measurements")

        # Statistics
        print()
        print("=== Statistics ===")
        stats = measurements.get("statistics", {})
        print(f"Average heating time: {stats.get('average_heating_time_ms', 0):.1f} ms")
        print(f"Average cooling time: {stats.get('average_cooling_time_ms', 0):.1f} ms")

        if stats.get("total_force_measurements", 0) > 0:
            print(f"Total force measurements: {stats.get('total_force_measurements', 0)}")
            print(
                f"Average force: {stats.get('average_force_kgf', 0):.3f} kgf "
                f"({stats.get('average_force_n', 0):.3f} N)"
            )
            print(
                f"Min force: {stats.get('min_force_kgf', 0):.3f} kgf "
                f"({stats.get('min_force_n', 0):.3f} N)"
            )
            print(
                f"Max force: {stats.get('max_force_kgf', 0):.3f} kgf "
                f"({stats.get('max_force_n', 0):.3f} N)"
            )

        # Power monitoring
        print()
        print("=== Power Monitoring ===")
        print(f"Average power: {stats.get('full_cycle_average_power_watts', 0):.1f} W")
        print(f"Peak power: {stats.get('full_cycle_peak_power_watts', 0):.1f} W")
        print(f"Total energy: {stats.get('total_energy_consumed_wh', 0):.3f} Wh")
        print(f"Power samples: {stats.get('power_sample_count', 0)}")

        # Verification
        print()
        print("=" * 80)
        print("VERIFICATION")
        print("=" * 80)

        expected_force_measurements = hc_config.repeat_count * len(
            hc_config.measurement_positions
        )

        checks = [
            ("Result is successful", result.is_success),
            (
                f"Heating cycles match repeat count ({heating_count} == {hc_config.repeat_count})",
                heating_count == hc_config.repeat_count,
            ),
            (
                f"Cooling cycles match repeat count ({cooling_count} == {hc_config.repeat_count})",
                cooling_count == hc_config.repeat_count,
            ),
            (
                f"Force measurements correct "
                f"({force_count} == {expected_force_measurements} "
                f"= {hc_config.repeat_count} cycles × {len(hc_config.measurement_positions)} positions)",
                force_count == expected_force_measurements,
            ),
            ("Statistics calculated", len(stats) > 0),
            ("Power monitoring data present", stats.get("power_sample_count", 0) > 0),
        ]

        all_passed = True
        for check_name, check_result in checks:
            status = "[PASS]" if check_result else "[FAIL]"
            print(f"{status}: {check_name}")
            if not check_result:
                all_passed = False

        print()
        if all_passed:
            print("=" * 80)
            print("ALL TESTS PASSED!")
            print("=" * 80)
        else:
            print("=" * 80)
            print("SOME TESTS FAILED")
            print("=" * 80)

        return result.is_success and all_passed

    except Exception as e:
        print()
        print("=" * 80)
        print("TEST EXECUTION FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        print()
        print("Cleaning up container...")
        # Container cleanup is automatic via dependency_injector
        print("[OK] Cleanup completed")


if __name__ == "__main__":
    success = asyncio.run(run_integration_test())
    sys.exit(0 if success else 1)
