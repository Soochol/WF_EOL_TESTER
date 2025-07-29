"""
LMA MCU Service

Integrated service for LMA MCU hardware control.
Handles temperature control, test modes, and fan management.
"""

import asyncio
import struct
from typing import Optional, Dict, Any
from loguru import logger

from application.interfaces.hardware.mcu import MCUService, TestMode, MCUStatus
from domain.value_objects.hardware_configuration import MCUConfig
from driver.serial.serial import SerialManager, SerialError, SerialConnection

from infrastructure.implementation.hardware.mcu.lma.constants import (
    STX,
    ETX,
    FRAME_STX_SIZE,
    FRAME_CMD_SIZE,
    FRAME_LEN_SIZE,
    FRAME_ETX_SIZE,
    CMD_ENTER_TEST_MODE,
    CMD_SET_UPPER_TEMP,
    CMD_SET_FAN_SPEED,
    CMD_LMA_INIT,
    CMD_SET_OPERATING_TEMP,
    CMD_SET_COOLING_TEMP,
    CMD_REQUEST_TEMP,
    STATUS_BOOT_COMPLETE,
    STATUS_TEST_MODE_COMPLETE,
    STATUS_TEMP_RESPONSE,
    STATUS_OPERATING_TEMP_OK,
    STATUS_UPPER_TEMP_OK,
    STATUS_FAN_SPEED_OK,
    STATUS_LMA_INIT_OK,
    STATUS_COOLING_TEMP_OK,
    STATUS_MESSAGES,
    TEST_MODE_1,
    TEST_MODE_2,
    TEST_MODE_3,
    FAN_SPEED_MIN,
    FAN_SPEED_MAX,
    TEMP_SCALE_FACTOR,
    DEFAULT_BAUDRATE,
    DEFAULT_TIMEOUT,
    BOOT_COMPLETE_TIMEOUT,
    MIN_TEMPERATURE,
    MAX_TEMPERATURE,
    DEFAULT_TEMPERATURE,
)
from infrastructure.implementation.hardware.mcu.lma.error_codes import (
    LMAError,
    LMACommunicationError,
    LMAHardwareError,
    LMAOperationError,
    LMAErrorCode,
    validate_temperature,
    validate_fan_speed,
)


