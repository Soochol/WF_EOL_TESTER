"""
Enhanced CLI Integration Module

Integration layer that enhances the existing CLI system with advanced input capabilities
while maintaining backward compatibility. This module provides seamless integration
of the EnhancedInputManager with existing CLI components.

Key Features:
- Backward compatible input replacement
- Enhanced menu navigation with auto-completion
- Advanced slash command mode with full features
- DUT information collection with validation
- Professional input experience throughout the CLI
- Graceful fallback when prompt_toolkit is unavailable
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from rich.console import Console

from .enhanced_input_manager import create_enhanced_input_manager
from .rich_formatter import RichFormatter


def get_default_model_from_profile() -> Optional[str]:
    """Get the default model name from the current test profile filename"""
    try:
        profiles_dir = Path("configuration/test_profiles")
        if profiles_dir.exists():
            # For now, use 'default' as the primary profile
            # In the future, could be extended to detect the active profile
            default_profile = profiles_dir / "default.yaml"
            if default_profile.exists():
                return "default"
        return None
    except Exception as e:
        logger.debug(f"Could not determine default model from profile: {e}")
        return None


class EnhancedInputIntegrator:
    """Integration layer that replaces basic input with enhanced input throughout the CLI"""

    def __init__(
        self,
        console: Console,
        formatter: RichFormatter,
        configuration_service: Optional[Any] = None,
    ):
        self.console = console
        self.formatter = formatter
        self.configuration_service = configuration_service
        default_model = get_default_model_from_profile()
        self.input_manager = create_enhanced_input_manager(
            console, formatter, default_model, configuration_service
        )

        # Menu option mappings for auto-completion
        self.menu_options = {
            "main_menu": {
                "1": "Execute EOL Test",
                "2": "Execute UseCase (Advanced)",
                "3": "Hardware Control Center",
                "4": "Real-time Monitoring Dashboard",
                "5": "Check Hardware Status",
                "6": "View Test Statistics",
                "7": "Slash Command Mode",
                "8": "Exit",
            },
            "hardware_menu": {
                "1": "Robot Control",
                "2": "MCU Control",
                "3": "LoadCell Control",
                "4": "Power Control",
                "b": "Back to Main Menu",
            },
            "usecase_menu": {"1": "EOL Force Test", "b": "Back to Main Menu"},
        }

        logger.info("Enhanced CLI Integration initialized")

    async def get_menu_choice(
        self,
        menu_type: str = "main_menu",
        prompt_text: str = "Select an option: ",
        custom_options: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Get menu choice with enhanced input and auto-completion

        Args:
            menu_type: Type of menu for context-aware completion
            prompt_text: Prompt text to display
            custom_options: Custom menu options if not using predefined

        Returns:
            Selected option string or None if cancelled
        """
        options = custom_options or self.menu_options.get(menu_type, {})

        # Create completions from menu options
        choices = list(options.keys())

        # Use the enhanced input manager's built-in completion system
        choice = await self.input_manager.get_input(
            prompt_text=prompt_text,
            input_type="general",
            placeholder=f"Choose from: {', '.join(choices)}",
            show_completions=True,
            enable_history=True,
        )

        return choice

    async def get_dut_information(self) -> Optional[Dict[str, str]]:
        """Get DUT information using enhanced input system"""
        return await self.input_manager.get_dut_info_interactive()

    async def get_slash_command(self) -> Optional[str]:
        """Get slash command using enhanced input system"""
        return await self.input_manager.get_slash_command_interactive()

    async def get_validated_input(
        self,
        prompt: str,
        input_type: str = "general",
        required: bool = False,
        placeholder: str = "",
    ) -> Optional[str]:
        """Get validated input with enhanced features

        Args:
            prompt: Prompt text to display
            input_type: Type of input for validation
            required: Whether input is required
            placeholder: Placeholder text

        Returns:
            Validated input string or None
        """
        while True:
            result = await self.input_manager.get_input(
                prompt_text=prompt,
                input_type=input_type,
                placeholder=placeholder,
                show_completions=input_type in ["dut_id", "model", "operator"],
                validator_type=input_type,
            )

            if result is None:  # User cancelled
                return None

            if not result and required:
                self.formatter.print_message(
                    "Input is required. Please try again.", message_type="warning"
                )
                continue

            return result if result else None

    async def get_confirmation(self, message: str, default: bool = False) -> bool:
        """Get confirmation with enhanced UI"""
        return await self.input_manager.get_confirmation(message, default)

    async def wait_for_acknowledgment(self, message: str = "Press Enter to continue...") -> None:
        """Wait for user acknowledgment with enhanced input"""
        await self.input_manager.get_input(
            prompt_text="",
            input_type="general",
            placeholder=message,
            show_completions=False,
            enable_history=False,
        )

    def show_input_help(self) -> None:
        """Show help information about enhanced input features"""
        help_content = """[bold cyan]Enhanced Input Features:[/bold cyan]

[bold]Auto-completion:[/bold]
• Press [cyan]Tab[/cyan] to see available completions
• Use [cyan]Ctrl+Space[/cyan] to force completion menu
• Arrow keys to navigate completion options

[bold]Command History:[/bold]
• Press [cyan]Up/Down[/cyan] arrows to browse history
• Use [cyan]Ctrl+R[/cyan] to search command history
• History is saved between sessions

[bold]Input Validation:[/bold]
• Real-time validation with visual feedback
• Error messages show specific formatting requirements
• Input is validated as you type

[bold]Navigation:[/bold]
• Use [cyan]Ctrl+A[/cyan] / [cyan]Ctrl+E[/cyan] to move to beginning/end
• [cyan]Ctrl+W[/cyan] deletes previous word
• [cyan]Ctrl+U[/cyan] clears entire line
• [cyan]Ctrl+L[/cyan] clears screen

[bold]Multi-line Input:[/bold]
• Some inputs support multiple lines
• Use [cyan]Ctrl+D[/cyan] to finish multi-line input
• [cyan]Alt+Enter[/cyan] for new line in multi-line mode

[bold]Cancellation:[/bold]
• Press [cyan]Ctrl+C[/cyan] to cancel current input
• Press [cyan]Ctrl+D[/cyan] on empty line to exit"""

        help_panel = self.formatter.create_message_panel(
            help_content, message_type="info", title="🎯 Enhanced Input Help"
        )
        self.console.print(help_panel)

    def get_history_statistics(self) -> Dict[str, Any]:
        """Get command history statistics"""
        return self.input_manager.get_history_stats()

    def clear_command_history(self) -> bool:
        """Clear command history"""
        return self.input_manager.clear_history()


