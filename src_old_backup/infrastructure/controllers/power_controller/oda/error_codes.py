"""
Error Codes for ODA Power Supply

This module contains all error codes and descriptions from the ODA manual.
"""

# Error Codes (from ODA Manual)
ERROR_CODES = {
    # Success
    0: "No error",
    
    # 동작 Error (Trip Errors)
    -1: "OVP Trip error - 파워서플라이 출력 과전압 검출",
    -2: "OCP Trip error - 파워서플라이 출력 과전류 검출", 
    -3: "OTP Trip error - 내부온도가 70°C 이상 상승",
    -4: "FAN Trip error - FAN 회전이 멈춤",
    -5: "AC Input Trip error - AC 입력 전압값 ±15% 이상 오차",
    -6: "PFC CAP Voltage Trip error - PFC 출력 전압값 ±15% 이상 오차",
    -7: "PA Imon Trip error - 파워모듈의 1차측 전류 과전류 측정",
    -8: "Power Down Trip error - 메인 MCU의 전원이 불안정",
    -10: "V-Sensing Trip error - V-Sensing 전압이 5% 이상 출력",
    
    # Remote Calibration Error
    -20: "Ignored min run under volt - 전압 Min값이 실행되지 않은 상태에서 MAX나 VALUE 실행",
    -21: "Ignored min save under volt - 전압 Min값의 Value를 실행하지 않고 MAX 실행",
    -22: "Invalid min value use under volt - 전압 Min값 value 실행 후 max 실행하지 않고 Value 재전송",
    -23: "En route to cal the curr - 전류 Calibration중에 전압관련 Calibration명령 전송",
    -24: "Over volt min parameter - 전압 Min의 value값 영역을 벗어남",
    -25: "Under volt max parameter - 전압 Max의 value값 영역 중 하한값을 벗어남",
    -26: "Over volt max parameter - 전압 Max의 value값 영역 중 상한값을 벗어남",
    -27: "Ignored min run under curr - 전류 Min값이 실행되지 않은 상태에서 MAX나 VALUE 실행",
    -28: "Ignored min save under curr - 전류 Min값의 Value를 실행하지 않고 MAX 실행",
    -29: "Invalid min value use under curr - 전류 Min값 value 실행 후 max 실행하지 않고 Value 재전송",
    -30: "En route to cal the curr - 전압 Calibration중에 전류관련 Calibration명령 전송",
    -31: "Over curr min parameter - 전류 Min의 value값 영역을 벗어남",
    -32: "Under curr max parameter - 전류 Max의 value값 영역 중 하한값을 벗어남",
    -33: "Over curr max parameter - 전류 Max의 value값 영역 중 상한값을 벗어남",
    -34: "Not allowed command under cal - Remote Calibration중에 다른 명령 사용 불가",
    
    # Calibration Error
    -74: "ADC-V low limit over - 전압 ADC Low 영역을 벗어남",
    -75: "ADC-V high limit over - 전압 ADC High 영역을 벗어남",
    -76: "ADC-A low limit over - 전류 ADC Low 영역을 벗어남",
    -77: "ADC-A high limit over - 전류 ADC High 영역을 벗어남",
    
    # 불휘발성 메모리 체크 Error
    -80: "Memory limit volt error - 제품의 설정 가능한 전압값에 오류",
    -81: "Memory limit curr error - 제품의 설정 가능한 전류값에 오류",
    -82: "Memory max volt error - 제품의 최대 전압값에 오류",
    -83: "Memory max curr error - 제품의 최대 전류값에 오류",
    -84: "Memory volt decimal error - 전압의 소수점 표현에 오류",
    -85: "Memory curr decimal error - 전류의 소수점 표현에 오류",
    -86: "Memory volt length error - 전압의 Digit길이에 오류",
    -87: "Memory curr length error - 전류의 Digit길이에 오류",
    -88: "Not match volt length and limit - 설정 가능한 전압값과 Digit길이가 서로 상이",
    -89: "Not match curr length and limit - 설정 가능한 전류값과 Digit길이가 서로 상이",
    
    # Interface Commands Error
    -120: "Suffix too long - 최대 50byte buffer를 초과",
    -121: "Invalid data - 숫자 자리에 문자가 있거나 올바르지 않은 데이터 입력",
    -122: "Syntax error - 문법오류",
    -123: "Invalid suffix - 수신된 데이터의 마지막 부분에 오류",
    -124: "Undefined header - 정의되지 않은 Command 전송",
    
    # Hardware Error
    -200: "System interface error - SCPI Module이 작동하지 않음",
    -201: "ADC operating failed - ADC Part의 회로가 작동되지 않음",
    -202: "Front panel operating failed - Front panel이 응답하지 않음",
    -220: "No execution - 현재 실행할 수 없는 명령",
    -221: "Setting conflict - 현 제품에는 사용하지 않는 명령어",
    -222: "Out of data - 설정값 영역을 벗어남",
    -223: "Incorrect error - Buffer내용을 처리하지 않고 새로운 작업 시도",
    -255: "Error not define - 정의되지 않은 에러",
}

