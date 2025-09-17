"""
TCP Communication Driver

Generic TCP/IP communication driver for network-based devices.
Provides low-level TCP communication primitives for command/response protocols.
"""

# Local application imports
from driver.tcp.communication import TCPCommunication
from driver.tcp.constants import DEFAULT_PORT, DEFAULT_TIMEOUT
from driver.tcp.exceptions import (
    TCPCommunicationError,
    TCPConnectionError,
    TCPError,
    TCPTimeoutError,
)


__all__ = [
    "TCPCommunication",
    "TCPError",
    "TCPConnectionError",
    "TCPCommunicationError",
    "TCPTimeoutError",
    "DEFAULT_PORT",
    "DEFAULT_TIMEOUT",
]
