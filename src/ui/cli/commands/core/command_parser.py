"""Enhanced Command Parser Implementation

Advanced command parser with middleware pipeline support, enhanced parsing
capabilities, and comprehensive error handling.
"""

import time
from typing import Dict, List, Optional, Tuple
from loguru import logger

from ui.cli.commands.interfaces.command_interface import (
    ICommand,
    ICommandParser,
    ICommandExecutionContext,
    ICommandMiddleware,
    CommandResult,
    MiddlewareResult,
)


class EnhancedCommandParser(ICommandParser):
    """Enhanced command parser with middleware pipeline support.

    Provides advanced parsing capabilities with middleware integration,
    comprehensive error handling, and performance monitoring.
    """

    def __init__(self):
        """Initialize enhanced command parser."""
        self._commands: Dict[str, ICommand] = {}
        self._aliases: Dict[str, str] = {}
        self._global_middleware: List[ICommandMiddleware] = []
        self._command_middleware: Dict[str, List[ICommandMiddleware]] = {}

        logger.debug("Initialized enhanced command parser")

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
        command_name = command.metadata.name
        self._commands[command_name] = command

        # Register aliases
        if command.metadata.aliases:
            for alias in command.metadata.aliases:
                self._aliases[alias] = command_name

        # Register command-specific middleware
        if middleware:
            self._command_middleware[command_name] = middleware

        logger.debug(
            f"Registered command: /{command_name} "
            f"(aliases: {command.metadata.aliases or 'none'}, "
            f"middleware: {len(middleware) if middleware else 0})"
        )

    def register_global_middleware(self, middleware: ICommandMiddleware) -> None:
        """Register global middleware that applies to all commands.

        Args:
            middleware: Middleware to register globally
        """
        self._global_middleware.append(middleware)
        # Sort by priority
        self._global_middleware.sort(key=lambda m: m.priority)

        logger.debug(f"Registered global middleware: {middleware.name} (priority: {middleware.priority})")

    def parse_input(self, user_input: str) -> Tuple[Optional[str], List[str]]:
        """Parse user input into command name and arguments.

        Enhanced parsing with support for quoted arguments and escape sequences.

        Args:
            user_input: Raw user input (e.g., "/test quick --verbose")

        Returns:
            Tuple of (command_name, arguments) or (None, []) if invalid
        """
        user_input = user_input.strip()

        # Check if input starts with slash
        if not user_input.startswith("/"):
            return None, []

        # Remove leading slash
        command_text = user_input[1:].strip()
        if not command_text:
            return None, []

        # Enhanced parsing with quote support
        args = self._parse_arguments(command_text)
        if not args:
            return None, []

        command_name = args[0].lower()
        command_args = args[1:] if len(args) > 1 else []

        # Resolve aliases
        if command_name in self._aliases:
            command_name = self._aliases[command_name]

        return command_name, command_args

    def _parse_arguments(self, command_text: str) -> List[str]:
        """Parse command text into arguments with quote support.

        Supports:
        - Single and double quotes
        - Escape sequences
        - Nested quotes

        Args:
            command_text: Command text to parse

        Returns:
            List of parsed arguments
        """
        args = []
        current_arg = ""
        in_quotes = False
        quote_char = None
        i = 0

        while i < len(command_text):
            char = command_text[i]

            if char in ['"', "'"] and not in_quotes:
                # Start of quoted string
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                # End of quoted string
                in_quotes = False
                quote_char = None
            elif char == '\\' and i + 1 < len(command_text):
                # Escape sequence
                next_char = command_text[i + 1]
                if next_char in ['"', "'", '\\', ' ']:
                    current_arg += next_char
                    i += 1  # Skip next character
                else:
                    current_arg += char
            elif char.isspace() and not in_quotes:
                # Argument separator
                if current_arg:
                    args.append(current_arg)
                    current_arg = ""
            else:
                # Regular character
                current_arg += char

            i += 1

        # Add final argument
        if current_arg:
            args.append(current_arg)

        return args

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
        start_time = time.perf_counter()

        # Parse input
        command_name, args = self.parse_input(user_input)

        if not command_name:
            return CommandResult.error(
                "Invalid command format. Commands must start with '/' followed by a command name."
            )

        if command_name not in self._commands:
            # Suggest similar commands
            suggestions = self._get_command_suggestions_for_name(command_name)
            error_msg = f"Unknown command: /{command_name}"
            if suggestions:
                error_msg += f"\nDid you mean: {', '.join(suggestions)}"
            return CommandResult.error(error_msg)

        command = self._commands[command_name]

        # Check if command is deprecated
        if command.metadata.deprecated:
            logger.warning(f"Using deprecated command: /{command_name}")

        try:
            # Build middleware chain
            middleware_chain = self._build_middleware_chain(command_name)

            # Execute middleware pipeline
            result = await self._execute_with_middleware(
                command, args, context, middleware_chain
            )

            # Add timing information
            if result.execution_time_ms is None:
                execution_time = (time.perf_counter() - start_time) * 1000
                result.execution_time_ms = execution_time

            return result

        except Exception as e:
            logger.error(f"Error executing command /{command_name}: {e}")
            execution_time = (time.perf_counter() - start_time) * 1000

            return CommandResult.error(
                f"Command execution failed: {str(e)}",
                execution_time_ms=execution_time,
                error_details={
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "command_name": command_name,
                    "args": args,
                },
            )

    def _build_middleware_chain(self, command_name: str) -> List[ICommandMiddleware]:
        """Build middleware chain for a command.

        Args:
            command_name: Name of command to build chain for

        Returns:
            List of middleware ordered by priority
        """
        middleware_chain = []

        # Add global middleware
        middleware_chain.extend(self._global_middleware)

        # Add command-specific middleware
        if command_name in self._command_middleware:
            middleware_chain.extend(self._command_middleware[command_name])

        # Sort by priority
        middleware_chain.sort(key=lambda m: m.priority)

        return middleware_chain

    async def _execute_with_middleware(
        self,
        command: ICommand,
        args: List[str],
        context: ICommandExecutionContext,
        middleware_chain: List[ICommandMiddleware],
    ) -> CommandResult:
        """Execute command with middleware pipeline.

        Args:
            command: Command to execute
            args: Command arguments
            context: Execution context
            middleware_chain: Middleware to execute

        Returns:
            CommandResult from command or middleware
        """
        # Execute before_execute middleware
        for middleware in middleware_chain:
            try:
                middleware_result, command_result = await middleware.before_execute(
                    command, args, context
                )

                if middleware_result == MiddlewareResult.STOP:
                    # Middleware stopped execution
                    return command_result or CommandResult.error(
                        f"Execution stopped by middleware: {middleware.name}"
                    )
                elif middleware_result == MiddlewareResult.SKIP:
                    # Skip remaining middleware, execute command
                    break
                elif middleware_result == MiddlewareResult.ERROR:
                    # Middleware error
                    return command_result or CommandResult.error(
                        f"Middleware error: {middleware.name}"
                    )
                # MiddlewareResult.CONTINUE - continue to next middleware

            except Exception as e:
                logger.error(f"Error in middleware {middleware.name}: {e}")
                # Try error handling
                try:
                    error_result = await middleware.on_error(command, args, context, e)
                    if error_result:
                        return error_result
                except Exception as inner_e:
                    logger.error(f"Error in middleware error handler {middleware.name}: {inner_e}")

                return CommandResult.error(
                    f"Middleware execution failed: {middleware.name}",
                    error_details={
                        "middleware_name": middleware.name,
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                    },
                )

        # Execute command
        try:
            result = await command.execute(args, context)
        except Exception as e:
            logger.error(f"Error executing command {command.metadata.name}: {e}")

            # Try middleware error handlers
            for middleware in reversed(middleware_chain):
                try:
                    error_result = await middleware.on_error(command, args, context, e)
                    if error_result:
                        return error_result
                except Exception as inner_e:
                    logger.error(f"Error in middleware error handler {middleware.name}: {inner_e}")

            # Default error handling
            result = CommandResult.error(
                f"Command execution failed: {str(e)}",
                error_details={
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                },
            )

        # Execute after_execute middleware (in reverse order)
        for middleware in reversed(middleware_chain):
            try:
                result = await middleware.after_execute(command, args, context, result)
            except Exception as e:
                logger.error(f"Error in after_execute middleware {middleware.name}: {e}")
                # Don't fail the entire command for after_execute errors

        return result

    def get_command_suggestions(self, partial_input: str) -> List[str]:
        """Get command suggestions for autocomplete.

        Args:
            partial_input: Partial user input

        Returns:
            List of matching command suggestions
        """
        if not partial_input.startswith("/"):
            return []

        partial = partial_input[1:].lower()

        if not partial:
            # Return all available commands
            return [f"/{cmd}" for cmd in sorted(self._commands.keys())]

        suggestions = []

        # Check for direct command matches
        for cmd_name in self._commands.keys():
            if cmd_name.startswith(partial):
                suggestions.append(f"/{cmd_name}")

        # Check for alias matches
        for alias in self._aliases.keys():
            if alias.startswith(partial):
                suggestions.append(f"/{alias}")

        # Check for subcommand matches
        parts = partial.split()
        if len(parts) >= 2:
            base_cmd = parts[0]
            partial_subcmd = parts[1]

            if base_cmd in self._commands:
                command = self._commands[base_cmd]
                subcommands = command.get_subcommands()

                for subcmd in subcommands.keys():
                    if subcmd and subcmd.startswith(partial_subcmd):
                        suggestions.append(f"/{base_cmd} {subcmd}")
        elif len(parts) == 1:
            # Add subcommands for matching base command
            base_cmd = parts[0]
            if base_cmd in self._commands:
                command = self._commands[base_cmd]
                subcommands = command.get_subcommands()

                for subcmd in subcommands.keys():
                    if subcmd:  # Skip empty subcommand
                        suggestions.append(f"/{base_cmd} {subcmd}")

        return sorted(list(set(suggestions)))

    def _get_command_suggestions_for_name(self, command_name: str) -> List[str]:
        """Get command suggestions for a given command name.

        Args:
            command_name: Command name to find suggestions for

        Returns:
            List of similar command names
        """
        suggestions = []

        # Simple substring matching
        for cmd_name in self._commands.keys():
            if command_name in cmd_name or cmd_name in command_name:
                suggestions.append(f"/{cmd_name}")

        # Check aliases
        for alias, real_name in self._aliases.items():
            if command_name in alias or alias in command_name:
                suggestions.append(f"/{alias}")

        return suggestions[:5]  # Limit to 5 suggestions

    def get_help_text(self, command_name: Optional[str] = None) -> str:
        """Get help text for commands.

        Args:
            command_name: Specific command to get help for, or None for all

        Returns:
            Formatted help text
        """
        if command_name:
            # Resolve alias
            if command_name in self._aliases:
                command_name = self._aliases[command_name]

            if command_name in self._commands:
                command = self._commands[command_name]
                return command.get_help()
            else:
                return f"Unknown command: /{command_name}"

        # Return help for all commands
        help_sections = ["Available Commands:"]

        # Group commands by category
        categories: Dict[str, List[ICommand]] = {}
        for command in self._commands.values():
            category = command.metadata.category
            if category not in categories:
                categories[category] = []
            categories[category].append(command)

        # Sort categories and commands
        for category in sorted(categories.keys()):
            if category != "general":
                help_sections.append(f"\n{category.title()} Commands:")
            else:
                help_sections.append("\nGeneral Commands:")

            commands = sorted(categories[category], key=lambda c: c.metadata.name)
            for command in commands:
                help_line = f"  /{command.metadata.name} - {command.metadata.description}"
                if command.metadata.deprecated:
                    help_line += " [DEPRECATED]"
                help_sections.append(help_line)

        help_sections.append("\nType '/{command_name}' or '/{command_name} help' for command-specific help")

        return "\n".join(help_sections)

    def get_all_commands(self) -> Dict[str, ICommand]:
        """Get all registered commands.

        Returns:
            Dictionary mapping command names to command instances
        """
        return self._commands.copy()

    def get_command_count(self) -> int:
        """Get the number of registered commands.

        Returns:
            Number of registered commands
        """
        return len(self._commands)

    def get_middleware_count(self) -> int:
        """Get the total number of registered middleware.

        Returns:
            Number of registered middleware (global + command-specific)
        """
        total = len(self._global_middleware)
        for middleware_list in self._command_middleware.values():
            total += len(middleware_list)
        return total
