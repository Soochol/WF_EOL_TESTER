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
        """Setup the simplified results UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Create flexible splitter for table and chart
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(4)

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

        # Set optimized splitter proportions (65% table, 35% chart)
        self.main_splitter.setSizes([650, 350])

        main_layout.addWidget(self.main_splitter)

        # Apply styling
        self.apply_styling()

    def apply_styling(self) -> None:
        """Apply styling to the widget."""
        widget_style = get_results_widget_style()
        splitter_style = get_splitter_style()

        combined_style = widget_style + splitter_style
        self.setStyleSheet(combined_style)
