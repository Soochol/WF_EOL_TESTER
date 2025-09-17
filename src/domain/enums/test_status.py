"""
Test Status Enumeration

Defines the possible states of test execution in the EOL testing system.
"""

# Standard library imports
from enum import Enum


class TestStatus(Enum):
    """Test execution status enumeration"""

    NOT_STARTED = "not_started"
    PREPARING = "preparing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ERROR = "error"

    def __str__(self) -> str:
        return self.value

    @property
    def is_active(self) -> bool:
        """Check if test is currently active/running"""
        return self in (
            TestStatus.PREPARING,
            TestStatus.RUNNING,
        )

    @property
    def is_finished(self) -> bool:
        """Check if test execution has finished (success or failure)"""
        return self in (
            TestStatus.COMPLETED,
            TestStatus.FAILED,
            TestStatus.CANCELLED,
            TestStatus.ERROR,
        )

    @property
    def is_successful(self) -> bool:
        """Check if test completed successfully"""
        return self == TestStatus.COMPLETED

    @property
    def requires_cleanup(self) -> bool:
        """Check if test status requires cleanup actions"""
        return self in (
            TestStatus.FAILED,
            TestStatus.ERROR,
            TestStatus.CANCELLED,
        )
