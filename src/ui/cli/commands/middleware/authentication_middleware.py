"""Authentication Middleware

Provides user authentication and authorization for command execution.
Integrates with session management and user permission systems.
"""

from typing import List, Optional, Set, Tuple
from loguru import logger

from ui.cli.commands.interfaces.command_interface import (
    ICommand,
    ICommandExecutionContext,
    CommandResult,
    MiddlewareResult,
)
from ui.cli.commands.middleware.base_middleware import BaseMiddleware


class AuthenticationMiddleware(BaseMiddleware):
    """Authentication middleware for command authorization.

    Validates user authentication and checks permissions before
    allowing command execution.
    """

    def __init__(
        self,
        require_authentication: bool = False,
        admin_commands: Optional[Set[str]] = None,
        guest_allowed_commands: Optional[Set[str]] = None,
    ):
        """Initialize authentication middleware.

        Args:
            require_authentication: Whether to require user authentication
            admin_commands: Set of commands requiring admin privileges
            guest_allowed_commands: Set of commands allowed for guest users
        """
        super().__init__(name="authentication", priority=10)  # High priority

        self._require_authentication = require_authentication
        self._admin_commands = admin_commands or set()
        self._guest_allowed_commands = guest_allowed_commands or {
            "help", "exit", "version"
        }

        logger.debug(
            f"Authentication middleware initialized: "
            f"require_auth={require_authentication}, "
            f"admin_commands={len(self._admin_commands)}, "
            f"guest_commands={len(self._guest_allowed_commands)}"
        )

    async def before_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> Tuple[MiddlewareResult, Optional[CommandResult]]:
        """Validate authentication before command execution.

        Args:
            command: Command about to be executed
            args: Command arguments
            context: Execution context

        Returns:
            Tuple of middleware result and optional command result
        """
        command_name = command.metadata.name

        self.log_middleware_action("checking authentication", command)

        # Check if command requires authentication
        if not self._require_authentication and command_name in self._guest_allowed_commands:
            return MiddlewareResult.CONTINUE, None

        # Get user information from context
        user_id = context.user_id
        session_data = context.session_data

        # Check if user is authenticated
        if not user_id:
            if self._require_authentication or command_name not in self._guest_allowed_commands:
                self.log_middleware_action("authentication required", command, "no user_id")
                return MiddlewareResult.STOP, CommandResult.error(
                    "Authentication required. Please log in to execute this command.",
                    error_details={"reason": "no_authentication", "command": command_name},
                )

        # Check admin permissions
        if command_name in self._admin_commands:
            user_role = session_data.get("role", "user")
            if user_role != "admin":
                self.log_middleware_action(
                    "admin permission denied", command, f"user_role={user_role}"
                )
                return MiddlewareResult.STOP, CommandResult.error(
                    f"Administrator privileges required for command: /{command_name}",
                    error_details={
                        "reason": "insufficient_privileges",
                        "required_role": "admin",
                        "user_role": user_role,
                        "command": command_name,
                    },
                )

        # Check command-specific permissions
        if command.metadata.permissions:
            user_permissions = set(session_data.get("permissions", []))
            required_permissions = set(command.metadata.permissions)

            if not required_permissions.issubset(user_permissions):
                missing_permissions = required_permissions - user_permissions
                self.log_middleware_action(
                    "permission denied",
                    command,
                    f"missing: {missing_permissions}"
                )
                return MiddlewareResult.STOP, CommandResult.error(
                    f"Insufficient permissions for command: /{command_name}. "
                    f"Required: {', '.join(missing_permissions)}",
                    error_details={
                        "reason": "missing_permissions",
                        "required_permissions": list(required_permissions),
                        "user_permissions": list(user_permissions),
                        "missing_permissions": list(missing_permissions),
                        "command": command_name,
                    },
                )

        # Authentication successful
        self.log_middleware_action("authentication passed", command, f"user={user_id}")
        return MiddlewareResult.CONTINUE, None

    async def after_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
        result: CommandResult,
    ) -> CommandResult:
        """Process result after command execution.

        Args:
            command: Command that was executed
            args: Command arguments
            context: Execution context
            result: Command execution result

        Returns:
            Command result (may be modified)
        """
        # Add authentication info to result metadata
        if result.middleware_data is None:
            result.middleware_data = {}

        result.middleware_data["authentication"] = {
            "user_id": context.user_id,
            "authenticated": context.user_id is not None,
            "timestamp": __import__("time").time(),
        }

        return result

    def add_admin_command(self, command_name: str) -> None:
        """Add a command to the admin-only list.

        Args:
            command_name: Name of command requiring admin privileges
        """
        self._admin_commands.add(command_name)
        logger.debug(f"Added admin command: {command_name}")

    def add_guest_command(self, command_name: str) -> None:
        """Add a command to the guest-allowed list.

        Args:
            command_name: Name of command allowed for guests
        """
        self._guest_allowed_commands.add(command_name)
        logger.debug(f"Added guest command: {command_name}")

    def remove_admin_command(self, command_name: str) -> None:
        """Remove a command from the admin-only list.

        Args:
            command_name: Name of command to remove from admin list
        """
        self._admin_commands.discard(command_name)
        logger.debug(f"Removed admin command: {command_name}")

    def get_admin_commands(self) -> Set[str]:
        """Get the set of admin-only commands.

        Returns:
            Set of command names requiring admin privileges
        """
        return self._admin_commands.copy()

    def get_guest_commands(self) -> Set[str]:
        """Get the set of guest-allowed commands.

        Returns:
            Set of command names allowed for guests
        """
        return self._guest_allowed_commands.copy()
