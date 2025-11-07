"""
Quick Test: Mock Power Analyzer Integration Improvements

Verifies that the mock now calculates energy based on actual elapsed time
instead of returning fixed values.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.implementation.hardware.power_analyzer.mock.mock_power_analyzer import (
    MockPowerAnalyzer,
)


async def test_mock_integration():
    """Test mock power analyzer integration with time-based calculation"""

    print("=" * 80)
    print("MOCK POWER ANALYZER INTEGRATION TEST")
    print("=" * 80)
    print()

    # Create mock analyzer
    print("Step 1: Creating mock power analyzer...")
    analyzer = MockPowerAnalyzer(
        host="192.168.1.100",
        port=10001,
        timeout=5.0,
        element=1,
    )
    print("  [OK] Mock created")
    print()

    # Connect
    print("Step 2: Connecting...")
    await analyzer.connect()
    print("  [OK] Connected")
    print()

    # Test 1: Short integration (1 second)
    print("=" * 80)
    print("TEST 1: Short Integration (1 second)")
    print("=" * 80)
    print()

    await analyzer.setup_integration(mode="normal", timer=3600)
    await analyzer.reset_integration()
    await analyzer.start_integration()

    print("  Integration started, waiting 1 second...")
    await asyncio.sleep(1.0)

    await analyzer.stop_integration()
    data1 = await analyzer.get_integration_data()

    print(f"  [RESULT] Active Energy: {data1['active_energy_wh']:.6f} Wh")
    print(f"  [RESULT] Apparent Energy: {data1['apparent_energy_vah']:.6f} VAh")
    print(f"  [RESULT] Reactive Energy: {data1['reactive_energy_varh']:.6f} varh")
    print()

    # Expected: ~60W * (1s / 3600s/h) = ~0.0167 Wh
    expected_wh_1s = 60.0 * (1.0 / 3600.0)
    print(f"  [EXPECTED] ~{expected_wh_1s:.6f} Wh (60W × 1s / 3600s/h)")
    print()

    # Test 2: Medium integration (5 seconds)
    print("=" * 80)
    print("TEST 2: Medium Integration (5 seconds)")
    print("=" * 80)
    print()

    await analyzer.reset_integration()
    await analyzer.start_integration()

    print("  Integration started, waiting 5 seconds...")
    await asyncio.sleep(5.0)

    await analyzer.stop_integration()
    data2 = await analyzer.get_integration_data()

    print(f"  [RESULT] Active Energy: {data2['active_energy_wh']:.6f} Wh")
    print(f"  [RESULT] Apparent Energy: {data2['apparent_energy_vah']:.6f} VAh")
    print(f"  [RESULT] Reactive Energy: {data2['reactive_energy_varh']:.6f} varh")
    print()

    # Expected: ~60W * (5s / 3600s/h) = ~0.0833 Wh
    expected_wh_5s = 60.0 * (5.0 / 3600.0)
    print(f"  [EXPECTED] ~{expected_wh_5s:.6f} Wh (60W × 5s / 3600s/h)")
    print()

    # Test 3: Long integration (10 seconds)
    print("=" * 80)
    print("TEST 3: Long Integration (10 seconds)")
    print("=" * 80)
    print()

    await analyzer.reset_integration()
    await analyzer.start_integration()

    print("  Integration started, waiting 10 seconds...")
    await asyncio.sleep(10.0)

    await analyzer.stop_integration()
    data3 = await analyzer.get_integration_data()

    print(f"  [RESULT] Active Energy: {data3['active_energy_wh']:.6f} Wh")
    print(f"  [RESULT] Apparent Energy: {data3['apparent_energy_vah']:.6f} VAh")
    print(f"  [RESULT] Reactive Energy: {data3['reactive_energy_varh']:.6f} varh")
    print()

    # Expected: ~60W * (10s / 3600s/h) = ~0.1667 Wh
    expected_wh_10s = 60.0 * (10.0 / 3600.0)
    print(f"  [EXPECTED] ~{expected_wh_10s:.6f} Wh (60W × 10s / 3600s/h)")
    print()

    # Verify proportional scaling
    print("=" * 80)
    print("VERIFICATION: Proportional Scaling")
    print("=" * 80)
    print()

    # Ratio should be approximately 1:5:10 (accounting for ±2% noise)
    ratio_2_to_1 = data2["active_energy_wh"] / data1["active_energy_wh"]
    ratio_3_to_1 = data3["active_energy_wh"] / data1["active_energy_wh"]

    print(f"  Energy ratio (5s / 1s): {ratio_2_to_1:.2f} (expected: ~5.0)")
    print(f"  Energy ratio (10s / 1s): {ratio_3_to_1:.2f} (expected: ~10.0)")
    print()

    # Check if ratios are within acceptable range (±10% due to random noise)
    checks = [
        ("1s energy in expected range", 0.014 < data1["active_energy_wh"] < 0.020),
        ("5s energy in expected range", 0.070 < data2["active_energy_wh"] < 0.095),
        ("10s energy in expected range", 0.140 < data3["active_energy_wh"] < 0.190),
        ("5s/1s ratio approximately 5:1", 4.5 < ratio_2_to_1 < 5.5),
        ("10s/1s ratio approximately 10:1", 9.0 < ratio_3_to_1 < 11.0),
    ]

    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print()

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
        print()
        print("✅ Mock now calculates energy based on actual elapsed time")
        print("✅ Energy scales proportionally with time (E = P × t)")
        print("✅ Much more accurate than old fixed-value implementation")
    else:
        print("=" * 80)
        print("SOME TESTS FAILED")
        print("=" * 80)

    # Cleanup
    await analyzer.disconnect()

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_mock_integration())
    sys.exit(0 if success else 1)
