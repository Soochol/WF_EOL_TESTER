"""Command Factory Implementation

Provides factory for creating commands with dependency injection integration
and lifecycle management. Supports configuration-driven command creation
and component integration.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from loguru import logger

from ui.cli.commands.interfaces.command_interface import (
    ICommand,
    ICommandMiddleware,
    CommandMetadata,
)
from ui.cli.container.dependency_container import DependencyContainer

# Type variable for command creation
T = TypeVar("T", bound=ICommand)


class CommandFactory:
    """Factory for creating commands with dependency injection.

    Provides centralized command creation with dependency injection,
    configuration management, and lifecycle support.
    """

    def __init__(self, container: DependencyContainer):
        """Initialize command factory.

        Args:
            container: Dependency injection container
        """
        self._container = container
        self._command_configurations: Dict[str, Dict[str, Any]] = {}
        self._middleware_configurations: Dict[str, Dict[str, Any]] = {}

        logger.debug("Initialized command factory")

    def create_command(
        self,
        command_type: Type[T],
        configuration: Optional[Dict[str, Any]] = None,
    ) -> T:
        """Create a command instance with dependency injection.

        Args:
            command_type: Type of command to create
            configuration: Optional configuration override

        Returns:
            Command instance with dependencies injected

        Raises:
            ValueError: If command cannot be created
        """
        try:
            # Get or create configuration
            config = configuration or self._get_command_configuration(
                command_type.__name__
            )

            # Create instance using dependency injection
            if config:
                # Create with configuration parameters
                command = self._create_with_config(command_type, config)
            else:
                # Create using container's automatic injection
                command = self._container.resolve(command_type)

            logger.debug(f"Created command: {command_type.__name__}")
            return command

        except Exception as e:
            logger.error(f"Failed to create command {command_type.__name__}: {e}")
            raise ValueError(f"Command creation failed: {e}")

    def create_command_by_name(
        self,
        command_name: str,
        command_type: Type[T],
        configuration: Optional[Dict[str, Any]] = None,
    ) -> T:
        """Create a command by name with configuration lookup.

        Args:
            command_name: Name of command for configuration lookup
            command_type: Type of command to create
            configuration: Optional configuration override

        Returns:
            Command instance with dependencies injected
        """
        # Use stored configuration for the named command
        config = configuration or self._command_configurations.get(command_name, {})

        return self.create_command(command_type, config)

    def create_middleware(
        self,
        middleware_type: Type[ICommandMiddleware],
        configuration: Optional[Dict[str, Any]] = None,
    ) -> ICommandMiddleware:
        """Create a middleware instance with dependency injection.

        Args:
            middleware_type: Type of middleware to create
            configuration: Optional configuration override

        Returns:
            Middleware instance with dependencies injected

        Raises:
            ValueError: If middleware cannot be created
        """
        try:
            # Get or create configuration
            config = configuration or self._get_middleware_configuration(
                middleware_type.__name__
            )

            # Create instance
            if config:
                middleware = self._create_with_config(middleware_type, config)
            else:
                # Try container resolution first
                try:
                    middleware = self._container.resolve(middleware_type)
                except ValueError:
                    # Fallback to direct instantiation
                    middleware = middleware_type()

            logger.debug(f"Created middleware: {middleware_type.__name__}")
            return middleware

        except Exception as e:
            logger.error(f"Failed to create middleware {middleware_type.__name__}: {e}")
            raise ValueError(f"Middleware creation failed: {e}")

    def register_command_configuration(
        self,
        command_name: str,
        configuration: Dict[str, Any],
    ) -> None:
        """Register configuration for a specific command.

        Args:
            command_name: Name of command
            configuration: Configuration parameters
        """
        self._command_configurations[command_name] = configuration
        logger.debug(f"Registered configuration for command: {command_name}")

    def register_middleware_configuration(
        self,
        middleware_name: str,
        configuration: Dict[str, Any],
    ) -> None:
        """Register configuration for a specific middleware.

        Args:
            middleware_name: Name of middleware
            configuration: Configuration parameters
        """
        self._middleware_configurations[middleware_name] = configuration
        logger.debug(f"Registered configuration for middleware: {middleware_name}")

    def create_command_with_metadata(
        self,
        command_type: Type[T],
        metadata: CommandMetadata,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> T:
        """Create a command with specific metadata.

        Args:
            command_type: Type of command to create
            metadata: Command metadata to use
            configuration: Optional configuration

        Returns:
            Command instance with specified metadata
        """
        # Add metadata to configuration
        config = configuration or {}
        config["metadata"] = metadata

        return self.create_command(command_type, config)

    def create_command_chain(
        self,
        command_configs: List[Dict[str, Any]],
    ) -> List[ICommand]:
        """Create a chain of commands from configuration.

        Args:
            command_configs: List of command configurations, each containing
                          'type' and optional 'config' keys

        Returns:
            List of created command instances

        Raises:
            ValueError: If any command in the chain cannot be created
        """
        commands = []

        for i, config in enumerate(command_configs):
            try:
                if "type" not in config:
                    raise ValueError(f"Command config {i} missing 'type' key")

                command_type = config["type"]
                command_config = config.get("config", {})

                command = self.create_command(command_type, command_config)
                commands.append(command)

            except Exception as e:
                logger.error(f"Failed to create command {i} in chain: {e}")
                raise ValueError(f"Command chain creation failed at index {i}: {e}")

        logger.debug(f"Created command chain with {len(commands)} commands")
        return commands

    def create_middleware_chain(
        self,
        middleware_configs: List[Dict[str, Any]],
    ) -> List[ICommandMiddleware]:
        """Create a chain of middleware from configuration.

        Args:
            middleware_configs: List of middleware configurations, each containing
                              'type' and optional 'config' keys

        Returns:
            List of created middleware instances ordered by priority
        """
        middleware_list = []

        for i, config in enumerate(middleware_configs):
            try:
                if "type" not in config:
                    raise ValueError(f"Middleware config {i} missing 'type' key")

                middleware_type = config["type"]
                middleware_config = config.get("config", {})

                middleware = self.create_middleware(middleware_type, middleware_config)
                middleware_list.append(middleware)

            except Exception as e:
                logger.error(f"Failed to create middleware {i} in chain: {e}")
                raise ValueError(f"Middleware chain creation failed at index {i}: {e}")

        # Sort by priority
        middleware_list.sort(key=lambda m: m.priority)

        logger.debug(f"Created middleware chain with {len(middleware_list)} middleware")
        return middleware_list

    def _create_with_config(self, instance_type: Type, config: Dict[str, Any]) -> Any:
        """Create instance with configuration parameters.

        Args:
            instance_type: Type to create
            config: Configuration parameters

        Returns:
            Created instance
        """
        import inspect

        # Get constructor signature
        signature = inspect.signature(instance_type.__init__)

        # Build constructor arguments
        constructor_args = {}

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            # Check if config provides this parameter
            if param_name in config:
                constructor_args[param_name] = config[param_name]
            elif param.annotation != inspect.Parameter.empty:
                # Try to resolve from container
                try:
                    dependency = self._container.resolve(param.annotation)
                    constructor_args[param_name] = dependency
                except ValueError:
                    # Check if parameter has default
                    if param.default == inspect.Parameter.empty:
                        logger.warning(
                            f"Could not resolve parameter {param_name} for {instance_type.__name__}"
                        )

        # Create instance
        return instance_type(**constructor_args)

    def _get_command_configuration(self, command_type_name: str) -> Dict[str, Any]:
        """Get configuration for a command type.

        Args:
            command_type_name: Name of command type

        Returns:
            Configuration dictionary
        """
        return self._command_configurations.get(command_type_name, {})

    def _get_middleware_configuration(self, middleware_type_name: str) -> Dict[str, Any]:
        """Get configuration for a middleware type.

        Args:
            middleware_type_name: Name of middleware type

        Returns:
            Configuration dictionary
        """
        return self._middleware_configurations.get(middleware_type_name, {})

    def get_registered_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered configurations.

        Returns:
            Dictionary containing command and middleware configurations
        """
        return {
            "commands": self._command_configurations.copy(),
            "middleware": self._middleware_configurations.copy(),
        }

    def clear_configurations(self) -> None:
        """Clear all registered configurations."""
        self._command_configurations.clear()
        self._middleware_configurations.clear()
        logger.debug("Cleared all factory configurations")

    def set_container(self, container: DependencyContainer) -> None:
        """Set or update the dependency injection container.

        Args:
            container: New dependency injection container
        """
        self._container = container
        logger.debug("Updated dependency injection container")
