"""
Input Manager Protocol Definitions

This module defines the protocols and interfaces for the enhanced input system,
providing clean abstractions that work with different backends (prompt_toolkit or basic).
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Dict, List, Optional, Protocol

if TYPE_CHECKING:
    from pathlib import Path
    from rich.console import Console
    from .rich_formatter import RichFormatter


class DocumentProtocol(Protocol):
    """Protocol for document-like objects with text and cursor position"""

    text: str
    cursor_position: int
    text_before_cursor: str
    lines: List[str]


class CompletionProtocol(Protocol):
    """Protocol for completion suggestions"""

    text: str
    start_position: int
    display_meta: str


class ValidationErrorProtocol(Protocol):
    """Protocol for validation errors"""

    message: str
    cursor_position: int


class FormattedTextProtocol(Protocol):
    """Protocol for formatted text objects"""

    data: Any


class HistoryProtocol(Protocol):
    """Protocol for command history objects"""

    pass


class StyleProtocol(Protocol):
    """Protocol for style objects"""

    @staticmethod
    def from_dict(data: Dict[str, str]) -> "StyleProtocol": ...


class KeyBindingsProtocol(Protocol):
    """Protocol for key bindings"""

    def add(self, key: str) -> Callable[[Callable], Callable]: ...


class CompleterProtocol(Protocol):
    """Protocol for auto-completion providers"""

    def get_completions(
        self, document: DocumentProtocol, complete_event: Any
    ) -> List[CompletionProtocol]: ...
    
    async def get_completions_async(
        self, document: DocumentProtocol, complete_event: Any
    ) -> AsyncGenerator: ...


class LexerProtocol(Protocol):
    """Protocol for syntax highlighting lexers"""

    def lex_document(
        self, document: DocumentProtocol
    ) -> Callable[[int], FormattedTextProtocol]: ...


class ValidatorProtocol(Protocol):
    """Protocol for input validators"""

    def validate(self, document: DocumentProtocol) -> None: ...
    
    async def validate_async(self, document: DocumentProtocol) -> None: ...


class AutoSuggestProtocol(Protocol):
    """Protocol for auto-suggestion providers"""

    pass


class InputBackend(ABC):
    """Abstract base class for input backends"""

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available"""

    @abstractmethod
    def create_document(self, text: str, cursor_position: int = 0) -> DocumentProtocol:
        """Create a document object"""

    @abstractmethod
    def create_completion(
        self, text: str, start_position: int = 0, display_meta: str = ""
    ) -> CompletionProtocol:
        """Create a completion object"""

    @abstractmethod
    def create_validation_error(
        self, message: str, cursor_position: int = 0
    ) -> ValidationErrorProtocol:
        """Create a validation error"""

    @abstractmethod
    def create_formatted_text(self, data: Any) -> FormattedTextProtocol:
        """Create formatted text"""

    @abstractmethod
    def create_style(self, style_dict: Dict[str, str]) -> StyleProtocol:
        """Create a style object"""

    @abstractmethod
    def create_file_history(self, filename: str) -> HistoryProtocol:
        """Create a file-based history object"""

    @abstractmethod
    def create_memory_history(self) -> HistoryProtocol:
        """Create an in-memory history object"""

    @abstractmethod
    def create_key_bindings(self) -> KeyBindingsProtocol:
        """Create key bindings object"""

    @abstractmethod
    def create_auto_suggest(self) -> Optional[AutoSuggestProtocol]:
        """Create auto-suggestion provider"""

    @abstractmethod
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
        """Get input from user with all features"""

    @abstractmethod
    async def confirm(self, message: str, default: bool = False) -> bool:
        """Get yes/no confirmation from user"""


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

    # Style dictionary for prompt_toolkit
    STYLE_DICT = {
        "slash-command": "#00aa00 bold",  # Green for slash commands
        "subcommand": "#0088ff bold",  # Blue for subcommands
        "arguments": "#ffaa00",  # Orange for arguments
        "prompt": "#00aa00 bold",  # Green prompt
        "error": "#ff0000 bold",  # Red for errors
        "success": "#00aa00",  # Green for success
        "warning": "#ffaa00",  # Orange for warnings
    }


# Input validation patterns
VALIDATION_PATTERNS = {
    "dut_id": r"^[A-Z0-9_-]{1,20}$",
    "model": r"^[A-Za-z0-9_\-\s\.]{1,50}$",
    "serial": r"^[A-Za-z0-9_\-]{1,30}$",
    "operator": r"^[A-Za-z0-9_\-\s]{1,30}$",
    "slash_command": r"^/\w+(\s+\w+(\s+.*)?)?$",
    "general": r"^.{1,500}$",
}


# Error messages for validation
VALIDATION_ERROR_MESSAGES = {
    "dut_id": "DUT ID must contain only uppercase letters, numbers, underscores, and hyphens",
    "model": "Model must contain only letters, numbers, spaces, dots, underscores, and hyphens",
    "serial": "Serial number must contain only letters, numbers, underscores, and hyphens",
    "operator": "Operator ID must contain only letters, numbers, spaces, underscores, and hyphens",
    "slash_command": "Command must start with / followed by valid command syntax",
    "general": "Invalid input format",
}


# Command completion data
COMMAND_COMPLETIONS = {
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


# Common completion data
COMMON_DUT_IDS = ["WF001", "WF002", "TEST001", "PROTO01", "SAMPLE1"]
COMMON_MODELS = ["WF-2024-A", "WF-2024-B", "WF-2023-X"]
COMMON_OPERATORS = ["Test", "Engineer1", "QA_Team", "Production"]
