"""
TCP Communication Driver

Generic TCP/IP communication driver for network-based devices.
Provides low-level TCP communication primitives for command/response protocols.
"""

from .communication import TCPCommunication
from .exceptions import TCPError, TCPConnectionError, TCPCommunicationError, TCPTimeoutError
from .constants import DEFAULT_PORT, DEFAULT_TIMEOUT

__all__ = [
    'TCPCommunication',
    'TCPError',
    'TCPConnectionError', 
    'TCPCommunicationError',
    'TCPTimeoutError',
    'DEFAULT_PORT',
    'DEFAULT_TIMEOUT'
]