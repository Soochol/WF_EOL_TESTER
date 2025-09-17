"""
Icon Configuration for CLI

Unicode icons for enhanced visual communication throughout the CLI interface.
This module defines all icon constants used in the Rich UI system to provide
consistent visual indicators and improve user experience.
"""

# Standard library imports
from typing import Dict

# Local application imports
from domain.enums.test_status import TestStatus


class IconSet:
    """Unicode icon set for CLI interface."""

    # Unicode icons for enhanced visual communication
    ICONS: Dict[str, str] = {
        "success": "✅",  # Successful operations and confirmations
        "error": "❌",  # Errors and failures
        "warning": "⚠️",  # Warnings and cautions
        "info": "ℹ️",  # Informational content
        "running": "🔄",  # Active processes and operations
        "hardware": "🔧",  # Hardware-related displays
        "test": "🧪",  # Test operations and results
        "report": "📊",  # Reports and statistics
        "settings": "⚙️",  # Configuration and settings
        "clock": "⏱️",  # Time-related information
        "check": "✓",  # Simple check marks
        "cross": "✗",  # Simple failure indicators
        "arrow_right": "➤",  # Navigation and flow indicators
        "bullet": "•",  # List items and bullet points
    }

    # Status-specific icons for TestStatus enum
    STATUS_ICONS: Dict[TestStatus, str] = {
        TestStatus.NOT_STARTED: "⏸️",  # Not started/paused
        TestStatus.PREPARING: "⚙️",  # Preparing/setup
        TestStatus.RUNNING: "🔄",  # Running/active
        TestStatus.COMPLETED: "✅",  # Completed successfully
        TestStatus.FAILED: "❌",  # Failed
        TestStatus.CANCELLED: "⚠️",  # Cancelled
        TestStatus.ERROR: "❌",  # Error
    }

    @classmethod
    def get_icon(cls, name: str) -> str:
        """Get icon by name.

        Args:
            name: Icon name from ICONS dictionary

        Returns:
            Unicode icon or default bullet if not found
        """
        return cls.ICONS.get(name, cls.ICONS["bullet"])

    @classmethod
    def get_status_icon(cls, status: TestStatus) -> str:
        """Get icon for test status.

        Args:
            status: TestStatus enum value

        Returns:
            Unicode icon for the status
        """
        return cls.STATUS_ICONS.get(status, cls.ICONS["info"])
