"""Performance Analysis Page

Detailed performance metrics and analysis.
"""

# Standard library imports
from typing import Any, Dict

# Local imports
from .base_statistics_page import BaseStatisticsPage
from ..performance_panel import PerformancePanel


class PerformancePage(BaseStatisticsPage):
    """Detailed Performance Analysis page."""

    def create_content(self) -> None:
        """Add detailed performance panel."""
        # Performance panel (full size)
        self.performance_panel = PerformancePanel()
        self.performance_panel.setMinimumHeight(500)  # Large performance display
        self.content_layout.addWidget(self.performance_panel)

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Update performance data."""
        try:
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
            print(f"Error updating performance page: {e}")
            import traceback
            traceback.print_exc()