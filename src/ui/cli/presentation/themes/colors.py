"""
Color Scheme Configuration for CLI

Professional color scheme optimized for readability and accessibility.
This module defines all color constants used throughout the Rich UI system
to ensure consistent visual styling and easy maintenance.
"""

from typing import Dict
from domain.enums.test_status import TestStatus


class ColorScheme:
    """Professional color scheme for CLI interface."""

    # Professional color palette optimized for readability and accessibility
    COLORS: Dict[str, str] = {
        "primary": "#2E86C1",  # Professional blue - main accent color
        "secondary": "#48C9B0",  # Teal - secondary operations and highlights
        "success": "#58D68D",  # Green - successful operations and confirmations
        "warning": "#F7DC6F",  # Yellow - warnings and cautions
        "error": "#EC7063",  # Red - errors and failures
        "info": "#85C1E9",  # Light blue - informational content
        "accent": "#BB8FCE",  # Purple - special emphasis and decorative elements
        "text": "#F8F9FA",  # Light text - primary readable content
        "muted": "#AEB6BF",  # Muted text - secondary information and labels
        "background": "#34495E",  # Dark background - container backgrounds
        "border": "#5D6D7E",  # Border color - panel and table borders
    }

    # Status color mapping for intuitive visual feedback
    STATUS_COLORS: Dict[TestStatus, str] = {
        TestStatus.NOT_STARTED: "muted",  # Inactive/waiting states
        TestStatus.PREPARING: "info",  # Preparation and setup phases
        TestStatus.RUNNING: "primary",  # Active execution states
        TestStatus.COMPLETED: "success",  # Successful completion
        TestStatus.FAILED: "error",  # Test failures
        TestStatus.CANCELLED: "warning",  # User-cancelled operations
        TestStatus.ERROR: "error",  # System errors and exceptions
    }

    @classmethod
    def get_color(cls, name: str) -> str:
        """Get color value by name.

        Args:
            name: Color name from COLORS dictionary

        Returns:
            Hex color value or default color if not found
        """
        return cls.COLORS.get(name, cls.COLORS["text"])

    @classmethod
    def get_status_color(cls, status: TestStatus) -> str:
        """Get color for test status.

        Args:
            status: TestStatus enum value

        Returns:
            Color name from COLORS dictionary
        """
        color_name = cls.STATUS_COLORS.get(status, "info")
        return cls.COLORS[color_name]