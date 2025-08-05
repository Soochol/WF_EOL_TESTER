"""Component Configuration System

Configuration for component bindings, environment-specific configurations,
service lifetime management, and interface implementation selection.
Supports different operational modes with appropriate service configurations.

Key Features:
- Configuration for component bindings
- Environment-specific configurations (production, development, testing)
- Service lifetime management
- Interface implementation selection
- Mock mode support for testing
"""

from enum import Enum
from typing import Any, Dict, Optional, Type

from ..container.dependency_container import ServiceLifetime


class ConfigurationMode(Enum):
    """Enumeration for different configuration modes.

    Defines operational modes that determine which implementations
    and configurations should be used.
    """

    PRODUCTION = "production"  # Full production configuration
    DEVELOPMENT = "development"  # Development mode with debugging
    TESTING = "testing"  # Testing mode with mocks
    MOCK = "mock"  # Mock mode for testing without hardware


class ComponentConfig:
    """Configuration for component bindings and service lifetimes.

    Provides centralized configuration for dependency injection container
    with support for different operational modes and environment-specific
    settings. Manages interface-to-implementation mappings and service
    lifetime configuration.
    """

    def __init__(self, mode: ConfigurationMode = ConfigurationMode.PRODUCTION):
        """Initialize component configuration.

        Args:
            mode: Configuration mode determining service implementations
        """
        self.mode = mode
        self._service_configurations: Dict[Type, Dict[str, Any]] = {}
        self._default_lifetimes: Dict[Type, ServiceLifetime] = {}

        # Initialize default configurations
        self._setup_default_configurations()

    def _setup_default_configurations(self) -> None:
        """Setup default service configurations based on mode."""
        # Import interfaces
        from ..interfaces.application_interface import ICLIApplication
        from ..interfaces.execution_interface import ITestExecutor
        from ..interfaces.formatter_interface import IFormatter
        from ..interfaces.menu_interface import IMenuSystem
        from ..interfaces.session_interface import ISessionManager
        from ..interfaces.validation_interface import IInputValidator

        # Default lifetime configurations
        self._default_lifetimes = {
            ICLIApplication: ServiceLifetime.SINGLETON,
            ISessionManager: ServiceLifetime.SINGLETON,
            IMenuSystem: ServiceLifetime.SINGLETON,
            ITestExecutor: ServiceLifetime.SINGLETON,
            IFormatter: ServiceLifetime.SINGLETON,
            IInputValidator: ServiceLifetime.SINGLETON,
        }

        # Mode-specific configurations
        if self.mode == ConfigurationMode.PRODUCTION:
            self._setup_production_config()
        elif self.mode == ConfigurationMode.DEVELOPMENT:
            self._setup_development_config()
        elif self.mode == ConfigurationMode.TESTING:
            self._setup_testing_config()
        elif self.mode == ConfigurationMode.MOCK:
            self._setup_mock_config()

    def _setup_production_config(self) -> None:
        """Setup production configuration with full implementations."""
        # Import interfaces
        from ..interfaces.application_interface import ICLIApplication
        from ..interfaces.execution_interface import ITestExecutor
        from ..interfaces.formatter_interface import IFormatter
        from ..interfaces.menu_interface import IMenuSystem
        from ..interfaces.session_interface import ISessionManager
        from ..interfaces.validation_interface import IInputValidator

        # Import concrete implementations
        from ..validation.input_validator import InputValidator

        # Production service mappings - using direct component creation in factory
        self._service_configurations = {
            IInputValidator: {
                "implementation": InputValidator,
                "lifetime": ServiceLifetime.SINGLETON,
            },
        }

    def _setup_development_config(self) -> None:
        """Setup development configuration with debugging support."""
        # Use same implementations as production but with transient lifetimes
        # for easier debugging and state isolation
        self._setup_production_config()

        # Override lifetimes for development
        for interface_type in self._service_configurations:
            self._service_configurations[interface_type]["lifetime"] = ServiceLifetime.TRANSIENT

    def _setup_testing_config(self) -> None:
        """Setup testing configuration with mock implementations."""
        # For now, use production implementations
        # In a full implementation, these would be test doubles/mocks
        self._setup_production_config()

        # Override lifetimes for testing isolation
        for interface_type in self._service_configurations:
            self._service_configurations[interface_type]["lifetime"] = ServiceLifetime.TRANSIENT

    def _setup_mock_config(self) -> None:
        """Setup mock configuration for testing without hardware."""
        # For now, use production implementations
        # In a full implementation, these would be mock implementations
        self._setup_production_config()

        # Use transient lifetimes for mocks
        for interface_type in self._service_configurations:
            self._service_configurations[interface_type]["lifetime"] = ServiceLifetime.TRANSIENT

    def get_implementation(self, interface_type: Type) -> Optional[Type]:
        """Get the implementation type for an interface.

        Args:
            interface_type: The interface type to get implementation for

        Returns:
            Implementation type if configured, None otherwise
        """
        config = self._service_configurations.get(interface_type)
        return config.get("implementation") if config else None

    def get_lifetime(self, interface_type: Type) -> ServiceLifetime:
        """Get the service lifetime for an interface.

        Args:
            interface_type: The interface type to get lifetime for

        Returns:
            Service lifetime for the interface
        """
        config = self._service_configurations.get(interface_type)
        if config and "lifetime" in config:
            return config["lifetime"]

        # Return default lifetime if configured
        return self._default_lifetimes.get(interface_type, ServiceLifetime.TRANSIENT)

    def get_factory(self, interface_type: Type) -> Optional[Any]:
        """Get the factory function for an interface.

        Args:
            interface_type: The interface type to get factory for

        Returns:
            Factory function if configured, None otherwise
        """
        config = self._service_configurations.get(interface_type)
        return config.get("factory") if config else None

    def get_all_configurations(self) -> Dict[Type, Dict[str, Any]]:
        """Get all service configurations.

        Returns:
            Dictionary of all configured services and their settings
        """
        return self._service_configurations.copy()

    def override_configuration(
        self,
        interface_type: Type,
        implementation: Optional[Type] = None,
        factory: Optional[Any] = None,
        lifetime: Optional[ServiceLifetime] = None,
    ) -> None:
        """Override configuration for a specific interface.

        Args:
            interface_type: The interface type to override
            implementation: New implementation type
            factory: New factory function
            lifetime: New service lifetime
        """
        if interface_type not in self._service_configurations:
            self._service_configurations[interface_type] = {}

        config = self._service_configurations[interface_type]

        if implementation is not None:
            config["implementation"] = implementation
        if factory is not None:
            config["factory"] = factory
        if lifetime is not None:
            config["lifetime"] = lifetime