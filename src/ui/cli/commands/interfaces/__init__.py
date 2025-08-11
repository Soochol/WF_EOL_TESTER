"""Command System Interfaces Package

Defines the interfaces for the enhanced command system with dependency injection,
middleware pipeline, and registry pattern support. These interfaces enable
loose coupling, testability, and extensibility.
"""

from src.ui.cli.commands.interfaces.command_interface import (
    ICommand,
    ICommandParser,
    ICommandRegistry,
    ICommandMiddleware,
    ICommandExecutionContext,
    CommandMetadata,
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
