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
from driver.tcp.communication import TCPCommunication
from driver.tcp.exceptions import TCPError


class OdaPower(PowerService):
    """ODA 전원 공급 장치 통합 서비스"""

    def __init__(self, config: Dict[str, Any]):
        """
        초기화

        Args:
            config: Power 연결 설정 딕셔너리
        """
        # Connection defaults
        self._host = config.get("host", "192.168.1.100")
        self._port = config.get("port", 8080)
        self._timeout = config.get("timeout", 5.0)
        self._channel = config.get("channel", 1)

        # Operational defaults
        self._voltage = config.get("default_voltage", 0.0)
        self._current_limit = config.get("default_current_limit", 5.0)

        # Operational limits
        self._max_voltage = config.get("max_voltage", 30.0)
        self._max_current = config.get("max_current", 50.0)

        # State initialization
        # Config values are already stored directly above

        self._tcp_comm = TCPCommunication(self._host, self._port, self._timeout)
        self._is_connected = False
        self._output_enabled = False
        self._device_identity = None  # Store device identification response

    async def connect(self) -> None:
        """
        Connect to power supply hardware

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            logger.info(
                "Connecting to ODA Power Supply at %s:%s (Channel: %s)",
                self._host,
                self._port,
                self._channel,
            )

            await self._tcp_comm.connect()

            # 연결 테스트 및 초기화
            response = await self._send_command("*IDN?")
            if response and "ODA" in response:
                self._is_connected = True
                self._device_identity = response  # Store device identity for CLI display

                # 안전을 위해 출력 비활성화
                await self.disable_output()

                logger.info(f"ODA Power Supply connected successfully: {response}")
            else:
                logger.warning("ODA Power Supply identification failed")
                raise HardwareConnectionError(
                    "oda_power",
                    "Device identification failed",
                )

        except TCPError as e:
            logger.error("Failed to connect to ODA Power Supply: %s", e)
            self._is_connected = False
            raise HardwareConnectionError("oda_power", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error during ODA connection: %s", e)
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
            logger.error("Error disconnecting ODA Power Supply: %s", e)
            raise HardwareOperationError("oda_power", "disconnect", str(e)) from e

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected and self._tcp_comm.is_connected

    async def set_voltage(self, voltage: Optional[float] = None) -> None:
        """
        Set output voltage

        Args:
            voltage: Target voltage in volts (uses default if None)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If voltage setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        # Apply default + override pattern
        target_voltage = voltage if voltage is not None else self._voltage

        # 값 범위 검증
        if not 0 <= target_voltage <= self._max_voltage:
            raise HardwareOperationError(
                "oda_power",
                "set_voltage",
                f"Voltage must be 0-{self._max_voltage}V, got {target_voltage}V",
            )

        try:
            logger.info("Setting ODA voltage: %sV", target_voltage)

            # 전압 설정
            voltage_response = await self._send_command(f"VOLT {target_voltage:.3f}")

            if voltage_response is None:
                # For commands that don't return responses, None is expected success
                logger.info("ODA voltage setting applied successfully")
            else:
                logger.info("ODA voltage setting response: %s", voltage_response)

        except TCPError as e:
            logger.error("Failed to set ODA voltage: %s", e)
            raise HardwareOperationError("oda_power", "set_voltage", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error setting ODA voltage: %s", e)
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
                raise HardwareOperationError(
                    "oda_power",
                    "get_voltage",
                    "No voltage response",
                )

            voltage = float(voltage_response.strip())
            logger.debug("ODA voltage measurement: %.3fV", voltage)
            return voltage

        except ValueError as e:
            raise HardwareOperationError(
                "oda_power",
                "get_voltage",
                f"Failed to parse voltage: {e}",
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
            logger.error("Failed to enable ODA output: %s", e)
            raise HardwareOperationError("oda_power", "enable_output", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error enabling ODA output: %s", e)
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
            logger.error("Failed to disable ODA output: %s", e)
            raise HardwareOperationError("oda_power", "disable_output", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error disabling ODA output: %s", e)
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

    async def get_device_identity(self) -> Optional[str]:
        """
        Get device identification string
        
        Returns:
            Device identification string from *IDN? command, or None if not connected
        """
        return self._device_identity

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
            "device_identity": self._device_identity,
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

            logger.debug("ODA command: %s -> response: %s", command, response)
            return response

        except Exception as e:
            logger.error("ODA command '%s' failed: %s", command, e)
            raise TCPError(f"Communication failed: {e}") from e

    async def set_current_limit(self, current: Optional[float] = None) -> None:
        """
        Set current limit

        Args:
            current: Current limit in amperes (uses default if None)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If current limit setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        # Apply default + override pattern
        target_current = current if current is not None else self._current_limit

        # 값 범위 검증
        if not 0 <= target_current <= self._max_current:
            raise HardwareOperationError(
                "oda_power",
                "set_current_limit",
                f"Current must be 0-{self._max_current}A, got {target_current}A",
            )

        try:
            logger.info("Setting ODA current limit: %sA", target_current)

            response = await self._send_command(f"CURR {target_current:.3f}")

            if response is None:
                # For commands that don't return responses, None is expected success
                logger.info("ODA current limit setting applied successfully")
            else:
                logger.info("ODA current limit setting response: %s", response)

        except TCPError as e:
            logger.error("Failed to set ODA current limit: %s", e)
            raise HardwareOperationError("oda_power", "set_current_limit", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error setting ODA current limit: %s", e)
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
                raise HardwareOperationError(
                    "oda_power",
                    "get_current",
                    "No current response",
                )

            current = float(current_response.strip())
            logger.debug("ODA current measurement: %.3fA", current)
            return current

        except ValueError as e:
            raise HardwareOperationError(
                "oda_power",
                "get_current",
                f"Failed to parse current: {e}",
            ) from e
        except TCPError as e:
            raise HardwareOperationError("oda_power", "get_current", str(e)) from e
        except Exception as e:
            raise HardwareOperationError("oda_power", "get_current", str(e)) from e
