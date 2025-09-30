"""New Overview Statistics Page

Dashboard-style overview with Quick Insights, key metrics, and performance summary.
"""

# Standard library imports
from typing import Any, Dict, List, Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

# Local imports
from ..overview_panel import OverviewPanel
from ..quick_insights_panel import QuickInsightsPanel


class NewOverviewPage(QWidget):
    """Enhanced overview page with insights and key metrics.

    Features:
    - Quick Insights panel (auto-detection of issues)
    - Key Metrics cards (Total, Pass Rate, Duration, Force)
    """

    def __init__(
        self,
        statistics_service: Any,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.statistics_service = statistics_service
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup overview page UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Quick Insights Panel (top priority)
        self.insights_panel = QuickInsightsPanel()
        content_layout.addWidget(self.insights_panel)

        # Key Metrics Panel (Overview)
        self.overview_panel = OverviewPanel()
        self.overview_panel.setMinimumHeight(200)
        content_layout.addWidget(self.overview_panel)

        # Add stretch to push content to top
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Apply dark theme
        self.setStyleSheet("background-color: #1e1e1e;")

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Update overview page data based on filters.

        Args:
            filters: Filter criteria from header controls
        """
        try:
            # Get overview statistics
            overview_stats = await self.statistics_service.get_overview_statistics(filters)

            # Update overview panel
            if hasattr(self.overview_panel, "update_statistics"):
                self.overview_panel.update_statistics(overview_stats)

            # Update Quick Insights
            if hasattr(self.insights_panel, "update_insights"):
                self.insights_panel.update_insights(overview_stats)

        except Exception as e:
            print(f"Error updating overview page: {e}")
            import traceback
            traceback.print_exc()

    def clear_data(self) -> None:
        """Clear all displayed data."""
        if hasattr(self.overview_panel, "clear"):
            self.overview_panel.clear()
        if hasattr(self.insights_panel, "clear_insights"):
            self.insights_panel.clear_insights()