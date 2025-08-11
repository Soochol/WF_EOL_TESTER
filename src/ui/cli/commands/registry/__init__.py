"""Command Registry Package

Provides command registration and discovery system with metadata management
and plugin-style command loading capabilities.
"""

from src.ui.cli.commands.registry.command_registry import EnhancedCommandRegistry

__all__ = [
    "EnhancedCommandRegistry",
]
