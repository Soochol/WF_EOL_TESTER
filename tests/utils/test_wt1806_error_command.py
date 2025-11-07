"""
WT1806 Error Check Command Test

Tests different error checking commands:
1. :STATUS:ERROR? (standard SCPI)
2. :SYSTem:ERRor? (current implementation)

Usage:
    uv run python test_wt1806_error_command.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from driver.visa import VISACommunication, INTERFACE_USB


async def test_error_commands():
    """Test different error checking commands"""

    print("\n" + "=" * 70)
    print("  WT1806 Error Check Command Test")
    print("  Testing: :STATUS:ERROR? vs :SYSTem:ERRor?")
    print("=" * 70)

    # VISA connection
    visa = VISACommunication(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",
        usb_model_code="0x0025",
        usb_serial_number=None,
        timeout=5.0,  # Short timeout for testing
    )

    try:
        # Connect
        print("\n[1/5] Connecting to WT1806...")
        await visa.connect()
        idn = await visa.query("*IDN?")
        print(f"      Device: {idn.strip()}")

        # Clear errors
        print("\n[2/5] Clearing errors with *CLS...")
        await visa.send_command("*CLS")
        await asyncio.sleep(0.2)
        print("      [OK] Errors cleared")

        # Test 1: :STATUS:ERROR? (recommended SCPI standard)
        print("\n[3/5] Testing :STATUS:ERROR? command...")
        try:
            response = await visa.query(":STATUS:ERROR?")
            print(f"      Response: {response.strip()}")

            # Parse response
            parts = response.strip().split(',', 1)
            if len(parts) >= 1:
                error_code = int(parts[0])
                error_msg = parts[1].strip('"') if len(parts) > 1 else ""
                print(f"      Code: {error_code}")
                print(f"      Message: {error_msg}")

                if error_code == 0:
                    print("      [SUCCESS] :STATUS:ERROR? works! No errors.")
                else:
                    print(f"      [WARNING] Error detected: {error_code}")

        except asyncio.TimeoutError:
            print("      [FAILED] :STATUS:ERROR? timed out")
        except Exception as e:
            print(f"      [FAILED] :STATUS:ERROR? error: {e}")

        # Test 2: :SYSTem:ERRor? (current implementation)
        print("\n[4/5] Testing :SYSTem:ERRor? command...")
        try:
            response = await visa.query(":SYSTem:ERRor?")
            print(f"      Response: {response.strip()}")

            # Parse response
            parts = response.strip().split(',', 1)
            if len(parts) >= 1:
                error_code = int(parts[0])
                error_msg = parts[1].strip('"') if len(parts) > 1 else ""
                print(f"      Code: {error_code}")
                print(f"      Message: {error_msg}")

                if error_code == 0:
                    print("      [SUCCESS] :SYSTem:ERRor? works!")
                else:
                    print(f"      [WARNING] Error detected: {error_code}")

        except asyncio.TimeoutError:
            print("      [FAILED] :SYSTem:ERRor? timed out (as expected)")
        except Exception as e:
            print(f"      [FAILED] :SYSTem:ERRor? error: {e}")

        # Disconnect
        print("\n[5/5] Disconnecting...")
        await visa.disconnect()
        print("      [OK] Disconnected")

        print("\n" + "=" * 70)
        print("[COMPLETE] ERROR COMMAND TEST FINISHED")
        print("=" * 70 + "\n")

        print("Recommendation:")
        print("  Use :STATUS:ERROR? if it works (SCPI standard)")
        print("  This is the recommended error checking method")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print(f"        Error type: {type(e).__name__}")

        import traceback
        print("\nTraceback:")
        traceback.print_exc()

        try:
            await visa.disconnect()
        except:
            pass

        return False


if __name__ == "__main__":
    result = asyncio.run(test_error_commands())
    sys.exit(0 if result else 1)
