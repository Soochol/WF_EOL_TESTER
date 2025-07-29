"""
Ajinextek DIO Card Constants

Constants and definitions for Ajinextek Digital I/O card communication.
"""

# DIO Card Configuration
DEFAULT_BOARD_NUMBER = 0
DEFAULT_MODULE_POSITION = 0
MAX_BOARDS = 32
MAX_MODULES_PER_BOARD = 4

# Channel Configuration
MAX_INPUT_CHANNELS = 32
MAX_OUTPUT_CHANNELS = 32
TOTAL_CHANNELS = MAX_INPUT_CHANNELS + MAX_OUTPUT_CHANNELS

# Input Channel Range
INPUT_CHANNEL_START = 0
INPUT_CHANNEL_END = MAX_INPUT_CHANNELS - 1

# Output Channel Range
OUTPUT_CHANNEL_START = 0
OUTPUT_CHANNEL_END = MAX_OUTPUT_CHANNELS - 1

# Logic Levels
LOGIC_LOW = 0
LOGIC_HIGH = 1

# Pin Mode Definitions
PIN_MODE_INPUT = 0
PIN_MODE_OUTPUT = 1
PIN_MODE_INPUT_PULLUP = 2
PIN_MODE_INPUT_PULLDOWN = 3

# Signal Types
SIGNAL_TYPE_TTL = 0  # TTL 5V logic
SIGNAL_TYPE_CMOS = 1  # CMOS 3.3V logic
SIGNAL_TYPE_24V = 2  # 24V industrial logic

# Timing Constants
DEFAULT_DEBOUNCE_TIME_MS = 10
MAX_DEBOUNCE_TIME_MS = 1000
DEFAULT_OUTPUT_DELAY_MS = 1
MAX_OUTPUT_DELAY_MS = 100

# Response Time Limits
MAX_RESPONSE_TIME_MS = 50
TYPICAL_RESPONSE_TIME_MS = 5

# Error Retry Configuration
DEFAULT_RETRY_COUNT = 3
MAX_RETRY_COUNT = 10
RETRY_DELAY_MS = 100

# Board Detection and Initialization
BOARD_DETECTION_TIMEOUT_MS = 5000
INITIALIZATION_TIMEOUT_MS = 10000
RESET_DELAY_MS = 1000

# Communication Settings
AXL_LIBRARY_NAME = "AXL.dll"
AXL_64BIT_LIBRARY_NAME = "AXL64.dll"

# Module Types (Ajinextek specific)
MODULE_TYPE_DI = "DI"  # Digital Input
MODULE_TYPE_DO = "DO"  # Digital Output
MODULE_TYPE_DIO = "DIO"  # Digital Input/Output
MODULE_TYPE_RELAY = "RELAY"  # Relay Output

# Standard Module Configurations
STANDARD_DI_MODULES = {
    "AX5A16": {
        "channels": 16,
        "type": MODULE_TYPE_DI,
        "voltage": "24V",
    },
    "AX5A32": {
        "channels": 32,
        "type": MODULE_TYPE_DI,
        "voltage": "24V",
    },
    "AX5B16": {
        "channels": 16,
        "type": MODULE_TYPE_DI,
        "voltage": "12V",
    },
}

STANDARD_DO_MODULES = {
    "AX5C16": {
        "channels": 16,
        "type": MODULE_TYPE_DO,
        "voltage": "24V",
    },
    "AX5C32": {
        "channels": 32,
        "type": MODULE_TYPE_DO,
        "voltage": "24V",
    },
    "AX5D16": {
        "channels": 16,
        "type": MODULE_TYPE_RELAY,
        "voltage": "240V",
    },
}

# Interrupt Configuration
INTERRUPT_DISABLED = 0
INTERRUPT_RISING_EDGE = 1
INTERRUPT_FALLING_EDGE = 2
INTERRUPT_BOTH_EDGES = 3

# Status Bit Masks
STATUS_BOARD_CONNECTED = 0x01
STATUS_MODULE_DETECTED = 0x02
STATUS_INITIALIZATION_OK = 0x04
STATUS_COMMUNICATION_OK = 0x08
STATUS_ERROR_PRESENT = 0x80

# Error Bit Masks
ERROR_NONE = 0x00
ERROR_BOARD_NOT_FOUND = 0x01
ERROR_MODULE_NOT_FOUND = 0x02
ERROR_INVALID_CHANNEL = 0x04
ERROR_COMMUNICATION_FAILED = 0x08
ERROR_TIMEOUT = 0x10
ERROR_INVALID_PARAMETER = 0x20
ERROR_HARDWARE_FAULT = 0x40
ERROR_LIBRARY_NOT_LOADED = 0x80

# Default Hardware Configuration
DEFAULT_CONFIG = {
    "board_number": DEFAULT_BOARD_NUMBER,
    "module_position": DEFAULT_MODULE_POSITION,
    "signal_type": SIGNAL_TYPE_24V,
    "debounce_time_ms": DEFAULT_DEBOUNCE_TIME_MS,
    "output_delay_ms": DEFAULT_OUTPUT_DELAY_MS,
    "retry_count": DEFAULT_RETRY_COUNT,
    "auto_initialize": True,
    "enable_interrupts": False,
}

# Pin Configuration Presets
PRESET_ALL_INPUTS = {
    i: PIN_MODE_INPUT for i in range(MAX_INPUT_CHANNELS)
}
PRESET_ALL_OUTPUTS = {
    i: PIN_MODE_OUTPUT for i in range(MAX_OUTPUT_CHANNELS)
}
PRESET_MIXED_IO = {
    **{
        i: PIN_MODE_INPUT for i in range(0, 16)
    },  # First 16 as inputs
    **{
        i: PIN_MODE_OUTPUT for i in range(16, 32)
    },  # Last 16 as outputs
}

# Status Messages
STATUS_MESSAGES = {
    "board_connected": "DIO board connected successfully",
    "board_disconnected": "DIO board disconnected",
    "module_detected": "DIO module detected and initialized",
    "initialization_complete": "DIO card initialization complete",
    "pin_configured": "Pin configuration updated",
    "input_read": "Digital input read successful",
    "output_written": "Digital output written successfully",
    "all_outputs_reset": "All outputs reset to LOW",
    "communication_ok": "Communication with DIO card OK",
    "hardware_ready": "DIO hardware ready for operation",
}

# Command Descriptions
COMMAND_DESCRIPTIONS = {
    "connect": "Connect to DIO board and initialize",
    "disconnect": "Disconnect from DIO board",
    "configure_pin": "Configure pin mode (input/output)",
    "read_input": "Read digital input state",
    "write_output": "Write digital output state",
    "read_multiple": "Read multiple input states",
    "write_multiple": "Write multiple output states",
    "reset_outputs": "Reset all outputs to LOW state",
    "get_status": "Get hardware status and configuration",
}

# Performance Monitoring
PERFORMANCE_THRESHOLDS = {
    "max_read_time_ms": 10,
    "max_write_time_ms": 10,
    "max_init_time_ms": 5000,
    "max_error_rate_percent": 1.0,
}
