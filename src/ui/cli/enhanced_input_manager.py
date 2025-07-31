"""
Enhanced Input Manager - Refactored Version

Comprehensive input management system with clean backend abstraction.
Provides advanced CLI input capabilities with graceful fallbacks.

Key Features:
- Clean backend abstraction (prompt_toolkit or basic)
- Auto-completion for slash commands and parameters
- Persistent command history with search capabilities
- Input validation with visual feedback
- Multi-line input support
- Cross-platform compatibility
"""

import asyncio
import re
from collections import Counter
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, cast

from loguru import logger
from rich.console import Console

from .backends import create_input_backend
from .input_protocols import (
    COMMAND_COMPLETIONS,
    COMMON_DUT_IDS,
    COMMON_MODELS,
    COMMON_OPERATORS,
    VALIDATION_ERROR_MESSAGES,
    VALIDATION_PATTERNS,
    CompleterProtocol,
    DocumentProtocol,
    EnhancedInputConfig,
    InputBackend,
    ValidatorProtocol,
)
from .rich_formatter import RichFormatter


class SlashCommandLexer:
    """Custom lexer for syntax highlighting of slash commands"""

    def __init__(self, backend: InputBackend):
        self.backend = backend
        self.command_pattern = re.compile(r"^(/\w+)")
        self.subcommand_pattern = re.compile(r"(/\w+)\s+(\w+)")
        self.argument_pattern = re.compile(r"(/\w+)\s+(\w+)\s+(.*)")

    def lex_document(self, document: DocumentProtocol):
        """Apply syntax highlighting to the document"""

        def get_line_tokens(line_number: int):
            try:
                line = document.lines[line_number]
                return self._highlight_line(line)
            except IndexError:
                return self.backend.create_formatted_text([])

        return get_line_tokens

    def _highlight_line(self, line: str):
        """Highlight a single line of text"""
        if not line.strip():
            return self.backend.create_formatted_text([])

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

        return self.backend.create_formatted_text(tokens)


class SlashCommandCompleter:
    """Advanced auto-completion system for slash commands and parameters"""

    def __init__(self, backend: InputBackend):
        self.backend = backend
        self.commands = COMMAND_COMPLETIONS
        self.common_dut_ids = COMMON_DUT_IDS
        self.common_models = COMMON_MODELS
        self.common_operators = COMMON_OPERATORS

    def get_completions(self, document: DocumentProtocol, complete_event: Any):
        """Generate completions based on current input"""
        text = document.text_before_cursor
        words = text.split()

        if not text:
            # Show all available commands
            return [
                self.backend.create_completion(cmd, 0, str(info["description"]))
                for cmd, info in self.commands.items()
            ]

        if text.startswith("/"):
            return self._complete_slash_command(text, words)
        return self._complete_general_input(text, words)

    async def get_completions_async(self, document: DocumentProtocol, complete_event: Any) -> AsyncGenerator:
        """Async version of get_completions for modern prompt_toolkit compatibility"""
        # For now, just return the sync version results
        # In the future, this could be enhanced with actual async completion logic
        completions = self.get_completions(document, complete_event)
        for completion in completions:
            yield completion

    def _complete_slash_command(self, text: str, words: List[str]):
        """Complete slash commands, subcommands, and parameters"""
        if len(words) == 1:
            # Complete command
            partial_cmd = words[0]
            return [
                self.backend.create_completion(cmd, -len(partial_cmd), str(info["description"]))
                for cmd, info in self.commands.items()
                if cmd.startswith(partial_cmd)
            ]

        if len(words) == 2:
            # Complete subcommand
            cmd = words[0]
            partial_sub = words[1]

            if cmd in self.commands:
                subcommands = self.commands[cmd]["subcommands"]
                return [
                    self.backend.create_completion(sub, -len(partial_sub), f"{cmd} {sub}")
                    for sub in subcommands
                    if sub.startswith(partial_sub)
                ]

        if len(words) >= 3:
            # Complete parameters
            cmd = words[0]
            sub = words[1]
            partial_param = words[-1]

            if cmd in self.commands and "parameters" in self.commands[cmd]:
                cmd_params = self.commands[cmd]["parameters"]
                if isinstance(cmd_params, dict) and sub in cmd_params:
                    params = cmd_params[sub]
                    return [
                        self.backend.create_completion(
                            param, -len(partial_param), f"Parameter for {cmd} {sub}"
                        )
                        for param in params
                        if param.startswith(partial_param)
                    ]

        return []

    def _complete_general_input(self, text: str, words: List[str]):
        """Complete general input like DUT IDs, models, etc."""
        if not words:
            return []

        last_word = words[-1]
        completions = []

        # Add common DUT IDs
        for dut_id in self.common_dut_ids:
            if dut_id.startswith(last_word.upper()):
                completions.append(
                    self.backend.create_completion(dut_id, -len(last_word), "DUT ID")
                )

        # Add common models
        for model in self.common_models:
            if model.startswith(last_word.upper()):
                completions.append(self.backend.create_completion(model, -len(last_word), "Model"))

        # Add common operators
        for operator in self.common_operators:
            if operator.lower().startswith(last_word.lower()):
                completions.append(
                    self.backend.create_completion(operator, -len(last_word), "Operator")
                )

        return completions[: EnhancedInputConfig.MAX_COMPLETIONS]


