"""Base Command Implementation

Enhanced base command class with dependency injection support, metadata
management, and improved validation capabilities.
"""

# Standard library imports
from abc import ABC
from typing import List, Optional, Tuple

# Third-party imports
from loguru import logger

# Local application imports
from ui.cli.commands.interfaces.command_interface import (
    CommandMetadata,
    CommandResult,
    ICommand,
    ICommandExecutionContext,
)


class BaseCommand(ICommand, ABC):
    """Enhanced base command implementation with modern patterns.

    Provides common functionality for command implementations including
    metadata management, validation, and dependency injection support.
    Commands extending this class should focus on business logic.
    """

    def __init__(self, metadata: CommandMetadata):
        """Initialize base command with metadata.

        Args:
            metadata: Command metadata containing configuration and information
        """
        self._metadata = metadata
        logger.debug(f"Initialized command: {metadata.name}")

    @property
    def metadata(self) -> CommandMetadata:
        """Get command metadata.

        Returns:
            CommandMetadata containing command information and configuration
        """
        return self._metadata

    def validate_args(self, args: List[str]) -> Tuple[bool, Optional[str]]:
        """Base validation for command arguments.

        Provides common validation patterns that can be extended by subclasses.
        Subclasses should call super().validate_args() and add specific validation.

        Args:
            args: Arguments to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation - subclasses should override for specific needs
        return True, None

    def validate_args_count(
        self,
        args: List[str],
        min_args: int = 0,
        max_args: Optional[int] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Validate argument count with detailed error messages.

        Args:
            args: Arguments to validate
            min_args: Minimum required arguments
            max_args: Maximum allowed arguments (None for unlimited)

        Returns:
            Tuple of (is_valid, error_message)
        """
        arg_count = len(args)

        if arg_count < min_args:
            if min_args == 1:
                return False, f"Command /{self.metadata.name} requires at least 1 argument"
            return False, f"Command /{self.metadata.name} requires at least {min_args} arguments"

        if max_args is not None and arg_count > max_args:
            if max_args == 0:
                return False, f"Command /{self.metadata.name} takes no arguments"
            elif max_args == 1:
                return False, f"Command /{self.metadata.name} takes at most 1 argument"
            else:
                return False, f"Command /{self.metadata.name} takes at most {max_args} arguments"

        return True, None

    def validate_subcommand(
        self,
        args: List[str],
        valid_subcommands: Optional[List[str]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Validate subcommand argument.

        Args:
            args: Arguments to validate
            valid_subcommands: List of valid subcommands, None to use get_subcommands()

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not args:
            return True, None  # No subcommand is valid for base command

        subcommand = args[0].lower()

        if valid_subcommands is None:
            valid_subcommands = list(self.get_subcommands().keys())

        # Remove empty string if present (represents base command)
        valid_subcommands = [cmd for cmd in valid_subcommands if cmd]

        if valid_subcommands and subcommand not in valid_subcommands:
            available = ", ".join(valid_subcommands)
            return False, f"Unknown subcommand '{subcommand}'. Available: {available}"

        return True, None

    def get_help_for_subcommand(self, subcommand: str) -> Optional[str]:
        """Get help text for a specific subcommand.

        Args:
            subcommand: Subcommand to get help for

        Returns:
            Help text for the subcommand or None if not found
        """
        subcommands = self.get_subcommands()
        return subcommands.get(subcommand)

    def handle_help_request(self, args: List[str]) -> Optional[CommandResult]:
        """Handle help subcommand requests.

        Args:
            args: Command arguments

        Returns:
            CommandResult with help information
        """
        if args and args[0].lower() == "help":
            if len(args) > 1:
                # Help for specific subcommand
                subcommand = args[1].lower()
                help_text = self.get_help_for_subcommand(subcommand)
                if help_text:
                    return CommandResult.info(f"/{self.metadata.name} {subcommand} - {help_text}")
                else:
                    return CommandResult.error(f"No help available for subcommand: {subcommand}")
            else:
                # General help
                return CommandResult.info(self.get_help())

        return None  # Not a help request

    def log_command_execution(
        self,
        args: List[str],
        context: ICommandExecutionContext,
        result: CommandResult,
    ) -> None:
        """Log command execution for audit and debugging.

        Args:
            args: Command arguments
            context: Execution context
            result: Command result
        """
        user_id = context.user_id or "anonymous"
        args_str = " ".join(args) if args else "(no args)"

        logger.info(
            f"Command executed: /{self.metadata.name} {args_str} | "
            f"User: {user_id} | Status: {result.status.value} | "
            f"Time: {result.execution_time_ms}ms"
        )

    async def execute_with_logging(
        self,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> CommandResult:
        """Execute command with automatic logging.

        Wrapper around execute() that adds automatic logging and timing.
        Subclasses should override execute() instead of this method.

        Args:
            args: Command arguments
            context: Execution context

        Returns:
            CommandResult with execution timing
        """
        # Standard library imports
        import time

        start_time = time.perf_counter()

        try:
            result = await self.execute(args, context)

            # Add execution time if not already set
            if result.execution_time_ms is None:
                execution_time = (time.perf_counter() - start_time) * 1000
                result.execution_time_ms = execution_time

            self.log_command_execution(args, context, result)
            return result

        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            error_result = CommandResult.error(
                f"Command execution failed: {str(e)}",
                execution_time_ms=execution_time,
                error_details={"exception_type": type(e).__name__, "exception_message": str(e)},
            )

            self.log_command_execution(args, context, error_result)
            logger.error(f"Command /{self.metadata.name} failed: {e}")
            return error_result
