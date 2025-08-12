#!/usr/bin/env python3
"""
단순 시리얼 통신 테스트

시리얼 포트 모니터와 동일한 방식으로 MCU와 직접 통신하여
딜레이 없이 정상 동작하는지 확인합니다.
"""

import json
import struct
import time
from datetime import datetime
from typing import Dict, List, Optional

import serial


class SimpleSerialTester:
    """단순 시리얼 통신 테스터"""

    def __init__(self, port: str = "COM4", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.test_results: List[Dict] = []

    def connect(self) -> bool:
        """MCU 연결"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity=serial.PARITY_NONE,
                stopbits=1,
                timeout=5.0,
            )
            print(f"✅ MCU 연결 성공: {self.port} @ {self.baudrate}")
            return True
        except Exception as e:
            print(f"❌ MCU 연결 실패: {e}")
            return False

    def disconnect(self):
        """MCU 연결 해제"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("📴 MCU 연결 해제")

    def send_packet(self, packet_hex: str, description: str = "") -> Dict:
        """패킷 전송 및 응답 수신"""
        if not self.serial_conn or not self.serial_conn.is_open:
            return {"error": "Not connected"}

        try:
            # 패킷 전송
            packet_bytes = bytes.fromhex(packet_hex.replace(" ", ""))
            start_time = time.time()

            self.serial_conn.write(packet_bytes)
            send_time = time.time()

            print(f"📤 TX: {packet_hex} ({description})")

            # 응답 대기 (5초 타임아웃)
            response_data = b""
            response_time = None

            while time.time() - start_time < 5.0:
                if self.serial_conn.in_waiting > 0:
                    new_data = self.serial_conn.read(self.serial_conn.in_waiting)
                    response_data += new_data

                    # 완전한 패킷 확인 (FEFE로 끝나는지)
                    if response_data.endswith(b"\xfe\xfe") and len(response_data) >= 6:
                        response_time = time.time()
                        break

                time.sleep(0.001)  # 1ms 대기

            if response_time:
                response_hex = response_data.hex().upper()
                # 2바이트씩 공백으로 구분
                formatted_hex = " ".join(
                    [response_hex[i : i + 2] for i in range(0, len(response_hex), 2)]
                )

                response_delay = (response_time - send_time) * 1000  # ms
                print(f"📥 RX: {formatted_hex} (+{response_delay:.1f}ms)")

                return {
                    "success": True,
                    "tx_packet": packet_hex,
                    "rx_packet": formatted_hex,
                    "response_time_ms": response_delay,
                    "description": description,
                }
            else:
                print(f"❌ 응답 타임아웃 (5초)")
                return {
                    "success": False,
                    "tx_packet": packet_hex,
                    "error": "Timeout",
                    "description": description,
                }

        except Exception as e:
            print(f"❌ 통신 오류: {e}")
            return {
                "success": False,
                "tx_packet": packet_hex,
                "error": str(e),
                "description": description,
            }

    def run_mcu_sequence_test(self) -> bool:
        """실제 로그와 동일한 MCU 시퀀스 테스트"""
        print("\n🚀 MCU 시퀀스 테스트 시작")
        print("=" * 60)

        # 실제 로그에서 확인된 명령 시퀀스
        test_sequence = [
            {
                "tx": "FF FF 01 04 00 00 00 01 FE FE",
                "desc": "CMD_ENTER_TEST_MODE (모드 1)",
                "expect_immediate": True,
            },
            {
                "tx": "FF FF 02 04 00 00 02 08 FE FE",
                "desc": "CMD_SET_UPPER_TEMP (52°C)",
                "expect_immediate": True,
            },
            {
                "tx": "FF FF 03 04 00 00 00 0A FE FE",
                "desc": "CMD_SET_FAN_SPEED (레벨 10)",
                "expect_immediate": True,
            },
            {
                "tx": "FF FF 04 0C 00 00 02 08 00 00 01 5E 00 00 27 10 FE FE",
                "desc": "CMD_LMA_INIT (동작:52°C, 대기:35°C)",
                "expect_immediate": True,
                "expect_delayed": True,  # 온도 도달 신호도 기대
            },
            {
                "tx": "FF FF 08 00 FE FE",
                "desc": "CMD_STROKE_INIT_COMPLETE",
                "expect_immediate": True,
                "expect_delayed": True,  # 온도 변화 신호도 기대
            },
        ]

        session_start = time.time()
        all_success = True

        for i, cmd in enumerate(test_sequence):
            print(f"\n[{i+1}/{len(test_sequence)}] {cmd['desc']}")

            result = self.send_packet(cmd["tx"], cmd["desc"])
            self.test_results.append(result)

            if not result.get("success", False):
                print(f"❌ 명령 실패!")
                all_success = False
                continue

            # 즉시 응답 확인
            if cmd.get("expect_immediate", False):
                response_time = result.get("response_time_ms", 0)
                if response_time < 100:  # 100ms 이하면 즉시 응답
                    print(f"✅ 즉시 응답 확인 ({response_time:.1f}ms)")
                else:
                    print(f"⚠️ 응답 지연 ({response_time:.1f}ms)")

            # 추가 응답 대기 (LMA_INIT, STROKE_INIT의 경우)
            if cmd.get("expect_delayed", False):
                print(f"⏳ 추가 응답 대기 중...")
                delayed_result = self.wait_for_additional_response()
                if delayed_result:
                    self.test_results.append(delayed_result)
                    print(
                        f"📥 추가 응답: {delayed_result['rx_packet']} (+{delayed_result['response_time_ms']:.1f}ms)"
                    )

        session_time = time.time() - session_start
        print(f"\n⏱️ 전체 테스트 시간: {session_time:.3f}초")

        if all_success:
            print("✅ 모든 명령 성공!")
        else:
            print("❌ 일부 명령 실패")

        return all_success

    def wait_for_additional_response(self, timeout: float = 15.0) -> Optional[Dict]:
        """추가 응답 대기"""
        if not self.serial_conn or not self.serial_conn.is_open:
            return None

        start_time = time.time()
        response_data = b""

        while time.time() - start_time < timeout:
            if self.serial_conn.in_waiting > 0:
                new_data = self.serial_conn.read(self.serial_conn.in_waiting)
                response_data += new_data

                # 완전한 패킷 확인
                if response_data.endswith(b"\xfe\xfe") and len(response_data) >= 6:
                    response_time = time.time()
                    response_hex = response_data.hex().upper()
                    formatted_hex = " ".join(
                        [response_hex[i : i + 2] for i in range(0, len(response_hex), 2)]
                    )

                    response_delay = (response_time - start_time) * 1000

                    return {
                        "success": True,
                        "rx_packet": formatted_hex,
                        "response_time_ms": response_delay,
                        "description": "Additional response",
                    }

            time.sleep(0.01)  # 10ms 대기

        return None

    def save_results(self, filename: str = None):
        """테스트 결과 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results/simple_test_results_{timestamp}.json"

        results_data = {
            "test_info": {
                "test_type": "Simple Serial Communication",
                "port": self.port,
                "baudrate": self.baudrate,
                "timestamp": datetime.now().isoformat(),
            },
            "results": self.test_results,
            "summary": {
                "total_commands": len([r for r in self.test_results if "tx_packet" in r]),
                "successful_commands": len(
                    [r for r in self.test_results if r.get("success", False)]
                ),
                "avg_response_time": (
                    sum(
                        [
                            r.get("response_time_ms", 0)
                            for r in self.test_results
                            if r.get("success", False)
                        ]
                    )
                    / max(1, len([r for r in self.test_results if r.get("success", False)]))
                ),
            },
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            print(f"📊 결과 저장: {filename}")
        except Exception as e:
            print(f"❌ 결과 저장 실패: {e}")


def main():
    """메인 실행"""
    print("🔧 단순 시리얼 통신 테스트")
    print("=" * 40)

    # 포트 설정 (필요시 수정)
    tester = SimpleSerialTester(port="COM4", baudrate=115200)

    try:
        # MCU 연결
        if not tester.connect():
            return

        # 시퀀스 테스트 실행
        success = tester.run_mcu_sequence_test()

        # 결과 저장
        tester.save_results()

        print(f"\n🎯 테스트 결과: {'성공' if success else '실패'}")

    except KeyboardInterrupt:
        print("\n⏹️ 사용자 중단")
    except Exception as e:
        print(f"\n❌ 테스트 오류: {e}")
    finally:
        tester.disconnect()


if __name__ == "__main__":
    main()
