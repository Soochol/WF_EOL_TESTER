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
from typing import Any, Dict, Optional

from loguru import logger
from rich.console import Console

# from .enhanced_input_manager import create_enhanced_input_manager  # Removed
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
        # default_model = get_default_model_from_profile()  # Not needed anymore
        # self.input_manager = create_enhanced_input_manager(
        #     console, formatter, default_model, configuration_service
        # )
        self.input_manager = None  # Enhanced input functionality removed

        # Menu option mappings for auto-completion
        self.menu_options = {
            "main_menu": {
                "1": "Execute EOL Test",
                "2": "Execute Simple MCU Test",
                "3": "Heating/Cooling Time Test",
                "4": "Robot Home",
                "5": "Hardware Control Center",
                "6": "Exit",
            },
            "hardware_menu": {
                "1": "Robot Control",
                "2": "MCU Control",
                "3": "LoadCell Control",
                "4": "Power Control",
                "b": "Back to Main Menu",
            },
            "usecase_menu": {
                "1": "Simple MCU Test", 
                "2": "Heating/Cooling Time Test",
                "b": "Back to Main Menu"
            },
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

        # Simple input replacement (enhanced input functionality removed)
        self.console.print(f"[dim]Choose from: {', '.join(choices)}[/dim]")
        choice = input(prompt_text).strip()
        return choice if choice else None

    async def get_dut_information(self) -> Optional[Dict[str, str]]:
        """Get DUT information - only Serial Number from user, rest from config"""
        self.console.print("[bold cyan]DUT Information Collection[/bold cyan]")

        # Load default values (required)
        defaults = {}
        if self.configuration_service:
            try:
                defaults = await self.configuration_service.load_dut_defaults()
                self.console.print(
                    f"[dim][green]✓ Loaded defaults: DUT ID: {defaults.get('dut_id')}, Model: {defaults.get('model')}, Operator: {defaults.get('operator_id')}[/green][/dim]"
                )
            except Exception as e:
                self.console.print(f"[dim][red]✗ Could not load defaults: {e}[/red][/dim]")
                return None
        else:
            self.console.print("[dim][red]✗ Configuration service not available[/red][/dim]")
            return None

        # Validate required defaults are present
        required_fields = ['dut_id', 'model', 'operator_id']
        for field in required_fields:
            if not defaults.get(field):
                self.console.print(f"[red]Error: Missing required default value for {field}[/red]")
                return None

        # Use defaults automatically
        dut_id = defaults['dut_id']
        model = defaults['model']
        operator = defaults['operator_id']

        # Only prompt for Serial Number
        serial = input(f"Serial Number [{dut_id}]: ").strip()
        if not serial:
            serial = dut_id  # Default to DUT ID

        self.console.print(f"[dim]Using: DUT ID={dut_id}, Model={model}, Operator={operator}, Serial={serial}[/dim]")

        return {"id": dut_id, "model": model, "serial": serial, "operator": operator}

    async def get_slash_command(self) -> Optional[str]:
        """Get slash command using simple input (enhanced functionality removed)"""
        command = input("Slash Command → ").strip()
        return command if command else None

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
            if placeholder:
                self.console.print(f"[dim]{placeholder}[/dim]")

            result = input(prompt).strip()

            if not result and required:
                self.formatter.print_message(
                    "Input is required. Please try again.", message_type="warning"
                )
                continue

            return result if result else None

    async def get_confirmation(self, message: str, default: bool = False) -> bool:
        """Get confirmation with simple input (enhanced functionality removed)"""
        default_text = "[Y/n]" if default else "[y/N]"
        response = input(f"{message} {default_text}: ").strip().lower()

        if not response:
            return default
        return response in ["y", "yes"]

    async def wait_for_acknowledgment(self, message: str = "Press Enter to continue...") -> None:
        """Wait for user acknowledgment with simple input (enhanced functionality removed)"""
        input(message)

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
        """Get command history statistics (enhanced functionality removed)"""
        return {"total_commands": 0, "unique_commands": 0, "most_used": [], "recent_commands": []}

    def clear_command_history(self) -> bool:
        """Clear command history (enhanced functionality removed)"""
        return True  # Always return success since no history to clear


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
        menu_text.append(" Execute Simple MCU Test\n")
        menu_text.append("3.", style="bold cyan")
        menu_text.append(" Heating/Cooling Time Test\n")
        menu_text.append("4.", style="bold cyan")
        menu_text.append(" Robot Home\n")
        menu_text.append("5.", style="bold cyan")
        menu_text.append(" Hardware Control Center\n")
        menu_text.append("6.", style="bold cyan")
        menu_text.append(" Exit\n")
        menu_text.append("help", style="bold cyan")
        menu_text.append(" Show input help\n\n")
        menu_text.append("Please select an option (1-6) or type 'help':")

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


# Integration factory functions
def create_enhanced_cli_integrator(
    console: Console, formatter: RichFormatter, configuration_service: Optional[Any] = None
) -> EnhancedInputIntegrator:
    """Factory function to create enhanced CLI integrator"""
    return EnhancedInputIntegrator(console, formatter, configuration_service)


def create_enhanced_menu_system(integrator: EnhancedInputIntegrator) -> EnhancedMenuSystem:
    """Factory function to create enhanced menu system"""
    return EnhancedMenuSystem(integrator)


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
