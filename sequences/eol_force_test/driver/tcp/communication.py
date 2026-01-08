"""
TCP/IP Communication Driver

Generic TCP/IP communication driver for network-based devices.
Supports command/response protocols commonly used in test equipment.
"""

from typing import Any, cast
import asyncio
from loguru import logger

from .constants import (
    COMMAND_BUFFER_SIZE,
    CONNECT_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    FLUSH_TIMEOUT,
    RECV_BUFFER_SIZE,
    RESPONSE_TERMINATOR,
)
from .exceptions import (
    TCPCommunicationError,
    TCPConnectionError,
    TCPTimeoutError,
)


class TCPCommunication:
    """Generic TCP/IP communication handler for network devices"""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize TCP communication

        Args:
            host: IP address of device
            port: TCP port (default: 5025)
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.reader = None
        self.writer = None
        self.is_connected = False

    async def connect(self) -> None:
        """
        Establish TCP connection

        Raises:
            TCPConnectionError: If connection fails
        """
        try:
            self.reader, self.writer = await asyncio.wait_for(
                cast(
                    Any,
                    asyncio.open_connection(self.host, self.port),
                ),
                timeout=CONNECT_TIMEOUT,
            )
            self.is_connected = True
            logger.info(f"TCP connected to {self.host}:{self.port}")

        except (OSError, asyncio.TimeoutError) as e:
            logger.error(f"TCP connection failed ({type(e).__name__}): {e}")
            self.is_connected = False
            raise TCPConnectionError(
                f"Failed to connect to {self.host}:{self.port}",
                host=self.host,
                port=self.port,
                details=str(e),
            ) from e

    async def disconnect(self) -> bool:
        """
        Close TCP connection

        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
                self.writer = None
                self.reader = None
            self.is_connected = False
            logger.info(f"TCP disconnected from {self.host}:{self.port}")
            return True

        except Exception as e:
            logger.error(f"Error during TCP disconnect: {e}")
            return False

    async def send_command(self, command: str) -> None:
        """
        Send command to device as-is without adding terminators

        Args:
            command: Command string (should include proper termination if needed)

        Raises:
            TCPCommunicationError: If command send fails
        """
        if not self.is_connected or not self.writer:
            logger.error("TCP not connected to device")
            raise TCPConnectionError(
                "Not connected to device",
                host=self.host,
                port=self.port,
            )

        try:
            # Check command length
            if len(command.encode()) > COMMAND_BUFFER_SIZE:
                logger.error(
                    f"Command too long: {len(command.encode())} bytes (max {COMMAND_BUFFER_SIZE})"
                )
                raise TCPCommunicationError(
                    f"Command too long: {len(command.encode())} bytes (max {COMMAND_BUFFER_SIZE})",
                    host=self.host,
                    port=self.port,
                )

            self.writer.write(command.encode())
            await self.writer.drain()
            logger.debug(f"TCP sent: {repr(command)}")

        except (OSError, ConnectionError) as e:
            logger.error(f"Failed to send TCP command '{command}': {e}")
            self.is_connected = False
            raise TCPCommunicationError(
                f"Failed to send command '{command}'",
                host=self.host,
                port=self.port,
                details=str(e),
            ) from e

    async def receive_response(self) -> str:
        """
        Receive response from device

        Returns:
            str: Response string

        Raises:
            TCPCommunicationError: If response reception fails
        """
        if not self.is_connected or not self.reader:
            logger.error("TCP not connected to device")
            raise TCPConnectionError(
                "Not connected to device",
                host=self.host,
                port=self.port,
            )

        try:
            response_data = b""

            # Read data until we get the response terminator or timeout
            while True:
                try:
                    data = await asyncio.wait_for(
                        self.reader.read(RECV_BUFFER_SIZE),
                        timeout=self.timeout,
                    )
                    if not data:
                        break

                    response_data += data

                    # Check if we have complete response
                    if RESPONSE_TERMINATOR.encode() in response_data:
                        break

                except asyncio.TimeoutError:
                    break

            if response_data:
                response = response_data.decode().strip()
                logger.debug(f"TCP received: {repr(response)}")
                return response

            logger.warning("No TCP response received")
            raise TCPTimeoutError(
                "No response received within timeout",
                host=self.host,
                port=self.port,
            )

        except (OSError, ConnectionError) as e:
            logger.error(f"Failed to receive TCP response: {e}")
            self.is_connected = False
            raise TCPCommunicationError(
                "Failed to receive response",
                host=self.host,
                port=self.port,
                details=str(e),
            ) from e

    async def query(self, command: str) -> str:
        """
        Send command and receive response

        Args:
            command: Query command

        Returns:
            str: Response string

        Raises:
            TCPCommunicationError: If query fails
        """
        await self.send_command(command)
        return await self.receive_response()

    async def flush_buffer(self) -> None:
        """Clear any pending data in receive buffer"""
        if not self.is_connected or not self.reader:
            return

        try:
            while True:
                try:
                    data = await asyncio.wait_for(
                        self.reader.read(RECV_BUFFER_SIZE),
                        timeout=FLUSH_TIMEOUT,
                    )
                    if not data:
                        break
                except asyncio.TimeoutError:
                    break
        except Exception:
            pass

    async def test_connection(self) -> bool:
        """
        Test if connection is still alive

        Returns:
            bool: True if connection is working
        """
        if not self.is_connected:
            return False

        try:
            await self.query("*IDN?")
            return True
        except Exception as e:
            logger.error(f"TCP connection test failed: {e}")
            self.is_connected = False
            return False

    async def reconnect(self) -> None:
        """
        Attempt to reconnect

        Raises:
            TCPConnectionError: If reconnection fails
        """
        logger.info(f"Attempting to reconnect to {self.host}:{self.port}...")
        await self.disconnect()
        await asyncio.sleep(1)
        await self.connect()

    async def __aenter__(self) -> "TCPCommunication":
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.disconnect()
