"""
Serial Communication Constants

Configuration constants for serial communication devices.
"""

# Serial Connection Settings
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 1.0
CONNECT_TIMEOUT = 5.0

# Protocol Settings
COMMAND_TERMINATOR = "\r"  # Carriage Return (most common for industrial devices)
RESPONSE_TERMINATOR = "\r"
ALTERNATIVE_TERMINATOR = "\n"
ENCODING = "ascii"

# Buffer Settings
READ_BUFFER_SIZE = 1024
MAX_COMMAND_LENGTH = 100
MAX_RESPONSE_LENGTH = 512

# Retry and Error Handling
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 0.1
FLUSH_TIMEOUT = 0.1

# Device-Specific Settings
BS205_BAUDRATE = 9600
BS205_TIMEOUT = 1.0
BS205_TERMINATOR = "\r"
