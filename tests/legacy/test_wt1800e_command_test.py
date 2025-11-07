"""
WT1800E Command Test - 계측기 에러 확인용

각 명령어를 보내고 계측기에 표시되는 에러를 확인합니다.
각 명령어 사이에 대기 시간을 두어 계측기에서 에러를 확인할 수 있습니다.

Usage:
    uv run python test_wt1800e_command_test.py
"""

import asyncio

from src.driver.visa import VISACommunication, INTERFACE_USB


async def test_command(visa, cmd, description, wait_time=3.0):
    """단일 명령어 테스트"""
    print(f"\n{'='*70}")
    print(f"명령어: {cmd}")
    print(f"설명: {description}")
    print(f"{'='*70}")

    try:
        # 명령어 전송
        print(f"[*] 명령어 전송 중...")
        if "?" in cmd:
            # Query 명령어
            response = await visa.query(cmd)
            print(f"[OK] 응답: {response.strip()}")
        else:
            # Write 명령어
            await visa.send_command(cmd)
            print(f"[OK] 명령어 전송 완료")

        # 계측기에서 에러 확인할 시간
        print(f"\n>>> 계측기 화면에서 에러 확인 중... ({wait_time}초 대기)")
        for i in range(int(wait_time)):
            await asyncio.sleep(1)
            print(f"    {i+1}/{int(wait_time)}초...")

        # 에러 상태 조회
        error = await visa.query(":STATus:ERRor?")
        print(f"\n[결과] 에러 상태: {error.strip()}")

        if error.startswith("0,"):
            print("[OK] 에러 없음 - 명령어 정상 작동!")
            return True
        else:
            print(f"[X] 에러 발생: {error.strip()}")
            return False

    except Exception as e:
        print(f"[ERROR] 예외 발생: {e}")
        print(f">>> 계측기 화면에서 에러 메시지를 확인해주세요!")
        await asyncio.sleep(wait_time)

        # 에러 상태 조회 시도
        try:
            error = await visa.query(":STATus:ERRor?")
            print(f"\n[결과] 에러 상태: {error.strip()}")
        except:
            pass

        return False


async def main():
    """메인 테스트"""

    print("\n" + "=" * 70)
    print("  WT1800E 명령어 테스트 - 계측기 에러 확인")
    print("  각 명령어를 보내고 계측기 화면을 확인하세요")
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
        # 초기 연결
        print("\n[1/12] 연결 중...")
        await visa.connect()
        idn = await visa.query("*IDN?")
        print(f"        장비: {idn.strip()}")

        print("\n[2/12] 초기화 중...")
        await visa.send_command("*CLS")
        await asyncio.sleep(0.2)
        await visa.send_command(":COMMunicate:REMote ON")
        await asyncio.sleep(0.2)

        # 범위 설정
        print("\n[3/12] 범위 설정 (60V / 50A)...")
        await visa.send_command(":INPut:VOLTage:AUTO:ALL OFF")
        await asyncio.sleep(0.1)
        await visa.send_command(":INPut:CURRent:AUTO:ALL OFF")
        await asyncio.sleep(0.1)
        await visa.send_command(":INPut:VOLTage:RANGe:ELEMent1 60V")
        await asyncio.sleep(0.1)
        await visa.send_command(":INPut:CURRent:RANGe:ELEMent1 50A")
        await asyncio.sleep(0.1)
        print("        [OK] 범위 설정 완료")

        # 에러 클리어
        await visa.send_command("*CLS")
        await asyncio.sleep(0.2)

        print("\n" + "=" * 70)
        print("테스트할 명령어 목록 (총 9개)")
        print("=" * 70)
        print("1. :MEASure:NORMal:VALue? URMS,1    (프로그래밍 가이드 표준)")
        print("2. :MEASure:VALue? URMS,1           (NORMal 없이)")
        print("3. :NUMeric:NORMal:VALue?           (숫자 표시 값)")
        print("4. :NUMeric:VALue?                  (NORMal 없이)")
        print("5. :FETCh:NORMal:VALue? URMS,1      (버퍼에서 읽기)")
        print("6. :FETCh? URMS,1                   (간단한 형태)")
        print("7. :READ:NORMal:VALue? URMS,1       (측정 후 읽기)")
        print("8. :READ? URMS,1                    (간단한 형태)")
        print("9. MEAS? URMS,1                     (짧은 형태)")
        print("=" * 70)

        print("\n테스트 자동 시작... (각 명령어마다 3초 대기)")
        await asyncio.sleep(2)

        results = {}

        # 테스트 1
        results["MEASure:NORMal:VALue"] = await test_command(
            visa,
            ":MEASure:NORMal:VALue? URMS,1",
            "프로그래밍 가이드 표준 명령어"
        )

        # 테스트 2
        results["MEASure:VALue"] = await test_command(
            visa,
            ":MEASure:VALue? URMS,1",
            "NORMal 계층 없이"
        )

        # 테스트 3
        results["NUMeric:NORMal:VALue"] = await test_command(
            visa,
            ":NUMeric:NORMal:VALue?",
            "숫자 표시 값 읽기 (표준)"
        )

        # 테스트 4
        results["NUMeric:VALue"] = await test_command(
            visa,
            ":NUMeric:VALue?",
            "숫자 표시 값 (NORMal 없이)"
        )

        # 테스트 5
        results["FETCh:NORMal:VALue"] = await test_command(
            visa,
            ":FETCh:NORMal:VALue? URMS,1",
            "버퍼에서 읽기 (표준)"
        )

        # 테스트 6
        results["FETCh"] = await test_command(
            visa,
            ":FETCh? URMS,1",
            "버퍼에서 읽기 (간단)"
        )

        # 테스트 7
        results["READ:NORMal:VALue"] = await test_command(
            visa,
            ":READ:NORMal:VALue? URMS,1",
            "측정 후 읽기 (표준)"
        )

        # 테스트 8
        results["READ"] = await test_command(
            visa,
            ":READ? URMS,1",
            "측정 후 읽기 (간단)"
        )

        # 테스트 9
        results["MEAS"] = await test_command(
            visa,
            "MEAS? URMS,1",
            "짧은 형태 (콜론 없음)"
        )

        # 결과 요약
        print("\n" + "=" * 70)
        print("  테스트 결과 요약")
        print("=" * 70)

        success = [k for k, v in results.items() if v == True]
        failed = [k for k, v in results.items() if v == False]

        if success:
            print(f"\n[성공] 작동하는 명령어:")
            for cmd in success:
                print(f"  ✓ {cmd}")

        if failed:
            print(f"\n[실패] 작동하지 않는 명령어:")
            for cmd in failed:
                print(f"  ✗ {cmd}")

        print("\n" + "=" * 70 + "\n")

        await visa.disconnect()

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        try:
            await visa.disconnect()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
