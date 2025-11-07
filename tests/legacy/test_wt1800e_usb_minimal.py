"""
Minimal WT1800E USB Connection Test

Minimal test without reset or configuration.
Tests only basic query operations.

Usage:
    uv run python test_wt1800e_usb_minimal.py
"""

import asyncio

from src.driver.visa import VISACommunication, INTERFACE_USB


async def test_wt1800e_usb_minimal():
    """Minimal USB test - no reset, no configuration"""

    print("\n" + "=" * 70)
    print("  WT1800E USB Connection Test - Minimal Version")
    print("=" * 70)

    # Create VISA connection
    visa = VISACommunication(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",      # Yokogawa
        usb_model_code="0x0025",     # Actual model code
        usb_serial_number=None,       # Auto-detect
        timeout=10.0,
    )

    try:
        # Step 1: Connect
        print("\n[1/6] Connecting to USB device...")
        await visa.connect()
        print("      [OK] Connected")

        # Step 2: Device identity
        print("\n[2/6] Getting device identity...")
        idn = await visa.query("*IDN?")
        print(f"      {idn.strip()}")

        # Step 3: Clear errors (but no reset)
        print("\n[3/6] Clearing error queue...")
        await visa.send_command("*CLS")
        print("      [OK] Errors cleared")

        # Step 4: Check error status
        print("\n[4/6] Checking error status...")
        error = await visa.query(":STATus:ERRor?")
        print(f"      Error status: {error.strip()}")

        # Step 5: Query current settings (read-only operations)
        print("\n[5/6] Querying current device settings...")

        try:
            wiring = await visa.query(":INPut:WIRing?")
            print(f"      Wiring mode: {wiring.strip()}")
        except Exception as e:
            print(f"      [!] Wiring query failed: {e}")

        try:
            integrate_mode = await visa.query(":INTEGrate:MODE?")
            print(f"      Integration mode: {integrate_mode.strip()}")
        except Exception as e:
            print(f"      [!] Integration mode query failed: {e}")

        # Step 6: Try measurement queries (device as-is)
        print("\n[6/6] Testing measurement queries...")
        print("      Note: Measurements may show 9.9E+37 if no input connected")

        try:
            voltage = await visa.query(":MEASure:NORMal:VALue? URMS,1")
            print(f"      Voltage (URMS,1): {voltage.strip()} V")
        except Exception as e:
            print(f"      [!] Voltage measurement failed: {e}")

        try:
            current = await visa.query(":MEASure:NORMal:VALue? IRMS,1")
            print(f"      Current (IRMS,1): {current.strip()} A")
        except Exception as e:
            print(f"      [!] Current measurement failed: {e}")

        try:
            power = await visa.query(":MEASure:NORMal:VALue? P,1")
            print(f"      Power (P,1): {power.strip()} W")
        except Exception as e:
            print(f"      [!] Power measurement failed: {e}")

        try:
            freq = await visa.query(":MEASure:NORMal:VALue? FREQ,1")
            print(f"      Frequency (FREQ,1): {freq.strip()} Hz")
        except Exception as e:
            print(f"      [!] Frequency measurement failed: {e}")

        # Disconnect
        print("\n[*] Disconnecting...")
        await visa.disconnect()
        print("    [OK] Disconnected")

        print("\n" + "=" * 70)
        print("[OK] MINIMAL USB TEST COMPLETED")
        print("=" * 70 + "\n")

        print("Next steps:")
        print("  - If measurements show 9.9E+37, it means no input signal")
        print("  - Connect test signal to measure actual values")
        print("  - USB communication is working correctly!")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print("\nDebugging info:")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error details: {str(e)}")

        print("\n" + "=" * 70)
        print("[X] MINIMAL USB TEST FAILED")
        print("=" * 70 + "\n")

        try:
            await visa.disconnect()
        except:
            pass

        return False


if __name__ == "__main__":
    asyncio.run(test_wt1800e_usb_minimal())
