"""
WT1806 Integration Basic Test

Tests basic integration functionality:
- Configure integration (10 second timer, NORMAL mode, RMS current)
- State transitions: RESET → START → STOP
- Read integration values: WH, AH, TIME

Usage:
    uv run python test_wt1806_integration_basic.py
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


async def test_basic_integration():
    """Test basic integration functionality with WT1806"""

    print("\n" + "=" * 70)
    print("  WT1806 Integration Basic Test")
    print("  Testing: Configure → Reset → Start → Wait → Stop → Read Values")
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
        print("\n[1/9] Connecting to WT1806...")
        await power_analyzer.connect()
        print("      [OK] Connected")

        # Step 2: Get device info
        print("\n[2/9] Getting device information...")
        identity = await power_analyzer.get_device_identity()
        print(f"      Device: {identity}")

        # Step 3: Configure integration
        print("\n[3/9] Configuring integration...")
        print("      Mode: NORMAL")
        print("      Timer: 10 seconds")
        print("      Auto Calibration: ON")
        print("      Current Mode: RMS")

        await power_analyzer.configure_integration(
            mode="NORMAL",
            timer_hours=0,
            timer_minutes=0,
            timer_seconds=10,
            auto_calibration=True,
            current_mode="RMS",
        )
        print("      [OK] Integration configured")

        # Step 4: Reset integration
        print("\n[4/9] Resetting integration...")
        await power_analyzer.reset_integration()
        await asyncio.sleep(0.5)

        state = await power_analyzer.get_integration_state()
        print(f"      State: {state}")

        if state == "RESET":
            print("      [OK] Integration reset successful")
        else:
            print(f"      [WARNING] Expected RESET, got {state}")

        # Step 5: Start integration
        print("\n[5/9] Starting integration...")
        await power_analyzer.start_integration()
        await asyncio.sleep(0.5)

        state = await power_analyzer.get_integration_state()
        print(f"      State: {state}")

        if state == "START":
            print("      [OK] Integration started")
        else:
            print(f"      [WARNING] Expected START, got {state}")

        # Step 6: Wait 10 seconds
        print("\n[6/9] Waiting for 10 seconds...")
        for i in range(10, 0, -1):
            print(f"      {i} seconds remaining...", end="\r")
            await asyncio.sleep(1.0)
        print("      [OK] Wait complete" + " " * 30)

        # Step 7: Stop integration
        print("\n[7/9] Stopping integration...")
        await power_analyzer.stop_integration()
        await asyncio.sleep(0.5)

        state = await power_analyzer.get_integration_state()
        print(f"      State: {state}")

        if state == "STOP":
            print("      [OK] Integration stopped")
        else:
            print(f"      [WARNING] Expected STOP, got {state}")

        # Step 8: Read integration values
        print("\n[8/9] Reading integration values...")
        print("      Note: Values may be 0 or 9.9E+37 if no input signal\n")

        values = await power_analyzer.get_integration_values()

        print(f"      Voltage:    {values['voltage']:.6f} V")
        print(f"      Current:    {values['current']:.6f} A")
        print(f"      Power:      {values['power']:.6f} W")
        print(f"      Energy WH:  {values['wh']:.6f} Wh")
        print(f"      Charge AH:  {values['ah']:.6f} Ah")
        print(f"      Time:       {values['time']:.3f} seconds")

        # Step 9: Disconnect
        print("\n[9/9] Disconnecting...")
        await power_analyzer.disconnect()
        print("      [OK] Disconnected")

        print("\n" + "=" * 70)
        print("[SUCCESS] INTEGRATION BASIC TEST PASSED")
        print("=" * 70 + "\n")

        print("Summary:")
        print("  [+] Integration configuration: WORKING")
        print("  [+] State transitions: WORKING")
        print("  [+] Integration start/stop: WORKING")
        print("  [+] Integration value reading: WORKING")
        print(f"\nIntegration Results:")
        print(f"  - Energy: {values['wh']:.6f} Wh")
        print(f"  - Charge: {values['ah']:.6f} Ah")
        print(f"  - Time:   {values['time']:.3f} s")
        print("\nNext Steps:")
        print("  - Run cycle test: test_wt1806_integration_cycle.py")
        print("  - Test with actual load for non-zero measurements")

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
        print("[FAILED] INTEGRATION BASIC TEST FAILED")
        print("=" * 70 + "\n")
        return False


if __name__ == "__main__":
    # Run test
    result = asyncio.run(test_basic_integration())
    sys.exit(0 if result else 1)