class InputValidator:
    """Real-time input validation with visual feedback"""

    def __init__(self, backend: InputBackend, validation_type: str = "general"):
        self.backend = backend
        self.validation_type = validation_type
        self.patterns = VALIDATION_PATTERNS
        self.error_messages = VALIDATION_ERROR_MESSAGES

    def validate(self, document: DocumentProtocol) -> None:
        """Validate input in real-time"""
        text = document.text

        if not text:
            return  # Allow empty input

        # Check length limit
        if len(text) > EnhancedInputConfig.MAX_INPUT_LENGTH:
            error = self.backend.create_validation_error(
                f"Input too long (max {EnhancedInputConfig.MAX_INPUT_LENGTH} characters)",
                EnhancedInputConfig.MAX_INPUT_LENGTH,
            )
            # Convert to actual exception if it's not already
            if isinstance(error, Exception):
                raise error
            else:
                raise ValueError(
                    f"Input too long (max {EnhancedInputConfig.MAX_INPUT_LENGTH} characters)"
                )

        # Apply pattern validation
        pattern = self.patterns.get(self.validation_type, self.patterns["general"])
        if not re.match(pattern, text):
            message = self.error_messages.get(self.validation_type, "Invalid input format")
            error = self.backend.create_validation_error(message, len(text))
            # Convert to actual exception if it's not already
            if isinstance(error, Exception):
                raise error
            else:
                raise ValueError(message)

    async def validate_async(self, document: DocumentProtocol) -> None:
        """Async version of validate for modern prompt_toolkit compatibility"""
        # For now, just call the sync version
        # In the future, this could be enhanced with actual async validation logic
        self.validate(document)


