"""
Serial Communication Driver

Provides async serial communication for hardware devices.
"""

from .serial import SerialConnection, SerialManager
from .exceptions import (
    SerialError,
    SerialConnectionError,
    SerialCommunicationError,
    SerialTimeoutError,
    SerialConfigurationError,
)
from .constants import (
    DEFAULT_BAUDRATE,
    DEFAULT_TIMEOUT,
    CONNECT_TIMEOUT,
    COMMAND_TERMINATOR,
    ENCODING,
)

__all__ = [
    "SerialConnection",
    "SerialManager",
    "SerialError",
    "SerialConnectionError",
    "SerialCommunicationError",
    "SerialTimeoutError",
    "SerialConfigurationError",
    "DEFAULT_BAUDRATE",
    "DEFAULT_TIMEOUT",
    "CONNECT_TIMEOUT",
    "COMMAND_TERMINATOR",
    "ENCODING",
]
