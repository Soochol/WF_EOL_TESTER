"""
Test Type Enumeration

Defines the types of tests that can be performed in the EOL testing system.
"""

from enum import Enum


class TestType(Enum):
    """EOL Test type enumeration"""
    FORCE_TEST = "force_test"
    ELECTRICAL_TEST = "electrical_test" 
    FUNCTIONAL_TEST = "functional_test"
    CALIBRATION_TEST = "calibration_test"
    FULL_EOL_TEST = "full_eol_test"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def requires_force_measurement(self) -> bool:
        """Check if test type requires force measurement"""
        return self in (TestType.FORCE_TEST, TestType.FULL_EOL_TEST)
    
    @property 
    def requires_electrical_measurement(self) -> bool:
        """Check if test type requires electrical measurement"""
        return self in (TestType.ELECTRICAL_TEST, TestType.FULL_EOL_TEST)
    
    @property
    def is_comprehensive(self) -> bool:
        """Check if test type is comprehensive (tests multiple aspects)"""
        return self in (TestType.FULL_EOL_TEST, TestType.FUNCTIONAL_TEST)