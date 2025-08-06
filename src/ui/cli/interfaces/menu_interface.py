"""Menu System Interface

Defines the contract for menu display, navigation, and user choice handling
for CLI interfaces. Provides professional menu system capabilities with
enhanced user experience and component integration.

This interface enables dependency injection and flexible implementation
substitution for different menu system strategies.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# TYPE_CHECKING imports to avoid circular dependencies
if TYPE_CHECKING:
    from .execution_interface import ITestExecutor
    from .session_interface import ISessionManager


class IMenuSystem(ABC):
    """Abstract interface for menu display and navigation system.

    Defines the contract for managing menu presentation, user choice collection,
    and navigation flow with professional Rich UI formatting. Implementations
    should provide comprehensive error handling and user feedback.

    Key Responsibilities:
    - Professional menu display with Rich formatting
    - Enhanced user input handling with validation
    - Menu navigation and choice processing
    - Integration with test execution and hardware control
    - Graceful error handling and user feedback
    """

    @abstractmethod
    def set_session_manager(self, session_manager: "ISessionManager") -> None:
        """Set session manager for session control.

        Args:
            session_manager: Session manager instance implementing ISessionManager
        """
        ...

    @abstractmethod
    def set_test_executor(self, test_executor: "ITestExecutor") -> None:
        """Set test executor for test operations.

        Args:
            test_executor: Test executor instance implementing ITestExecutor
        """
        ...

    @abstractmethod
    def set_usecase_manager(self, usecase_manager) -> None:
        """Set usecase manager for advanced operations.

        Args:
            usecase_manager: UseCase manager instance for advanced functionality
        """
        ...

    @abstractmethod
    def set_hardware_manager(self, hardware_manager) -> None:
        """Set hardware manager for hardware control.

        Args:
            hardware_manager: Hardware manager instance for hardware operations
        """
        ...

    @abstractmethod
    async def show_main_menu(self) -> None:
        """Display the main menu with advanced input features.

        Shows the main menu and processes user selections with comprehensive
        error handling and navigation control. Should handle user input validation,
        menu choice processing, and graceful exit scenarios.

        Raises:
            Exception: Various exceptions may be raised during menu operations
        """
        ...