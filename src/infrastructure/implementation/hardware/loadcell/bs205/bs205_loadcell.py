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
    parse_weight_response,
    validate_sample_parameters,
    validate_weight_range,
)


class BS205LoadCell(LoadCellService):
    """BS205 로드셀 통합 서비스"""

    def __init__(
        self,
        config: Dict[str, Any],
    ):
        """
        초기화

        Args:
            config: LoadCell 연결 설정 딕셔너리
        """
        # Extract config values with defaults
        self._port = config.get("port", "COM3")
        self._baudrate = config.get("baudrate", 9600)
        self._timeout = config.get("timeout", 1.0)
        self._bytesize = config.get("bytesize", 8)
        self._stopbits = config.get("stopbits", 1)
        self._parity = config.get("parity", None)
        self._indicator_id = config.get("indicator_id", 1)
        self._max_force_range = config.get("max_force_range", 1000.0)
        self._sampling_interval_ms = config.get("sampling_interval_ms", 100)
        self._zero_tolerance = config.get("zero_tolerance", 0.01)

        # State initialization
        # Config values are already stored directly above

        self._connection: Optional[SerialConnection] = None
        self._is_connected = False

    async def connect(self) -> None:
        """
        하드웨어 연결

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            # 사용 가능한 COM 포트 체크
            try:
                import serial.tools.list_ports

                available_ports = [port.device for port in serial.tools.list_ports.comports()]
                logger.info(f"Available COM ports: {available_ports}")
            except ImportError:
                logger.warning("Cannot check available ports - pyserial not fully installed")

            logger.info(
                f"Connecting to BS205 LoadCell - Port: {self._port}, Baud: {self._baudrate}, Timeout: {self._timeout}, "
                f"ByteSize: {self._bytesize}, StopBits: {self._stopbits}, Parity: {self._parity}, ID: {self._indicator_id}"
            )

            self._connection = await SerialManager.create_connection(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout,
                bytesize=self._bytesize,
                stopbits=self._stopbits,
                parity=self._parity,
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

    async def zero(self) -> bool:
        """
        영점 조정

        Returns:
            영점 조정 성공 여부

        Raises:
            BS205HardwareError: 연결되지 않은 경우
            BS205OperationError: 영점 조정 실패
        """
        if not await self.is_connected():
            raise BS205HardwareError(
                "BS205 LoadCell is not connected",
                error_code=int(BS205ErrorCode.HARDWARE_NOT_CONNECTED),
            )

        try:
            logger.info("Zeroing BS205 LoadCell")

            # 영점 조정 명령 (바이너리 프로토콜)
            response = await self._send_bs205_command(CMD_ZERO)

            # 영점 조정 완료 대기
            await asyncio.sleep(ZERO_OPERATION_DELAY)

            # 영점 조정 결과 확인
            if response and ("OK" in response or "Z" in response):
                logger.info(STATUS_MESSAGES["zeroed"])
                return True

            logger.warning(f"BS205 zero command unclear response: {response}")
            return True  # BS205는 응답이 애매할 수 있음

        except (SerialCommunicationError, SerialConnectionError, SerialTimeoutError) as e:
            logger.error(STATUS_MESSAGES["zero_failed"])
            raise BS205OperationError(
                f"Failed to zero BS205 LoadCell: {e}",
                error_code=int(BS205ErrorCode.OPERATION_ZERO_FAILED),
            ) from e

    async def zero_calibration(self) -> None:
        """
        영점 조정 (zero_calibration은 zero 메서드를 래핑)

        Raises:
            HardwareOperationError: If calibration fails
        """
        from domain.exceptions.eol_exceptions import (
            HardwareOperationError,
        )

        try:
            success = await self.zero()
            if not success:
                raise HardwareOperationError(
                    "bs205_loadcell",
                    "zero_calibration",
                    "Zero calibration failed",
                )
        except Exception as e:
            raise HardwareOperationError(
                "bs205_loadcell",
                "zero_calibration",
                f"Zero calibration failed: {e}",
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

        Returns:
            상태 정보 딕셔너리
        """
        status = {
            "connected": await self.is_connected(),
            "port": self._port,
            "baudrate": self._baudrate,
            "indicator_id": self._indicator_id,
            "hardware_type": "BS205",
        }

        if await self.is_connected():
            try:
                # 현재 측정값도 포함
                force_value = await self.read_force()
                status["current_force"] = force_value.value
                status["current_force_unit"] = force_value.unit.value
                status["last_error"] = None
            except Exception as e:
                status["current_force"] = None
                status["current_force_unit"] = None
                status["last_error"] = str(e)

        return status

    async def _send_bs205_command(self, command: str, timeout: Optional[float] = None) -> Optional[str]:
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

        try:
            cmd_timeout = timeout if timeout is not None else self._timeout
            
            # BS205 바이너리 명령어 생성: ID + Command
            # ID=0 → 30H, R → 52H
            id_byte = ord(str(self._indicator_id))  # '0' → 0x30
            cmd_byte = ord(command)  # 'R' → 0x52
            command_bytes = bytes([id_byte, cmd_byte])
            
            logger.debug(f"Sending BS205 binary command: ID={self._indicator_id}({id_byte:02X}H) + {command}({cmd_byte:02X}H)")
            
            # 바이너리 명령어 전송
            await self._connection.write(command_bytes)
            
            # STX(02H)까지 읽기
            stx_response = await self._connection.read_until(b"\x02", timeout=cmd_timeout)
            if not stx_response or stx_response[-1:] != b"\x02":
                logger.warning("STX not received or invalid")
                return None
            
            # ETX(03H)까지 나머지 응답 읽기
            response_data = await self._connection.read_until(b"\x03", timeout=cmd_timeout)
            if not response_data or response_data[-1:] != b"\x03":
                logger.warning("ETX not received or invalid")
                return None
                
            # STX + 데이터 + ETX 결합
            full_response = stx_response + response_data[:-1]  # ETX 제거 후 결합
            
            # 바이너리 응답을 ASCII로 변환하여 파싱
            ascii_response = self._parse_bs205_response(full_response)
            logger.debug(f"BS205 response: {ascii_response}")
            
            return ascii_response
            
        except Exception as e:
            logger.error(f"BS205 binary command '{command}' failed: {e}")
            raise BS205CommunicationError(
                f"Command '{command}' failed: {e}",
                error_code=int(BS205ErrorCode.COMM_SERIAL_ERROR),
            ) from e

    def _parse_bs205_response(self, response_bytes: bytes) -> str:
        """
        BS205 바이너리 응답을 ASCII 문자열로 파싱
        
        응답 형태: STX(02H) + ID + 부호 + 값 + ETX(03H)
        예: 02 30 2B 20 37 2E 34 38 37 03 → "0+_7.487"
        """
        try:
            if len(response_bytes) < 4:  # 최소: STX + ID + 부호 + ETX
                return ""
                
            # STX(02H) 확인
            if response_bytes[0] != 0x02:
                return ""
                
            # ETX(03H) 찾기
            etx_pos = response_bytes.find(0x03)
            if etx_pos == -1:
                return ""
                
            # 데이터 부분 추출 (STX와 ETX 사이)
            data_bytes = response_bytes[1:etx_pos]
            
            # ASCII로 변환
            ascii_data = data_bytes.decode('ascii', errors='ignore')
            logger.debug(f"Parsed BS205 data: '{ascii_data}'")
            
            return ascii_data
            
        except Exception as e:
            logger.error(f"Failed to parse BS205 response: {e}")
            return ""

    def _parse_bs205_weight(self, response: str) -> tuple[float, str]:
        """
        BS205 가중치 응답 파싱
        
        응답 형태: "ID + 부호 + 값"
        예: "0+_7.487", "0-12.34", "15+1.7486"
        
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
            
            # ID 제거 (첫 번째 또는 처음 두 문자)
            # "0+_7.487" → "+_7.487" 또는 "15+1.7486" → "+1.7486"
            if response[1] in ['+', '-']:
                # 단일 ID인 경우 (0, 1, 2, ...)
                weight_part = response[1:]
            elif len(response) > 2 and response[2] in ['+', '-']:
                # 두 자리 ID인 경우 (10, 15, ...)
                weight_part = response[2:]
            else:
                raise BS205CommunicationError(
                    f"Cannot find sign in BS205 response: '{response}'",
                    error_code=int(BS205ErrorCode.DATA_PARSING_ERROR),
                )
            
            # 부호 추출
            sign = weight_part[0]  # '+' 또는 '-'
            value_part = weight_part[1:]  # "_7.487" 또는 "12.34"
            
            # 공백('_' 또는 실제 공백) 제거하고 숫자 추출
            value_clean = value_part.replace('_', '').replace(' ', '')
            
            # 소수점이 없으면 적절한 위치에 추가 (BS205 특성에 따라)
            if '.' not in value_clean and len(value_clean) > 2:
                # 마지막 3자리를 소수점 이하로 처리 (예: "7487" → "7.487")
                value_clean = value_clean[:-3] + '.' + value_clean[-3:]
            
            # float 변환
            weight_value = float(value_clean)
            if sign == '-':
                weight_value = -weight_value
                
            logger.debug(f"Parsed BS205 weight: '{response}' → {weight_value}")
            
            # BS205는 일반적으로 kg 단위 사용
            return weight_value, "kg"
            
        except ValueError as e:
            raise BS205CommunicationError(
                f"Cannot convert BS205 weight value: '{response}'",
                error_code=int(BS205ErrorCode.DATA_CONVERSION_ERROR),
            ) from e
        except Exception as e:
            raise BS205CommunicationError(
                f"Failed to parse BS205 weight: '{response}', error: {e}",
                error_code=int(BS205ErrorCode.DATA_PARSING_ERROR),
            ) from e

    async def _send_command(self, command: str, timeout: Optional[float] = None) -> Optional[str]:
        """
        BS205에 명령 전송

        Args:
            command: 전송할 명령

        Returns:
            응답 문자열

        Raises:
            SerialCommunicationError, SerialConnectionError, SerialTimeoutError: 통신 오류
        """
        if not self._connection:
            raise BS205CommunicationError(
                "No connection available",
                error_code=int(BS205ErrorCode.HARDWARE_NOT_CONNECTED),
            )

        try:
            # 새로운 간단한 API 사용
            cmd_timeout = timeout if timeout is not None else self._timeout
            response = await self._connection.send_command(command, "\r", cmd_timeout)

            logger.debug(f"BS205 command: {command} -> response: {response}")
            return response

        except Exception as e:
            logger.error(f"BS205 command '{command}' failed: {e}")
            raise BS205CommunicationError(
                f"Command '{command}' failed: {e}",
                error_code=int(BS205ErrorCode.COMM_SERIAL_ERROR),
            ) from e

    async def read_multiple_samples(self, count: int, interval_ms: int = 100) -> list[float]:
        """
        여러 샘플 연속 측정

        Args:
            count: 측정 횟수
            interval_ms: 측정 간격 (밀리초)

        Returns:
            힘 값 리스트

        Raises:
            BS205HardwareError: 연결되지 않은 경우
            BS205OperationError: 샘플링 실패
        """
        if not await self.is_connected():
            raise BS205HardwareError(
                "BS205 LoadCell is not connected",
                error_code=int(BS205ErrorCode.HARDWARE_NOT_CONNECTED),
            )

        # 샘플링 파라미터 검증
        validate_sample_parameters(count, interval_ms)

        samples = []
        interval_sec = interval_ms / 1000.0

        logger.info(f"Reading {count} samples with {interval_ms}ms interval")

        for i in range(count):
            if i > 0:
                await asyncio.sleep(interval_sec)

            force = await self.read_force()
            force_value = force.value  # Extract the numeric value
            samples.append(force_value)
            logger.debug(f"Sample {i + 1}/{count}: {force_value:.3f}N")

        logger.info(f"Completed {count} samples, avg: {sum(samples) / len(samples):.3f}N")
        return samples
