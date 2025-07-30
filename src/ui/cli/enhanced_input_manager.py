"""
Enhanced Input Manager with prompt_toolkit Integration

Comprehensive input management system that provides advanced CLI input capabilities
including auto-completion, command history, syntax highlighting, and real-time validation.
This module integrates seamlessly with the existing Rich UI system while providing
professional-grade input features.

Key Features:
- Auto-completion for slash commands, hardware names, and parameters
- Persistent command history with search and filtering capabilities
- Syntax highlighting for different command types
- Real-time input validation with visual feedback
- Multi-line input support for complex operations
- Cross-platform compatibility with graceful fallbacks
- Integration with existing Rich UI components
"""

import asyncio
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable

# Conditional import for prompt_toolkit with graceful fallback
try:
    from prompt_toolkit import prompt
    from prompt_toolkit.application import Application
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import (
        Completer,
        Completion,
        PathCompleter,
        WordCompleter,
    )
    from prompt_toolkit.document import Document
    from prompt_toolkit.formatted_text import FormattedText
    from prompt_toolkit.history import FileHistory, InMemoryHistory
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.lexers import Lexer
    from prompt_toolkit.shortcuts import confirm
    from prompt_toolkit.styles import Style
    from prompt_toolkit.validation import ValidationError, Validator

    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

from loguru import logger
from rich.console import Console

from .rich_formatter import RichFormatter


class EnhancedInputConfig:
    """Configuration settings for the enhanced input system"""

    # History settings
    MAX_HISTORY_ENTRIES = 1000
    HISTORY_FILE_NAME = ".eol_tester_history"

    # Input validation settings
    MAX_INPUT_LENGTH = 500
    TIMEOUT_SECONDS = 300  # 5 minutes timeout for input

    # Auto-completion settings
    MAX_COMPLETIONS = 50
    COMPLETION_TIMEOUT = 0.5  # seconds

    # Visual settings
    PROMPT_STYLE = "bold green"
    ERROR_STYLE = "bold red"
    SUCCESS_STYLE = "bold cyan"
    WARNING_STYLE = "bold yellow"


class SlashCommandLexer(Lexer):
    """Custom lexer for syntax highlighting of slash commands"""

    def __init__(self):
        self.command_pattern = re.compile(r"^(/\w+)")
        self.subcommand_pattern = re.compile(r"(/\w+)\s+(\w+)")
        self.argument_pattern = re.compile(r"(/\w+)\s+(\w+)\s+(.*)")

    def lex_document(self, document: Document) -> Callable[[int], FormattedText]:
        """Apply syntax highlighting to the document"""

        def get_line_tokens(line_number: int) -> FormattedText:
            try:
                line = document.lines[line_number]
                return self._highlight_line(line)
            except IndexError:
                return FormattedText([])

        return get_line_tokens

    def _highlight_line(self, line: str) -> FormattedText:
        """Highlight a single line of text"""
        if not line.strip():
            return FormattedText([])

        tokens = []

        # Check for slash command pattern
        if line.startswith("/"):
            # Match full command with arguments
            arg_match = self.argument_pattern.match(line)
            if arg_match:
                command, subcommand, arguments = arg_match.groups()
                tokens.extend(
                    [
                        ("class:slash-command", command),
                        ("", " "),
                        ("class:subcommand", subcommand),
                        ("", " "),
                        ("class:arguments", arguments),
                    ]
                )
            else:
                # Match command with subcommand
                sub_match = self.subcommand_pattern.match(line)
                if sub_match:
                    command, subcommand = sub_match.groups()
                    tokens.extend(
                        [
                            ("class:slash-command", command),
                            ("", " "),
                            ("class:subcommand", subcommand),
                        ]
                    )
                else:
                    # Just command
                    cmd_match = self.command_pattern.match(line)
                    if cmd_match:
                        command = cmd_match.group(1)
                        remaining = line[len(command) :]
                        tokens.extend([("class:slash-command", command), ("", remaining)])
                    else:
                        tokens.append(("", line))
        else:
            # Regular text
            tokens.append(("", line))

        return FormattedText(tokens)


