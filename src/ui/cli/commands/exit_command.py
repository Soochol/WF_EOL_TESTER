"""
Exit Command

Handles application exit.
"""

from typing import Dict, List

from ui.cli.commands.base import Command, CommandResult


class ExitCommand(Command):
    """Command for exiting the application"""

    def __init__(self) -> None:
        super().__init__(name="exit", description="Exit the application")

    async def execute(self, args: List[str]) -> CommandResult:
        """
        Execute exit command

        Args:
            args: Command arguments (ignored)

        Returns:
            CommandResult indicating exit request
        """
        return CommandResult.success("Exiting EOL Tester...", {"exit": True})

    def get_subcommands(self) -> Dict[str, str]:
        """Get available subcommands"""
        return {}
