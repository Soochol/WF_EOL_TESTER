"""Force 4D Scatter Plot Panel

4D scatter plot showing force measurements with time as the 4th dimension (color).
"""

# Standard library imports
from typing import Any, Dict, List, Optional

# Third-party imports
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

try:
    # Third-party imports
    import matplotlib

    matplotlib.use("QtAgg")
    # Third-party imports
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class Force4DScatter(QWidget):
    """4D scatter plot panel with time as color dimension.

    Creates a 4D scatter plot where:
    - X-axis: Temperature (°C)
    - Y-axis: Position (mm)
    - Z-axis: Force (N)
    - Color: Time (timestamp)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        if MATPLOTLIB_AVAILABLE:
            self.figure: Figure
            self.canvas: FigureCanvas
            self.ax: Any  # 3D axes type (mpl_toolkits.mplot3d.axes3d.Axes3D)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the 4D scatter plot UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("4D Scatter Plot: Force Measurements with Time")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "4D visualization with time represented by color gradient (older → newer)"
        )
        desc_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        main_layout.addWidget(desc_label)

        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure and canvas
            self.figure = Figure(figsize=(10, 7), facecolor="#2d2d2d")
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("background-color: #2d2d2d;")

            # Create 3D axes
            self.ax = self.figure.add_subplot(111, projection="3d")
            self.setup_axes_style()

            main_layout.addWidget(self.canvas)
        else:
            # Fallback if matplotlib is not available
            error_label = QLabel(
                "⚠️ matplotlib and numpy not installed\n\nInstall with: uv add matplotlib numpy"
            )
            error_label.setStyleSheet("color: #f59e0b; font-size: 11pt; padding: 20px;")
            main_layout.addWidget(error_label)

    def setup_axes_style(self) -> None:
        """Setup matplotlib 3D axes styling for dark theme."""
        if not MATPLOTLIB_AVAILABLE:
            return

        # Set dark theme colors
        self.ax.set_facecolor("#1e1e1e")
        self.ax.xaxis.pane.set_facecolor("#1e1e1e")  # type: ignore[attr-defined]
        self.ax.yaxis.pane.set_facecolor("#1e1e1e")  # type: ignore[attr-defined]
        self.ax.zaxis.pane.set_facecolor("#1e1e1e")  # type: ignore[attr-defined]

        # Grid colors
        self.ax.xaxis.pane.set_edgecolor("#404040")  # type: ignore[attr-defined]
        self.ax.yaxis.pane.set_edgecolor("#404040")  # type: ignore[attr-defined]
        self.ax.zaxis.pane.set_edgecolor("#404040")  # type: ignore[attr-defined]

        # Tick colors
        self.ax.tick_params(colors="#ffffff", which="both")
        self.ax.xaxis.label.set_color("#ffffff")
        self.ax.yaxis.label.set_color("#ffffff")
        self.ax.zaxis.label.set_color("#ffffff")
        self.ax.title.set_color("#ffffff")

    def update_scatter(self, scatter_data: List[Dict[str, Any]]) -> None:
        """Update the 4D scatter plot.

        Args:
            scatter_data: List of measurements, each containing:
                - temperature: float
                - position_mm: float
                - force: float
                - timestamp: datetime
        """
        if not MATPLOTLIB_AVAILABLE or not scatter_data:
            return

        # Clear previous plot
        self.ax.clear()
        self.setup_axes_style()

        # Extract data
        temperatures: list[float] = [d["temperature"] for d in scatter_data]
        positions: list[float] = [d["position_mm"] for d in scatter_data]
        forces: list[float] = [d["force"] for d in scatter_data]
        timestamps: list[Any] = [d["timestamp"] for d in scatter_data]

        # Convert timestamps to numerical values for coloring
        time_values = mdates.date2num(timestamps)

        # Normalize time values for better color mapping
        time_min = min(time_values)
        time_max = max(time_values)
        time_normalized = [
            (t - time_min) / (time_max - time_min) if time_max > time_min else 0.5
            for t in time_values
        ]

        # Create 4D scatter plot (3D with color as 4th dimension)
        scatter = self.ax.scatter(
            temperatures,
            positions,
            forces,
            c=time_normalized,
            cmap="plasma",  # Good for time progression
            marker="o",
            s=40,
            alpha=0.7,
            edgecolors="#ffffff",
            linewidths=0.5,
        )

        # Labels
        self.ax.set_xlabel("Temperature (°C)", fontsize=10, color="#ffffff", labelpad=10)
        self.ax.set_ylabel("Position (mm)", fontsize=10, color="#ffffff", labelpad=10)
        self.ax.set_zlabel("Force (N)", fontsize=10, color="#ffffff", labelpad=10)
        self.ax.set_title(
            "Force Over Time: Temperature × Position × Time", fontsize=12, color="#ffffff", pad=20
        )

        # Colorbar with time labels
        cbar = self.figure.colorbar(scatter, ax=self.ax, shrink=0.5, aspect=10)
        cbar.set_label("Time (older → newer)", color="#ffffff", fontsize=10)
        cbar.ax.yaxis.set_tick_params(color="#ffffff")
        cbar.ax.tick_params(labelcolor="#ffffff")
        cbar.outline.set_edgecolor("#404040")  # type: ignore[attr-defined]

        # Format colorbar ticks as dates (first, middle, last)
        if len(timestamps) > 0:
            first_date = timestamps[0].strftime("%Y-%m-%d")
            last_date = timestamps[-1].strftime("%Y-%m-%d")
            cbar.ax.set_yticklabels(["", first_date, "", last_date, ""])

        # Set viewing angle
        self.ax.view_init(elev=20, azim=45)

        # Tight layout
        self.figure.tight_layout()

        # Redraw canvas
        self.canvas.draw()

    def clear(self) -> None:
        """Clear the 4D scatter plot."""
        if MATPLOTLIB_AVAILABLE:
            self.ax.clear()
            self.setup_axes_style()
            self.canvas.draw()
