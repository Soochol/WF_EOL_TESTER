"""4D Analysis Page

4D analysis with time dimension and test comparison.
"""

# Standard library imports
from typing import Any, Dict

# Local imports
from .base_statistics_page import BaseStatisticsPage
from ..force_4d_scatter import Force4DScatter
from ..comparison_panel import ComparisonPanel


class Analysis4DPage(BaseStatisticsPage):
    """4D Analysis with Time Dimension page."""

    def create_content(self) -> None:
        """Add 4D scatter and comparison panels."""
        # 4D Scatter Plot (full size)
        self.scatter_4d = Force4DScatter()
        self.scatter_4d.setMinimumHeight(600)  # Large 4D plot
        self.content_layout.addWidget(self.scatter_4d)

        # Test Comparison (full size)
        self.comparison = ComparisonPanel()
        self.comparison.setMinimumHeight(500)  # Large comparison table
        self.content_layout.addWidget(self.comparison)

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Update 4D analysis and comparison data."""
        try:
            # Update 4D scatter plot
            scatter_data = await self.statistics_service.get_4d_scatter_data(filters)
            if hasattr(self.scatter_4d, "update_scatter"):
                self.scatter_4d.update_scatter(scatter_data)

            # Update test comparison
            all_tests = await self.statistics_service.repository.get_all_tests()
            filtered_tests = self.statistics_service._apply_filters(all_tests, filters)

            tests = []
            for result in filtered_tests:
                forces = self.statistics_service._extract_all_forces(result)
                avg_force = sum(forces) / len(forces) if forces else 0.0
                max_force = max(forces) if forces else 0.0
                min_force = min(forces) if forces else 0.0

                tests.append(
                    {
                        "serial_number": result.get("dut", {}).get("serial_number", "N/A"),
                        "timestamp": result.get("start_time"),
                        "duration": result.get("duration_seconds", 0.0),
                        "status": result.get("test_result", {}).get("test_status", "unknown"),
                        "avg_force": avg_force,
                        "max_force": max_force,
                        "min_force": min_force,
                    }
                )

            if hasattr(self.comparison, "set_available_tests"):
                self.comparison.set_available_tests(tests)

        except Exception as e:
            print(f"Error updating 4D analysis page: {e}")
            import traceback
            traceback.print_exc()