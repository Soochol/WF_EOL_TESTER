"""
Serial Communication Exceptions

Exception classes for serial communication errors.
Provides structured error handling for different types of serial communication failures.
"""

from typing import Optional


class SerialError(Exception):
    """Base serial communication error"""

    def __init__(
        self,
        message: str,
        port: Optional[str] = None,
        baudrate: Optional[int] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.port = port
        self.baudrate = baudrate
        self.details = details

    def __str__(self) -> str:
        base_msg = self.message
        if self.details:
            base_msg = (
                f"{base_msg}. Details: {self.details}"
            )

        if self.port and self.baudrate:
            base_msg = f"{base_msg} (Port: {self.port} @ {self.baudrate} baud)"
        elif self.port:
            base_msg = f"{base_msg} (Port: {self.port})"

        return base_msg


class SerialConnectionError(SerialError):
    """Serial connection establishment errors.

    Raised when unable to establish a connection to the serial port,
    including port access issues, hardware not found, or permission errors.
    """


class SerialCommunicationError(SerialError):
    """Serial communication errors (send/receive failures).

    Raised when data transmission or reception fails during serial communication,
    including checksum errors, protocol violations, or unexpected responses.
    """


class SerialTimeoutError(SerialError):
    """Serial operation timeout errors.

    Raised when serial operations exceed their configured timeout limits,
    including read timeouts, write timeouts, or handshake timeouts.
    """


class SerialConfigurationError(SerialError):
    """Serial configuration errors.

    Raised when serial port configuration is invalid or cannot be applied,
    including unsupported baud rates, parity settings, or data bits.
    """


class SerialBufferError(SerialError):
    """Serial buffer operation errors.

    Raised when buffer operations fail, including buffer overflow,
    buffer underrun, or memory allocation issues for serial buffers.
    """
