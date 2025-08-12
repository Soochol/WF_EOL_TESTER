#!/usr/bin/env python3
"""
Fast LMAMCU 구현 테스트

simple_serial_test.py의 성능을 기반으로 한 빠른 LMAMCU 클래스 구현
기존 LMAMCU와 동일한 인터페이스를 제공하면서 성능 최적화
"""

import serial
import time
import struct
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

# 프로젝트 루트를 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from src.domain.enums.mcu_enums import TestMode, MCUStatus
    from src.domain.exceptions.eol_exceptions import HardwareConnectionError, HardwareOperationError
except ImportError as e:
    print(f"⚠️ 프로젝트 모듈 임포트 실패: {e}")
    print("Mock enums 사용")

    # Mock enums for standalone testing
    class TestMode(Enum):
        MODE_1 = 1
        MODE_2 = 2
        MODE_3 = 3

    class MCUStatus(Enum):
        IDLE = "idle"
        HEATING = "heating"
        COOLING = "cooling"


# LMA MCU 상수들
TEMP_SCALE_FACTOR = 10
DEFAULT_TIMEOUT = 5.0


class FastLMAMCU:
    """
    빠른 LMA MCU 클래스

    simple_serial_test.py의 직접적인 통신 방식을 기반으로 구현
    복잡한 버퍼 관리나 노이즈 처리 없이 핵심 기능에 집중
    """

    def __init__(self):
        self.serial_conn: Optional[serial.Serial] = None
        self._port = ""
        self._baudrate = 0
        self._timeout = DEFAULT_TIMEOUT

        # 상태 관리
        self._is_connected = False
        self._current_temperature = 0.0
        self._target_temperature = 0.0
        self._current_test_mode = TestMode.MODE_1
        self._current_fan_speed = 0.0
        self._mcu_status = MCUStatus.IDLE

    async def connect(
        self,
        port: str,
        baudrate: int,
        timeout: float,
        bytesize: int = 8,
        stopbits: int = 1,
        parity: Optional[str] = None,
    ) -> None:
        """MCU 연결 (pyserial 직접 사용)"""
        try:
            self._port = port
            self._baudrate = baudrate
            self._timeout = timeout

            print(f"🔌 Fast MCU 연결 시도: {port} @ {baudrate}")

            # pyserial 직접 사용 (추상화 레이어 우회)
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=serial.PARITY_NONE if parity is None else parity,
                stopbits=stopbits,
                timeout=timeout,
            )

            self._is_connected = True
            print("✅ Fast MCU 연결 성공")

        except Exception as e:
            self._is_connected = False
            error_msg = f"Fast MCU 연결 실패: {e}"
            print(f"❌ {error_msg}")
            raise HardwareConnectionError("fast_lma_mcu", "connect", error_msg) from e

    async def disconnect(self) -> None:
        """MCU 연결 해제"""
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
                print("📴 Fast MCU 연결 해제")

            self._is_connected = False

        except Exception as e:
            error_msg = f"Fast MCU 해제 오류: {e}"
            print(f"⚠️ {error_msg}")
            raise HardwareOperationError("fast_lma_mcu", "disconnect", error_msg) from e

    async def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._is_connected and self.serial_conn and self.serial_conn.is_open

    def _ensure_connected(self) -> None:
        """연결 상태 확인 (동기 버전)"""
        if not self._is_connected or not self.serial_conn or not self.serial_conn.is_open:
            raise HardwareConnectionError("fast_lma_mcu", "Not connected")

    def _send_packet_sync(self, packet_hex: str, description: str = "") -> Optional[bytes]:
        """
        패킷 전송 및 응답 수신 (동기 버전)
        simple_serial_test.py의 로직을 그대로 사용
        """
        self._ensure_connected()

        try:
            # 패킷 전송
            packet_bytes = bytes.fromhex(packet_hex.replace(" ", ""))
            start_time = time.time()

            self.serial_conn.write(packet_bytes)
            print(f"📤 TX: {packet_hex} ({description})")

            # 응답 대기
            response_data = b""
            while time.time() - start_time < self._timeout:
                if self.serial_conn.in_waiting > 0:
                    new_data = self.serial_conn.read(self.serial_conn.in_waiting)
                    response_data += new_data

                    # 완전한 패킷 확인 (FEFE로 끝나는지)
                    if response_data.endswith(b"\xfe\xfe") and len(response_data) >= 6:
                        response_hex = response_data.hex().upper()
                        formatted_hex = " ".join(
                            [response_hex[i : i + 2] for i in range(0, len(response_hex), 2)]
                        )

                        response_time = (time.time() - start_time) * 1000
                        print(f"📥 RX: {formatted_hex} (+{response_time:.1f}ms)")

                        return response_data

                time.sleep(0.001)  # 1ms 대기

            print(f"❌ 응답 타임아웃 ({self._timeout}s)")
            return None

        except Exception as e:
            print(f"❌ 통신 오류: {e}")
            raise HardwareOperationError("fast_lma_mcu", "_send_packet_sync", str(e)) from e

    async def _send_packet(self, packet_hex: str, description: str = "") -> Optional[bytes]:
        """비동기 래퍼"""
        return self._send_packet_sync(packet_hex, description)

    def _wait_for_additional_response(
        self, timeout: float = 15.0, description: str = ""
    ) -> Optional[bytes]:
        """
        추가 응답 대기 (온도 도달 신호 등)
        simple_serial_test.py의 로직 사용
        """
        self._ensure_connected()

        start_time = time.time()
        response_data = b""

        print(f"⏳ 추가 응답 대기 중... ({description})")

        while time.time() - start_time < timeout:
            if self.serial_conn.in_waiting > 0:
                new_data = self.serial_conn.read(self.serial_conn.in_waiting)
                response_data += new_data

                # 완전한 패킷 확인
                if response_data.endswith(b"\xfe\xfe") and len(response_data) >= 6:
                    response_hex = response_data.hex().upper()
                    formatted_hex = " ".join(
                        [response_hex[i : i + 2] for i in range(0, len(response_hex), 2)]
                    )

                    response_time = (time.time() - start_time) * 1000
                    print(f"📥 추가 응답: {formatted_hex} (+{response_time:.1f}ms)")

                    return response_data

            time.sleep(0.01)  # 10ms 대기

        print(f"⏰ 추가 응답 타임아웃 ({timeout}s)")
        return None

    # ===== 기존 LMAMCU와 동일한 인터페이스 구현 =====

    async def set_test_mode(self, mode: TestMode) -> None:
        """테스트 모드 설정"""
        self._ensure_connected()

        try:
            # 테스트 모드 매핑 (문자열 값을 정수로 변환)
            mode_mapping = {TestMode.MODE_1: 1, TestMode.MODE_2: 2, TestMode.MODE_3: 3}

            if mode in mode_mapping:
                mode_value = mode_mapping[mode]
            else:
                # Fallback for integer values
                mode_value = int(mode) if not hasattr(mode, "value") else 1

            packet = f"FFFF0104{mode_value:08X}FEFE"

            response = await self._send_packet(packet, f"CMD_ENTER_TEST_MODE (모드 {mode_value})")

            if not response or len(response) < 6 or response[2] != 0x01:
                raise HardwareOperationError("fast_lma_mcu", "set_test_mode", "Invalid response")

            self._current_test_mode = mode
            print(f"✅ 테스트 모드 설정: {mode}")

        except Exception as e:
            error_msg = f"테스트 모드 설정 실패: {e}"
            print(f"❌ {error_msg}")
            raise HardwareOperationError("fast_lma_mcu", "set_test_mode", error_msg) from e

    async def set_upper_temperature(self, upper_temp: float) -> None:
        """상한 온도 설정"""
        self._ensure_connected()

        try:
            temp_scaled = int(upper_temp * TEMP_SCALE_FACTOR)
            packet = f"FFFF0204{temp_scaled:08X}FEFE"

            response = await self._send_packet(packet, f"CMD_SET_UPPER_TEMP ({upper_temp}°C)")

            if not response or len(response) < 6 or response[2] != 0x02:
                raise HardwareOperationError(
                    "fast_lma_mcu", "set_upper_temperature", "Invalid response"
                )

            print(f"✅ 상한 온도 설정: {upper_temp}°C")

        except Exception as e:
            error_msg = f"상한 온도 설정 실패: {e}"
            print(f"❌ {error_msg}")
            raise HardwareOperationError("fast_lma_mcu", "set_upper_temperature", error_msg) from e

    async def set_fan_speed(self, fan_level: int) -> None:
        """팬 속도 설정"""
        self._ensure_connected()

        try:
            packet = f"FFFF0304{fan_level:08X}FEFE"

            response = await self._send_packet(packet, f"CMD_SET_FAN_SPEED (레벨 {fan_level})")

            if not response or len(response) < 6 or response[2] != 0x03:
                raise HardwareOperationError("fast_lma_mcu", "set_fan_speed", "Invalid response")

            self._current_fan_speed = float(fan_level)
            print(f"✅ 팬 속도 설정: 레벨 {fan_level}")

        except Exception as e:
            error_msg = f"팬 속도 설정 실패: {e}"
            print(f"❌ {error_msg}")
            raise HardwareOperationError("fast_lma_mcu", "set_fan_speed", error_msg) from e

    async def start_standby_heating(
        self, operating_temp: float, standby_temp: float, hold_time_ms: int = 10000
    ) -> None:
        """대기 가열 시작"""
        self._ensure_connected()

        try:
            # 온도 스케일링
            op_temp_scaled = int(operating_temp * TEMP_SCALE_FACTOR)
            standby_temp_scaled = int(standby_temp * TEMP_SCALE_FACTOR)

            # 12바이트 데이터 패킹
            data = f"{op_temp_scaled:08X}{standby_temp_scaled:08X}{hold_time_ms:08X}"
            packet = f"FFFF040C{data}FEFE"

            # 첫 번째 응답 (즉시 ACK)
            response = await self._send_packet(
                packet, f"CMD_LMA_INIT (동작:{operating_temp}°C, 대기:{standby_temp}°C)"
            )

            if not response or len(response) < 6 or response[2] != 0x04:
                raise HardwareOperationError(
                    "fast_lma_mcu", "start_standby_heating", "Invalid ACK response"
                )

            # 두 번째 응답 대기 (온도 도달)
            temp_response = self._wait_for_additional_response(
                timeout=15.0, description="온도 도달 신호"
            )

            if temp_response and len(temp_response) >= 6 and temp_response[2] == 0x0B:
                print("✅ 동작 온도 도달 확인")
            else:
                print("⚠️ 온도 도달 신호 미확인 (계속 진행)")

            self._mcu_status = MCUStatus.HEATING
            print(f"✅ 대기 가열 시작: 동작 {operating_temp}°C, 대기 {standby_temp}°C")

        except Exception as e:
            error_msg = f"대기 가열 시작 실패: {e}"
            print(f"❌ {error_msg}")
            raise HardwareOperationError("fast_lma_mcu", "start_standby_heating", error_msg) from e

    async def start_standby_cooling(self) -> None:
        """대기 냉각 시작"""
        self._ensure_connected()

        try:
            packet = "FFFF0800FEFE"

            # 첫 번째 응답 (즉시 ACK)
            response = await self._send_packet(packet, "CMD_STROKE_INIT_COMPLETE")

            if not response or len(response) < 6 or response[2] != 0x08:
                raise HardwareOperationError(
                    "fast_lma_mcu", "start_standby_cooling", "Invalid ACK response"
                )

            # 두 번째 응답 대기 (냉각 완료)
            cooling_response = self._wait_for_additional_response(
                timeout=15.0, description="냉각 완료 신호"
            )

            if cooling_response and len(cooling_response) >= 6 and cooling_response[2] == 0x0C:
                print("✅ 대기 온도 도달 확인")
            else:
                print("⚠️ 냉각 완료 신호 미확인 (계속 진행)")

            self._mcu_status = MCUStatus.COOLING
            print("✅ 대기 냉각 시작")

        except Exception as e:
            error_msg = f"대기 냉각 시작 실패: {e}"
            print(f"❌ {error_msg}")
            raise HardwareOperationError("fast_lma_mcu", "start_standby_cooling", error_msg) from e

    async def wait_boot_complete(self) -> None:
        """MCU 부팅 완료 대기"""
        self._ensure_connected()

        try:
            print("⏳ MCU 부팅 완료 신호 대기 중...")

            # 부팅 완료 신호 대기 (간단 구현 - 실제로는 특정 패킷을 기다림)
            boot_timeout = 30.0  # 30초 타임아웃
            start_time = time.time()

            while time.time() - start_time < boot_timeout:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    print(f"📥 부팅 데이터: {data.hex()}")

                    # STATUS_BOOT_COMPLETE (0x30) 확인 (간단 구현)
                    if b"\x30" in data:
                        print("✅ MCU 부팅 완료 확인")
                        return

                await asyncio.sleep(0.1)

            print("⚠️ 부팅 완료 신호 타임아웃 (계속 진행)")

        except Exception as e:
            error_msg = f"MCU 부팅 대기 실패: {e}"
            print(f"❌ {error_msg}")
            raise HardwareOperationError("fast_lma_mcu", "wait_boot_complete", error_msg) from e

    async def set_temperature(self, target_temp: float) -> None:
        """목표 온도 설정 (동작 온도 설정)"""
        self._ensure_connected()

        try:
            temp_scaled = int(target_temp * TEMP_SCALE_FACTOR)
            packet = f"FFFF0504{temp_scaled:08X}FEFE"

            response = await self._send_packet(packet, f"CMD_SET_OPERATING_TEMP ({target_temp}°C)")

            if not response or len(response) < 6 or response[2] != 0x05:
                raise HardwareOperationError("fast_lma_mcu", "set_temperature", "Invalid response")

            self._target_temperature = target_temp
            print(f"✅ 목표 온도 설정: {target_temp}°C")

        except Exception as e:
            error_msg = f"목표 온도 설정 실패: {e}"
            print(f"❌ {error_msg}")
            raise HardwareOperationError("fast_lma_mcu", "set_temperature", error_msg) from e

    async def get_temperature(self) -> float:
        """현재 온도 조회 (실제 MCU에서 읽기)"""
        self._ensure_connected()

        try:
            # 온도 요청 패킷 (CMD_REQUEST_TEMP)
            packet = "FFFF0700FEFE"

            response = await self._send_packet(packet, "CMD_REQUEST_TEMP")

            if response and len(response) >= 10 and response[2] == 0x07:
                # 온도 데이터 추출 (4바이트, little endian)
                temp_data = response[4:8]
                temp_scaled = struct.unpack("<I", temp_data)[0]
                temp_celsius = temp_scaled / TEMP_SCALE_FACTOR

                self._current_temperature = temp_celsius
                print(f"📊 현재 온도: {temp_celsius:.1f}°C")
                return temp_celsius
            else:
                print("⚠️ 온도 읽기 실패, 캐시된 값 반환")
                return self._current_temperature

        except Exception as e:
            print(f"❌ 온도 조회 오류: {e}, 캐시된 값 반환")
            return self._current_temperature

    async def get_test_mode(self) -> TestMode:
        """현재 테스트 모드 조회"""
        return self._current_test_mode

    async def get_fan_speed(self) -> int:
        """현재 팬 속도 조회"""
        return int(self._current_fan_speed)

    async def get_status(self) -> Dict[str, Any]:
        """하드웨어 상태 조회"""
        return {
            "connected": await self.is_connected(),
            "port": self._port,
            "baudrate": self._baudrate,
            "current_temperature": self._current_temperature,
            "target_temperature": self._target_temperature,
            "test_mode": (
                self._current_test_mode.name
                if hasattr(self._current_test_mode, "name")
                else str(self._current_test_mode)
            ),
            "fan_speed": self._current_fan_speed,
            "mcu_status": (
                self._mcu_status.name
                if hasattr(self._mcu_status, "name")
                else str(self._mcu_status)
            ),
            "hardware_type": "FastLMA",
            "implementation": "Fast & Simple",
        }


