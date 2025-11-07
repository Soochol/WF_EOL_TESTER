"""
WT1800E USB Termination Character Test

Tests different termination characters to resolve "query unterminated" error.

Usage:
    uv run python test_wt1800e_usb_termination.py
"""

import asyncio

from src.driver.visa import VISACommunication, INTERFACE_USB


async def test_termination(write_term, read_term, description):
    """Test with specific termination characters"""

    print(f"\n{'='*70}")
    print(f"  Testing: {description}")
    print(f"  Write termination: {repr(write_term)}")
    print(f"  Read termination: {repr(read_term)}")
    print(f"{'='*70}")

    visa = VISACommunication(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",
        usb_model_code="0x0025",
        usb_serial_number=None,
        timeout=5.0,
        write_termination=write_term,
        read_termination=read_term,
    )

    try:
        print("\n[1/4] Connecting...")
        await visa.connect()
        print("      [OK] Connected")

        print("\n[2/4] Testing *IDN? query...")
        idn = await visa.query("*IDN?")
        print(f"      Response: {idn.strip()}")

        print("\n[3/4] Sending *CLS command...")
        await visa.send_command("*CLS")
        await asyncio.sleep(0.1)
        print("      [OK] Command sent")

        print("\n[4/4] Checking error status...")
        error = await visa.query(":STATus:ERRor?")
        print(f"      Error status: {error.strip()}")

        if "query unterminated" in error.lower() or "unterminated" in error.lower():
            print(f"\n      [X] Still getting 'unterminated' error")
            result = False
        elif error.startswith("0,"):
            print(f"\n      [OK] No errors! This termination works!")
            result = True
        else:
            print(f"\n      [?] Different error: {error.strip()}")
            result = None

        await visa.disconnect()
        print(f"\n{'='*70}")
        if result == True:
            print(f"[SUCCESS] {description} WORKS!")
        elif result == False:
            print(f"[FAILED] {description} doesn't work")
        else:
            print(f"[UNKNOWN] {description} - check error above")
        print(f"{'='*70}\n")

        return result

    except Exception as e:
        print(f"\n[ERROR] {e}")
        try:
            await visa.disconnect()
        except:
            pass

        print(f"\n{'='*70}")
        print(f"[FAILED] {description}")
        print(f"{'='*70}\n")
        return False


async def main():
    """Test different termination character combinations"""

    print("\n" + "=" * 70)
    print("  WT1800E USB Termination Character Test")
    print("  Finding correct termination for WT1806-06")
    print("=" * 70 + "\n")

    print("Will test 4 common termination combinations:")
    print("  1. LF/LF (\\n/\\n) - Programming guide default")
    print("  2. CR+LF/LF (\\r\\n/\\n) - Common for many instruments")
    print("  3. CR+LF/CR+LF (\\r\\n/\\r\\n) - Windows style")
    print("  4. LF/CR+LF (\\n/\\r\\n) - Alternative")

    results = {}

    # Test 1: LF/LF (default)
    results["LF/LF"] = await test_termination(
        "\n", "\n", "LF/LF (Programming Guide Default)"
    )
    await asyncio.sleep(1)

    # Test 2: CR+LF/LF (common for instruments)
    results["CR+LF/LF"] = await test_termination(
        "\r\n", "\n", "CR+LF/LF (Common for Instruments)"
    )
    await asyncio.sleep(1)

    # Test 3: CR+LF/CR+LF (Windows style)
    results["CR+LF/CR+LF"] = await test_termination(
        "\r\n", "\r\n", "CR+LF/CR+LF (Windows Style)"
    )
    await asyncio.sleep(1)

    # Test 4: LF/CR+LF
    results["LF/CR+LF"] = await test_termination(
        "\n", "\r\n", "LF/CR+LF (Alternative)"
    )

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    working = [k for k, v in results.items() if v == True]
    failed = [k for k, v in results.items() if v == False]
    unknown = [k for k, v in results.items() if v == None]

    if working:
        print(f"\n[OK] Working termination(s):")
        for term in working:
            print(f"     - {term}")
        print(f"\nRecommendation: Update constants.py with working termination")
    else:
        print(f"\n[X] No termination combination worked!")
        print(f"    This might indicate a different issue")

    if failed:
        print(f"\n[X] Failed termination(s): {', '.join(failed)}")

    if unknown:
        print(f"\n[?] Unknown status: {', '.join(unknown)}")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
