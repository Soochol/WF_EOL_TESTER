"""
Base CLI

Base class for CLI components providing common functionality.
"""

import sys
import json
import yaml
import threading
import time
from typing import Any, Optional
from abc import ABC


class BaseCLI(ABC):
    """Base class for CLI components"""
    
    def __init__(self):
        """Initialize base CLI"""
        self._spinner_active = False
        self._spinner_thread = None
    
    def print_header(self, title: str) -> None:
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}")
    
    def print_section_header(self, title: str) -> None:
        """Print formatted section header"""
        print(f"\n{title}")
        print(f"{'-'*len(title)}")
    
    def print_success(self, message: str) -> None:
        """Print success message in green"""
        print(f"\033[92m✓ {message}\033[0m")
    
    def print_error(self, message: str) -> None:
        """Print error message in red"""
        print(f"\033[91m✗ {message}\033[0m", file=sys.stderr)
    
    def print_warning(self, message: str) -> None:
        """Print warning message in yellow"""
        print(f"\033[93m⚠ {message}\033[0m")
    
    def print_info(self, message: str) -> None:
        """Print info message"""
        print(f"  {message}")
    
    def print_key_value(self, key: str, value: str, color: Optional[str] = None) -> None:
        """Print key-value pair in formatted way"""
        if color == "green":
            print(f"  {key:20}: \033[92m{value}\033[0m")
        elif color == "red":
            print(f"  {key:20}: \033[91m{value}\033[0m")
        elif color == "yellow":
            print(f"  {key:20}: \033[93m{value}\033[0m")
        else:
            print(f"  {key:20}: {value}")
    
    def print_json(self, data: Any) -> None:
        """Print data as formatted JSON"""
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    def print_yaml(self, data: Any) -> None:
        """Print data as formatted YAML"""
        print(yaml.dump(data, default_flow_style=False, allow_unicode=True))
    
    def get_user_input(self, prompt: str, required: bool = False) -> Optional[str]:
        """
        Get user input with prompt
        
        Args:
            prompt: Input prompt message
            required: Whether input is required
            
        Returns:
            User input or None if not provided and not required
        """
        while True:
            try:
                user_input = input(f"{prompt}: ").strip()
                
                if not user_input and required:
                    self.print_warning("This field is required")
                    continue
                
                return user_input if user_input else None
                
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                raise
            except EOFError:
                print("\nEOF received")
                return None
    
    def get_user_confirmation(self, message: str, default: bool = False) -> bool:
        """
        Get user confirmation (y/n)
        
        Args:
            message: Confirmation message
            default: Default value if user just presses enter
            
        Returns:
            True if user confirms, False otherwise
        """
        default_text = "Y/n" if default else "y/N"
        
        while True:
            try:
                response = input(f"{message} ({default_text}): ").strip().lower()
                
                if not response:
                    return default
                
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    self.print_warning("Please enter 'y' or 'n'")
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                return False
            except EOFError:
                print("\nEOF received")
                return False
    
    def show_spinner(self, message: str = "Processing...") -> None:
        """Show spinner animation"""
        if self._spinner_active:
            return
        
        self._spinner_active = True
        
        def spin():
            spinner_chars = "|/-\\"
            i = 0
            while self._spinner_active:
                print(f"\r{message} {spinner_chars[i % len(spinner_chars)]}", end="", flush=True)
                time.sleep(0.1)
                i += 1
            print("\r" + " " * (len(message) + 5) + "\r", end="", flush=True)
        
        self._spinner_thread = threading.Thread(target=spin)
        self._spinner_thread.daemon = True
        self._spinner_thread.start()
    
    def hide_spinner(self) -> None:
        """Hide spinner animation"""
        self._spinner_active = False
        if self._spinner_thread:
            self._spinner_thread.join(timeout=1)
            self._spinner_thread = None
    
    def print_table(self, headers: list, rows: list) -> None:
        """
        Print data in table format
        
        Args:
            headers: Table column headers
            rows: Table rows (list of lists)
        """
        if not rows:
            self.print_info("No data to display")
            return
        
        # Calculate column widths
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(str(header))
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)  # Add padding
        
        # Print header
        header_row = "".join(f"{str(headers[i]):<{col_widths[i]}}" for i in range(len(headers)))
        print(header_row)
        print("-" * len(header_row))
        
        # Print rows
        for row in rows:
            row_str = ""
            for i in range(len(headers)):
                value = str(row[i]) if i < len(row) else ""
                row_str += f"{value:<{col_widths[i]}}"
            print(row_str)
    
    def print_progress_bar(self, current: int, total: int, width: int = 50) -> None:
        """
        Print progress bar
        
        Args:
            current: Current progress value
            total: Total progress value
            width: Width of progress bar in characters
        """
        if total == 0:
            return
        
        percentage = min(100, (current / total) * 100)
        filled_width = int(width * current / total)
        
        bar = "█" * filled_width + "░" * (width - filled_width)
        print(f"\r[{bar}] {percentage:6.1f}% ({current}/{total})", end="", flush=True)
        
        if current >= total:
            print()  # New line when complete
    
    def clear_screen(self) -> None:
        """Clear terminal screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_separator(self, char: str = "-", length: int = 60) -> None:
        """Print separator line"""
        print(char * length)