"""
AJINEXTEK AXL Library Error Codes

This module contains all error codes and descriptions from the AXL library.
"""

# ============================================================================
# General Return Codes
# ============================================================================

# Success
AXT_RT_SUCCESS = 0x0000  # 함수 실행 성공

# Library Open/Close Errors (1000-1099)
AXT_RT_OPEN_ERROR = 1001  # 라이브러리가 오픈 되어있지 않음
AXT_RT_OPEN_ALREADY = 1002  # 라이브러리가 오픈 되어있고 사용 중임
AXT_RT_NOT_INITIAL = 1052  # Serial module이 초기화되어있지 않음
AXT_RT_NOT_OPEN = 1053  # 라이브러리 초기화 실패
AXT_RT_NOT_SUPPORT_VERSION = 1054  # 지원하지않는 하드웨어
AXT_RT_BAD_PARAMETER = 1070  # 사용자가 입력한 파라미터가 적절하지 않음

# Hardware Validation Errors (1100-1159)
AXT_RT_INVALID_HARDWARE = 1100  # 유효하지 않는 보드
AXT_RT_INVALID_BOARD_NO = 1101  # 유효하지 않는 보드 번호
AXT_RT_INVALID_MODULE_POS = 1102  # 유효하지 않는 모듈 위치
AXT_RT_INVALID_LEVEL = 1103  # 유효하지 않는 레벨
AXT_RT_INVALID_VARIABLE = 1104  # 유효하지 않는 변수
AXT_RT_INVALID_MODULE_NO = 1105  # 유효하지 않는 모듈
AXT_RT_INVALID_NO = 1106  # 유효하지 않는 번호
AXT_RT_ERROR_VERSION_READ = 1151  # 라이브러리 버전을 읽을수 없음
AXT_RT_NETWORK_ERROR = 1152  # 하드웨어 네트워크 에러

# Motion Module Errors (4000-4999)
AXT_RT_MOTION_OPEN_ERROR = 4001  # 모션 라이브러리 Open 실패
AXT_RT_MOTION_NOT_MODULE = 4051  # 시스템에 장착된 모션 모듈이 없음
AXT_RT_MOTION_NOT_INTERRUPT = 4052  # 인터럽트 결과 읽기 실패
AXT_RT_MOTION_INVALID_AXIS_NO = 4101  # 해당 축이 존재하지 않음
AXT_RT_MOTION_INVALID_METHOD = 4102  # 해당 축 구동에 필요한 설정이 잘못됨
AXT_RT_MOTION_INVALID_VELOCITY = 4113  # 모션 구동 속도값이 0으로 설정되어 모션 에러 발생
AXT_RT_MOTION_ERROR_IN_MOTION = 4152  # 모션 구동 중에 다른 모션 구동 함수를 실행함
AXT_RT_MOTION_ERROR_IN_NONMOTION = 4151  # 모션 구동중이어야 되는데 모션 구동중이 아닐 때
AXT_RT_MOTION_HOME_SEARCHING = 4201  # 홈을 찾고 있는 중일 때 다른 모션 함수들을 사용할 때
AXT_RT_PROTECTED_DURING_SERVOON = 4260  # 서보 온 되어 있는 상태에서 사용 못 함

# DIO Module Errors (3000-3199)
AXT_RT_DIO_OPEN_ERROR = 3001  # DIO 모듈 오픈실패
AXT_RT_DIO_NOT_MODULE = 3051  # DIO 모듈 없음
AXT_RT_DIO_INVALID_MODULE_NO = 3101  # 유효하지않는 DIO 모듈 번호
AXT_RT_DIO_INVALID_OFFSET_NO = 3102  # 유효하지않는 DIO OFFSET 번호
AXT_RT_DIO_INVALID_VALUE = 3105  # 유효하지않는 값 설정

# ============================================================================
# Error Code Mapping Dictionary
# ============================================================================

ERROR_MESSAGES = {
    # General
    AXT_RT_SUCCESS: "Function executed successfully",
    # Library Errors
    AXT_RT_OPEN_ERROR: "Library is not open",
    AXT_RT_OPEN_ALREADY: "Library is already open and in use",
    AXT_RT_NOT_INITIAL: "Serial module is not initialized",
    AXT_RT_NOT_OPEN: "Library initialization failed",
    AXT_RT_NOT_SUPPORT_VERSION: "Unsupported hardware",
    AXT_RT_BAD_PARAMETER: "Invalid parameter provided by user",
    # Hardware Validation
    AXT_RT_INVALID_HARDWARE: "Invalid board",
    AXT_RT_INVALID_BOARD_NO: "Invalid board number",
    AXT_RT_INVALID_MODULE_POS: "Invalid module position",
    AXT_RT_INVALID_LEVEL: "Invalid level",
    AXT_RT_INVALID_VARIABLE: "Invalid variable",
    AXT_RT_INVALID_MODULE_NO: "Invalid module number",
    AXT_RT_INVALID_NO: "Invalid number",
    # DIO Errors
    AXT_RT_DIO_OPEN_ERROR: "DIO module open failed",
    AXT_RT_DIO_NOT_MODULE: "DIO module not found",
    AXT_RT_DIO_INVALID_MODULE_NO: "Invalid DIO module number",
    AXT_RT_DIO_INVALID_OFFSET_NO: "Invalid DIO offset number",
    AXT_RT_DIO_INVALID_VALUE: "Invalid value setting",
    # Motion Errors
    AXT_RT_MOTION_OPEN_ERROR: "Motion library open failed",
    AXT_RT_MOTION_NOT_MODULE: "No motion module installed in system",
    AXT_RT_MOTION_INVALID_AXIS_NO: "Axis does not exist",
    AXT_RT_MOTION_INVALID_METHOD: "Invalid axis drive configuration",
    AXT_RT_MOTION_INVALID_VELOCITY: "Motion velocity set to 0, causing motion error",
    AXT_RT_MOTION_ERROR_IN_MOTION: "Cannot execute motion function while axis is already in motion",
    AXT_RT_MOTION_ERROR_IN_NONMOTION: "Axis should be in motion but is not moving",
    AXT_RT_MOTION_HOME_SEARCHING: "Cannot use other motion functions while home search is in progress",
    AXT_RT_PROTECTED_DURING_SERVOON: "Cannot use this function while servo is ON",
}


def get_error_message(error_code: int) -> str:
    """
    Get error message for given error code

    Args:
        error_code: AXL library error code

    Returns:
        str: Error description in English
    """
    return ERROR_MESSAGES.get(error_code, f"Unknown error code: {error_code}")


def is_success(error_code: int) -> bool:
    """
    Check if error code indicates success

    Args:
        error_code: AXL library error code

    Returns:
        bool: True if success, False otherwise
    """
    return error_code == AXT_RT_SUCCESS


def is_library_error(error_code: int) -> bool:
    """
    Check if error code is library related

    Args:
        error_code: AXL library error code

    Returns:
        bool: True if library error, False otherwise
    """
    return 1000 <= error_code < 2000


def is_motion_error(error_code: int) -> bool:
    """
    Check if error code is motion related

    Args:
        error_code: AXL library error code

    Returns:
        bool: True if motion error, False otherwise
    """
    return 4000 <= error_code < 5000


def is_dio_error(error_code: int) -> bool:
    """
    Check if error code is DIO related

    Args:
        error_code: AXL library error code

    Returns:
        bool: True if DIO error, False otherwise
    """
    return 3000 <= error_code < 3200
