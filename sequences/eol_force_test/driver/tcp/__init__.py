"""
TCP Communication Driver

Provides async TCP/IP communication for network-based devices.
"""

from .communication import TCPCommunication
from .exceptions import (
    TCPError,
    TCPConnectionError,
    TCPCommunicationError,
    TCPTimeoutError,
)
from .constants import (
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    CONNECT_TIMEOUT,
    COMMAND_TERMINATOR,
    RESPONSE_TERMINATOR,
)

__all__ = [
    "TCPCommunication",
    "TCPError",
    "TCPConnectionError",
    "TCPCommunicationError",
    "TCPTimeoutError",
    "DEFAULT_PORT",
    "DEFAULT_TIMEOUT",
    "CONNECT_TIMEOUT",
    "COMMAND_TERMINATOR",
    "RESPONSE_TERMINATOR",
]
