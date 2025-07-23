"""
Serial Communication Constants

Configuration constants for serial communication devices.
Optimized for request-response patterns like BS205 LoadCell and similar hardware.
"""

# Serial Connection Settings
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 1.0
CONNECT_TIMEOUT = 5.0

# Protocol Settings
COMMAND_TERMINATOR = '\r'        # Carriage Return (most common for industrial devices)
RESPONSE_TERMINATOR = '\r'       # Match command terminator
ALTERNATIVE_TERMINATOR = '\n'    # Line Feed (alternative for some devices)
ENCODING = 'ascii'               # Standard encoding for industrial protocols

# Buffer Settings
READ_BUFFER_SIZE = 1024         # Read buffer size in bytes
MAX_COMMAND_LENGTH = 100        # Maximum command length in characters
MAX_RESPONSE_LENGTH = 512       # Maximum expected response length

# Retry and Error Handling
MAX_RETRY_ATTEMPTS = 3          # Maximum retry attempts for failed operations
RETRY_DELAY = 0.1               # Delay between retry attempts (seconds)
FLUSH_TIMEOUT = 0.1             # Timeout for buffer flushing operations

# Device-Specific Settings
BS205_BAUDRATE = 9600           # BS205 LoadCell specific baud rate
BS205_TIMEOUT = 1.0             # BS205 LoadCell specific timeout
BS205_TERMINATOR = '\r'         # BS205 LoadCell specific terminator