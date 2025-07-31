"""
Basic Input Backend

Fallback implementation that doesn't require prompt_toolkit.
Provides basic input functionality using standard Python input().
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional

from ..input_protocols import (
    AutoSuggestProtocol,
    CompletionProtocol,
    CompleterProtocol,
    DocumentProtocol,
    FormattedTextProtocol,
    HistoryProtocol,
    InputBackend,
    KeyBindingsProtocol,
    LexerProtocol,
    StyleProtocol,
    ValidationErrorProtocol,
    ValidatorProtocol,
)


class BasicDocument:
    """Basic document implementation"""

    def __init__(self, text: str, cursor_position: int = 0):
        self.text = text
        self.cursor_position = cursor_position
        self.text_before_cursor = text[:cursor_position]
        self.lines = text.split("\n")


class BasicCompletion:
    """Basic completion implementation"""

    def __init__(self, text: str, start_position: int = 0, display_meta: str = ""):
        self.text = text
        self.start_position = start_position
        self.display_meta = display_meta


class BasicValidationError(Exception):
    """Basic validation error implementation"""

    def __init__(self, message: str, cursor_position: int = 0):
        super().__init__(message)
        self.message = message
        self.cursor_position = cursor_position


class BasicFormattedText:
    """Basic formatted text implementation"""

    def __init__(self, data: Any):
        self.data = data


class BasicHistory:
    """Basic history implementation"""

    def __init__(self, filename: Optional[str] = None):
        self.filename = filename


class BasicStyle:
    """Basic style implementation"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def from_dict(data: Dict[str, str]) -> "BasicStyle":
        return BasicStyle()


class BasicKeyBindings:
    """Basic key bindings implementation"""

    def add(self, key: str) -> Callable[[Callable], Callable]:
        def decorator(func: Callable) -> Callable:
            return func

        return decorator


class BasicCompleter:
    """Basic completer implementation"""

    def get_completions(
        self, document: DocumentProtocol, complete_event: Any
    ) -> List[CompletionProtocol]:
        return []


class BasicLexer:
    """Basic lexer implementation"""

    def lex_document(self, document: DocumentProtocol) -> Callable[[int], FormattedTextProtocol]:
        def get_line_tokens(line_number: int) -> FormattedTextProtocol:
            return BasicFormattedText([])

        return get_line_tokens


class BasicValidator:
    """Basic validator implementation"""

    def validate(self, document: DocumentProtocol) -> None:
        pass


class BasicAutoSuggest:
    """Basic auto-suggest implementation"""

    pass


class BasicInputBackend(InputBackend):
    """Basic input backend using standard Python input()"""

    @property
    def is_available(self) -> bool:
        """Basic backend is always available"""
        return True

    def create_document(self, text: str, cursor_position: int = 0) -> DocumentProtocol:
        """Create a basic document object"""
        return BasicDocument(text, cursor_position)

    def create_completion(
        self, text: str, start_position: int = 0, display_meta: str = ""
    ) -> CompletionProtocol:
        """Create a basic completion object"""
        return BasicCompletion(text, start_position, display_meta)

    def create_validation_error(
        self, message: str, cursor_position: int = 0
    ) -> ValidationErrorProtocol:
        """Create a basic validation error"""
        return BasicValidationError(message, cursor_position)

    def create_formatted_text(self, data: Any) -> FormattedTextProtocol:
        """Create basic formatted text"""
        return BasicFormattedText(data)

    def create_style(self, style_dict: Dict[str, str]) -> StyleProtocol:
        """Create a basic style object"""
        return BasicStyle()

    def create_file_history(self, filename: str) -> HistoryProtocol:
        """Create a basic file-based history object"""
        return BasicHistory(filename)

    def create_memory_history(self) -> HistoryProtocol:
        """Create a basic in-memory history object"""
        return BasicHistory()

    def create_key_bindings(self) -> KeyBindingsProtocol:
        """Create basic key bindings object"""
        return BasicKeyBindings()

    def create_auto_suggest(self) -> Optional[AutoSuggestProtocol]:
        """Create basic auto-suggestion provider"""
        return BasicAutoSuggest()

    async def prompt(
        self,
        message: str,
        history: Optional[HistoryProtocol] = None,
        completer: Optional[CompleterProtocol] = None,
        validator: Optional[ValidatorProtocol] = None,
        lexer: Optional[LexerProtocol] = None,
        style: Optional[StyleProtocol] = None,
        auto_suggest: Optional[AutoSuggestProtocol] = None,
        key_bindings: Optional[KeyBindingsProtocol] = None,
        placeholder: str = "",
        multiline: bool = False,
        **kwargs: Any,
    ) -> str:
        """Get input from user using basic input()"""
        try:
            # Show placeholder if provided and no message
            if placeholder and not message.strip():
                print(f"({placeholder})")

            # Use asyncio to allow for cancellation
            loop = asyncio.get_event_loop()

            if multiline:
                lines = []
                print(f"{message}")
                print("(Press Ctrl+D when finished, or enter a line with just '.' to finish)")
                try:
                    while True:
                        line = await loop.run_in_executor(None, input, "  ")
                        if line.strip() == ".":
                            break
                        lines.append(line)
                except EOFError:
                    pass
                return "\n".join(lines)
            else:
                result = await loop.run_in_executor(None, input, message)
                return result

        except (KeyboardInterrupt, EOFError):
            return ""

    async def confirm(self, message: str, default: bool = False) -> bool:
        """Get yes/no confirmation from user"""
        try:
            suffix = " [Y/n]" if default else " [y/N]"
            response = await self.prompt(f"{message}{suffix}: ")

            if not response.strip():
                return default

            return response.lower().startswith("y")

        except (KeyboardInterrupt, EOFError):
            return False
