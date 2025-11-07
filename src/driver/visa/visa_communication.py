"""
VISA Communication Driver

Async wrapper for PyVISA supporting TCP/IP, USB-TMC, and GPIB interfaces.
Provides unified interface for instrument communication with automatic
resource string generation.
"""

# Standard library imports
from typing import Optional

# Third-party imports
import asyncio
from loguru import logger
import pyvisa

# Local application imports
from driver.visa.constants import (
    DEFAULT_ENCODING,
    DEFAULT_READ_TERMINATION,
    DEFAULT_TIMEOUT_MS,
    DEFAULT_WRITE_TERMINATION,
    GPIB_INSTR_TEMPLATE,
    INTERFACE_GPIB,
    INTERFACE_TCP,
    INTERFACE_USB,
    TCPIP_INSTR_TEMPLATE,
    USB_INSTR_TEMPLATE,
    WT1800E_MODEL_CODE,
    YOKOGAWA_VENDOR_ID,
)
from driver.visa.exceptions import (
    VISACommunicationError,
    VISAConnectionError,
    VISAResourceNotFoundError,
    VISATimeoutError,
)


class VISACommunication:
    """
    Async VISA communication driver

    Supports multiple interfaces:
    - TCP/IP: SOCKET and INSTR protocols
    - USB: USB-TMC (Test & Measurement Class)
    - GPIB: IEEE 488.2
    """

    def __init__(
        self,
        interface_type: str = INTERFACE_TCP,
        # TCP/IP parameters
        tcp_host: Optional[str] = None,
        tcp_port: Optional[int] = None,
        # USB parameters
        usb_vendor_id: Optional[str] = None,
        usb_model_code: Optional[str] = None,
        usb_serial_number: Optional[str] = None,
        # GPIB parameters
        gpib_board: int = 0,
        gpib_address: int = 7,
        # Common parameters
        timeout: float = DEFAULT_TIMEOUT_MS / 1000.0,
        read_termination: str = DEFAULT_READ_TERMINATION,
        write_termination: str = DEFAULT_WRITE_TERMINATION,
        encoding: str = DEFAULT_ENCODING,
    ):
        """
        Initialize VISA communication

        Args:
            interface_type: Interface type ('tcp', 'usb', 'gpib')
            tcp_host: TCP/IP host address (for TCP interface)
            tcp_port: TCP/IP port number (for TCP interface)
            usb_vendor_id: USB vendor ID hex string (for USB interface)
            usb_model_code: USB model code hex string (for USB interface)
            usb_serial_number: USB serial number (None = auto-detect)
            gpib_board: GPIB board number (for GPIB interface)
            gpib_address: GPIB device address (for GPIB interface)
            timeout: Communication timeout in seconds
            read_termination: Read termination character
            write_termination: Write termination character
            encoding: Character encoding
        """
        self._interface_type = interface_type
        self._tcp_host = tcp_host
        self._tcp_port = tcp_port
        self._usb_vendor_id = usb_vendor_id or YOKOGAWA_VENDOR_ID
        self._usb_model_code = usb_model_code or WT1800E_MODEL_CODE
        self._usb_serial_number = usb_serial_number
        self._gpib_board = gpib_board
        self._gpib_address = gpib_address
        self._timeout = timeout
        self._read_termination = read_termination
        self._write_termination = write_termination
        self._encoding = encoding

        # State
        self._resource_manager: Optional[pyvisa.ResourceManager] = None
        self._instrument: Optional[pyvisa.Resource] = None
        self._resource_string: Optional[str] = None
        self._is_connected = False

    def _generate_resource_string(self) -> str:
        """
        Generate PyVISA resource string based on interface type

        Returns:
            VISA resource string

        Raises:
            VISAConnectionError: If resource string cannot be generated
        """
        if self._interface_type == INTERFACE_TCP:
            if not self._tcp_host:
                raise VISAConnectionError(
                    "TCP",
                    "TCP host is required for TCP interface",
                )
            # Use VXI-11 (INSTR) protocol for WT1800E
            resource_string = TCPIP_INSTR_TEMPLATE.format(
                host=self._tcp_host,
            )
            logger.debug(f"Generated TCP resource string (VXI-11): {resource_string}")
            return resource_string

        elif self._interface_type == INTERFACE_USB:
            # Use serial number if provided, otherwise auto-detect
            serial = self._usb_serial_number or "?*"
            resource_string = USB_INSTR_TEMPLATE.format(
                vendor_id=self._usb_vendor_id,
                model_code=self._usb_model_code,
                serial=serial,
            )
            logger.debug(f"Generated USB resource string: {resource_string}")
            return resource_string

        elif self._interface_type == INTERFACE_GPIB:
            resource_string = GPIB_INSTR_TEMPLATE.format(
                board=self._gpib_board,
                address=self._gpib_address,
            )
            logger.debug(f"Generated GPIB resource string: {resource_string}")
            return resource_string

        else:
            raise VISAConnectionError(
                self._interface_type,
                f"Unsupported interface type: {self._interface_type}",
            )

    async def connect(self) -> None:
        """
        Connect to VISA instrument

        Raises:
            VISAConnectionError: If connection fails
        """
        try:
            # Run blocking VISA operations in executor
            loop = asyncio.get_event_loop()

            # Initialize resource manager
            logger.debug("Initializing PyVISA resource manager (@py backend)")
            self._resource_manager = await loop.run_in_executor(
                None, lambda: pyvisa.ResourceManager("@py")
            )

            # Generate resource string
            self._resource_string = self._generate_resource_string()

            logger.info(
                f"Connecting to VISA instrument: {self._resource_string} "
                f"(timeout: {self._timeout}s)"
            )

            # Open instrument resource
            self._instrument = await loop.run_in_executor(
                None, self._resource_manager.open_resource, self._resource_string
            )

            # Configure timeout (convert seconds to milliseconds)
            self._instrument.timeout = int(self._timeout * 1000)

            # Configure termination characters
            self._instrument.read_termination = self._read_termination
            self._instrument.write_termination = self._write_termination

            # Set encoding
            self._instrument.encoding = self._encoding

            self._is_connected = True
            logger.info(f"VISA instrument connected successfully: {self._resource_string}")

        except pyvisa.errors.VisaIOError as e:
            logger.error(f"VISA connection failed: {e}")
            self._is_connected = False
            raise VISAConnectionError(self._resource_string or "unknown", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error during VISA connection: {e}")
            self._is_connected = False
            raise VISAConnectionError(self._resource_string or "unknown", str(e)) from e

    async def disconnect(self) -> None:
        """
        Disconnect from VISA instrument

        Note:
            Always completes cleanup even if errors occur
        """
        disconnect_error = None

        try:
            if self._instrument:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self._instrument.close)
                    logger.debug("VISA instrument closed")
                except Exception as inst_error:
                    disconnect_error = inst_error
                    logger.warning(f"Error closing VISA instrument: {inst_error}")

            if self._resource_manager:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self._resource_manager.close)
                    logger.debug("VISA resource manager closed")
                except Exception as rm_error:
                    disconnect_error = rm_error
                    logger.warning(f"Error closing resource manager: {rm_error}")

        except Exception as e:
            logger.error(f"Unexpected error disconnecting VISA: {e}")
            disconnect_error = e

        finally:
            # Always perform cleanup
            self._instrument = None
            self._resource_manager = None
            self._is_connected = False

            if disconnect_error:
                logger.warning(f"VISA instrument disconnected with errors: {disconnect_error}")
            else:
                logger.info("VISA instrument disconnected successfully")

    @property
    def is_connected(self) -> bool:
        """
        Check if VISA instrument is connected

        Returns:
            True if connected, False otherwise
        """
        return self._is_connected and self._instrument is not None

    async def send_command(self, command: str) -> None:
        """
        Send command to VISA instrument (write-only)

        Args:
            command: Command string to send

        Raises:
            VISAConnectionError: If not connected
            VISACommunicationError: If write fails
        """
        if not self.is_connected:
            raise VISAConnectionError(
                self._resource_string or "unknown", "Not connected to instrument"
            )

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._instrument.write, command)
            logger.debug(f"VISA command sent: {command.strip()}")

        except pyvisa.errors.VisaIOError as e:
            logger.error(f"VISA write failed: {e}")
            raise VISACommunicationError("write", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error during VISA write: {e}")
            raise VISACommunicationError("write", str(e)) from e

    async def receive_response(self) -> str:
        """
        Receive response from VISA instrument (read-only)

        Returns:
            Response string from instrument

        Raises:
            VISAConnectionError: If not connected
            VISACommunicationError: If read fails
            VISATimeoutError: If read times out
        """
        if not self.is_connected:
            raise VISAConnectionError(
                self._resource_string or "unknown", "Not connected to instrument"
            )

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._instrument.read)
            logger.debug(f"VISA response received: {response.strip()}")
            return response

        except pyvisa.errors.VisaIOError as e:
            if "timeout" in str(e).lower():
                logger.error(f"VISA read timeout: {e}")
                raise VISATimeoutError("read", int(self._timeout * 1000)) from e
            else:
                logger.error(f"VISA read failed: {e}")
                raise VISACommunicationError("read", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error during VISA read: {e}")
            raise VISACommunicationError("read", str(e)) from e

    async def query(self, command: str) -> str:
        """
        Send query command and receive response (write + read)

        Args:
            command: Query command string

        Returns:
            Response string from instrument

        Raises:
            VISAConnectionError: If not connected
            VISACommunicationError: If query fails
        """
        if not self.is_connected:
            raise VISAConnectionError(
                self._resource_string or "unknown", "Not connected to instrument"
            )

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._instrument.query, command)
            logger.debug(f"VISA query: {command.strip()} -> {response.strip()}")
            return response

        except pyvisa.errors.VisaIOError as e:
            if "timeout" in str(e).lower():
                logger.error(f"VISA query timeout: {e}")
                raise VISATimeoutError("query", int(self._timeout * 1000)) from e
            else:
                logger.error(f"VISA query failed: {e}")
                raise VISACommunicationError("query", str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error during VISA query: {e}")
            raise VISACommunicationError("query", str(e)) from e

    async def list_resources(self) -> list[str]:
        """
        List all available VISA resources

        Returns:
            List of VISA resource strings

        Raises:
            VISACommunicationError: If resource listing fails
        """
        try:
            if not self._resource_manager:
                loop = asyncio.get_event_loop()
                rm = await loop.run_in_executor(None, lambda: pyvisa.ResourceManager("@py"))
            else:
                rm = self._resource_manager

            loop = asyncio.get_event_loop()
            resources = await loop.run_in_executor(None, rm.list_resources)

            logger.info(f"Available VISA resources: {list(resources)}")
            return list(resources)

        except Exception as e:
            logger.error(f"Failed to list VISA resources: {e}")
            raise VISACommunicationError("list_resources", str(e)) from e
