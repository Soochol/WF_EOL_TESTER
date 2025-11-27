"""
NeuroHub MES TCP/IP Protocol Driver

Length-prefixed JSON protocol for NeuroHub MES integration.
Protocol: 4-byte Big Endian length header + UTF-8 JSON payload
"""

# Standard library imports
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party imports
from loguru import logger

# Local application imports
from driver.tcp.exceptions import (
    TCPCommunicationError,
    TCPConnectionError,
    TCPTimeoutError,
)


# Protocol constants
HEADER_SIZE = 4  # 4-byte Big Endian length header
MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB max message size
DEFAULT_RECV_BUFFER = 4096


@dataclass
class NeuroHubMessage:
    """NeuroHub message data structure"""

    message_type: str  # "START" or "COMPLETE"
    serial_number: str
    result: Optional[str] = None  # "PASS" or "FAIL" (for COMPLETE)
    measurements: Optional[List[Dict[str, Any]]] = None
    defects: Optional[List[Dict[str, Any]]] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data: Dict[str, Any] = {
            "message_type": self.message_type,
            "serial_number": self.serial_number,
        }

        if self.result is not None:
            data["result"] = self.result

        if self.measurements is not None:
            data["measurements"] = self.measurements

        if self.defects is not None:
            data["defects"] = self.defects

        if self.timestamp is not None:
            data["timestamp"] = self.timestamp

        return data


@dataclass
class NeuroHubAck:
    """NeuroHub ACK response structure"""

    status: str  # "OK" or "ERROR"
    message: Optional[str] = None
    error_code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NeuroHubAck":
        """Create from dictionary"""
        return cls(
            status=data.get("status", "ERROR"),
            message=data.get("message"),
            error_code=data.get("error_code"),
        )


