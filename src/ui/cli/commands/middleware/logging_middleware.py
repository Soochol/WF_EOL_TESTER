"""Logging Middleware

Provides comprehensive logging for command execution including performance
metrics, audit trails, and debugging information.
"""

import time
from typing import List, Optional, Tuple, Dict, Any
from loguru import logger

from ui.cli.commands.interfaces.command_interface import (
    ICommand,
    ICommandExecutionContext,
    CommandResult,
    MiddlewareResult,
)
from ui.cli.commands.middleware.base_middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    """Logging middleware for comprehensive command execution logging.

    Provides audit trails, performance metrics, and debugging information
    for all command executions.
    """

    def __init__(
        self,
        log_level: str = "INFO",
        include_args: bool = True,
        include_performance: bool = True,
        include_user_context: bool = True,
    ):
        """Initialize logging middleware.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            include_args: Whether to log command arguments
            include_performance: Whether to log performance metrics
            include_user_context: Whether to log user context information
        """
        super().__init__(name="logging", priority=1000)  # Low priority, run last

        self._log_level = log_level.upper()
        self._include_args = include_args
        self._include_performance = include_performance
        self._include_user_context = include_user_context
        self._start_times: Dict[str, float] = {}

        logger.debug(
            f"Logging middleware initialized: level={log_level}, "
            f"args={include_args}, perf={include_performance}, user={include_user_context}"
        )

    async def before_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> Tuple[MiddlewareResult, Optional[CommandResult]]:
        """Log command execution start.

        Args:
            command: Command about to be executed
            args: Command arguments
            context: Execution context

        Returns:
            Tuple of (CONTINUE, None) to proceed with execution
        """
        execution_id = self._generate_execution_id(command, context)
        start_time = time.perf_counter()
        self._start_times[execution_id] = start_time

        # Build log message
        log_data = {
            "event": "command_start",
            "command": command.metadata.name,
            "execution_id": execution_id,
        }

        if self._include_args and args:
            log_data["args"] = args

        if self._include_user_context:
            log_data["user_id"] = context.user_id
            log_data["session_id"] = context.session_data.get("session_id")

        # Add command metadata
        log_data["command_category"] = command.metadata.category
        log_data["command_version"] = command.metadata.version

        if command.metadata.deprecated:
            log_data["deprecated"] = True
            logger.warning(
                f"DEPRECATED COMMAND EXECUTED: {log_data}",
                extra={"structured": True, "data": log_data}
            )
        else:
            logger.info(
                f"Command execution started: /{command.metadata.name}",
                extra={"structured": True, "data": log_data}
            )

        return MiddlewareResult.CONTINUE, None

    async def after_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
        result: CommandResult,
    ) -> CommandResult:
        """Log command execution completion.

        Args:
            command: Command that was executed
            args: Command arguments
            context: Execution context
            result: Command execution result

        Returns:
            Command result with logging metadata
        """
        execution_id = self._generate_execution_id(command, context)
        end_time = time.perf_counter()

        # Calculate execution time
        start_time = self._start_times.pop(execution_id, end_time)
        execution_time_ms = (end_time - start_time) * 1000

        # Build log message
        log_data = {
            "event": "command_complete",
            "command": command.metadata.name,
            "execution_id": execution_id,
            "status": result.status.value,
            "execution_time_ms": execution_time_ms,
        }

        if self._include_args and args:
            log_data["args"] = args

        if self._include_user_context:
            log_data["user_id"] = context.user_id

        if self._include_performance:
            log_data["performance"] = {
                "execution_time_ms": execution_time_ms,
                "result_data_size": len(str(result.data)) if result.data else 0,
                "middleware_data_size": len(str(result.middleware_data)) if result.middleware_data else 0,
            }

        # Add error details if present
        if result.error_details:
            log_data["error_details"] = result.error_details

        # Choose log level based on result status
        if result.status.value == "error":
            logger.error(
                f"Command execution failed: /{command.metadata.name} - {result.message}",
                extra={"structured": True, "data": log_data}
            )
        elif result.status.value == "warning":
            logger.warning(
                f"Command execution warning: /{command.metadata.name} - {result.message}",
                extra={"structured": True, "data": log_data}
            )
        else:
            logger.info(
                f"Command execution completed: /{command.metadata.name}",
                extra={"structured": True, "data": log_data}
            )

        # Add logging info to result metadata
        if result.middleware_data is None:
            result.middleware_data = {}

        result.middleware_data["logging"] = {
            "execution_id": execution_id,
            "logged_at": time.time(),
            "execution_time_ms": execution_time_ms,
        }

        return result

    async def on_error(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
        error: Exception,
    ) -> Optional[CommandResult]:
        """Log command execution errors.

        Args:
            command: Command that encountered error
            args: Command arguments
            context: Execution context
            error: Exception that occurred

        Returns:
            None to use default error handling
        """
        execution_id = self._generate_execution_id(command, context)

        # Build error log message
        log_data = {
            "event": "command_error",
            "command": command.metadata.name,
            "execution_id": execution_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

        if self._include_args and args:
            log_data["args"] = args

        if self._include_user_context:
            log_data["user_id"] = context.user_id

        # Log the error
        logger.error(
            f"Command execution error: /{command.metadata.name} - {str(error)}",
            extra={"structured": True, "data": log_data, "exception": error}
        )

        # Clean up timing data
        self._start_times.pop(execution_id, None)

        return None  # Let default error handling proceed

    def _generate_execution_id(self, command: ICommand, context: ICommandExecutionContext) -> str:
        """Generate unique execution ID for tracking.

        Args:
            command: Command being executed
            context: Execution context

        Returns:
            Unique execution identifier
        """
        import hashlib

        # Create unique ID based on command, user, and timestamp
        id_components = [
            command.metadata.name,
            context.user_id or "anonymous",
            str(time.time()),
            str(id(context))  # Memory address for uniqueness
        ]

        id_string = ":".join(id_components)
        return hashlib.md5(id_string.encode()).hexdigest()[:12]

    def set_log_level(self, log_level: str) -> None:
        """Set the logging level.

        Args:
            log_level: New logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self._log_level = log_level.upper()
        logger.debug(f"Logging middleware level changed to: {self._log_level}")

    def enable_argument_logging(self) -> None:
        """Enable logging of command arguments."""
        self._include_args = True
        logger.debug("Enabled argument logging")

    def disable_argument_logging(self) -> None:
        """Disable logging of command arguments for privacy."""
        self._include_args = False
        logger.debug("Disabled argument logging")

    def enable_performance_logging(self) -> None:
        """Enable performance metrics logging."""
        self._include_performance = True
        logger.debug("Enabled performance logging")

    def disable_performance_logging(self) -> None:
        """Disable performance metrics logging."""
        self._include_performance = False
        logger.debug("Disabled performance logging")

    def get_active_executions(self) -> int:
        """Get count of currently active command executions.

        Returns:
            Number of commands currently being executed
        """
        return len(self._start_times)
