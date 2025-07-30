"""
Base Command Classes

Abstract base classes for the command pattern implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class CommandStatus(Enum):
    """Command execution status"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CommandResult:
    """Result of command execution"""

    status: CommandStatus
    message: str
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def success(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "CommandResult":
        """Create success result"""
        return cls(CommandStatus.SUCCESS, message, data)

    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "CommandResult":
        """Create error result"""
        return cls(CommandStatus.ERROR, message, data)

    @classmethod
    def warning(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "CommandResult":
        """Create warning result"""
        return cls(CommandStatus.WARNING, message, data)

    @classmethod
    def info(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "CommandResult":
        """Create info result"""
        return cls(CommandStatus.INFO, message, data)


class Command(ABC):
    """
    Abstract base class for all slash commands

    Implements the Command pattern for extensible CLI functionality.
    Each command handles its own parsing, validation, and execution.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize command

        Args:
            name: Command name (e.g., "test", "config")
            description: Brief description of what the command does
        """
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(
        self, args: List[str]
    ) -> CommandResult:
        """
        Execute the command with given arguments

        Args:
            args: List of command arguments (excluding the command name)

        Returns:
            CommandResult indicating success/failure and any data
        """

    @abstractmethod
    def get_subcommands(self) -> Dict[str, str]:
        """
        Get available subcommands for this command

        Returns:
            Dictionary mapping subcommand names to descriptions
        """

    def get_help(self) -> str:
        """
        Get help text for this command

        Returns:
            Formatted help text including subcommands
        """
        help_text = f"/{self.name} - {self.description}\n"

        subcommands = self.get_subcommands()
        if subcommands:
            help_text += "\nSubcommands:\n"
            for subcmd, desc in subcommands.items():
                help_text += (
                    f"  /{self.name} {subcmd} - {desc}\n"
                )

        return help_text

    def validate_args(
        self,
        args: List[str],
        min_args: int = 0,
        max_args: Optional[int] = None,
    ) -> bool:
        """
        Validate command arguments

        Args:
            args: Arguments to validate
            min_args: Minimum required arguments
            max_args: Maximum allowed arguments (None for unlimited)

        Returns:
            True if arguments are valid
        """
        if len(args) < min_args:
            return False

        if max_args is not None and len(args) > max_args:
            return False

        return True
