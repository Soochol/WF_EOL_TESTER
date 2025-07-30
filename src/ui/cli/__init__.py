"""
CLI User Interface Module

Contains CLI-related classes and utilities for the EOL Tester application.
Includes Rich UI formatting capabilities for beautiful terminal output.
"""

from .eol_tester_cli import EOLTesterCLI
from .enhanced_eol_tester_cli import EnhancedEOLTesterCLI
from .rich_formatter import RichFormatter
from .rich_utils import (
    RichUIManager,
    create_quick_message,
    create_quick_results_table,
    create_quick_status_display,
)

__all__ = [
    "EOLTesterCLI",
    "EnhancedEOLTesterCLI", 
    "RichFormatter",
    "RichUIManager",
    "create_quick_message",
    "create_quick_results_table",
    "create_quick_status_display",
]