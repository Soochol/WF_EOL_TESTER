"""3D Visualizations Page

3D visualizations including surface plots, scatter plots, and contour plots.
"""

# Standard library imports
from typing import Any, Dict

# Local imports
from .base_statistics_page import BaseStatisticsPage
from ..force_3d_surface import Force3DSurface
from ..force_3d_scatter import Force3DScatter
from ..force_contour_plot import ForceContourPlot


class Visualizations3DPage(BaseStatisticsPage):
    """3D Visualization Tools page."""

    def create_content(self) -> None:
        """Add 3 3D visualization panels."""
        # 3D Surface Plot (full size)
        self.surface_3d = Force3DSurface()
        self.surface_3d.setMinimumHeight(600)  # Large 3D plot
        self.content_layout.addWidget(self.surface_3d)

        # 3D Scatter Plot (full size)
        self.scatter_3d = Force3DScatter()
        self.scatter_3d.setMinimumHeight(600)  # Large 3D plot
        self.content_layout.addWidget(self.scatter_3d)

        # Contour Plot (full size)
        self.contour = ForceContourPlot()
        self.contour.setMinimumHeight(600)  # Large contour plot
        self.content_layout.addWidget(self.contour)

    async def update_data(self, filters: Dict[str, Any]) -> None:
        """Update 3D visualizations."""
        try:
            # Update 3D surface plot
            surface_data = await self.statistics_service.get_force_heatmap_data(filters)
            if hasattr(self.surface_3d, "update_surface"):
                self.surface_3d.update_surface(surface_data)

            # Update 3D scatter plot
            scatter_data = await self.statistics_service.get_3d_scatter_data(filters)
            if hasattr(self.scatter_3d, "update_scatter"):
                self.scatter_3d.update_scatter(scatter_data)

            # Update contour plot
            contour_data = await self.statistics_service.get_force_heatmap_data(filters)
            if hasattr(self.contour, "update_contour"):
                self.contour.update_contour(contour_data)

        except Exception as e:
            print(f"Error updating 3D visualizations page: {e}")
            import traceback
            traceback.print_exc()