class FastMCUTester:
    """Fast MCU 테스터"""

    def __init__(self, port: str = "COM4", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.fast_mcu = FastLMAMCU()
        self.test_results: List[Dict] = []

    async def run_performance_test(self) -> bool:
        """Fast MCU 성능 테스트"""
        print("\n🚀 Fast LMAMCU 성능 테스트")
        print("=" * 60)

        session_start = time.time()

        try:
            # MCU 연결
            await self.fast_mcu.connect(port=self.port, baudrate=self.baudrate, timeout=5.0)

            # 테스트 시퀀스 실행
            commands = [
                ("set_test_mode", lambda: self.fast_mcu.set_test_mode(TestMode.MODE_1)),
                ("set_upper_temperature", lambda: self.fast_mcu.set_upper_temperature(52.0)),
                ("set_fan_speed", lambda: self.fast_mcu.set_fan_speed(10)),
                (
                    "start_standby_heating",
                    lambda: self.fast_mcu.start_standby_heating(52.0, 35.0, 10000),
                ),
                ("start_standby_cooling", lambda: self.fast_mcu.start_standby_cooling()),
            ]

            for i, (cmd_name, cmd_func) in enumerate(commands, 1):
                print(f"\n[{i}/{len(commands)}] {cmd_name}")

                cmd_start = time.time()
                success = False
                error_msg = None

                try:
                    await cmd_func()
                    success = True
                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ 실패: {e}")

                cmd_time = time.time() - cmd_start

                result = {
                    "command": cmd_name,
                    "success": success,
                    "execution_time": cmd_time,
                    "error": error_msg,
                }

                self.test_results.append(result)

                if success:
                    print(f"✅ 성공 ({cmd_time*1000:.1f}ms)")

            session_time = time.time() - session_start
            print(f"\n⏱️ 전체 테스트 시간: {session_time:.3f}초")

            return all(r["success"] for r in self.test_results)

        except Exception as e:
            print(f"❌ 테스트 오류: {e}")
            return False
        finally:
            await self.fast_mcu.disconnect()

    def save_results(self):
        """테스트 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results/fast_mcu_test_{timestamp}.json"

        results_data = {
            "test_info": {
                "test_type": "Fast LMAMCU Performance Test",
                "port": self.port,
                "baudrate": self.baudrate,
                "timestamp": datetime.now().isoformat(),
            },
            "results": self.test_results,
            "summary": {
                "total_commands": len(self.test_results),
                "successful_commands": len(
                    [r for r in self.test_results if r.get("success", False)]
                ),
                "total_execution_time": sum(
                    [r.get("execution_time", 0) for r in self.test_results]
                ),
                "avg_execution_time": (
                    sum([r.get("execution_time", 0) for r in self.test_results])
                    / max(1, len(self.test_results))
                ),
            },
        }

        try:
            os.makedirs("test_results", exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            print(f"📊 결과 저장: {filename}")
        except Exception as e:
            print(f"❌ 결과 저장 실패: {e}")


async def main():
    """메인 실행"""
    print("🔧 Fast LMAMCU 테스트")
    print("=" * 40)

    tester = FastMCUTester(port="COM4", baudrate=115200)

    try:
        # 성능 테스트 실행
        success = await tester.run_performance_test()

        # 결과 저장
        tester.save_results()

        print(f"\n🎯 테스트 결과: {'성공' if success else '실패'}")

        if success:
            print("\n💡 Fast LMAMCU 구현 완료!")
            print("   - 단순하고 빠른 통신")
            print("   - 기존 인터페이스 호환")
            print("   - 노이즈 처리 최소화")

    except KeyboardInterrupt:
        print("\n⏹️ 사용자 중단")
    except Exception as e:
        print(f"\n❌ 테스트 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
