"""
WT1806 Reset Test

Resets the WT1806 to factory defaults to clear stuck integration state.

Usage:
    uv run python test_wt1806_reset.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from driver.visa import VISACommunication, INTERFACE_USB


async def reset_wt1806():
    """Reset WT1806 to clear stuck state"""

    print("\n" + "=" * 70)
    print("  WT1806 Reset Tool")
    print("  Clearing stuck integration state")
    print("=" * 70)

    visa = VISACommunication(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",
        usb_model_code="0x0025",
        usb_serial_number=None,
        timeout=10.0,
    )

    try:
        # Connect
        print("\n[1/5] Connecting...")
        await visa.connect()
        idn = await visa.query("*IDN?")
        print(f"      Device: {idn.strip()}")

        # Check integration state
        print("\n[2/5] Checking integration state...")
        state = await visa.query(":INTEGrate:STATe?")
        print(f"      State: {state.strip()}")

        # Try to stop integration
        print("\n[3/5] Stopping integration...")
        await visa.send_command(":INTEGrate:STOP")
        await asyncio.sleep(0.5)
        state = await visa.query(":INTEGrate:STATe?")
        print(f"      State after STOP: {state.strip()}")

        # Reset integration
        print("\n[4/5] Resetting integration...")
        await visa.send_command(":INTEGrate:RESet")
        await asyncio.sleep(0.5)
        state = await visa.query(":INTEGrate:STATe?")
        print(f"      State after RESET: {state.strip()}")

        # Clear errors
        print("\n[5/5] Clearing errors...")
        await visa.send_command("*CLS")
        error = await visa.query(":STATUS:ERROR?")
        print(f"      Error status: {error.strip()}")

        # Disconnect
        await visa.disconnect()

        print("\n" + "=" * 70)
        print("[SUCCESS] WT1806 Reset Complete")
        print("=" * 70 + "\n")
        print("You can now run the integration test again.")

        return True

    except Exception as e:
        print(f"\n[ERROR] Reset failed: {e}")

        import traceback
        print("\nTraceback:")
        traceback.print_exc()

        try:
            await visa.disconnect()
        except:
            pass

        return False


if __name__ == "__main__":
    result = asyncio.run(reset_wt1806())
    sys.exit(0 if result else 1)
