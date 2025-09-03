"""
Abstract Base Hardware Controller

Provides common functionality for all hardware controllers including
connection management, status display, and shared UI patterns.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from rich.status import Status

from ...rich_formatter import RichFormatter


def simple_interactive_menu(console, menu_options: dict, title: str, prompt: str) -> Optional[str]:
    """Simple replacement for RichUIManager.create_interactive_menu"""
    console.print(f"\n[bold blue]{title}[/bold blue]")
    console.print()

    # Display menu options
    for key, value in menu_options.items():
        console.print(f"  {key}. {value}")

    console.print()

    while True:
        try:
            choice = input(f"{prompt}: ").strip()
            if choice in menu_options:
                return choice
            else:
                console.print(f"[red]Invalid choice: {choice}[/red]")
        except (KeyboardInterrupt, EOFError):
            return None


class HardwareController(ABC):
    """Abstract base class for hardware controllers

    Provides common functionality including:
    - Connection/disconnection patterns
    - Status display logic
    - Progress display management
    - Menu creation utilities
    """

    def __init__(self, formatter: RichFormatter):
        self.formatter = formatter

    @abstractmethod
    async def show_status(self) -> None:
        """Display hardware status"""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to hardware"""

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from hardware"""

    @abstractmethod
    async def show_control_menu(self) -> Optional[str]:
        """Show hardware-specific control menu"""

    @abstractmethod
    async def execute_command(self, command: str) -> bool:
        """Execute hardware-specific command"""

    # Common helper methods
    async def _show_progress_with_message(
        self,
        message: str,
        operation,
        success_message: str,
        error_message: str,
        show_time: float = 0.5,
    ) -> bool:
        """Show progress display while executing operation

        Args:
            message: Progress message to display
            operation: Async function to execute
            success_message: Message to show on success
            error_message: Base error message
            show_time: Time to show spinner for visibility

        Returns:
            bool: True if operation succeeded, False otherwise
        """
        try:
            with self.formatter.create_progress_display(
                message, show_spinner=True
            ) as progress_display:
                if isinstance(progress_display, Status):
                    progress_display.update(message)
                await asyncio.sleep(show_time)  # Show spinner for visibility

                await operation()

                if isinstance(progress_display, Status):
                    progress_display.update(success_message)
                    await asyncio.sleep(0.3)  # Show success message briefly

            self.formatter.print_message(success_message, message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(f"{error_message}: {str(e)}", message_type="error")
            return False

    def _create_enhanced_menu(self, base_options: dict, shortcuts: Optional[dict] = None) -> dict:
        """Create enhanced menu with shortcuts

        Args:
            base_options: Base menu options
            shortcuts: Optional shortcut mappings

        Returns:
            dict: Enhanced menu options
        """
        enhanced_options = base_options.copy()

        # Add standard back option
        enhanced_options["b"] = "Back to Hardware Menu"

        # Add shortcuts if provided
        if shortcuts:
            enhanced_options.update(shortcuts)

        return enhanced_options

    def _format_connection_status(self, is_connected: bool) -> str:
        """Format connection status with emoji"""
        return "Connected" if is_connected else "Disconnected"

    def _get_user_input_with_validation(
        self, prompt: str, input_type: type = str, allow_cancel: bool = True, validator=None
    ):
        """Get user input with type validation and cancellation support

        Args:
            prompt: Input prompt to display
            input_type: Expected input type (str, float, int)
            allow_cancel: Whether to allow 'cancel' input
            validator: Optional validation function

        Returns:
            Validated input value or None if cancelled
        """
        while True:
            try:
                self.formatter.console.print(f"[bold cyan]{prompt}[/bold cyan]")
                if allow_cancel:
                    self.formatter.console.print(
                        "[yellow]   Enter value or 'cancel' to abort:[/yellow]"
                    )

                user_input = input("  → ").strip()

                if allow_cancel and (not user_input or user_input.lower() == "cancel"):
                    return None

                # Type conversion
                if input_type is not str:
                    converted_value = input_type(user_input)
                else:
                    converted_value = user_input

                # Custom validation
                if validator and not validator(converted_value):
                    self.formatter.print_message("Invalid input value", message_type="error")
                    continue

                return converted_value

            except ValueError:
                self.formatter.print_message(
                    f"Invalid {input_type.__name__} value - please try again", message_type="error"
                )
            except (KeyboardInterrupt, EOFError):
                return None