class EnhancedMenuSystem:
    """Enhanced menu system with advanced navigation and input features"""

    def __init__(self, integrator: EnhancedInputIntegrator):
        self.integrator = integrator
        self.formatter = integrator.formatter
        self.console = integrator.console

    async def show_main_menu_enhanced(self) -> Optional[str]:
        """Show enhanced main menu with auto-completion and help"""
        from rich.panel import Panel
        from rich.text import Text

        # Create menu content with proper Rich markup
        menu_text = Text()
        menu_text.append("1.", style="bold cyan")
        menu_text.append(" Execute EOL Test\n")
        menu_text.append("2.", style="bold cyan")
        menu_text.append(" Execute UseCase (Advanced)\n")
        menu_text.append("3.", style="bold cyan")
        menu_text.append(" Hardware Control Center\n")
        menu_text.append("4.", style="bold cyan")
        menu_text.append(" Real-time Monitoring Dashboard\n")
        menu_text.append("5.", style="bold cyan")
        menu_text.append(" Check Hardware Status\n")
        menu_text.append("6.", style="bold cyan")
        menu_text.append(" View Test Statistics\n")
        menu_text.append("7.", style="bold cyan")
        menu_text.append(" Slash Command Mode\n")
        menu_text.append("8.", style="bold cyan")
        menu_text.append(" Exit\n")
        menu_text.append("help", style="bold cyan")
        menu_text.append(" Show input help\n\n")
        menu_text.append("Please select an option (1-8) or type 'help':")

        # Create panel with properly styled content
        self.console.print("\n")
        menu_panel = Panel(
            menu_text,
            title="🧪 Enhanced Main Menu",
            title_align="left",
            border_style="bright_blue",
            padding=(1, 2),
        )
        self.console.print(menu_panel)

        # Get choice with enhanced input
        choice = await self.integrator.get_menu_choice(menu_type="main_menu", prompt_text="→ ")

        # Handle special commands
        if choice and choice.lower() == "help":
            self.integrator.show_input_help()
            return await self.show_main_menu_enhanced()  # Show menu again

        return choice

    async def show_hardware_menu_enhanced(self) -> Optional[str]:
        """Show enhanced hardware control menu"""
        from rich.panel import Panel
        from rich.text import Text

        # Create menu content with proper Rich styling
        menu_text = Text()
        menu_text.append("1.", style="bold cyan")
        menu_text.append(" Robot Control (AJINEXTEK)\n")
        menu_text.append("2.", style="bold cyan")
        menu_text.append(" MCU Control (LMA Temperature)\n")
        menu_text.append("3.", style="bold cyan")
        menu_text.append(" LoadCell Control (BS205)\n")
        menu_text.append("4.", style="bold cyan")
        menu_text.append(" Power Control (ODA)\n")
        menu_text.append("b.", style="bold cyan")
        menu_text.append(" Back to Main Menu\n\n")
        menu_text.append("Select hardware component (1-4) or 'b' for back:")

        self.console.print("\n")
        menu_panel = Panel(
            menu_text,
            title="🔧 Hardware Control Center",
            title_align="left",
            border_style="bright_blue",
            padding=(1, 2),
        )
        self.console.print(menu_panel)

        return await self.integrator.get_menu_choice(menu_type="hardware_menu", prompt_text="→ ")

    async def show_usecase_menu_enhanced(self) -> Optional[str]:
        """Show enhanced UseCase selection menu"""
        from rich.panel import Panel
        from rich.text import Text

        # Create menu content with proper Rich styling
        menu_text = Text()
        menu_text.append("1.", style="bold cyan")
        menu_text.append(" EOL Force Test\n")
        menu_text.append("b.", style="bold cyan")
        menu_text.append(" Back to Main Menu\n\n")
        menu_text.append("Select UseCase (1) or 'b' for back:")

        self.console.print("\n")
        menu_panel = Panel(
            menu_text,
            title="⚙️ UseCase Selection",
            title_align="left",
            border_style="bright_blue",
            padding=(1, 2),
        )
        self.console.print(menu_panel)

        return await self.integrator.get_menu_choice(menu_type="usecase_menu", prompt_text="→ ")

    async def show_statistics_menu(self) -> None:
        """Show input system statistics"""
        stats = self.integrator.get_history_statistics()

        stats_content = f"""[bold]Command History Statistics:[/bold]

• Total Commands: {stats['total_commands']}
• Unique Commands: {stats['unique_commands']}

[bold]Most Used Commands:[/bold]"""

        if stats["most_used"]:
            for cmd, count in stats["most_used"]:
                stats_content += f"\n  • {cmd}: {count} times"
        else:
            stats_content += "\n  No commands in history yet"

        if stats["recent_commands"]:
            stats_content += "\n\n[bold]Recent Commands:[/bold]"
            for cmd in stats["recent_commands"][-5:]:  # Show last 5
                stats_content += f"\n  • {cmd}"

        stats_panel = self.formatter.create_message_panel(
            stats_content, message_type="info", title="📊 Input System Statistics"
        )
        self.console.print(stats_panel)

        # Offer to clear history
        if stats["total_commands"] > 0:
            if await self.integrator.get_confirmation("\nClear command history?", default=False):
                if self.integrator.clear_command_history():
                    self.formatter.print_message(
                        "Command history cleared successfully", message_type="success"
                    )
                else:
                    self.formatter.print_message(
                        "Failed to clear command history", message_type="error"
                    )


