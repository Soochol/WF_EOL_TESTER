"""MCU-related enumerations for domain layer"""
from enum import Enum


class TestMode(Enum):
    """테스트 모드"""

    MODE_1 = "mode_1"
    MODE_2 = "mode_2"
    MODE_3 = "mode_3"


class MCUStatus(Enum):
    """MCU 상태"""

    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    HEATING = "heating"
    COOLING = "cooling"