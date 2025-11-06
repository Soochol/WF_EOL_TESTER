"""
Graph Panel

Panel for displaying Force vs Temperature graphs grouped by serial number.
"""

# Standard library imports
from typing import Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt
from loguru import logger
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# Set matplotlib to use Qt backend
matplotlib.use("QtAgg")

# Local application imports
from ui.gui.styles.common_styles import (
    BACKGROUND_DARK,
    BACKGROUND_MEDIUM,
    BORDER_DEFAULT,
    TEXT_SECONDARY,
    get_groupbox_style,
)


class SerialNumberGraph(QWidget):
    """Single graph for one serial number"""

    def __init__(self, serial_number: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.serial_number = serial_number
        self.test_data: Dict[str, List[Dict]] = {}  # test_id -> measurements
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup graph UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Create matplotlib figure with dark theme
        self.figure = Figure(figsize=(10, 4), facecolor="#1e1e1e")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Apply dark theme to axes
        self.ax.set_facecolor("#2d2d2d")
        self.ax.spines["bottom"].set_color("#404040")
        self.ax.spines["top"].set_color("#404040")
        self.ax.spines["left"].set_color("#404040")
        self.ax.spines["right"].set_color("#404040")
        self.ax.tick_params(colors="#cccccc")
        self.ax.set_xlabel("Temperature (°C)", color="#ffffff", fontweight="bold")
        self.ax.set_ylabel("Force (N)", color="#ffffff", fontweight="bold")

        # Enable grid for both X and Y axes
        self.ax.grid(
            True,
            which="both",
            axis="both",
            color="#404040",
            alpha=0.5,
            linestyle="-",
            linewidth=0.8,
        )
        self.ax.grid(
            True,
            which="minor",
            axis="both",
            color="#404040",
            alpha=0.2,
            linestyle=":",
            linewidth=0.5,
        )

        layout.addWidget(self.canvas)

    def add_test_data(self, test_id: str, measurements: List[Dict]) -> None:
        """Add test data to graph"""
        logger.debug(
            f"Adding test data to graph: serial={self.serial_number}, "
            f"test_id={test_id}, measurements={len(measurements)}"
        )
        self.test_data[test_id] = measurements
        self.update_graph()

    def clear_data(self) -> None:
        """Clear all test data"""
        self.test_data.clear()
        self.ax.clear()
        self.canvas.draw()

    def update_graph(self) -> None:
        """Update graph with all test data"""
        logger.debug(f"Updating graph for serial={self.serial_number}, tests={len(self.test_data)}")
        self.ax.clear()

        # Re-apply dark theme after clear
        self.ax.set_facecolor("#2d2d2d")
        self.ax.spines["bottom"].set_color("#404040")
        self.ax.spines["top"].set_color("#404040")
        self.ax.spines["left"].set_color("#404040")
        self.ax.spines["right"].set_color("#404040")
        self.ax.tick_params(colors="#cccccc")
        self.ax.set_xlabel("Temperature (°C)", color="#ffffff", fontweight="bold")
        self.ax.set_ylabel("Force (N)", color="#ffffff", fontweight="bold")

        # Enable grid for both X and Y axes
        self.ax.grid(
            True,
            which="both",
            axis="both",
            color="#404040",
            alpha=0.5,
            linestyle="-",
            linewidth=0.8,
        )
        self.ax.grid(
            True,
            which="minor",
            axis="both",
            color="#404040",
            alpha=0.2,
            linestyle=":",
            linewidth=0.5,
        )

        # Color palette for different tests
        colors = ["#0078d4", "#ff6b6b", "#51cf66", "#ffd43b", "#a78bfa", "#38bdf8"]

        plotted_count = 0
        # Plot each test
        for idx, (test_id, measurements) in enumerate(self.test_data.items()):
            if not measurements:
                logger.warning(f"No measurements for test_id={test_id}")
                continue

            # Extract temperature and force values (filter out None values)
            temps: List[float] = [
                float(m.get("temperature"))  # type: ignore[arg-type]
                for m in measurements
                if m.get("temperature") is not None
            ]
            forces: List[float] = [
                float(m.get("force"))  # type: ignore[arg-type]
                for m in measurements
                if m.get("force") is not None
            ]

            logger.debug(
                f"Test {test_id}: {len(temps)} temps, {len(forces)} forces "
                f"(from {len(measurements)} measurements)"
            )

            if temps and forces and len(temps) == len(forces):
                color = colors[idx % len(colors)]

                # Use serial number for legend (more meaningful than test_id)
                # Get serial number from first measurement (all measurements have same serial)
                serial_number = measurements[0].get("serial_number", "Unknown")
                legend_label = serial_number

                self.ax.plot(
                    temps,
                    forces,
                    marker="o",
                    linewidth=2,
                    markersize=6,
                    color=color,
                    label=legend_label,
                    alpha=0.8,
                )
                plotted_count += 1
                logger.debug(f"Plotted test {legend_label} with {len(temps)} points")
            else:
                logger.warning(
                    f"Skipping test {test_id}: temps={len(temps)}, forces={len(forces)}, "
                    f"match={len(temps) == len(forces)}"
                )

        # Add legend if there's data
        if self.test_data:
            legend = self.ax.legend(
                loc="upper left",
                framealpha=0.9,
                facecolor="#2d2d2d",
                edgecolor="#404040",
            )
            plt.setp(legend.get_texts(), color="#cccccc")

        # Set title - use "Selected Tests" when serial_number is generic
        if self.serial_number == "All Selected Tests":
            title = f"Selected Tests ({len(self.test_data)} tests)"
        else:
            title = f"Serial Number: {self.serial_number} ({len(self.test_data)} tests)"

        self.ax.set_title(
            title,
            color="#ffffff",
            fontweight="bold",
            pad=15,
        )

        # Tight layout and redraw
        self.figure.tight_layout()
        self.canvas.draw()
        logger.debug(f"Graph rendered: serial={self.serial_number}, plotted={plotted_count} tests")


class GraphPanel(QWidget):
    """
    Graph panel widget for displaying multiple serial number graphs.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.serial_graphs: Dict[str, SerialNumberGraph] = {}
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Group box
        graph_group = QGroupBox("Force vs Temperature Graphs")
        graph_group.setStyleSheet(get_groupbox_style())
        group_layout = QVBoxLayout(graph_group)

        # Scroll area for graphs
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(self._get_scroll_style())

        # Container for graphs
        self.graph_container = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_container)
        self.graph_layout.setSpacing(15)
        self.graph_layout.setContentsMargins(5, 5, 5, 5)

        # Placeholder label
        self.placeholder_label = QLabel("No data to display. Please run a search.")
        self.placeholder_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 14px; padding: 40px;"
        )
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_layout.addWidget(self.placeholder_label)

        self.scroll_area.setWidget(self.graph_container)
        group_layout.addWidget(self.scroll_area)
        layout.addWidget(graph_group)

    def update_graphs(self, grouped_data: Dict[str, Dict[str, List[Dict]]]) -> None:
        """
        Update graphs with new data.

        Args:
            grouped_data: {serial_number: {test_id: [measurements]}}
        """
        logger.info(f"Updating graph panel: {len(grouped_data)} serial numbers")

        # Clear existing graphs
        self.clear_graphs()

        if not grouped_data:
            logger.info("No data to display - showing placeholder")
            self.placeholder_label.show()
            return

        self.placeholder_label.hide()

        # Create graph for each serial number
        for serial_number, tests in grouped_data.items():
            logger.info(f"Creating graph for serial={serial_number}, tests={len(tests)}")
            graph = SerialNumberGraph(serial_number)

            # Add all tests for this serial number
            for test_id, measurements in tests.items():
                logger.debug(
                    f"Adding test to graph: serial={serial_number}, "
                    f"test_id={test_id}, measurements={len(measurements)}"
                )
                graph.add_test_data(test_id, measurements)

            self.serial_graphs[serial_number] = graph
            self.graph_layout.addWidget(graph)

        # Add stretch at the end
        self.graph_layout.addStretch()
        logger.info(f"Graph panel update complete: {len(self.serial_graphs)} graphs created")

    def clear_graphs(self) -> None:
        """Clear all graphs"""
        logger.debug(f"Clearing {len(self.serial_graphs)} graphs")
        # Remove all graph widgets
        for graph in self.serial_graphs.values():
            self.graph_layout.removeWidget(graph)
            graph.deleteLater()

        self.serial_graphs.clear()

        # Show placeholder
        if self.placeholder_label.parent() is None:
            self.graph_layout.addWidget(self.placeholder_label)
        logger.debug("Graphs cleared")

    def _get_scroll_style(self) -> str:
        """Get scroll area stylesheet"""
        return f"""
        QScrollArea {{
            background-color: {BACKGROUND_DARK};
            border: 1px solid {BORDER_DEFAULT};
            border-radius: 4px;
        }}
        QScrollBar:vertical {{
            background-color: {BACKGROUND_DARK};
            width: 14px;
            border: 1px solid {BORDER_DEFAULT};
        }}
        QScrollBar::handle:vertical {{
            background-color: {BACKGROUND_MEDIUM};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: #0078d4;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        """