class EnhancedSlashCommandInterface:
    """Enhanced slash command interface with full prompt_toolkit features"""

    def __init__(self, integrator: EnhancedInputIntegrator, slash_handler: Any):
        self.integrator = integrator
        self.slash_handler = slash_handler
        self.formatter = integrator.formatter
        self.console = integrator.console

    async def run_enhanced_slash_mode(self) -> None:
        """Run enhanced slash command mode with full features"""
        self.formatter.print_header(
            "Enhanced Slash Command Mode",
            "Professional hardware control with auto-completion and history",
        )

        # Show enhanced introduction
        intro_content = """Welcome to Enhanced Slash Command Mode!

[bold cyan]Enhanced Features:[/bold cyan]
• [green]Auto-completion[/green] - Press Tab for command suggestions
• [green]Command history[/green] - Use Up/Down arrows to browse history
• [green]Syntax highlighting[/green] - Commands are visually highlighted
• [green]Real-time validation[/green] - Instant feedback on command syntax
• [green]Smart suggestions[/green] - Context-aware parameter completion

[bold cyan]Available Commands:[/bold cyan]
• [cyan]/robot[/cyan] connect, disconnect, status, init, stop
• [cyan]/mcu[/cyan] connect, disconnect, status, temp [value], testmode, fan [speed]
• [cyan]/loadcell[/cyan] connect, disconnect, status, read, zero, monitor
• [cyan]/power[/cyan] connect, disconnect, status, on, off, voltage [value], current [value]
• [cyan]/all[/cyan] status - Show all hardware status
• [cyan]/help[/cyan] [command] - Show help information

[bold]Type commands and press Enter. Use 'exit' to return to main menu.[/bold]
[dim]Tip: Press Ctrl+L to clear screen, Ctrl+R to search history[/dim]"""

        intro_panel = self.formatter.create_message_panel(
            intro_content, message_type="info", title="🚀 Getting Started"
        )
        self.console.print(intro_panel)
        self.console.print("")

        command_count = 0

        while True:
            try:
                # Get enhanced command input
                command_input = await self.integrator.get_slash_command()

                if command_input is None:
                    # User cancelled (Ctrl+C or Ctrl+D)
                    self.formatter.print_message(
                        "Exiting Enhanced Slash Command Mode", message_type="info"
                    )
                    break

                # Check for exit commands
                if command_input.lower() in ["exit", "quit", "back"]:
                    self.formatter.print_message(
                        "Exiting Enhanced Slash Command Mode", message_type="info"
                    )
                    break

                # Skip empty input
                if not command_input:
                    continue

                command_count += 1

                # Show command feedback
                self.console.print(
                    f"[dim]Executing command #{command_count}: {command_input}[/dim]"
                )

                # Execute the command
                if self.slash_handler.is_slash_command(command_input):
                    success = await self.slash_handler.execute_command(command_input)

                    if success:
                        self.console.print(
                            "[dim green]✓ Command completed successfully[/dim green]"
                        )
                    else:
                        self.console.print("[dim red]✗ Command failed or had errors[/dim red]")

                    self.console.print("")  # Add spacing
                else:
                    # Provide helpful guidance for non-slash commands
                    self.formatter.print_message(
                        f"Commands must start with '/'. Did you mean '/{command_input}'?",
                        message_type="warning",
                    )

                    # Show suggestions
                    suggestions = self._get_command_suggestions(command_input)
                    if suggestions:
                        suggestion_text = "Suggestions: " + ", ".join(suggestions)
                        self.formatter.print_message(suggestion_text, message_type="info")

            except KeyboardInterrupt:
                self.formatter.print_message(
                    "\nExiting Enhanced Slash Command Mode", message_type="info"
                )
                break
            except Exception as e:
                self.formatter.print_message(
                    f"Command processing error: {str(e)}", message_type="error"
                )
                logger.error(f"Enhanced slash command error: {e}")

        # Show session summary
        if command_count > 0:
            self.formatter.print_message(
                f"Session completed. {command_count} commands executed.",
                message_type="info",
                title="Session Summary",
            )

    def _get_command_suggestions(self, input_text: str) -> List[str]:
        """Get command suggestions for invalid input"""
        commands = ["/robot", "/mcu", "/loadcell", "/power", "/all", "/help"]

        # Simple fuzzy matching
        suggestions = []
        input_lower = input_text.lower()

        for cmd in commands:
            cmd_name = cmd[1:]  # Remove /
            if (
                input_lower in cmd_name
                or cmd_name.startswith(input_lower)
                or any(input_lower in part for part in cmd_name.split("_"))
            ):
                suggestions.append(cmd)

        return suggestions[:3]  # Return top 3 suggestions


