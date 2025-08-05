"""Base Middleware Implementation

Provides a base class for middleware implementations with common functionality
and default behavior patterns.
"""

from abc import ABC
from typing import List, Optional, Tuple
from loguru import logger

from ui.cli.commands.interfaces.command_interface import (
    ICommand,
    ICommandExecutionContext,
    ICommandMiddleware,
    CommandResult,
    MiddlewareResult,
)


class BaseMiddleware(ICommandMiddleware, ABC):
    """Base implementation for command middleware.

    Provides common functionality and default implementations for middleware
    components. Subclasses should override specific methods as needed.
    """

    def __init__(self, name: str, priority: int = 100):
        """Initialize base middleware.

        Args:
            name: Middleware name for identification
            priority: Execution priority (lower numbers execute first)
        """
        self._name = name
        self._priority = priority

        logger.debug(f"Initialized middleware: {name} (priority: {priority})")

    @property
    def name(self) -> str:
        """Get middleware name for identification."""
        return self._name

    @property
    def priority(self) -> int:
        """Get middleware priority (lower numbers execute first)."""
        return self._priority

    async def before_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> Tuple[MiddlewareResult, Optional[CommandResult]]:
        """Default before_execute implementation.

        Args:
            command: Command about to be executed
            args: Command arguments
            context: Execution context

        Returns:
            Tuple of (CONTINUE, None) to proceed with execution
        """
        return MiddlewareResult.CONTINUE, None

    async def after_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
        result: CommandResult,
    ) -> CommandResult:
        """Default after_execute implementation.

        Args:
            command: Command that was executed
            args: Command arguments
            context: Execution context
            result: Command execution result

        Returns:
            Unmodified command result
        """
        return result

    async def on_error(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
        error: Exception,
    ) -> Optional[CommandResult]:
        """Default error handling implementation.

        Args:
            command: Command that encountered error
            args: Command arguments
            context: Execution context
            error: Exception that occurred

        Returns:
            None to use default error handling
        """
        return None

    def should_apply_to_command(self, command: ICommand) -> bool:
        """Determine if middleware should apply to a specific command.

        Args:
            command: Command to check

        Returns:
            True if middleware should be applied
        """
        return True  # Apply to all commands by default

    def log_middleware_action(
        self,
        action: str,
        command: ICommand,
        details: Optional[str] = None,
    ) -> None:
        """Log middleware actions for debugging.

        Args:
            action: Action being performed
            command: Command being processed
            details: Optional additional details
        """
        log_message = f"Middleware {self.name}: {action} for command /{command.metadata.name}"
        if details:
            log_message += f" - {details}"

        logger.debug(log_message)