class NeuroHubProtocol:
    """
    NeuroHub MES TCP/IP Protocol Handler

    Implements length-prefixed JSON protocol:
    - 4-byte Big Endian length header
    - UTF-8 JSON payload
    - ACK response after each message
    """

    def __init__(
        self,
        host: str,
        port: int = 9000,
        timeout: float = 5.0,
    ):
        """
        Initialize NeuroHub protocol handler

        Args:
            host: NeuroHub Client host address
            port: TCP port (default: 9000)
            timeout: Communication timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.is_connected = False

    async def connect(self) -> None:
        """
        Establish TCP connection to NeuroHub Client

        Raises:
            TCPConnectionError: If connection fails
        """
        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout,
            )
            self.is_connected = True
            logger.info(f"NeuroHub connected to {self.host}:{self.port}")

        except asyncio.TimeoutError as e:
            logger.error(f"NeuroHub connection timeout: {self.host}:{self.port}")
            self.is_connected = False
            raise TCPConnectionError(
                f"Connection timeout to {self.host}:{self.port}",
                host=self.host,
                port=self.port,
                details="Connection timed out",
            ) from e

        except OSError as e:
            logger.error(f"NeuroHub connection failed: {e}")
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
            logger.info(f"NeuroHub disconnected from {self.host}:{self.port}")
            return True

        except Exception as e:
            logger.error(f"Error during NeuroHub disconnect: {e}")
            return False

    def _encode_message(self, data: Dict[str, Any]) -> bytes:
        """
        Encode message with length header

        Args:
            data: Dictionary to encode as JSON

        Returns:
            bytes: Length header + JSON payload
        """
        json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        length_header = len(json_bytes).to_bytes(HEADER_SIZE, byteorder="big")
        return length_header + json_bytes

    async def _send_raw(self, data: bytes) -> None:
        """
        Send raw bytes to NeuroHub

        Args:
            data: Bytes to send

        Raises:
            TCPCommunicationError: If send fails
        """
        if not self.is_connected or not self.writer:
            raise TCPConnectionError(
                "Not connected to NeuroHub",
                host=self.host,
                port=self.port,
            )

        try:
            self.writer.write(data)
            await self.writer.drain()
            logger.debug(f"NeuroHub sent {len(data)} bytes")

        except (OSError, ConnectionError) as e:
            logger.error(f"Failed to send to NeuroHub: {e}")
            self.is_connected = False
            raise TCPCommunicationError(
                "Failed to send message",
                host=self.host,
                port=self.port,
                details=str(e),
            ) from e

    async def _receive_ack(self) -> NeuroHubAck:
        """
        Receive ACK response from NeuroHub

        Returns:
            NeuroHubAck: ACK response

        Raises:
            TCPTimeoutError: If no response within timeout
            TCPCommunicationError: If response reception fails
        """
        if not self.is_connected or not self.reader:
            raise TCPConnectionError(
                "Not connected to NeuroHub",
                host=self.host,
                port=self.port,
            )

        try:
            # Receive response (NeuroHub sends JSON without length header in ACK)
            response_data = await asyncio.wait_for(
                self.reader.read(DEFAULT_RECV_BUFFER),
                timeout=self.timeout,
            )

            if not response_data:
                raise TCPTimeoutError(
                    "No ACK received from NeuroHub",
                    host=self.host,
                    port=self.port,
                )

            # Parse JSON response
            response_str = response_data.decode("utf-8").strip()
            logger.debug(f"NeuroHub ACK: {response_str}")

            try:
                response_dict = json.loads(response_str)
                return NeuroHubAck.from_dict(response_dict)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in NeuroHub ACK: {response_str}")
                return NeuroHubAck(
                    status="ERROR",
                    message=f"Invalid JSON response: {str(e)}",
                    error_code="PARSE_ERROR",
                )

        except asyncio.TimeoutError as e:
            logger.error("NeuroHub ACK timeout")
            raise TCPTimeoutError(
                "ACK timeout from NeuroHub",
                host=self.host,
                port=self.port,
            ) from e

        except (OSError, ConnectionError) as e:
            logger.error(f"Failed to receive NeuroHub ACK: {e}")
            self.is_connected = False
            raise TCPCommunicationError(
                "Failed to receive ACK",
                host=self.host,
                port=self.port,
                details=str(e),
            ) from e

    async def send_message(self, message: NeuroHubMessage) -> NeuroHubAck:
        """
        Send message to NeuroHub and receive ACK

        Args:
            message: NeuroHub message to send

        Returns:
            NeuroHubAck: ACK response from NeuroHub

        Raises:
            TCPConnectionError: If not connected
            TCPCommunicationError: If communication fails
            TCPTimeoutError: If ACK not received within timeout
        """
        # Add timestamp if not set
        if message.timestamp is None:
            message.timestamp = datetime.now().isoformat()

        # Encode and send
        message_dict = message.to_dict()
        encoded = self._encode_message(message_dict)

        # Log detailed message content
        logger.info(f"NeuroHub sending {message.message_type}: serial={message.serial_number}")
        logger.debug(f"NeuroHub message payload: {json.dumps(message_dict, indent=2, ensure_ascii=False)}")

        await self._send_raw(encoded)
        return await self._receive_ack()

    async def send_start(self, serial_number: str) -> NeuroHubAck:
        """
        Send START (착공) message

        Args:
            serial_number: WIP serial number

        Returns:
            NeuroHubAck: ACK response
        """
        message = NeuroHubMessage(
            message_type="START",
            serial_number=serial_number,
        )
        return await self.send_message(message)

    async def send_complete(
        self,
        serial_number: str,
        result: str,
        measurements: Optional[List[Dict[str, Any]]] = None,
        defects: Optional[List[Dict[str, Any]]] = None,
    ) -> NeuroHubAck:
        """
        Send COMPLETE (완공) message

        Args:
            serial_number: WIP serial number
            result: Test result ("PASS" or "FAIL")
            measurements: List of measurement data
            defects: List of defect information (for FAIL results)

        Returns:
            NeuroHubAck: ACK response
        """
        message = NeuroHubMessage(
            message_type="COMPLETE",
            serial_number=serial_number,
            result=result,
            measurements=measurements,
            defects=defects,
        )
        return await self.send_message(message)

    async def __aenter__(self) -> "NeuroHubProtocol":
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.disconnect()
