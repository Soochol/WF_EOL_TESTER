"""
ODA Power Supply Service

Integrated service for ODA power supply hardware control.
Combines adapter and controller functionality into a single service.
"""

from typing import Any, Dict, Optional

from loguru import logger

from application.interfaces.hardware.power import (
    PowerService,
)
from domain.exceptions import (
    HardwareConnectionError,
    HardwareOperationError,
)
from domain.value_objects.hardware_configuration import (
    PowerConfig,
)
from driver.tcp.communication import TCPCommunication
from driver.tcp.exceptions import TCPError


class OdaPower(PowerService):
    """ODA 전원 공급 장치 통합 서비스"""

    def __init__(self, host: str, port: int = 8080, timeout: float = 5.0, channel: int = 1):
        """
        초기화

        Args:
            host: IP 주소
            port: TCP 포트
            timeout: 통신 타임아웃 (초)
            channel: 출력 채널 번호
        """
        self._host = host
        self._port = port
        self._timeout = timeout
        self._channel = channel

        self._tcp_comm = TCPCommunication(host, port, timeout)
        self._is_connected = False
        self._output_enabled = False

    async def connect(self, power_config: PowerConfig) -> None:
        """
        Connect to power supply hardware

        Args:
            power_config: Power supply connection configuration

        Raises:
            HardwareConnectionError: If connection fails
        """
        # Update connection parameters from config
        self._host = power_config.host
        self._port = power_config.port
        self._timeout = power_config.timeout
        self._channel = power_config.channel
        self._tcp_comm = TCPCommunication(self._host, self._port, self._timeout)

        try:
            logger.info(
                f"Connecting to ODA Power Supply at {self._host}:{self._port} (Channel: {self._channel})"
            )

            await self._tcp_comm.connect()

            # 연결 테스트 및 초기화
            response = await self._send_command("*IDN?")
            if response and "ODA" in response:
                self._is_connected = True

                # 안전을 위해 출력 비활성화
                await self.disable_output()

                logger.info("ODA Power Supply connected successfully")
            else:
                logger.warning("ODA Power Supply identification failed")
                raise HardwareConnectionError("oda_power", "Device identification failed")

        except TCPError as e:
            logger.error(f"Failed to connect to ODA Power Supply: {e}")
            self._is_connected = False
            raise HardwareConnectionError("oda_power", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error during ODA connection: {e}")
            self._is_connected = False
            raise HardwareConnectionError("oda_power", str(e)) from e

    async def disconnect(self) -> None:
        """
        Disconnect from power supply hardware

        Raises:
            HardwareOperationError: If disconnection fails
        """
        try:
            # 안전을 위해 출력 비활성화
            if self._is_connected:
                await self.disable_output()

            await self._tcp_comm.disconnect()
            self._is_connected = False
            self._output_enabled = False

            logger.info("ODA Power Supply disconnected")

        except Exception as e:
            logger.error(f"Error disconnecting ODA Power Supply: {e}")
            raise HardwareOperationError("oda_power", "disconnect", str(e)) from e

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected and self._tcp_comm.is_connected

    async def set_voltage(self, voltage: float) -> None:
        """
        Set output voltage

        Args:
            voltage: Target voltage in volts

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If voltage setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        # 값 범위 검증
        if not 0 <= voltage <= 30:
            raise HardwareOperationError(
                "oda_power", "set_voltage", f"Voltage must be 0-30V, got {voltage}V"
            )

        try:
            logger.info(f"Setting ODA voltage: {voltage}V")

            # 전압 설정
            voltage_response = await self._send_command(f"VOLT {voltage:.3f}")

            if voltage_response is None:
                # For commands that don't return responses, None is expected success
                logger.info("ODA voltage setting applied successfully")
            else:
                logger.info(f"ODA voltage setting response: {voltage_response}")

        except TCPError as e:
            logger.error(f"Failed to set ODA voltage: {e}")
            raise HardwareOperationError("oda_power", "set_voltage", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error setting ODA voltage: {e}")
            raise HardwareOperationError("oda_power", "set_voltage", str(e)) from e

    async def get_voltage(self) -> float:
        """
        Get current output voltage

        Returns:
            Current voltage in volts

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If voltage reading fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        try:
            # 전압 측정
            voltage_response = await self._send_command("MEAS:VOLT?")

            if voltage_response is None:
                raise HardwareOperationError("oda_power", "get_voltage", "No voltage response")

            voltage = float(voltage_response.strip())
            logger.debug(f"ODA voltage measurement: {voltage:.3f}V")
            return voltage

        except ValueError as e:
            raise HardwareOperationError(
                "oda_power", "get_voltage", f"Failed to parse voltage: {e}"
            ) from e
        except TCPError as e:
            raise HardwareOperationError("oda_power", "get_voltage", str(e)) from e
        except Exception as e:
            raise HardwareOperationError("oda_power", "get_voltage", str(e)) from e

    async def enable_output(self) -> None:
        """
        Enable power output

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If output enabling fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        try:
            _ = await self._send_command("OUTP ON")

            # For commands that don't return responses, None is expected success
            self._output_enabled = True
            logger.info("ODA output enabled")

        except TCPError as e:
            logger.error(f"Failed to enable ODA output: {e}")
            raise HardwareOperationError("oda_power", "enable_output", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error enabling ODA output: {e}")
            raise HardwareOperationError("oda_power", "enable_output", str(e)) from e

    async def disable_output(self) -> None:
        """
        Disable power output

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If output disabling fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        try:
            _ = await self._send_command("OUTP OFF")

            # For commands that don't return responses, None is expected success
            self._output_enabled = False
            logger.info("ODA output disabled")

        except TCPError as e:
            logger.error(f"Failed to disable ODA output: {e}")
            raise HardwareOperationError("oda_power", "disable_output", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error disabling ODA output: {e}")
            raise HardwareOperationError("oda_power", "disable_output", str(e)) from e

    async def is_output_enabled(self) -> bool:
        """
        Check if power output is enabled

        Returns:
            True if output is enabled, False otherwise

        Raises:
            HardwareConnectionError: If not connected
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        return self._output_enabled

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Returns:
            상태 정보 딕셔너리
        """
        status = {
            "connected": await self.is_connected(),
            "host": self._host,
            "port": self._port,
            "channel": self._channel,
            "output_enabled": self._output_enabled,
            "hardware_type": "ODA",
        }

        if await self.is_connected():
            try:
                # 현재 측정값도 포함
                status["current_voltage"] = await self.get_voltage()
                status["current_current"] = await self.get_current()
                status["output_enabled"] = await self.is_output_enabled()
                status["last_error"] = None
            except Exception as e:
                status["current_voltage"] = None
                status["current_current"] = None
                status["output_enabled"] = None
                status["last_error"] = str(e)

        return status

    async def _send_command(self, command: str) -> Optional[str]:
        """
        ODA에 명령 전송

        Args:
            command: 전송할 명령

        Returns:
            응답 문자열

        Raises:
            TCPError: 통신 오류
        """
        if not self._tcp_comm.is_connected:
            raise TCPError("No connection available")

        try:
            # 명령 전송 및 응답 수신 (SCPI 형식)
            command_with_terminator = f"{command}\n"

            # Use query() method for commands that expect responses
            if command.endswith("?"):
                response = await self._tcp_comm.query(command_with_terminator)
            else:
                # For commands that don't expect responses, just send
                await self._tcp_comm.send_command(command_with_terminator)
                response = None

            if response:
                response = response.strip()

            logger.debug(f"ODA command: {command} -> response: {response}")
            return response

        except Exception as e:
            logger.error(f"ODA command '{command}' failed: {e}")
            raise TCPError(f"Communication failed: {e}") from e

    async def set_current_limit(self, current: float) -> None:
        """
        Set current limit

        Args:
            current: Current limit in amperes

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If current limit setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        # 값 범위 검증
        if not 0 <= current <= 5:
            raise HardwareOperationError(
                "oda_power", "set_current_limit", f"Current must be 0-5A, got {current}A"
            )

        try:
            logger.info(f"Setting ODA current limit: {current}A")

            response = await self._send_command(f"CURR {current:.3f}")

            if response is None:
                # For commands that don't return responses, None is expected success
                logger.info("ODA current limit setting applied successfully")
            else:
                logger.info(f"ODA current limit setting response: {response}")

        except TCPError as e:
            logger.error(f"Failed to set ODA current limit: {e}")
            raise HardwareOperationError("oda_power", "set_current_limit", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error setting ODA current limit: {e}")
            raise HardwareOperationError("oda_power", "set_current_limit", str(e)) from e

    async def get_current(self) -> float:
        """
        Get current output current

        Returns:
            Current in amperes

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If current reading fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        try:
            # 전류 측정
            current_response = await self._send_command("MEAS:CURR?")

            if current_response is None:
                raise HardwareOperationError("oda_power", "get_current", "No current response")

            current = float(current_response.strip())
            logger.debug(f"ODA current measurement: {current:.3f}A")
            return current

        except ValueError as e:
            raise HardwareOperationError(
                "oda_power", "get_current", f"Failed to parse current: {e}"
            ) from e
        except TCPError as e:
            raise HardwareOperationError("oda_power", "get_current", str(e)) from e
        except Exception as e:
            raise HardwareOperationError("oda_power", "get_current", str(e)) from e
