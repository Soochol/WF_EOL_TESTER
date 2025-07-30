"""
Slash Command Executor

Provides both interactive and direct execution modes for slash commands.
This module enables external applications to execute hardware control commands
programmatically or to create scripts that use the slash command system.

Key Features:
- Direct command execution without interactive mode
- Batch command processing from scripts or lists
- Programmatic interface for external integrations
- Return values for command success/failure checking
- Logging integration for command execution tracking
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger
from rich.console import Console

from infrastructure.factory import ServiceFactory

from .slash_command_handler import SlashCommandHandler


class SlashCommandExecutor:
    """Executor for running slash commands in batch or direct mode"""

    def __init__(self, slash_handler: SlashCommandHandler):
        """Initialize executor with slash command handler

        Args:
            slash_handler: Configured slash command handler instance
        """
        self.slash_handler = slash_handler
        self.console = slash_handler.console

    async def execute_single_command(self, command: str) -> bool:
        """Execute a single slash command directly

        Args:
            command: Slash command string to execute

        Returns:
            True if command succeeded, False otherwise
        """
        logger.info("Executing direct command: %s", command)

        try:
            result = await self.slash_handler.execute_command(command)
            logger.info("Command execution result: %s", result)
            return result

        except Exception as e:
            logger.error("Command execution failed: %s", e)
            return False

    async def execute_command_list(self, commands: List[str]) -> Dict[str, bool]:
        """Execute a list of commands in sequence

        Args:
            commands: List of slash command strings

        Returns:
            Dictionary mapping commands to their success status
        """
        results = {}

        self.console.print("[bold cyan]Executing batch commands...[/bold cyan]")

        for i, command in enumerate(commands, 1):
            self.console.print(
                f"\n[bold yellow]Command {i}/{len(commands)}:[/bold yellow] {command}"
            )

            success = await self.execute_single_command(command)
            results[command] = success

            if not success:
                self.console.print(f"[red]✗[/red] Command failed: {command}")
            else:
                self.console.print(f"[green]✓[/green] Command succeeded: {command}")

        # Print summary
        self.console.print("\n[bold cyan]Batch execution summary:[/bold cyan]")
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        self.console.print(f"Successful: {successful}/{total}")

        if successful < total:
            self.console.print("[yellow]Failed commands:[/yellow]")
            for cmd, success in results.items():
                if not success:
                    self.console.print(f"  - {cmd}")

        return results

    async def execute_from_file(self, file_path: Path) -> Dict[str, bool]:
        """Execute commands from a file

        Args:
            file_path: Path to file containing slash commands (one per line)

        Returns:
            Dictionary mapping commands to their success status
        """
        try:
            commands = []

            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Validate it's a slash command
                    if not self.slash_handler.is_slash_command(line):
                        logger.warning("Line %s is not a valid slash command: %s", line_num, line)
                        continue

                    commands.append(line)

            self.console.print(
                f"[bold cyan]Loaded {len(commands)} commands from {file_path}[/bold cyan]"
            )

            if not commands:
                self.console.print("[yellow]No valid commands found in file[/yellow]")
                return {}

            return await self.execute_command_list(commands)

        except FileNotFoundError:
            self.console.print(f"[red]Error: File not found: {file_path}[/red]")
            return {}
        except Exception as e:
            self.console.print(f"[red]Error reading file: {e}[/red]")
            logger.error("File execution error: %s", e)
            return {}

    def create_demo_script(self, file_path: Path) -> None:
        """Create a demo script file with example commands

        Args:
            file_path: Path where to create the demo script
        """
        demo_commands = [
            "# Slash Command Demo Script",
            "# This file demonstrates various slash commands for hardware control",
            "",
            "# Show help for all commands",
            "/help",
            "",
            "# Check all hardware status",
            "/all status",
            "",
            "# Robot commands",
            "/robot status",
            "/robot connect",
            "/robot init",
            "",
            "# MCU commands",
            "/mcu status",
            "/mcu connect",
            "/mcu temp",
            "/mcu temp 85.0",
            "/mcu fan 75",
            "",
            "# LoadCell commands",
            "/loadcell status",
            "/loadcell connect",
            "/loadcell read",
            "/loadcell zero",
            "",
            "# Power supply commands",
            "/power status",
            "/power connect",
            "/power voltage 24.0",
            "/power current 2.5",
            "/power on",
            "",
            "# Show final status",
            "/all status",
        ]

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(demo_commands))

            self.console.print(f"[green]Demo script created: {file_path}[/green]")
            self.console.print(
                "You can run it with: python -m slash_command_executor --file script.txt"
            )

        except Exception as e:
            self.console.print(f"[red]Error creating demo script: {e}[/red]")
            logger.error("Demo script creation error: %s", e)


async def create_slash_executor_from_config(
    config_path: Optional[str] = None,
) -> SlashCommandExecutor:
    """Create a slash command executor with hardware services from configuration

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configured SlashCommandExecutor instance
    """
    # For demo purposes, create mock hardware services
    # In a real application, you would load from configuration

    console = Console()

    # Create mock hardware services using the factory
    mock_config = {
        "model": "mock",
        "port": "COM_MOCK",
        "baudrate": 115200,
        "timeout": 2.0,
        "default_temperature": 25.0,
        "default_fan_speed": 50.0,
        "response_delay": 0.1,
        "connection_delay": 0.2,
    }

    # Create hardware services using factory instance
    factory = ServiceFactory()
    robot_service = factory.create_robot_service(mock_config)
    mcu_service = factory.create_mcu_service(mock_config)
    loadcell_service = factory.create_loadcell_service(mock_config)
    power_service = factory.create_power_service(mock_config)

    # Create slash command handler
    slash_handler = SlashCommandHandler(
        robot_service=robot_service,
        mcu_service=mcu_service,
        loadcell_service=loadcell_service,
        power_service=power_service,
        console=console,
    )

    return SlashCommandExecutor(slash_handler)


async def main() -> None:
    """Main entry point for direct command execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Slash Command Executor")
    parser.add_argument("--command", "-c", help="Single command to execute")
    parser.add_argument("--file", "-f", help="File containing commands to execute")
    parser.add_argument("--demo", action="store_true", help="Create demo script file")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    # Create executor
    executor = await create_slash_executor_from_config()

    if args.demo:
        # Create demo script
        demo_path = Path("slash_commands_demo.txt")
        executor.create_demo_script(demo_path)
        return

    if args.command:
        # Execute single command
        success = await executor.execute_single_command(args.command)
        sys.exit(0 if success else 1)

    if args.file:
        # Execute commands from file
        file_path = Path(args.file)
        results = await executor.execute_from_file(file_path)

        # Exit with error code if any commands failed
        all_successful = all(results.values())
        sys.exit(0 if all_successful else 1)

    if args.interactive:
        # Interactive mode (similar to the CLI slash command mode)
        console = executor.console
        console.print("[bold cyan]Interactive Slash Command Mode[/bold cyan]")
        console.print("Type slash commands or 'exit' to quit.")
        console.print("Example: /robot status")
        console.print("")

        while True:
            try:
                console.print("[bold green]$[/bold green] ", end="")
                command = input().strip()

                if command.lower() in ["exit", "quit"]:
                    break

                if not command:
                    continue

                if executor.slash_handler.is_slash_command(command):
                    await executor.execute_single_command(command)
                else:
                    console.print("[yellow]Commands must start with '/'. Try '/help'[/yellow]")

            except (KeyboardInterrupt, EOFError):
                break

        console.print("\n[cyan]Goodbye![/cyan]")
        return

    # No arguments provided - show help
    parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
