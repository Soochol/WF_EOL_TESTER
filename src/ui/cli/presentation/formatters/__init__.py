"""Formatters Package for CLI Rich UI Components

This package provides specialized formatter classes for different aspects of
the Rich UI system, organized by responsibility and functionality. Each formatter
focuses on a specific domain while maintaining consistent styling and behavior.

The formatter classes are designed to work together through composition and
inherit common functionality from the BaseFormatter class.
"""

from .base_formatter import BaseFormatter
from .status_formatter import StatusFormatter
from .table_formatter import TableFormatter
from .progress_formatter import ProgressFormatter
from .layout_formatter import LayoutFormatter

__all__ = [
    "BaseFormatter",
    "StatusFormatter",
    "TableFormatter",
    "ProgressFormatter",
    "LayoutFormatter",
]