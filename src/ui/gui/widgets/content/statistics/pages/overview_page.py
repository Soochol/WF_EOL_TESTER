"""Overview Statistics Page

Main overview page with general statistics and performance analysis.
"""

# Standard library imports
from typing import Any, Dict

# Local imports
from .base_statistics_page import BaseStatisticsPage
from ..overview_panel import OverviewPanel
from ..performance_panel import PerformancePanel


class OverviewPage(BaseStatisticsPage):
    """Overview page with general statistics and performance metrics."""

    def create_content(self) -> None:
        """Add overview and performance panels."""
        # Overview statistics panel (full size, no collapsible wrapper)
        self.overview_panel = OverviewPanel()
        self.overview_panel.setMinimumHeight(400)  # Larger size for better visibility
        self.content_layout.addWidget(self.overview_panel)

        # Performance analysis panel (full size, no collapsible wrapper)
        self.performance_panel = PerformancePanel()
        self.performance_panel.setMinimumHeight(400)  # Larger size for better visibility
        self.content_layout.addWidget(self.performance_panel)

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Update overview and performance data."""
        try:
            # Update overview statistics
            overview = await self.statistics_service.get_overview_statistics(filters)
            if hasattr(self.overview_panel, "update_statistics"):
                self.overview_panel.update_statistics(overview)

            # Update performance analysis
            all_tests = await self.statistics_service.repository.get_all_tests()
            filtered_tests = self.statistics_service._apply_filters(all_tests, filters)

            all_tests_data = []
            for result in filtered_tests:
                all_tests_data.append(
                    {
                        "serial_number": result.get("dut", {}).get("serial_number", "N/A"),
                        "duration": result.get("duration_seconds", 0.0),
                        "timestamp": result.get("start_time"),
                    }
                )

            fastest = sorted(all_tests_data, key=lambda x: x["duration"])[:5]
            slowest = sorted(all_tests_data, key=lambda x: x["duration"], reverse=True)[:5]

            if hasattr(self.performance_panel, "update_performance"):
                self.performance_panel.update_performance(fastest, slowest)

        except Exception as e:
            print(f"Error updating overview page: {e}")
            import traceback
            traceback.print_exc()