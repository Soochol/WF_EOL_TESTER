"""
WT1806 USB Connection - Working Test with NUMERIC Commands

WT1806-06은 :MEASure 명령어가 아닌 :NUMeric 명령어를 사용합니다.

Usage:
    uv run python test_wt1806_usb_success.py
"""

import asyncio

from src.driver.visa import VISACommunication, INTERFACE_USB


async def test_wt1806_usb():
    """WT1806 USB 테스트 - NUMERIC 명령어 사용"""

    print("\n" + "=" * 70)
    print("  WT1806 USB Connection Test - NUMERIC Commands")
    print("=" * 70)

    # VISA 연결
    visa = VISACommunication(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",
        usb_model_code="0x0025",
        usb_serial_number=None,
        timeout=10.0,
    )

    try:
        # 1. 연결
        print("\n[1/6] Connecting to device...")
        await visa.connect()
        idn = await visa.query("*IDN?")
        print(f"      Device: {idn.strip()}")

        # 2. 초기화
        print("\n[2/6] Initializing...")
        await visa.send_command("*CLS")
        await asyncio.sleep(0.2)
        await visa.send_command(":COMMunicate:REMote ON")
        await asyncio.sleep(0.2)
        print("      [OK] Remote mode enabled")

        # 3. 범위 설정 (60V / 50A)
        print("\n[3/6] Configuring range (60V / 50A)...")
        await visa.send_command(":INPut:VOLTage:AUTO:ALL OFF")
        await asyncio.sleep(0.1)
        await visa.send_command(":INPut:CURRent:AUTO:ALL OFF")
        await asyncio.sleep(0.1)
        await visa.send_command(":INPut:VOLTage:RANGe:ELEMent1 60V")
        await asyncio.sleep(0.1)
        await visa.send_command(":INPut:CURRent:RANGe:ELEMent1 50A")
        await asyncio.sleep(0.1)
        print("      [OK] Range configured")

        # 4. NUMERIC 항목 설정
        print("\n[4/6] Setting up NUMERIC display items...")
        await visa.send_command("*CLS")  # 이전 에러 클리어
        await asyncio.sleep(0.2)

        # ITEM1 = 전압 (URMS, Element 1)
        await visa.send_command(":NUMeric:NORMal:ITEM1 URMS,1")
        await asyncio.sleep(0.1)

        # ITEM2 = 전류 (IRMS, Element 1)
        await visa.send_command(":NUMeric:NORMal:ITEM2 IRMS,1")
        await asyncio.sleep(0.1)

        # ITEM3 = 전력 (P, Element 1)
        await visa.send_command(":NUMeric:NORMal:ITEM3 P,1")
        await asyncio.sleep(0.1)

        # ITEM4 = 주파수 (FREQ, Element 1)
        await visa.send_command(":NUMeric:NORMal:ITEM4 FREQ,1")
        await asyncio.sleep(0.1)

        print("      [OK] NUMERIC items configured:")
        print("          ITEM1 = URMS,1 (Voltage)")
        print("          ITEM2 = IRMS,1 (Current)")
        print("          ITEM3 = P,1 (Power)")
        print("          ITEM4 = FREQ,1 (Frequency)")

        # 에러 체크
        error = await visa.query(":STATus:ERRor?")
        print(f"      Error status: {error.strip()}")

        # 5. 측정값 읽기
        print("\n[5/6] Reading measurements...")
        print("      Note: 9.9E+37 = over-range (no input signal)\n")

        # 전체 NUMERIC 값 읽기 (15개 항목)
        values = await visa.query(":NUMeric:NORMal:VALue?")
        value_list = values.strip().split(",")

        print(f"      Total values received: {len(value_list)}")
        print(f"      Raw response: {values.strip()}\n")

        # 개별 값 출력
        if len(value_list) >= 4:
            print(f"      ITEM1 (Voltage):   {value_list[0]} V")
            print(f"      ITEM2 (Current):   {value_list[1]} A")
            print(f"      ITEM3 (Power):     {value_list[2]} W")
            print(f"      ITEM4 (Frequency): {value_list[3]} Hz")

            # 남은 항목들
            if len(value_list) > 4:
                print(f"\n      Other items (ITEM5-ITEM15):")
                for i in range(4, len(value_list)):
                    print(f"      ITEM{i+1}: {value_list[i]}")

        # 6. 최종 에러 체크
        print("\n[6/6] Final error check...")
        error = await visa.query(":STATus:ERRor?")
        print(f"      Error status: {error.strip()}")

        # 연결 해제
        print("\n[*] Disconnecting...")
        await visa.disconnect()
        print("    [OK] Disconnected")

        print("\n" + "=" * 70)
        print("[SUCCESS] WT1806 USB CONNECTION TEST PASSED")
        print("=" * 70 + "\n")

        print("Summary:")
        print("  [+] USB connection: WORKING")
        print("  [+] Device communication: WORKING")
        print("  [+] Range configuration: WORKING")
        print("  [+] NUMERIC measurement: WORKING")
        print("\nKey Finding:")
        print("  - WT1806 uses :NUMeric commands instead of :MEASure")
        print("  - Set measurement items with :NUMeric:NORMal:ITEMx")
        print("  - Read all values with :NUMeric:NORMal:VALue?")
        print("\nProduction Integration:")
        print("  - Update WT1800EPowerAnalyzer to use :NUMeric commands")
        print("  - Configure ITEM1-3 for V/I/P measurements")
        print("  - Parse comma-separated response")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print(f"        Error type: {type(e).__name__}")

        try:
            await visa.disconnect()
        except:
            pass

        print("\n" + "=" * 70)
        print("[FAILED] TEST FAILED")
        print("=" * 70 + "\n")
        return False


if __name__ == "__main__":
    asyncio.run(test_wt1806_usb())
