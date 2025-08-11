"""Error Handling Middleware

Provides comprehensive error handling and recovery for command execution
with user-friendly error messages and debugging support.
"""

import traceback
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from ui.cli.commands.interfaces.command_interface import (
    CommandResult,
    ICommand,
    ICommandExecutionContext,
    MiddlewareResult,
)
from ui.cli.commands.middleware.base_middleware import BaseMiddleware


class ErrorHandlingMiddleware(BaseMiddleware):
    """Error handling middleware for comprehensive error processing.

    Provides user-friendly error messages, recovery mechanisms,
    and debugging support for command execution failures.
    """

    def __init__(
        self,
        include_stack_trace: bool = False,
        enable_recovery_suggestions: bool = True,
        max_error_message_length: int = 500,
    ):
        """Initialize error handling middleware.

        Args:
            include_stack_trace: Whether to include stack traces in error responses
            enable_recovery_suggestions: Whether to provide recovery suggestions
            max_error_message_length: Maximum length for error messages
        """
        super().__init__(name="error_handling", priority=900)  # Low priority, but before logging

        self._include_stack_trace = include_stack_trace
        self._enable_recovery_suggestions = enable_recovery_suggestions
        self._max_error_message_length = max_error_message_length
        self._error_counts: Dict[str, int] = {}

        logger.debug(
            f"Error handling middleware initialized: "
            f"stack_trace={include_stack_trace}, "
            f"suggestions={enable_recovery_suggestions}, "
            f"max_length={max_error_message_length}"
        )

    async def before_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> Tuple[MiddlewareResult, Optional[CommandResult]]:
        """Before execution - no special handling needed.

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
        """Process result after command execution.

        Args:
            command: Command that was executed
            args: Command arguments
            context: Execution context
            result: Command execution result

        Returns:
            Enhanced command result with error handling metadata
        """
        # Add error handling metadata
        if result.middleware_data is None:
            result.middleware_data = {}

        result.middleware_data["error_handling"] = {
            "processed_by_error_handler": True,
            "error_count": self._error_counts.get(command.metadata.name, 0),
        }

        # If it's an error result, enhance it
        if result.status.value == "error":
            result = self._enhance_error_result(result, command, args, context)

        return result

    async def on_error(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
        error: Exception,
    ) -> Optional[CommandResult]:
        """Handle command execution errors with comprehensive error processing.

        Args:
            command: Command that encountered error
            args: Command arguments
            context: Execution context
            error: Exception that occurred

        Returns:
            Enhanced CommandResult with user-friendly error information
        """
        command_name = command.metadata.name

        # Track error count for this command
        self._error_counts[command_name] = self._error_counts.get(command_name, 0) + 1

        self.log_middleware_action(
            "handling error", command, f"{type(error).__name__}: {str(error)[:100]}"
        )

        # Create enhanced error result
        error_result = self._create_enhanced_error_result(error, command, args, context)

        return error_result

    def _create_enhanced_error_result(
        self,
        error: Exception,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> CommandResult:
        """Create an enhanced error result with comprehensive information.

        Args:
            error: Exception that occurred
            command: Command that failed
            args: Command arguments
            context: Execution context

        Returns:
            Enhanced CommandResult with error details
        """
        error_type = type(error).__name__
        error_message = str(error)

        # Create user-friendly error message
        user_message = self._create_user_friendly_message(error, command)

        # Truncate message if too long
        if len(user_message) > self._max_error_message_length:
            user_message = user_message[: self._max_error_message_length - 3] + "..."

        # Build comprehensive error details
        error_details = {
            "command": command.metadata.name,
            "error_type": error_type,
            "error_message": error_message,
            "args": args,
            "user_id": context.user_id,
            "error_count": self._error_counts.get(command.metadata.name, 0),
        }

        # Add stack trace if enabled
        if self._include_stack_trace:
            error_details["stack_trace"] = traceback.format_exc()

        # Add recovery suggestions if enabled
        if self._enable_recovery_suggestions:
            suggestions = self._get_recovery_suggestions(error, command, args)
            if suggestions:
                error_details["recovery_suggestions"] = suggestions

        # Add context information
        error_details["context"] = {
            "session_data_keys": list(context.session_data.keys()),
            "configuration_keys": list(context.configuration.keys()),
        }

        return CommandResult.error(
            message=user_message,
            error_details=error_details,
        )

    def _enhance_error_result(
        self,
        result: CommandResult,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> CommandResult:
        """Enhance an existing error result with additional information.

        Args:
            result: Existing error result
            command: Command that failed
            args: Command arguments
            context: Execution context

        Returns:
            Enhanced error result
        """
        if result.error_details is None:
            result.error_details = {}

        # Add error handling enhancements
        result.error_details.update(
            {
                "enhanced_by_error_handler": True,
                "error_count": self._error_counts.get(command.metadata.name, 0),
            }
        )

        # Add recovery suggestions if not present and enabled
        if self._enable_recovery_suggestions and "recovery_suggestions" not in result.error_details:

            # Try to infer error type from message
            suggestions = self._get_recovery_suggestions_from_message(result.message, command, args)
            if suggestions:
                result.error_details["recovery_suggestions"] = suggestions

        return result

    def _create_user_friendly_message(self, error: Exception, command: ICommand) -> str:
        """Create a user-friendly error message.

        Args:
            error: Exception that occurred
            command: Command that failed

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        error_message = str(error)
        command_name = command.metadata.name

        # Handle common error types with user-friendly messages
        if error_type == "ValueError":
            return f"Invalid input for command /{command_name}: {error_message}"
        elif error_type == "TypeError":
            return f"Incorrect usage of command /{command_name}: {error_message}"
        elif error_type == "FileNotFoundError":
            return f"Required file not found for command /{command_name}: {error_message}"
        elif error_type == "PermissionError":
            return f"Permission denied for command /{command_name}: {error_message}"
        elif error_type == "ConnectionError":
            return f"Connection failed for command /{command_name}: {error_message}"
        elif error_type == "TimeoutError":
            return f"Command /{command_name} timed out: {error_message}"
        elif error_type == "KeyboardInterrupt":
            return f"Command /{command_name} was cancelled by user"
        else:
            # Generic error message
            return f"Command /{command_name} failed: {error_message}"

    def _get_recovery_suggestions(
        self, error: Exception, command: ICommand, args: List[str]
    ) -> List[str]:
        """Get recovery suggestions based on error type and context.

        Args:
            error: Exception that occurred
            command: Command that failed
            args: Command arguments

        Returns:
            List of recovery suggestions
        """
        suggestions = []
        error_type = type(error).__name__
        command_name = command.metadata.name

        if error_type == "ValueError":
            suggestions.extend(
                [
                    f"Check the arguments for command /{command_name}",
                    f"Use '/{command_name} help' for usage information",
                    "Verify that all required arguments are provided",
                ]
            )
        elif error_type == "FileNotFoundError":
            suggestions.extend(
                [
                    "Check that all required files exist",
                    "Verify file paths are correct",
                    "Ensure you have access to the specified files",
                ]
            )
        elif error_type == "PermissionError":
            suggestions.extend(
                [
                    "Check your user permissions",
                    "Try running with appropriate privileges",
                    "Contact your administrator if needed",
                ]
            )
        elif error_type == "ConnectionError":
            suggestions.extend(
                [
                    "Check your network connection",
                    "Verify service endpoints are accessible",
                    "Try again in a few moments",
                ]
            )
        elif error_type == "TimeoutError":
            suggestions.extend(
                [
                    "Try running the command again",
                    "Check if the system is under heavy load",
                    "Consider using a shorter timeout if available",
                ]
            )

        # Add general suggestions
        if not suggestions:
            suggestions.extend(
                [
                    f"Use '/{command_name} help' for command usage",
                    "Check the system logs for more details",
                    "Contact support if the problem persists",
                ]
            )

        return suggestions

    def _get_recovery_suggestions_from_message(
        self, message: str, command: ICommand, args: List[str]
    ) -> List[str]:
        """Get recovery suggestions based on error message content.

        Args:
            message: Error message
            command: Command that failed
            args: Command arguments

        Returns:
            List of recovery suggestions
        """
        suggestions = []
        message_lower = message.lower()
        command_name = command.metadata.name

        if "not found" in message_lower:
            suggestions.append("Check that the specified resource exists")
        elif "permission" in message_lower or "denied" in message_lower:
            suggestions.append("Check your user permissions")
        elif "connection" in message_lower or "network" in message_lower:
            suggestions.append("Check your network connection")
        elif "timeout" in message_lower:
            suggestions.append("Try running the command again")
        elif "invalid" in message_lower or "incorrect" in message_lower:
            suggestions.append(f"Use '/{command_name} help' for correct usage")

        return suggestions

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for all commands.

        Returns:
            Dictionary containing error statistics
        """
        total_errors = sum(self._error_counts.values())

        return {
            "total_errors": total_errors,
            "commands_with_errors": len(self._error_counts),
            "error_counts_by_command": self._error_counts.copy(),
            "most_error_prone_command": (
                max(self._error_counts.keys(), key=lambda k: self._error_counts[k])
                if self._error_counts
                else None
            ),
        }

    def reset_error_counts(self) -> None:
        """Reset error counts for all commands."""
        self._error_counts.clear()
        logger.debug("Reset error counts")

    def enable_stack_traces(self) -> None:
        """Enable stack trace inclusion in error responses."""
        self._include_stack_trace = True
        logger.debug("Enabled stack trace inclusion")

    def disable_stack_traces(self) -> None:
        """Disable stack trace inclusion in error responses."""
        self._include_stack_trace = False
        logger.debug("Disabled stack trace inclusion")
