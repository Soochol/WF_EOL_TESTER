"""
Dashboard Widget

Main dashboard page showing system overview and key information.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.widgets.hardware_status_widget import HardwareStatusWidget
from ui.gui.widgets.results_table_widget import ResultsTableWidget
from ui.gui.widgets.test_progress_widget import TestProgressWidget


class DashboardWidget(QWidget):
    """
    Dashboard widget showing system overview.

    Displays hardware status, test progress, and recent results.
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
        """Setup the dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Top row: Hardware Status
        self.hardware_status = HardwareStatusWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        main_layout.addWidget(self.hardware_status)

        # Middle row: Test Progress
        self.test_progress = TestProgressWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        main_layout.addWidget(self.test_progress)

        # Bottom row: Results table
        self.results_table = ResultsTableWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        main_layout.addWidget(self.results_table, stretch=1)

        # Apply styling
        self.setStyleSheet(
            """
            DashboardWidget {
                background-color: #1e1e1e;
                color: #cccccc;
            }
        """
        )
