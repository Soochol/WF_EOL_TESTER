"""
Improved WT1800E USB Connection Test

Tests USB connection with proper initialization and longer timeouts.
Based on WT1800E Programming Guide best practices.

Usage:
    uv run python test_wt1800e_usb_improved.py
"""

import asyncio

from src.driver.visa import VISACommunication, INTERFACE_USB


async def test_wt1800e_usb_improved():
    """Test WT1800E via USB with proper initialization"""

    print("\n" + "=" * 70)
    print("  WT1800E USB Connection Test - Improved Version")
    print("=" * 70)

    # Create VISA connection with longer timeout
    visa = VISACommunication(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",      # Yokogawa
        usb_model_code="0x0025",     # Actual model code
        usb_serial_number=None,       # Auto-detect
        timeout=10.0,                 # Increased timeout to 10 seconds
    )

    try:
        # 1. List available resources
        print("\n[1/8] Scanning for VISA resources...")
        resources = await visa.list_resources()
        print(f"      Found {len(resources)} resource(s)")
        for resource in resources:
            if "USB" in resource:
                print(f"      USB: {resource}")

        # 2. Connect to device
        print("\n[2/8] Connecting to WT1800E via USB...")
        await visa.connect()
        print("      [OK] Connected")

        # 3. Get device identity
        print("\n[3/8] Querying device identity...")
        idn = await visa.query("*IDN?")
        print(f"      Device: {idn.strip()}")

        # 4. Clear errors and reset
        print("\n[4/8] Clearing errors and resetting device...")
        await visa.send_command("*RST")  # Reset to known state
        await asyncio.sleep(2.0)  # Wait for reset
        await visa.send_command("*CLS")  # Clear error queue
        print("      [OK] Device reset and cleared")

        # 5. Enable remote mode
        print("\n[5/8] Enabling remote mode...")
        await visa.send_command(":COMMunicate:REMote ON")
        print("      [OK] Remote mode enabled")

        # 6. Configure basic measurement settings
        print("\n[6/8] Configuring measurement settings...")
        await visa.send_command(":INPut:VOLTage:RANGe:ALL 300V")  # Set voltage range
        await visa.send_command(":INPut:CURRent:RANGe:ALL 5A")    # Set current range
        await visa.send_command(":INTEGrate:MODE NORMal")         # Set integration mode
        print("      [OK] Basic settings configured")
        print("          - Voltage range: 300V")
        print("          - Current range: 5A")
        print("          - Integration mode: Normal")

        # 7. Wait for measurement to stabilize
        print("\n[7/8] Waiting for measurement stabilization...")
        await asyncio.sleep(2.0)
        print("      [OK] Ready for measurements")

        # 8. Test measurements with error handling
        print("\n[8/8] Testing measurements...")

        try:
            # Test voltage measurement
            print("      [*] Querying voltage (URMS,1)...")
            voltage = await visa.query(":MEASure:NORMal:VALue? URMS,1")
            print(f"          Voltage: {voltage.strip()} V")
        except Exception as e:
            print(f"          [!] Voltage measurement failed: {e}")

        try:
            # Test current measurement
            print("      [*] Querying current (IRMS,1)...")
            current = await visa.query(":MEASure:NORMal:VALue? IRMS,1")
            print(f"          Current: {current.strip()} A")
        except Exception as e:
            print(f"          [!] Current measurement failed: {e}")

        try:
            # Test power measurement
            print("      [*] Querying power (P,1)...")
            power = await visa.query(":MEASure:NORMal:VALue? P,1")
            print(f"          Power: {power.strip()} W")
        except Exception as e:
            print(f"          [!] Power measurement failed: {e}")

        # 9. Test error query
        print("\n[*] Checking device error status...")
        error = await visa.query(":STATus:ERRor?")
        print(f"    Error status: {error.strip()}")

        # 10. Disconnect
        print("\n[*] Disconnecting...")
        await visa.disconnect()
        print("    [OK] Disconnected")

        print("\n" + "=" * 70)
        print("[OK] USB CONNECTION TEST COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check that device is powered on")
        print("  2. Verify USB cable connection")
        print("  3. Check if measurement inputs are connected")
        print("  4. Review error status on device display")
        print("\n" + "=" * 70)
        print("[X] USB CONNECTION TEST FAILED")
        print("=" * 70 + "\n")

        try:
            await visa.disconnect()
        except:
            pass

        return False


if __name__ == "__main__":
    asyncio.run(test_wt1800e_usb_improved())
