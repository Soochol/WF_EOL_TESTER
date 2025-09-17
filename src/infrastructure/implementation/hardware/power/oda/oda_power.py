"""
ODA Power Supply Service

Integrated service for ODA power supply hardware control.
Combines adapter and controller functionality into a single service.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
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

    def __init__(self, host: str, port: int, timeout: float, channel: int):
        """
        초기화

        Args:
            host: IP address or hostname
            port: TCP port number
            timeout: Connection timeout in seconds
            channel: Power channel number
        """

        # Connection parameters
        self._host = host
        self._port = port
        self._timeout = timeout
        self._channel = channel

        # State initialization
        self._is_connected = False
        self._output_enabled = False
        self._device_identity: Optional[str] = None  # Store device identification response
        self._tcp_comm: Optional[TCPCommunication] = None

    async def connect(self) -> None:
        """
        Connect to power supply hardware

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            # Create TCP connection with config values
            self._tcp_comm = TCPCommunication(self._host, self._port, self._timeout)

            logger.info(
                f"Connecting to ODA Power Supply at {self._host}:{self._port} (Channel: {self._channel})"
            )

            await self._tcp_comm.connect()

            # 연결 테스트 및 초기화
            response = await self._send_command("*IDN?")
            logger.info(f"*IDN? response received: {response!r}")  # 상세 응답 로깅

            if response and len(response.strip()) > 0:
                self._is_connected = True
                self._device_identity = response  # Store device identity for CLI display

                # Clear any error status from previous operations
                await self._send_command("*CLS")
                logger.debug("Power Supply error status cleared with *CLS")

                # Small delay before next command
                await asyncio.sleep(0.2)

                logger.info(f"Power Supply connected successfully: {response}")
            else:
                logger.warning("Power Supply identification failed - no valid *IDN? response")
                logger.debug(f"Raw *IDN? response: {response!r}")
                raise HardwareConnectionError(
                    "oda_power",
                    "Device identification failed - no valid *IDN? response",
                )

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
            if self._tcp_comm:
                await self._tcp_comm.disconnect()

            self._tcp_comm = None
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
            logger.info(f"Setting ODA voltage: {voltage}V")

            # 전압 설정
            voltage_response = await self._send_command(f"VOLT {voltage:.2f}")

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
                raise HardwareOperationError(
                    "oda_power",
                    "get_voltage",
                    "No voltage response",
                )

            voltage = float(voltage_response.strip())
            logger.debug(f"ODA voltage measurement: {voltage:.2f}V")
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
            logger.info(f"Setting ODA current: {current:.2f}A")

            response = await self._send_command(f"CURR {current:.2f}")

            if response is None:
                # For commands that don't return responses, None is expected success
                logger.info("ODA current setting applied successfully")
            else:
                logger.info(f"ODA current setting response: {response}")

        except TCPError as e:
            logger.error(f"Failed to set ODA current: {e}")
            raise HardwareOperationError("oda_power", "set_current", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error setting ODA current: {e}")
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

        # Return cached state directly to avoid unnecessary hardware queries during monitoring
        # Hardware state is synchronized when enable_output()/disable_output() is called
        logger.debug(
            f"ODA output state (cached): {'ENABLED' if self._output_enabled else 'DISABLED'}"
        )
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
            except asyncio.CancelledError:
                # During shutdown, return safe defaults without raising
                status["current_voltage"] = None
                status["current_current"] = None
                status["output_enabled"] = False  # Assume safe state (output disabled)
                status["last_error"] = "Status check cancelled during shutdown"
                logger.debug(
                    "Power status check cancelled during shutdown - returning safe defaults"
                )
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
        assert (
            self._tcp_comm is not None
        ), "TCP communication should be available after connection check"

        try:
            # 명령 전송 및 응답 수신 (SCPI 형식)
            # Always add LF terminator for SCPI compatibility
            command_with_terminator = f"{command}\n"
            logger.debug(f"Adding LF terminator to command: {command!r}")

            logger.debug(f"Sending command: {command}")

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

            # Add small delay after each command to prevent overwhelming the device
            await asyncio.sleep(0.05)  # 50ms delay between commands

            return response

        except asyncio.CancelledError:
            logger.debug(f"ODA command '{command}' cancelled during shutdown")
            # Re-raise CancelledError to properly propagate cancellation
            raise
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

        try:
            logger.info(f"Setting ODA current limit: {current}A")

            response = await self._send_command(f"CURR {current:.2f}")

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
                raise HardwareOperationError(
                    "oda_power",
                    "get_current",
                    "No current response",
                )

            current = float(current_response.strip())
            logger.debug(f"ODA current measurement: {current:.2f}A")
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
            logger.debug(f"ODA current limit: {current_limit:.2f}A")
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

    async def get_all_measurements(self) -> Dict[str, float]:
        """
        Get all measurements at once using MEAS:ALL? command

        Uses SCPI MEAS:ALL? command to retrieve voltage and current simultaneously,
        reducing communication overhead and ensuring consistent measurement timing.

        Returns:
            Dictionary containing:
            - 'voltage': Output voltage in volts
            - 'current': Output current in amperes
            - 'power': Calculated power in watts (V × A)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If measurement fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("oda_power", "Power Supply is not connected")

        try:
            # Check power output status first
            output_enabled = await self.is_output_enabled()
            logger.debug(
                f"Power output status before measurement: {'ENABLED' if output_enabled else 'DISABLED'}"
            )

            # Send MEAS:ALL? command for simultaneous voltage and current measurement
            logger.debug("Sending MEAS:ALL? command for simultaneous measurements")
            response = await self._send_command("MEAS:ALL?")
            logger.debug(f"Raw MEAS:ALL? response: '{response}'")

            if response is None:
                logger.error("MEAS:ALL? command returned None response")
                raise HardwareOperationError(
                    "oda_power", "get_all_measurements", "No response from MEAS:ALL? command"
                )

            # Parse response format: "voltage,current" e.g. "10.0000,1.0000"
            response_clean = response.strip()
            logger.debug(f"Cleaned response: '{response_clean}' (length: {len(response_clean)})")

            values = response_clean.split(",")
            logger.debug(f"Split values: {values} (count: {len(values)})")

            if len(values) != 2:
                logger.error(
                    f"Invalid MEAS:ALL? response format. Expected 2 values, got {len(values)}"
                )
                raise HardwareOperationError(
                    "oda_power",
                    "get_all_measurements",
                    f"Unexpected MEAS:ALL? response format: '{response}'. Expected 'voltage,current'",
                )

            try:
                voltage = float(values[0])
                current = float(values[1])
                logger.debug(f"Parsed values - Voltage: {voltage}, Current: {current}")
            except (ValueError, IndexError) as e:
                logger.error(f"Failed to parse voltage/current values: {values}, error: {e}")
                raise

            power = voltage * current

            logger.info(
                f"⚡ MEAS:ALL? → \033[32mV:{voltage:.4f}V\033[0m \033[93mI:{current:.4f}A\033[0m \033[31mP:{power:.4f}W\033[0m"
            )

            return {"voltage": voltage, "current": current, "power": power}

        except ValueError as e:
            logger.error(
                f"Failed to parse MEAS:ALL? response, trying fallback individual measurements: {e}"
            )
            return await self._get_measurements_fallback()
        except HardwareOperationError as e:
            logger.error(f"MEAS:ALL? command failed, trying fallback individual measurements: {e}")
            return await self._get_measurements_fallback()
        except TCPError as e:
            logger.error(
                f"TCP error during MEAS:ALL?, trying fallback individual measurements: {e}"
            )
            return await self._get_measurements_fallback()
        except Exception as e:
            logger.error(
                f"Unexpected error during MEAS:ALL?, trying fallback individual measurements: {e}"
            )
            return await self._get_measurements_fallback()

    async def _get_measurements_fallback(self) -> Dict[str, float]:
        """
        Fallback method to get measurements using individual commands

        Used when MEAS:ALL? command fails or returns invalid response.
        Makes separate calls for voltage and current measurements.

        Returns:
            Dictionary containing voltage, current, and calculated power

        Raises:
            HardwareOperationError: If individual measurements also fail
        """
        try:
            logger.info("Using fallback individual measurements (MEAS:VOLT? + MEAS:CURR?)")

            # Get voltage and current separately
            voltage = await self.get_voltage()
            current = await self.get_current()
            power = voltage * current

            logger.info(
                f"Fallback measurements - Voltage: {voltage:.4f}V, Current: {current:.4f}A, Power: {power:.4f}W"
            )

            return {"voltage": voltage, "current": current, "power": power}

        except Exception as e:
            logger.error(f"Fallback individual measurements also failed: {e}")
            raise HardwareOperationError("oda_power", "_get_measurements_fallback", str(e)) from e
