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

# Import new enhanced interfaces and core components
from src.ui.cli.commands.interfaces.command_interface import (
    ICommand,
    ICommandParser,
    ICommandRegistry,
    ICommandMiddleware,
    ICommandExecutionContext,
    CommandMetadata,
    CommandResult,
    CommandStatus,
    MiddlewareResult,
)
from src.ui.cli.commands.core.base_command import BaseCommand
from src.ui.cli.commands.core.command_parser import EnhancedCommandParser
from src.ui.cli.commands.core.execution_context import CommandExecutionContext
from src.ui.cli.commands.registry.command_registry import EnhancedCommandRegistry
from src.ui.cli.commands.factories.command_factory import CommandFactory

# Import middleware components
from src.ui.cli.commands.middleware.base_middleware import BaseMiddleware
from src.ui.cli.commands.middleware.authentication_middleware import AuthenticationMiddleware
from src.ui.cli.commands.middleware.validation_middleware import ValidationMiddleware
from src.ui.cli.commands.middleware.logging_middleware import LoggingMiddleware
from src.ui.cli.commands.middleware.error_handling_middleware import ErrorHandlingMiddleware

# Import enhanced command handlers
from src.ui.cli.commands.handlers.test_command_handler import TestCommandHandler

# BACKWARD COMPATIBILITY IMPORTS
# Import legacy components for existing integrations
from src.ui.cli.commands.base import Command, CommandResult as LegacyCommandResult, CommandStatus as LegacyCommandStatus
from src.ui.cli.commands.parser import SlashCommandParser
from src.ui.cli.commands.help_command import HelpCommand
from src.ui.cli.commands.test_command import TestCommand
from src.ui.cli.commands.config_command import ConfigCommand
from src.ui.cli.commands.hardware_command import HardwareCommand
from src.ui.cli.commands.exit_command import ExitCommand
from src.ui.cli.commands.results_command import ResultsCommand

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
