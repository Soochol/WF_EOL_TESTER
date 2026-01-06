"""
Serial Communication Exceptions

Exception classes for serial communication errors.
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
            base_msg = f"{base_msg}. Details: {self.details}"

        if self.port and self.baudrate:
            base_msg = f"{base_msg} (Port: {self.port} @ {self.baudrate} baud)"
        elif self.port:
            base_msg = f"{base_msg} (Port: {self.port})"

        return base_msg


class SerialConnectionError(SerialError):
    """Serial connection establishment errors."""
    pass


class SerialCommunicationError(SerialError):
    """Serial communication errors (send/receive failures)."""
    pass


class SerialTimeoutError(SerialError):
    """Serial operation timeout errors."""
    pass


class SerialConfigurationError(SerialError):
    """Serial configuration errors."""
    pass


class SerialBufferError(SerialError):
    """Serial buffer operation errors."""
    pass
