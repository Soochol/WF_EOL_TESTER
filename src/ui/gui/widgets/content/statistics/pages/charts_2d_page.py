"""2D Charts Page

2D visualizations and analysis including trends, heatmaps, temperature, and position statistics.
"""

# Standard library imports
from typing import Any, Dict

# Local imports
from .base_statistics_page import BaseStatisticsPage
from ..force_trend_chart import ForceTrendChart
from ..force_heatmap_2d import ForceHeatmap2D
from ..temperature_force_panel import TemperatureForcePanel
from ..position_force_panel import PositionForcePanel


class Charts2DPage(BaseStatisticsPage):
    """2D Charts and Analysis page."""

    def create_content(self) -> None:
        """Add 4 2D visualization panels."""
        # Force Trend Chart (full size)
        self.trend_chart = ForceTrendChart()
        self.trend_chart.setMinimumHeight(500)  # Large chart for better visibility
        self.content_layout.addWidget(self.trend_chart)

        # Force Heatmap (full size)
        self.heatmap = ForceHeatmap2D()
        self.heatmap.setMinimumHeight(500)  # Large heatmap
        self.content_layout.addWidget(self.heatmap)

        # Temperature Analysis (full size)
        self.temp_panel = TemperatureForcePanel()
        self.temp_panel.setMinimumHeight(400)
        self.content_layout.addWidget(self.temp_panel)

        # Position Analysis (full size)
        self.pos_panel = PositionForcePanel()
        self.pos_panel.setMinimumHeight(400)
        self.content_layout.addWidget(self.pos_panel)

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Update all 2D charts."""
        try:
            # Update trend chart
            all_tests = await self.statistics_service.repository.get_all_tests()
            filtered_tests = self.statistics_service._apply_filters(all_tests, filters)

            trend_data = []
            for result in filtered_tests:
                measurements = result.get("test_result", {}).get("actual_results", {}).get(
                    "measurements", {}
                )
                timestamp = result.get("start_time")

                for temp_str, positions in measurements.items():
                    for position_str, data in positions.items():
                        trend_data.append(
                            {
                                "timestamp": timestamp,
                                "temperature": float(temp_str),
                                "position_mm": float(position_str) / 1000.0,
                                "force": data.get("force", 0.0),
                            }
                        )

            if hasattr(self.trend_chart, "update_chart"):
                self.trend_chart.update_chart(trend_data)

            # Update heatmap
            heatmap_data = await self.statistics_service.get_force_heatmap_data(filters)
            if hasattr(self.heatmap, "update_heatmap"):
                self.heatmap.update_heatmap(heatmap_data)

            # Update temperature statistics
            temp_stats = await self.statistics_service.get_force_statistics_by_temperature(
                filters
            )
            aggregated_temp = {}
            for temp, positions in temp_stats.items():
                all_avgs = [stats["avg"] for stats in positions.values()]
                all_stds = [stats["std"] for stats in positions.values()]
                all_mins = [stats["min"] for stats in positions.values()]
                all_maxs = [stats["max"] for stats in positions.values()]

                aggregated_temp[temp] = {
                    "mean": sum(all_avgs) / len(all_avgs) if all_avgs else 0.0,
                    "std": sum(all_stds) / len(all_stds) if all_stds else 0.0,
                    "min": min(all_mins) if all_mins else 0.0,
                    "max": max(all_maxs) if all_maxs else 0.0,
                }

            if hasattr(self.temp_panel, "update_statistics"):
                self.temp_panel.update_statistics(aggregated_temp)

            # Update position statistics
            pos_stats = await self.statistics_service.get_force_statistics_by_position(filters)
            aggregated_pos = {}
            for position, temps in pos_stats.items():
                all_avgs = [stats["avg"] for stats in temps.values()]
                all_stds = [stats["std"] for stats in temps.values()]
                all_mins = [stats["min"] for stats in temps.values()]
                all_maxs = [stats["max"] for stats in temps.values()]

                aggregated_pos[position] = {
                    "mean": sum(all_avgs) / len(all_avgs) if all_avgs else 0.0,
                    "std": sum(all_stds) / len(all_stds) if all_stds else 0.0,
                    "min": min(all_mins) if all_mins else 0.0,
                    "max": max(all_maxs) if all_maxs else 0.0,
                }

            if hasattr(self.pos_panel, "update_statistics"):
                self.pos_panel.update_statistics(aggregated_pos)

        except Exception as e:
            print(f"Error updating 2D charts page: {e}")
            import traceback
            traceback.print_exc()