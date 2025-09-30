"""
Modern Dashboard Widget

Beautiful card-based dashboard with Material Design 3.
"""

from typing import Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame
)

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
        value_label = QLabel(self.value)
        value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {self.color};
        """)
        layout.addWidget(value_label)

        layout.addStretch()


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

        self.setup_ui()

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

        # Statistics cards row (4 cards)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        total_card = StatCard("Total Tests", "127", "check_circle", "#2196F3")
        passed_card = StatCard("Passed", "120", "check_circle", "#00D9A5")
        failed_card = StatCard("Failed", "7", "x_circle", "#F44336")
        rate_card = StatCard("Pass Rate", "94.5%", "statistics", "#FF9800")

        stats_layout.addWidget(total_card)
        stats_layout.addWidget(passed_card)
        stats_layout.addWidget(failed_card)
        stats_layout.addWidget(rate_card)

        main_layout.addLayout(stats_layout)

        # Results table card
        results_card = ModernCard("Recent Results")
        self.results_table = ResultsTableWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        results_card.add_widget(self.results_table)
        main_layout.addWidget(results_card, stretch=1)