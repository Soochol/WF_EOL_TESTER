"""
Simple WT1800E USB Connection Test

Quick test for USB connection to Yokogawa WT1800E with serial number 91M950263.

Usage:
    uv run python test_wt1800e_usb_simple.py
"""

import asyncio

from src.driver.visa import VISACommunication, INTERFACE_USB


async def test_wt1800e_usb():
    """Test WT1800E via USB with serial number 91M950263"""

    print("\n" + "=" * 70)
    print("  WT1800E USB Connection Test (SN: 91M950263)")
    print("=" * 70)

    # Create VISA connection for WT1800E USB
    # Note: Using auto-detect (serial_number=None) to find first Yokogawa device
    visa = VISACommunication(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",      # Yokogawa
        usb_model_code="0x0025",      # WT1800E (actual model code: 0x0025 = 37 decimal)
        usb_serial_number=None,       # Auto-detect first device
        timeout=5.0,
    )

    try:
        # 1. List available resources
        print("\n[*] Scanning for VISA resources...")
        resources = await visa.list_resources()
        print(f"Found resources: {resources}")

        # 2. Connect to device
        print("\n[*] Connecting to WT1800E...")
        await visa.connect()
        print("[OK] Connected!")

        # 3. Get device identity
        print("\n[*] Device Information:")
        idn = await visa.query("*IDN?")
        print(f"  {idn.strip()}")

        # 4. Clear errors
        await visa.send_command("*CLS")

        # 5. Enable remote mode
        await visa.send_command(":COMMunicate:REMote ON")
        print("[OK] Remote mode enabled")

        # 6. Test measurement
        print("\n[*] Measurement Test:")
        voltage = await visa.query(":MEASure:NORMal:VALue? URMS,1")
        current = await visa.query(":MEASure:NORMal:VALue? IRMS,1")
        power = await visa.query(":MEASure:NORMal:VALue? P,1")

        print(f"  Voltage: {voltage.strip()} V")
        print(f"  Current: {current.strip()} A")
        print(f"  Power:   {power.strip()} W")

        # 7. Disconnect
        print("\n[*] Disconnecting...")
        await visa.disconnect()
        print("[OK] Disconnected")

        print("\n" + "=" * 70)
        print("[OK] TEST PASSED")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nTroubleshooting:")
        print("  1. Check USB cable connection")
        print("  2. Verify device is powered on")
        print("  3. Check Windows Device Manager for USB-TMC device")
        print("  4. Install PyVISA-py: uv sync")
        print("\n" + "=" * 70)
        print("[X] TEST FAILED")
        print("=" * 70 + "\n")

        try:
            await visa.disconnect()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(test_wt1800e_usb())
