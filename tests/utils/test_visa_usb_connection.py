"""
VISA USB Connection Test Script

Test script to verify USB connection to Yokogawa WT1800E Power Analyzer.
This script will:
1. List all available VISA resources
2. Attempt to connect via USB
3. Query device identity
4. Test basic measurements

Usage:
    uv run python test_visa_usb_connection.py
"""

# Standard library imports
import asyncio
import sys

# Third-party imports
from loguru import logger

# Local application imports
from src.driver.visa import INTERFACE_USB, VISACommunication


async def list_visa_resources():
    """List all available VISA resources"""
    print("\n" + "=" * 70)
    print("🔍 Scanning for VISA resources...")
    print("=" * 70)

    visa_comm = VISACommunication()
    try:
        resources = await visa_comm.list_resources()

        if not resources:
            print("❌ No VISA resources found!")
            print("\nTroubleshooting:")
            print("  1. Check if WT1800E is connected via USB")
            print("  2. Verify USB drivers are installed")
            print("  3. Try re-plugging the USB cable")
            return []

        print(f"\n✅ Found {len(resources)} VISA resource(s):\n")
        for i, resource in enumerate(resources, 1):
            print(f"  [{i}] {resource}")

        return resources

    except Exception as e:
        print(f"❌ Error listing VISA resources: {e}")
        return []


async def test_usb_connection(serial_number: str = None):
    """
    Test USB connection to WT1800E

    Args:
        serial_number: Device serial number (None = auto-detect first device)
    """
    print("\n" + "=" * 70)
    print("🔌 Testing USB Connection to WT1800E")
    print("=" * 70)

    if serial_number:
        print(f"\nSerial Number: {serial_number}")
    else:
        print("\nSerial Number: Auto-detect (first device)")

    visa_comm = VISACommunication(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",  # Yokogawa
        usb_model_code="0x0039",  # WT1800E
        usb_serial_number=serial_number,
        timeout=5.0,
    )

    try:
        # Connect
        print("\n📡 Connecting to WT1800E via USB...")
        await visa_comm.connect()
        print("✅ Connected successfully!")

        # Query device identity
        print("\n📋 Querying device identity...")
        idn_response = await visa_comm.query("*IDN?")
        print(f"✅ Device: {idn_response.strip()}")

        # Clear errors
        print("\n🧹 Clearing error status...")
        await visa_comm.send_command("*CLS")
        print("✅ Error status cleared")

        # Enable Remote mode
        print("\n🔐 Enabling Remote mode...")
        await visa_comm.send_command(":COMMunicate:REMote ON")
        print("✅ Remote mode enabled")

        # Query measurement (example)
        print("\n📊 Testing measurement query...")
        measurement = await visa_comm.query(":MEASure:NORMal:VALue? URMS,1")
        print(f"✅ Voltage (Element 1): {measurement.strip()} V")

        # Disconnect
        print("\n🔌 Disconnecting...")
        await visa_comm.disconnect()
        print("✅ Disconnected successfully")

        print("\n" + "=" * 70)
        print("✅ USB Connection Test PASSED")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ USB Connection Test FAILED: {e}")
        print("\nTroubleshooting:")
        print("  1. Check USB connection")
        print("  2. Verify device is powered on")
        print("  3. Check USB drivers (see documentation)")
        print("  4. Try running 'list_resources()' to find correct device")

        # Try to disconnect
        try:
            await visa_comm.disconnect()
        except:
            pass

        print("\n" + "=" * 70)
        print("❌ USB Connection Test FAILED")
        print("=" * 70)
        return False


async def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("  WT1800E VISA USB Connection Test")
    print("=" * 70)

    # Step 1: List all VISA resources
    resources = await list_visa_resources()

    # Step 2: Test USB connection
    if resources:
        print("\n💡 Tip: USB resources typically look like:")
        print("     USB::0x0B21::0x0039::C1PD29001N::INSTR")
        print("     USB::<vendor>::<model>::<serial>::INSTR")

    print("\n" + "-" * 70)
    proceed = input("\nProceed with USB connection test? (y/n): ")

    if proceed.lower() == "y":
        # Option to specify serial number
        print("\n" + "-" * 70)
        serial = input("\nEnter serial number (or press Enter for auto-detect): ").strip()
        serial_number = serial if serial else None

        await test_usb_connection(serial_number)
    else:
        print("\nTest cancelled.")

    print("\n✨ Test completed\n")


if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    # Run test
    asyncio.run(main())
