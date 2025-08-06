"""Command System Interfaces

Core interfaces for the enhanced command system with dependency injection,
middleware pipeline support, and extensible architecture.

Key Features:
- Interface-based design for loose coupling and testability
- Middleware pipeline for cross-cutting concerns
- Command metadata for registration and discovery
- Execution context for stateful command processing
- Registry pattern for command management
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class CommandStatus(Enum):
    """Command execution status with enhanced states.

    Provides comprehensive status tracking for command execution
    including middleware pipeline states and error conditions.
    """

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PENDING = "pending"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class MiddlewareResult(Enum):
    """Middleware execution result states.

    Controls middleware pipeline flow and command execution continuation.
    """

    CONTINUE = "continue"  # Continue to next middleware or command
    STOP = "stop"  # Stop pipeline, return current result
    SKIP = "skip"  # Skip remaining middleware, execute command
    ERROR = "error"  # Error occurred, stop with error


@dataclass
class CommandResult:
    """Enhanced command execution result with metadata.

    Provides comprehensive result information including execution context,
    performance metrics, and middleware pipeline data.
    """

    status: CommandStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
    middleware_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None

    @classmethod
    def success(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None,
    ) -> "CommandResult":
        """Create success result with optional performance data."""
        return cls(
            status=CommandStatus.SUCCESS,
            message=message,
            data=data,
            execution_time_ms=execution_time_ms,
        )

    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error_details: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None,
    ) -> "CommandResult":
        """Create error result with detailed error information."""
        return cls(
            status=CommandStatus.ERROR,
            message=message,
            data=data,
            error_details=error_details,
            execution_time_ms=execution_time_ms,
        )

    @classmethod
    def warning(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None,
    ) -> "CommandResult":
        """Create warning result."""
        return cls(
            status=CommandStatus.WARNING,
            message=message,
            data=data,
            execution_time_ms=execution_time_ms,
        )

    @classmethod
    def info(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None,
    ) -> "CommandResult":
        """Create info result."""
        return cls(
            status=CommandStatus.INFO,
            message=message,
            data=data,
            execution_time_ms=execution_time_ms,
        )


@dataclass
class CommandMetadata:
    """Metadata for command registration and discovery.

    Contains comprehensive information about a command including
    its capabilities, dependencies, and execution requirements.
    """

    name: str
    description: str
    category: str = "general"
    aliases: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    requires_confirmation: bool = False
    is_async: bool = True
    timeout_seconds: Optional[int] = None
    middleware_config: Optional[Dict[str, Any]] = None
    help_text: Optional[str] = None
    examples: Optional[List[str]] = None
    version: str = "1.0.0"
    author: Optional[str] = None
    deprecated: bool = False
    deprecation_message: Optional[str] = None


class ICommandExecutionContext(ABC):
    """Interface for command execution context.

    Provides stateful information and services during command execution
    including user session, configuration, and runtime data.
    """

    @property
    @abstractmethod
    def user_id(self) -> Optional[str]:
        """Get the current user identifier."""
        ...

    @property
    @abstractmethod
    def session_data(self) -> Dict[str, Any]:
        """Get session-specific data."""
        ...

    @property
    @abstractmethod
    def configuration(self) -> Dict[str, Any]:
        """Get command execution configuration."""
        ...

    @abstractmethod
    def get_service(self, service_type: type) -> Any:
        """Resolve a service from the dependency injection container.

        Args:
            service_type: The interface type to resolve

        Returns:
            Service instance implementing the requested interface
        """
        ...

    @abstractmethod
    def set_data(self, key: str, value: Any) -> None:
        """Set context-specific data."""
        ...

    @abstractmethod
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get context-specific data."""
        ...


