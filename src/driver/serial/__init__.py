"""
Serial Communication Driver Module

Simple and efficient serial communication system for hardware devices.
Optimized for request-response patterns like BS205 LoadCell and similar industrial equipment.

The architecture provides:
- SerialConnection: Core async serial communication class
- SerialManager: Factory class for creating connections
- Constants: Centralized configuration values
- Exceptions: Structured error handling
"""

# Configuration constants (always available)
from driver.serial.constants import (
    DEFAULT_BAUDRATE,
    DEFAULT_TIMEOUT,
    CONNECT_TIMEOUT,
    COMMAND_TERMINATOR,
    RESPONSE_TERMINATOR,
    ENCODING,
    READ_BUFFER_SIZE,
    MAX_COMMAND_LENGTH,
    MAX_RESPONSE_LENGTH,
    MAX_RETRY_ATTEMPTS,
    RETRY_DELAY,
    FLUSH_TIMEOUT,
    BS205_BAUDRATE,
    BS205_TIMEOUT,
    BS205_TERMINATOR,
)

# Exception classes (always available)
from driver.serial.exceptions import (
    SerialError,
    SerialConnectionError,
    SerialCommunicationError,
    SerialTimeoutError,
    SerialConfigurationError,
    SerialBufferError,
)

# Core serial communication classes (conditional import for dependencies)
try:
    from driver.serial.serial import SerialConnection, SerialManager

    _SERIAL_AVAILABLE = True
except ImportError:
    _SERIAL_AVAILABLE = False
    SerialConnection = None
    SerialManager = None

__all__ = [
    # Core classes
    "SerialConnection",
    "SerialManager",
    # Constants
    "DEFAULT_BAUDRATE",
    "DEFAULT_TIMEOUT",
    "CONNECT_TIMEOUT",
    "COMMAND_TERMINATOR",
    "RESPONSE_TERMINATOR",
    "ENCODING",
    "READ_BUFFER_SIZE",
    "MAX_COMMAND_LENGTH",
    "MAX_RESPONSE_LENGTH",
    "MAX_RETRY_ATTEMPTS",
    "RETRY_DELAY",
    "FLUSH_TIMEOUT",
    "BS205_BAUDRATE",
    "BS205_TIMEOUT",
    "BS205_TERMINATOR",
    # Exceptions
    "SerialError",
    "SerialConnectionError",
    "SerialCommunicationError",
    "SerialTimeoutError",
    "SerialConfigurationError",
    "SerialBufferError",
]
