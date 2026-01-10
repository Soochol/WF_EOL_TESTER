"""
Serial Communication Driver

Simplified serial communication for hardware devices.
Optimized for request-response patterns like BS205 LoadCell.
"""

from typing import Optional
import asyncio
from loguru import logger

from .constants import (
    COMMAND_TERMINATOR,
    CONNECT_TIMEOUT,
    DEFAULT_BAUDRATE,
    DEFAULT_TIMEOUT,
    ENCODING,
)
from .exceptions import (
    SerialCommunicationError,
    SerialConfigurationError,
    SerialConnectionError,
    SerialTimeoutError,
)


try:
    import serial_asyncio
except ImportError:
    logger.warning("serial_asyncio not available, install with: pip install pyserial-asyncio")
    serial_asyncio = None


class SerialConnection:
    """Simple serial connection for async communication"""

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        """
        Initialize serial connection

        Args:
            reader: Async stream reader
            writer: Async stream writer
        """
        self._reader = reader
        self._writer = writer
        self._is_connected = True

    @staticmethod
    async def connect(
        port: str,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = CONNECT_TIMEOUT,
        bytesize: int = 8,
        stopbits: int = 1,
        parity: Optional[str] = None,
    ) -> "SerialConnection":
        """
        Connect to serial port

        Args:
            port: Serial port (e.g., 'COM3', '/dev/ttyUSB0')
            baudrate: Baud rate
            timeout: Connection timeout
            bytesize: Number of data bits (5, 6, 7, 8)
            stopbits: Number of stop bits (1, 2)
            parity: Parity setting (None, 'even', 'odd', 'mark', 'space')

        Returns:
            SerialConnection instance

        Raises:
            SerialError: Connection failed
        """
        if serial_asyncio is None:
            raise SerialConfigurationError(
                "pyserial-asyncio not installed",
                port=port,
                baudrate=baudrate,
                details="Install with: pip install pyserial-asyncio",
            )

        try:
            # Convert parity string to pyserial constant
            parity_map = {
                None: "N",
                "none": "N",
                "even": "E",
                "odd": "O",
                "mark": "M",
                "space": "S",
            }
            parity_value = parity_map.get(parity.lower() if parity else None, "N")

            # Convert stopbits to float for pyserial
            stopbits_value = float(stopbits)

            reader, writer = await asyncio.wait_for(
                serial_asyncio.open_serial_connection(
                    url=port,
                    baudrate=baudrate,
                    bytesize=bytesize,
                    stopbits=stopbits_value,
                    parity=parity_value,
                    timeout=timeout,
                ),
                timeout=timeout,
            )

            logger.info(
                f"Serial connected to {port} at {baudrate} baud "
                f"({bytesize}{parity[0].upper() if parity else 'N'}{int(stopbits)})"
            )
            return SerialConnection(reader, writer)

        except asyncio.TimeoutError as e:
            raise SerialConnectionError(
                f"Connection timeout to {port}",
                port=port,
                baudrate=baudrate,
            ) from e
        except Exception as e:
            raise SerialConnectionError(
                f"Failed to connect to {port}",
                port=port,
                baudrate=baudrate,
                details=str(e),
            ) from e

    async def disconnect(self) -> None:
        """Disconnect from serial port with explicit serial handle cleanup"""
        try:
            # First, explicitly close the underlying pyserial Serial object
            if self._writer and hasattr(self._writer, "transport"):
                transport = self._writer.transport
                if transport and hasattr(transport, "serial"):
                    serial_instance = transport.serial  # type: ignore[attr-defined]
                    if serial_instance and hasattr(serial_instance, "close"):
                        try:
                            serial_instance.close()
                            logger.debug("Underlying serial port closed explicitly")
                        except Exception as serial_close_error:
                            logger.warning(
                                f"Failed to close underlying serial port: {serial_close_error}"
                            )

            # Then close the writer (stream layer)
            if self._writer and not self._writer.is_closing():
                self._writer.close()
                try:
                    await self._writer.wait_closed()
                except Exception as wait_error:
                    logger.warning(f"Error waiting for writer to close: {wait_error}")

        except Exception as e:
            logger.error(f"Error during serial disconnect: {e}")
        finally:
            self._is_connected = False
            logger.info("Serial connection closed")

    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self._is_connected and not self._writer.is_closing()

    async def flush_input_buffer(self) -> bool:
        """Clear input buffer using pyserial's native flush method"""
        try:
            if hasattr(self._writer, "transport") and self._writer.transport:
                serial_instance = getattr(self._writer.transport, "serial", None)
                if serial_instance is None:
                    return False
                if hasattr(serial_instance, "reset_input_buffer"):
                    serial_instance.reset_input_buffer()
                    logger.debug("Input buffer flushed")
                    return True
        except Exception as e:
            logger.debug(f"Native buffer flush failed: {e}")
        return False

    async def set_dtr(self, state: bool) -> bool:
        """Set DTR (Data Terminal Ready) line state"""
        try:
            if hasattr(self._writer, "transport") and self._writer.transport:
                serial_instance = getattr(self._writer.transport, "serial", None)
                if serial_instance and hasattr(serial_instance, "dtr"):
                    serial_instance.dtr = state
                    logger.debug(f"DTR set to {state}")
                    return True
        except Exception as e:
            logger.debug(f"Failed to set DTR: {e}")
        return False

    async def set_rts(self, state: bool) -> bool:
        """Set RTS (Request To Send) line state"""
        try:
            if hasattr(self._writer, "transport") and self._writer.transport:
                serial_instance = getattr(self._writer.transport, "serial", None)
                if serial_instance and hasattr(serial_instance, "rts"):
                    serial_instance.rts = state
                    logger.debug(f"RTS set to {state}")
                    return True
        except Exception as e:
            logger.debug(f"Failed to set RTS: {e}")
        return False

    async def write(self, data: bytes) -> None:
        """
        Write data to serial port

        Args:
            data: Data to write

        Raises:
            SerialError: Write failed
        """
        if not self.is_connected():
            raise SerialConnectionError("Not connected")

        try:
            self._writer.write(data)
            await self._writer.drain()

        except Exception as e:
            raise SerialCommunicationError("Write failed", details=str(e)) from e

    async def read_until(
        self,
        separator: bytes,
        timeout: Optional[float] = None,
    ) -> bytes:
        """
        Read data until separator is found

        Args:
            separator: Byte sequence to read until
            timeout: Read timeout

        Returns:
            Data including separator

        Raises:
            SerialError: Read failed or timeout
        """
        if not self.is_connected():
            raise SerialConnectionError("Not connected")

        try:
            if timeout:
                data = await asyncio.wait_for(
                    self._reader.readuntil(separator),
                    timeout=timeout,
                )
            else:
                data = await self._reader.readuntil(separator)

            return data

        except asyncio.TimeoutError as e:
            raise SerialTimeoutError("Read timeout") from e
        except Exception as e:
            raise SerialCommunicationError("Read failed", details=str(e)) from e

    async def read(
        self,
        size: int = -1,
        timeout: Optional[float] = None,
    ) -> bytes:
        """
        Read specified number of bytes

        Args:
            size: Number of bytes to read (-1 for all available)
            timeout: Read timeout

        Returns:
            Data read

        Raises:
            SerialError: Read failed or timeout
        """
        if not self.is_connected():
            raise SerialConnectionError("Not connected")

        try:
            if timeout:
                data = await asyncio.wait_for(self._reader.read(size), timeout=timeout)
            else:
                data = await self._reader.read(size)

            return data

        except asyncio.TimeoutError as e:
            raise SerialTimeoutError("Read timeout") from e
        except Exception as e:
            raise SerialCommunicationError("Read failed", details=str(e)) from e

    async def send_command(
        self,
        command: str,
        terminator: str = COMMAND_TERMINATOR,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> str:
        """
        Send command and read response (convenience method)

        Args:
            command: Command to send
            terminator: Command/response terminator
            timeout: Response timeout

        Returns:
            Response string (without terminator)

        Raises:
            SerialError: Communication failed
        """
        try:
            # Send command
            command_bytes = f"{command}{terminator}".encode(ENCODING)
            await self.write(command_bytes)

            # Read response
            terminator_bytes = terminator.encode(ENCODING)
            response_bytes = await self.read_until(terminator_bytes, timeout)

            # Decode and strip terminator
            response = response_bytes.decode(ENCODING).rstrip(terminator)

            logger.debug(f"Command: {command} -> Response: {response}")
            return response

        except UnicodeDecodeError as e:
            raise SerialCommunicationError("Response decode failed", details=str(e)) from e
        except Exception as e:
            raise SerialCommunicationError("Command failed", details=str(e)) from e


class SerialManager:
    """Simple serial manager for creating connections"""

    @staticmethod
    async def create_connection(
        port: str,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = CONNECT_TIMEOUT,
        bytesize: int = 8,
        stopbits: int = 1,
        parity: Optional[str] = None,
    ) -> SerialConnection:
        """
        Create serial connection (convenience method)

        Args:
            port: Serial port
            baudrate: Baud rate
            timeout: Connection timeout
            bytesize: Number of data bits
            stopbits: Number of stop bits
            parity: Parity setting

        Returns:
            SerialConnection instance
        """
        return await SerialConnection.connect(port, baudrate, timeout, bytesize, stopbits, parity)
