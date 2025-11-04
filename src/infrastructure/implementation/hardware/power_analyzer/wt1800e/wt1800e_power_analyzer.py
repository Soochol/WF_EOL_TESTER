"""
Yokogawa WT1800E Power Analyzer Service

Implementation for Yokogawa WT1800E power analyzer hardware.
Uses SCPI commands over TCP/IP for power measurement.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.interfaces.hardware.power_analyzer import PowerAnalyzerService
from domain.exceptions import HardwareConnectionError, HardwareOperationError
from driver.tcp.communication import TCPCommunication
from driver.tcp.exceptions import TCPError


class WT1800EPowerAnalyzer(PowerAnalyzerService):
    """Yokogawa WT1800E power analyzer service"""

    def __init__(
        self,
        host: str = "192.168.1.100",
        port: int = 10001,
        timeout: float = 5.0,
        element: int = 1,
    ):
        """
        Initialize WT1800E Power Analyzer

        Args:
            host: IP address of WT1800E
            port: TCP port number (default: 10001)
            timeout: Connection timeout in seconds
            element: Measurement element/channel number (1-6)
        """
        # Connection parameters
        self._host = host
        self._port = port
        self._timeout = timeout
        self._element = element

        # State initialization
        self._is_connected = False
        self._device_identity: Optional[str] = None
        self._tcp_comm: Optional[TCPCommunication] = None

        logger.info(
            f"WT1800EPowerAnalyzer initialized (Element {self._element}, {self._host}:{self._port})"
        )

    async def connect(self) -> None:
        """
        Connect to WT1800E power analyzer

        Raises:
            HardwareConnectionError: If connection fails
        """
        try:
            # Create TCP connection
            self._tcp_comm = TCPCommunication(self._host, self._port, self._timeout)

            logger.info(
                f"Connecting to WT1800E Power Analyzer at {self._host}:{self._port} "
                f"(Element {self._element})"
            )

            await self._tcp_comm.connect()

            # Test connection and get device identity
            response = await self._send_command("*IDN?")
            logger.info(f"WT1800E *IDN? response: {response!r}")

            if response and len(response.strip()) > 0:
                self._is_connected = True
                self._device_identity = response

                # Clear any error status
                await self._send_command("*CLS")
                logger.debug("WT1800E error status cleared with *CLS")

                # Small delay for command processing
                await asyncio.sleep(0.2)

                logger.info(f"WT1800E Power Analyzer connected successfully: {response}")
            else:
                logger.warning(
                    "WT1800E identification failed - no valid *IDN? response"
                )
                raise HardwareConnectionError(
                    "wt1800e",
                    "Device identification failed - no valid *IDN? response",
                )

        except TCPError as e:
            logger.error(f"Failed to connect to WT1800E Power Analyzer: {e}")
            self._is_connected = False
            raise HardwareConnectionError("wt1800e", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error during WT1800E connection: {e}")
            self._is_connected = False
            raise HardwareConnectionError("wt1800e", str(e)) from e

    async def disconnect(self) -> None:
        """
        Disconnect from WT1800E power analyzer

        Note:
            Always completes cleanup even if errors occur to prevent resource leaks
        """
        disconnect_error = None

        try:
            if self._tcp_comm:
                try:
                    await self._tcp_comm.disconnect()
                    logger.debug("WT1800E TCP connection disconnect completed")
                except Exception as tcp_error:
                    disconnect_error = tcp_error
                    logger.warning(f"Error during WT1800E TCP disconnect: {tcp_error}")

        except Exception as e:
            logger.error(f"Unexpected error disconnecting WT1800E: {e}")
            disconnect_error = e

        finally:
            # Always perform cleanup
            self._tcp_comm = None
            self._is_connected = False

            if disconnect_error:
                logger.warning(
                    f"WT1800E Power Analyzer disconnected with errors: {disconnect_error}"
                )
            else:
                logger.info("WT1800E Power Analyzer disconnected successfully")

    async def is_connected(self) -> bool:
        """
        Check if power analyzer is connected

        Returns:
            True if connected, False otherwise
        """
        return (
            self._is_connected
            and self._tcp_comm is not None
            and self._tcp_comm.is_connected
        )

    async def get_measurements(self) -> Dict[str, float]:
        """
        Get all measurements at once (voltage, current, power)

        Uses SCPI commands to retrieve voltage, current, and power measurements
        from the specified element.

        Returns:
            Dictionary containing:
            - 'voltage': Measured voltage in volts
            - 'current': Measured current in amperes
            - 'power': Measured power in watts

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If measurement fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            # Query voltage (U<element>)
            voltage_cmd = f":NUMeric:NORMal:VALue? U{self._element}"
            voltage_response = await self._send_command(voltage_cmd)
            voltage = self._parse_float_response(voltage_response, "voltage")

            # Query current (I<element>)
            current_cmd = f":NUMeric:NORMal:VALue? I{self._element}"
            current_response = await self._send_command(current_cmd)
            current = self._parse_float_response(current_response, "current")

            # Query power (P<element>)
            power_cmd = f":NUMeric:NORMal:VALue? P{self._element}"
            power_response = await self._send_command(power_cmd)
            power = self._parse_float_response(power_response, "power")

            logger.debug(
                f"WT1800E measurements (Element {self._element}) - "
                f"Voltage: {voltage:.4f}V, Current: {current:.4f}A, Power: {power:.4f}W"
            )

            return {
                "voltage": voltage,
                "current": current,
                "power": power,
            }

        except TCPError as e:
            logger.error(f"Failed to get WT1800E measurements: {e}")
            raise HardwareOperationError("wt1800e", "get_measurements", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error getting WT1800E measurements: {e}")
            raise HardwareOperationError("wt1800e", "get_measurements", str(e)) from e

    async def get_device_identity(self) -> str:
        """
        Get device identification string

        Returns:
            Device identification string from *IDN? command

        Raises:
            HardwareConnectionError: If not connected
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        if self._device_identity:
            return self._device_identity

        # Query device identity if not cached
        try:
            response = await self._send_command("*IDN?")
            self._device_identity = response
            return response
        except Exception as e:
            logger.error(f"Failed to get WT1800E device identity: {e}")
            raise HardwareOperationError("wt1800e", "get_device_identity", str(e)) from e

    async def _send_command(self, command: str) -> str:
        """
        Send SCPI command to WT1800E and receive response

        Args:
            command: SCPI command string

        Returns:
            Response string from device

        Raises:
            TCPError: If communication fails
        """
        if not self._tcp_comm:
            raise TCPError("TCP communication not initialized")

        # SCPI commands should end with newline
        if not command.endswith("\n"):
            command = command + "\n"

        # Send command
        await self._tcp_comm.send_command(command)

        # If command is a query (ends with ?), read response
        if "?" in command:
            response = await self._tcp_comm.read_response()
            return response.strip()

        # Non-query commands don't return responses
        return ""

    def _parse_float_response(self, response: str, parameter_name: str) -> float:
        """
        Parse float value from SCPI response

        Args:
            response: Response string from device
            parameter_name: Name of parameter for error messages

        Returns:
            Parsed float value

        Raises:
            HardwareOperationError: If parsing fails
        """
        try:
            # Remove any whitespace and parse
            value = float(response.strip())
            return value
        except ValueError as e:
            logger.error(
                f"Failed to parse {parameter_name} response '{response}': {e}"
            )
            raise HardwareOperationError(
                "wt1800e",
                "parse_response",
                f"Invalid {parameter_name} response: {response}",
            ) from e
