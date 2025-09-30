"""Test Comparison Panel

Compare multiple test results side-by-side.
"""

# Standard library imports
from typing import List, Dict, Any, Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ComparisonPanel(QWidget):
    """Test comparison panel for side-by-side analysis.

    Features:
    - Select multiple tests to compare
    - Side-by-side comparison table
    - Key metrics comparison
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.available_tests: List[Dict[str, Any]] = []
        self.selected_tests: List[str] = []
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the comparison panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("Test Comparison")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Compare multiple test results side-by-side")
        desc_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        main_layout.addWidget(desc_label)

        # Selection controls
        selection_layout = self.create_selection_controls()
        main_layout.addLayout(selection_layout)

        # Comparison table
        self.comparison_table = QTableWidget()
        self.comparison_table.setStyleSheet("""
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
        self.comparison_table.setAlternatingRowColors(True)
        self.comparison_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.comparison_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        main_layout.addWidget(self.comparison_table)

    def create_selection_controls(self) -> QHBoxLayout:
        """Create test selection controls."""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # Test selector label
        label = QLabel("Select tests:")
        label.setStyleSheet("color: #ffffff; font-weight: bold;")
        layout.addWidget(label)

        # Test 1 selector
        self.test1_combo = QComboBox()
        self.test1_combo.setPlaceholderText("Test 1")
        self.test1_combo.currentTextChanged.connect(self.on_selection_changed)
        layout.addWidget(self.test1_combo)

        # Test 2 selector
        self.test2_combo = QComboBox()
        self.test2_combo.setPlaceholderText("Test 2")
        self.test2_combo.currentTextChanged.connect(self.on_selection_changed)
        layout.addWidget(self.test2_combo)

        # Test 3 selector
        self.test3_combo = QComboBox()
        self.test3_combo.setPlaceholderText("Test 3 (optional)")
        self.test3_combo.currentTextChanged.connect(self.on_selection_changed)
        layout.addWidget(self.test3_combo)

        # Compare button
        compare_btn = QPushButton("Compare")
        compare_btn.clicked.connect(self.compare_tests)
        layout.addWidget(compare_btn)

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_comparison)
        layout.addWidget(clear_btn)

        layout.addStretch()

        return layout

    def set_available_tests(self, tests: List[Dict[str, Any]]) -> None:
        """Set the list of available tests.

        Args:
            tests: List of test dictionaries with 'serial_number' and other data
        """
        self.available_tests = tests

        # Update combo boxes
        test_labels = [f"{t['serial_number']} ({t.get('timestamp', 'N/A')})"
                      for t in tests]

        for combo in [self.test1_combo, self.test2_combo, self.test3_combo]:
            combo.clear()
            combo.addItem("")  # Empty option
            combo.addItems(test_labels)

    def on_selection_changed(self) -> None:
        """Handle selection change in combo boxes."""
        # Auto-compare when selections change
        pass

    def compare_tests(self) -> None:
        """Compare selected tests."""
        # Get selected test indices
        selected_indices = []
        for combo in [self.test1_combo, self.test2_combo, self.test3_combo]:
            if combo.currentIndex() > 0:  # Skip empty selection
                selected_indices.append(combo.currentIndex() - 1)

        if len(selected_indices) < 2:
            return  # Need at least 2 tests to compare

        # Get selected tests
        selected_tests = [self.available_tests[i] for i in selected_indices]

        # Update comparison table
        self.update_comparison_table(selected_tests)

    def update_comparison_table(self, tests: List[Dict[str, Any]]) -> None:
        """Update the comparison table with selected tests.

        Args:
            tests: List of test dictionaries to compare
        """
        # Define metrics to compare
        metrics = [
            ("Serial Number", "serial_number"),
            ("Test Date", "timestamp"),
            ("Duration (s)", "duration"),
            ("Status", "status"),
            ("Average Force (N)", "avg_force"),
            ("Max Force (N)", "max_force"),
            ("Min Force (N)", "min_force"),
        ]

        # Set table dimensions
        self.comparison_table.setRowCount(len(metrics))
        self.comparison_table.setColumnCount(len(tests) + 1)

        # Set headers
        headers = ["Metric"] + [t["serial_number"] for t in tests]
        self.comparison_table.setHorizontalHeaderLabels(headers)

        # Populate table
        for row_idx, (metric_name, metric_key) in enumerate(metrics):
            # Metric name
            metric_item = QTableWidgetItem(metric_name)
            metric_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            metric_item.setFont(QFont("", 10, QFont.Weight.Bold))
            self.comparison_table.setItem(row_idx, 0, metric_item)

            # Values for each test
            for col_idx, test in enumerate(tests):
                value = test.get(metric_key, "N/A")

                # Format value
                if isinstance(value, float):
                    value_str = f"{value:.2f}"
                else:
                    value_str = str(value)

                value_item = QTableWidgetItem(value_str)
                value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.comparison_table.setItem(row_idx, col_idx + 1, value_item)

    def clear_comparison(self) -> None:
        """Clear the comparison table and selections."""
        self.test1_combo.setCurrentIndex(0)
        self.test2_combo.setCurrentIndex(0)
        self.test3_combo.setCurrentIndex(0)
        self.comparison_table.setRowCount(0)
        self.comparison_table.setColumnCount(0)