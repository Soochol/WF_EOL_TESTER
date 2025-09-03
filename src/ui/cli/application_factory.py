"""CLI Application Factory

Factory functions for creating CLI applications with dependency injection.
Provides convenient methods for creating fully configured CLI applications
with all dependencies properly injected based on configuration mode.

Key Features:
- Factory functions for different operational modes
- Automatic dependency injection and configuration
- Easy integration with existing application code
- Support for testing and mock modes
"""

from typing import Any, Optional

from loguru import logger

from .config.component_config import ConfigurationMode
from .factories.component_factory import CLIComponentFactory
from .interfaces.application_interface import ICLIApplication


def create_cli_application(
    use_case: Any,
    hardware_facade: Optional[Any] = None,
    configuration_service: Optional[Any] = None,
    emergency_stop_service: Optional[Any] = None,
    mode: ConfigurationMode = ConfigurationMode.PRODUCTION,
) -> ICLIApplication:
    """Create a CLI application with dependency injection.

    Factory function that creates a fully configured CLI application
    with all dependencies properly injected based on the specified
    configuration mode.

    Args:
        use_case: EOL test execution use case
        hardware_facade: Optional hardware service facade
        configuration_service: Optional configuration service
        emergency_stop_service: Optional emergency stop service for hardware safety
        mode: Configuration mode for dependency injection

    Returns:
        CLI application instance with dependencies injected

    Raises:
        ValueError: If application creation fails
    """
    logger.info(f"Creating CLI application in {mode.value} mode")

    try:
        # Create component factory for the specified mode
        factory = CLIComponentFactory(mode)

        # Create CLI application with dependencies
        application = factory.create_cli_application(
            use_case=use_case,
            hardware_facade=hardware_facade,
            configuration_service=configuration_service,
            emergency_stop_service=emergency_stop_service,
        )

        logger.info("CLI application created successfully")
        return application

    except Exception as e:
        logger.error(f"Failed to create CLI application: {e}")
        raise ValueError(f"Failed to create CLI application: {e}") from e


def create_production_cli_application(
    use_case: Any,
    hardware_facade: Optional[Any] = None,
    configuration_service: Optional[Any] = None,
    emergency_stop_service: Optional[Any] = None,
) -> ICLIApplication:
    """Create a CLI application in production mode.

    Args:
        use_case: EOL test execution use case
        hardware_facade: Optional hardware service facade
        configuration_service: Optional configuration service
        emergency_stop_service: Optional emergency stop service for hardware safety

    Returns:
        CLI application instance configured for production
    """
    return create_cli_application(
        use_case=use_case,
        hardware_facade=hardware_facade,
        configuration_service=configuration_service,
        emergency_stop_service=emergency_stop_service,
        mode=ConfigurationMode.PRODUCTION,
    )


def create_development_cli_application(
    use_case: Any,
    hardware_facade: Optional[Any] = None,
    configuration_service: Optional[Any] = None,
) -> ICLIApplication:
    """Create a CLI application in development mode.

    Args:
        use_case: EOL test execution use case
        hardware_facade: Optional hardware service facade
        configuration_service: Optional configuration service

    Returns:
        CLI application instance configured for development
    """
    return create_cli_application(
        use_case=use_case,
        hardware_facade=hardware_facade,
        configuration_service=configuration_service,
        mode=ConfigurationMode.DEVELOPMENT,
    )


def create_testing_cli_application(
    use_case: Any,
    hardware_facade: Optional[Any] = None,
    configuration_service: Optional[Any] = None,
) -> ICLIApplication:
    """Create a CLI application in testing mode.

    Args:
        use_case: EOL test execution use case
        hardware_facade: Optional hardware service facade
        configuration_service: Optional configuration service

    Returns:
        CLI application instance configured for testing
    """
    return create_cli_application(
        use_case=use_case,
        hardware_facade=hardware_facade,
        configuration_service=configuration_service,
        mode=ConfigurationMode.TESTING,
    )


def create_mock_cli_application(
    use_case: Any,
    hardware_facade: Optional[Any] = None,
    configuration_service: Optional[Any] = None,
) -> ICLIApplication:
    """Create a CLI application in mock mode.

    Args:
        use_case: EOL test execution use case
        hardware_facade: Optional hardware service facade
        configuration_service: Optional configuration service

    Returns:
        CLI application instance configured for mock testing
    """
    return create_cli_application(
        use_case=use_case,
        hardware_facade=hardware_facade,
        configuration_service=configuration_service,
        mode=ConfigurationMode.MOCK,
    )
