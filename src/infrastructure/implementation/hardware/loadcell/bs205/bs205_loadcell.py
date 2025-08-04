"""
BS205 LoadCell Service

Integrated service for BS205 LoadCell hardware control.
Combines adapter and controller functionality into a single service.
"""

import asyncio
from typing import Any, Dict, Optional

from loguru import logger

from application.interfaces.hardware.loadcell import (
    LoadCellService,
)
from domain.enums.measurement_units import MeasurementUnit
from domain.value_objects.measurements import ForceValue
from driver.serial.exceptions import (
    SerialCommunicationError,
    SerialConnectionError,
    SerialTimeoutError,
)
from driver.serial.serial import SerialConnection, SerialManager
from infrastructure.implementation.hardware.loadcell.bs205.constants import (
    CMD_HOLD,
    CMD_HOLD_RELEASE,
    CMD_READ_WEIGHT,
    CMD_ZERO,
    STATUS_MESSAGES,
    ZERO_OPERATION_DELAY,
)
from infrastructure.implementation.hardware.loadcell.bs205.error_codes import (
    BS205CommunicationError,
    BS205Error,
    BS205ErrorCode,
    BS205HardwareError,
    BS205OperationError,
    validate_weight_range,
)


class BS205LoadCell(LoadCellService):
    """BS205 로드셀 통합 서비스"""

    def __init__(self):
        """
        초기화
        """

        # Connection parameters (will be set during connect)
        self._port = ""
        self._baudrate = 0
        self._timeout = 0.0
        self._bytesize = 0
        self._stopbits = 0
        self._parity: Optional[str] = None
        self._indicator_id = 0

        # State initialization
        self._connection: Optional[SerialConnection] = None
        self._is_connected = False

        # Command rate limiting
        self._last_command_time = 0.0
        self._min_command_interval = 0.2  # 200ms minimum between commands
        self._command_lock = asyncio.Lock()

    async def connect(
        self,
        port: str,
        baudrate: int,
        timeout: float,
        bytesize: int,
        stopbits: int,
        parity: Optional[str],
        indicator_id: int
    ) -> None:
        """
        하드웨어 연결

        Args:
            port: Serial port (e.g., "COM3")
            baudrate: Baud rate (e.g., 9600)
            timeout: Connection timeout in seconds
            bytesize: Data bits
            stopbits: Stop bits
            parity: Parity setting
            indicator_id: Indicator device ID

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
            self._indicator_id = indicator_id

            # 사용 가능한 COM 포트 체크
            try:
                import serial.tools.list_ports

                available_ports = [port.device for port in serial.tools.list_ports.comports()]
                logger.info(f"Available COM ports: {available_ports}")
            except ImportError:
                logger.warning("Cannot check available ports - pyserial not fully installed")

            logger.info(
                f"Connecting to BS205 LoadCell - Port: {port}, Baud: {baudrate}, Timeout: {timeout}, "
                f"ByteSize: {bytesize}, StopBits: {stopbits}, Parity: {parity}, ID: {indicator_id}"
            )

            self._connection = await SerialManager.create_connection(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                bytesize=bytesize,
                stopbits=stopbits,
                parity=parity,
            )

            # Serial 연결 성공하면 바로 연결된 것으로 간주
            self._is_connected = True
            logger.info(STATUS_MESSAGES["connected"])

        except (SerialCommunicationError, SerialConnectionError, SerialTimeoutError) as e:
            error_msg = (
                f"Failed to connect to BS205 LoadCell: {e}\n"
                f"(Port: {self._port} @ {self._baudrate} baud)"
            )
            logger.error(
                f"BS205 LoadCell connection failed - Port: {self._port}, Baud: {self._baudrate}, Error: {e}"
            )
            self._is_connected = False
            raise BS205CommunicationError(
                error_msg,
                error_code=int(BS205ErrorCode.HARDWARE_INITIALIZATION_FAILED),
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
            logger.info(STATUS_MESSAGES["disconnected"])

        except Exception as e:
            logger.error(f"Error disconnecting BS205 LoadCell: {e}")
            from domain.exceptions.eol_exceptions import (
                HardwareOperationError,
            )

            raise HardwareOperationError(
                "bs205_loadcell",
                "disconnect",
                f"Disconnection failed: {e}",
            ) from e

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected and self._connection is not None

    async def read_force(self) -> ForceValue:
        """
        힘 측정값 읽기

        Returns:
            측정된 힘 값 (ForceValue)

        Raises:
            BS205HardwareError: 연결되지 않은 경우
            BS205OperationError: 측정 실패
            BS205CommunicationError: 통신 실패
        """
        if not await self.is_connected():
            raise BS205HardwareError(
                "BS205 LoadCell is not connected",
                error_code=int(BS205ErrorCode.HARDWARE_NOT_CONNECTED),
            )

        try:
            # BS205 바이너리 프로토콜 사용
            response = await self._send_bs205_command(CMD_READ_WEIGHT)

            if not response:
                raise BS205CommunicationError(
                    "No response from BS205 LoadCell",
                    error_code=int(BS205ErrorCode.COMM_TIMEOUT),
                )

            # 응답 파싱 및 검증 (BS205 형태: "0+_7.487")
            weight_value, unit = self._parse_bs205_weight(response)

            # 단위에 따른 처리
            if unit == "kg":
                # 무게 범위 검증
                validate_weight_range(weight_value)

                # kg을 kgf로 변환 (1kg = 1kgf 중력하에서)
                force_kgf = weight_value

                logger.debug(f"BS205 LoadCell reading: {weight_value}kg = {force_kgf:.3f}kgf")
                return ForceValue.from_raw_data(force_kgf, MeasurementUnit.KILOGRAM_FORCE)

            elif unit == "N":
                # 이미 Newton 단위인 경우
                logger.debug(f"BS205 LoadCell reading: {weight_value:.3f}N")
                return ForceValue.from_raw_data(weight_value, MeasurementUnit.NEWTON)

            else:
                # 지원하지 않는 단위
                raise BS205OperationError(
                    f"Unsupported unit '{unit}' from device",
                    error_code=int(BS205ErrorCode.OPERATION_INVALID_UNIT),
                )

        except BS205Error:
            raise  # Re-raise BS205 specific errors
        except (SerialCommunicationError, SerialConnectionError, SerialTimeoutError) as e:
            raise BS205CommunicationError(
                f"Communication error: {e}",
                error_code=int(BS205ErrorCode.COMM_SERIAL_ERROR),
            ) from e
        except Exception as e:
            raise BS205OperationError(
                f"Unexpected error reading force: {e}",
                error_code=int(BS205ErrorCode.OPERATION_TIMEOUT),
            ) from e


    async def hold(self) -> bool:
        """
        Hold 설정 - 현재 측정값을 고정

        BS205 프로토콜에서 ID + H 명령으로 현재 표시값을 고정합니다.
        응답이 없으므로 명령 전송 후 성공으로 간주합니다.

        Returns:
            Hold 설정 성공 여부

        Raises:
            BS205HardwareError: 연결되지 않은 경우
            BS205OperationError: Hold 설정 실패
        """
        if not await self.is_connected():
            raise BS205HardwareError(
                "BS205 LoadCell is not connected",
                error_code=int(BS205ErrorCode.HARDWARE_NOT_CONNECTED),
            )

        try:
            logger.info("Setting BS205 LoadCell hold")

            # Hold 명령 (바이너리 프로토콜) - 응답 없음
            await self._send_bs205_command(CMD_HOLD)

            logger.info(STATUS_MESSAGES["hold_set"])
            return True

        except (SerialCommunicationError, SerialConnectionError, SerialTimeoutError) as e:
            logger.error(STATUS_MESSAGES["hold_failed"])
            raise BS205OperationError(
                f"Failed to set BS205 LoadCell hold: {e}",
                error_code=int(BS205ErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def hold_release(self) -> bool:
        """
        Hold 해제 - 실시간 측정값 표시

        BS205 프로토콜에서 ID + L 명령으로 Hold를 해제하고 실시간 값을 표시합니다.
        응답이 없으므로 명령 전송 후 성공으로 간주합니다.

        Returns:
            Hold 해제 성공 여부

        Raises:
            BS205HardwareError: 연결되지 않은 경우
            BS205OperationError: Hold 해제 실패
        """
        if not await self.is_connected():
            raise BS205HardwareError(
                "BS205 LoadCell is not connected",
                error_code=int(BS205ErrorCode.HARDWARE_NOT_CONNECTED),
            )

        try:
            logger.info("Releasing BS205 LoadCell hold")

            # Hold 해제 명령 (바이너리 프로토콜) - 응답 없음
            await self._send_bs205_command(CMD_HOLD_RELEASE)

            logger.info(STATUS_MESSAGES["hold_released"])
            return True

        except (SerialCommunicationError, SerialConnectionError, SerialTimeoutError) as e:
            logger.error(STATUS_MESSAGES["hold_failed"])
            raise BS205OperationError(
                f"Failed to release BS205 LoadCell hold: {e}",
                error_code=int(BS205ErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def zero_calibration(self) -> None:
        """
        영점 조정

        Raises:
            HardwareOperationError: If calibration fails
        """
        from domain.exceptions.eol_exceptions import (
            HardwareOperationError,
        )

        if not await self.is_connected():
            raise HardwareOperationError(
                "bs205_loadcell",
                "zero_calibration",
                "BS205 LoadCell is not connected"
            )

        try:
            logger.info("Zeroing BS205 LoadCell")

            # 영점 조정 명령 (바이너리 프로토콜) - 응답 없음
            await self._send_bs205_command(CMD_ZERO)

            # 영점 조정 완료 대기 (더 긴 시간)
            await asyncio.sleep(ZERO_OPERATION_DELAY)

            # Zero 명령은 응답이 없으므로 성공으로 간주
            logger.info(STATUS_MESSAGES["zeroed"])

        except (SerialCommunicationError, SerialConnectionError, SerialTimeoutError) as e:
            logger.error(STATUS_MESSAGES["zero_failed"])
            raise HardwareOperationError(
                "bs205_loadcell",
                "zero_calibration",
                f"Failed to zero BS205 LoadCell: {e}",
            ) from e

    async def read_raw_value(self) -> float:
        """
        원시 측정값 읽기 (BS205는 force와 동일)

        Returns:
            Raw measurement value
        """
        force_value = await self.read_force()
        return force_value.value

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회
        """
        return {
            "connected": await self.is_connected(),
            "port": self._port,
            "baudrate": self._baudrate,
            "indicator_id": self._indicator_id,
            "hardware_type": "BS205",
        }

    async def _send_bs205_command(
        self, command: str, timeout: Optional[float] = None
    ) -> Optional[str]:
        """
        BS205 바이너리 프로토콜로 명령 전송

        Args:
            command: 명령어 ('R', 'Z', 'H', 'L')
            timeout: 응답 타임아웃

        Returns:
            파싱된 응답 문자열
        """
        if not self._connection:
            raise BS205CommunicationError(
                "No connection available",
                error_code=int(BS205ErrorCode.HARDWARE_NOT_CONNECTED),
            )

        # Command rate limiting to prevent interference
        async with self._command_lock:
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self._last_command_time

            if time_since_last < self._min_command_interval:
                wait_time = self._min_command_interval - time_since_last
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s before command")
                await asyncio.sleep(wait_time)

            try:
                cmd_timeout = timeout if timeout is not None else 3.0  # Increase default timeout

                # BS205 바이너리 명령어 생성: ID + Command
                # ID=0 → 30H, R → 52H
                id_byte = ord(str(self._indicator_id))  # '0' → 0x30
                cmd_byte = ord(command)  # 'R' → 0x52
                command_bytes = bytes([id_byte, cmd_byte])

                logger.debug(f"Sending BS205 command: {command}")

                # 바이너리 명령어 전송
                await self._connection.write(command_bytes)

                # Update last command time
                self._last_command_time = asyncio.get_event_loop().time()

                # Small delay to allow BS205 to prepare response
                await asyncio.sleep(0.15)  # Increased to 150ms delay

                # Hold, Hold Release, and Zero commands don't return responses
                if command in [CMD_HOLD, CMD_HOLD_RELEASE, CMD_ZERO]:
                    logger.debug(f"Command '{command}' sent - no response expected")
                    return "OK"  # Return success indicator

                # Read response for other commands
                response_buffer = await self._read_response(cmd_timeout)

                if not response_buffer:
                    logger.warning("No response data received from BS205")
                    return None

                # Parse the response
                ascii_response = self._parse_bs205_response(response_buffer)

                return ascii_response if ascii_response else None

            except Exception as e:
                logger.error(f"BS205 binary command '{command}' failed: {e}")
                raise BS205CommunicationError(
                    f"Command '{command}' failed: {e}",
                    error_code=int(BS205ErrorCode.COMM_SERIAL_ERROR),
                ) from e

    async def _read_response(self, timeout: float) -> bytes:
        """
        Read BS205 response with simple retry strategy

        Args:
            timeout: Total timeout for reading

        Returns:
            Response bytes or empty bytes if failed
        """
        try:
            # Try to read response data
            if not self._connection:
                raise BS205CommunicationError("No connection available")
            response = await self._connection.read(size=64, timeout=timeout)
            # If first read is incomplete, try one more time
            if response and len(response) < 10:  # Minimum expected frame size
                additional = await self._connection.read(size=32, timeout=0.5)
                if additional:
                    response += additional

            return response

        except Exception as e:
            logger.error(f"Error reading response: {e}")
            return b""

    def _extract_frame_data(self, response_bytes: bytes) -> bytes:
        """
        Extract data portion from BS205 response frame
        """
        try:
            # Look for STX/ETX framing
            stx_pos = response_bytes.find(0x02)
            if stx_pos != -1:
                etx_pos = response_bytes.find(0x03, stx_pos)
                if etx_pos != -1:
                    return response_bytes[stx_pos + 1 : etx_pos]
                else:
                    return response_bytes[stx_pos + 1 :]

            # No framing, return as-is
            return response_bytes

        except Exception as e:
            logger.error(f"Error extracting frame data: {e}")
            return b""

    def _parse_bs205_response(self, response_bytes: bytes) -> str:
        """
        BS205 바이너리 응답을 ASCII 문자열로 파싱
        """
        try:
            if len(response_bytes) < 5:
                return ""

            data_bytes = self._extract_frame_data(response_bytes)
            if not data_bytes:
                return ""

            # ASCII로 변환 (공백을 _로 표시)
            ascii_data = ""
            for byte_val in data_bytes:
                if 0x20 <= byte_val <= 0x7E:
                    if byte_val == 0x20:
                        ascii_data += "_"
                    else:
                        ascii_data += chr(byte_val)
                else:
                    ascii_data += f"[{byte_val:02X}]"

            return ascii_data

        except Exception:
            return ""

    def _parse_bs205_weight(self, response: str) -> tuple[float, str]:
        """
        BS205 가중치 응답 파싱

        응답 형태: "ID + 부호 + 값" (문서 기준)
        예: "0+_7.487", "0-12.34", "15+1.7486"

        실제 프로토콜 문서 예시:
        - "1+_7.487" (ID=1, +7.487kg)
        - "1+_ _7487" (ID=1, +7.487kg, 소수점 없음)
        - "15+1.7486" (ID=15, +1.7486kg)

        Args:
            response: BS205 응답 문자열

        Returns:
            (weight_value, unit) 튜플
        """
        try:
            if not response or len(response) < 3:
                raise BS205CommunicationError(
                    f"Invalid BS205 response: '{response}'",
                    error_code=int(BS205ErrorCode.DATA_INVALID_FORMAT),
                )

            logger.debug(f"Parsing BS205 weight response: '{response}'")

            # ID 부분과 데이터 부분 분리
            sign_pos = -1
            for i, char in enumerate(response):
                if char in ["+", "-"]:
                    sign_pos = i
                    break

            if sign_pos == -1:
                raise BS205CommunicationError(
                    f"Cannot find sign (+/-) in BS205 response: '{response}'",
                    error_code=int(BS205ErrorCode.DATA_PARSING_ERROR),
                )

            # 부호와 값 추출
            sign = response[sign_pos]
            value_part = response[sign_pos + 1 :]

            # 값 정리: 언더스코어(_)를 공백으로 변환, 연속 공백 정리
            value_clean = value_part.replace("_", " ").strip()
            # 연속된 공백을 하나로 정리
            import re

            value_clean = re.sub(r"\s+", " ", value_clean)
            # 최종적으로 공백 제거하여 숫자만 추출
            value_clean = value_clean.replace(" ", "")

            # 빈 정수 부분 처리 (예: ".487" → "0.487")
            if value_clean.startswith("."):
                value_clean = "0" + value_clean

            # float 변환
            try:
                weight_value = float(value_clean)
            except ValueError:
                # 마지막 시도: 숫자만 추출
                import re

                numbers = re.findall(r"\d+\.?\d*", value_clean)
                if numbers:
                    weight_value = float(numbers[0])
                else:
                    raise ValueError(f"No valid number found in '{value_clean}'")

            # 부호 적용
            if sign == "-":
                weight_value = -weight_value

            logger.info(f"Successfully parsed BS205 weight: '{response}' → {weight_value} kg")

            # BS205는 kg 단위 사용 (문서 확인)
            return weight_value, "kg"

        except ValueError as e:
            raise BS205CommunicationError(
                f"Cannot convert BS205 weight value: '{response}' → {str(e)}",
                error_code=int(BS205ErrorCode.DATA_CONVERSION_ERROR),
            ) from e
        except Exception as e:
            raise BS205CommunicationError(
                f"Failed to parse BS205 weight: '{response}', error: {e}",
                error_code=int(BS205ErrorCode.DATA_PARSING_ERROR),
            ) from e
