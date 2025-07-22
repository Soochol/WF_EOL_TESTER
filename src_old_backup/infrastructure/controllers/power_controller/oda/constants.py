"""
Constants for ODA Power Supply (SCPI Commands)

SCPI commands and ODA-specific constants based on ODA manual specifications.
TCP communication constants are now in driver.tcp module.
"""

# Device Limits (Single Channel Power Supply)
MAX_CHANNELS = 1  # ODA는 단일 채널

# Actual SCPI Commands from Manual
COMMANDS = {
    # System Commands
    'IDENTITY': '*IDN?',
    'SERIAL_NUMBER': '*SN?',
    'RESET': '*RST',
    'CLEAR': '*CLS',
    'ERROR': 'SYST:ERR?',
    'VERSION': 'SYST:VERS?',
    'TEMPERATURE': 'SYST:TEMP?',
    'BEEP': 'SYST:BEEP',
    'REMOTE': 'SYST:REM {mode}',  # 232 or 485
    
    # Output Control
    'OUTPUT_ON': 'OUTP ON',
    'OUTPUT_OFF': 'OUTP OFF',
    'OUTPUT_STATE': 'OUTP?',
    
    # Voltage Control
    'SET_VOLTAGE': 'VOLT {value}',
    'GET_VOLTAGE': 'VOLT?',
    'VOLTAGE_UP': 'VOLT UP',
    'VOLTAGE_DOWN': 'VOLT DOWN',
    'VOLTAGE_STEP': 'VOLT:STEP {value}',
    'GET_VOLTAGE_STEP': 'VOLT:STEP?',
    'MEASURE_VOLTAGE': 'MEAS:VOLT?',
    
    # Current Control  
    'SET_CURRENT': 'CURR {value}',
    'GET_CURRENT': 'CURR?',
    'CURRENT_UP': 'CURR UP',
    'CURRENT_DOWN': 'CURR DOWN',
    'CURRENT_STEP': 'CURR:STEP {value}',
    'GET_CURRENT_STEP': 'CURR:STEP?',
    'MEASURE_CURRENT': 'MEAS:CURR?',
    
    # Combined Commands
    'APPLY': 'APPL {voltage},{current}',
    'APPLY_QUERY': 'APPL?',
    'MEASURE_ALL': 'MEAS:ALL?',
    
    # Protection - Over Voltage Protection (OVP)
    'SET_OVP': 'VOLT:OVP {value}',
    'GET_OVP': 'VOLT:OVP?',
    'OVP_TRIP_STATUS': 'VOLT:OVP:TRIP?',
    'CLEAR_OVP': 'VOLT:OVP:CLE',
    
    # Protection - Over Current Protection (OCP)
    'SET_OCP': 'CURR:OCP {value}',
    'GET_OCP': 'CURR:OCP?',
    'OCP_TRIP_STATUS': 'CURR:OCP:TRIP?',
    'CLEAR_OCP': 'CURR:OCP:CLE',
    
    # Under/Over Limit Settings
    'SET_UVL': 'VOLT:UVL {value}',  # Under Voltage Limit
    'GET_UVL': 'VOLT:UVL?',
    'SET_OVL': 'VOLT:OVL {value}',  # Over Voltage Limit
    'GET_OVL': 'VOLT:OVL?',
    'SET_UCL': 'CURR:UCL {value}',  # Under Current Limit
    'GET_UCL': 'CURR:UCL?',
    'SET_OCL': 'CURR:OCL {value}',  # Over Current Limit
    'GET_OCL': 'CURR:OCL?',
    
    # Polarity (for applicable models)
    'SET_POLARITY': 'POL {polarity}',  # P or N
    'GET_POLARITY': 'POL?',
    
    # Flow Query
    'FLOW_QUERY': 'FLOW?',
    
    # Key Lock
    'KEY_LOCK_ON': 'KEYL ON',
    'KEY_LOCK_OFF': 'KEYL OFF',
    'KEY_LOCK_STATE': 'KEYL?',
    
    # Memory Save/Recall
    'SAVE_SETTINGS': '*SAV {slot}',    # 1-8, 10
    'RECALL_SETTINGS': '*RCL {slot}',  # 1-8, 10
    
    # Factory Settings
    'FACTORY_RESET': 'FACT:LOAD-DEF',
    'FACTORY_USER_CLEAR': 'FACT:USER-M CLR',
    'FACTORY_LAST_STATE': 'FACT:LAST-STA {state}',  # DIS/SAF/FUL
    'GET_FACTORY_LAST_STATE': 'FACT:LAST-STA?',
    'FACTORY_AUTO_CURRENT': 'FACT:AUTO-CUR {state}',  # DIS/ENA
    'GET_FACTORY_AUTO_CURRENT': 'FACT:AUTO-CUR?',
    'FACTORY_AUTO_LOCK': 'FACT:AUTO-LOC {state}',  # DIS/ENA
    'GET_FACTORY_AUTO_LOCK': 'FACT:AUTO-LOC?',
    'FACTORY_OVP': 'FACT:OVP {state}',  # DIS/ENA
    'GET_FACTORY_OVP': 'FACT:OVP?',
    'FACTORY_OCP': 'FACT:OCP {state}',  # DIS/ENA
    'GET_FACTORY_OCP': 'FACT:OCP?',
    'FACTORY_ADC': 'FACT:ADC {value}',  # 5/20/50/100/300/1300
    'GET_FACTORY_ADC': 'FACT:ADC?',
    
    # Calibration Commands
    'CAL_VOLTAGE': 'CAL:VOLT {value}',  # value/MIN/MAX
    'CAL_CURRENT': 'CAL:CURR {value}',  # value/MIN/MAX
}

# Response Patterns
RESPONSE_PATTERNS = {
    'OK': 'OK',
    'ERROR': 'ERR',
    'ON': '1',
    'OFF': '0',
}

# Import error codes from separate file
from .error_codes import ERROR_CODES, get_error_message

# Protection Types
PROTECTION_TYPES = {
    'OVP': 'Over Voltage Protection',
    'OCP': 'Over Current Protection',
    'OTP': 'Over Temperature Protection',
    'OPP': 'Over Power Protection',
}

# Output Modes
OUTPUT_MODES = {
    'CV': 'Constant Voltage',
    'CC': 'Constant Current',
    'CP': 'Constant Power',
}

# Units
UNITS = {
    'VOLTAGE': 'V',
    'CURRENT': 'A',
    'POWER': 'W',
    'RESISTANCE': 'Ω',
    'TIME': 's',
}

def validate_channel(channel: int) -> bool:
    """Validate channel number (ODA is single channel)"""
    return channel == 1

def validate_memory_slot(slot: int) -> bool:
    """Validate memory slot number"""
    return slot in [1, 2, 3, 4, 5, 6, 7, 8, 10]

def validate_voltage(voltage: float, max_voltage: float = 999.0) -> bool:
    """Validate voltage value"""
    return 0.0 <= voltage <= max_voltage

def validate_current(current: float, max_current: float = 999.0) -> bool:
    """Validate current value"""
    return 0.0 <= current <= max_current