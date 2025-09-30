"""Base Statistics Sub-Page

Base class for all statistics sub-pages with shared header and scrollable content.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget


class BaseStatisticsPage(QWidget):
    """Base class for all statistics sub-pages.

    Features:
    - Shared header controls (filters, actions)
    - Scrollable content area
    - Common styling
    - Abstract methods for subclass customization
    """

    def __init__(
        self,
        header_controls: QWidget,
        statistics_service: Any,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize base statistics page.

        Args:
            header_controls: Shared StatisticsHeaderControls instance
            statistics_service: EOLStatisticsService instance
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.header_controls = header_controls
        self.statistics_service = statistics_service

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup page UI with shared header and scrollable content."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Add shared header
        main_layout.addWidget(self.header_controls)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(12)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # Subclass will add content here via create_content()
        self.create_content()

        # Add stretch to push content to top
        self.content_layout.addStretch()

        scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(scroll_area)

        # Apply styling
        self.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
            }
        """
        )

    def create_content(self) -> None:
        """Override this method to add page-specific content.

        Subclasses should add widgets to self.content_layout.
        """
        pass

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Override this method to update page data.

        Args:
            filters: Filter criteria from header controls
        """
        pass