class EnhancedInputManager:
    """Comprehensive input management system with backend abstraction"""

    def __init__(
        self,
        console: Console,
        formatter: RichFormatter,
        default_model: Optional[str] = None,
        configuration_service: Optional[Any] = None,
    ):
        self.console = console
        self.formatter = formatter
        self.config = EnhancedInputConfig()
        self.default_model = default_model
        self.configuration_service = configuration_service

        # Create backend
        self.backend = create_input_backend()

        # Initialize history
        self.history_file = self._get_history_file_path()

        # Create style
        self.style = self.backend.create_style(self.config.STYLE_DICT)

        # Initialize components
        self.completer = SlashCommandCompleter(self.backend)
        self.lexer = SlashCommandLexer(self.backend)

        logger.info(f"Enhanced Input Manager initialized (backend: {type(self.backend).__name__})")

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
        validator_type: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Optional[str]:
        """Get enhanced input with all advanced features"""
        try:
            # Setup history
            history = None
            if enable_history:
                if self.history_file.exists():
                    history = self.backend.create_file_history(str(self.history_file))
                else:
                    history = self.backend.create_memory_history()

            # Setup validator
            validator = None
            if validator_type or input_type != "general":
                validation_type = validator_type or input_type
                validator = cast(ValidatorProtocol, InputValidator(self.backend, validation_type))

            # Setup completer
            completer = cast(CompleterProtocol, self.completer) if show_completions else None

            # Setup auto-suggest
            auto_suggest = self.backend.create_auto_suggest()

            # Create key bindings
            key_bindings = self._create_key_bindings()

            # Get input using backend
            kwargs = {}
            if timeout:
                kwargs["timeout"] = timeout

            result = await self.backend.prompt(
                message=prompt_text,
                history=history,
                completer=completer,
                validator=validator,
                lexer=self.lexer,
                style=self.style,
                auto_suggest=auto_suggest,
                key_bindings=key_bindings,
                placeholder=placeholder,
                multiline=multiline,
                **kwargs,
            )

            # Save to history if enabled and result is meaningful
            if enable_history and result and result.strip():
                self._save_to_history(result.strip())

            return result.strip() if result else None

        except (KeyboardInterrupt, EOFError):
            self.formatter.print_message("Input cancelled by user", "info")
            return None
        except Exception as e:
            logger.error("Enhanced input error: %s", e)
            # Fallback to basic input
            return await self._basic_fallback_input(prompt_text)

    def _create_key_bindings(self):
        """Create custom key bindings for enhanced functionality"""
        if not self.backend.is_available:
            return None

        try:
            kb = self.backend.create_key_bindings()

            # Add custom key bindings if backend supports it
            if hasattr(kb, "add"):

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
        except Exception:
            return None

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
            logger.warning("Failed to save command history: %s", e)

    async def _basic_fallback_input(self, prompt_text: str) -> Optional[str]:
        """Basic fallback input when all else fails"""
        try:
            self.console.print(f"[{self.config.PROMPT_STYLE}]{prompt_text}[/]", end="")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, input)
            return result.strip() if result else None
        except (KeyboardInterrupt, EOFError):
            return None

    async def get_confirmation(self, message: str, default: bool = False) -> bool:
        """Get yes/no confirmation with enhanced UI"""
        try:
            return await self.backend.confirm(message, default)
        except Exception:
            # Fallback to basic confirmation
            suffix = " [Y/n]" if default else " [y/N]"
            response = await self._basic_fallback_input(f"{message}{suffix}: ")

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
        try:
            document = self.backend.create_document(text, len(text))
            completions = self.completer.get_completions(document, None)
            return [completion.text for completion in completions]
        except Exception:
            return []

    def validate_input_format(self, text: str, input_type: str) -> Tuple[bool, str]:
        """Validate input format and return result with error message"""
        try:
            validator = cast(ValidatorProtocol, InputValidator(self.backend, input_type))
            document = self.backend.create_document(text)
            validator.validate(document)
            return True, ""
        except Exception as e:
            return False, str(e)

    async def get_dut_info_interactive(self) -> Optional[Dict[str, str]]:
        """Interactive DUT information collection with file-based defaults"""
        try:
            self.formatter.print_header("DUT Information Collection")

            # Load DUT defaults from configuration file
            dut_defaults = {}
            try:
                if self.configuration_service:
                    dut_defaults = await self.configuration_service.load_dut_defaults()
                    self.console.print("[dim]✓ DUT defaults loaded from configuration file[/dim]\n")
                else:
                    logger.warning("Configuration service not available, using fallback values")
            except Exception as e:
                logger.warning(f"Failed to load DUT defaults: {e}")
                self.console.print(f"[yellow]⚠ Could not load DUT defaults: {e}[/yellow]")
                self.console.print("[dim]Using fallback values...[/dim]\n")

            # Use loaded defaults or fallback values
            dut_id = dut_defaults.get("dut_id", "DEFAULT001")
            model = dut_defaults.get("model", "Default Model")
            operator_id = dut_defaults.get("operator_id", "DEFAULT_OP")

            # Display auto-populated information
            self.console.print("📋 [bold cyan]Auto-populated DUT Information:[/bold cyan]")
            self.console.print(
                f"   [bold cyan]DUT ID:[/bold cyan] [green]{dut_id}[/green] [dim](from configuration)[/dim]"
            )
            self.console.print(
                f"   [bold cyan]Model:[/bold cyan] [green]{model}[/green] [dim](from configuration)[/dim]"
            )
            self.console.print(
                f"   [bold cyan]Operator:[/bold cyan] [green]{operator_id}[/green] [dim](from configuration)[/dim]"
            )

            # Serial Number (only user input required)
            self.console.print("\n[bold cyan]Serial Number[/bold cyan] [red](required)[/red]:")
            serial = await self.get_input(
                prompt_text="  → ",
                input_type="serial",
                placeholder="e.g., S001, SN20250730001",
                validator_type="serial",
            )

            if not serial or not serial.strip():
                self.formatter.print_message("Serial Number is required", "error")
                return None

            # Create final DUT information
            dut_info = {
                "id": dut_id,
                "model": model,
                "serial": serial.strip(),
                "operator": operator_id,
            }

            # Display collected information summary
            self.formatter.print_status(
                "DUT Information Ready",
                "COMPLETE",
                details={
                    "DUT ID": dut_id + " (auto)",
                    "Model": model + " (auto)",
                    "Serial": serial.strip() + " (user input)",
                    "Operator": operator_id + " (auto)",
                },
            )

            self.formatter.print_message(
                "DUT information collection completed successfully", "success"
            )
            return dut_info

        except (KeyboardInterrupt, EOFError):
            self.formatter.print_message("DUT information collection cancelled by user", "info")
            return None
        except Exception as e:
            self.formatter.print_message(f"Error during DUT information collection: {e}", "error")
            logger.error(f"DUT info collection error: {e}")
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

            command_counts = Counter(commands)

            return {
                "total_commands": len(commands),
                "unique_commands": len(command_counts),
                "most_used": command_counts.most_common(10),
                "recent_commands": commands[-10:] if commands else [],
            }

        except Exception as e:
            logger.error("Error getting history stats: %s", e)
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
            logger.error("Error clearing history: %s", e)
            return False


# Integration helper functions
def create_enhanced_input_manager(
    console: Console,
    formatter: RichFormatter,
    default_model: Optional[str] = None,
    configuration_service: Optional[Any] = None,
) -> EnhancedInputManager:
    """Factory function to create EnhancedInputManager instance"""
    return EnhancedInputManager(console, formatter, default_model, configuration_service)


def is_prompt_toolkit_available() -> bool:
    """Check if prompt_toolkit is available"""
    from .backends.backend_factory import is_prompt_toolkit_available as _is_available

    return _is_available()


# Example usage
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
