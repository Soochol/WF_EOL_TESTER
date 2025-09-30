"""Force Heat Map Panel (2D)

2D heat map showing force values across Temperature × Position grid.
"""

# Standard library imports
from typing import Dict, Optional, Tuple

# Third-party imports
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

try:
    # Third-party imports
    import matplotlib

    matplotlib.use("QtAgg")
    # Third-party imports
    import numpy as np
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ForceHeatmap2D(QWidget):
    """2D heat map panel showing Temperature × Position force distribution.

    Color intensity represents average force values.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the force heat map UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("Force Heat Map (Temperature × Position)")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Description
        desc_label = QLabel("2D color-coded heat map showing average force distribution")
        desc_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        main_layout.addWidget(desc_label)

        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure and canvas
            self.figure = Figure(figsize=(10, 6), facecolor="#2d2d2d")
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("background-color: #2d2d2d;")

            # Create axes
            self.ax = self.figure.add_subplot(111)
            self.setup_axes_style()

            main_layout.addWidget(self.canvas)
        else:
            # Fallback if matplotlib is not available
            error_label = QLabel(
                "⚠️ matplotlib and numpy not installed\n\n" "Install with: uv add matplotlib numpy"
            )
            error_label.setStyleSheet("color: #f59e0b; font-size: 11pt; padding: 20px;")
            main_layout.addWidget(error_label)

    def setup_axes_style(self) -> None:
        """Setup matplotlib axes styling for dark theme."""
        if not MATPLOTLIB_AVAILABLE:
            return

        # Set dark theme colors
        self.ax.set_facecolor("#1e1e1e")
        self.ax.spines["bottom"].set_color("#404040")
        self.ax.spines["left"].set_color("#404040")
        self.ax.spines["top"].set_color("#404040")
        self.ax.spines["right"].set_color("#404040")
        self.ax.tick_params(colors="#ffffff", which="both")
        self.ax.xaxis.label.set_color("#ffffff")
        self.ax.yaxis.label.set_color("#ffffff")
        self.ax.title.set_color("#ffffff")

    def update_heatmap(self, heatmap_data: Dict[Tuple[float, float], float]) -> None:
        """Update the force heat map.

        Args:
            heatmap_data: Dictionary mapping (temperature, position_mm) to avg force.
                Example: {
                    (38.0, 130.0): 45.2,
                    (38.0, 150.0): 47.5,
                    (38.0, 170.0): 49.1,
                    (52.0, 130.0): 46.8,
                    ...
                }
        """
        if not MATPLOTLIB_AVAILABLE or not heatmap_data:
            return

        # Clear previous plot
        self.ax.clear()
        self.setup_axes_style()

        # Extract unique temperatures and positions
        temperatures = sorted(set(temp for temp, _ in heatmap_data.keys()))
        positions = sorted(set(pos for _, pos in heatmap_data.keys()))

        if not temperatures or not positions:
            return

        # Create 2D grid for heat map
        force_grid = np.zeros((len(positions), len(temperatures)))

        for i, pos in enumerate(positions):
            for j, temp in enumerate(temperatures):
                force = heatmap_data.get((temp, pos), 0.0)
                force_grid[i, j] = force

        # Create heat map
        im = self.ax.imshow(
            force_grid,
            cmap="hot",
            aspect="auto",
            origin="lower",
            interpolation="nearest",
        )

        # Set ticks
        self.ax.set_xticks(range(len(temperatures)))
        self.ax.set_yticks(range(len(positions)))
        self.ax.set_xticklabels([f"{t:.1f}°C" for t in temperatures])
        self.ax.set_yticklabels([f"{p:.1f}mm" for p in positions])

        # Labels
        self.ax.set_xlabel("Temperature", fontsize=10, color="#ffffff")
        self.ax.set_ylabel("Position", fontsize=10, color="#ffffff")
        self.ax.set_title("Average Force Heat Map", fontsize=12, color="#ffffff")

        # Colorbar
        cbar = self.figure.colorbar(im, ax=self.ax)
        cbar.set_label("Force (N)", color="#ffffff", fontsize=10)
        cbar.ax.yaxis.set_tick_params(color="#ffffff")
        cbar.ax.tick_params(labelcolor="#ffffff")
        cbar.outline.set_edgecolor("#404040")  # type: ignore[attr-defined]

        # Add text annotations
        for i in range(len(positions)):
            for j in range(len(temperatures)):
                force = force_grid[i, j]
                text_color = "#000000" if force > force_grid.max() * 0.5 else "#ffffff"
                self.ax.text(
                    j,
                    i,
                    f"{force:.1f}",
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=9,
                )

        # Tight layout
        self.figure.tight_layout()

        # Redraw canvas
        self.canvas.draw()

    def clear(self) -> None:
        """Clear the heat map."""
        if MATPLOTLIB_AVAILABLE:
            self.ax.clear()
            self.setup_axes_style()
            self.canvas.draw()
