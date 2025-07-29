"""
BS205 LoadCell Service

Integrated service for BS205 LoadCell hardware control.
Combines adapter and controller functionality into a single service.
"""

from typing import Any, Dict, Optional

import asyncio
from loguru import logger

from application.interfaces.hardware.loadcell import (
    LoadCellService,
)
from domain.enums.measurement_units import MeasurementUnit
from domain.value_objects.hardware_configuration import (
    LoadCellConfig,
)
from domain.value_objects.measurements import ForceValue
from driver.serial.serial import SerialError, SerialManager
from infrastructure.implementation.hardware.loadcell.bs205.constants import (
    CMD_IDENTITY,
    CMD_READ_WEIGHT,
    CMD_ZERO,
    DEFAULT_BAUDRATE,
    DEFAULT_INDICATOR_ID,
    DEFAULT_TIMEOUT,
    DEVICE_ID_PATTERN,
    KG_TO_NEWTON,
    STATUS_MESSAGES,
    ZERO_OPERATION_DELAY,
)
from infrastructure.implementation.hardware.loadcell.bs205.error_codes import (
    BS205CommunicationError,
    BS205Error,
    BS205ErrorCode,
    BS205HardwareError,
    BS205OperationError,
    convert_weight_to_force,
    parse_weight_response,
    validate_sample_parameters,
    validate_weight_range,
)


class BS205LoadCell(LoadCellService):
    """BS205 로드셀 통합 서비스"""

    def __init__(
        self,
        port: str,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = DEFAULT_TIMEOUT,
        indicator_id: int = DEFAULT_INDICATOR_ID,
    ):
        """
        초기화

        Args:
            port: 시리얼 포트 (예: 'COM3', '/dev/ttyUSB0')
            baudrate: 통신 속도
            timeout: 통신 타임아웃 (초)
            indicator_id: 지시계 ID
        """
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._indicator_id = indicator_id

        self._connection = None
        self._is_connected = False

    async def connect(self, loadcell_config: LoadCellConfig) -> None:
        """
        하드웨어 연결

        Args:
            loadcell_config: LoadCell connection configuration

        Raises:
            HardwareConnectionError: If connection fails
        """
        # Update connection parameters from config
        self._port = loadcell_config.port
        self._baudrate = loadcell_config.baudrate
        self._timeout = loadcell_config.timeout
        self._indicator_id = loadcell_config.indicator_id

        try:
            logger.info(
                f"Connecting to BS205 LoadCell on {self._port} at {self._baudrate} baud (ID: {self._indicator_id})"
            )

            self._connection = await SerialManager.create_connection(
                port=self._port, baudrate=self._baudrate, timeout=self._timeout
            )

            # 연결 테스트 명령 전송
            response = await self._send_command(CMD_IDENTITY)
            if response and DEVICE_ID_PATTERN in response:
                self._is_connected = True
                logger.info(STATUS_MESSAGES["connected"])
                return True

            logger.warning("Connection test failed: expected %s in response", DEVICE_ID_PATTERN)
            return False

        except SerialError as e:
            error_msg = f"Failed to connect to BS205 LoadCell: {e}"
            logger.error(error_msg)
            self._is_connected = False
            raise BS205CommunicationError(
                error_msg, error_code=int(BS205ErrorCode.HARDWARE_INITIALIZATION_FAILED)
            ) from e

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
            logger.info(STATUS_MESSAGES["disconnected"])
            return True

        except Exception as e:
            logger.error("Error disconnecting BS205 LoadCell: %s", e)
            return False

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
            # 현재 무게 읽기 명령
            response = await self._send_command(CMD_READ_WEIGHT)

            if not response:
                raise BS205CommunicationError(
                    "No response from BS205 LoadCell", error_code=int(BS205ErrorCode.COMM_TIMEOUT)
                )

            # 응답 파싱 및 검증
            weight_kg, _ = parse_weight_response(response)

            # 무게 범위 검증
            validate_weight_range(weight_kg)

            # kg을 Newton으로 변환
            force_n = convert_weight_to_force(weight_kg, KG_TO_NEWTON)

            logger.debug("BS205 LoadCell reading: %skg = %.3fN", weight_kg, force_n)
            return ForceValue.from_raw_data(force_n, MeasurementUnit.NEWTON)

        except BS205Error:
            raise  # Re-raise BS205 specific errors
        except SerialError as e:
            raise BS205CommunicationError(
                f"Communication error: {e}", error_code=int(BS205ErrorCode.COMM_SERIAL_ERROR)
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

            # 영점 조정 명령
            response = await self._send_command(CMD_ZERO)

            # 영점 조정 완료 대기
            await asyncio.sleep(ZERO_OPERATION_DELAY)

            # 영점 조정 결과 확인
            if response and ("OK" in response or "Z" in response):
                logger.info(STATUS_MESSAGES["zeroed"])
                return True

            logger.warning("BS205 zero command unclear response: %s", response)
            return True  # BS205는 응답이 애매할 수 있음

        except SerialError as e:
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
                    "bs205_loadcell", "zero_calibration", "Zero calibration failed"
                )
        except Exception as e:
            raise HardwareOperationError(
                "bs205_loadcell", "zero_calibration", f"Zero calibration failed: {e}"
            ) from e

    async def read_raw_value(self) -> float:
        """
        원시 측정값 읽기 (BS205는 force와 동일)

        Returns:
            Raw measurement value
        """
        force_value = await self.read_force()
        return force_value.value

    async def set_measurement_rate(self, rate_hz: int) -> None:
        """
        측정 샘플링 속도 설정 (BS205는 고정 속도 사용)

        Args:
            rate_hz: Sampling rate in Hz

        Raises:
            HardwareOperationError: If rate setting fails
        """
        # BS205는 고정 측정 속도를 사용하므로 경고만 출력
        logger.warning(
            "BS205 LoadCell uses fixed measurement rate, ignoring requested %sHz", rate_hz
        )
        # 실제 하드웨어에서는 이 기능을 지원하지 않을 수 있음

    async def get_measurement_rate(self) -> int:
        """
        현재 측정 샘플링 속도 조회

        Returns:
            Current sampling rate in Hz
        """
        # BS205의 기본 측정 속도 (추정값)
        return 10  # 10Hz 추정

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
            "measurement_rate_hz": await self.get_measurement_rate(),
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

    async def _send_command(self, command: str) -> Optional[str]:
        """
        BS205에 명령 전송

        Args:
            command: 전송할 명령

        Returns:
            응답 문자열

        Raises:
            SerialError: 통신 오류
        """
        if not self._connection:
            raise BS205CommunicationError(
                "No connection available", error_code=int(BS205ErrorCode.HARDWARE_NOT_CONNECTED)
            )

        try:
            # 새로운 간단한 API 사용
            response = await self._connection.send_command(command, "\r", self._timeout)

            logger.debug("BS205 command: %s -> response: %s", command, response)
            return response

        except Exception as e:
            logger.error("BS205 command '%s' failed: %s", command, e)
            raise BS205CommunicationError(
                f"Command '{command}' failed: {e}", error_code=int(BS205ErrorCode.COMM_SERIAL_ERROR)
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

        logger.info("Reading %d samples with %dms interval", count, interval_ms)

        for i in range(count):
            if i > 0:
                await asyncio.sleep(interval_sec)

            force = await self.read_force()
            samples.append(force)
            logger.debug("Sample %d/%d: %.3fN", i + 1, count, force)

        logger.info("Completed %d samples, avg: %.3fN", count, sum(samples) / len(samples))
        return samples
