"""Validation Middleware

Provides input validation for command execution using the validation
system from Phase 4. Integrates with IInputValidator for comprehensive
input security and validation.
"""

from typing import List, Optional, Tuple
from loguru import logger

from ui.cli.commands.interfaces.command_interface import (
    ICommand,
    ICommandExecutionContext,
    CommandResult,
    MiddlewareResult,
)
from ui.cli.commands.middleware.base_middleware import BaseMiddleware
from ui.cli.interfaces.validation_interface import IInputValidator


class ValidationMiddleware(BaseMiddleware):
    """Validation middleware for command input validation.

    Uses the IInputValidator from Phase 4 to provide comprehensive
    input validation with security hardening.
    """

    def __init__(self, enable_strict_validation: bool = True):
        """Initialize validation middleware.

        Args:
            enable_strict_validation: Whether to enable strict validation rules
        """
        super().__init__(name="validation", priority=20)  # High priority, after auth

        self._enable_strict_validation = enable_strict_validation

        logger.debug(f"Validation middleware initialized: strict={enable_strict_validation}")

    async def before_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> Tuple[MiddlewareResult, Optional[CommandResult]]:
        """Validate command arguments before execution.

        Args:
            command: Command about to be executed
            args: Command arguments
            context: Execution context

        Returns:
            Tuple of middleware result and optional command result
        """
        self.log_middleware_action("validating arguments", command)

        # Validate arguments using command's validation method
        is_valid, error_message = command.validate_args(args)
        if not is_valid:
            self.log_middleware_action(
                "validation failed", command, error_message
            )
            return MiddlewareResult.STOP, CommandResult.error(
                f"Invalid arguments for command /{command.metadata.name}: {error_message}",
                error_details={
                    "reason": "invalid_arguments",
                    "command": command.metadata.name,
                    "args": args,
                    "validation_error": error_message,
                },
            )

        # Additional security validation using IInputValidator if available
        try:
            validator = context.get_service(IInputValidator)

            # Validate each argument for security threats
            for i, arg in enumerate(args):
                if not validator.validate_input(arg, "command_argument"):
                    self.log_middleware_action(
                        "security validation failed",
                        command,
                        f"argument {i}: {arg[:50]}..."
                    )
                    return MiddlewareResult.STOP, CommandResult.error(
                        f"Security validation failed for argument {i + 1}. "
                        "Argument contains potentially unsafe content.",
                        error_details={
                            "reason": "security_validation_failed",
                            "command": command.metadata.name,
                            "argument_index": i,
                            "argument_preview": arg[:100],
                        },
                    )

        except ValueError:
            # IInputValidator not available - continue with basic validation
            logger.debug("IInputValidator not available, using basic validation only")

        # Check for potentially dangerous patterns if strict validation is enabled
        if self._enable_strict_validation:
            validation_result = self._check_dangerous_patterns(args, command)
            if validation_result:
                return validation_result

        # Validation passed
        self.log_middleware_action("validation passed", command)
        return MiddlewareResult.CONTINUE, None

    def _check_dangerous_patterns(
        self, args: List[str], command: ICommand
    ) -> Optional[Tuple[MiddlewareResult, CommandResult]]:
        """Check arguments for potentially dangerous patterns.

        Args:
            args: Arguments to check
            command: Command being validated

        Returns:
            Tuple of middleware result and error result if dangerous pattern found
        """
        dangerous_patterns = [
            "--",  # Command injection attempt
            ";",   # Command chaining
            "|",   # Pipe operator
            ">",   # Redirection
            "<",   # Input redirection
            "&",   # Background execution
            "$(",  # Command substitution
            "`",   # Backtick execution
            "rm ", # Dangerous commands
            "del ",
            "format",
            "../", # Path traversal
            "..\\\\"  # Windows path traversal
        ]

        for i, arg in enumerate(args):
            arg_lower = arg.lower()
            for pattern in dangerous_patterns:
                if pattern in arg_lower:
                    self.log_middleware_action(
                        "dangerous pattern detected",
                        command,
                        f"pattern '{pattern}' in argument {i}"
                    )
                    return (
                        MiddlewareResult.STOP,
                        CommandResult.error(
                            f"Potentially dangerous pattern detected in argument {i + 1}: '{pattern}'",
                            error_details={
                                "reason": "dangerous_pattern",
                                "command": command.metadata.name,
                                "argument_index": i,
                                "detected_pattern": pattern,
                                "argument_preview": arg[:100],
                            },
                        ),
                    )

        return None

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
            Command result with validation metadata
        """
        # Add validation info to result metadata
        if result.middleware_data is None:
            result.middleware_data = {}

        result.middleware_data["validation"] = {
            "validated_args_count": len(args),
            "strict_validation": self._enable_strict_validation,
            "timestamp": __import__("time").time(),
        }

        return result

    def enable_strict_validation(self) -> None:
        """Enable strict validation mode."""
        self._enable_strict_validation = True
        logger.debug("Enabled strict validation mode")

    def disable_strict_validation(self) -> None:
        """Disable strict validation mode."""
        self._enable_strict_validation = False
        logger.debug("Disabled strict validation mode")

    def is_strict_validation_enabled(self) -> bool:
        """Check if strict validation is enabled.

        Returns:
            True if strict validation is enabled
        """
        return self._enable_strict_validation
