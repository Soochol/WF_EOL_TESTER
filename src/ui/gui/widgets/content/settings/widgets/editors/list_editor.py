"""
List editor widget for editing list-type configuration values.

Provides a table-based editor for list values, particularly designed
for spec_points configuration with temperature, stroke, and force limits.
"""

# Standard library imports
from typing import Any

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

# Local folder imports
from ...core import Colors
from .base_editor import BaseEditorWidget


class DoubleSpinBoxDelegate(QStyledItemDelegate):
    """Custom delegate for QDoubleSpinBox in table cells"""

    def __init__(self, min_value=-1000.0, max_value=1000.0, decimals=1, parent=None):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.decimals = decimals

    def createEditor(self, parent, option, index):
        """Create spin box editor for cell"""
        editor = QDoubleSpinBox(parent)
        editor.setRange(self.min_value, self.max_value)
        editor.setDecimals(self.decimals)
        editor.setStyleSheet(
            f"""
            QDoubleSpinBox {{
                border: 2px solid {Colors.PRIMARY_ACCENT};
                border-radius: 4px;
                padding: 4px;
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                font-size: 12px;
            }}
        """
        )
        return editor

    def setEditorData(self, editor, index):
        """Set data from model to editor"""
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        try:
            editor.setValue(float(value))
        except (ValueError, TypeError):
            editor.setValue(0.0)

    def setModelData(self, editor, model, index):
        """Set data from editor to model"""
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.ItemDataRole.EditRole)


class ListEditorWidget(BaseEditorWidget):
    """Table-based editor for list configuration values - saves immediately on changes"""

    # Immediate save: table changes (add/delete row, cell edit) are applied instantly
    IMMEDIATE_SAVE = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup_ui(self) -> None:
        """Setup list editor UI with table"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header with Add button
        header_layout = QHBoxLayout()
        header_layout.addStretch()

        add_btn = QPushButton("➕ Add Point")
        add_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.PRIMARY_ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: rgba(33, 150, 243, 0.8);
            }}
            QPushButton:pressed {{
                background-color: rgba(33, 150, 243, 0.6);
            }}
        """
        )
        add_btn.clicked.connect(self.add_row)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Temp (°C)", "Stroke (μm)", "Upper (kgf)", "Lower (kgf)", ""]
        )

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 100)  # Temperature
        self.table.setColumnWidth(1, 120)  # Stroke
        self.table.setColumnWidth(2, 110)  # Upper limit
        self.table.setColumnWidth(3, 110)  # Lower limit
        self.table.setColumnWidth(4, 50)  # Delete button

        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.verticalHeader().setVisible(False)

        # Enable sorting
        self.table.setSortingEnabled(False)

        # Set item delegates for numeric columns
        self.table.setItemDelegateForColumn(0, DoubleSpinBoxDelegate(-100.0, 200.0, 1, self))
        self.table.setItemDelegateForColumn(1, DoubleSpinBoxDelegate(0.0, 999999.0, 1, self))
        self.table.setItemDelegateForColumn(2, DoubleSpinBoxDelegate(-1000.0, 1000.0, 1, self))
        self.table.setItemDelegateForColumn(3, DoubleSpinBoxDelegate(-1000.0, 1000.0, 1, self))

        # Styling
        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {Colors.SECONDARY_BACKGROUND};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                gridline-color: {Colors.BORDER};
                color: {Colors.TEXT_PRIMARY};
            }}
            QTableWidget::item {{
                padding: 5px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: rgba(33, 150, 243, 0.3);
            }}
            QTableWidget::item:hover {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
            QHeaderView::section {{
                background-color: {Colors.TERTIARY_BACKGROUND};
                color: {Colors.TEXT_SECONDARY};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {Colors.BORDER};
                font-weight: 600;
                font-size: 11px;
            }}
        """
        )

        layout.addWidget(self.table)

        # Populate table with initial data
        self.populate_table()

    def populate_table(self) -> None:
        """Populate table from config value list"""
        self.table.setRowCount(0)

        if not isinstance(self.config_value.value, list):
            return

        for row_data in self.config_value.value:
            if isinstance(row_data, (list, tuple)) and len(row_data) >= 4:
                self.add_row_with_data(row_data)

    def add_row_with_data(self, data: Any) -> None:
        """Add a row with specific data"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Temperature
        temp_item = QTableWidgetItem(str(data[0]))
        temp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, temp_item)

        # Stroke
        stroke_item = QTableWidgetItem(str(data[1]))
        stroke_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, stroke_item)

        # Upper limit
        upper_item = QTableWidgetItem(str(data[2]))
        upper_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, upper_item)

        # Lower limit
        lower_item = QTableWidgetItem(str(data[3]))
        lower_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, lower_item)

        # Delete button
        delete_btn = QPushButton("🗑")
        delete_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(244, 67, 54, 0.2);
                border-radius: 4px;
            }
        """
        )
        delete_btn.clicked.connect(lambda checked, r=row: self.delete_row(r))
        self.table.setCellWidget(row, 4, delete_btn)

    def add_row(self) -> None:
        """Add a new empty row to the table"""
        # Default values for new row
        default_data = [38.0, 170000.0, 10.0, -10.0]
        self.add_row_with_data(default_data)
        self.on_value_changed()

    def delete_row(self, row: int) -> None:
        """Delete a specific row from the table"""
        self.table.removeRow(row)
        # Re-connect delete buttons after row removal
        for r in range(self.table.rowCount()):
            btn = self.table.cellWidget(r, 4)
            if btn and isinstance(btn, QPushButton):
                btn.clicked.disconnect()
                btn.clicked.connect(lambda checked, row_num=r: self.delete_row(row_num))
        self.on_value_changed()

    def connect_signals(self) -> None:
        """Connect signals for value changes"""
        self.table.itemChanged.connect(self.on_value_changed)

    def get_value(self) -> Any:
        """Get the current value from the table as a list"""
        result = []
        for row in range(self.table.rowCount()):
            try:
                temp = float(self.table.item(row, 0).text() if self.table.item(row, 0) else 0.0)
                stroke = float(self.table.item(row, 1).text() if self.table.item(row, 1) else 0.0)
                upper = float(self.table.item(row, 2).text() if self.table.item(row, 2) else 0.0)
                lower = float(self.table.item(row, 3).text() if self.table.item(row, 3) else 0.0)

                result.append([temp, stroke, upper, lower])
            except (ValueError, AttributeError):
                # Skip invalid rows
                continue

        return result

    def set_value(self, value: Any) -> None:
        """Set the value in the table"""
        if isinstance(value, list):
            self.config_value.value = value
            self.populate_table()
