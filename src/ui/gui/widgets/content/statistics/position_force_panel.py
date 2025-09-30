"""Position Force Statistics Panel

Displays force statistics grouped by position levels with mm unit conversion.
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

# Local application imports


class PositionForcePanel(QWidget):
    """Position-based force statistics panel with mm unit conversion.

    Shows force statistics (mean, std, min, max) for each position level.
    Positions are converted from μm to mm for display.
    Typical position levels: 130mm, 150mm, 170mm
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the position force panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("Force Statistics by Position")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Force measurements grouped by position levels (displayed in mm)"
        )
        desc_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        main_layout.addWidget(desc_label)

        # Statistics table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Position (mm)",
            "Mean Force (N)",
            "Std Dev (N)",
            "Min Force (N)",
            "Max Force (N)",
        ])

        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 6px;
                gridline-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #404040;
                font-weight: bold;
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
        self, stats_by_position: Dict[float, Dict[str, float]]
    ) -> None:
        """Update the position force statistics table.

        Args:
            stats_by_position: Dictionary mapping position (in mm) to statistics.
                Example: {
                    130.0: {"mean": 45.2, "std": 2.1, "min": 40.0, "max": 50.0},
                    150.0: {"mean": 48.5, "std": 1.8, "min": 45.0, "max": 52.0},
                    170.0: {"mean": 51.3, "std": 2.3, "min": 47.0, "max": 55.0},
                }

        Note:
            Input positions should already be converted to mm.
            If positions are in μm, convert using PositionUnitConverter.um_to_mm()
        """
        # Clear existing rows
        self.table.setRowCount(0)

        if not stats_by_position:
            return

        # Sort positions
        positions = sorted(stats_by_position.keys())

        # Add rows for each position
        for row_idx, position_mm in enumerate(positions):
            stats = stats_by_position[position_mm]

            self.table.insertRow(row_idx)

            # Position (mm)
            pos_item = QTableWidgetItem(f"{position_mm:.1f}")
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, pos_item)

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