"""
Results Widget

Simple results viewer with table and chart display.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.styles.common_styles import get_results_widget_style, get_splitter_style
from ui.gui.widgets.results_table_widget import ResultsTableWidget
from ui.gui.widgets.temperature_force_chart_widget import TemperatureForceChartWidget


class ResultsWidget(QWidget):
    """
    Simple results widget for test results display.

    Features:
    - Results table view
    - Temperature-Force chart view
    - Flexible splitter layout
    """

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager

        # Initialize components
        self.results_table: Optional[ResultsTableWidget] = None
        self.temp_force_chart: Optional[TemperatureForceChartWidget] = None
        self.main_splitter: Optional[QSplitter] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the modern results UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Apply dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
        """)

        # Create flexible splitter for table and chart
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(8)
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                margin: 4px 0;
            }
            QSplitter::handle:hover {
                background-color: rgba(33, 150, 243, 0.3);
            }
        """)

        # Results table
        self.results_table = ResultsTableWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.main_splitter.addWidget(self.results_table)

        # Temperature-Force chart
        self.temp_force_chart = TemperatureForceChartWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.main_splitter.addWidget(self.temp_force_chart)

        # Set optimized splitter proportions (60% table, 40% chart)
        self.main_splitter.setSizes([600, 400])

        main_layout.addWidget(self.main_splitter)
