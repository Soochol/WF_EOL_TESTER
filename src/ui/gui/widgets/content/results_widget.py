"""
Results Widget

Results analysis page with detailed test results and statistics.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.widgets.results_table_widget import ResultsTableWidget
from ui.gui.widgets.temperature_force_chart_widget import TemperatureForceChartWidget


class ResultsWidget(QWidget):
    """
    Results widget for detailed test results analysis.

    Shows comprehensive test results, statistics, and export options.
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
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the results UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header with controls
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)

        # Create splitter for table and chart
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Results table (upper part)
        self.results_table = ResultsTableWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        splitter.addWidget(self.results_table)

        # Temperature-Force chart (lower part)
        self.temp_force_chart = TemperatureForceChartWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        splitter.addWidget(self.temp_force_chart)

        # Set initial splitter proportions (60% table, 40% chart)
        splitter.setSizes([600, 400])

        main_layout.addWidget(splitter)

        # Apply styling
        self.setStyleSheet(
            """
            ResultsWidget {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: 1px solid #106ebe;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """
        )

    def create_header(self) -> QHBoxLayout:
        """Create header with controls"""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # Title
        title = QLabel("Test Results")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        # Add stretch to maintain layout
        layout.addStretch()

        return layout