class ICommand(ABC):
    """Interface for command implementation with enhanced capabilities.

    Defines the contract for command handlers with dependency injection,
    metadata support, and validation capabilities. Commands should be
    stateless and rely on the execution context for state management.
    """

    @property
    @abstractmethod
    def metadata(self) -> CommandMetadata:
        """Get command metadata.

        Returns:
            CommandMetadata containing command information and configuration
        """
        ...

    @abstractmethod
    async def execute(
        self,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> CommandResult:
        """Execute the command with enhanced context.

        Args:
            args: Command arguments (excluding command name)
            context: Execution context with services and session data

        Returns:
            CommandResult with execution outcome and data
        """
        ...

    @abstractmethod
    def get_subcommands(self) -> Dict[str, str]:
        """Get available subcommands.

        Returns:
            Dictionary mapping subcommand names to descriptions
        """
        ...

    @abstractmethod
    def validate_args(self, args: List[str]) -> tuple[bool, Optional[str]]:
        """Validate command arguments with detailed error reporting.

        Args:
            args: Arguments to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        ...

    def get_help(self) -> str:
        """Get comprehensive help text for this command.

        Returns:
            Formatted help text including metadata, subcommands, and examples
        """
        help_sections = []

        # Basic command info
        help_sections.append(f"/{self.metadata.name} - {self.metadata.description}")

        if self.metadata.category != "general":
            help_sections.append(f"Category: {self.metadata.category}")

        # Aliases
        if self.metadata.aliases:
            aliases_str = ", ".join([f"/{alias}" for alias in self.metadata.aliases])
            help_sections.append(f"Aliases: {aliases_str}")

        # Subcommands
        subcommands = self.get_subcommands()
        if subcommands:
            help_sections.append("\nSubcommands:")
            for subcmd, desc in subcommands.items():
                if subcmd:
                    help_sections.append(f"  /{self.metadata.name} {subcmd} - {desc}")
                else:
                    help_sections.append(f"  /{self.metadata.name} - {desc}")

        # Examples
        if self.metadata.examples:
            help_sections.append("\nExamples:")
            for example in self.metadata.examples:
                help_sections.append(f"  {example}")

        # Additional help text
        if self.metadata.help_text:
            help_sections.append(f"\n{self.metadata.help_text}")

        # Deprecation warning
        if self.metadata.deprecated:
            warning = "\n⚠️  WARNING: This command is deprecated."
            if self.metadata.deprecation_message:
                warning += f" {self.metadata.deprecation_message}"
            help_sections.append(warning)

        return "\n".join(help_sections)


class ICommandMiddleware(ABC):
    """Interface for command execution middleware.

    Middleware components can intercept command execution for cross-cutting
    concerns like authentication, validation, logging, and error handling.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get middleware name for identification."""
        ...

    @property
    @abstractmethod
    def priority(self) -> int:
        """Get middleware priority (lower numbers execute first)."""
        ...

    @abstractmethod
    async def before_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> tuple[MiddlewareResult, Optional[CommandResult]]:
        """Execute before command execution.

        Args:
            command: Command about to be executed
            args: Command arguments
            context: Execution context

        Returns:
            Tuple of (middleware_result, optional_command_result)
            If middleware_result is STOP, optional_command_result will be returned
        """
        ...

    @abstractmethod
    async def after_execute(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
        result: CommandResult,
    ) -> CommandResult:
        """Execute after command execution.

        Args:
            command: Command that was executed
            args: Command arguments
            context: Execution context
            result: Command execution result

        Returns:
            Modified or original command result
        """
        ...

    @abstractmethod
    async def on_error(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
        error: Exception,
    ) -> Optional[CommandResult]:
        """Handle command execution errors.

        Args:
            command: Command that encountered error
            args: Command arguments
            context: Execution context
            error: Exception that occurred

        Returns:
            Optional CommandResult to override error handling
        """
        ...


class ICommandParser(ABC):
    """Interface for command parsing with enhanced capabilities.

    Defines the contract for parsing user input into commands and arguments
    with support for complex command structures and validation.
    """

    @abstractmethod
    def parse_input(self, user_input: str) -> tuple[Optional[str], List[str]]:
        """Parse user input into command name and arguments.

        Args:
            user_input: Raw user input (e.g., "/test quick --verbose")

        Returns:
            Tuple of (command_name, arguments) or (None, []) if invalid
        """
        ...

    @abstractmethod
    async def execute_command(
        self,
        user_input: str,
        context: ICommandExecutionContext,
    ) -> CommandResult:
        """Parse and execute a command with middleware pipeline.

        Args:
            user_input: Raw user input
            context: Execution context

        Returns:
            CommandResult from command execution or middleware
        """
        ...

    @abstractmethod
    def get_command_suggestions(self, partial_input: str) -> List[str]:
        """Get command suggestions for autocomplete.

        Args:
            partial_input: Partial user input

        Returns:
            List of matching command suggestions
        """
        ...

    @abstractmethod
    def get_help_text(self, command_name: Optional[str] = None) -> str:
        """Get help text for commands.

        Args:
            command_name: Specific command to get help for, or None for all

        Returns:
            Formatted help text
        """
        ...


class ICommandRegistry(ABC):
    """Interface for command registration and discovery.

    Defines the contract for managing command lifecycle including
    registration, discovery, and metadata management.
    """

    @abstractmethod
    def register_command(
        self,
        command: ICommand,
        middleware: Optional[List[ICommandMiddleware]] = None,
    ) -> None:
        """Register a command with optional middleware.

        Args:
            command: Command instance to register
            middleware: Optional list of command-specific middleware
        """
        ...

    @abstractmethod
    def unregister_command(self, command_name: str) -> bool:
        """Unregister a command.

        Args:
            command_name: Name of command to unregister

        Returns:
            True if command was unregistered, False if not found
        """
        ...

    @abstractmethod
    def get_command(self, command_name: str) -> Optional[ICommand]:
        """Get a registered command by name.

        Args:
            command_name: Name of command to retrieve

        Returns:
            Command instance or None if not found
        """
        ...

    @abstractmethod
    def get_all_commands(self) -> Dict[str, ICommand]:
        """Get all registered commands.

        Returns:
            Dictionary mapping command names to command instances
        """
        ...

    @abstractmethod
    def get_commands_by_category(self, category: str) -> List[ICommand]:
        """Get commands by category.

        Args:
            category: Category to filter by

        Returns:
            List of commands in the specified category
        """
        ...

    @abstractmethod
    def register_middleware(self, middleware: ICommandMiddleware) -> None:
        """Register global middleware.

        Args:
            middleware: Middleware to register globally
        """
        ...

    @abstractmethod
    def get_middleware_for_command(self, command_name: str) -> List[ICommandMiddleware]:
        """Get middleware chain for a specific command.

        Args:
            command_name: Name of command

        Returns:
            List of middleware ordered by priority
        """
        ...

    @abstractmethod
    def discover_commands(self, module_path: str) -> int:
        """Discover and register commands from a module.

        Args:
            module_path: Python module path to scan for commands

        Returns:
            Number of commands discovered and registered
        """
        ...
