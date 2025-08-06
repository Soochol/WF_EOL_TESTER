"""
Enhanced EOL Tester CLI - Compatibility Module

This module provides backward compatibility for the Enhanced EOL Tester CLI
while delegating functionality to the new modular architecture.

MIGRATION NOTICE:
This module has been refactored into specialized components:
- Core application logic: src/ui/cli/core/cli_application.py
- Session management: src/ui/cli/session/session_manager.py
- Menu system: src/ui/cli/menu/menu_system.py
- Input validation: src/ui/cli/validation/input_validator.py
- Test execution: src/ui/cli/execution/test_executor.py

For new development, please use the modular components directly.
This compatibility module will be deprecated in a future version.
"""

# Standard library imports
from typing import TYPE_CHECKING, Any, Optional

# Local imports - New modular architecture
from .application_factory import create_production_cli_application
from .validation.input_validator import InputValidator, ValidationConstants

# TYPE_CHECKING imports
if TYPE_CHECKING:
    from src.application.services.hardware_service_facade import HardwareServiceFacade
    from src.application.use_cases.eol_force_test import EOLForceTestUseCase


# Re-export validation components for backward compatibility
__all__ = ["ValidationConstants", "InputValidator", "EnhancedEOLTesterCLI"]


class EnhancedEOLTesterCLI:
    """Enhanced EOL Tester CLI - Compatibility wrapper using dependency injection.

    This class provides backward compatibility by wrapping the new dependency
    injection based CLI application. All functionality is delegated to the
    interface-based architecture components.

    DEPRECATED: Use application_factory functions directly for new development.
    """

    def __init__(
        self,
        use_case: "EOLForceTestUseCase",
        hardware_facade: Optional["HardwareServiceFacade"] = None,
        configuration_service: Optional[Any] = None,
    ):
        """Initialize the enhanced CLI with backward compatibility.

        Args:
            use_case: EOL test execution use case
            hardware_facade: Hardware service facade for individual hardware control
            configuration_service: Configuration service for loading DUT defaults
        """
        # Create CLI application using dependency injection
        self._application = create_production_cli_application(
            use_case=use_case,
            hardware_facade=hardware_facade,
            configuration_service=configuration_service,
        )

        # Store dependencies for backward compatibility
        self._use_case = use_case
        self._hardware_facade = hardware_facade
        self._configuration_service = configuration_service

        # Maintain backward compatibility by exposing legacy properties
        self._validator = self._application.get_validator()
        self._hardware_manager = self._application.get_hardware_manager()
        self._usecase_manager = self._application.get_usecase_manager()

        # Configuration reader compatibility
        if self._hardware_facade:
            from .config_reader import CLIConfigReader

            self._config_reader = CLIConfigReader()
        else:
            self._config_reader = None

    async def run_interactive(self) -> None:
        """Run the interactive CLI application.

        Delegates to the injected CLI application for session handling.
        """
        await self._application.run_interactive()

    # Legacy compatibility properties
    @property
    def _running(self) -> bool:
        """Legacy compatibility property for running state."""
        return self._application._running  # pylint: disable=protected-access

    @_running.setter
    def _running(self, value: bool) -> None:
        """Legacy compatibility setter for running state."""
        self._application._running = value  # pylint: disable=protected-access  # type: ignore

    # Component access methods for backward compatibility
    def get_console(self):
        """Get console instance for external components."""
        return self._application.get_console()

    def get_formatter(self):
        """Get formatter instance for external components."""
        return self._application.get_formatter()

    def get_validator(self):
        """Get validator instance for external components."""
        return self._application.get_validator()

    def get_hardware_manager(self):
        """Get hardware manager instance for external components."""
        return self._application.get_hardware_manager()

    def get_usecase_manager(self):
        """Get usecase manager instance for external components."""
        return self._application.get_usecase_manager()