class SlashCommandCompleter(Completer):
    """Advanced auto-completion system for slash commands and parameters"""

    def __init__(self):
        # Define command completion data
        self.commands = {
            "/robot": {
                "subcommands": ["connect", "disconnect", "status", "init", "stop"],
                "description": "Control robot hardware (AJINEXTEK)",
                "parameters": {
                    "connect": [],
                    "disconnect": [],
                    "status": [],
                    "init": [],
                    "stop": [],
                },
            },
            "/mcu": {
                "subcommands": ["connect", "disconnect", "status", "temp", "testmode", "fan"],
                "description": "Control MCU hardware (LMA Temperature)",
                "parameters": {
                    "connect": [],
                    "disconnect": [],
                    "status": [],
                    "temp": ["25.0", "85.0", "105.0"],  # Common test temperatures
                    "testmode": [],
                    "fan": ["0", "25", "50", "75", "100"],  # Fan speed percentages
                },
            },
            "/loadcell": {
                "subcommands": ["connect", "disconnect", "status", "read", "zero", "monitor"],
                "description": "Control LoadCell hardware (BS205)",
                "parameters": {
                    "connect": [],
                    "disconnect": [],
                    "status": [],
                    "read": [],
                    "zero": [],
                    "monitor": [],
                },
            },
            "/power": {
                "subcommands": [
                    "connect",
                    "disconnect",
                    "status",
                    "on",
                    "off",
                    "voltage",
                    "current",
                ],
                "description": "Control Power supply hardware (ODA)",
                "parameters": {
                    "connect": [],
                    "disconnect": [],
                    "status": [],
                    "on": [],
                    "off": [],
                    "voltage": ["5.0", "12.0", "24.0", "48.0"],  # Common voltages
                    "current": ["0.5", "1.0", "2.0", "5.0"],  # Common current limits
                },
            },
            "/all": {
                "subcommands": ["status"],
                "description": "Show all hardware status",
                "parameters": {"status": []},
            },
            "/help": {
                "subcommands": ["robot", "mcu", "loadcell", "power", "all"],
                "description": "Show help information",
                "parameters": {},
            },
        }

        # Common DUT IDs and test parameters for general completion
        self.common_dut_ids = ["WF001", "WF002", "TEST001", "PROTO01", "SAMPLE1"]
        self.common_models = ["WF-2024-A", "WF-2024-B", "WF-2023-X"]
        self.common_operators = ["Test", "Engineer1", "QA_Team", "Production"]

    def get_completions(self, document: Document, complete_event) -> List[Completion]:
        """Generate completions based on current input"""
        text = document.text_before_cursor
        words = text.split()

        if not text:
            # Show all available commands
            return [
                Completion(cmd, start_position=0, display_meta=info["description"])
                for cmd, info in self.commands.items()
            ]

        if text.startswith("/"):
            return self._complete_slash_command(text, words)
        else:
            return self._complete_general_input(text, words)

    def _complete_slash_command(self, text: str, words: List[str]) -> List[Completion]:
        """Complete slash commands, subcommands, and parameters"""
        if len(words) == 1:
            # Complete command
            partial_cmd = words[0]
            return [
                Completion(cmd, start_position=-len(partial_cmd), display_meta=info["description"])
                for cmd, info in self.commands.items()
                if cmd.startswith(partial_cmd)
            ]

        elif len(words) == 2:
            # Complete subcommand
            cmd = words[0]
            partial_sub = words[1]

            if cmd in self.commands:
                subcommands = self.commands[cmd]["subcommands"]
                return [
                    Completion(sub, start_position=-len(partial_sub), display_meta=f"{cmd} {sub}")
                    for sub in subcommands
                    if sub.startswith(partial_sub)
                ]

        elif len(words) >= 3:
            # Complete parameters
            cmd = words[0]
            sub = words[1]
            partial_param = words[-1]

            if cmd in self.commands and sub in self.commands[cmd]["parameters"]:
                params = self.commands[cmd]["parameters"][sub]
                return [
                    Completion(
                        param,
                        start_position=-len(partial_param),
                        display_meta=f"Parameter for {cmd} {sub}",
                    )
                    for param in params
                    if param.startswith(partial_param)
                ]

        return []

    def _complete_general_input(self, text: str, words: List[str]) -> List[Completion]:
        """Complete general input like DUT IDs, models, etc."""
        if not words:
            return []

        last_word = words[-1]
        completions = []

        # Add common DUT IDs
        for dut_id in self.common_dut_ids:
            if dut_id.startswith(last_word.upper()):
                completions.append(
                    Completion(dut_id, start_position=-len(last_word), display_meta="DUT ID")
                )

        # Add common models
        for model in self.common_models:
            if model.startswith(last_word.upper()):
                completions.append(
                    Completion(model, start_position=-len(last_word), display_meta="Model")
                )

        # Add common operators
        for operator in self.common_operators:
            if operator.lower().startswith(last_word.lower()):
                completions.append(
                    Completion(operator, start_position=-len(last_word), display_meta="Operator")
                )

        return completions[: EnhancedInputConfig.MAX_COMPLETIONS]


