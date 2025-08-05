"""
CLI User Interface Module

Contains CLI-related classes and utilities for the EOL Tester application.
Includes Rich UI formatting capabilities for beautiful terminal output.
"""

from .enhanced_eol_tester_cli import EnhancedEOLTesterCLI
from .rich_formatter import RichFormatter

__all__ = [
    "EnhancedEOLTesterCLI", 
    "RichFormatter",
]
