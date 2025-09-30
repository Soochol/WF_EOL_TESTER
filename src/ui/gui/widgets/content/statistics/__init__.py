"""Statistics Widget Package

Provides comprehensive statistics and analysis UI for EOL Force Test results.
"""

# Export sub-pages
from .pages import (
    OverviewPage,
    Charts2DPage,
    Visualizations3DPage,
    Analysis4DPage,
    PerformancePage,
    ExportPage,
)

# Export components
from .collapsible_section import CollapsibleSection
from .header_controls import StatisticsHeaderControls
from .overview_panel import OverviewPanel
from .temperature_force_panel import TemperatureForcePanel
from .position_force_panel import PositionForcePanel
from .force_trend_chart import ForceTrendChart
from .force_heatmap_2d import ForceHeatmap2D
from .force_3d_surface import Force3DSurface
from .force_3d_scatter import Force3DScatter
from .force_4d_scatter import Force4DScatter
from .force_contour_plot import ForceContourPlot
from .performance_panel import PerformancePanel
from .comparison_panel import ComparisonPanel
from .export_panel import ExportPanel

__all__ = [
    # Sub-pages
    "OverviewPage",
    "Charts2DPage",
    "Visualizations3DPage",
    "Analysis4DPage",
    "PerformancePage",
    "ExportPage",
    # Components
    "CollapsibleSection",
    "StatisticsHeaderControls",
    "OverviewPanel",
    "TemperatureForcePanel",
    "PositionForcePanel",
    "ForceTrendChart",
    "ForceHeatmap2D",
    "Force3DSurface",
    "Force3DScatter",
    "Force4DScatter",
    "ForceContourPlot",
    "PerformancePanel",
    "ComparisonPanel",
    "ExportPanel",
]