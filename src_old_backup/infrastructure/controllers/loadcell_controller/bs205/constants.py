"""
BS205 Loadcell Controller Constants

Constants and definitions for BS205 loadcell controller protocol.
"""

# Protocol Control Characters
STX = 0x02  # Start of Text
ETX = 0x03  # End of Text

# Command Characters
CMD_READ_VALUE = ord('R')      # 0x52 - Read current value
CMD_AUTO_ZERO = ord('Z')       # 0x5A - Auto zero
CMD_HOLD_ON = ord('H')         # 0x48 - Hold on
CMD_HOLD_OFF = ord('L')        # 0x4C - Hold off (Low)

# Data Format Constants
DATA_LENGTH_MIN = 6   # Minimum data length (STX + ID + sign + digit + ETX)
DATA_LENGTH_MAX = 12  # Maximum data length for response
DECIMAL_POINT = ord('.')  # 0x2E
PLUS_SIGN = ord('+')      # 0x2B
MINUS_SIGN = ord('-')     # 0x2D
SPACE_CHAR = ord(' ')     # 0x20

# Communication Settings
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 1.0
DEFAULT_RETRY_COUNT = 3

# Thread Management
THREAD_STOP_SAFETY_MARGIN = 2.0      # Extra seconds beyond serial timeout
MIN_THREAD_STOP_TIMEOUT = 3.0        # Minimum guaranteed thread stop time
DEFAULT_THREAD_STOP_TIMEOUT = DEFAULT_TIMEOUT + THREAD_STOP_SAFETY_MARGIN  # 3.0

# Supported Baud Rates
SUPPORTED_BAUDRATES = [1200, 2400, 4800, 9600, 19200, 38400]

# Parity Options
PARITY_NONE = 'N'
PARITY_EVEN = 'E'
PARITY_ODD = 'O'

# Protocol Configuration
DATA_BITS = 8
STOP_BITS = 1
START_BITS = 1

# Response Parsing
MAX_DIGITS = 8        # Maximum number of digits in response
MAX_RESPONSE_TIME = 5.0  # Maximum time to wait for response in seconds

# Error Conditions
ERROR_TIMEOUT = "TIMEOUT"
ERROR_INVALID_RESPONSE = "INVALID_RESPONSE"
ERROR_CHECKSUM = "CHECKSUM"
ERROR_NO_DATA = "NO_DATA"

# Indicator ID Limits
MIN_INDICATOR_ID = 1
MAX_INDICATOR_ID = 255

# Data Validation
MIN_VALUE = -999999.99
MAX_VALUE = 999999.99

# Response Format Examples
RESPONSE_EXAMPLES = {
    'positive_int': '1+_7.487',
    'positive_space': '1+_ _7487', 
    'two_digit_id': '15+1.7486',
    'decimal_format': '10+_748.6',
    'negative': '2-_74.86'
}

# ASCII to HEX mappings for common characters
ASCII_MAPPINGS = {
    'STX': 0x02,
    'ETX': 0x03,
    '+': 0x2B,
    '-': 0x2D,
    '.': 0x2E,
    ' ': 0x20,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39
}

# Command Descriptions
COMMAND_DESCRIPTIONS = {
    CMD_READ_VALUE: "Read current display value",
    CMD_AUTO_ZERO: "Perform auto zero operation",
    CMD_HOLD_ON: "Enable hold function",
    CMD_HOLD_OFF: "Disable hold function"
}

# Status Messages
STATUS_CONNECTED = "Connected to loadcell controller"
STATUS_DISCONNECTED = "Disconnected from loadcell controller"
STATUS_READING = "Reading loadcell value"
STATUS_ZERO_SETTING = "Performing auto zero"
STATUS_HOLD_ENABLED = "Hold function enabled"
STATUS_HOLD_DISABLED = "Hold function disabled"


# ============================================================================
# Timeout Calculation Helpers
# ============================================================================

def calculate_thread_stop_timeout(serial_timeout: float) -> float:
    """
    Calculate appropriate thread stop timeout based on serial communication timeout
    
    Args:
        serial_timeout: Serial communication timeout in seconds
        
    Returns:
        float: Thread join timeout (serial_timeout + margin, minimum guaranteed)
    """
    return max(serial_timeout + THREAD_STOP_SAFETY_MARGIN, MIN_THREAD_STOP_TIMEOUT)