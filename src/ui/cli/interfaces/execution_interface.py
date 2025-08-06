"""Test Execution Interface

Defines the contract for test execution coordination, result display, and
test workflow management. Handles the complete test execution lifecycle
from parameter collection to result presentation.

This interface enables dependency injection and flexible implementation
substitution for different test execution strategies.
"""

from abc import ABC, abstractmethod


class ITestExecutor(ABC):
    """Abstract interface for test execution coordinator.

    Defines the contract for managing the complete test execution workflow
    including parameter collection, test execution, and result presentation.
    Implementations should provide comprehensive error handling and professional
    user feedback.

    Key Responsibilities:
    - Test execution coordination and workflow management
    - DUT information collection with validation
    - Comprehensive test result display with Rich formatting
    - Progress indication during test execution
    - Error handling and user feedback
    """

    @abstractmethod
    async def execute_eol_test(self) -> None:
        """Execute EOL test with Rich UI feedback.

        Complete test execution workflow including parameter collection,
        test execution, and result display. Should handle the entire
        test lifecycle with comprehensive error handling and user feedback.

        Raises:
            Exception: Various exceptions may be raised during test execution
        """
        ...