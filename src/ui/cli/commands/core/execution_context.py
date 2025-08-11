"""Command Execution Context Implementation

Provides concrete implementation of command execution context with
dependency injection integration and session management.
"""

from typing import Any, Dict, Optional

from loguru import logger

from src.ui.cli.commands.interfaces.command_interface import ICommandExecutionContext
from src.ui.cli.container.dependency_container import DependencyContainer


class CommandExecutionContext(ICommandExecutionContext):
    """Concrete implementation of command execution context.

    Provides stateful information and services during command execution
    including user session, configuration, and dependency injection.
    """

    def __init__(
        self,
        container: DependencyContainer,
        user_id: Optional[str] = None,
        session_data: Optional[Dict[str, Any]] = None,
        configuration: Optional[Dict[str, Any]] = None,
    ):
        """Initialize execution context.

        Args:
            container: Dependency injection container
            user_id: Optional user identifier
            session_data: Optional session-specific data
            configuration: Optional configuration data
        """
        self._container = container
        self._user_id = user_id
        self._session_data = session_data or {}
        self._configuration = configuration or {}
        self._context_data: Dict[str, Any] = {}

        logger.debug(f"Created execution context for user: {user_id}")

    @property
    def user_id(self) -> Optional[str]:
        """Get the current user identifier."""
        return self._user_id

    @property
    def session_data(self) -> Dict[str, Any]:
        """Get session-specific data."""
        return self._session_data.copy()

    @property
    def configuration(self) -> Dict[str, Any]:
        """Get command execution configuration."""
        return self._configuration.copy()

    def get_service(self, service_type: type) -> Any:
        """Resolve a service from the dependency injection container.

        Args:
            service_type: The interface type to resolve

        Returns:
            Service instance implementing the requested interface

        Raises:
            ValueError: If service cannot be resolved
        """
        try:
            service = self._container.resolve(service_type)
            logger.debug(f"Resolved service: {service_type.__name__}")
            return service
        except Exception as e:
            logger.error(f"Failed to resolve service {service_type.__name__}: {e}")
            raise ValueError(f"Could not resolve service {service_type.__name__}: {e}") from e

    def set_data(self, key: str, value: Any) -> None:
        """Set context-specific data.

        Args:
            key: Data key
            value: Data value
        """
        self._context_data[key] = value
        logger.debug(f"Set context data: {key}")

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get context-specific data.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Data value or default
        """
        return self._context_data.get(key, default)

    def update_session_data(self, data: Dict[str, Any]) -> None:
        """Update session data.

        Args:
            data: Data to merge into session
        """
        self._session_data.update(data)
        logger.debug(f"Updated session data with {len(data)} items")

    def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update configuration data.

        Args:
            config: Configuration to merge
        """
        self._configuration.update(config)
        logger.debug(f"Updated configuration with {len(config)} items")

    def clear_context_data(self) -> None:
        """Clear all context-specific data."""
        self._context_data.clear()
        logger.debug("Cleared context data")

    def get_all_context_data(self) -> Dict[str, Any]:
        """Get all context data for debugging.

        Returns:
            Dictionary containing all context information
        """
        return {
            "user_id": self._user_id,
            "session_data": self._session_data,
            "configuration": self._configuration,
            "context_data": self._context_data,
        }
