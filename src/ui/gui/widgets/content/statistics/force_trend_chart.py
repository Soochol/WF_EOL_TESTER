"""Force Trend Chart Panel

2D line chart showing force trends over time.
"""

# Standard library imports
from typing import List, Dict, Any, Optional

# Third-party imports
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QFont

try:
    import matplotlib
    matplotlib.use('QtAgg')  # Use Qt backend
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ForceTrendChart(QWidget):
    """Force trend chart panel with 2D line visualization.

    Shows force values over time with optional grouping by temperature or position.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the force trend chart UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("Force Trend Over Time")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Force measurements over time (2D line chart)")
        desc_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        main_layout.addWidget(desc_label)

        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure and canvas
            self.figure = Figure(figsize=(10, 5), facecolor='#2d2d2d')
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("background-color: #2d2d2d;")

            # Create axes
            self.ax = self.figure.add_subplot(111)
            self.setup_axes_style()

            main_layout.addWidget(self.canvas)
        else:
            # Fallback if matplotlib is not available
            error_label = QLabel("⚠️ matplotlib not installed\n\n"
                                "Install with: uv add matplotlib")
            error_label.setStyleSheet("color: #f59e0b; font-size: 11pt; padding: 20px;")
            main_layout.addWidget(error_label)

    def setup_axes_style(self) -> None:
        """Setup matplotlib axes styling for dark theme."""
        if not MATPLOTLIB_AVAILABLE:
            return

        # Set dark theme colors
        self.ax.set_facecolor('#1e1e1e')
        self.ax.spines['bottom'].set_color('#404040')
        self.ax.spines['left'].set_color('#404040')
        self.ax.spines['top'].set_color('#404040')
        self.ax.spines['right'].set_color('#404040')
        self.ax.tick_params(colors='#ffffff', which='both')
        self.ax.xaxis.label.set_color('#ffffff')
        self.ax.yaxis.label.set_color('#ffffff')
        self.ax.title.set_color('#ffffff')

        # Grid
        self.ax.grid(True, alpha=0.2, color='#404040')

    def update_chart(self, trend_data: List[Dict[str, Any]]) -> None:
        """Update the force trend chart.

        Args:
            trend_data: List of data points, each containing:
                - timestamp: datetime
                - force: float
                - temperature: float (optional, for grouping)
                - position_mm: float (optional, for grouping)
        """
        if not MATPLOTLIB_AVAILABLE or not trend_data:
            return

        # Clear previous plot
        self.ax.clear()
        self.setup_axes_style()

        # Extract timestamps and forces
        timestamps = [point["timestamp"] for point in trend_data]
        forces = [point["force"] for point in trend_data]

        # Plot force trend
        self.ax.plot(
            timestamps,
            forces,
            marker='o',
            markersize=4,
            linewidth=2,
            color='#0078d4',
            label='Force',
        )

        # Format x-axis for dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.figure.autofmt_xdate()  # Rotate date labels

        # Labels
        self.ax.set_xlabel('Time', fontsize=10, color='#ffffff')
        self.ax.set_ylabel('Force (N)', fontsize=10, color='#ffffff')
        self.ax.set_title('Force Measurements Over Time', fontsize=12, color='#ffffff')

        # Legend
        self.ax.legend(facecolor='#2d2d2d', edgecolor='#404040', labelcolor='#ffffff')

        # Tight layout
        self.figure.tight_layout()

        # Redraw canvas
        self.canvas.draw()

    def update_grouped_chart(
        self,
        trend_data: List[Dict[str, Any]],
        group_by: str = "temperature"
    ) -> None:
        """Update the force trend chart with grouping.

        Args:
            trend_data: List of data points
            group_by: Grouping key ("temperature" or "position")
        """
        if not MATPLOTLIB_AVAILABLE or not trend_data:
            return

        # Clear previous plot
        self.ax.clear()
        self.setup_axes_style()

        # Group data
        groups: Dict[Any, List[Dict[str, Any]]] = {}
        for point in trend_data:
            key = point.get(group_by)
            if key is not None:
                if key not in groups:
                    groups[key] = []
                groups[key].append(point)

        # Color palette
        colors = ['#0078d4', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']

        # Plot each group
        for idx, (key, group_points) in enumerate(sorted(groups.items())):
            timestamps = [p["timestamp"] for p in group_points]
            forces = [p["force"] for p in group_points]

            color = colors[idx % len(colors)]
            label = f"{key}°C" if group_by == "temperature" else f"{key}mm"

            self.ax.plot(
                timestamps,
                forces,
                marker='o',
                markersize=3,
                linewidth=1.5,
                color=color,
                label=label,
            )

        # Format x-axis for dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.figure.autofmt_xdate()

        # Labels
        self.ax.set_xlabel('Time', fontsize=10, color='#ffffff')
        self.ax.set_ylabel('Force (N)', fontsize=10, color='#ffffff')
        title = f'Force Over Time (by {group_by.title()})'
        self.ax.set_title(title, fontsize=12, color='#ffffff')

        # Legend
        self.ax.legend(facecolor='#2d2d2d', edgecolor='#404040', labelcolor='#ffffff')

        # Tight layout
        self.figure.tight_layout()

        # Redraw canvas
        self.canvas.draw()

    def clear(self) -> None:
        """Clear the chart."""
        if MATPLOTLIB_AVAILABLE:
            self.ax.clear()
            self.setup_axes_style()
            self.canvas.draw()