"""
Domain Enumerations Package

Contains enumerations that define valid states, types, and categories within the domain.
"""

# Local application imports
from domain.enums.digital_input_enums import LogicLevel, PinMode
from domain.enums.hardware_status import HardwareStatus
from domain.enums.mcu_enums import MCUStatus, TestMode
from domain.enums.measurement_units import MeasurementUnit
from domain.enums.robot_enums import MotionStatus
from domain.enums.test_status import TestStatus


__all__ = [
    "HardwareStatus",
    "MeasurementUnit",
    "TestStatus",
    "PinMode",
    "LogicLevel",
    "MotionStatus",
    "TestMode",
    "MCUStatus",
]
