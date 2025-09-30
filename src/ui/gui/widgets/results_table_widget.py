"""
Results Table Widget

Widget for displaying test results in a table format.
"""

# Standard library imports
from datetime import datetime
from typing import Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager, TestResult


class ResultsTableWidget(QWidget):
    """
    Results table widget for displaying test results.

    Shows test results with columns for Cycle, Temp, Stroke, Force,
    Heating Time, Cooling Time, Status, and Time.
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
        self.connect_signals()
        # Sample data removed - start with empty table

    def setup_ui(self) -> None:
        """Setup the results table UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create table (no group box for modern style)
        self.results_table = QTableWidget()
        self.setup_table()
        main_layout.addWidget(self.results_table)

        # Apply styling
        self.setStyleSheet(self._get_widget_style())

    def setup_table(self) -> None:
        """Setup the table widget"""
        # Set up columns
        headers = [
            "Cycle",
            "Temp(°C)",
            "Stroke(mm)",
            "Force(kgf)",
            "Heating Time(s)",
            "Cooling Time(s)",
            "Status",
            "Time",
        ]

        self.results_table.setColumnCount(len(headers))
        self.results_table.setHorizontalHeaderLabels(headers)

        # Table properties
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.results_table.setSortingEnabled(False)  # Disable sorting to maintain order

        # Header configuration
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)

        # Optimize column widths for better header visibility
        self.results_table.setColumnWidth(0, 80)  # Cycle - wider for repetition display
        self.results_table.setColumnWidth(1, 100)  # Temp(°C) - wider for full header
        self.results_table.setColumnWidth(2, 110)  # Stroke(mm) - wider for full header
        self.results_table.setColumnWidth(3, 110)  # Force(kgf) - wider for full header
        self.results_table.setColumnWidth(4, 140)  # Heating Time(s) - much wider for full header
        self.results_table.setColumnWidth(5, 140)  # Cooling Time(s) - much wider for full header
        self.results_table.setColumnWidth(6, 80)  # Status
        # Time column will stretch

        # Vertical header
        self.results_table.verticalHeader().setVisible(False)

        # Set minimum height
        self.results_table.setMinimumHeight(200)

    def connect_signals(self) -> None:
        """Connect to state manager signals"""
        self.state_manager.test_result_added.connect(self._on_test_result_added)
        self.state_manager.cycle_result_added.connect(self._on_cycle_result_added)

    def _on_test_result_added(self, result: TestResult) -> None:
        """Handle new test result"""
        self.add_test_result(result)

    def _on_cycle_result_added(self, result: TestResult) -> None:
        """Handle new cycle result (for individual test repetitions)"""
        # Third-party imports
        from loguru import logger

        logger.info(
            f"📋 Results Table Widget: Received cycle result signal for cycle {result.cycle}"
        )
        logger.info(
            f"📋 Results Table Widget: Data - Temp: {result.temperature:.1f}°C, Force: {result.force:.2f}kgf, Status: {result.status}"
        )

        try:
            self.add_cycle_result(result)
            logger.info(
                f"✅ Results Table Widget: Successfully processed cycle {result.cycle} result"
            )
        except Exception as e:
            logger.error(
                f"❌ Results Table Widget: Failed to process cycle {result.cycle} result: {e}"
            )

    def add_test_result(self, result) -> None:  # Accept both TestResult and EOLTestResult
        """Add a test result to the table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        # Handle different result types - GUI TestResult vs domain EOLTestResult
        if hasattr(result, "cycle"):  # GUI TestResult
            status_text = result.status
            items = [
                QTableWidgetItem(str(result.cycle)),
                QTableWidgetItem(f"{result.temperature:.1f}"),
                QTableWidgetItem(f"{result.stroke:.1f}"),
                QTableWidgetItem(f"{result.force:.2f}"),
                QTableWidgetItem(str(result.heating_time)),
                QTableWidgetItem(str(result.cooling_time)),
                QTableWidgetItem(status_text),
                QTableWidgetItem(result.timestamp.strftime("%Y-%m-%d %H:%M")),
            ]
        else:  # Domain result objects (EOL, HeatingCooling, etc) - convert to display format
            # Determine status text from domain result
            if hasattr(result, "test_status"):
                # Check for EOL-specific attributes first
                if hasattr(result, "is_device_passed"):
                    if result.is_device_passed:
                        status_text = "PASS"
                    elif result.is_device_failed:
                        status_text = "FAIL"
                    elif result.is_failed_execution:
                        status_text = "ERROR"
                    else:
                        status_text = result.test_status.value
                # For other result types (like HeatingCoolingTimeTestResult), use is_success or error_message
                elif hasattr(result, "is_success"):
                    if result.is_success and not result.error_message:
                        status_text = "PASS"
                    else:
                        status_text = "FAIL" if result.error_message else "PASS"
                else:
                    status_text = result.test_status.value
            else:
                status_text = "UNKNOWN"

            # Create items with available data (use defaults for missing fields)
            items = [
                QTableWidgetItem("1"),  # Default cycle
                QTableWidgetItem("25.0"),  # Default temperature
                QTableWidgetItem("12.5"),  # Default stroke
                QTableWidgetItem("5.00"),  # Default force
                QTableWidgetItem("45"),  # Default heating time
                QTableWidgetItem("120"),  # Default cooling time
                QTableWidgetItem(status_text),
                QTableWidgetItem(datetime.now().strftime("%Y-%m-%d %H:%M")),
            ]

        for col, item in enumerate(items):
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

            # Color coding for status - modern colors
            if col == 6:  # Status column
                status_value = item.text()
                if status_value == "PASS":
                    item.setForeground(QColor("#00D9A5"))
                elif status_value in ["FAIL", "ERROR"]:
                    item.setForeground(QColor("#F44336"))
                elif status_value == "PENDING":
                    item.setForeground(QColor("#FF9800"))

            self.results_table.setItem(row, col, item)

        # Scroll to bottom to show latest result
        self.results_table.scrollToBottom()

        # Highlight current row if it's the latest
        if hasattr(result, "cycle") and result.cycle > 0:  # Not pending
            self.results_table.selectRow(row)

    def add_cycle_result(self, result: TestResult) -> None:
        """Add a cycle result to the table (for individual test repetitions)"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        # Format cycle display
        cycle_display = str(result.cycle)

        items = [
            QTableWidgetItem(cycle_display),
            QTableWidgetItem(f"{result.temperature:.1f}"),
            QTableWidgetItem(f"{result.stroke:.1f}"),
            QTableWidgetItem(f"{result.force:.2f}"),
            QTableWidgetItem(str(result.heating_time)),
            QTableWidgetItem(str(result.cooling_time)),
            QTableWidgetItem(result.status),
            QTableWidgetItem(result.timestamp.strftime("%Y-%m-%d %H:%M")),
        ]

        for col, item in enumerate(items):
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

            # Color coding for status - modern colors
            if col == 6:  # Status column
                status_value = item.text()
                if status_value == "PASS":
                    item.setForeground(QColor("#00D9A5"))
                elif status_value in ["FAIL", "ERROR"]:
                    item.setForeground(QColor("#F44336"))
                elif status_value == "PENDING":
                    item.setForeground(QColor("#FF9800"))

            self.results_table.setItem(row, col, item)

        # Scroll to bottom to show latest result
        self.results_table.scrollToBottom()

        # Select the new row
        self.results_table.selectRow(row)

    def clear_results(self) -> None:
        """Clear all results from the table"""
        self.results_table.setRowCount(0)

    def _populate_with_sample_data(self) -> None:
        """Populate table with sample data for demonstration"""
        sample_results = [
            TestResult(1, 24.2, 12.5, 4.98, 45, 120, "PASS", datetime(2024, 9, 25, 14, 23)),
            TestResult(2, 24.3, 12.3, 5.02, 46, 118, "PASS", datetime(2024, 9, 25, 14, 26)),
            TestResult(3, 24.4, 12.4, 4.99, 44, 122, "PASS", datetime(2024, 9, 25, 14, 29)),
            TestResult(4, 24.5, 12.1, 5.21, 47, 115, "FAIL", datetime(2024, 9, 25, 14, 32)),
            TestResult(5, 24.5, 12.6, 5.00, 45, 120, "PASS", datetime(2024, 9, 25, 14, 35)),
            TestResult(6, 24.6, 12.4, 4.97, 46, 119, "PASS", datetime(2024, 9, 25, 14, 38)),
            TestResult(7, 0.0, 0.0, 0.0, 0, 0, "PENDING", datetime.now()),
            TestResult(8, 0.0, 0.0, 0.0, 0, 0, "PENDING", datetime.now()),
        ]

        for result in sample_results:
            self.add_test_result(result)

    def _get_group_font(self) -> QFont:
        """Get font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def _get_widget_style(self) -> str:
        """Get widget stylesheet"""
        return """
        ResultsTableWidget {
            background-color: transparent;
            color: #cccccc;
        }
        QTableWidget {
            background-color: transparent;
            alternate-background-color: rgba(255, 255, 255, 0.02);
            color: #ffffff;
            border: none;
            selection-background-color: rgba(33, 150, 243, 0.3);
            selection-color: #ffffff;
            gridline-color: rgba(255, 255, 255, 0.1);
        }
        QTableWidget::item {
            padding: 12px 8px;
            border: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        QTableWidget::item:hover {
            background-color: rgba(255, 255, 255, 0.05);
        }
        QHeaderView::section {
            background-color: rgba(255, 255, 255, 0.05);
            color: #cccccc;
            padding: 14px 8px;
            border: none;
            border-bottom: 2px solid #2196F3;
            font-weight: 600;
            font-size: 13px;
        }
        QHeaderView::section:hover {
            background-color: rgba(255, 255, 255, 0.08);
        }
        QScrollBar:vertical {
            background-color: transparent;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: rgba(255, 255, 255, 0.3);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """
