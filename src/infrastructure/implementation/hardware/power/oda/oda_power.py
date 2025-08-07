"""
ODA Power Supply Service

Integrated service for ODA power supply hardware control.
Combines adapter and controller functionality into a single service.
"""

import asyncio
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

    def __init__(self):
        """
        초기화
        """

        # Connection parameters (will be set during connect)
        self._host = ""
        self._port = 0
        self._timeout = 0.0
        self._channel = 0

        # State initialization
        self._is_connected = False
        self._output_enabled = False
        self._device_identity: Optional[str] = None  # Store device identification response
        self._tcp_comm: Optional[TCPCommunication] = None

    async def connect(self, host: str, port: int, timeout: float, channel: int) -> None:
        """
        Connect to power supply hardware

        Args:
            host: IP address or hostname
            port: TCP port number
            timeout: Connection timeout in seconds
            channel: Power channel number

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            # Store connection parameters
            self._host = host
            self._port = port
            self._timeout = timeout
            self._channel = channel

            # Create TCP connection with config values
            self._tcp_comm = TCPCommunication(host, port, timeout)

            logger.info(f"Connecting to ODA Power Supply at {host}:{port} (Channel: {channel})")

            await self._tcp_comm.connect()

            # 연결 테스트 및 초기화
            response = await self._send_command("*IDN?")
            logger.info("*IDN? response received: %r", response)  # 상세 응답 로깅
            
            if response and len(response.strip()) > 0:
                self._is_connected = True
                self._device_identity = response  # Store device identity for CLI display

                # Clear any error status from previous operations
                await self._send_command("*CLS")
                logger.debug("Power Supply error status cleared with *CLS")

                # Small delay before next command
                await asyncio.sleep(0.2)

                logger.info("Power Supply connected successfully: %s", response)
            else:
                logger.warning("Power Supply identification failed - no valid *IDN? response")
                logger.debug("Raw *IDN? response: %r", response)
                raise HardwareConnectionError(
                    "oda_power",
                    "Device identification failed - no valid *IDN? response",
                )

        except TCPError as e:
            logger.error("Failed to connect to ODA Power Supply: %s", str(e))
            self._is_connected = False
            raise HardwareConnectionError("oda_power", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error during ODA connection: %s", str(e))
            self._is_connected = False
            raise HardwareConnectionError("oda_power", str(e)) from e

    async def disconnect(self) -> None:
        """
        Disconnect from power supply hardware

        Raises:
            HardwareOperationError: If disconnection fails
        """
        try:
            if self._tcp_comm:
                await self._tcp_comm.disconnect()

            self._tcp_comm = None
            self._is_connected = False
            self._output_enabled = False

            logger.info("ODA Power Supply disconnected")

        except Exception as e:
            logger.error("Error disconnecting ODA Power Supply: %s", str(e))
            raise HardwareOperationError("oda_power", "disconnect", str(e)) from e

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected and self._tcp_comm is not None and self._tcp_comm.is_connected

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

        try:
            logger.info("Setting ODA voltage: %sV", voltage)

            # 전압 설정
            voltage_response = await self._send_command(f"VOLT {voltage:.2f}")

            if voltage_response is None:
                # For commands that don't return responses, None is expected success
                logger.info("ODA voltage setting applied successfully")
            else:
                logger.info("ODA voltage setting response: %s", voltage_response)

        except TCPError as e:
            logger.error("Failed to set ODA voltage: %s", str(e))
            raise HardwareOperationError("oda_power", "set_voltage", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error setting ODA voltage: %s", str(e))
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
            logger.debug("ODA voltage measurement: %.2fV", voltage)
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

    async def set_current(self, current: float) -> None:
        """
        Set output current

        Args:
            current: Current in amperes

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If current setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        try:
            logger.info("Setting ODA current: %.2fA", current)

            response = await self._send_command(f"CURR {current:.2f}")

            if response is None:
                # For commands that don't return responses, None is expected success
                logger.info("ODA current setting applied successfully")
            else:
                logger.info("ODA current setting response: %s", response)

        except TCPError as e:
            logger.error("Failed to set ODA current: %s", str(e))
            raise HardwareOperationError("oda_power", "set_current", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error setting ODA current: %s", str(e))
            raise HardwareOperationError("oda_power", "set_current", str(e)) from e

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
            logger.error("Failed to enable ODA output: %s", str(e))
            raise HardwareOperationError("oda_power", "enable_output", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error enabling ODA output: %s", str(e))
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
            logger.error("Failed to disable ODA output: %s", str(e))
            raise HardwareOperationError("oda_power", "disable_output", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error disabling ODA output: %s", str(e))
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

        try:
            # Query actual hardware state using OUTP? command
            response = await self._send_command("OUTP?")
            if response:
                # According to manual: "0" = OFF, "1" = ON
                hardware_state = response.strip() == "1"
                self._output_enabled = hardware_state  # Sync software state with hardware
                logger.debug(
                    "ODA output state queried: %s (hardware: %s)", hardware_state, response.strip()
                )
                return hardware_state
            else:
                logger.warning("No response from OUTP? query, using cached state")
                return self._output_enabled
        except Exception as e:
            logger.error("Failed to query ODA output state: %s", str(e))
            return self._output_enabled  # Return cached state on error

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
            "timeout": self._timeout,
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
        if not self._tcp_comm or not self._tcp_comm.is_connected:
            raise HardwareConnectionError("oda_power", "TCP connection not available")

        # MyPy type narrowing: assert that _tcp_comm is not None after connection check
        assert self._tcp_comm is not None, "TCP communication should be available after connection check"

        try:
            # 명령 전송 및 응답 수신 (SCPI 형식)
            # Always add LF terminator for SCPI compatibility
            command_with_terminator = f"{command}\n"
            logger.debug("Adding LF terminator to command: %s", repr(command))

            logger.info(f"Sending command: {command}")

            # Use query() method for commands that expect responses
            if command.endswith("?"):
                response = await self._tcp_comm.query(command_with_terminator)
            else:
                # For commands that don't expect responses, just send
                await self._tcp_comm.send_command(command_with_terminator)
                response = None

            if response:
                response = response.strip()

            logger.info(f"ODA command: {command} -> response: {response}")

            # Add small delay after each command to prevent overwhelming the device
            await asyncio.sleep(0.05)  # 50ms delay between commands

            return response

        except Exception as e:
            logger.error("ODA command '%s' failed: %s", command, str(e))
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

        try:
            logger.info("Setting ODA current limit: %sA", current)

            response = await self._send_command(f"CURR {current:.2f}")

            if response is None:
                # For commands that don't return responses, None is expected success
                logger.info("ODA current limit setting applied successfully")
            else:
                logger.info("ODA current limit setting response: %s", response)

        except TCPError as e:
            logger.error("Failed to set ODA current limit: %s", str(e))
            raise HardwareOperationError("oda_power", "set_current_limit", str(e)) from e
        except Exception as e:
            logger.error("Unexpected error setting ODA current limit: %s", str(e))
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
            logger.debug("ODA current measurement: %.2fA", current)
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

    async def get_current_limit(self) -> float:
        """
        Get current limit setting

        Returns:
            Current limit in amperes

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If current limit reading fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        try:
            # Query current limit
            limit_response = await self._send_command("CURR:UCL?")

            if limit_response is None:
                raise HardwareOperationError(
                    "oda_power",
                    "get_current_limit",
                    "No current limit response",
                )

            current_limit = float(limit_response.strip())
            logger.debug("ODA current limit: %.2fA", current_limit)
            return current_limit

        except ValueError as e:
            raise HardwareOperationError(
                "oda_power",
                "get_current_limit",
                f"Failed to parse current limit: {e}",
            ) from e
        except TCPError as e:
            raise HardwareOperationError("oda_power", "get_current_limit", str(e)) from e
        except Exception as e:
            raise HardwareOperationError("oda_power", "get_current_limit", str(e)) from e
