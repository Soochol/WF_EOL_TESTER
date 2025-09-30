"""Force 3D Surface Plot Panel

3D surface plot showing Temperature × Position × Force relationship.
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
    import numpy as np
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class Force3DSurface(QWidget):
    """3D surface plot panel showing Temperature × Position × Force.

    Creates a 3D surface where:
    - X-axis: Temperature (°C)
    - Y-axis: Position (mm)
    - Z-axis: Force (N)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the 3D surface plot UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("3D Surface Plot: Temperature × Position × Force")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Interactive 3D surface showing force distribution across temperature and position"
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
                "⚠️ matplotlib and numpy not installed\n\n" "Install with: uv add matplotlib numpy"
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

    def update_surface(self, surface_data: Dict[Tuple[float, float], float]) -> None:
        """Update the 3D surface plot.

        Args:
            surface_data: Dictionary mapping (temperature, position_mm) to avg force.
                Example: {
                    (38.0, 130.0): 45.2,
                    (38.0, 150.0): 47.5,
                    (38.0, 170.0): 49.1,
                    (52.0, 130.0): 46.8,
                    ...
                }
        """
        if not MATPLOTLIB_AVAILABLE or not surface_data:
            return

        # Clear previous plot
        self.ax.clear()
        self.setup_axes_style()

        # Extract unique temperatures and positions
        temperatures: list[float] = sorted(set(temp for temp, _ in surface_data.keys()))
        positions: list[float] = sorted(set(pos for _, pos in surface_data.keys()))

        if not temperatures or not positions:
            return

        # Create meshgrid
        T, P = np.meshgrid(temperatures, positions)

        # Create force grid
        F = np.zeros_like(T)
        for i, pos in enumerate(positions):
            for j, temp in enumerate(temperatures):
                force = surface_data.get((temp, pos), 0.0)
                F[i, j] = force

        # Create 3D surface plot
        surf = self.ax.plot_surface(
            T,
            P,
            F,
            cmap="viridis",
            alpha=0.8,
            edgecolor="#404040",
            linewidth=0.3,
            antialiased=True,
        )

        # Labels
        self.ax.set_xlabel("Temperature (°C)", fontsize=10, color="#ffffff", labelpad=10)
        self.ax.set_ylabel("Position (mm)", fontsize=10, color="#ffffff", labelpad=10)
        self.ax.set_zlabel("Force (N)", fontsize=10, color="#ffffff", labelpad=10)
        self.ax.set_title(
            "Force Surface: Temperature × Position", fontsize=12, color="#ffffff", pad=20
        )

        # Colorbar
        cbar = self.figure.colorbar(surf, ax=self.ax, shrink=0.5, aspect=10)
        cbar.set_label("Force (N)", color="#ffffff", fontsize=10)
        cbar.ax.yaxis.set_tick_params(color="#ffffff")
        cbar.ax.tick_params(labelcolor="#ffffff")
        cbar.outline.set_edgecolor("#404040")  # type: ignore[attr-defined]

        # Set viewing angle
        self.ax.view_init(elev=20, azim=45)

        # Tight layout
        self.figure.tight_layout()

        # Redraw canvas
        self.canvas.draw()

    def clear(self) -> None:
        """Clear the 3D surface plot."""
        if MATPLOTLIB_AVAILABLE:
            self.ax.clear()
            self.setup_axes_style()
            self.canvas.draw()