class InputValidator(Validator):
    """Real-time input validation with visual feedback"""

    def __init__(self, validation_type: str = "general"):
        self.validation_type = validation_type

        # Validation patterns
        self.patterns = {
            "dut_id": r"^[A-Z0-9_-]{1,20}$",
            "model": r"^[A-Za-z0-9_\-\s\.]{1,50}$",
            "serial": r"^[A-Za-z0-9_\-]{1,30}$",
            "operator": r"^[A-Za-z0-9_\-\s]{1,30}$",
            "slash_command": r"^/\w+(\s+\w+(\s+.*)?)?$",
            "general": r"^.{1,500}$",
        }

    def validate(self, document: Document) -> None:
        """Validate input in real-time"""
        text = document.text

        if not text:
            return  # Allow empty input

        # Check length limit
        if len(text) > EnhancedInputConfig.MAX_INPUT_LENGTH:
            raise ValidationError(
                message=f"Input too long (max {EnhancedInputConfig.MAX_INPUT_LENGTH} characters)",
                cursor_position=EnhancedInputConfig.MAX_INPUT_LENGTH,
            )

        # Apply pattern validation
        pattern = self.patterns.get(self.validation_type, self.patterns["general"])
        if not re.match(pattern, text):
            error_messages = {
                "dut_id": (
                    "DUT ID must contain only uppercase letters, numbers, underscores, and hyphens"
                ),
                "model": (
                    "Model must contain only letters, numbers, spaces, dots, underscores, and hyphens"
                ),
                "serial": (
                    "Serial number must contain only letters, numbers, underscores, and hyphens"
                ),
                "operator": (
                    "Operator ID must contain only letters, numbers, spaces, underscores, and hyphens"
                ),
                "slash_command": "Command must start with / followed by valid command syntax",
                "general": "Invalid input format",
            }

            raise ValidationError(
                message=error_messages.get(self.validation_type, "Invalid input format"),
                cursor_position=len(text),
            )


