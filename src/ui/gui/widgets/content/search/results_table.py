"""
Results Table

Table widget for displaying search results from database.
"""

# Standard library imports
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from ui.gui.styles.common_styles import (
    ACCENT_BLUE,
    BACKGROUND_DARK,
    BACKGROUND_MEDIUM,
    BORDER_DEFAULT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    get_groupbox_style,
)


class ResultsTable(QWidget):
    """
    Results table widget for displaying test results.

    Signals:
        row_selected: Emitted when a row is selected (test_id)
        selection_changed: Emitted when checkbox selection changes (selected_count)
    """

    row_selected = Signal(str)  # test_id
    selection_changed = Signal(int)  # selected_count

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.test_results: List[Dict] = []
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the table UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Group box for table
        table_group = QGroupBox("Test Results")
        table_group.setStyleSheet(get_groupbox_style())
        group_layout = QVBoxLayout(table_group)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["☑", "Test ID", "Serial Number", "Created At", "Measurements", "Status"]
        )

        # Table properties
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.table.setAlternatingRowColors(False)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        # Disable editing and focus
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Test ID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # Serial Number
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Created At
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Measurements
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status

        # Style
        self.table.setStyleSheet(self._get_table_style())

        # Connect signals
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        group_layout.addWidget(self.table)
        layout.addWidget(table_group)

    def update_results(self, results: List[Dict]) -> None:
        """Update table with new results"""
        self.test_results = results
        self.table.setSortingEnabled(False)  # Disable sorting while updating
        self.table.setRowCount(0)  # Clear existing rows

        for row_idx, result in enumerate(results):
            self.table.insertRow(row_idx)

            # Checkbox (Column 0)
            checkbox = QCheckBox()
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    background-color: transparent;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {BORDER_DEFAULT};
                    border-radius: 3px;
                    background-color: {BACKGROUND_MEDIUM};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {ACCENT_BLUE};
                    border-color: {ACCENT_BLUE};
                    image: none;
                }}
                QCheckBox::indicator:hover {{
                    border-color: {ACCENT_BLUE};
                }}
            """)
            checkbox.stateChanged.connect(self._on_checkbox_changed)

            # Center checkbox in cell
            checkbox_widget = QWidget()
            checkbox_layout = QVBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row_idx, 0, checkbox_widget)

            # Test ID (Column 1)
            test_id_item = QTableWidgetItem(result.get("test_id", ""))
            test_id_item.setData(Qt.ItemDataRole.UserRole, result)  # Store full result
            self.table.setItem(row_idx, 1, test_id_item)

            # Serial Number (Column 2)
            serial_item = QTableWidgetItem(result.get("serial_number", "N/A"))
            self.table.setItem(row_idx, 2, serial_item)

            # Created At (Column 3)
            created_at = result.get("created_at")
            created_str = self._format_datetime(created_at) if created_at else "N/A"
            created_item = QTableWidgetItem(created_str)
            self.table.setItem(row_idx, 3, created_item)

            # Measurement Count (Column 4)
            measurement_count = result.get("measurement_count", 0)
            count_item = QTableWidgetItem(f"{measurement_count}")
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, count_item)

            # Status (Column 5) - N/A for raw_measurements
            status = result.get("status", "N/A")
            status_item = QTableWidgetItem(status if status == "N/A" else self._format_status(status))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, status_item)

        self.table.setSortingEnabled(True)  # Re-enable sorting
        self.table.resizeColumnsToContents()

        # Emit initial selection count (0)
        self.selection_changed.emit(0)

    def _on_selection_changed(self) -> None:
        """Handle row selection change"""
        selected_rows = self.table.selectedItems()
        if selected_rows:
            # Get test_id from second column (index 1) of selected row
            row = selected_rows[0].row()
            test_id_item = self.table.item(row, 1)
            if test_id_item:
                test_id = test_id_item.text()
                self.row_selected.emit(test_id)

    def _on_checkbox_changed(self) -> None:
        """Handle checkbox state change"""
        selected_count = self.get_selected_count()
        self.selection_changed.emit(selected_count)

    def get_selected_test_ids(self) -> List[str]:
        """Get list of test IDs for checked rows"""
        selected_ids = []
        for row in range(self.table.rowCount()):
            # Get checkbox widget
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                # Find QCheckBox in the cell widget
                checkbox = cell_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    # Get test_id from column 1
                    test_id_item = self.table.item(row, 1)
                    if test_id_item:
                        selected_ids.append(test_id_item.text())
        return selected_ids

    def get_selected_count(self) -> int:
        """Get count of checked rows"""
        return len(self.get_selected_test_ids())

    def select_all(self) -> None:
        """Check all checkboxes"""
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                checkbox = cell_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)

    def deselect_all(self) -> None:
        """Uncheck all checkboxes"""
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                checkbox = cell_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)

    def _format_status(self, status: str) -> str:
        """Format status with emoji"""
        status_map = {
            "completed": "✅ Pass",
            "failed": "❌ Fail",
            "running": "🔄 Running",
            "pending": "⏳ Pending",
        }
        return status_map.get(status.lower(), f"❓ {status}")

    def _format_datetime(self, dt) -> str:
        """Format datetime for display"""
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except ValueError:
                return dt

        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        return str(dt)

    def _get_table_style(self) -> str:
        """Get table stylesheet"""
        return f"""
        QTableWidget {{
            background-color: {BACKGROUND_DARK};
            color: {TEXT_SECONDARY};
            gridline-color: {BORDER_DEFAULT};
            border: 1px solid {BORDER_DEFAULT};
            border-radius: 4px;
            selection-background-color: transparent;
            selection-color: {TEXT_SECONDARY};
            outline: none;
        }}
        QTableWidget::item {{
            padding: 8px;
            border: none;
            outline: none;
        }}
        QTableWidget::item:selected {{
            background-color: transparent;
            color: {TEXT_SECONDARY};
        }}
        QTableWidget::item:focus {{
            background-color: transparent;
            outline: none;
            border: none;
        }}
        QTableWidget::item:hover {{
            background-color: rgba(0, 120, 212, 0.3);
        }}
        QHeaderView::section {{
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_PRIMARY};
            font-weight: bold;
            border: 1px solid {BORDER_DEFAULT};
            padding: 8px;
            text-align: left;
        }}
        QHeaderView::section:hover {{
            background-color: {ACCENT_BLUE};
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
            background-color: {ACCENT_BLUE};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        """
