"""
BS205 LoadCell Constants

Constants and definitions for BS205 LoadCell communication protocol.
"""

# Communication Settings
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 1.0
DEFAULT_INDICATOR_ID = 1
DEFAULT_RETRY_COUNT = 3

# Serial Protocol Settings
COMMAND_TERMINATOR = '\r'
RESPONSE_TERMINATOR = '\r\n'
RESPONSE_ENCODING = 'ascii'
COMMAND_ENCODING = 'ascii'

# BS205 Commands
CMD_READ_WEIGHT = "R"           # Read current weight value
CMD_ZERO = "Z"                  # Zero calibration
CMD_IDENTITY = "ID"             # Device identification
CMD_SPAN = "S"                  # Span calibration
CMD_TARE = "T"                  # Tare operation
CMD_PRINT = "P"                 # Print current reading
CMD_STABILITY = "ST"            # Check stability status
CMD_UNITS = "U"                 # Change units
CMD_RESET = "RST"               # Reset device

# Expected Response Patterns
RESPONSE_PATTERN_WEIGHT = r"R,([+-]?\d+\.?\d*),(\w+)"
RESPONSE_PATTERN_ZERO = r"Z,(OK|FAIL)"
RESPONSE_PATTERN_ID = r"ID,BS205"
RESPONSE_PATTERN_STABILITY = r"ST,(STABLE|UNSTABLE)"

# Response Values
RESPONSE_OK = "OK"
RESPONSE_FAIL = "FAIL"
RESPONSE_STABLE = "STABLE"
RESPONSE_UNSTABLE = "UNSTABLE"
DEVICE_ID_PATTERN = "BS205"

# Unit Conversions
KG_TO_NEWTON = 9.81             # 1 kg ≈ 9.81 N (standard gravity)
GRAM_TO_KG = 0.001              # 1 g = 0.001 kg
POUND_TO_KG = 0.453592          # 1 lb = 0.453592 kg

# Supported Units
UNIT_KG = "kg"
UNIT_G = "g"
UNIT_LB = "lb"
UNIT_OZ = "oz"
UNIT_N = "N"                    # Newton (calculated)

SUPPORTED_UNITS = [UNIT_KG, UNIT_G, UNIT_LB, UNIT_OZ]

# Weight Range and Precision
MAX_WEIGHT_KG = 500.0           # Maximum weight capacity
MIN_WEIGHT_KG = -500.0          # Minimum weight (for signed values)
WEIGHT_PRECISION = 0.001        # Weight measurement precision in kg
FORCE_PRECISION = 0.01          # Force measurement precision in N

# Timing Constants
ZERO_OPERATION_DELAY = 2.0      # Seconds to wait after zero operation
STABILITY_CHECK_INTERVAL = 0.5  # Seconds between stability checks
CONNECTION_RETRY_DELAY = 1.0    # Seconds between connection retries
COMMAND_RETRY_DELAY = 0.5       # Seconds between command retries

# Multiple Sampling
DEFAULT_SAMPLE_COUNT = 10
DEFAULT_SAMPLE_INTERVAL_MS = 100
MAX_SAMPLE_COUNT = 1000
MIN_SAMPLE_INTERVAL_MS = 50

# Response Parsing
RESPONSE_FIELD_SEPARATOR = ','
WEIGHT_FIELD_INDEX = 1
UNIT_FIELD_INDEX = 2
STATUS_FIELD_INDEX = 1

# Error Thresholds
MAX_CONSECUTIVE_ERRORS = 5
COMMUNICATION_TIMEOUT_MULTIPLIER = 2.0

# Command Descriptions
COMMAND_DESCRIPTIONS = {
    CMD_READ_WEIGHT: "Read current weight measurement",
    CMD_ZERO: "Perform zero calibration",
    CMD_IDENTITY: "Get device identification",
    CMD_SPAN: "Perform span calibration",
    CMD_TARE: "Perform tare operation",
    CMD_PRINT: "Print current reading to device display",
    CMD_STABILITY: "Check measurement stability",
    CMD_UNITS: "Change measurement units",
    CMD_RESET: "Reset device to default state"
}

# Status Messages
STATUS_MESSAGES = {
    "connected": "Device connected successfully",
    "disconnected": "Device disconnected",
    "zeroed": "Zero calibration completed",
    "zero_failed": "Zero calibration failed",
    "stable": "Measurement is stable",
    "unstable": "Measurement is unstable",
    "reading_ok": "Weight reading successful",
    "reading_failed": "Weight reading failed",
    "timeout": "Communication timeout",
    "invalid_response": "Invalid response format"
}

# Default Configuration
DEFAULT_CONFIG = {
    'baudrate': DEFAULT_BAUDRATE,
    'timeout': DEFAULT_TIMEOUT,
    'indicator_id': DEFAULT_INDICATOR_ID,
    'retry_count': DEFAULT_RETRY_COUNT,
    'auto_zero_on_connect': True,
    'stability_check': False,
    'preferred_unit': UNIT_KG
}