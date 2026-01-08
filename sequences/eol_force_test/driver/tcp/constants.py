"""
TCP Communication Constants

Low-level TCP communication settings for network-based devices.
"""

# TCP Connection Settings
DEFAULT_PORT = 5025
DEFAULT_TIMEOUT = 2.0
CONNECT_TIMEOUT = 5.0

# Protocol Settings
COMMAND_TERMINATOR = "\n"  # LF (Line Feed)
RESPONSE_TERMINATOR = "\n"
COMMAND_BUFFER_SIZE = 50
MAX_COMMAND_LENGTH = 40

# Socket Settings
RECV_BUFFER_SIZE = 1024
FLUSH_TIMEOUT = 0.1
