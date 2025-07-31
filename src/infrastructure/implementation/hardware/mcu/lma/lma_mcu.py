"""
LMA MCU Service

Integrated service for LMA MCU hardware control.
Handles temperature control, test modes, and fan management.
"""

import asyncio
import struct
from typing import Any, Dict, Optional

from loguru import logger

from application.interfaces.hardware.mcu import MCUService
from domain.enums.mcu_enums import MCUStatus, TestMode
from domain.exceptions.eol_exceptions import (
    HardwareConnectionError,
    HardwareOperationError,
)
from driver.serial.serial import (
    SerialConnection,
    SerialManager,
)
from infrastructure.implementation.hardware.mcu.lma.constants import (
    BOOT_COMPLETE_TIMEOUT,
    CMD_ENTER_TEST_MODE,
    CMD_LMA_INIT,
    CMD_REQUEST_TEMP,
    CMD_SET_COOLING_TEMP,
    CMD_SET_FAN_SPEED,
    CMD_SET_OPERATING_TEMP,
    CMD_SET_UPPER_TEMP,
    ETX,
    FAN_SPEED_MAX,
    FAN_SPEED_MIN,
    FRAME_CMD_SIZE,
    FRAME_ETX_SIZE,
    FRAME_LEN_SIZE,
    FRAME_STX_SIZE,
    STATUS_BOOT_COMPLETE,
    STATUS_FAN_SPEED_OK,
    STATUS_MESSAGES,
    STATUS_OPERATING_TEMP_OK,
    STATUS_OPERATING_TEMP_REACHED,
    STATUS_STANDBY_TEMP_REACHED,
    STATUS_TEMP_RESPONSE,
    STATUS_TEST_MODE_COMPLETE,
    STATUS_UPPER_TEMP_OK,
    STX,
    TEMP_SCALE_FACTOR,
    TEST_MODE_1,
    TEST_MODE_2,
    TEST_MODE_3,
)
from infrastructure.implementation.hardware.mcu.lma.error_codes import (
    LMACommunicationError,
    LMAError,
    LMAErrorCode,
    LMAHardwareError,
    validate_fan_speed,
    validate_temperature,
)


