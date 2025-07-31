"""
Prompt Toolkit Input Backend

Advanced implementation using prompt_toolkit for enhanced input features.
Provides auto-completion, syntax highlighting, validation, and history.
"""

import asyncio
from typing import Any, Dict, Optional, cast

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


# Check if prompt_toolkit is available
def _check_prompt_toolkit_available() -> bool:
    """Check if prompt_toolkit can be imported"""
    try:
        import prompt_toolkit  # noqa: F401

        return True
    except ImportError:
        return False


PROMPT_TOOLKIT_AVAILABLE = _check_prompt_toolkit_available()


class PromptToolkitInputBackend(InputBackend):
    """Advanced input backend using prompt_toolkit"""

    @property
    def is_available(self) -> bool:
        """Check if prompt_toolkit is available"""
        return PROMPT_TOOLKIT_AVAILABLE

    def create_document(self, text: str, cursor_position: int = 0) -> DocumentProtocol:
        """Create a prompt_toolkit document object"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")
        from prompt_toolkit.document import Document

        return cast(DocumentProtocol, Document(text, cursor_position))

    def create_completion(
        self, text: str, start_position: int = 0, display_meta: str = ""
    ) -> CompletionProtocol:
        """Create a prompt_toolkit completion object"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")
        from prompt_toolkit.completion import Completion

        return cast(CompletionProtocol, Completion(text, start_position, display_meta=display_meta))

    def create_validation_error(
        self, message: str, cursor_position: int = 0
    ) -> ValidationErrorProtocol:
        """Create a prompt_toolkit validation error"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")
        from prompt_toolkit.validation import ValidationError

        return ValidationError(message=message, cursor_position=cursor_position)

    def create_formatted_text(self, data: Any) -> FormattedTextProtocol:
        """Create prompt_toolkit formatted text"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")
        from prompt_toolkit.formatted_text import FormattedText

        return cast(FormattedTextProtocol, FormattedText(data))

    def create_style(self, style_dict: Dict[str, str]) -> StyleProtocol:
        """Create a prompt_toolkit style object"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")
        from prompt_toolkit.styles import Style

        return cast(StyleProtocol, Style.from_dict(style_dict))

    def create_file_history(self, filename: str) -> HistoryProtocol:
        """Create a prompt_toolkit file-based history object"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")
        from prompt_toolkit.history import FileHistory

        return FileHistory(filename)

    def create_memory_history(self) -> HistoryProtocol:
        """Create a prompt_toolkit in-memory history object"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")
        from prompt_toolkit.history import InMemoryHistory

        return InMemoryHistory()

    def create_key_bindings(self) -> KeyBindingsProtocol:
        """Create prompt_toolkit key bindings object"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")
        from prompt_toolkit.key_binding import KeyBindings

        return cast(KeyBindingsProtocol, KeyBindings())

    def create_auto_suggest(self) -> Optional[AutoSuggestProtocol]:
        """Create prompt_toolkit auto-suggestion provider"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            return None
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

        return AutoSuggestFromHistory()

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
        """Get input from user using prompt_toolkit"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")

        try:
            # Prepare arguments for prompt_toolkit
            prompt_kwargs = {
                "message": message,
                "multiline": multiline,
                "wrap_lines": True,
                "mouse_support": True,
                "complete_style": "multi-column",
                "validate_while_typing": True,
            }

            # Add optional parameters if provided
            if history is not None:
                prompt_kwargs["history"] = history
            if completer is not None:
                prompt_kwargs["completer"] = completer
            if validator is not None:
                prompt_kwargs["validator"] = validator
            if lexer is not None:
                prompt_kwargs["lexer"] = lexer
            if style is not None:
                prompt_kwargs["style"] = style
            if auto_suggest is not None:
                prompt_kwargs["auto_suggest"] = auto_suggest
            if key_bindings is not None:
                prompt_kwargs["key_bindings"] = key_bindings
            if placeholder:
                prompt_kwargs["placeholder"] = placeholder

            # Add any additional kwargs
            prompt_kwargs.update(kwargs)

            # Get input using prompt_toolkit
            from prompt_toolkit import prompt

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: prompt(**prompt_kwargs))  # type: ignore

            return result or ""

        except (KeyboardInterrupt, EOFError):
            return ""

    async def confirm(self, message: str, default: bool = False) -> bool:
        """Get yes/no confirmation from user using prompt_toolkit"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("prompt_toolkit not available")

        try:
            from prompt_toolkit.shortcuts import confirm

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: confirm(message))
            return result if result is not None else default

        except (KeyboardInterrupt, EOFError):
            return False
