"""
WT1800E USB Connection Test using FETCH commands

Tests measurement using :FETCh commands which read from buffer
without triggering new measurements.

Usage:
    uv run python test_wt1800e_usb_fetch.py
"""

import asyncio

from src.driver.visa import VISACommunication, INTERFACE_USB


async def test_wt1800e_usb_fetch():
    """Test USB connection using FETCH commands"""

    print("\n" + "=" * 70)
    print("  WT1800E USB Test - Using FETCH Commands")
    print("=" * 70)

    # Create VISA connection
    visa = VISACommunication(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",
        usb_model_code="0x0025",
        usb_serial_number=None,
        timeout=10.0,
    )

    try:
        # Connect
        print("\n[1/5] Connecting to USB device...")
        await visa.connect()
        print("      [OK] Connected")

        # Device identity
        print("\n[2/5] Getting device identity...")
        idn = await visa.query("*IDN?")
        print(f"      {idn.strip()}")

        # Clear errors
        print("\n[3/5] Clearing error queue...")
        await visa.send_command("*CLS")
        error = await visa.query(":STATus:ERRor?")
        print(f"      Error status: {error.strip()}")

        # Check current settings
        print("\n[4/5] Device configuration:")
        wiring = await visa.query(":INPut:WIRing?")
        print(f"      Wiring: {wiring.strip()}")
        integrate_mode = await visa.query(":INTEGrate:MODE?")
        print(f"      Integration mode: {integrate_mode.strip()}")

        # Test FETCH commands (read from buffer)
        print("\n[5/5] Testing FETCH commands (reading from buffer)...")
        print("      Note: Values may be 9.9E+37 if no input signal\n")

        try:
            # Use FETCh instead of MEASure
            voltage = await visa.query(":FETCh:NORMal:VALue? URMS,1")
            print(f"      Voltage (URMS,1): {voltage.strip()} V")
        except Exception as e:
            print(f"      [!] Voltage fetch failed: {e}")

        try:
            current = await visa.query(":FETCh:NORMal:VALue? IRMS,1")
            print(f"      Current (IRMS,1): {current.strip()} A")
        except Exception as e:
            print(f"      [!] Current fetch failed: {e}")

        try:
            power = await visa.query(":FETCh:NORMal:VALue? P,1")
            print(f"      Power (P,1): {power.strip()} W")
        except Exception as e:
            print(f"      [!] Power fetch failed: {e}")

        try:
            freq = await visa.query(":FETCh:NORMal:VALue? FREQ,1")
            print(f"      Frequency (FREQ,1): {freq.strip()} Hz")
        except Exception as e:
            print(f"      [!] Frequency fetch failed: {e}")

        # Try multiple values in one query
        print("\n      Testing combined query:")
        try:
            combined = await visa.query(":FETCh:NORMal:VALue? URMS,1,IRMS,1,P,1")
            values = combined.strip().split(",")
            print(f"      V={values[0]}, I={values[1]}, P={values[2]}")
        except Exception as e:
            print(f"      [!] Combined fetch failed: {e}")

        # Check final error status
        print("\n[*] Final error check...")
        error = await visa.query(":STATus:ERRor?")
        print(f"    Error status: {error.strip()}")

        # Disconnect
        print("\n[*] Disconnecting...")
        await visa.disconnect()
        print("    [OK] Disconnected")

        print("\n" + "=" * 70)
        print("[OK] USB FETCH TEST COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")

        print("Summary:")
        print("  USB communication: WORKING")
        print("  Device queries: WORKING")
        print("  Data fetching: See results above")
        print("\nIf measurements show 9.9E+37:")
        print("  - This indicates 'over-range' or 'no input signal'")
        print("  - Connect AC/DC source to measure actual values")
        print("  - The USB connection itself is functioning correctly")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print(f"        Error type: {type(e).__name__}")

        print("\n" + "=" * 70)
        print("[X] USB FETCH TEST FAILED")
        print("=" * 70 + "\n")

        try:
            await visa.disconnect()
        except:
            pass

        return False


if __name__ == "__main__":
    asyncio.run(test_wt1800e_usb_fetch())
