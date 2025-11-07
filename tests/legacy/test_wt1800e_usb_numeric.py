"""
WT1800E USB Test using NUMERIC commands

Tests alternative measurement commands for WT1806-06 device.
The :MEASure command doesn't work, so trying :NUMeric instead.

Usage:
    uv run python test_wt1800e_usb_numeric.py
"""

import asyncio

from src.driver.visa import VISACommunication, INTERFACE_USB


async def test_wt1800e_usb_numeric():
    """Test USB with NUMERIC measurement commands"""

    print("\n" + "=" * 70)
    print("  WT1800E USB Test - Using NUMERIC Commands")
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
        print("\n[1/6] Connecting...")
        await visa.connect()
        idn = await visa.query("*IDN?")
        print(f"      {idn.strip()}")

        # Clear and enable remote
        print("\n[2/6] Initializing...")
        await visa.send_command("*CLS")
        await asyncio.sleep(0.2)
        await visa.send_command(":COMMunicate:REMote ON")
        await asyncio.sleep(0.2)
        print("      [OK] Remote mode enabled")

        # Configure ranges
        print("\n[3/6] Configuring range (60V / 50A)...")
        await visa.send_command(":INPut:VOLTage:AUTO:ALL OFF")
        await asyncio.sleep(0.1)
        await visa.send_command(":INPut:CURRent:AUTO:ALL OFF")
        await asyncio.sleep(0.1)
        await visa.send_command(":INPut:VOLTage:RANGe:ELEMent1 60V")
        await asyncio.sleep(0.1)
        await visa.send_command(":INPut:CURRent:RANGe:ELEMent1 50A")
        await asyncio.sleep(0.1)
        error = await visa.query(":STATus:ERRor?")
        print(f"      Error: {error.strip()}")

        # Try querying NUMERIC display settings
        print("\n[4/6] Querying NUMERIC configuration...")
        try:
            num_item1 = await visa.query(":NUMeric:NORMal:ITEM1?")
            print(f"      ITEM1: {num_item1.strip()}")
        except Exception as e:
            print(f"      [!] ITEM1 query failed: {e}")

        try:
            num_item2 = await visa.query(":NUMeric:NORMal:ITEM2?")
            print(f"      ITEM2: {num_item2.strip()}")
        except Exception as e:
            print(f"      [!] ITEM2 query failed: {e}")

        # Set NUMERIC items for display
        print("\n[5/6] Setting NUMERIC items...")
        try:
            await visa.send_command(":NUMeric:NORMal:ITEM1 URMS,1")
            await asyncio.sleep(0.1)
            await visa.send_command(":NUMeric:NORMal:ITEM2 IRMS,1")
            await asyncio.sleep(0.1)
            await visa.send_command(":NUMeric:NORMal:ITEM3 P,1")
            await asyncio.sleep(0.1)
            print("      [OK] NUMERIC items configured")
        except Exception as e:
            print(f"      [!] NUMERIC setup failed: {e}")

        # Try NUMeric:VALue query
        print("\n[6/6] Testing NUMERIC value query...")
        try:
            values = await visa.query(":NUMeric:NORMal:VALue?")
            print(f"      Values: {values.strip()}")
        except Exception as e:
            print(f"      [!] NUMERIC value query failed: {e}")

        # Try alternative commands
        print("\n[*] Testing alternative measurement commands...")

        test_commands = [
            (":MEASure? URMS,1", "MEAS URMS"),
            (":DATA? URMS,1", "DATA URMS"),
            (":NUMeric? URMS,1", "NUMERIC URMS"),
            (":FETCh? URMS,1", "FETCH URMS"),
            (":READ? URMS,1", "READ URMS"),
        ]

        for cmd, desc in test_commands:
            try:
                result = await visa.query(cmd)
                print(f"      [OK] {desc}: {result.strip()}")
                break  # Found a working command!
            except Exception as e:
                print(f"      [!] {desc} failed")

        # Final error check
        print("\n[*] Final error check...")
        error = await visa.query(":STATus:ERRor?")
        print(f"    Error: {error.strip()}")

        # Disconnect
        print("\n[*] Disconnecting...")
        await visa.disconnect()
        print("    [OK] Done")

        print("\n" + "=" * 70)
        print("[OK] TEST COMPLETED")
        print("=" * 70 + "\n")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        try:
            await visa.disconnect()
        except:
            pass
        return False


if __name__ == "__main__":
    asyncio.run(test_wt1800e_usb_numeric())