class LMAMCU(MCUService):
    """LMA MCU 통합 서비스"""

    def __init__(
        self,
        config: Dict[str, Any],
    ):
        """
        초기화

        Args:
            config: MCU 설정 딕셔너리
        """
        # Connection defaults
        self._port = config.get("port", "COM4")
        self._baudrate = config.get("baudrate", 115200)
        self._timeout = config.get("timeout", 2.0)
        self._bytesize = config.get("bytesize", 8)
        self._stopbits = config.get("stopbits", 1)
        self._parity = config.get("parity", None)

        # Operational defaults
        self._temperature = config.get("default_temperature", 25.0)
        self._fan_speed = config.get("default_fan_speed", 50.0)

        # Limits
        self._max_temperature = config.get("max_temperature", 150.0)
        self._min_temperature = config.get("min_temperature", -40.0)
        self._max_fan_speed = config.get("max_fan_speed", 100.0)

        # State initialization
        # Config values are already stored directly above

        self._connection: Optional[SerialConnection] = None
        self._is_connected = False
        self._current_temperature: float = self._temperature
        self._target_temperature: float = self._temperature
        self._current_test_mode: TestMode = TestMode.MODE_1
        self._current_fan_speed: float = self._fan_speed
        self._mcu_status: MCUStatus = MCUStatus.IDLE

    async def connect(self) -> None:
        """
        하드웨어 연결

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            logger.info("Connecting to LMA MCU at %s (baudrate: %s)", self._port, self._baudrate)

            self._connection = await SerialManager.create_connection(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout,
                bytesize=self._bytesize,
                stopbits=self._stopbits,
                parity=self._parity,
            )

            # Wait for boot complete message with timeout protection
            await asyncio.wait_for(
                self._wait_for_boot_complete(),
                timeout=BOOT_COMPLETE_TIMEOUT + 2.0,  # Extra time for connection setup
            )

            self._is_connected = True
            logger.info("LMA MCU connected successfully")

        except Exception as e:
            error_msg = f"Failed to connect to LMA MCU: {e}"
            logger.error(error_msg)
            self._is_connected = False
            raise HardwareConnectionError(
                "lma_mcu",
                "connect",
                error_msg,
            ) from e

    async def disconnect(self) -> None:
        """
        하드웨어 연결 해제

        Raises:
            HardwareOperationError: If disconnection fails
        """
        try:
            if self._connection:
                await self._connection.disconnect()
                self._connection = None

            self._is_connected = False
            logger.info("LMA MCU disconnected")

        except Exception as e:
            error_msg = f"Error disconnecting LMA MCU: {e}"
            logger.error(error_msg)

            raise HardwareOperationError(
                "lma_mcu",
                "disconnect",
                error_msg,
            ) from e

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return (
            self._is_connected
            and self._connection is not None
            and self._connection.is_connected() is True
        )

    async def _ensure_connected(self) -> None:
        """
        연결 상태 확인 및 예외 발생

        Raises:
            HardwareConnectionError: 연결되지 않은 경우
        """
        if not await self.is_connected():
            raise HardwareConnectionError("lma_mcu", "LMA MCU is not connected")

    async def set_temperature(self, target_temp: Optional[float] = None) -> None:
        """
        목표 온도 설정

        Args:
            target_temp: 목표 온도 (°C). None인 경우 기본값 사용

        Raises:
            HardwareOperationError: If temperature setting fails
        """
        await self._ensure_connected()

        # Apply default + override pattern
        effective_temp = target_temp if target_temp is not None else self._temperature

        validate_temperature(effective_temp, self._min_temperature, self._max_temperature)

        try:
            # Send operating temperature command and wait for confirmation
            await self._send_and_wait_for(
                CMD_SET_OPERATING_TEMP,
                self._encode_temperature(effective_temp),
                STATUS_OPERATING_TEMP_OK,
            )
            self._target_temperature = effective_temp

            logger.info("LMA target temperature set to %s°C", effective_temp)

        except LMAError as e:
            error_msg = f"Failed to set LMA temperature: {e}"
            logger.error(error_msg)

            raise HardwareOperationError(
                "lma_mcu",
                "set_temperature",
                error_msg,
            ) from e

    async def get_temperature(self) -> float:
        """
        현재 온도 측정

        Returns:
            현재 온도 (°C)
        """
        await self._ensure_connected()

        try:
            response = await self._send_and_wait_for(CMD_REQUEST_TEMP, b"", STATUS_TEMP_RESPONSE)
            temp_data = response.get("data", b"\x00\x00")
            self._current_temperature = self._decode_temperature(temp_data)
            return self._current_temperature

        except LMAError as e:
            logger.error("Failed to get LMA temperature: %s", e)
            raise RuntimeError(f"Temperature measurement failed: {e}") from e

    async def set_test_mode(self, mode: TestMode) -> None:
        """
        테스트 모드 설정

        Args:
            mode: 테스트 모드

        Raises:
            HardwareOperationError: If test mode setting fails
        """
        await self._ensure_connected()

        try:
            mode_mapping = {
                TestMode.MODE_1: TEST_MODE_1,
                TestMode.MODE_2: TEST_MODE_2,
                TestMode.MODE_3: TEST_MODE_3,
            }

            lma_mode = mode_mapping.get(mode)
            if lma_mode is None:
                raise ValueError(f"Invalid test mode: {mode}")

            # Send test mode command and wait for confirmation
            mode_data = struct.pack("<I", lma_mode)
            await self._send_and_wait_for(
                CMD_ENTER_TEST_MODE,
                mode_data,
                STATUS_TEST_MODE_COMPLETE,
            )

            self._current_test_mode = mode
            logger.info("LMA test mode set to %s", mode)

        except (LMAError, ValueError) as e:
            error_msg = f"Failed to set LMA test mode: {e}"
            logger.error(error_msg)

            raise HardwareOperationError(
                "lma_mcu",
                "set_test_mode",
                error_msg,
            ) from e

    async def get_test_mode(self) -> TestMode:
        """
        현재 테스트 모드 조회

        Returns:
            현재 테스트 모드
        """
        await self._ensure_connected()

        return self._current_test_mode

    async def wait_boot_complete(self) -> None:
        """
        MCU 부팅 완료 신호 대기

        MCU가 완전히 부팅되고 준비될 때까지 대기합니다.

        Raises:
            HardwareConnectionError: 연결되지 않은 경우
            RuntimeError: 부팅 완료 타임아웃
        """
        await self._ensure_connected()

        try:
            # Add timeout protection to boot complete wait
            await asyncio.wait_for(
                self._wait_for_boot_complete(),
                timeout=BOOT_COMPLETE_TIMEOUT + 1.0,  # Add extra buffer time
            )
        except asyncio.TimeoutError as e:
            logger.error("MCU boot complete wait timed out")
            raise RuntimeError("MCU boot complete timeout") from e
        except Exception as e:
            logger.error("MCU boot complete wait failed: %s", e)
            raise RuntimeError(f"MCU boot complete timeout: {e}") from e

    async def set_fan_speed(self, speed_percent: Optional[float] = None) -> None:
        """
        팬 속도 설정

        Args:
            speed_percent: 팬 속도 (0-100%). None인 경우 기본값 사용

        Raises:
            HardwareOperationError: If fan speed setting fails
        """
        await self._ensure_connected()

        # Apply default + override pattern
        effective_speed = speed_percent if speed_percent is not None else self._fan_speed

        if not 0 <= effective_speed <= self._max_fan_speed:

            raise HardwareOperationError(
                "lma_mcu",
                "set_fan_speed",
                f"Fan speed must be 0-{self._max_fan_speed}%, got {effective_speed}%",
            )

        try:
            # Convert percentage to LMA fan speed level (1-10)
            # 0% -> level 1, 100% -> level 10
            if effective_speed == 0:
                fan_level = 1
            else:
                fan_level = max(1, min(10, int((effective_speed / 100.0) * 9) + 1))
            validate_fan_speed(fan_level, FAN_SPEED_MIN, FAN_SPEED_MAX)

            # Send fan speed command and wait for confirmation
            fan_data = struct.pack("<B", fan_level)
            await self._send_and_wait_for(
                CMD_SET_FAN_SPEED,
                fan_data,
                STATUS_FAN_SPEED_OK,
            )

            self._current_fan_speed = effective_speed
            logger.info("LMA fan speed set to %s%% (level %s)", effective_speed, fan_level)

        except (LMAError, ValueError) as e:
            error_msg = f"Failed to set LMA fan speed: {e}"
            logger.error(error_msg)

            raise HardwareOperationError(
                "lma_mcu",
                "set_fan_speed",
                error_msg,
            ) from e

    async def get_fan_speed(self) -> float:
        """
        현재 팬 속도 조회

        Returns:
            현재 팬 속도 (0-100%)
        """
        await self._ensure_connected()

        return self._current_fan_speed

    async def set_upper_temperature(self, upper_temp: float) -> None:
        """
        상한 온도 설정

        Args:
            upper_temp: 상한 온도 (°C)

        Raises:
            HardwareOperationError: If upper temperature setting fails
        """
        await self._ensure_connected()

        validate_temperature(upper_temp, self._min_temperature, self._max_temperature)

        try:
            # Send upper temperature command and wait for confirmation
            await self._send_and_wait_for(
                CMD_SET_UPPER_TEMP,
                self._encode_temperature(upper_temp),
                STATUS_UPPER_TEMP_OK,
            )

            logger.info("LMA upper temperature set to %s°C", upper_temp)

        except LMAError as e:
            error_msg = f"Failed to set LMA upper temperature: {e}"
            logger.error(error_msg)

            raise HardwareOperationError(
                "lma_mcu",
                "set_upper_temperature",
                error_msg,
            ) from e

    async def start_standby_heating(
        self,
        operating_temp: float,
        standby_temp: float,
        hold_time_ms: int = 10000,
    ) -> None:
        """
        대기 가열 시작

        Args:
            operating_temp: 동작온도 (°C)
            standby_temp: 대기온도 (°C)
            hold_time_ms: 유지시간 (밀리초)

        Raises:
            HardwareOperationError: If heating start fails
        """
        await self._ensure_connected()

        # 온도 범위 검증
        validate_temperature(operating_temp, self._min_temperature, self._max_temperature)
        validate_temperature(standby_temp, self._min_temperature, self._max_temperature)

        try:
            # 온도 스케일링 (프로토콜에 맞게 정수로 변환)
            op_temp_int = int(operating_temp * TEMP_SCALE_FACTOR)
            standby_temp_int = int(standby_temp * TEMP_SCALE_FACTOR)

            # 12바이트 데이터 패킹: 동작온도(4B) + 대기온도(4B) + 유지시간(4B)
            data = struct.pack(
                "<III",
                op_temp_int,
                standby_temp_int,
                hold_time_ms,
            )

            # LMA 초기화 명령 전송 및 응답 대기
            await self._send_and_wait_for(
                CMD_LMA_INIT,
                data,
                STATUS_OPERATING_TEMP_REACHED,
            )
            self._mcu_status = MCUStatus.HEATING

            logger.info(
                f"LMA standby heating started - op:{operating_temp}°C, "
                f"standby:{standby_temp}°C, hold:{hold_time_ms}ms"
            )

        except LMAError as e:
            error_msg = f"Failed to start LMA standby heating: {e}"
            logger.error(error_msg)

            raise HardwareOperationError(
                "lma_mcu",
                "start_standby_heating",
                error_msg,
            ) from e

    async def start_standby_cooling(self) -> None:
        """
        대기 냉각 시작

        Raises:
            HardwareOperationError: If cooling start fails
        """
        await self._ensure_connected()

        try:
            # Send cooling command with 0x00 data
            await self._send_and_wait_for(
                CMD_SET_COOLING_TEMP,
                b"\x00",
                STATUS_STANDBY_TEMP_REACHED,
            )
            self._mcu_status = MCUStatus.COOLING

            logger.info("LMA standby cooling started")

        except LMAError as e:
            error_msg = f"Failed to start LMA standby cooling: {e}"
            logger.error(error_msg)

            raise HardwareOperationError(
                "lma_mcu",
                "start_standby_cooling",
                error_msg,
            ) from e

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Returns:
            상태 정보 딕셔너리
        """
        status = {
            "connected": await self.is_connected(),
            "port": self._port,
            "baudrate": self._baudrate,
            "current_temperature": self._current_temperature,
            "target_temperature": self._target_temperature,
            "test_mode": self._current_test_mode.name,
            "fan_speed": self._current_fan_speed,
            "mcu_status": self._mcu_status.name,
            "hardware_type": "LMA",
        }

        if await self.is_connected():
            try:
                # Get current temperature
                current_temp = await self.get_temperature()
                status["current_temperature"] = current_temp
                status["last_error"] = None
            except Exception as e:
                status["last_error"] = str(e)

        return status

    # Private helper methods

    async def _wait_for_boot_complete(self) -> None:
        """Wait for MCU boot complete message"""
        try:
            # Wait for boot complete status
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < BOOT_COMPLETE_TIMEOUT:
                try:
                    response = await self._receive_response(timeout=1.0)
                    if response and response.get("status") == STATUS_BOOT_COMPLETE:
                        logger.info("LMA MCU boot complete")
                        return
                except asyncio.TimeoutError:
                    continue

            raise LMAHardwareError(
                "Boot complete timeout",
                error_code=int(LMAErrorCode.HARDWARE_INITIALIZATION_FAILED),
            )

        except Exception as e:
            raise LMAHardwareError(f"Boot wait failed: {e}") from e

    async def _send_command(self, command: int, data: bytes = b"") -> None:
        """Send command to LMA MCU (전송만)"""
        if not self._connection:
            raise LMACommunicationError("No connection available")

        try:
            # Build frame: STX + CMD + LEN + DATA + ETX
            frame = STX + struct.pack("B", command) + struct.pack("B", len(data)) + data + ETX

            # Send frame
            await self._connection.write(frame)

            logger.debug("LMA command 0x%02X sent", command)

        except Exception as e:
            raise LMACommunicationError(f"Command send failed: {e}") from e

    async def _wait_for_response(
        self, target_status: int, max_attempts: int = 10
    ) -> Dict[str, Any]:
        """
        특정 응답 상태를 기다림 (방법 2: 로그 남기고 버리기)

        Args:
            target_status: 기다릴 응답 상태 코드
            max_attempts: 최대 시도 횟수

        Returns:
            타겟 응답 딕셔너리

        Raises:
            LMACommunicationError: 타겟 응답을 받지 못한 경우
        """
        for attempt in range(max_attempts):
            try:
                response = await self._receive_response()

                if response and response["status"] == target_status:
                    logger.debug(
                        f"Got target response: status=0x{response['status']:02X}, "
                        f"message='{response['message']}'"
                    )
                    return response

                # 원하지 않는 응답은 로그 남기고 버림
                if response:
                    logger.debug(
                        f"Discarding unwanted response: status=0x{response['status']:02X}, "
                        f"message='{response['message']}' (waiting for 0x{target_status:02X})"
                    )
                else:
                    logger.debug("Received None response (attempt %s/%s)", attempt + 1, max_attempts)

            except Exception as e:
                logger.debug("Response receive error (attempt %s/%s): %s", attempt + 1, max_attempts, e)

        raise LMACommunicationError(
            f"Target response 0x{target_status:02X} not received after {max_attempts} attempts"
        )

    async def _send_and_wait_for(
        self, command: int, data: bytes, target_status: int
    ) -> Dict[str, Any]:
        """
        명령 전송 + 특정 응답 대기 (타임아웃 보호)

        Args:
            command: 명령 코드
            data: 데이터
            target_status: 기다릴 응답 상태 코드

        Returns:
            타겟 응답 딕셔너리

        Raises:
            TimeoutError: 응답 타임아웃
        """
        await self._send_command(command, data)

        # Add timeout protection to prevent hanging
        try:
            return await asyncio.wait_for(
                self._wait_for_response(target_status),
                timeout=self._timeout * 2,  # Allow extra time for complex operations
            )
        except asyncio.TimeoutError as e:
            logger.error("Timeout waiting for response 0x%02X", target_status)
            raise TimeoutError(
                f"Operation timed out waiting for response 0x{target_status:02X}"
            ) from e

    async def _receive_response(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Receive response from LMA MCU"""
        if not self._connection:
            raise LMACommunicationError("No connection available")

        try:
            response_timeout = timeout or self._timeout

            # Read STX
            stx_data = await self._connection.read(FRAME_STX_SIZE, response_timeout)
            if stx_data != STX:
                raise LMACommunicationError("Invalid STX")

            # Read status and length
            header = await self._connection.read(
                FRAME_CMD_SIZE + FRAME_LEN_SIZE,
                response_timeout,
            )
            status = header[0]
            data_len = header[1]

            # Read data if present
            data = b""
            if data_len > 0:
                data = await self._connection.read(data_len, response_timeout)

            # Read ETX
            etx_data = await self._connection.read(FRAME_ETX_SIZE, response_timeout)
            if etx_data != ETX:
                raise LMACommunicationError("Invalid ETX")

            return {
                "status": status,
                "data": data,
                "message": STATUS_MESSAGES.get(
                    status,
                    f"Unknown status: 0x{status:02X}",
                ),
            }

        except Exception as e:
            raise LMACommunicationError(f"Response receive failed: {e}") from e

    def _encode_temperature(self, temperature: float) -> bytes:
        """Encode temperature for LMA protocol"""
        temp_int = int(temperature * TEMP_SCALE_FACTOR)
        return struct.pack("<h", temp_int)  # signed short, little endian

    def _decode_temperature(self, data: bytes) -> float:
        """Decode temperature from LMA protocol"""
        if len(data) >= 2:
            temp_int = struct.unpack("<h", data[:2])[0]
            return float(temp_int) / TEMP_SCALE_FACTOR
        return 0.0
