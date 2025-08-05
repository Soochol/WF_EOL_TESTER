"""Command Result Classes

Extracted command result and status classes from the base module for better
organization and reusability. Provides comprehensive result handling with
metadata and performance tracking.
"""

# Re-export the enhanced classes from interfaces for backward compatibility
from ui.cli.commands.interfaces.command_interface import (
    CommandResult,
    CommandStatus,
    MiddlewareResult,
)

__all__ = [
    "CommandResult",
    "CommandStatus",
    "MiddlewareResult",
]
