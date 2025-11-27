"""
Modern Dashboard Widget

Beautiful card-based dashboard with Material Design 3.
"""

from typing import Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QFrame
)
from loguru import logger

from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.svg_icon_provider import get_svg_icon_provider
from ui.gui.widgets.results_table_widget import ResultsTableWidget


class StatCard(QFrame):
    """Statistics summary card"""

    def __init__(self, title: str, value: str, icon_name: str, color: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon_name = icon_name
        self.color = color
        self.setup_ui()

    def setup_ui(self):
        """Setup stat card UI"""
        self.setFixedHeight(120)
        self.setStyleSheet(f"""
            StatCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                border-left: 4px solid {self.color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Icon and title row
        top_layout = QHBoxLayout()

        svg_provider = get_svg_icon_provider()
        icon_label = QLabel()
        icon = svg_provider.get_icon(self.icon_name, size=24, color=self.color)
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(QSize(24, 24)))
        top_layout.addWidget(icon_label)

        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 12px;
            color: #999999;
            font-weight: 500;
        """)
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        layout.addLayout(top_layout)

        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {self.color};
        """)
        layout.addWidget(self.value_label)

        layout.addStretch()

    def update_value(self, new_value: str):
        """Update the card value"""
        self.value = new_value
        self.value_label.setText(new_value)


class ModernCard(QFrame):
    """Modern glassmorphism card"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setup_ui(title)

    def setup_ui(self, title: str):
        """Setup card UI"""
        self.setStyleSheet("""
            ModernCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 20px;
            }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        if title:
            # Title bar
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
            """)
            self.main_layout.addWidget(title_label)

    def add_widget(self, widget):
        """Add widget to card"""
        self.main_layout.addWidget(widget)


class ModernDashboardWidget(QWidget):
    """
    Modern dashboard widget with Material Design 3.
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

        # Statistics cards (will be initialized in setup_ui)
        self.total_card: Optional[StatCard] = None
        self.passed_card: Optional[StatCard] = None
        self.failed_card: Optional[StatCard] = None
        self.rate_card: Optional[StatCard] = None

        self.setup_ui()
        self._connect_signals()
        self._load_today_results()  # Load today's results from disk
        self._update_statistics()  # Update display with loaded data

    def setup_ui(self):
        """Setup modern dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Apply dark background
        self.setStyleSheet("""
            ModernDashboardWidget {
                background-color: #1e1e1e;
            }
        """)

        # Statistics cards grid (2x2 layout)
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        stats_layout.setColumnStretch(0, 1)
        stats_layout.setColumnStretch(1, 1)
        stats_layout.setRowStretch(0, 0)
        stats_layout.setRowStretch(1, 0)

        self.total_card = StatCard("Total Tests", "0", "check_circle", "#2196F3")
        self.passed_card = StatCard("Passed", "0", "check_circle", "#00D9A5")
        self.failed_card = StatCard("Failed", "0", "x_circle", "#F44336")
        self.rate_card = StatCard("Pass Rate", "0%", "statistics", "#FF9800")

        # Add cards to grid: row, column
        stats_layout.addWidget(self.total_card, 0, 0)
        stats_layout.addWidget(self.passed_card, 0, 1)
        stats_layout.addWidget(self.failed_card, 1, 0)
        stats_layout.addWidget(self.rate_card, 1, 1)

        main_layout.addLayout(stats_layout)

        # Results table card
        results_card = ModernCard("Recent Results")
        self.results_table = ResultsTableWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        results_card.add_widget(self.results_table)
        main_layout.addWidget(results_card, stretch=1)

    def _connect_signals(self):
        """Connect state manager signals"""
        self.state_manager.test_result_added.connect(self._on_test_result_added)

    def _load_today_results(self):
        """Load today's test results from JSON files on startup"""
        json_dir = "logs/test_results/json"
        count = self.state_manager.load_today_results_from_disk(json_dir)
        if count > 0:
            logger.info(f"📂 Dashboard: Loaded {count} results from today's files")

    def _on_test_result_added(self, result):
        """Handle new test result added"""
        logger.info(f"📊 Dashboard: Test result added - Test ID: {result.test_id}, Status: {result.status}")
        self._update_statistics()

    def _update_statistics(self):
        """Update statistics cards from test results"""
        # Check if cards are initialized
        if not all([self.total_card, self.passed_card, self.failed_card, self.rate_card]):
            logger.warning("Dashboard: Cards not initialized yet")
            return

        # Get all test results
        test_results = self.state_manager.get_test_results()

        # Calculate statistics
        total = len(test_results)
        passed = sum(1 for r in test_results if r.status.upper() == "PASS")
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0.0

        logger.info(f"📊 Dashboard: Updating statistics - Total: {total}, Passed: {passed}, Failed: {failed}, Rate: {pass_rate:.1f}%")

        # Update cards (cards are guaranteed to be initialized by the check above)
        assert self.total_card is not None
        assert self.passed_card is not None
        assert self.failed_card is not None
        assert self.rate_card is not None

        self.total_card.update_value(str(total))
        self.passed_card.update_value(str(passed))
        self.failed_card.update_value(str(failed))
        self.rate_card.update_value(f"{pass_rate:.1f}%")