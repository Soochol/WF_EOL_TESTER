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
    COMMAND_MESSAGES,
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
    STATUS_LMA_INIT_OK,
    STATUS_STROKE_INIT_OK,
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

    def __init__(self):
        """
        초기화 (기본 LMA 설정 사용)
        """

        # Connection parameters (will be set during connect)
        self._port = ""
        self._baudrate = 0
        self._timeout = 0.0
        self._bytesize = 0
        self._stopbits = 0
        self._parity: Optional[str] = None

        # Default operational parameters
        self._temperature = 25.0
        self._fan_speed = 50.0
        self._max_temperature = 150.0
        self._min_temperature = -40.0
        self._max_fan_speed = 100.0

        # State initialization
        self._connection: Optional[SerialConnection] = None
        self._is_connected = False
        self._current_temperature: float = self._temperature
        self._target_temperature: float = self._temperature
        self._current_test_mode: TestMode = TestMode.MODE_1
        self._current_fan_speed: float = self._fan_speed
        self._mcu_status: MCUStatus = MCUStatus.IDLE

    async def connect(
        self,
        port: str,
        baudrate: int,
        timeout: float,
        bytesize: int,
        stopbits: int,
        parity: Optional[str],
    ) -> None:
        """
        하드웨어 연결

        Args:
            port: Serial port (e.g., "COM4")
            baudrate: Baud rate (e.g., 115200)
            timeout: Connection timeout in seconds
            bytesize: Data bits
            stopbits: Stop bits
            parity: Parity setting

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:

            # Store actual values being used
            self._port = port
            self._baudrate = baudrate
            self._timeout = timeout
            self._bytesize = bytesize
            self._stopbits = stopbits
            self._parity = parity

            logger.info(f"Connecting to LMA MCU at {port} (baudrate: {baudrate})")

            self._connection = await SerialManager.create_connection(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                bytesize=bytesize,
                stopbits=stopbits,
                parity=parity,
            )

            # Clear any noise or leftover data from previous connections (direct flush for fastest startup)
            if hasattr(self._connection, 'flush_input_buffer'):
                flushed = await self._connection.flush_input_buffer()
                logger.debug(f"Connection buffer flush: {'success' if flushed else 'not available'}")
            else:
                logger.debug("Native flush not available, skipping buffer clear on connection")

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

            logger.info(f"LMA target temperature set to {effective_temp}°C")

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
        Array 센서 온도 측정 (최고 온도 반환)

        Returns:
            최고 온도 (°C) - array 센서 픽셀 중 최고값
        """
        await self._ensure_connected()

        try:
            response = await self._send_and_wait_for(CMD_REQUEST_TEMP, b"", STATUS_TEMP_RESPONSE)
            temp_data_bytes = response.get("data", b"\x00\x00\x00\x00\x00\x00\x00\x00")
            max_temp, min_temp = self._decode_temperature(temp_data_bytes)
            
            # Store max temperature as current temperature
            self._current_temperature = max_temp
            
            return self._current_temperature

        except LMAError as e:
            logger.error(f"Failed to get LMA temperature: {e}")
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

            # Send test mode command and wait for confirmation (use big-endian for MCU protocol)
            mode_data = struct.pack(">I", lma_mode)
            await self._send_and_wait_for(
                CMD_ENTER_TEST_MODE,
                mode_data,
                STATUS_TEST_MODE_COMPLETE,
            )

            self._current_test_mode = mode
            logger.info(f"LMA test mode set to {mode}")

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
                timeout=BOOT_COMPLETE_TIMEOUT,  # Add extra buffer time
            )
        except asyncio.TimeoutError as e:
            logger.error("MCU boot complete wait timed out")
            raise RuntimeError("MCU boot complete timeout") from e
        except Exception as e:
            logger.error(f"MCU boot complete wait failed: {e}")
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
            logger.info(f"LMA fan speed set to {effective_speed}% (level {fan_level})")

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

            logger.info(f"LMA upper temperature set to {upper_temp}°C")

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

            # 12바이트 데이터 패킹: 동작온도(4B) + 대기온도(4B) + 유지시간(4B) (big-endian)
            data = struct.pack(
                ">III",
                op_temp_int,
                standby_temp_int,
                hold_time_ms,
            )

            # LMA 초기화 명령 전송 및 응답 대기
            await self._send_and_wait_for(
                CMD_LMA_INIT,
                data,
                STATUS_LMA_INIT_OK,
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
                STATUS_STROKE_INIT_OK,
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
            # Use cached temperature value instead of reading from hardware
            # Temperature can be explicitly updated via get_temperature() when needed
            status["last_error"] = None

        return status

    # Private helper methods

    async def _clear_serial_buffer(self, fast_mode: bool = True) -> None:
        """Clear serial buffer to remove noise and sync issues
        
        Args:
            fast_mode: If True, prefer native flush for speed. If False, use thorough read method.
        """
        if not self._connection:
            return
            
        try:
            # Step 1: Try native flush first (fastest method)
            if fast_mode and hasattr(self._connection, 'flush_input_buffer'):
                if await self._connection.flush_input_buffer():
                    logger.debug("Buffer cleared using native flush (fast mode)")
                    return
                else:
                    logger.debug("Native flush failed, falling back to read method")
            
            # Step 2: Fallback to read-and-discard method
            discarded_bytes = 0
            timeout = 0.01 if fast_mode else 0.1  # Much shorter timeout for fast mode
            max_attempts = 5 if fast_mode else 20  # Fewer attempts for fast mode
            attempts = 0
            
            while attempts < max_attempts:
                try:
                    data = await self._connection.read(1, timeout)
                    if not data:
                        break
                    discarded_bytes += len(data)
                    attempts += 1
                except asyncio.TimeoutError:
                    break
            
            if discarded_bytes > 0:
                mode_str = "fast" if fast_mode else "thorough"
                logger.debug(f"Cleared {discarded_bytes} bytes from serial buffer ({mode_str} mode)")
            elif not fast_mode:
                logger.debug("No data found in serial buffer during thorough clear")
                
        except Exception as e:
            logger.debug(f"Error clearing serial buffer: {e}")

    async def _find_stx_sync(self, max_search_bytes: int = 1024, timeout: float = 2.0) -> bool:
        """
        Search for STX pattern in incoming data stream to handle noise
        
        Args:
            max_search_bytes: Maximum number of bytes to search through
            timeout: Total timeout for STX search
            
        Returns:
            True if STX found and positioned, False if timeout or max bytes reached
        """
        if not self._connection:
            raise LMACommunicationError("No connection available")
        
        logger.debug("Searching for STX pattern to sync with MCU...")
        start_time = asyncio.get_event_loop().time()
        bytes_searched = 0
        noise_bytes = bytearray()
        
        try:
            while (asyncio.get_event_loop().time() - start_time) < timeout and bytes_searched < max_search_bytes:
                # Read one byte at a time
                try:
                    byte_data = await self._connection.read(1, 0.1)
                    if not byte_data:
                        continue
                        
                    bytes_searched += 1
                    noise_bytes.extend(byte_data)
                    
                    # Check if we have potential STX pattern
                    if len(noise_bytes) >= 2:
                        # Check last 2 bytes for STX pattern
                        if noise_bytes[-2:] == STX:
                            # Found STX! Log noise data if any
                            if len(noise_bytes) > 2:
                                noise_data = noise_bytes[:-2]
                                logger.debug(f"Found STX after {len(noise_data)} noise bytes: {noise_data.hex()}")
                            else:
                                logger.debug("Found STX at start of stream")
                            return True
                        
                        # Keep only last byte to check for split STX
                        if len(noise_bytes) > 2:
                            noise_bytes = noise_bytes[-1:]
                            
                except asyncio.TimeoutError:
                    continue
                    
            # Timeout or max bytes reached - use debug level to avoid noise spam
            if noise_bytes:
                logger.debug(f"STX sync failed after searching {bytes_searched} bytes")
            else:
                logger.debug(f"STX sync failed - no data received in {timeout}s")
                
            return False
            
        except Exception as e:
            logger.error(f"Error during STX sync search: {e}")
            return False

    async def _wait_for_boot_complete(self) -> None:
        """Wait for MCU boot complete message"""
        try:
            logger.info("Waiting for MCU boot complete signal...")
            
            # Wait for boot complete status with improved error handling
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < BOOT_COMPLETE_TIMEOUT:
                try:
                    response = await self._receive_response(timeout=1.0)
                    if response and response.get("status") == STATUS_BOOT_COMPLETE:
                        logger.info("LMA MCU boot complete signal received")
                        return
                    elif response:
                        # Log received response for debugging
                        logger.debug(f"Received non-boot response: status=0x{response.get('status', 0):02X}")
                except asyncio.TimeoutError:
                    # This is expected while waiting, just continue
                    logger.debug("Timeout waiting for boot complete, continuing...")
                    continue
                except Exception as e:
                    # Log but don't fail on individual response errors
                    logger.debug(f"Response error while waiting for boot complete: {e}")
                    continue

            # Timeout reached
            logger.warning(f"Boot complete timeout after {BOOT_COMPLETE_TIMEOUT} seconds")
            raise LMAHardwareError(
                "Boot complete timeout - MCU may not be sending boot complete signal",
                error_code=int(LMAErrorCode.HARDWARE_INITIALIZATION_FAILED),
            )

        except LMAHardwareError:
            # Re-raise LMA specific errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error during boot complete wait: {e}")
            raise LMAHardwareError(f"Boot wait failed: {e}") from e

    async def _send_command(self, command: int, data: bytes = b"") -> None:
        """Send command to LMA MCU (전송만)"""
        if not self._connection:
            raise LMACommunicationError("No connection available")

        try:
            # Build frame: STX + CMD + LEN + DATA + ETX
            frame = STX + struct.pack("B", command) + struct.pack("B", len(data)) + data + ETX

            # Format hex display with spaces: STX CMD LEN DATA ETX
            hex_parts = [STX.hex().upper(), f"{command:02X}", f"{len(data):02X}"]
            if data:
                hex_parts.append(data.hex().upper())
            hex_parts.append(ETX.hex().upper())
            packet_hex = " ".join(hex_parts)

            # Get command description
            cmd_name = COMMAND_MESSAGES.get(command, f"Unknown CMD 0x{command:02X}")
            
            # Send frame
            await self._connection.write(frame)

            logger.info(f"PC -> MCU: {packet_hex} ({cmd_name})")

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
                    logger.debug(
                        f"Received None response (attempt {attempt + 1}/{max_attempts})"
                    )

            except Exception as e:
                logger.debug(
                    f"Response receive error (attempt {attempt + 1}/{max_attempts}): {e}"
                )

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
            logger.error(f"Timeout waiting for response 0x{target_status:02X}")
            raise TimeoutError(
                f"Operation timed out waiting for response 0x{target_status:02X}"
            ) from e

    async def _receive_response(self, timeout: Optional[float] = None, enable_sync: bool = True) -> Optional[Dict[str, Any]]:
        """
        Receive response from LMA MCU with noise-resistant protocol handling
        
        Args:
            timeout: Response timeout in seconds
            enable_sync: Whether to attempt STX synchronization on failure
            
        Returns:
            Dictionary containing status, data, and message, or None if failed
        """
        if not self._connection:
            raise LMACommunicationError("No connection available")

        response_timeout = timeout or self._timeout
        sync_attempted = False

        while True:
            try:
                # Try direct STX read first (normal case)
                stx_data = await self._connection.read(FRAME_STX_SIZE, response_timeout)
                if not stx_data:
                    raise LMACommunicationError("No data received (empty response)")
                
                # Check for valid STX
                if stx_data == STX:
                    logger.debug("Valid STX received directly")
                else:
                    # Invalid STX - handle noise
                    logger.debug(f"Invalid STX received: {stx_data.hex()} (expected: {STX.hex()})")
                    
                    if enable_sync and not sync_attempted:
                        logger.debug("Attempting STX synchronization due to noise...")
                        sync_attempted = True
                        
                        # Clear buffer thoroughly for noise recovery
                        await self._clear_serial_buffer(fast_mode=False)
                        
                        # Search for STX pattern
                        if await self._find_stx_sync():
                            logger.debug("STX synchronization successful, continuing with packet reception")
                            # STX already found, break to read rest of packet
                            break
                        else:
                            raise LMACommunicationError("STX synchronization failed - no valid STX found")
                    else:
                        raise LMACommunicationError(f"Invalid STX: received {stx_data.hex()}, expected {STX.hex()}")

                # Read status and length (header)
                header = await self._connection.read(
                    FRAME_CMD_SIZE + FRAME_LEN_SIZE,
                    response_timeout,
                )
                if len(header) < 2:
                    raise LMACommunicationError(f"Incomplete header: received {len(header)} bytes, expected 2")
                    
                status = header[0]
                data_len = header[1]

                # Validate data length
                if data_len > 255:  # Reasonable maximum for LMA protocol
                    raise LMACommunicationError(f"Invalid data length: {data_len}")

                # Read data payload if present
                data = b""
                if data_len > 0:
                    data = await self._connection.read(data_len, response_timeout)
                    if len(data) != data_len:
                        raise LMACommunicationError(f"Incomplete data: received {len(data)} bytes, expected {data_len}")

                # Read ETX (end of frame)
                etx_data = await self._connection.read(FRAME_ETX_SIZE, response_timeout)
                if not etx_data:
                    raise LMACommunicationError("No ETX received")
                    
                if etx_data != ETX:
                    logger.debug(f"Invalid ETX received: {etx_data.hex()} (expected: {ETX.hex()})")
                    raise LMACommunicationError(f"Invalid ETX: received {etx_data.hex()}, expected {ETX.hex()}")

                # Successful packet reception - format hex display with spaces: STX STATUS LEN DATA ETX
                hex_parts = [STX.hex().upper(), f"{status:02X}", f"{data_len:02X}"]
                if data:
                    hex_parts.append(data.hex().upper())
                hex_parts.append(ETX.hex().upper())
                packet_hex = " ".join(hex_parts)

                # Get status description and parse data
                status_name = STATUS_MESSAGES.get(status, f"Unknown STATUS 0x{status:02X}")
                parsed_info = ""
                
                # Parse data based on status type
                if status == STATUS_TEMP_RESPONSE and len(data) >= 2:
                    max_temp, min_temp = self._decode_temperature(data)
                    if len(data) >= 8:
                        parsed_info = f": max {max_temp:.1f}°C, min {min_temp:.1f}°C"
                    else:
                        parsed_info = f": {max_temp:.1f}°C"
                elif status == STATUS_BOOT_COMPLETE:
                    parsed_info = ""
                elif status in [STATUS_TEST_MODE_COMPLETE, STATUS_OPERATING_TEMP_OK, STATUS_FAN_SPEED_OK]:
                    parsed_info = ""

                logger.info(f"MCU -> PC: {packet_hex} ({status_name}{parsed_info})")
                
                return {
                    "status": status,
                    "data": data,
                    "message": STATUS_MESSAGES.get(
                        status,
                        f"Unknown status: 0x{status:02X}",
                    ),
                }

            except LMACommunicationError as e:
                # If sync was already attempted or sync is disabled, re-raise
                if sync_attempted or not enable_sync:
                    raise e
                    
                # Otherwise, try sync once
                logger.debug(f"Communication error, will attempt sync: {e}")
                sync_attempted = True
                continue
                
            except asyncio.TimeoutError as e:
                raise LMACommunicationError(f"Response receive timeout after {response_timeout}s") from e
            except Exception as e:
                raise LMACommunicationError(f"Response receive failed: {e}") from e

    def _encode_temperature(self, temperature: float) -> bytes:
        """Encode temperature for LMA protocol"""
        temp_int = int(temperature * TEMP_SCALE_FACTOR)
        return struct.pack(">h", temp_int)  # signed short, big endian

    def _decode_temperature(self, data: bytes) -> tuple[float, float]:
        """Decode temperature from LMA array sensor protocol
        
        Args:
            data: 8-byte data containing max temperature (4 bytes) + min temperature (4 bytes)
            
        Returns:
            Tuple of (max_temp, min_temp) from array sensor pixels
        """
        if len(data) >= 8:
            # Unpack two 4-byte big-endian integers
            max_raw, min_raw = struct.unpack(">II", data[:8])
            
            # Convert to temperature values (divide by scale factor)
            max_temp = float(max_raw) / TEMP_SCALE_FACTOR
            min_temp = float(min_raw) / TEMP_SCALE_FACTOR
            
            return (max_temp, min_temp)
        elif len(data) >= 2:
            # Fallback for legacy 2-byte format (for compatibility)
            temp_int = struct.unpack(">h", data[:2])[0]
            temp = float(temp_int) / TEMP_SCALE_FACTOR
            return (temp, temp)  # Same value for both max and min
        
        return (0.0, 0.0)
