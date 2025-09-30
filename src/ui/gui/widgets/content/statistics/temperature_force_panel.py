"""Temperature Force Statistics Panel

Displays force statistics grouped by temperature levels.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TemperatureForcePanel(QWidget):
    """Temperature-based force statistics panel.

    Shows force statistics (mean, std, min, max) for each temperature level.
    Temperature levels: 38°C, 52°C, 66°C
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the temperature force panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Modern title
        title_label = QLabel("🌡️ Force Statistics by Temperature")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            color: #ffffff;
            margin-bottom: 15px;
            padding: 12px;
            background-color: rgba(255, 152, 0, 0.1);
            border-left: 4px solid #FF9800;
            border-radius: 8px;
        """)
        main_layout.addWidget(title_label)

        # Statistics table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Temperature (°C)",
            "Mean Force (N)",
            "Std Dev (N)",
            "Min Force (N)",
            "Max Force (N)",
        ])

        # Modern table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                gridline-color: rgba(255, 255, 255, 0.05);
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QTableWidget::item:selected {
                background-color: rgba(255, 152, 0, 0.3);
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QHeaderView::section {
                background-color: rgba(255, 152, 0, 0.2);
                color: #ffffff;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #FF9800;
                font-weight: 600;
                font-size: 12px;
            }
        """)

        # Table properties
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)

        main_layout.addWidget(self.table)

    def update_statistics(
        self, stats_by_temp: Dict[float, Dict[str, float]]
    ) -> None:
        """Update the temperature force statistics table.

        Args:
            stats_by_temp: Dictionary mapping temperature to statistics.
                Example: {
                    38.0: {"mean": 45.2, "std": 2.1, "min": 40.0, "max": 50.0},
                    52.0: {"mean": 48.5, "std": 1.8, "min": 45.0, "max": 52.0},
                    66.0: {"mean": 51.3, "std": 2.3, "min": 47.0, "max": 55.0},
                }
        """
        # Clear existing rows
        self.table.setRowCount(0)

        if not stats_by_temp:
            return

        # Sort temperatures
        temperatures = sorted(stats_by_temp.keys())

        # Add rows for each temperature
        for row_idx, temp in enumerate(temperatures):
            stats = stats_by_temp[temp]

            self.table.insertRow(row_idx)

            # Temperature
            temp_item = QTableWidgetItem(f"{temp:.1f}")
            temp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, temp_item)

            # Mean
            mean_item = QTableWidgetItem(f"{stats.get('mean', 0.0):.2f}")
            mean_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, mean_item)

            # Std Dev
            std_item = QTableWidgetItem(f"{stats.get('std', 0.0):.2f}")
            std_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, std_item)

            # Min
            min_item = QTableWidgetItem(f"{stats.get('min', 0.0):.2f}")
            min_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, min_item)

            # Max
            max_item = QTableWidgetItem(f"{stats.get('max', 0.0):.2f}")
            max_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, max_item)

    def clear(self) -> None:
        """Clear all table data."""
        self.table.setRowCount(0)