# Integration factory functions
def create_enhanced_cli_integrator(
    console: Console, formatter: RichFormatter, configuration_service: Optional[Any] = None
) -> EnhancedInputIntegrator:
    """Factory function to create enhanced CLI integrator"""
    return EnhancedInputIntegrator(console, formatter, configuration_service)


def create_enhanced_menu_system(integrator: EnhancedInputIntegrator) -> EnhancedMenuSystem:
    """Factory function to create enhanced menu system"""
    return EnhancedMenuSystem(integrator)


def create_enhanced_slash_interface(
    integrator: EnhancedInputIntegrator, slash_handler: Any
) -> EnhancedSlashCommandInterface:
    """Factory function to create enhanced slash command interface"""
    return EnhancedSlashCommandInterface(integrator, slash_handler)


# Example usage and testing
async def demo_enhanced_integration() -> None:
    """Demonstration of enhanced CLI integration"""
    console = Console(force_terminal=True, legacy_windows=False, color_system="truecolor")
    formatter = RichFormatter(console)

    # Create enhanced components
    integrator = create_enhanced_cli_integrator(console, formatter)
    menu_system = create_enhanced_menu_system(integrator)

    console.print("[bold]Enhanced CLI Integration Demo[/bold]\n")

    # Demo enhanced menu
    console.print("[cyan]1. Enhanced Main Menu:[/cyan]")
    choice = await menu_system.show_main_menu_enhanced()
    console.print(f"Selected: {choice}\n")

    # Demo DUT information collection
    console.print("[cyan]2. Enhanced DUT Information:[/cyan]")
    dut_info = await integrator.get_dut_information()
    console.print(f"DUT Info: {dut_info}\n")

    # Demo statistics
    console.print("[cyan]3. Input Statistics:[/cyan]")
    await menu_system.show_statistics_menu()


if __name__ == "__main__":
    # Run demo if executed directly
    asyncio.run(demo_enhanced_integration())
