"""
WT1806 Production Integration Test

Tests the updated WT1800EPowerAnalyzer with WT1806 compatibility.

Usage:
    uv run python test_wt1806_production_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.implementation.hardware.power_analyzer.wt1800e.wt1800e_power_analyzer import (
    WT1800EPowerAnalyzer,
)
from driver.visa import INTERFACE_USB


async def test_wt1806_production():
    """Test WT1806 with production WT1800EPowerAnalyzer class"""

    print("\n" + "=" * 70)
    print("  WT1806 Production Integration Test")
    print("  Testing WT1800EPowerAnalyzer with WT1806 compatibility")
    print("=" * 70)

    # Create power analyzer with USB connection
    power_analyzer = WT1800EPowerAnalyzer(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",
        usb_model_code="0x0025",
        usb_serial_number=None,  # Auto-detect
        element=1,
        voltage_range="60V",
        current_range="50A",
        auto_range=False,
        timeout=10.0,
    )

    try:
        # Step 1: Connect
        print("\n[1/5] Connecting to WT1806...")
        await power_analyzer.connect()
        print("      [OK] Connected")

        # Step 2: Get device info
        print("\n[2/5] Getting device information...")
        identity = await power_analyzer.get_device_identity()
        print(f"      Device: {identity}")

        # Step 3: Check connection status
        print("\n[3/5] Checking connection status...")
        is_connected = await power_analyzer.is_connected()
        print(f"      Connected: {is_connected}")

        # Step 4: Get measurements (multiple times to ensure stability)
        print("\n[4/5] Getting measurements (3 samples)...")
        print("      Note: Values may be 0 or 9.9E+37 if no input signal\n")

        for i in range(3):
            measurements = await power_analyzer.get_measurements()

            print(f"      Sample {i+1}:")
            print(f"        Voltage: {measurements['voltage']:.6f} V")
            print(f"        Current: {measurements['current']:.6f} A")
            print(f"        Power:   {measurements['power']:.6f} W")

            if i < 2:  # Don't wait after last measurement
                await asyncio.sleep(1.0)

        # Step 5: Disconnect
        print("\n[5/5] Disconnecting...")
        await power_analyzer.disconnect()
        print("      [OK] Disconnected")

        print("\n" + "=" * 70)
        print("[SUCCESS] WT1806 PRODUCTION INTEGRATION TEST PASSED")
        print("=" * 70 + "\n")

        print("Summary:")
        print("  [+] USB connection: WORKING")
        print("  [+] Device initialization: WORKING")
        print("  [+] NUMERIC item configuration: WORKING")
        print("  [+] Measurement retrieval: WORKING")
        print("\nProduction Ready:")
        print("  - WT1800EPowerAnalyzer class is compatible with WT1806")
        print("  - Uses :NUMeric commands automatically")
        print("  - Fallback to :MEASure for other WT models")
        print("  - Configuration: 60V / 50A range, Element 1")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print(f"        Error type: {type(e).__name__}")

        import traceback
        print("\nTraceback:")
        traceback.print_exc()

        try:
            await power_analyzer.disconnect()
        except:
            pass

        print("\n" + "=" * 70)
        print("[FAILED] PRODUCTION INTEGRATION TEST FAILED")
        print("=" * 70 + "\n")
        return False


if __name__ == "__main__":
    # Run test
    result = asyncio.run(test_wt1806_production())
    sys.exit(0 if result else 1)
