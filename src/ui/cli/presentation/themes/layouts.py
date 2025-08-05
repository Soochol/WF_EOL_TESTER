"""
Layout Configuration for CLI

UI formatting constants that define standard dimensions, timing, and layout
parameters used throughout the Rich UI system to maintain visual consistency
and improve code maintainability.
"""

from typing import Tuple


class LayoutConstants:
    """UI layout constants for consistent formatting."""

    # Text truncation lengths for consistent display widths
    DEFAULT_TRUNCATE_LENGTH = 10  # Standard truncation for short fields
    EXTENDED_TRUNCATE_LENGTH = 15  # Extended truncation for medium fields
    MAX_TEXT_DISPLAY_LENGTH = 50  # Maximum before forced truncation

    # Table column widths for optimal readability
    STATUS_COLUMN_WIDTH = 10  # Status indicator column
    TEST_ID_COLUMN_WIDTH = 12  # Test identifier column
    DUT_ID_COLUMN_WIDTH = 15  # Device under test ID column
    MODEL_COLUMN_WIDTH = 12  # Model number column
    DURATION_COLUMN_WIDTH = 10  # Test duration column
    MEASUREMENTS_COLUMN_WIDTH = 12  # Measurement count column
    TIMESTAMP_COLUMN_WIDTH = 16  # Timestamp display column

    # Panel padding for consistent spacing
    DEFAULT_PANEL_PADDING: Tuple[int, int] = (1, 2)  # Standard panel padding (vertical, horizontal)
    HEADER_PANEL_PADDING: Tuple[int, int] = (1, 2)  # Header panel padding

    # Grid layout constraints for organized display
    MAX_GRID_COMPONENTS = 4  # Maximum components in grid layout
    GRID_TOP_COMPONENTS = 2  # Components in top row of grid

    # Animation and timing for smooth user experience
    DEFAULT_REFRESH_RATE = 4  # Updates per second for live displays
    PROGRESS_UPDATE_DELAY = 0.1  # Seconds between progress updates

    @classmethod
    def get_column_width(cls, column_type: str) -> int:
        """Get column width by type.

        Args:
            column_type: Type of column (status, test_id, dut_id, etc.)

        Returns:
            Column width in characters
        """
        width_map = {
            "status": cls.STATUS_COLUMN_WIDTH,
            "test_id": cls.TEST_ID_COLUMN_WIDTH,
            "dut_id": cls.DUT_ID_COLUMN_WIDTH,
            "model": cls.MODEL_COLUMN_WIDTH,
            "duration": cls.DURATION_COLUMN_WIDTH,
            "measurements": cls.MEASUREMENTS_COLUMN_WIDTH,
            "timestamp": cls.TIMESTAMP_COLUMN_WIDTH,
        }
        return width_map.get(column_type, 10)  # Default width

    @classmethod
    def get_truncate_length(cls, field_type: str = "default") -> int:
        """Get truncation length by field type.

        Args:
            field_type: Type of field (default, extended, max)

        Returns:
            Truncation length in characters
        """
        length_map = {
            "default": cls.DEFAULT_TRUNCATE_LENGTH,
            "extended": cls.EXTENDED_TRUNCATE_LENGTH,
            "max": cls.MAX_TEXT_DISPLAY_LENGTH,
        }
        return length_map.get(field_type, cls.DEFAULT_TRUNCATE_LENGTH)