class EnhancedInputManager:
    """Comprehensive input management system with prompt_toolkit integration"""

    def __init__(self, console: Console, formatter: RichFormatter):
        self.console = console
        self.formatter = formatter
        self.config = EnhancedInputConfig()

        # Initialize history
        self.history_file = self._get_history_file_path()

        # Create style for prompt_toolkit
        self.style = Style.from_dict(
            {
                "slash-command": "#00aa00 bold",  # Green for slash commands
                "subcommand": "#0088ff bold",  # Blue for subcommands
                "arguments": "#ffaa00",  # Orange for arguments
                "prompt": "#00aa00 bold",  # Green prompt
                "error": "#ff0000 bold",  # Red for errors
                "success": "#00aa00",  # Green for success
                "warning": "#ffaa00",  # Orange for warnings
            }
        )

        # Initialize components
        self.completer = SlashCommandCompleter()
        self.lexer = SlashCommandLexer()

        logger.info(
            f"Enhanced Input Manager initialized (prompt_toolkit: {PROMPT_TOOLKIT_AVAILABLE})"
        )

    def _get_history_file_path(self) -> Path:
        """Get the path for the history file"""
        home_dir = Path.home()
        return home_dir / self.config.HISTORY_FILE_NAME

    async def get_input(
        self,
        prompt_text: str = "> ",
        input_type: str = "general",
        placeholder: str = "",
        multiline: bool = False,
        show_completions: bool = True,
        enable_history: bool = True,
        validator_type: str = None,
        timeout: Optional[float] = None,
    ) -> Optional[str]:
        """Get enhanced input with all advanced features

        Args:
            prompt_text: Text to show as prompt
            input_type: Type of input for validation and completion
            placeholder: Placeholder text to show when empty
            multiline: Enable multi-line input mode
            show_completions: Enable auto-completion
            enable_history: Enable command history
            validator_type: Type of validation to apply
            timeout: Input timeout in seconds

        Returns:
            Input string if successful, None if cancelled or timeout
        """
        if not PROMPT_TOOLKIT_AVAILABLE:
            return await self._fallback_input(prompt_text, input_type)

        try:
            # Setup history
            if enable_history and self.history_file.exists():
                history = FileHistory(str(self.history_file))
            else:
                history = InMemoryHistory()

            # Setup validator
            validator = None
            if validator_type or input_type != "general":
                validation_type = validator_type or input_type
                validator = InputValidator(validation_type)

            # Setup completer
            completer = self.completer if show_completions else None

            # Create key bindings
            kb = self._create_key_bindings()

            # Configure prompt session
            session_kwargs = {
                "message": FormattedText([("class:prompt", prompt_text)]),
                "history": history,
                "completer": completer,
                "validator": validator,
                "validate_while_typing": True,
                "lexer": self.lexer,
                "style": self.style,
                "auto_suggest": AutoSuggestFromHistory(),
                "key_bindings": kb,
                "complete_style": "multi-column",
                "placeholder": placeholder,
                "multiline": multiline,
                "wrap_lines": True,
                "mouse_support": True,
            }

            # Add timeout if specified
            if timeout:
                session_kwargs["timeout"] = timeout

            # Get input
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: prompt(**session_kwargs)
            )

            # Save to history if enabled and result is meaningful
            if enable_history and result and result.strip():
                self._save_to_history(result.strip())

            return result.strip() if result else None

        except KeyboardInterrupt:
            self.formatter.print_message("Input cancelled by user", "info")
            return None
        except EOFError:
            return None
        except Exception as e:
            logger.error(f"Enhanced input error: {e}")
            return await self._fallback_input(prompt_text, input_type)

    def _create_key_bindings(self) -> KeyBindings:
        """Create custom key bindings for enhanced functionality"""
        kb = KeyBindings()

        @kb.add("c-c")
        def _(event):
            """Handle Ctrl+C gracefully"""
            event.app.exit(exception=KeyboardInterrupt)

        @kb.add("c-d")
        def _(event):
            """Handle Ctrl+D (EOF)"""
            event.app.exit(exception=EOFError)

        @kb.add("c-l")
        def _(event):
            """Clear screen with Ctrl+L"""
            event.app.renderer.clear()

        return kb

    def _save_to_history(self, command: str) -> None:
        """Save command to persistent history"""
        try:
            # Load existing history
            history_data = []
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history_data = f.read().splitlines()

            # Add new command if not already the last one
            if not history_data or history_data[-1] != command:
                history_data.append(command)

            # Limit history size
            if len(history_data) > self.config.MAX_HISTORY_ENTRIES:
                history_data = history_data[-self.config.MAX_HISTORY_ENTRIES :]

            # Save updated history
            with open(self.history_file, "w", encoding="utf-8") as f:
                f.write("\n".join(history_data))

        except Exception as e:
            logger.warning(f"Failed to save command history: {e}")

    async def _fallback_input(self, prompt_text: str, input_type: str) -> Optional[str]:
        """Fallback input method when prompt_toolkit is not available"""
        try:
            self.console.print(f"[{self.config.PROMPT_STYLE}]{prompt_text}[/]", end="")

            # Use asyncio to allow for timeout
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, input)

            return result.strip() if result else None

        except (KeyboardInterrupt, EOFError):
            return None

    async def get_confirmation(self, message: str, default: bool = False) -> bool:
        """Get yes/no confirmation with enhanced UI"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            return await self._fallback_confirmation(message, default)

        try:
            # Use basic confirm function without style parameter for compatibility
            result = await asyncio.get_event_loop().run_in_executor(None, lambda: confirm(message))
            return result if result is not None else default

        except (KeyboardInterrupt, EOFError):
            return False
        except Exception as e:
            logger.error(f"Confirmation error: {e}")
            return await self._fallback_confirmation(message, default)

    async def _fallback_confirmation(self, message: str, default: bool) -> bool:
        """Fallback confirmation method"""
        suffix = " [Y/n]" if default else " [y/N]"
        response = await self._fallback_input(f"{message}{suffix}: ", "general")

        if not response:
            return default

        return response.lower().startswith("y")

    async def get_multiline_input(
        self, prompt_text: str = "Enter text (Ctrl+D to finish):\n", input_type: str = "general"
    ) -> Optional[str]:
        """Get multi-line input with enhanced features"""
        return await self.get_input(
            prompt_text=prompt_text,
            input_type=input_type,
            multiline=True,
            placeholder="Type your text here... (Ctrl+D when finished)",
        )

    def get_completion_suggestions(self, text: str) -> List[str]:
        """Get completion suggestions for given text"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            return []

        document = Document(text, len(text))
        completions = self.completer.get_completions(document, None)

        return [completion.text for completion in completions]

    def validate_input_format(self, text: str, input_type: str) -> Tuple[bool, str]:
        """Validate input format and return result with error message"""
        try:
            validator = InputValidator(input_type)
            document = Document(text)
            validator.validate(document)
            return True, ""
        except ValidationError as e:
            return False, e.message

    async def get_dut_info_interactive(self) -> Optional[Dict[str, str]]:
        """Interactive DUT information collection with enhanced input"""
        try:
            self.formatter.print_header("DUT Information Collection")

            # DUT ID (required)
            self.console.print("\n[bold cyan]DUT ID[/bold cyan] (required):")
            dut_id = await self.get_input(
                prompt_text="  → ",
                input_type="dut_id",
                placeholder="e.g., WF001, TEST001",
                show_completions=True,
                validator_type="dut_id",
            )

            if not dut_id:
                self.formatter.print_message("DUT ID is required", "error")
                return None

            # Model (optional)
            self.console.print("\n[bold cyan]Model[/bold cyan] (optional):")
            model = (
                await self.get_input(
                    prompt_text="  → ",
                    input_type="model",
                    placeholder="e.g., WF-2024-A (press Enter for 'Unknown')",
                    show_completions=True,
                    validator_type="model",
                )
                or "Unknown"
            )

            # Serial Number (optional)
            self.console.print("\n[bold cyan]Serial Number[/bold cyan] (optional):")
            serial = (
                await self.get_input(
                    prompt_text="  → ",
                    input_type="serial",
                    placeholder="e.g., S001 (press Enter for 'N/A')",
                    validator_type="serial",
                )
                or "N/A"
            )

            # Operator (optional)
            self.console.print("\n[bold cyan]Operator ID[/bold cyan] (optional):")
            operator = (
                await self.get_input(
                    prompt_text="  → ",
                    input_type="operator",
                    placeholder="e.g., Test, Engineer1 (press Enter for 'Test')",
                    show_completions=True,
                    validator_type="operator",
                )
                or "Test"
            )

            # Confirmation
            dut_info = {"id": dut_id, "model": model, "serial": serial, "operator": operator}

            # Display collected information
            self.formatter.print_status(
                "DUT Information Collected",
                "READY",
                details={"DUT ID": dut_id, "Model": model, "Serial": serial, "Operator": operator},
            )

            # Confirm information
            if await self.get_confirmation("\nIs this information correct?", default=True):
                return dut_info
            else:
                self.formatter.print_message("DUT information collection cancelled", "warning")
                return None

        except (KeyboardInterrupt, EOFError):
            self.formatter.print_message("DUT information collection cancelled", "info")
            return None

    async def get_slash_command_interactive(self) -> Optional[str]:
        """Interactive slash command input with full enhancement features"""
        try:
            return await self.get_input(
                prompt_text="$ ",
                input_type="slash_command",
                placeholder="Type a slash command (e.g., /robot connect) or 'exit' to quit",
                show_completions=True,
                enable_history=True,
                validator_type="slash_command",
            )
        except (KeyboardInterrupt, EOFError):
            return None

    def get_history_stats(self) -> Dict[str, Any]:
        """Get command history statistics"""
        try:
            if not self.history_file.exists():
                return {
                    "total_commands": 0,
                    "unique_commands": 0,
                    "most_used": [],
                    "recent_commands": [],
                }

            with open(self.history_file, "r", encoding="utf-8") as f:
                commands = f.read().splitlines()

            from collections import Counter

            command_counts = Counter(commands)

            return {
                "total_commands": len(commands),
                "unique_commands": len(command_counts),
                "most_used": command_counts.most_common(10),
                "recent_commands": commands[-10:] if commands else [],
            }

        except Exception as e:
            logger.error(f"Error getting history stats: {e}")
            return {
                "total_commands": 0,
                "unique_commands": 0,
                "most_used": [],
                "recent_commands": [],
            }

    def clear_history(self) -> bool:
        """Clear command history"""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False


