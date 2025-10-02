"""New Advanced Statistics Page

Advanced visualizations including 3D surface plots, scatter plots, 4D analysis, and contour plots.
Merges functionality from Visualizations3DPage and Analysis4DPage.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

# Local folder imports
from ..force_3d_scatter import Force3DScatter

# Local imports
from ..force_3d_surface import Force3DSurface
from ..force_4d_scatter import Force4DScatter
from ..force_contour_plot import ForceContourPlot


class NewAdvancedPage(QWidget):
    """Advanced analysis page with 3D/4D visualizations.

    Features:
    - 3D Surface Plot (Force vs Temp vs Position)
    - 3D Scatter Plot (Interactive visualization)
    - 4D Analysis (Force + Temp + Position + Time)
    - Contour Plot (Force distribution mapping)

    Note: This page is for advanced users and in-depth analysis.
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
        """Setup advanced page UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Info header
        info_label = QLabel("🔬 Advanced Visualizations")
        info_font = QFont()
        info_font.setPointSize(14)
        info_font.setBold(True)
        info_label.setFont(info_font)
        info_label.setStyleSheet(
            """
            color: #ffffff;
            padding: 12px;
            background-color: rgba(156, 39, 176, 0.1);
            border-left: 4px solid #9C27B0;
            border-radius: 8px;
            margin-bottom: 10px;
        """
        )
        main_layout.addWidget(info_label)

        desc_label = QLabel(
            "ℹ️ Advanced 3D/4D visualizations for in-depth analysis. "
            "Interact with charts by rotating, zooming, and panning."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #aaaaaa; font-size: 12px; padding: 5px;")
        main_layout.addWidget(desc_label)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(
            """
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
        """
        )

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 3D Surface Plot
        self.surface_plot = Force3DSurface()
        self.surface_plot.setMinimumHeight(500)
        content_layout.addWidget(self.surface_plot)

        # 3D Scatter Plot
        self.scatter_plot = Force3DScatter()
        self.scatter_plot.setMinimumHeight(500)
        content_layout.addWidget(self.scatter_plot)

        # 4D Analysis
        self.analysis_4d = Force4DScatter()
        self.analysis_4d.setMinimumHeight(500)
        content_layout.addWidget(self.analysis_4d)

        # Contour Plot
        self.contour_plot = ForceContourPlot()
        self.contour_plot.setMinimumHeight(400)
        content_layout.addWidget(self.contour_plot)

        # Add stretch to push content to top
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Apply dark theme
        self.setStyleSheet("background-color: #1e1e1e;")

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Update advanced page data based on filters.

        Args:
            filters: Filter criteria from header controls
        """
        try:
            # Get all tests with filters
            all_tests = await self.statistics_service.repository.get_all_tests()
            filtered_tests = self.statistics_service._apply_filters(all_tests, filters)

            # Prepare 3D data
            plot_3d_data = []
            for result in filtered_tests:
                measurements = (
                    result.get("test_result", {}).get("actual_results", {}).get("measurements", {})
                )
                timestamp = result.get("start_time")

                for temp_str, positions in measurements.items():
                    temp = float(temp_str)
                    for position_str, data in positions.items():
                        position_mm = float(position_str) / 1000.0
                        force = data.get("force", 0.0)

                        plot_3d_data.append(
                            {
                                "temperature": temp,
                                "position_mm": position_mm,
                                "force": force,
                                "timestamp": timestamp,
                            }
                        )

            # Update 3D surface plot (convert list to dict format)
            if hasattr(self.surface_plot, "update_surface"):
                # Convert list format to dict format: {(temp, pos): avg_force}
                surface_dict: Dict[tuple[float, float], float] = {}
                for data_point in plot_3d_data:
                    key = (data_point["temperature"], data_point["position_mm"])
                    if key in surface_dict:
                        # Average if multiple measurements at same temp/position
                        surface_dict[key] = (surface_dict[key] + data_point["force"]) / 2
                    else:
                        surface_dict[key] = data_point["force"]
                self.surface_plot.update_surface(surface_dict)

            # Update 3D scatter plot
            if hasattr(self.scatter_plot, "update_scatter"):
                self.scatter_plot.update_scatter(plot_3d_data)

            # Update 4D analysis (includes time dimension)
            if hasattr(self.analysis_4d, "update_scatter"):
                self.analysis_4d.update_scatter(plot_3d_data)

            # Update contour plot (reuse surface dict or create new)
            if hasattr(self.contour_plot, "update_contour"):
                # Convert list format to dict format: {(temp, pos): avg_force}
                contour_dict: Dict[tuple[float, float], float] = {}
                for data_point in plot_3d_data:
                    key = (data_point["temperature"], data_point["position_mm"])
                    if key in contour_dict:
                        # Average if multiple measurements at same temp/position
                        contour_dict[key] = (contour_dict[key] + data_point["force"]) / 2
                    else:
                        contour_dict[key] = data_point["force"]
                self.contour_plot.update_contour(contour_dict)

        except Exception as e:
            print(f"Error updating advanced page: {e}")
            # Standard library imports
            import traceback

            traceback.print_exc()

    def clear_data(self) -> None:
        """Clear all displayed data."""
        if hasattr(self.surface_plot, "clear"):
            self.surface_plot.clear()
        if hasattr(self.scatter_plot, "clear"):
            self.scatter_plot.clear()
        if hasattr(self.analysis_4d, "clear"):
            self.analysis_4d.clear()
        if hasattr(self.contour_plot, "clear"):
            self.contour_plot.clear()
