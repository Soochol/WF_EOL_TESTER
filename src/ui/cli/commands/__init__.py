"""
CLI Commands Package - Enhanced Command System

Modern command system with dependency injection, middleware pipeline,
and extensible architecture. Maintains backward compatibility with
existing command implementations.

New Features:
- Interface-based design with dependency injection
- Middleware pipeline for cross-cutting concerns
- Enhanced command registry with discovery
- Command factory with configuration support
- Comprehensive validation and error handling
"""

# Local application imports
# BACKWARD COMPATIBILITY IMPORTS
# Import legacy components for existing integrations
from ui.cli.commands.base import (
    Command,
    CommandResult as LegacyCommandResult,
    CommandStatus as LegacyCommandStatus,
)
from ui.cli.commands.config_command import ConfigCommand
from ui.cli.commands.core.base_command import BaseCommand
from ui.cli.commands.core.command_parser import EnhancedCommandParser
from ui.cli.commands.core.execution_context import CommandExecutionContext
from ui.cli.commands.exit_command import ExitCommand
from ui.cli.commands.factories.command_factory import CommandFactory

# Import enhanced command handlers
from ui.cli.commands.handlers.test_command_handler import TestCommandHandler
from ui.cli.commands.hardware_command import HardwareCommand
from ui.cli.commands.help_command import HelpCommand

# Import new enhanced interfaces and core components
from ui.cli.commands.interfaces.command_interface import (
    CommandMetadata,
    CommandResult,
    CommandStatus,
    ICommand,
    ICommandExecutionContext,
    ICommandMiddleware,
    ICommandParser,
    ICommandRegistry,
    MiddlewareResult,
)
from ui.cli.commands.middleware.authentication_middleware import AuthenticationMiddleware

# Import middleware components
from ui.cli.commands.middleware.base_middleware import BaseMiddleware
from ui.cli.commands.middleware.error_handling_middleware import ErrorHandlingMiddleware
from ui.cli.commands.middleware.logging_middleware import LoggingMiddleware
from ui.cli.commands.middleware.validation_middleware import ValidationMiddleware
from ui.cli.commands.parser import SlashCommandParser
from ui.cli.commands.registry.command_registry import EnhancedCommandRegistry
from ui.cli.commands.results_command import ResultsCommand
from ui.cli.commands.test_command import TestCommand


# Export enhanced components (primary API)
__all__ = [
    # Core Interfaces
    "ICommand",
    "ICommandParser",
    "ICommandRegistry",
    "ICommandMiddleware",
    "ICommandExecutionContext",
    # Data Classes and Enums
    "CommandMetadata",
    "CommandResult",
    "CommandStatus",
    "MiddlewareResult",
    # Core Components
    "BaseCommand",
    "EnhancedCommandParser",
    "CommandExecutionContext",
    "EnhancedCommandRegistry",
    "CommandFactory",
    # Middleware
    "BaseMiddleware",
    "AuthenticationMiddleware",
    "ValidationMiddleware",
    "LoggingMiddleware",
    "ErrorHandlingMiddleware",
    # Enhanced Command Handlers
    "TestCommandHandler",
    # LEGACY COMPATIBILITY (deprecated - use enhanced versions)
    "Command",  # Use BaseCommand instead
    "SlashCommandParser",  # Use EnhancedCommandParser instead
    # Legacy Command Implementations (maintained for compatibility)
    "HelpCommand",
    "TestCommand",  # Use TestCommandHandler instead
    "ConfigCommand",
    "HardwareCommand",
    "ExitCommand",
    "ResultsCommand",
]

# Backward compatibility aliases
LegacyCommand = Command
LegacySlashCommandParser = SlashCommandParser
