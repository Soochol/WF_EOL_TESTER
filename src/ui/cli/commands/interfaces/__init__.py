"""Command System Interfaces Package

Defines the interfaces for the enhanced command system with dependency injection,
middleware pipeline, and registry pattern support. These interfaces enable
loose coupling, testability, and extensibility.
"""

# Local application imports
from ui.cli.commands.interfaces.command_interface import (
    CommandMetadata,
    ICommand,
    ICommandExecutionContext,
    ICommandMiddleware,
    ICommandParser,
    ICommandRegistry,
    MiddlewareResult,
)


__all__ = [
    "ICommand",
    "ICommandParser",
    "ICommandRegistry",
    "ICommandMiddleware",
    "ICommandExecutionContext",
    "CommandMetadata",
    "MiddlewareResult",
]