class LMAMCU(MCUService):
    """LMA MCU 통합 서비스"""

    def __init__(
        self, port: str, baudrate: int = DEFAULT_BAUDRATE, timeout: float = DEFAULT_TIMEOUT
    ):
        """
        초기화

        Args:
            port: 시리얼 포트 (예: 'COM3', '/dev/ttyUSB0')
            baudrate: 통신 속도
            timeout: 통신 타임아웃 (초)
        """
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout

        self._connection: Optional[SerialConnection] = None
        self._is_connected = False
        self._current_temperature = DEFAULT_TEMPERATURE
        self._target_temperature = DEFAULT_TEMPERATURE
        self._current_test_mode = TestMode.MODE_1
        self._current_fan_speed = 50.0  # percentage
        self._mcu_status = MCUStatus.IDLE

    async def connect(self, mcu_config: MCUConfig) -> None:
        """
        하드웨어 연결

        Args:
            mcu_config: MCU connection configuration

        Raises:
            HardwareConnectionError: If connection fails
        """
        # Update connection parameters from config
        self._port = mcu_config.port
        self._baudrate = mcu_config.baudrate
        self._timeout = mcu_config.timeout

        try:
            logger.info(f"Connecting to LMA MCU at {self._port} (baudrate: {self._baudrate})")

            self._connection = await SerialManager.create_connection(
                port=self._port, baudrate=self._baudrate, timeout=self._timeout
            )

            # Wait for boot complete message
            await self._wait_for_boot_complete()

            self._is_connected = True
            logger.info("LMA MCU connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to LMA MCU: {e}")
            self._is_connected = False
            return False

    async def disconnect(self) -> bool:
        """
        하드웨어 연결 해제

        Returns:
            연결 해제 성공 여부
        """
        try:
            if self._connection:
                await self._connection.disconnect()
                self._connection = None

            self._is_connected = False
            logger.info("LMA MCU disconnected")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting LMA MCU: {e}")
            return False

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected and self._connection and self._connection.is_connected()

    async def set_temperature(self, target_temp: float) -> bool:
        """
        목표 온도 설정

        Args:
            target_temp: 목표 온도 (°C)

        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        validate_temperature(target_temp, MIN_TEMPERATURE, MAX_TEMPERATURE)

        try:
            # Send operating temperature command and wait for confirmation
            await self._send_and_wait_for(
                CMD_SET_OPERATING_TEMP,
                self._encode_temperature(target_temp),
                STATUS_OPERATING_TEMP_OK,
            )
            self._target_temperature = target_temp

            logger.info(f"LMA target temperature set to {target_temp}°C")
            return True

        except LMAError as e:
            logger.error(f"Failed to set LMA temperature: {e}")
            return False

    async def get_temperature(self) -> float:
        """
        현재 온도 측정

        Returns:
            현재 온도 (°C)
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        try:
            response = await self._send_and_wait_for(CMD_REQUEST_TEMP, b"", STATUS_TEMP_RESPONSE)
            temp_data = response.get("data", b"\\x00\\x00")
            self._current_temperature = self._decode_temperature(temp_data)
            return self._current_temperature

        except LMAError as e:
            logger.error(f"Failed to get LMA temperature: {e}")
            raise RuntimeError(f"Temperature measurement failed: {e}")

    async def set_test_mode(self, mode: TestMode) -> bool:
        """
        테스트 모드 설정

        Args:
            mode: 테스트 모드

        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

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
            await self._send_and_wait_for(CMD_ENTER_TEST_MODE, mode_data, STATUS_TEST_MODE_COMPLETE)

            self._current_test_mode = mode
            logger.info(f"LMA test mode set to {mode}")
            return True

        except (LMAError, ValueError) as e:
            logger.error(f"Failed to set LMA test mode: {e}")
            return False

    async def get_test_mode(self) -> TestMode:
        """
        현재 테스트 모드 조회

        Returns:
            현재 테스트 모드
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        return self._current_test_mode

    async def wait_for_boot_complete(self) -> None:
        """
        MCU 부팅 완료 신호 대기

        MCU가 완전히 부팅되고 준비될 때까지 대기합니다.

        Raises:
            ConnectionError: 연결되지 않은 경우
            RuntimeError: 부팅 완료 타임아웃
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        try:
            await self._wait_for_boot_complete()
        except Exception as e:
            logger.error(f"MCU boot complete wait failed: {e}")
            raise RuntimeError(f"MCU boot complete timeout: {e}")

    async def set_fan_speed(self, speed_percent: float) -> bool:
        """
        팬 속도 설정

        Args:
            speed_percent: 팬 속도 (0-100%)

        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        if not (0 <= speed_percent <= 100):
            raise ValueError(f"Fan speed must be 0-100%, got {speed_percent}%")

        try:
            # Convert percentage to LMA fan speed level (1-10)
            fan_level = max(1, min(10, int((speed_percent / 100.0) * 10) + 1))
            validate_fan_speed(fan_level, FAN_SPEED_MIN, FAN_SPEED_MAX)

            # Send fan speed command and wait for confirmation
            fan_data = struct.pack("<B", fan_level)
            await self._send_and_wait_for(CMD_SET_FAN_SPEED, fan_data, STATUS_FAN_SPEED_OK)

            self._current_fan_speed = speed_percent
            logger.info(f"LMA fan speed set to {speed_percent}% (level {fan_level})")
            return True

        except (LMAError, ValueError) as e:
            logger.error(f"Failed to set LMA fan speed: {e}")
            return False

    async def get_fan_speed(self) -> float:
        """
        현재 팬 속도 조회

        Returns:
            현재 팬 속도 (0-100%)
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        return self._current_fan_speed

    async def set_upper_temperature(self, upper_temp: float) -> bool:
        """
        상한 온도 설정

        Args:
            upper_temp: 상한 온도 (°C)

        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        validate_temperature(upper_temp, MIN_TEMPERATURE, MAX_TEMPERATURE)

        try:
            # Send upper temperature command and wait for confirmation
            await self._send_and_wait_for(
                CMD_SET_UPPER_TEMP, self._encode_temperature(upper_temp), STATUS_UPPER_TEMP_OK
            )

            logger.info(f"LMA upper temperature set to {upper_temp}°C")
            return True

        except LMAError as e:
            logger.error(f"Failed to set LMA upper temperature: {e}")
            return False

    async def start_standby_heating(self) -> bool:
        """
        대기 가열 시작

        Returns:
            시작 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        try:
            # Initialize LMA for heating and wait for confirmation
            await self._send_and_wait_for(CMD_LMA_INIT, b"", STATUS_LMA_INIT_OK)
            self._mcu_status = MCUStatus.HEATING

            logger.info("LMA standby heating started")
            return True

        except LMAError as e:
            logger.error(f"Failed to start LMA standby heating: {e}")
            return False

    async def start_standby_cooling(self) -> bool:
        """
        대기 냉각 시작

        Returns:
            시작 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        try:
            # Set cooling temperature (lower than current) and wait for confirmation
            cooling_temp = max(MIN_TEMPERATURE, self._current_temperature - 10.0)
            await self._send_and_wait_for(
                CMD_SET_COOLING_TEMP, self._encode_temperature(cooling_temp), STATUS_COOLING_TEMP_OK
            )
            self._mcu_status = MCUStatus.COOLING

            logger.info(f"LMA standby cooling started to {cooling_temp}°C")
            return True

        except LMAError as e:
            logger.error(f"Failed to start LMA standby cooling: {e}")
            return False

    async def stop_temperature_control(self) -> bool:
        """
        온도 제어 중지

        Returns:
            중지 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("LMA MCU is not connected")

        try:
            # Set temperature to current temperature (stop heating/cooling) and wait for confirmation
            await self._send_and_wait_for(
                CMD_SET_OPERATING_TEMP,
                self._encode_temperature(self._current_temperature),
                STATUS_OPERATING_TEMP_OK,
            )
            self._mcu_status = MCUStatus.IDLE

            logger.info("LMA temperature control stopped")
            return True

        except LMAError as e:
            logger.error(f"Failed to stop LMA temperature control: {e}")
            return False

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
                "Boot complete timeout", error_code=int(LMAErrorCode.HARDWARE_INITIALIZATION_FAILED)
            )

        except Exception as e:
            raise LMAHardwareError(f"Boot wait failed: {e}")

    async def _send_command(self, command: int, data: bytes = b"") -> None:
        """Send command to LMA MCU (전송만)"""
        if not self._connection:
            raise LMACommunicationError("No connection available")

        try:
            # Build frame: STX + CMD + LEN + DATA + ETX
            frame = STX + struct.pack("B", command) + struct.pack("B", len(data)) + data + ETX

            # Send frame
            await self._connection.write(frame)

            logger.debug(f"LMA command 0x{command:02X} sent")

        except Exception as e:
            raise LMACommunicationError(f"Command send failed: {e}")

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
                else:
                    # 원하지 않는 응답은 로그 남기고 버림
                    if response:
                        logger.debug(
                            f"Discarding unwanted response: status=0x{response['status']:02X}, "
                            f"message='{response['message']}' (waiting for 0x{target_status:02X})"
                        )
                    else:
                        logger.debug(
                            f"Received None response (attempt {attempt + 1}/{max_attempts})"
                        )

            except Exception as e:
                logger.debug(f"Response receive error (attempt {attempt + 1}/{max_attempts}): {e}")

        raise LMACommunicationError(
            f"Target response 0x{target_status:02X} not received after {max_attempts} attempts"
        )

    async def _send_and_wait_for(
        self, command: int, data: bytes, target_status: int
    ) -> Dict[str, Any]:
        """
        명령 전송 + 특정 응답 대기

        Args:
            command: 명령 코드
            data: 데이터
            target_status: 기다릴 응답 상태 코드

        Returns:
            타겟 응답 딕셔너리
        """
        await self._send_command(command, data)
        return await self._wait_for_response(target_status)

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
            header = await self._connection.read(FRAME_CMD_SIZE + FRAME_LEN_SIZE, response_timeout)
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
                "message": STATUS_MESSAGES.get(status, f"Unknown status: 0x{status:02X}"),
            }

        except Exception as e:
            raise LMACommunicationError(f"Response receive failed: {e}")

    def _encode_temperature(self, temperature: float) -> bytes:
        """Encode temperature for LMA protocol"""
        temp_int = int(temperature * TEMP_SCALE_FACTOR)
        return struct.pack("<h", temp_int)  # signed short, little endian

    def _decode_temperature(self, data: bytes) -> float:
        """Decode temperature from LMA protocol"""
        if len(data) >= 2:
            temp_int = struct.unpack("<h", data[:2])[0]
            return temp_int / TEMP_SCALE_FACTOR
        return 0.0