# Error Categories for easier classification
ERROR_CATEGORIES = {
    'TRIP_ERRORS': list(range(-10, 0)),  # -10 to -1
    'CALIBRATION_ERRORS': list(range(-34, -19)) + list(range(-89, -73)),  # -34 to -20, -89 to -74
    'INTERFACE_ERRORS': list(range(-124, -119)),  # -124 to -120
    'HARDWARE_ERRORS': [-200, -201, -202, -220, -221, -222, -223, -255],
    'MEMORY_ERRORS': list(range(-89, -79)),  # -89 to -80
}

# Error Severity Levels
ERROR_SEVERITY = {
    'CRITICAL': [-3, -4, -5, -6, -7, -8, -200, -201, -202, -255],  # System/Hardware failures
    'WARNING': [-1, -2, -10],  # Protection trips (recoverable)
    'INFO': [0],  # No error
    'MINOR': [-120, -121, -122, -123, -124, -220, -221, -222, -223],  # Command/syntax errors
}

# Protection Error Types
PROTECTION_ERRORS = {
    -1: 'OVP',  # Over Voltage Protection
    -2: 'OCP',  # Over Current Protection  
    -3: 'OTP',  # Over Temperature Protection
    -10: 'VSP', # V-Sensing Protection
}

# Trip Error Recovery Actions
RECOVERY_ACTIONS = {
    -1: "Check load and voltage settings, clear OVP",
    -2: "Check load and current settings, clear OCP", 
    -3: "Check ventilation, wait for cooling, check fan",
    -4: "Check fan operation, replace if necessary",
    -5: "Check AC input voltage stability",
    -6: "Contact service - PFC circuit issue",
    -7: "Contact service - Primary current issue", 
    -8: "Check power supply, restart device",
    -10: "Check voltage sensing connections",
}


def get_error_message(error_code: int) -> str:
    """
    Get error message for given error code
    
    Args:
        error_code: ODA error code
        
    Returns:
        str: Error description in Korean
    """
    return ERROR_CODES.get(error_code, f"알수없는 에러코드: {error_code}")


def get_error_category(error_code: int) -> str:
    """
    Get error category for given error code
    
    Args:
        error_code: ODA error code
        
    Returns:
        str: Error category name
    """
    for category, codes in ERROR_CATEGORIES.items():
        if error_code in codes:
            return category
    return "UNKNOWN"


def get_error_severity(error_code: int) -> str:
    """
    Get error severity level
    
    Args:
        error_code: ODA error code
        
    Returns:
        str: Severity level (CRITICAL, WARNING, INFO, MINOR)
    """
    for severity, codes in ERROR_SEVERITY.items():
        if error_code in codes:
            return severity
    return "UNKNOWN"


def get_protection_type(error_code: int) -> str:
    """
    Get protection type for trip errors
    
    Args:
        error_code: ODA error code
        
    Returns:
        str: Protection type or empty string
    """
    return PROTECTION_ERRORS.get(error_code, "")


def get_recovery_action(error_code: int) -> str:
    """
    Get suggested recovery action for error
    
    Args:
        error_code: ODA error code
        
    Returns:
        str: Recovery action description
    """
    return RECOVERY_ACTIONS.get(error_code, "Check manual for specific recovery procedure")


def is_success(error_code: int) -> bool:
    """
    Check if error code indicates success
    
    Args:
        error_code: ODA error code
        
    Returns:
        bool: True if success, False otherwise
    """
    return error_code == 0


def is_trip_error(error_code: int) -> bool:
    """
    Check if error code is a protection trip
    
    Args:
        error_code: ODA error code
        
    Returns:
        bool: True if trip error, False otherwise
    """
    return error_code in ERROR_CATEGORIES['TRIP_ERRORS']


def is_hardware_error(error_code: int) -> bool:
    """
    Check if error code is hardware related
    
    Args:
        error_code: ODA error code
        
    Returns:
        bool: True if hardware error, False otherwise
    """
    return error_code in ERROR_CATEGORIES['HARDWARE_ERRORS']


def is_interface_error(error_code: int) -> bool:
    """
    Check if error code is interface/command related
    
    Args:
        error_code: ODA error code
        
    Returns:
        bool: True if interface error, False otherwise
    """
    return error_code in ERROR_CATEGORIES['INTERFACE_ERRORS']


def analyze_error(error_code: int) -> dict:
    """
    Comprehensive error analysis
    
    Args:
        error_code: ODA error code
        
    Returns:
        dict: Complete error analysis
    """
    return {
        'code': error_code,
        'message': get_error_message(error_code),
        'category': get_error_category(error_code),
        'severity': get_error_severity(error_code),
        'protection_type': get_protection_type(error_code),
        'recovery_action': get_recovery_action(error_code),
        'is_success': is_success(error_code),
        'is_trip': is_trip_error(error_code),
        'is_hardware': is_hardware_error(error_code),
        'is_interface': is_interface_error(error_code),
    }