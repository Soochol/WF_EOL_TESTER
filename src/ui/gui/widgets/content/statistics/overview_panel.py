"""Overview Statistics Panel

Displays summary statistics for all EOL force tests.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class StatCard(QWidget):
    """A statistics card widget with a value label."""

    value_label: QLabel


class OverviewPanel(QWidget):
    """Overview statistics panel displaying key metrics.

    Shows:
    - Total number of tests
    - Pass rate percentage
    - Average test duration
    - Average force values
    """

    total_tests_label: StatCard
    pass_rate_label: StatCard
    avg_duration_label: StatCard
    avg_force_label: StatCard

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the overview panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Modern title
        title_label = QLabel("📊 Test Overview Summary")
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

        # Statistics grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        stats_layout.setHorizontalSpacing(40)

        # Create modern stat cards with Material Design 3 colors
        self.total_tests_label = self.create_stat_card("Total Tests", "0", "#2196F3")
        self.pass_rate_label = self.create_stat_card("Pass Rate", "0%", "#00D9A5")
        self.avg_duration_label = self.create_stat_card("Avg Duration", "0.0s", "#FF9800")
        self.avg_force_label = self.create_stat_card("Avg Force", "0.0N", "#9C27B0")

        # Add to grid (2x2)
        stats_layout.addWidget(self.total_tests_label, 0, 0)
        stats_layout.addWidget(self.pass_rate_label, 0, 1)
        stats_layout.addWidget(self.avg_duration_label, 1, 0)
        stats_layout.addWidget(self.avg_force_label, 1, 1)

        main_layout.addLayout(stats_layout)
        main_layout.addStretch()

    def create_stat_card(self, label: str, value: str, color: str) -> StatCard:
        """Create a statistics card widget.

        Args:
            label: Stat label (e.g., "Total Tests")
            value: Initial value
            color: Border color for the card

        Returns:
            StatCard containing the stat card
        """
        card = StatCard()
        card.setStyleSheet(
            f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                border-left: 4px solid {color};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)

        # Label
        label_widget = QLabel(label)
        label_font = QFont()
        label_font.setPointSize(10)
        label_widget.setFont(label_font)
        label_widget.setStyleSheet(f"color: {color}; font-weight: bold;")
        layout.addWidget(label_widget)

        # Value
        value_widget = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_widget.setFont(value_font)
        value_widget.setStyleSheet("color: #ffffff;")
        value_widget.setObjectName(f"{label}_value")
        layout.addWidget(value_widget)

        # Store reference for easy access
        setattr(card, "value_label", value_widget)

        return card

    def update_statistics(self, stats: Dict[str, Any]) -> None:
        """Update the overview statistics display.

        Args:
            stats: Dictionary containing:
                - total_tests: int
                - pass_rate: float (0-100)
                - avg_duration: float (seconds)
                - avg_force: float (Newtons)
        """
        # Update total tests
        total = stats.get("total_tests", 0)
        self.total_tests_label.value_label.setText(str(total))

        # Update pass rate
        pass_rate = stats.get("pass_rate", 0.0)
        self.pass_rate_label.value_label.setText(f"{pass_rate:.1f}%")

        # Update average duration
        avg_duration = stats.get("avg_duration", 0.0)
        self.avg_duration_label.value_label.setText(f"{avg_duration:.1f}s")

        # Update average force (handle both avg_force and avg_max_force keys)
        avg_force = stats.get("avg_force", stats.get("avg_max_force", 0.0))
        self.avg_force_label.value_label.setText(f"{avg_force:.2f}N")
