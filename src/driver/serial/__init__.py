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

# Local application imports
# Configuration constants (always available)
from driver.serial.constants import (
    BS205_BAUDRATE,
    BS205_TERMINATOR,
    BS205_TIMEOUT,
    COMMAND_TERMINATOR,
    CONNECT_TIMEOUT,
    DEFAULT_BAUDRATE,
    DEFAULT_TIMEOUT,
    ENCODING,
    FLUSH_TIMEOUT,
    MAX_COMMAND_LENGTH,
    MAX_RESPONSE_LENGTH,
    MAX_RETRY_ATTEMPTS,
    READ_BUFFER_SIZE,
    RESPONSE_TERMINATOR,
    RETRY_DELAY,
)

# Exception classes (always available)
from driver.serial.exceptions import (
    SerialBufferError,
    SerialCommunicationError,
    SerialConfigurationError,
    SerialConnectionError,
    SerialError,
    SerialTimeoutError,
)


# Core serial communication classes (conditional import for dependencies)
try:
    # Local application imports
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