# Integration helper functions
def create_enhanced_input_manager(
    console: Console, formatter: RichFormatter
) -> EnhancedInputManager:
    """Factory function to create EnhancedInputManager instance"""
    return EnhancedInputManager(console, formatter)


def is_prompt_toolkit_available() -> bool:
    """Check if prompt_toolkit is available"""
    return PROMPT_TOOLKIT_AVAILABLE


# Example usage and integration patterns
async def demo_enhanced_input():
    """Demonstration of enhanced input capabilities"""
    console = Console()
    formatter = RichFormatter(console)
    input_manager = EnhancedInputManager(console, formatter)

    # Demo various input types
    console.print("[bold]Enhanced Input Manager Demo[/bold]\n")

    # Slash command input
    console.print("[cyan]1. Slash Command Input:[/cyan]")
    slash_cmd = await input_manager.get_slash_command_interactive()
    console.print(f"Got command: {slash_cmd}\n")

    # DUT information collection
    console.print("[cyan]2. DUT Information Collection:[/cyan]")
    dut_info = await input_manager.get_dut_info_interactive()
    console.print(f"Got DUT info: {dut_info}\n")

    # Multi-line input
    console.print("[cyan]3. Multi-line Input:[/cyan]")
    multiline = await input_manager.get_multiline_input()
    console.print(f"Got multi-line: {multiline}\n")

    # Confirmation
    console.print("[cyan]4. Confirmation:[/cyan]")
    confirmed = await input_manager.get_confirmation("Continue with demo?")
    console.print(f"Confirmed: {confirmed}\n")

    # History stats
    console.print("[cyan]5. History Statistics:[/cyan]")
    stats = input_manager.get_history_stats()
    console.print(f"History stats: {stats}")


if __name__ == "__main__":
    # Run demo if executed directly
    asyncio.run(demo_enhanced_input())
