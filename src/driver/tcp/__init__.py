"""
TCP Communication Driver

Generic TCP/IP communication driver for network-based devices.
Provides low-level TCP communication primitives for command/response protocols.
"""

from driver.tcp.communication import TCPCommunication
from driver.tcp.exceptions import TCPError, TCPConnectionError, TCPCommunicationError, TCPTimeoutError
from driver.tcp.constants import DEFAULT_PORT, DEFAULT_TIMEOUT

__all__ = [
    'TCPCommunication',
    'TCPError',
    'TCPConnectionError', 
    'TCPCommunicationError',
    'TCPTimeoutError',
    'DEFAULT_PORT',
    'DEFAULT_TIMEOUT'
]