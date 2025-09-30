"""Performance Analysis Panel

Displays performance metrics including fastest/slowest tests and duration distribution.
"""

# Standard library imports
from typing import List, Dict, Any, Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class PerformancePanel(QWidget):
    """Performance analysis panel showing test duration metrics.

    Features:
    - Top 5 fastest tests
    - Top 5 slowest tests
    - Average duration statistics
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the performance panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Modern title
        title_label = QLabel("⚡ Test Performance Analysis")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            color: #ffffff;
            margin-bottom: 15px;
            padding: 12px;
            background-color: rgba(33, 150, 243, 0.1);
            border-left: 4px solid #2196F3;
            border-radius: 8px;
        """)
        main_layout.addWidget(title_label)

        # Grid layout for two tables
        tables_layout = QGridLayout()
        tables_layout.setSpacing(15)

        # Fastest tests table
        fastest_group = self.create_fastest_group()
        tables_layout.addWidget(fastest_group, 0, 0)

        # Slowest tests table
        slowest_group = self.create_slowest_group()
        tables_layout.addWidget(slowest_group, 0, 1)

        main_layout.addLayout(tables_layout)

    def create_fastest_group(self) -> QGroupBox:
        """Create fastest tests table group."""
        group = QGroupBox("⚡ Top 5 Fastest Tests")
        group.setStyleSheet(self._get_group_style("#00D9A5"))

        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        self.fastest_table = QTableWidget()
        self.fastest_table.setColumnCount(3)
        self.fastest_table.setHorizontalHeaderLabels([
            "Serial Number",
            "Duration (s)",
            "Date",
        ])
        self.fastest_table.setStyleSheet(self._get_table_style())
        self.fastest_table.setAlternatingRowColors(True)
        self.fastest_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.fastest_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.fastest_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fastest_table.verticalHeader().setVisible(False)
        self.fastest_table.setMaximumHeight(200)

        layout.addWidget(self.fastest_table)
        return group

    def create_slowest_group(self) -> QGroupBox:
        """Create slowest tests table group."""
        group = QGroupBox("🐌 Top 5 Slowest Tests")
        group.setStyleSheet(self._get_group_style("#F44336"))

        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        self.slowest_table = QTableWidget()
        self.slowest_table.setColumnCount(3)
        self.slowest_table.setHorizontalHeaderLabels([
            "Serial Number",
            "Duration (s)",
            "Date",
        ])
        self.slowest_table.setStyleSheet(self._get_table_style())
        self.slowest_table.setAlternatingRowColors(True)
        self.slowest_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.slowest_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.slowest_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.slowest_table.verticalHeader().setVisible(False)
        self.slowest_table.setMaximumHeight(200)

        layout.addWidget(self.slowest_table)
        return group

    def _get_group_style(self, border_color: str) -> str:
        """Get group box styling with custom border color."""
        return f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 13px;
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: 4px solid {border_color};
                border-radius: 12px;
                margin-top: 12px;
                padding: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 10px;
                background-color: transparent;
                color: {border_color};
            }}
        """

    def _get_table_style(self) -> str:
        """Get table styling."""
        return """
            QTableWidget {
                background-color: transparent;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                gridline-color: rgba(255, 255, 255, 0.05);
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QTableWidget::item:selected {
                background-color: rgba(33, 150, 243, 0.3);
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QHeaderView::section {
                background-color: rgba(33, 150, 243, 0.2);
                color: #ffffff;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #2196F3;
                font-weight: 600;
                font-size: 12px;
            }
        """

    def update_performance(
        self,
        fastest: List[Dict[str, Any]],
        slowest: List[Dict[str, Any]]
    ) -> None:
        """Update the performance tables.

        Args:
            fastest: List of fastest tests, each containing:
                - serial_number: str
                - duration: float
                - timestamp: datetime
            slowest: List of slowest tests, same structure as fastest
        """
        # Update fastest table
        self.fastest_table.setRowCount(0)
        for row_idx, test in enumerate(fastest[:5]):
            self.fastest_table.insertRow(row_idx)

            # Serial number
            serial_item = QTableWidgetItem(test["serial_number"])
            serial_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fastest_table.setItem(row_idx, 0, serial_item)

            # Duration
            duration_item = QTableWidgetItem(f"{test['duration']:.2f}")
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fastest_table.setItem(row_idx, 1, duration_item)

            # Date
            date_str = test["timestamp"].strftime("%Y-%m-%d %H:%M")
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fastest_table.setItem(row_idx, 2, date_item)

        # Update slowest table
        self.slowest_table.setRowCount(0)
        for row_idx, test in enumerate(slowest[:5]):
            self.slowest_table.insertRow(row_idx)

            # Serial number
            serial_item = QTableWidgetItem(test["serial_number"])
            serial_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.slowest_table.setItem(row_idx, 0, serial_item)

            # Duration
            duration_item = QTableWidgetItem(f"{test['duration']:.2f}")
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.slowest_table.setItem(row_idx, 1, duration_item)

            # Date
            date_str = test["timestamp"].strftime("%Y-%m-%d %H:%M")
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.slowest_table.setItem(row_idx, 2, date_item)

    def clear(self) -> None:
        """Clear all performance data."""
        self.fastest_table.setRowCount(0)
        self.slowest_table.setRowCount(0)