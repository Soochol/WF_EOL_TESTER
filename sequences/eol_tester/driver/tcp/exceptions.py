"""
TCP Communication Exceptions

Base exception classes for TCP/IP communication errors.
"""

from typing import Optional


class TCPError(Exception):
    """Base TCP communication error"""

    def __init__(
        self,
        message: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.host = host
        self.port = port
        self.details = details

    def __str__(self) -> str:
        base_msg = self.message
        if self.details:
            base_msg = f"{base_msg}. Details: {self.details}"

        if self.host and self.port:
            base_msg = f"{base_msg} (Host: {self.host}:{self.port})"
        elif self.host:
            base_msg = f"{base_msg} (Host: {self.host})"

        return base_msg


class TCPConnectionError(TCPError):
    """TCP connection establishment errors."""


class TCPCommunicationError(TCPError):
    """TCP communication errors (send/receive failures)."""


class TCPTimeoutError(TCPError):
    """TCP operation timeout errors."""
