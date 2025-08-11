"""Command Handlers Package

Contains enhanced command handler implementations that integrate with
the new command system architecture and dependency injection.
"""

from src.ui.cli.commands.handlers.test_command_handler import TestCommandHandler

__all__ = [
    "TestCommandHandler",
]
