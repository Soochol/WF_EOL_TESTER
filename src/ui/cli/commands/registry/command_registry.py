"""Enhanced Command Registry Implementation

Provides comprehensive command registration and discovery system with
metadata management, middleware support, and plugin-style loading.
"""

import importlib
import inspect
from typing import Any, Dict, List, Optional, Set, Type
from loguru import logger

from ui.cli.commands.interfaces.command_interface import (
    ICommand,
    ICommandRegistry,
    ICommandMiddleware,
    CommandMetadata,
)


class EnhancedCommandRegistry(ICommandRegistry):
    """Enhanced command registry with comprehensive management capabilities.

    Provides command registration, discovery, middleware management,
    and plugin-style command loading with metadata support.
    """

    def __init__(self):
        """Initialize enhanced command registry."""
        self._commands: Dict[str, ICommand] = {}
        self._aliases: Dict[str, str] = {}
        self._global_middleware: List[ICommandMiddleware] = []
        self._command_middleware: Dict[str, List[ICommandMiddleware]] = {}
        self._categories: Dict[str, Set[str]] = {}
        self._command_metadata: Dict[str, CommandMetadata] = {}

        logger.debug("Initialized enhanced command registry")

    def register_command(
        self,
        command: ICommand,
        middleware: Optional[List[ICommandMiddleware]] = None,
    ) -> None:
        """Register a command with optional middleware.

        Args:
            command: Command instance to register
            middleware: Optional list of command-specific middleware

        Raises:
            ValueError: If command name is already registered
        """
        command_name = command.metadata.name

        # Check for duplicate registration
        if command_name in self._commands:
            existing_command = self._commands[command_name]
            if existing_command is not command:  # Allow re-registration of same instance
                raise ValueError(f"Command '{command_name}' is already registered")

        # Register the command
        self._commands[command_name] = command
        self._command_metadata[command_name] = command.metadata

        # Register aliases
        if command.metadata.aliases:
            for alias in command.metadata.aliases:
                if alias in self._aliases:
                    logger.warning(f"Alias '{alias}' is already registered, overriding")
                self._aliases[alias] = command_name

        # Register category
        category = command.metadata.category
        if category not in self._categories:
            self._categories[category] = set()
        self._categories[category].add(command_name)

        # Register command-specific middleware
        if middleware:
            self._command_middleware[command_name] = sorted(
                middleware, key=lambda m: m.priority
            )

        # Log registration
        logger.info(
            f"Registered command: /{command_name} "
            f"(category: {category}, aliases: {command.metadata.aliases or 'none'}, "
            f"middleware: {len(middleware) if middleware else 0})"
        )

        # Log deprecation warning if applicable
        if command.metadata.deprecated:
            logger.warning(
                f"Registered DEPRECATED command: /{command_name} - "
                f"{command.metadata.deprecation_message or 'No migration info'}"
            )

    def unregister_command(self, command_name: str) -> bool:
        """Unregister a command.

        Args:
            command_name: Name of command to unregister

        Returns:
            True if command was unregistered, False if not found
        """
        if command_name not in self._commands:
            return False

        command = self._commands[command_name]

        # Remove from commands
        del self._commands[command_name]
        del self._command_metadata[command_name]

        # Remove aliases
        if command.metadata.aliases:
            for alias in command.metadata.aliases:
                if alias in self._aliases and self._aliases[alias] == command_name:
                    del self._aliases[alias]

        # Remove from category
        category = command.metadata.category
        if category in self._categories:
            self._categories[category].discard(command_name)
            if not self._categories[category]:  # Remove empty category
                del self._categories[category]

        # Remove command-specific middleware
        if command_name in self._command_middleware:
            del self._command_middleware[command_name]

        logger.info(f"Unregistered command: /{command_name}")
        return True

    def get_command(self, command_name: str) -> Optional[ICommand]:
        """Get a registered command by name.

        Args:
            command_name: Name of command to retrieve

        Returns:
            Command instance or None if not found
        """
        # Check direct name
        if command_name in self._commands:
            return self._commands[command_name]

        # Check aliases
        if command_name in self._aliases:
            real_name = self._aliases[command_name]
            return self._commands.get(real_name)

        return None

    def get_all_commands(self) -> Dict[str, ICommand]:
        """Get all registered commands.

        Returns:
            Dictionary mapping command names to command instances
        """
        return self._commands.copy()

    def get_commands_by_category(self, category: str) -> List[ICommand]:
        """Get commands by category.

        Args:
            category: Category to filter by

        Returns:
            List of commands in the specified category
        """
        if category not in self._categories:
            return []

        command_names = self._categories[category]
        return [self._commands[name] for name in command_names if name in self._commands]

    def get_all_categories(self) -> List[str]:
        """Get all registered command categories.

        Returns:
            List of category names
        """
        return list(self._categories.keys())

    def get_commands_by_author(self, author: str) -> List[ICommand]:
        """Get commands by author.

        Args:
            author: Author to filter by

        Returns:
            List of commands by the specified author
        """
        commands = []
        for command in self._commands.values():
            if command.metadata.author == author:
                commands.append(command)
        return commands

    def get_deprecated_commands(self) -> List[ICommand]:
        """Get all deprecated commands.

        Returns:
            List of deprecated commands
        """
        commands = []
        for command in self._commands.values():
            if command.metadata.deprecated:
                commands.append(command)
        return commands

    def register_middleware(self, middleware: ICommandMiddleware) -> None:
        """Register global middleware.

        Args:
            middleware: Middleware to register globally
        """
        # Check for duplicate middleware names
        for existing in self._global_middleware:
            if existing.name == middleware.name:
                logger.warning(f"Middleware '{middleware.name}' is already registered globally")
                return

        self._global_middleware.append(middleware)
        # Sort by priority
        self._global_middleware.sort(key=lambda m: m.priority)

        logger.info(f"Registered global middleware: {middleware.name} (priority: {middleware.priority})")

    def unregister_middleware(self, middleware_name: str) -> bool:
        """Unregister global middleware.

        Args:
            middleware_name: Name of middleware to unregister

        Returns:
            True if middleware was unregistered, False if not found
        """
        for i, middleware in enumerate(self._global_middleware):
            if middleware.name == middleware_name:
                del self._global_middleware[i]
                logger.info(f"Unregistered global middleware: {middleware_name}")
                return True
        return False

    def get_middleware_for_command(self, command_name: str) -> List[ICommandMiddleware]:
        """Get middleware chain for a specific command.

        Args:
            command_name: Name of command

        Returns:
            List of middleware ordered by priority
        """
        middleware_chain = []

        # Add global middleware
        middleware_chain.extend(self._global_middleware)

        # Add command-specific middleware
        if command_name in self._command_middleware:
            middleware_chain.extend(self._command_middleware[command_name])

        # Sort by priority and return
        return sorted(middleware_chain, key=lambda m: m.priority)

    def get_all_middleware(self) -> Dict[str, List[ICommandMiddleware]]:
        """Get all registered middleware.

        Returns:
            Dictionary with 'global' and command-specific middleware lists
        """
        result = {
            "global": self._global_middleware.copy()
        }

        for command_name, middleware_list in self._command_middleware.items():
            result[command_name] = middleware_list.copy()

        return result

    def discover_commands(self, module_path: str) -> int:
        """Discover and register commands from a module.

        Args:
            module_path: Python module path to scan for commands

        Returns:
            Number of commands discovered and registered

        Raises:
            ImportError: If module cannot be imported
            ValueError: If module contains invalid command classes
        """
        try:
            # Import the module
            module = importlib.import_module(module_path)

            discovered_count = 0

            # Scan module for command classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if class implements ICommand interface
                if (issubclass(obj, ICommand) and obj != ICommand):

                    try:
                        # Try to instantiate the command
                        # This assumes commands have a default constructor or can be created via DI
                        if self._can_instantiate_command(obj):
                            command_instance = obj()
                            self.register_command(command_instance)
                            discovered_count += 1

                    except Exception as e:
                        logger.warning(
                            f"Could not instantiate command class {name} from {module_path}: {e}"
                        )

            logger.info(f"Discovered {discovered_count} commands from module: {module_path}")
            return discovered_count

        except ImportError as e:
            logger.error(f"Could not import module {module_path}: {e}")
            raise ImportError(f"Module discovery failed for {module_path}: {e}")

    def _can_instantiate_command(self, command_class: Type) -> bool:
        """Check if a command class can be instantiated.

        Args:
            command_class: Command class to check

        Returns:
            True if class can be instantiated
        """
        try:
            # Get constructor signature
            signature = inspect.signature(command_class.__init__)

            # Check if all parameters have defaults (except self)
            for param_name, param in signature.parameters.items():
                if param_name == "self":
                    continue

                if param.default == inspect.Parameter.empty:
                    # Required parameter without default
                    return False

            return True

        except Exception:
            return False

    def search_commands(self, query: str) -> List[ICommand]:
        """Search commands by name, description, or category.

        Args:
            query: Search query string

        Returns:
            List of commands matching the query
        """
        query_lower = query.lower()
        matches = []

        for command in self._commands.values():
            metadata = command.metadata

            # Check name match
            if query_lower in metadata.name.lower():
                matches.append(command)
                continue

            # Check description match
            if query_lower in metadata.description.lower():
                matches.append(command)
                continue

            # Check category match
            if query_lower in metadata.category.lower():
                matches.append(command)
                continue

            # Check aliases match
            if metadata.aliases:
                for alias in metadata.aliases:
                    if query_lower in alias.lower():
                        matches.append(command)
                        break

        return matches

    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics.

        Returns:
            Dictionary containing registry statistics
        """
        total_commands = len(self._commands)
        total_aliases = len(self._aliases)
        total_categories = len(self._categories)
        total_global_middleware = len(self._global_middleware)
        total_command_middleware = sum(len(mw) for mw in self._command_middleware.values())
        deprecated_count = len(self.get_deprecated_commands())

        return {
            "total_commands": total_commands,
            "total_aliases": total_aliases,
            "total_categories": total_categories,
            "total_global_middleware": total_global_middleware,
            "total_command_middleware": total_command_middleware,
            "deprecated_commands": deprecated_count,
            "commands_by_category": {cat: len(cmds) for cat, cmds in self._categories.items()},
            "average_middleware_per_command": (
                total_command_middleware / total_commands if total_commands > 0 else 0
            ),
        }

    def validate_registry(self) -> List[str]:
        """Validate registry consistency and return any issues found.

        Returns:
            List of validation issues (empty if no issues)
        """
        issues = []

        # Check for orphaned aliases
        for alias, command_name in self._aliases.items():
            if command_name not in self._commands:
                issues.append(f"Orphaned alias '{alias}' points to non-existent command '{command_name}'")

        # Check for orphaned categories
        for category, command_names in self._categories.items():
            for command_name in command_names:
                if command_name not in self._commands:
                    issues.append(f"Category '{category}' contains non-existent command '{command_name}'")

        # Check for orphaned command middleware
        for command_name in self._command_middleware.keys():
            if command_name not in self._commands:
                issues.append(f"Command-specific middleware exists for non-existent command '{command_name}'")

        # Check metadata consistency
        for command_name, command in self._commands.items():
            stored_metadata = self._command_metadata.get(command_name)
            if stored_metadata != command.metadata:
                issues.append(f"Metadata mismatch for command '{command_name}'")

        return issues

    def clear_registry(self) -> None:
        """Clear all commands and middleware from the registry."""
        self._commands.clear()
        self._aliases.clear()
        self._global_middleware.clear()
        self._command_middleware.clear()
        self._categories.clear()
        self._command_metadata.clear()

        logger.info("Cleared command registry")
