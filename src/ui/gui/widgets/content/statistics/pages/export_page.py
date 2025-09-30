"""Export Data Page

Data export tools and options.
"""

# Standard library imports
from typing import Any, Dict

# Local imports
from .base_statistics_page import BaseStatisticsPage
from ..export_panel import ExportPanel


class ExportPage(BaseStatisticsPage):
    """Data Export Tools page."""

    def create_content(self) -> None:
        """Add export panel (no collapsible section needed)."""
        self.export_panel = ExportPanel()
        self.content_layout.addWidget(self.export_panel)

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Update export options.

        Export panel typically doesn't need data updates,
        but we can pass filter info if needed.
        """
        pass