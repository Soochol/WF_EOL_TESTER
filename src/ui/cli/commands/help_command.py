"""
Help Command

Provides help and documentation for all available commands.
"""

from typing import Dict, List

from src.ui.cli.commands.base import Command, CommandResult


class HelpCommand(Command):
    """Command for displaying help information"""

    def __init__(self) -> None:
        super().__init__(
            name="help",
            description="Show help information for commands",
        )

    async def execute(self, args: List[str]) -> CommandResult:
        """
        Execute help command

        Args:
            args: Optional command name to get specific help for

        Returns:
            CommandResult with help information
        """
        if args:
            # Get help for specific command
            command_name = args[0]
            # This will be populated by the parser when it has access to all commands
            help_text = f"Help for /{command_name} would be shown here"
        else:
            # Show general help
            help_text = self._get_general_help()

        return CommandResult.success(help_text)

    def get_subcommands(self) -> Dict[str, str]:
        """Get available subcommands"""
        return {}

    def _get_general_help(self) -> str:
        """Get general help text"""
        return """EOL Tester - Interactive Mode

Available Commands:
  /help                   - Show this help message
  /test                   - Execute EOL tests
  /config                 - Configuration management
  /hardware               - Hardware operations
  /results                - Test results management
  /exit                   - Exit application

Usage:
  Type '/' to see available commands
  Type '/{command}' to execute a command
  Type '/{command} {subcommand}' for specific actions

Examples:
  /test                   - Start interactive EOL test
  /config view            - View current configuration
  /hardware status        - Check hardware status
  /results list           - List recent test results

For command-specific help, type '/{command} help' or '/help {command}'
"""
