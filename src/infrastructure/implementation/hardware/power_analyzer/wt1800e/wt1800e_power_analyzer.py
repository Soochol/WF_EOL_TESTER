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
        voltage_range: Optional[str] = None,
        current_range: Optional[str] = None,
        auto_range: bool = True,
        line_filter: Optional[str] = None,
        frequency_filter: Optional[str] = None,
    ):
        """
        Initialize WT1800E Power Analyzer

        Args:
            host: IP address of WT1800E
            port: TCP port number (default: 10001)
            timeout: Connection timeout in seconds
            element: Measurement element/channel number (1-6)
            voltage_range: Voltage range (e.g., "300V", "600V") - None for auto-range
            current_range: Current range (e.g., "5A", "10A") - None for auto-range
            auto_range: Enable automatic range adjustment
            line_filter: Line filter frequency (e.g., "10KHZ") - None for default
            frequency_filter: Frequency filter (e.g., "1HZ") - None for default
        """
        # Connection parameters
        self._host = host
        self._port = port
        self._timeout = timeout
        self._element = element

        # Input range configuration
        self._voltage_range = voltage_range
        self._current_range = current_range
        self._auto_range = auto_range

        # Filter configuration
        self._line_filter = line_filter
        self._frequency_filter = frequency_filter

        # State initialization
        self._is_connected = False
        self._device_identity: Optional[str] = None
        self._tcp_comm: Optional[TCPCommunication] = None

        logger.info(
            f"WT1800EPowerAnalyzer initialized (Element {self._element}, {self._host}:{self._port}, "
            f"Auto-range: {self._auto_range})"
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

                # Enable Remote mode to lock out front panel (Guide 2.1)
                await self._send_command(":COMMunicate:REMote ON")
                logger.debug("WT1800E Remote mode enabled")

                # Configure input ranges (Guide 4.1, 7.2)
                await self.configure_input(
                    voltage_range=self._voltage_range,
                    current_range=self._current_range,
                    auto_range=self._auto_range,
                )

                # Configure filters if specified (Guide 4.1.3)
                if self._line_filter or self._frequency_filter:
                    await self.configure_filter(
                        line_filter=self._line_filter,
                        frequency_filter=self._frequency_filter,
                    )

                # Check for any initialization errors
                errors = await self._check_errors()
                if errors:
                    logger.warning(f"WT1800E initialization completed with warnings: {errors}")

                logger.info(f"WT1800E Power Analyzer connected and configured successfully: {response}")
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

        Uses optimized single SCPI query for all measurements (Guide 4.2.2, 5.2).
        This reduces TCP round-trips from 3 to 1 for ~3x performance improvement.

        Returns:
            Dictionary containing:
            - 'voltage': Measured voltage in volts (RMS)
            - 'current': Measured current in amperes (RMS)
            - 'power': Measured power in watts (active power)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If measurement fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            # Single query for all measurements (Guide 4.2.2)
            # Format: :MEASure:NORMal:VALue? URMS,<element>,IRMS,<element>,P,<element>
            # Response: voltage,current,power (e.g., "220.5E+00,10.2E+00,2.25E+03")
            cmd = f":MEASure:NORMal:VALue? URMS,{self._element},IRMS,{self._element},P,{self._element}"
            response = await self._send_command(cmd)

            # Parse comma-separated values
            values = [float(x.strip()) for x in response.split(',')]

            if len(values) != 3:
                raise HardwareOperationError(
                    "wt1800e",
                    "get_measurements",
                    f"Expected 3 values (voltage, current, power), got {len(values)}: {response}",
                )

            voltage, current, power = values

            logger.debug(
                f"WT1800E measurements (Element {self._element}) - "
                f"Voltage: {voltage:.4f}V, Current: {current:.4f}A, Power: {power:.4f}W"
            )

            # Check for errors after measurement (Guide 6.4)
            errors = await self._check_errors()
            if errors:
                logger.warning(f"WT1800E measurement completed with errors: {errors}")

            return {
                "voltage": voltage,
                "current": current,
                "power": power,
            }

        except TCPError as e:
            logger.error(f"Failed to get WT1800E measurements: {e}")
            await self._check_errors()  # Check for device errors
            raise HardwareOperationError("wt1800e", "get_measurements", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error getting WT1800E measurements: {e}")
            await self._check_errors()  # Check for device errors
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
            response = await self._tcp_comm.receive_response()
            return response.strip()

        # Non-query commands don't return responses
        return ""

    async def configure_input(
        self,
        voltage_range: Optional[str] = None,
        current_range: Optional[str] = None,
        auto_range: bool = True,
    ) -> None:
        """
        Configure voltage and current input ranges (Guide 4.1.1, 4.1.2)

        Args:
            voltage_range: Voltage range (e.g., "15V", "30V", "60V", "150V", "300V", "600V", "1000V")
            current_range: Current range (e.g., "1A", "2A", "5A", "10A", "20A", "50A")
            auto_range: Enable automatic range adjustment (recommended)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If configuration fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            if auto_range:
                # Enable auto-range for voltage and current (Guide 4.1.1, 4.1.2)
                await self._send_command(":INPut:VOLTage:AUTO:ALL ON")
                await self._send_command(":INPut:CURRent:AUTO:ALL ON")
                logger.info("WT1800E auto-range enabled for voltage and current")
            else:
                # Set manual ranges
                if voltage_range:
                    cmd = f":INPut:VOLTage:RANGe:ELEMent{self._element} {voltage_range}"
                    await self._send_command(cmd)
                    logger.info(f"WT1800E voltage range set to {voltage_range}")

                if current_range:
                    cmd = f":INPut:CURRent:RANGe:ELEMent{self._element} {current_range}"
                    await self._send_command(cmd)
                    logger.info(f"WT1800E current range set to {current_range}")

            # Check for errors
            errors = await self._check_errors()
            if errors:
                logger.error(f"WT1800E input configuration errors: {errors}")
                raise HardwareOperationError(
                    "wt1800e",
                    "configure_input",
                    f"Configuration failed with errors: {errors}",
                )

        except Exception as e:
            logger.error(f"Failed to configure WT1800E input: {e}")
            raise HardwareOperationError("wt1800e", "configure_input", str(e)) from e

    async def configure_filter(
        self,
        line_filter: Optional[str] = None,
        frequency_filter: Optional[str] = None,
    ) -> None:
        """
        Configure measurement filters (Guide 4.1.3)

        Args:
            line_filter: Line filter frequency (e.g., "500HZ", "1KHZ", "10KHZ", "100KHZ")
            frequency_filter: Frequency filter (e.g., "0.5HZ", "1HZ", "10HZ", "100HZ", "1KHZ")

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If configuration fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            if line_filter:
                await self._send_command(f":INPut:FILTer:LINE:ALL {line_filter}")
                logger.info(f"WT1800E line filter set to {line_filter}")

            if frequency_filter:
                await self._send_command(f":INPut:FILTer:FREQuency:ALL {frequency_filter}")
                logger.info(f"WT1800E frequency filter set to {frequency_filter}")

            # Check for errors
            errors = await self._check_errors()
            if errors:
                logger.error(f"WT1800E filter configuration errors: {errors}")
                raise HardwareOperationError(
                    "wt1800e",
                    "configure_filter",
                    f"Configuration failed with errors: {errors}",
                )

        except Exception as e:
            logger.error(f"Failed to configure WT1800E filters: {e}")
            raise HardwareOperationError("wt1800e", "configure_filter", str(e)) from e

    async def _check_errors(self) -> list[str]:
        """
        Check error queue after command execution (Guide 6.4)

        Queries the :SYSTem:ERRor? command repeatedly until error code 0 is returned.
        This follows the WT1800E Programming Guide best practices for error handling.

        Returns:
            List of error strings found in the queue

        Raises:
            TCPError: If communication fails
        """
        errors = []
        max_iterations = 10  # Prevent infinite loop

        for _ in range(max_iterations):
            try:
                response = await self._send_command(":SYSTem:ERRor?")

                # Parse error response: "code,message" format
                # Example: '0,"No error"' or '-113,"Undefined header"'
                if response.startswith('0'):
                    # No error (code 0)
                    break

                # Error found
                errors.append(response)
                logger.warning(f"WT1800E error detected: {response}")

            except Exception as e:
                logger.error(f"Failed to check WT1800E errors: {e}")
                break

        return errors

    async def setup_integration(
        self,
        mode: str = "normal",
        timer: int = 3600,
    ) -> None:
        """
        Configure integration (energy) measurement (Guide 4.4, 7.3)

        Args:
            mode: Integration mode - "normal" or "continuous"
            timer: Integration timer in seconds (1-36000, max 10 hours)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If configuration fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            # Set integration mode
            mode_upper = mode.upper()
            if mode_upper not in ["NORMAL", "CONTINUOUS"]:
                raise HardwareOperationError(
                    "wt1800e",
                    "setup_integration",
                    f"Invalid mode '{mode}'. Must be 'normal' or 'continuous'",
                )

            await self._send_command(f":INTEGrate:MODE {mode_upper}")
            logger.info(f"WT1800E integration mode set to {mode_upper}")

            # Set integration timer
            if not 1 <= timer <= 36000:
                raise HardwareOperationError(
                    "wt1800e",
                    "setup_integration",
                    f"Timer {timer}s out of range (1-36000 seconds)",
                )

            await self._send_command(f":INTEGrate:TIMer {timer}")
            logger.info(f"WT1800E integration timer set to {timer} seconds")

            # Check for errors
            errors = await self._check_errors()
            if errors:
                logger.error(f"WT1800E integration setup errors: {errors}")
                raise HardwareOperationError(
                    "wt1800e",
                    "setup_integration",
                    f"Configuration failed with errors: {errors}",
                )

        except Exception as e:
            logger.error(f"Failed to setup WT1800E integration: {e}")
            raise HardwareOperationError("wt1800e", "setup_integration", str(e)) from e

    async def start_integration(self) -> None:
        """
        Start integration measurement (Guide 4.4)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If operation fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            await self._send_command(":INTEGrate:STARt")
            logger.info("WT1800E integration started")

            # Check for errors
            errors = await self._check_errors()
            if errors:
                raise HardwareOperationError(
                    "wt1800e",
                    "start_integration",
                    f"Start failed with errors: {errors}",
                )

        except Exception as e:
            logger.error(f"Failed to start WT1800E integration: {e}")
            raise HardwareOperationError("wt1800e", "start_integration", str(e)) from e

    async def stop_integration(self) -> None:
        """
        Stop integration measurement (Guide 4.4)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If operation fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            await self._send_command(":INTEGrate:STOP")
            logger.info("WT1800E integration stopped")

            # Check for errors
            errors = await self._check_errors()
            if errors:
                raise HardwareOperationError(
                    "wt1800e",
                    "stop_integration",
                    f"Stop failed with errors: {errors}",
                )

        except Exception as e:
            logger.error(f"Failed to stop WT1800E integration: {e}")
            raise HardwareOperationError("wt1800e", "stop_integration", str(e)) from e

    async def reset_integration(self) -> None:
        """
        Reset integration measurement (Guide 4.4)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If operation fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            await self._send_command(":INTEGrate:RESet")
            logger.info("WT1800E integration reset")

            # Check for errors
            errors = await self._check_errors()
            if errors:
                raise HardwareOperationError(
                    "wt1800e",
                    "reset_integration",
                    f"Reset failed with errors: {errors}",
                )

        except Exception as e:
            logger.error(f"Failed to reset WT1800E integration: {e}")
            raise HardwareOperationError("wt1800e", "reset_integration", str(e)) from e

    async def get_integration_time(self) -> Dict[str, Optional[str]]:
        """
        Get integration elapsed time (Guide 4.4)

        Returns:
            Dictionary containing:
            - 'start': Start time string
            - 'end': End time string (or None if not completed)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If query fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            response = await self._send_command(":INTEGrate:RTIMe?")

            # Parse response: "start_time,end_time" or "start_time,"
            parts = response.split(',')
            result = {
                'start': parts[0].strip() if len(parts) > 0 else None,
                'end': parts[1].strip() if len(parts) > 1 and parts[1].strip() else None,
            }

            logger.debug(f"WT1800E integration time: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to get WT1800E integration time: {e}")
            raise HardwareOperationError("wt1800e", "get_integration_time", str(e)) from e

    async def get_integration_data(self, element: Optional[int] = None) -> Dict[str, float]:
        """
        Get integration (energy) measurement data (Guide 4.4, 7.3)

        Args:
            element: Measurement element (1-6). If None, uses configured element.

        Returns:
            Dictionary containing:
            - 'active_energy_wh': Active energy in Wh (WP)
            - 'apparent_energy_vah': Apparent energy in VAh (WS)
            - 'reactive_energy_varh': Reactive energy in varh (WQ)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If measurement fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        elem = element if element is not None else self._element

        try:
            # Query all integration values in one command
            # Format: :INTEGrate:VALue? WP,<element>,WS,<element>,WQ,<element>
            cmd = f":INTEGrate:VALue? WP,{elem},WS,{elem},WQ,{elem}"
            response = await self._send_command(cmd)

            # Parse comma-separated values
            values = [float(x.strip()) for x in response.split(',')]

            if len(values) != 3:
                raise HardwareOperationError(
                    "wt1800e",
                    "get_integration_data",
                    f"Expected 3 values (WP, WS, WQ), got {len(values)}: {response}",
                )

            active_wh, apparent_vah, reactive_varh = values

            logger.debug(
                f"WT1800E integration data (Element {elem}) - "
                f"Active: {active_wh:.4f}Wh, Apparent: {apparent_vah:.4f}VAh, Reactive: {reactive_varh:.4f}varh"
            )

            # Check for errors
            errors = await self._check_errors()
            if errors:
                logger.warning(f"WT1800E integration data query completed with errors: {errors}")

            return {
                "active_energy_wh": active_wh,
                "apparent_energy_vah": apparent_vah,
                "reactive_energy_varh": reactive_varh,
            }

        except Exception as e:
            logger.error(f"Failed to get WT1800E integration data: {e}")
            await self._check_errors()
            raise HardwareOperationError("wt1800e", "get_integration_data", str(e)) from e

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
