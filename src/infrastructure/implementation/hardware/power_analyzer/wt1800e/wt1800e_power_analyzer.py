"""
Yokogawa WT1800E Power Analyzer Service

Implementation for Yokogawa WT1800E power analyzer hardware.
Uses SCPI commands over TCP/IP for power measurement.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.interfaces.hardware.power_analyzer import PowerAnalyzerService
from domain.exceptions import HardwareConnectionError, HardwareOperationError
from driver.visa.constants import INTERFACE_GPIB, INTERFACE_TCP, INTERFACE_USB
from driver.visa.exceptions import VISAConnectionError, VISAError, VISATimeoutError
from driver.visa.visa_communication import VISACommunication


class WT1800EPowerAnalyzer(PowerAnalyzerService):
    """Yokogawa WT1800E power analyzer service"""

    def __init__(
        self,
        interface_type: str = INTERFACE_TCP,
        # TCP/IP parameters
        host: str = "192.168.1.100",
        port: int = 10001,
        # USB parameters
        usb_vendor_id: Optional[str] = None,
        usb_model_code: Optional[str] = None,
        usb_serial_number: Optional[str] = None,
        # GPIB parameters
        gpib_board: int = 0,
        gpib_address: int = 7,
        # Common parameters
        timeout: float = 5.0,
        element: int = 1,
        voltage_range: Optional[str] = None,
        current_range: Optional[str] = None,
        auto_range: bool = True,
        line_filter: Optional[str] = None,
        frequency_filter: Optional[str] = None,
        # External Current Sensor parameters
        external_current_sensor_enabled: bool = False,
        external_current_sensor_voltage_range: Optional[str] = None,
        external_current_sensor_scaling_ratio: Optional[int] = None,
    ):
        """
        Initialize WT1800E Power Analyzer with PyVISA

        Args:
            interface_type: Connection interface ('tcp', 'usb', 'gpib')
            host: IP address of WT1800E (for TCP)
            port: TCP port number (default: 10001, for TCP)
            usb_vendor_id: USB vendor ID (for USB, default: Yokogawa 0x0B21)
            usb_model_code: USB model code (for USB, default: WT1800E 0x0039)
            usb_serial_number: USB serial number (for USB, None = auto-detect)
            gpib_board: GPIB board number (for GPIB)
            gpib_address: GPIB device address (for GPIB)
            timeout: Connection timeout in seconds
            element: Measurement element/channel number (1-6)
            voltage_range: Voltage range (e.g., "300V", "600V") - None for auto-range
            current_range: Current range (e.g., "5A", "10A") - None for auto-range
            auto_range: Enable automatic range adjustment
            line_filter: Line filter frequency (e.g., "10KHZ") - None for default
            frequency_filter: Frequency filter (e.g., "1HZ") - None for default
            external_current_sensor_enabled: Enable external current sensor
            external_current_sensor_voltage_range: Sensor voltage range (e.g., "1V")
            external_current_sensor_scaling_ratio: Scaling ratio (e.g., 100 for 1V=100A)
        """
        # Connection interface
        self._interface_type = interface_type

        # TCP/IP parameters
        self._host = host
        self._port = port

        # USB parameters
        self._usb_vendor_id = usb_vendor_id
        self._usb_model_code = usb_model_code
        self._usb_serial_number = usb_serial_number

        # GPIB parameters
        self._gpib_board = gpib_board
        self._gpib_address = gpib_address

        # Common parameters
        self._timeout = timeout
        self._element = element

        # Input range configuration
        self._voltage_range = voltage_range
        self._current_range = current_range
        self._auto_range = auto_range

        # Filter configuration
        self._line_filter = line_filter
        self._frequency_filter = frequency_filter

        # External Current Sensor configuration
        self._external_current_sensor_enabled = external_current_sensor_enabled
        self._external_current_sensor_voltage_range = external_current_sensor_voltage_range
        self._external_current_sensor_scaling_ratio = external_current_sensor_scaling_ratio

        # State initialization
        self._is_connected = False
        self._device_identity: Optional[str] = None
        self._visa_comm: Optional[VISACommunication] = None

        # Log initialization
        conn_info = self._get_connection_info()
        logger.info(
            f"WT1800EPowerAnalyzer initialized (Element {self._element}, "
            f"Interface: {self._interface_type.upper()}, {conn_info}, "
            f"Auto-range: {self._auto_range})"
        )

    def _get_connection_info(self) -> str:
        """Get connection information string for logging"""
        if self._interface_type == INTERFACE_TCP:
            return f"TCP {self._host}:{self._port}"
        elif self._interface_type == INTERFACE_USB:
            serial = self._usb_serial_number or "auto-detect"
            return f"USB {self._usb_vendor_id}:{self._usb_model_code} (SN: {serial})"
        elif self._interface_type == INTERFACE_GPIB:
            return f"GPIB{self._gpib_board}::{self._gpib_address}"
        else:
            return "Unknown"

    async def connect(self) -> None:
        """
        Connect to WT1800E power analyzer via PyVISA

        Raises:
            HardwareConnectionError: If connection fails
        """
        try:
            # Create VISA connection
            self._visa_comm = VISACommunication(
                interface_type=self._interface_type,
                tcp_host=self._host,
                tcp_port=self._port,
                usb_vendor_id=self._usb_vendor_id,
                usb_model_code=self._usb_model_code,
                usb_serial_number=self._usb_serial_number,
                gpib_board=self._gpib_board,
                gpib_address=self._gpib_address,
                timeout=self._timeout,
            )

            conn_info = self._get_connection_info()
            logger.info(
                f"Connecting to WT1800E Power Analyzer via {self._interface_type.upper()} "
                f"({conn_info}, Element {self._element})"
            )

            await self._visa_comm.connect()

            # Test connection and get device identity
            response = await self._send_command("*IDN?")
            logger.info(f"WT1800E *IDN? response: {response!r}")

            if response and len(response.strip()) > 0:
                self._is_connected = True
                self._device_identity = response

                # Stop and reset any running integration to allow configuration changes
                # Error 813: "Cannot be set while integration is running"
                try:
                    await self._send_command(":INTEGrate:STOP")
                    await self._send_command(":INTEGrate:RESet")
                    logger.debug("WT1800E integration stopped and reset")
                except Exception:
                    # Ignore errors - integration may not have been running
                    pass

                # Clear any error status (including error 844 from STOP command)
                await self._send_command("*CLS")
                logger.debug("WT1800E error status cleared with *CLS")

                # Longer delay to ensure integration state change completes
                await asyncio.sleep(0.5)

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

                # Configure external current sensor if enabled (Guide 5.3)
                if self._external_current_sensor_enabled:
                    if (
                        self._external_current_sensor_voltage_range
                        and self._external_current_sensor_scaling_ratio
                    ):
                        await self.configure_external_current_sensor(
                            voltage_range=self._external_current_sensor_voltage_range,
                            scaling_ratio=self._external_current_sensor_scaling_ratio,
                        )
                    else:
                        logger.warning(
                            "External current sensor enabled but voltage_range or scaling_ratio not specified. "
                            "Skipping sensor configuration."
                        )

                # Configure NUMERIC display items for WT1806 compatibility
                # WT1806 uses :NUMeric commands instead of :MEASure
                await self._configure_numeric_items()

                # Check for any initialization errors
                errors = await self._check_errors()
                if errors:
                    logger.warning(f"WT1800E initialization completed with warnings: {errors}")

                logger.info(
                    f"WT1800E Power Analyzer connected and configured successfully: {response}"
                )
            else:
                logger.warning("WT1800E identification failed - no valid *IDN? response")
                raise HardwareConnectionError(
                    "wt1800e",
                    "Device identification failed - no valid *IDN? response",
                )

        except (VISAError, VISAConnectionError) as e:
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
            if self._visa_comm:
                try:
                    await self._visa_comm.disconnect()
                    logger.debug("WT1800E VISA connection disconnect completed")
                except Exception as visa_error:
                    disconnect_error = visa_error
                    logger.warning(f"Error during WT1800E VISA disconnect: {visa_error}")

        except Exception as e:
            logger.error(f"Unexpected error disconnecting WT1800E: {e}")
            disconnect_error = e

        finally:
            # Always perform cleanup
            self._visa_comm = None
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
        return self._is_connected and self._visa_comm is not None and self._visa_comm.is_connected

    async def get_measurements(self) -> Dict[str, float]:
        """
        Get all measurements at once (voltage, current, power)

        Uses :NUMeric commands for WT1806 compatibility, with fallback to :MEASure.
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
            # Try :NUMeric command first (WT1806 compatibility)
            # Response contains 15 values, ITEM1-3 are V, I, P (configured in _configure_numeric_items)
            try:
                response = await self._send_command(":NUMeric:NORMal:VALue?")
                values = [float(x.strip()) for x in response.split(",")]

                # Extract first 3 values (ITEM1=V, ITEM2=I, ITEM3=P)
                if len(values) >= 3:
                    voltage, current, power = values[0], values[1], values[2]
                    logger.debug(
                        f"WT1800E measurements via :NUMeric (Element {self._element}) - "
                        f"Voltage: {voltage:.4f}V, Current: {current:.4f}A, Power: {power:.4f}W"
                    )

                    return {
                        "voltage": voltage,
                        "current": current,
                        "power": power,
                    }
                else:
                    logger.warning(
                        f":NUMeric command returned {len(values)} values, expected at least 3"
                    )
                    raise ValueError("Insufficient values from :NUMeric command")

            except Exception as numeric_error:
                logger.debug(f":NUMeric command failed: {numeric_error}, trying :MEASure")

                # Fallback to :MEASure command (for WT1800E models)
                # Format: :MEASure:NORMal:VALue? URMS,<element>,IRMS,<element>,P,<element>
                # Response: voltage,current,power (e.g., "220.5E+00,10.2E+00,2.25E+03")
                cmd = f":MEASure:NORMal:VALue? URMS,{self._element},IRMS,{self._element},P,{self._element}"
                response = await self._send_command(cmd)

                # Parse comma-separated values
                values = [float(x.strip()) for x in response.split(",")]

                if len(values) != 3:
                    raise HardwareOperationError(
                        "wt1800e",
                        "get_measurements",
                        f"Expected 3 values (voltage, current, power), got {len(values)}: {response}",
                    )

                voltage, current, power = values

                logger.debug(
                    f"WT1800E measurements via :MEASure (Element {self._element}) - "
                    f"Voltage: {voltage:.4f}V, Current: {current:.4f}A, Power: {power:.4f}W"
                )

                return {
                    "voltage": voltage,
                    "current": current,
                    "power": power,
                }

        except VISAError as e:
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
        Send SCPI command to WT1800E and receive response via VISA

        Args:
            command: SCPI command string

        Returns:
            Response string from device

        Raises:
            VISAError: If communication fails
        """
        if not self._visa_comm:
            raise VISAConnectionError("wt1800e", "VISA communication not initialized")

        # If command is a query (ends with ?), use query method
        if "?" in command:
            response = await self._visa_comm.query(command)
            return response.strip()
        else:
            # Non-query command, just send
            await self._visa_comm.send_command(command)
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
                # Enable auto-range for voltage (Guide 4.1.1)
                await self._send_command(":INPut:VOLTage:AUTO:ALL ON")

                # Enable auto-range for current ONLY if external sensor is NOT used
                # External sensor conflicts with current range settings
                if not self._external_current_sensor_enabled:
                    await self._send_command(":INPut:CURRent:AUTO:ALL ON")
                    logger.info("WT1800E auto-range enabled for voltage and current")
                else:
                    logger.info(
                        "WT1800E auto-range enabled for voltage (current controlled by external sensor)"
                    )
            else:
                # Set manual ranges
                if voltage_range:
                    cmd = f":INPut:VOLTage:RANGe:ELEMent{self._element} {voltage_range}"
                    await self._send_command(cmd)
                    logger.info(f"WT1800E voltage range set to {voltage_range}")

                # Set current range ONLY if external sensor is NOT used
                # External sensor conflicts with current range settings
                if current_range and not self._external_current_sensor_enabled:
                    cmd = f":INPut:CURRent:RANGe:ELEMent{self._element} {current_range}"
                    await self._send_command(cmd)
                    logger.info(f"WT1800E current range set to {current_range}")
                elif self._external_current_sensor_enabled:
                    logger.info("WT1800E current range skipped (external sensor enabled)")

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

    async def configure_external_current_sensor(
        self,
        voltage_range: str = "1V",
        scaling_ratio: int = 100,
    ) -> None:
        """
        Configure external current sensor (Guide 5.3)

        Configures the WT1800E to use an external current sensor with
        specified voltage range and scaling ratio.

        Example:
            Sensor: 10mV/A, Range: 100A
            → Sensor outputs 1V at 100A
            → voltage_range="1V", scaling_ratio=100

        Args:
            voltage_range: Sensor input voltage range
                          Crest Factor 3: "50mV", "100mV", "200mV", "500mV",
                                          "1V", "2V", "5V", "10V"
                          Crest Factor 6: "25mV", "50mV", "100mV", "250mV",
                                          "500mV", "1V", "2.5V", "5V"
            scaling_ratio: Current scaling ratio (e.g., 100 for 1V = 100A)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If configuration fails

        SCPI Commands:
            :INPUT:CURRENT:RANGE:ELEMENT<x> (EXTernal,<voltage>)
            :INPUT:CURRENT:SRATIO:ELEMENT<x> <ratio>
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            # Parse voltage range to numeric value
            voltage_numeric = voltage_range.upper().replace("V", "").replace("M", "E-3")
            if voltage_numeric == "1":
                voltage_numeric = "1"

            # Set external current sensor using RANGE command with EXTERNAL parameter
            # Command: :INPUT:CURRENT:RANGE:ELEMENT1 (EXTernal, <voltage>)
            # Note: Space after comma is required by WT1800E SCPI parser
            await self._send_command(
                f":INPut:CURRent:RANGe:ELEMent{self._element} (EXTernal, {voltage_numeric})"
            )
            logger.info(
                f"WT1800E external current sensor range set to (EXTernal, {voltage_numeric}) "
                f"(Element {self._element})"
            )

            # Set current scaling ratio
            # Command: :INPUT:CURRENT:SRATIO:ELEMENT1 <ratio>
            await self._send_command(
                f":INPut:CURRent:SRATio:ELEMent{self._element} {scaling_ratio}"
            )
            logger.info(
                f"WT1800E current scaling ratio set to {scaling_ratio} "
                f"(Element {self._element}, {voltage_range} = {scaling_ratio}A)"
            )

            # Check for errors
            errors = await self._check_errors()
            if errors:
                logger.error(f"WT1800E external current sensor configuration errors: {errors}")
                raise HardwareOperationError(
                    "wt1800e",
                    "configure_external_current_sensor",
                    f"Configuration failed with errors: {errors}",
                )

            logger.info(
                f"✅ External current sensor configured: {voltage_range} = {scaling_ratio}A "
                f"(Sensor: {scaling_ratio/10}mV/A)"
            )

        except Exception as e:
            logger.error(f"Failed to configure WT1800E external current sensor: {e}")
            raise HardwareOperationError(
                "wt1800e", "configure_external_current_sensor", str(e)
            ) from e

    async def _configure_numeric_items(self) -> None:
        """
        Configure NUMERIC display items for WT1806 compatibility

        WT1806 models use :NUMeric commands instead of :MEASure commands.
        This configures ITEM1-6 for:
        - ITEM1-3: Instant measurements (voltage, current, power)
        - ITEM4-6: Integration values (WH, AH, TIME)

        Raises:
            HardwareOperationError: If configuration fails
        """
        try:
            # Configure NUMERIC items for instant measurements
            # ITEM1 = Voltage (URMS, Element)
            await self._send_command(f":NUMeric:NORMal:ITEM1 URMS,{self._element}")
            logger.debug(f"WT1800E NUMERIC ITEM1 set to URMS,{self._element}")

            # ITEM2 = Current (IRMS, Element)
            await self._send_command(f":NUMeric:NORMal:ITEM2 IRMS,{self._element}")
            logger.debug(f"WT1800E NUMERIC ITEM2 set to IRMS,{self._element}")

            # ITEM3 = Power (P, Element)
            await self._send_command(f":NUMeric:NORMal:ITEM3 P,{self._element}")
            logger.debug(f"WT1800E NUMERIC ITEM3 set to P,{self._element}")

            # Configure NUMERIC items for integration values
            # ITEM4 = Active Energy (WH, Element)
            await self._send_command(f":NUMeric:NORMal:ITEM4 WH,{self._element}")
            logger.debug(f"WT1800E NUMERIC ITEM4 set to WH,{self._element}")

            # ITEM5 = Charge (AH, Element)
            await self._send_command(f":NUMeric:NORMal:ITEM5 AH,{self._element}")
            logger.debug(f"WT1800E NUMERIC ITEM5 set to AH,{self._element}")

            # ITEM6 = Integration Time (TIME, Element)
            await self._send_command(f":NUMeric:NORMal:ITEM6 TIME,{self._element}")
            logger.debug(f"WT1800E NUMERIC ITEM6 set to TIME,{self._element}")

            # Set number of items to 6
            await self._send_command(":NUMeric:NORMal:NUMber 6")
            logger.debug("WT1800E NUMERIC number of items set to 6")

            logger.info(
                f"WT1800E NUMERIC items configured for Element {self._element} "
                "(URMS, IRMS, P, WH, AH, TIME)"
            )

        except Exception as e:
            logger.error(f"Failed to configure WT1800E NUMERIC items: {e}")
            # Don't raise error - this is for WT1806 compatibility
            # If it fails, we'll fall back to :MEASure commands (for other models)
            logger.warning("NUMERIC configuration failed - will attempt :MEASure commands")

    async def _check_errors(self) -> list[str]:
        """
        Check error queue after command execution (Guide 6.4)

        Queries the :STATUS:ERROR? command (SCPI standard) repeatedly until
        error code 0 is returned. This is compatible with all WT series models
        including WT1806.

        Returns:
            List of error strings found in the queue

        Raises:
            TCPError: If communication fails
        """
        errors = []
        max_iterations = 10  # Prevent infinite loop

        for _ in range(max_iterations):
            try:
                # Use :STATUS:ERROR? (SCPI standard) instead of :SYSTem:ERRor?
                # This is compatible with WT1806 and all WT series models
                response = await self._send_command(":STATUS:ERROR?")

                # Parse error response: "code,message" format
                # Example: '0,"No error"' or '113,"Undefined header"'
                if response.startswith("0"):
                    # No error (code 0)
                    break

                # Error found
                errors.append(response)
                logger.warning(f"WT1800E error detected: {response}")

            except Exception as e:
                logger.error(f"Failed to check WT1800E errors: {e}")
                break

        return errors

    async def configure_integration(
        self,
        mode: str = "NORMAL",
        timer_hours: int = 0,
        timer_minutes: int = 0,
        timer_seconds: int = 0,
        auto_calibration: bool = True,
        current_mode: str = "RMS",
    ) -> None:
        """
        Configure integration (energy) measurement settings

        IMPORTANT: Integration must be stopped before configuration changes.
        This method automatically stops running integration if detected.

        Args:
            mode: Integration mode - "NORMAL", "CONTinuous", "RNORmal", "RCONtinuous"
            timer_hours: Timer hours (0-10000)
            timer_minutes: Timer minutes (0-59)
            timer_seconds: Timer seconds (0-59)
            auto_calibration: Enable automatic calibration
            current_mode: Current integration mode - "RMS", "MEAN", "DC", "RMEAN", "AC"

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If configuration fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            # ========================================================================
            # STEP 1: Check integration state and stop if running
            # ========================================================================
            try:
                state = await self.get_integration_state()
                logger.debug(f"WT1800E integration state before configuration: {state}")

                if state == "START":
                    # Integration is running - must stop before configuration
                    logger.info("Integration is running, stopping before configuration...")
                    await self.stop_integration()

                    # Wait for state change to complete
                    await asyncio.sleep(0.2)

                    # Verify state changed
                    new_state = await self.get_integration_state()
                    logger.debug(f"WT1800E integration state after stop: {new_state}")

            except Exception as state_error:
                logger.warning(f"Could not check integration state: {state_error}")
                # Try to stop anyway as a safety measure
                try:
                    await self._send_command(":INTEGrate:STOP")
                    await asyncio.sleep(0.2)
                except Exception:
                    pass  # Ignore errors - integration may not have been running

            # ========================================================================
            # STEP 2: Reset integration to clear previous state
            # ========================================================================
            try:
                await self._send_command(":INTEGrate:RESet")
                logger.debug("WT1800E integration reset before configuration")
                await asyncio.sleep(0.1)
            except Exception as reset_error:
                logger.warning(f"Integration reset warning: {reset_error}")

            # ========================================================================
            # STEP 3: Clear any error status
            # ========================================================================
            await self._send_command("*CLS")
            logger.debug("WT1800E error status cleared before configuration")

            # Wait for device to be ready for configuration
            await asyncio.sleep(0.3)

            # ========================================================================
            # STEP 4: Apply configuration (original code)
            # ========================================================================

            # Set integration mode
            mode_upper = mode.upper()
            valid_modes = ["NORMAL", "CONTINUOUS", "RNORMAL", "RCONTINUOUS"]
            if mode_upper not in valid_modes:
                raise HardwareOperationError(
                    "wt1800e",
                    "configure_integration",
                    f"Invalid mode '{mode}'. Must be one of {valid_modes}",
                )

            await self._send_command(f":INTEGrate:MODE {mode_upper}")
            logger.info(f"WT1800E integration mode set to {mode_upper}")

            # Set integration timer (hours, minutes, seconds format)
            if not 0 <= timer_hours <= 10000:
                raise HardwareOperationError(
                    "wt1800e",
                    "configure_integration",
                    f"Timer hours {timer_hours} out of range (0-10000)",
                )
            if not 0 <= timer_minutes <= 59:
                raise HardwareOperationError(
                    "wt1800e",
                    "configure_integration",
                    f"Timer minutes {timer_minutes} out of range (0-59)",
                )
            if not 0 <= timer_seconds <= 59:
                raise HardwareOperationError(
                    "wt1800e",
                    "configure_integration",
                    f"Timer seconds {timer_seconds} out of range (0-59)",
                )

            timer_cmd = (
                f":INTEGrate:TIMer{self._element} {timer_hours},{timer_minutes},{timer_seconds}"
            )
            await self._send_command(timer_cmd)
            logger.info(
                f"WT1800E integration timer set to {timer_hours}h {timer_minutes}m {timer_seconds}s"
            )

            # Set auto calibration
            acal_value = "ON" if auto_calibration else "OFF"
            await self._send_command(f":INTEGrate:ACAL {acal_value}")
            logger.info(f"WT1800E integration auto-calibration set to {acal_value}")

            # Set current integration mode
            current_mode_upper = current_mode.upper()
            valid_current_modes = ["RMS", "MEAN", "DC", "RMEAN", "AC"]
            if current_mode_upper not in valid_current_modes:
                raise HardwareOperationError(
                    "wt1800e",
                    "configure_integration",
                    f"Invalid current mode '{current_mode}'. Must be one of {valid_current_modes}",
                )

            await self._send_command(
                f":INTEGrate:QMODe:ELEMent{self._element} {current_mode_upper}"
            )
            logger.info(f"WT1800E integration current mode set to {current_mode_upper}")

            # Check for errors
            errors = await self._check_errors()
            if errors:
                logger.error(f"WT1800E integration configuration errors: {errors}")
                raise HardwareOperationError(
                    "wt1800e",
                    "configure_integration",
                    f"Configuration failed with errors: {errors}",
                )

            logger.info("WT1800E integration configuration completed successfully")

        except Exception as e:
            logger.error(f"Failed to configure WT1800E integration: {e}")
            raise HardwareOperationError("wt1800e", "configure_integration", str(e)) from e

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

            # Filter out non-critical errors during stop operation:
            # - Error 844: Timer expired (integration already stopped) - normal in TIMER mode
            # - Error 813: Config attempted during run - old queue errors, not from STOP
            # - Error 85: Button pressed on device - harmless remote mode lock notification
            non_critical_codes = ["844", "813", "85"]
            critical_errors = [
                e
                for e in errors
                if not any(e.startswith(f"{code},") for code in non_critical_codes)
            ]

            if critical_errors:
                raise HardwareOperationError(
                    "wt1800e",
                    "stop_integration",
                    f"Stop failed with errors: {critical_errors}",
                )

            if errors and not critical_errors:
                logger.debug(
                    f"Integration stopped with {len(errors)} non-critical warnings in error queue"
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

    async def get_integration_time(self) -> Dict[str, Any]:
        """
        Get integration elapsed time with automatic calculation (Guide 4.4)

        Returns:
            Dictionary containing:
            - 'start': Start time string (format: "HH:MM:SS")
            - 'end': End time string (or None if not completed)
            - 'elapsed_time': Calculated elapsed time in seconds

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If query fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            response = await self._send_command(":INTEGrate:RTIMe?")

            # Parse response: "start_time,end_time" or "start_time,"
            parts = response.split(",")
            start_time = parts[0].strip() if len(parts) > 0 else None
            end_time = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None

            # Calculate elapsed time in seconds
            elapsed_seconds = 0.0
            if start_time and end_time:
                try:
                    elapsed_seconds = self._calculate_time_difference(start_time, end_time)
                except Exception as calc_error:
                    logger.warning(
                        f"Failed to calculate elapsed time from '{start_time}' to '{end_time}': {calc_error}"
                    )

            result = {
                "start": start_time,
                "end": end_time,
                "elapsed_time": elapsed_seconds,
            }

            logger.debug(
                f"WT1800E integration time: start={start_time}, end={end_time}, "
                f"elapsed={elapsed_seconds:.2f}s"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to get WT1800E integration time: {e}")
            raise HardwareOperationError("wt1800e", "get_integration_time", str(e)) from e

    def _calculate_time_difference(self, start_time_str: str, end_time_str: str) -> float:
        """
        Calculate time difference in seconds from WT1800E time strings

        Args:
            start_time_str: Start time in "HH:MM:SS" format
            end_time_str: End time in "HH:MM:SS" format

        Returns:
            Elapsed time in seconds

        Raises:
            ValueError: If time format is invalid
        """
        try:
            # Parse time strings (format: "HH:MM:SS")
            start_parts = start_time_str.split(":")
            end_parts = end_time_str.split(":")

            if len(start_parts) != 3 or len(end_parts) != 3:
                raise ValueError(
                    f"Invalid time format. Expected 'HH:MM:SS', got start='{start_time_str}', end='{end_time_str}'"
                )

            # Convert to seconds
            start_seconds = (
                int(start_parts[0]) * 3600 + int(start_parts[1]) * 60 + int(start_parts[2])
            )
            end_seconds = int(end_parts[0]) * 3600 + int(end_parts[1]) * 60 + int(end_parts[2])

            # Calculate difference (handle day rollover if needed)
            elapsed = end_seconds - start_seconds
            if elapsed < 0:
                # Day rollover occurred (end time < start time)
                elapsed += 24 * 3600

            return float(elapsed)

        except (ValueError, IndexError) as e:
            raise ValueError(
                f"Failed to parse time strings: start='{start_time_str}', end='{end_time_str}'"
            ) from e

    async def get_integration_state(self) -> str:
        """
        Get integration status

        Returns:
            Integration state: "RESET", "READY", "START", "STOP", "ERROR", "TIMEUP"

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If query fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            # Note: :INTEGrate:STATe? does NOT take element parameter
            response = await self._send_command(":INTEGrate:STATe?")
            state = response.strip().upper()
            logger.debug(f"WT1800E integration state: {state}")
            return state

        except Exception as e:
            logger.error(f"Failed to get WT1800E integration state: {e}")
            raise HardwareOperationError("wt1800e", "get_integration_state", str(e)) from e

    async def get_integration_values(self) -> Dict[str, float]:
        """
        Get integration (energy) measurement values using :NUMeric commands

        This method reads integration values (WH, AH, TIME) that were configured
        in the NUMERIC items during initialization.

        Returns:
            Dictionary containing:
            - 'voltage': Measured voltage in volts (RMS)
            - 'current': Measured current in amperes (RMS)
            - 'power': Measured power in watts (active power)
            - 'wh': Active energy in Watt-hours (integrated power)
            - 'ah': Charge in Ampere-hours (integrated current)
            - 'time': Integration time in seconds

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If measurement fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("wt1800e", "Power Analyzer is not connected")

        try:
            # Use :NUMeric command to read all configured items
            # Response contains values for ITEM1-6: URMS, IRMS, P, WH, AH, TIME
            response = await self._send_command(":NUMeric:NORMal:VALue?")
            values = [float(x.strip()) for x in response.split(",")]

            # Extract first 6 values
            if len(values) < 6:
                raise HardwareOperationError(
                    "wt1800e",
                    "get_integration_values",
                    f"Expected at least 6 values, got {len(values)}: {response}",
                )

            voltage, current, power, wh, ah, time_seconds = values[0:6]

            logger.debug(
                f"WT1800E integration values (Element {self._element}) - "
                f"V: {voltage:.4f}V, I: {current:.4f}A, P: {power:.4f}W, "
                f"WH: {wh:.6f}Wh, AH: {ah:.6f}Ah, Time: {time_seconds:.1f}s"
            )

            return {
                "voltage": voltage,
                "current": current,
                "power": power,
                "wh": wh,
                "ah": ah,
                "time": time_seconds,
            }

        except Exception as e:
            logger.error(f"Failed to get WT1800E integration values: {e}")
            await self._check_errors()
            raise HardwareOperationError("wt1800e", "get_integration_values", str(e)) from e

    # ========================================================================
    # BACKWARDS COMPATIBILITY WRAPPERS (PowerAnalyzerService interface)
    # ========================================================================

    async def setup_integration(self, mode: str = "normal", timer: int = 3600) -> None:
        """
        Setup integration (energy) measurement parameters (backwards compatibility wrapper)

        This is a compatibility wrapper for the PowerAnalyzerService interface.
        Internally calls configure_integration() with proper parameter format.

        Args:
            mode: Integration mode - "normal" or "continuous"
            timer: Integration timer in seconds (1-36000)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If setup fails
        """
        # Convert total seconds to hours, minutes, seconds
        hours = timer // 3600
        minutes = (timer % 3600) // 60
        seconds = timer % 60

        # Map mode to proper format
        mode_map = {
            "normal": "NORMAL",
            "continuous": "CONTINUOUS",
        }
        integration_mode = mode_map.get(mode.lower(), mode.upper())

        # Call the new configure_integration method
        await self.configure_integration(
            mode=integration_mode,
            timer_hours=hours,
            timer_minutes=minutes,
            timer_seconds=seconds,
            auto_calibration=True,
            current_mode="RMS",
        )

    async def get_integration_data(self, _element: Optional[int] = None) -> Dict[str, float]:
        """
        Get integration (energy) measurement data (backwards compatibility wrapper)

        This is a compatibility wrapper for the PowerAnalyzerService interface.
        Internally calls get_integration_values() and reformats the result.

        Args:
            _element: Measurement element/channel (ignored - uses configured element)

        Returns:
            Dictionary containing:
            - 'active_energy_wh': Active energy in Wh (WP)
            - 'apparent_energy_vah': Apparent energy in VAh (WS)
            - 'reactive_energy_varh': Reactive energy in varh (WQ)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If query fails
        """
        # Get integration values using new method
        values = await self.get_integration_values()

        # Reformat to match interface contract
        # Note: WT1806 only provides WH (active energy) via NUMERIC commands
        # WS and WQ would require additional NUMERIC item configuration
        return {
            "active_energy_wh": values["wh"],
            "apparent_energy_vah": 0.0,  # Not configured in NUMERIC items
            "reactive_energy_varh": 0.0,  # Not configured in NUMERIC items
        }

    # ========================================================================

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
            logger.error(f"Failed to parse {parameter_name} response '{response}': {e}")
            raise HardwareOperationError(
                "wt1800e",
                "parse_response",
                f"Invalid {parameter_name} response: {response}",
            ) from e
