"""New Analysis Statistics Page

Comprehensive analysis page with 2D charts, heatmaps, and statistical tables.
Merges functionality from Charts2DPage and PerformancePage.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

# Local imports
from ..force_trend_chart import ForceTrendChart
from ..force_heatmap_2d import ForceHeatmap2D
from ..temperature_force_panel import TemperatureForcePanel
from ..position_force_panel import PositionForcePanel


class NewAnalysisPage(QWidget):
    """Enhanced analysis page with detailed charts and statistics.

    Features:
    - Force trend chart (time series)
    - Force heatmap (temperature vs position)
    - Temperature statistics table
    - Position statistics table
    - Export functionality for each chart
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
        """Setup analysis page UI."""
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

        # Force Trend Chart
        self.trend_chart = ForceTrendChart()
        self.trend_chart.setMinimumHeight(400)
        content_layout.addWidget(self.trend_chart)

        # Force Heatmap
        self.heatmap = ForceHeatmap2D()
        self.heatmap.setMinimumHeight(400)
        content_layout.addWidget(self.heatmap)

        # Temperature Analysis
        self.temp_panel = TemperatureForcePanel()
        self.temp_panel.setMinimumHeight(300)
        content_layout.addWidget(self.temp_panel)

        # Position Analysis
        self.pos_panel = PositionForcePanel()
        self.pos_panel.setMinimumHeight(300)
        content_layout.addWidget(self.pos_panel)

        # Add stretch to push content to top
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Apply dark theme
        self.setStyleSheet("background-color: #1e1e1e;")

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Update analysis page data based on filters.

        Args:
            filters: Filter criteria from header controls
        """
        try:
            # Get all tests with filters
            all_tests = await self.statistics_service.repository.get_all_tests()
            filtered_tests = self.statistics_service._apply_filters(all_tests, filters)

            # Update trend chart
            trend_data = []
            for result in filtered_tests:
                measurements = result.get("test_result", {}).get("actual_results", {}).get(
                    "measurements", {}
                )
                timestamp = result.get("start_time")

                for temp_str, positions in measurements.items():
                    for position_str, data in positions.items():
                        trend_data.append({
                            "timestamp": timestamp,
                            "temperature": float(temp_str),
                            "position_mm": float(position_str) / 1000.0,
                            "force": data.get("force", 0.0),
                        })

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
            print(f"Error updating analysis page: {e}")
            import traceback
            traceback.print_exc()

    def clear_data(self) -> None:
        """Clear all displayed data."""
        if hasattr(self.trend_chart, "clear"):
            self.trend_chart.clear()
        if hasattr(self.heatmap, "clear"):
            self.heatmap.clear()
        if hasattr(self.temp_panel, "clear"):
            self.temp_panel.clear()
        if hasattr(self.pos_panel, "clear"):
            self.pos_panel.clear()