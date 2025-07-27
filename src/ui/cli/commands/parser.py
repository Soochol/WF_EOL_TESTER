"""
Slash Command Parser

Parser for handling slash command input and routing to appropriate command handlers.
"""

import re
from typing import List, Dict, Optional, Tuple
from loguru import logger

from ui.cli.commands.base import Command, CommandResult


class SlashCommandParser:
    """
    Parser for slash commands in Claude Code style
    
    Handles parsing of command input like:
    - /test
    - /config view
    - /hardware status
    """
    
    def __init__(self):
        """Initialize parser with empty command registry"""
        self._commands: Dict[str, Command] = {}
        self._aliases: Dict[str, str] = {}
    
    def register_command(self, command: Command, aliases: Optional[List[str]] = None) -> None:
        """
        Register a command with the parser
        
        Args:
            command: Command instance to register
            aliases: Optional list of command aliases
        """
        self._commands[command.name] = command
        
        if aliases:
            for alias in aliases:
                self._aliases[alias] = command.name
        
        logger.debug(f"Registered command: /{command.name}")
    
    def parse_input(self, user_input: str) -> Tuple[Optional[str], List[str]]:
        """
        Parse user input into command name and arguments
        
        Args:
            user_input: Raw user input (e.g., "/test quick")
            
        Returns:
            Tuple of (command_name, arguments) or (None, []) if invalid
        """
        user_input = user_input.strip()
        
        # Check if input starts with slash
        if not user_input.startswith('/'):
            return None, []
        
        # Remove leading slash and split into parts
        command_text = user_input[1:].strip()
        if not command_text:
            return None, []
        
        parts = command_text.split()
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Resolve aliases
        if command_name in self._aliases:
            command_name = self._aliases[command_name]
        
        return command_name, args
    
    async def execute_command(self, user_input: str) -> CommandResult:
        """
        Parse and execute a command from user input
        
        Args:
            user_input: Raw user input (e.g., "/test quick")
            
        Returns:
            CommandResult from command execution
        """
        command_name, args = self.parse_input(user_input)
        
        if not command_name:
            return CommandResult.error("Invalid command format. Commands must start with '/'")
        
        if command_name not in self._commands:
            return CommandResult.error(f"Unknown command: /{command_name}")
        
        try:
            command = self._commands[command_name]
            result = await command.execute(args)
            logger.debug(f"Command /{command_name} executed with status: {result.status}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing command /{command_name}: {e}")
            return CommandResult.error(f"Command execution failed: {str(e)}")
    
    def get_all_commands(self) -> Dict[str, Command]:
        """
        Get all registered commands
        
        Returns:
            Dictionary mapping command names to Command instances
        """
        return self._commands.copy()
    
    def get_command_suggestions(self, partial_input: str) -> List[str]:
        """
        Get command suggestions for autocomplete
        
        Args:
            partial_input: Partial user input (e.g., "/te", "/config v")
            
        Returns:
            List of matching command suggestions
        """
        if not partial_input.startswith('/'):
            return []
        
        # Remove leading slash
        partial = partial_input[1:].lower()
        
        if not partial:
            # Return all available commands
            return [f"/{cmd}" for cmd in sorted(self._commands.keys())]
        
        suggestions = []
        
        # Check for direct command matches
        for cmd_name in self._commands.keys():
            if cmd_name.startswith(partial):
                suggestions.append(f"/{cmd_name}")
        
        # Check for subcommand matches
        parts = partial.split()
        if len(parts) >= 2:
            base_cmd = parts[0]
            partial_subcmd = parts[1]
            
            if base_cmd in self._commands:
                command = self._commands[base_cmd]
                subcommands = command.get_subcommands()
                
                for subcmd in subcommands.keys():
                    if subcmd.startswith(partial_subcmd):
                        suggestions.append(f"/{base_cmd} {subcmd}")
        elif len(parts) == 1:
            # Partial command name - also check subcommands
            base_cmd = parts[0]
            if base_cmd in self._commands:
                command = self._commands[base_cmd]
                subcommands = command.get_subcommands()
                
                for subcmd in subcommands.keys():
                    suggestions.append(f"/{base_cmd} {subcmd}")
        
        # Check aliases
        for alias, real_cmd in self._aliases.items():
            if alias.startswith(partial):
                suggestions.append(f"/{alias}")
        
        return sorted(list(set(suggestions)))
    
    def get_help_text(self, command_name: Optional[str] = None) -> str:
        """
        Get help text for a specific command or all commands
        
        Args:
            command_name: Specific command to get help for, or None for all
            
        Returns:
            Formatted help text
        """
        if command_name:
            if command_name in self._commands:
                return self._commands[command_name].get_help()
            else:
                return f"Unknown command: /{command_name}"
        
        # Return help for all commands
        help_text = "Available Commands:\n\n"
        
        for cmd_name in sorted(self._commands.keys()):
            command = self._commands[cmd_name]
            help_text += f"/{cmd_name} - {command.description}\n"
        
        help_text += "\nType '/{command_name}' for command-specific help"
        return help_text