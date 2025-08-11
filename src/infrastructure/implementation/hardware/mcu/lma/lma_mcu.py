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
    CMD_SET_FAN_SPEED,
    CMD_SET_OPERATING_TEMP,
    CMD_SET_UPPER_TEMP,
    CMD_STROKE_INIT_COMPLETE,
    COMMAND_MESSAGES,
    ETX,
    FRAME_CMD_SIZE,
    FRAME_ETX_SIZE,
    FRAME_LEN_SIZE,
    MAX_DATA_SIZE,
    STATUS_BOOT_COMPLETE,
    STATUS_FAN_SPEED_OK,
    STATUS_LMA_INIT_OK,
    STATUS_MESSAGES,
    STATUS_OPERATING_TEMP_OK,
    STATUS_OPERATING_TEMP_REACHED,
    STATUS_STANDBY_TEMP_REACHED,
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

        # No default operational parameters - all values must be provided explicitly

        # State initialization
        self._connection: Optional[SerialConnection] = None
        self._is_connected = False
        self._current_temperature: float = 0.0
        self._target_temperature: float = 0.0
        self._current_test_mode: TestMode = TestMode.MODE_1
        self._current_fan_speed: float = 0.0
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
            if hasattr(self._connection, "flush_input_buffer"):
                flushed = await self._connection.flush_input_buffer()
                logger.debug(
                    f"Connection buffer flush: {'success' if flushed else 'not available'}"
                )
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

    async def set_temperature(self, target_temp: float) -> None:
        """
        목표 온도 설정

        Args:
            target_temp: 목표 온도 (°C)

        Raises:
            HardwareOperationError: If temperature setting fails
        """
        await self._ensure_connected()

        try:
            # Send operating temperature command and wait for confirmation
            await self._send_and_wait_for(
                CMD_SET_OPERATING_TEMP,
                self._encode_temperature(target_temp),
                STATUS_OPERATING_TEMP_OK,
            )
            self._target_temperature = target_temp

            logger.info(f"LMA target temperature set to {target_temp}°C")

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
            max_temp, ambient_temp = self._decode_temperature(temp_data_bytes)

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

    async def set_fan_speed(self, fan_level: int) -> None:
        """
        팬 속도 설정

        Args:
            fan_level: 팬 레벨 (1-10)

        Raises:
            HardwareOperationError: If fan speed setting fails
        """
        await self._ensure_connected()

        try:
            # Send fan speed command and wait for confirmation
            fan_data = struct.pack(">I", fan_level)
            await self._send_and_wait_for(
                CMD_SET_FAN_SPEED,
                fan_data,
                STATUS_FAN_SPEED_OK,
            )

            self._current_fan_speed = float(fan_level)
            logger.info(f"LMA fan speed set to level {fan_level}")

        except (LMAError, ValueError) as e:
            error_msg = f"Failed to set LMA fan speed: {e}"
            logger.error(error_msg)

            raise HardwareOperationError(
                "lma_mcu",
                "set_fan_speed",
                error_msg,
            ) from e

    async def get_fan_speed(self) -> int:
        """
        현재 팬 속도 조회

        Returns:
            현재 팬 레벨 (1-10)
        """
        return int(self._current_fan_speed)

    async def set_upper_temperature(self, upper_temp: float) -> None:
        """
        상한 온도 설정

        Args:
            upper_temp: 상한 온도 (°C)

        Raises:
            HardwareOperationError: If upper temperature setting fails
        """
        await self._ensure_connected()

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

            # LMA 초기화 명령 전송 및 순차적 응답 대기 (2개의 ACK 패킷)
            logger.debug("Sending CMD_LMA_INIT with sequential response handling")
            await self._send_and_wait_for_sequence(
                CMD_LMA_INIT,
                data,
                [STATUS_LMA_INIT_OK, STATUS_OPERATING_TEMP_REACHED],
            )
            logger.info("LMA initialization sequence completed - both ACK packets received")
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
            # Send cooling command with no data and sequential response handling (2개의 ACK 패킷)
            logger.debug("Sending CMD_STROKE_INIT_COMPLETE with sequential response handling")
            await self._send_and_wait_for_sequence(
                CMD_STROKE_INIT_COMPLETE,
                b"",
                [STATUS_STROKE_INIT_OK, STATUS_STANDBY_TEMP_REACHED],
            )
            logger.info("LMA cooling sequence completed - both ACK packets received")
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
            if fast_mode and hasattr(self._connection, "flush_input_buffer"):
                if await self._connection.flush_input_buffer():
                    logger.debug("Buffer cleared using native flush (fast mode)")
                    return
                else:
                    logger.debug("Native flush failed, falling back to read method")

            # Step 2: Fallback to read-and-discard method
            discarded_bytes = 0
            noise_data = bytearray()
            timeout = 0.01 if fast_mode else 0.1  # Much shorter timeout for fast mode
            max_attempts = 5 if fast_mode else 20  # Fewer attempts for fast mode
            attempts = 0

            while attempts < max_attempts:
                try:
                    data = await self._connection.read(1, timeout)
                    if not data:
                        break
                    discarded_bytes += len(data)
                    noise_data.extend(data)
                    attempts += 1
                except asyncio.TimeoutError:
                    break

            if discarded_bytes > 0:
                mode_str = "fast" if fast_mode else "thorough"
                logger.debug(
                    f"🔧 NOISE: Cleared {discarded_bytes} bytes from buffer [{noise_data.hex().upper()}] ({mode_str} mode)"
                )
            elif not fast_mode:
                logger.debug("No data found in serial buffer during thorough clear")

        except Exception as e:
            logger.debug(f"Error clearing serial buffer: {e}")

    async def _find_stx_in_stream(
        self, timeout: float = 60.0, max_search_bytes: int = 1024
    ) -> bool:
        """
        Find STX pattern in incoming data stream for normal packet reception

        This function searches byte-by-byte for STX pattern, handling noise automatically.
        When STX is found, the stream position is left at the byte immediately after STX.

        Args:
            timeout: Maximum time to search for STX
            max_search_bytes: Maximum bytes to search through

        Returns:
            True if STX found (stream positioned after STX), False if not found
        """
        if not self._connection:
            raise LMACommunicationError("No connection available")

        start_time = asyncio.get_event_loop().time()
        bytes_searched = 0
        noise_buffer = bytearray()
        waiting_for_second_ff = False

        try:
            while (
                asyncio.get_event_loop().time() - start_time < timeout
                and bytes_searched < max_search_bytes
            ):
                try:
                    # Read one byte at a time with appropriate timeout for MCU communication
                    byte_data = await self._connection.read(1, timeout)
                    if not byte_data:
                        continue

                    bytes_searched += 1
                    current_byte = byte_data[0]

                    # Periodic progress update (every 200 bytes, avoid log spam)
                    if bytes_searched % 200 == 0:
                        logger.debug(
                            f"MCU search progress: {bytes_searched} bytes processed, {len(noise_buffer)} noise bytes"
                        )

                    # Simple state machine for STX detection
                    if current_byte == 0xFF:
                        if waiting_for_second_ff:
                            # Found second FF - STX complete!
                            logger.debug(
                                f"STX pattern found in stream at position {bytes_searched}"
                            )
                            # Log some context bytes before STX for analysis
                            if len(noise_buffer) > 0:
                                recent_bytes = (
                                    noise_buffer[-10:] if len(noise_buffer) >= 10 else noise_buffer
                                )
                                logger.debug(
                                    f"Bytes before STX: {bytes(recent_bytes).hex().upper()}"
                                )
                            return True
                        else:
                            # Found first FF - wait for second
                            waiting_for_second_ff = True
                    else:
                        # Not FF - handle as noise with reduced logging
                        if waiting_for_second_ff:
                            # Previous FF was not part of STX - add to noise buffer
                            noise_buffer.append(0xFF)
                            waiting_for_second_ff = False

                        # Current byte is also noise - add to buffer
                        noise_buffer.append(current_byte)

                        # Heavy noise detection (no logging - just count)

                except asyncio.TimeoutError:
                    # Don't spam logs with timeout errors - MCU may be slow during boot
                    if bytes_searched == 0:
                        logger.debug("Waiting for MCU response...")
                    continue

            # Timeout or max bytes reached
            logger.debug(f"STX search timeout - no data received in {timeout}s")

            return False

        except Exception as e:
            logger.error(f"Error during STX stream search: {e}")
            return False

    async def _find_stx_sync(self, max_search_bytes: int = 1024, timeout: float = 60.0) -> bool:
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
            while (
                asyncio.get_event_loop().time() - start_time
            ) < timeout and bytes_searched < max_search_bytes:
                # Read one byte at a time
                try:
                    byte_data = await self._connection.read(1, timeout)
                    if not byte_data:
                        continue

                    bytes_searched += 1
                    noise_bytes.extend(byte_data)

                    # Check if we have potential STX pattern
                    if len(noise_bytes) >= 2:
                        # Check last 2 bytes for STX pattern
                        if noise_bytes[-2:] == STX:
                            # Found STX!
                            logger.debug("STX sync recovery successful")
                            return True

                        # Keep only last byte to check for split STX
                        if len(noise_bytes) > 2:
                            noise_bytes = noise_bytes[-1:]

                except asyncio.TimeoutError:
                    # Reduce timeout error spam during sync recovery
                    continue

            # Timeout or max bytes reached
            logger.debug(f"STX sync failed - no data received in {timeout}s")

            return False

        except Exception as e:
            logger.error(f"Error during STX sync search: {e}")
            return False

    async def _validate_complete_packet_structure(self, timeout: float) -> Optional[Dict[str, Any]]:
        """
        Validate complete LMA packet structure after finding STX candidate

        Args:
            timeout: Timeout for reading packet components

        Returns:
            Dictionary with packet data if valid, None if invalid
        """
        try:
            # Read STATUS and LEN (header)
            header = await self._connection.read(FRAME_CMD_SIZE + FRAME_LEN_SIZE, timeout)
            if len(header) < 2:
                logger.debug("Invalid header length in packet validation")
                return None

            status = header[0]
            data_len = header[1]

            # Validate STATUS field (must be 0x00-0x0E for LMA)
            if not (0 <= status <= 0x0E):
                logger.debug(f"Invalid STATUS in packet validation: 0x{status:02X}")
                return None

            # Validate data length (must be 0-12 for LMA)
            if not (0 <= data_len <= MAX_DATA_SIZE):
                logger.debug(f"Invalid data length in packet validation: {data_len}")
                return None

            # Read data payload if present
            data = b""
            if data_len > 0:
                data = await self._connection.read(data_len, timeout)
                if len(data) != data_len:
                    logger.debug(
                        f"Data length mismatch in packet validation: expected {data_len}, got {len(data)}"
                    )
                    return None

            # Read and validate ETX
            etx_data = await self._connection.read(FRAME_ETX_SIZE, timeout)
            if len(etx_data) != FRAME_ETX_SIZE or etx_data != ETX:
                logger.debug(f"Invalid ETX in packet validation: {etx_data.hex().upper()}")
                return None

            # Complete valid packet found!
            logger.debug(f"Valid packet found: STATUS=0x{status:02X}, LEN={data_len}")
            return {
                "status": status,
                "data": data,
                "message": STATUS_MESSAGES.get(status, f"Unknown status: 0x{status:02X}"),
            }

        except asyncio.TimeoutError:
            logger.debug("Timeout during packet validation")
            return None
        except Exception as e:
            logger.debug(f"Error during packet validation: {e}")
            return None

    async def _find_and_validate_complete_packet(self, timeout: float) -> Optional[Dict[str, Any]]:
        """
        Find and validate complete LMA packet with robust STX synchronization

        This method searches for STX patterns and validates the entire packet structure
        to prevent false STX detection in noisy environments.

        Args:
            timeout: Total timeout for finding valid packet

        Returns:
            Dictionary with packet data if valid packet found, None otherwise
        """
        if not self._connection:
            raise LMACommunicationError("No connection available")

        start_time = asyncio.get_event_loop().time()
        stx_candidates_checked = 0

        logger.debug(f"Searching for complete valid LMA packet (timeout: {timeout}s)")

        try:
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                # Step 1: Find STX candidate
                if not await self._find_stx_in_stream(timeout=min(timeout / 4, 15.0)):
                    logger.debug("No STX candidate found")
                    continue

                stx_candidates_checked += 1
                logger.debug(
                    f"STX candidate #{stx_candidates_checked} found, validating packet structure..."
                )

                # Step 2: Validate complete packet structure
                remaining_timeout = timeout - (asyncio.get_event_loop().time() - start_time)
                packet_data = await self._validate_complete_packet_structure(
                    timeout=min(remaining_timeout, 5.0)
                )

                if packet_data is not None:
                    # Complete valid packet found!
                    logger.debug(
                        f"Valid packet found after checking {stx_candidates_checked} STX candidates"
                    )
                    return packet_data
                else:
                    # Invalid packet, continue searching for next STX
                    logger.debug(
                        f"STX candidate #{stx_candidates_checked} failed validation, continuing search..."
                    )
                    continue

            # Timeout reached without finding valid packet
            logger.debug(
                f"Packet search timeout after checking {stx_candidates_checked} STX candidates"
            )
            return None

        except Exception as e:
            logger.error(f"Error during complete packet search: {e}")
            return None

    async def _wait_for_boot_complete(self) -> None:
        """Wait for MCU boot complete message"""
        try:
            logger.info("Waiting for MCU boot complete signal...")

            # Wait for boot complete status with improved error handling
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < BOOT_COMPLETE_TIMEOUT:
                try:
                    response = await self._receive_response(timeout=self._timeout)
                    if response and response.get("status") == STATUS_BOOT_COMPLETE:
                        logger.info("LMA MCU boot complete signal received")
                        return
                    elif response:
                        # Log received response for debugging
                        logger.debug(
                            f"Received non-boot response: status=0x{response.get('status', 0):02X}"
                        )
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

    async def _wait_for_response(self, target_status: int) -> Dict[str, Any]:
        """
        특정 응답 상태를 기다림 (단순화된 버전)

        Args:
            target_status: 기다릴 응답 상태 코드

        Returns:
            타겟 응답 딕셔너리

        Raises:
            LMACommunicationError: 타겟 응답을 받지 못한 경우
        """
        response = await self._receive_response(timeout=self._timeout)

        if response and response["status"] == target_status:
            logger.debug(
                f"Got target response: status=0x{response['status']:02X}, "
                f"message='{response['message']}'"
            )
            return response

        # 원하지 않는 응답 처리
        if response:
            raise LMACommunicationError(
                f"Unexpected response: status=0x{response['status']:02X}, "
                f"expected 0x{target_status:02X} ({response['message']})"
            )
        else:
            raise LMACommunicationError(f"No response received (expected 0x{target_status:02X})")

    async def _send_and_wait_for(
        self, command: int, data: bytes, target_status: int
    ) -> Dict[str, Any]:
        """
        명령 전송 + 특정 응답 대기 (타임아웃 보호 + 자동 재시도)

        Args:
            command: 명령 코드
            data: 데이터
            target_status: 기다릴 응답 상태 코드

        Returns:
            타겟 응답 딕셔너리

        Raises:
            TimeoutError: 응답 타임아웃 (재시도 후에도 실패)
        """
        max_retries = 3

        for retry_count in range(max_retries):
            try:
                logger.debug(f"🔄 Attempt {retry_count + 1}/{max_retries} for command 0x{command:02X} (timeout: {self._timeout}s)")
                await self._send_command(command, data)

                # Add timeout protection to prevent hanging
                return await asyncio.wait_for(
                    self._wait_for_response(target_status),
                    timeout=self._timeout,
                )

            except (asyncio.TimeoutError, LMACommunicationError) as e:
                error_msg = str(e)
                # Debug logging for exception analysis
                logger.error(f"🚨 Exception in attempt {retry_count + 1}/{max_retries} for command 0x{command:02X}: {type(e).__name__}: {error_msg}")
                
                # Check for any timeout-related error (including asyncio.TimeoutError and STX timeouts)
                is_timeout_error = (
                    isinstance(e, asyncio.TimeoutError)
                    or "timeout" in error_msg.lower()
                    or "Read timeout" in error_msg
                    or "STX" in error_msg
                )
                
                logger.debug(f"🔍 Timeout check: isinstance(asyncio.TimeoutError)={isinstance(e, asyncio.TimeoutError)}, error_msg='{error_msg}', is_timeout_error={is_timeout_error}")

                if is_timeout_error and retry_count < max_retries - 1:
                    logger.warning(
                        f"🔄 Communication timeout (retry {retry_count + 1}/{max_retries}) "
                        f"for command 0x{command:02X}, clearing buffer and retrying..."
                    )

                    # Clear serial buffer to remove potential noise
                    await self._clear_serial_buffer(fast_mode=True)
                    await asyncio.sleep(0.1)  # Short delay before retry
                    continue
                else:
                    # Final attempt failed or non-STX error
                    if retry_count == max_retries - 1:
                        logger.error(
                            f"Command 0x{command:02X} failed after {max_retries} retries: {error_msg}"
                        )
                    else:
                        logger.error(
                            f"Non-recoverable error for command 0x{command:02X}: {error_msg}"
                        )

                    if isinstance(e, asyncio.TimeoutError):
                        raise TimeoutError(
                            f"Operation timed out waiting for response 0x{target_status:02X} after {max_retries} retries"
                        ) from e
                    else:
                        raise e

            except Exception as e:
                # Unexpected error - don't retry
                logger.error(f"Unexpected error for command 0x{command:02X}: {e}")
                raise e

        # Should never reach here due to the loop logic, but just in case
        raise TimeoutError(
            f"Operation failed after {max_retries} retries for command 0x{command:02X}"
        )

    async def _send_and_wait_for_sequence(
        self, command: int, data: bytes, expected_statuses: list[int]
    ) -> Dict[str, Any]:
        """
        명령 전송 + 순차적 응답 대기 (다중 ACK 패킷 처리 + 자동 재시도)

        Args:
            command: 명령 코드
            data: 데이터
            expected_statuses: 기다릴 응답 상태 코드 리스트 (순서대로)

        Returns:
            마지막 응답 딕셔너리

        Raises:
            TimeoutError: 응답 타임아웃 (재시도 후에도 실패)
            LMACommunicationError: 예상하지 못한 응답
        """
        max_retries = 3

        for retry_count in range(max_retries):
            try:
                logger.debug(f"🔄 Sequence attempt {retry_count + 1}/{max_retries} for command 0x{command:02X} (timeout: {self._timeout}s)")
                await self._send_command(command, data)

                # Add timeout protection for entire sequence
                last_response = None
                for i, expected_status in enumerate(expected_statuses):
                    logger.debug(
                        f"Waiting for response {i+1}/{len(expected_statuses)}: 0x{expected_status:02X}"
                    )

                    response = await asyncio.wait_for(
                        self._wait_for_response(expected_status),
                        timeout=self._timeout,
                    )

                    if i == len(expected_statuses) - 1:
                        # This is the final response
                        last_response = response
                        logger.debug(f"Final response received: 0x{expected_status:02X}")
                    else:
                        # This is an intermediate response
                        logger.debug(f"Intermediate response received: 0x{expected_status:02X}")

                if last_response is None:
                    raise LMACommunicationError("No responses received in sequence")

                return last_response

            except (asyncio.TimeoutError, LMACommunicationError) as e:
                error_msg = str(e)
                # Debug logging for exception analysis
                logger.error(f"🚨 Sequence exception in attempt {retry_count + 1}/{max_retries} for command 0x{command:02X}: {type(e).__name__}: {error_msg}")
                
                # Check for any timeout-related error (including asyncio.TimeoutError and STX timeouts)
                is_timeout_error = (
                    isinstance(e, asyncio.TimeoutError)
                    or "timeout" in error_msg.lower()
                    or "Read timeout" in error_msg
                    or "STX" in error_msg
                )
                
                logger.debug(f"🔍 Sequence timeout check: isinstance(asyncio.TimeoutError)={isinstance(e, asyncio.TimeoutError)}, error_msg='{error_msg}', is_timeout_error={is_timeout_error}")

                if is_timeout_error and retry_count < max_retries - 1:
                    logger.warning(
                        f"🔄 Communication timeout in sequence (retry {retry_count + 1}/{max_retries}) "
                        f"for command 0x{command:02X}, clearing buffer and retrying..."
                    )

                    # Clear serial buffer to remove potential noise
                    await self._clear_serial_buffer(fast_mode=True)
                    await asyncio.sleep(0.1)  # Short delay before retry
                    continue
                else:
                    # Final attempt failed or non-STX error
                    if retry_count == max_retries - 1:
                        logger.error(
                            f"Command sequence 0x{command:02X} failed after {max_retries} retries: {error_msg}"
                        )
                    else:
                        logger.error(
                            f"Non-recoverable error for command sequence 0x{command:02X}: {error_msg}"
                        )

                    if isinstance(e, asyncio.TimeoutError):
                        raise TimeoutError(
                            f"Operation timed out waiting for response sequence {[hex(s) for s in expected_statuses]} after {max_retries} retries"
                        ) from e
                    else:
                        raise e

            except Exception as e:
                # Unexpected error - don't retry
                logger.error(f"Unexpected error for command sequence 0x{command:02X}: {e}")
                raise e

        # Should never reach here due to the loop logic, but just in case
        raise TimeoutError(
            f"Operation failed after {max_retries} retries for command sequence 0x{command:02X}"
        )

    async def _receive_response(
        self, timeout: float, enable_sync: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Receive response from LMA MCU with robust packet validation

        Args:
            timeout: Response timeout in seconds (required)
            enable_sync: Whether to attempt STX synchronization on failure

        Returns:
            Dictionary containing status, data, and message, or None if failed
        """
        if not self._connection:
            raise LMACommunicationError("No connection available")

        try:
            # Use new complete packet validation method
            logger.debug(
                f"Receiving MCU response with complete packet validation (timeout: {timeout}s)"
            )

            packet_data = await self._find_and_validate_complete_packet(timeout)

            if packet_data is not None:
                # Log successful packet reception with details
                status = packet_data["status"]
                data = packet_data["data"]
                message = packet_data["message"]

                # Format hex display with spaces: STX STATUS LEN DATA ETX
                hex_parts = [STX.hex().upper(), f"{status:02X}", f"{len(data):02X}"]
                if data:
                    hex_parts.append(data.hex().upper())
                hex_parts.append(ETX.hex().upper())
                packet_hex = " ".join(hex_parts)

                # Parse data based on status type for enhanced logging
                parsed_info = ""
                if status == STATUS_TEMP_RESPONSE and len(data) >= 2:
                    max_temp, ambient_temp = self._decode_temperature(data)
                    if len(data) >= 8:
                        parsed_info = f": max {max_temp:.1f}°C, ambient {ambient_temp:.1f}°C"
                    else:
                        parsed_info = f": {max_temp:.1f}°C"

                logger.info(f"PC <- MCU: {packet_hex} ({message}{parsed_info})")
                return packet_data
            else:
                # No valid packet found within timeout
                raise LMACommunicationError(f"No valid packet received within {timeout}s")

        except LMACommunicationError as e:
            # Handle sync recovery if enabled
            if enable_sync and "No valid packet received" in str(e):
                logger.debug("Attempting STX sync recovery for robust packet detection...")
                if await self._find_stx_sync(timeout=timeout):
                    logger.info("STX sync recovery successful, retrying with validation")
                    return await self._receive_response(
                        timeout, enable_sync=False
                    )  # Avoid infinite recursion
                else:
                    logger.warning("STX sync recovery failed")

            logger.error(f"❌ PROTOCOL ERROR: {e}")
            raise e
        except Exception as e:
            logger.error(f"❌ COMMUNICATION ERROR: {e}")
            raise LMACommunicationError(f"Response receive failed: {e}") from e

    def _encode_temperature(self, temperature: float) -> bytes:
        """Encode temperature for LMA protocol"""
        temp_int = int(temperature * TEMP_SCALE_FACTOR)
        return struct.pack(">I", temp_int)  # 4-byte unsigned int, big endian

    def _decode_temperature(self, data: bytes) -> tuple[float, float]:
        """Decode temperature from LMA array sensor protocol

        Args:
            data: 8-byte data containing max temperature (4 bytes) + ambient temperature (4 bytes)

        Returns:
            Tuple of (max_temp, ambient_temp) from sensor readings
        """
        if len(data) >= 8:
            # Unpack two 4-byte big-endian integers
            max_raw, ambient_raw = struct.unpack(">II", data[:8])

            # Convert to temperature values (divide by scale factor)
            max_temp = float(max_raw) / TEMP_SCALE_FACTOR
            ambient_temp = float(ambient_raw) / TEMP_SCALE_FACTOR

            return (max_temp, ambient_temp)
        elif len(data) >= 4:
            # Fallback for single 4-byte temperature
            temp_int = struct.unpack(">I", data[:4])[0]
            temp = float(temp_int) / TEMP_SCALE_FACTOR
            return (temp, temp)  # Same value for both max and ambient

        return (0.0, 0.0)
