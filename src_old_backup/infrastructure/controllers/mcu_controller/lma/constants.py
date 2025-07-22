"""
LMA MCU Controller Constants

Constants and definitions for LMA MCU controller protocol.
"""

# Protocol Frame Markers
STX = b'\xFF\xFF'  # Start of frame
ETX = b'\xFE\xFE'  # End of frame

# Frame Structure
FRAME_STX_SIZE = 2
FRAME_CMD_SIZE = 1
FRAME_LEN_SIZE = 1
FRAME_ETX_SIZE = 2
FRAME_OVERHEAD = FRAME_STX_SIZE + FRAME_CMD_SIZE + FRAME_LEN_SIZE + FRAME_ETX_SIZE

# Command Codes (PC -> Controller)
CMD_ENTER_TEST_MODE = 0x01
CMD_SET_UPPER_TEMP = 0x02
CMD_SET_FAN_SPEED = 0x03
CMD_LMA_INIT = 0x04
CMD_SET_OPERATING_TEMP = 0x05
CMD_SET_COOLING_TEMP = 0x06
CMD_REQUEST_TEMP = 0x07
CMD_STROKE_INIT_COMPLETE = 0x08

# Status Codes (Controller -> PC)
STATUS_BOOT_COMPLETE = 0x00
STATUS_TEST_MODE_COMPLETE = 0x01
STATUS_UPPER_TEMP_OK = 0x02
STATUS_FAN_SPEED_OK = 0x03
STATUS_LMA_INIT_OK = 0x04
STATUS_OPERATING_TEMP_OK = 0x05
STATUS_COOLING_TEMP_OK = 0x06
STATUS_TEMP_RESPONSE = 0x07
STATUS_STROKE_INIT_OK = 0x08
STATUS_TEMP_RISE_START = 0x09
STATUS_TEMP_FALL_START = 0x0A
STATUS_OPERATING_TEMP_REACHED = 0x0B
STATUS_STANDBY_TEMP_REACHED = 0x0C
STATUS_COOLING_TEMP_REACHED = 0x0D
STATUS_LMA_INIT_COMPLETE = 0x0E

# Test Modes
TEST_MODE_1 = 0x00000001
TEST_MODE_2 = 0x00000002
TEST_MODE_3 = 0x00000003

# Fan Speed Levels
FAN_SPEED_MIN = 1
FAN_SPEED_MAX = 10

# Protocol Limits
MAX_DATA_SIZE = 12  # Maximum data payload size
MAX_FRAME_SIZE = MAX_DATA_SIZE + FRAME_OVERHEAD

# Temperature Scale
TEMP_SCALE_FACTOR = 10  # Temperature is sent as integer * 10 (e.g., 40.5°C = 405)

# Communication Settings
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 5.0
DEFAULT_RETRY_COUNT = 3
BOOT_COMPLETE_TIMEOUT = 60.0  # Boot complete message wait timeout

# Status Message Descriptions
STATUS_MESSAGES = {
    STATUS_BOOT_COMPLETE: "Boot complete",
    STATUS_TEST_MODE_COMPLETE: "Test mode entry complete",
    STATUS_UPPER_TEMP_OK: "Upper temperature set OK",
    STATUS_FAN_SPEED_OK: "Fan speed set OK",
    STATUS_LMA_INIT_OK: "LMA initialization OK",
    STATUS_OPERATING_TEMP_OK: "Operating temperature set OK",
    STATUS_COOLING_TEMP_OK: "Cooling temperature set OK",
    STATUS_TEMP_RESPONSE: "Temperature response",
    STATUS_STROKE_INIT_OK: "Stroke initialization OK",
    STATUS_TEMP_RISE_START: "Temperature rise started",
    STATUS_TEMP_FALL_START: "Temperature fall started",
    STATUS_OPERATING_TEMP_REACHED: "Operating temperature reached",
    STATUS_STANDBY_TEMP_REACHED: "Standby temperature reached",
    STATUS_COOLING_TEMP_REACHED: "Cooling temperature reached",
    STATUS_LMA_INIT_COMPLETE: "LMA initialization complete"
}

# Command Descriptions
COMMAND_MESSAGES = {
    CMD_ENTER_TEST_MODE: "Enter test mode",
    CMD_SET_UPPER_TEMP: "Set upper temperature",
    CMD_SET_FAN_SPEED: "Set fan speed",
    CMD_LMA_INIT: "LMA initialization",
    CMD_SET_OPERATING_TEMP: "Set operating temperature",
    CMD_SET_COOLING_TEMP: "Set cooling temperature",
    CMD_REQUEST_TEMP: "Request temperature",
    CMD_STROKE_INIT_COMPLETE: "Stroke initialization complete"
}