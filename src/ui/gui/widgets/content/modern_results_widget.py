"""
Modern Results Widget

Beautiful card-based results display with data visualization.
"""

from typing import Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
)

from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.svg_icon_provider import get_svg_icon_provider


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
            # Title bar with actions
            title_bar = QHBoxLayout()

            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
            """)
            title_bar.addWidget(title_label)
            title_bar.addStretch()

            self.action_layout = QHBoxLayout()
            title_bar.addLayout(self.action_layout)

            self.main_layout.addLayout(title_bar)

    def add_widget(self, widget):
        """Add widget to card"""
        self.main_layout.addWidget(widget)

    def add_action_button(self, icon_name: str, tooltip: str):
        """Add action button to title bar"""
        svg_provider = get_svg_icon_provider()
        btn = QPushButton()
        icon = svg_provider.get_icon(icon_name, size=18, color="#cccccc")
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(QSize(18, 18))
        btn.setToolTip(tooltip)
        btn.setFixedSize(36, 36)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: #2196F3;
            }
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_layout.addWidget(btn)
        return btn


class ModernResultsWidget(QWidget):
    """
    Modern results widget with Material Design 3.
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
        """Setup modern results UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Apply dark background
        self.setStyleSheet("""
            ModernResultsWidget {
                background-color: #1e1e1e;
            }
        """)

        # Statistics cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        total_card = StatCard("Total Tests", "127", "check_circle", "#00D9A5")
        passed_card = StatCard("Passed", "120", "check_circle", "#00D9A5")
        failed_card = StatCard("Failed", "7", "x_circle", "#F44336")
        rate_card = StatCard("Pass Rate", "94.5%", "statistics", "#2196F3")

        stats_layout.addWidget(total_card)
        stats_layout.addWidget(passed_card)
        stats_layout.addWidget(failed_card)
        stats_layout.addWidget(rate_card)

        main_layout.addLayout(stats_layout)

        # Search and Filter bar
        toolbar_card = self.create_toolbar()
        main_layout.addWidget(toolbar_card)

        # Results table card
        table_card = self.create_table_card()
        main_layout.addWidget(table_card)

    def create_toolbar(self) -> QWidget:
        """Create search and filter toolbar"""
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Search box
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Search results...")
        search_edit.setFixedHeight(40)
        search_edit.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 0 16px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                background-color: rgba(33, 150, 243, 0.1);
            }
        """)

        svg_provider = get_svg_icon_provider()
        search_icon = svg_provider.get_icon("search", size=18, color="#999999")
        if not search_icon.isNull():
            search_edit.addAction(search_icon, QLineEdit.ActionPosition.LeadingPosition)

        layout.addWidget(search_edit)

        # Filter button
        filter_btn = self.create_icon_button("filter", "Filter results")
        layout.addWidget(filter_btn)

        # Refresh button
        refresh_btn = self.create_icon_button("refresh_cw", "Refresh")
        layout.addWidget(refresh_btn)

        # Export button
        export_btn = self.create_icon_button("download", "Export to CSV")
        layout.addWidget(export_btn)

        return toolbar

    def create_icon_button(self, icon_name: str, tooltip: str) -> QPushButton:
        """Create icon button"""
        svg_provider = get_svg_icon_provider()
        btn = QPushButton()
        icon = svg_provider.get_icon(icon_name, size=20, color="#cccccc")
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
        btn.setToolTip(tooltip)
        btn.setFixedSize(40, 40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.2);
                border-color: #2196F3;
            }
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def create_table_card(self) -> ModernCard:
        """Create results table card"""
        card = ModernCard("📊 Test Results")

        # Add action buttons
        card.add_action_button("refresh_cw", "Refresh")
        card.add_action_button("download", "Export")

        # Create table
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Serial Number", "Test Type", "Result", "Force (N)", "Timestamp", "Duration"
        ])

        # Sample data
        sample_data = [
            ("SN-001234", "Force Test", "✓ Pass", "48.5", "2025-01-15 14:30", "2.5s"),
            ("SN-001235", "Force Test", "✓ Pass", "49.2", "2025-01-15 14:35", "2.4s"),
            ("SN-001236", "Heating Test", "✗ Fail", "35.1", "2025-01-15 14:40", "3.1s"),
            ("SN-001237", "Force Test", "✓ Pass", "50.1", "2025-01-15 14:45", "2.3s"),
            ("SN-001238", "Force Test", "✓ Pass", "47.8", "2025-01-15 14:50", "2.6s"),
        ]

        table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Color code results
                if col == 2:  # Result column
                    if "Pass" in value:
                        item.setForeground(Qt.GlobalColor.green)
                    else:
                        item.setForeground(Qt.GlobalColor.red)

                table.setItem(row, col, item)

        # Table styling
        table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                color: #ffffff;
                gridline-color: rgba(255, 255, 255, 0.1);
                selection-background-color: rgba(33, 150, 243, 0.3);
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QHeaderView::section {
                background-color: rgba(255, 255, 255, 0.05);
                color: #cccccc;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #2196F3;
                font-weight: 600;
                font-size: 13px;
            }
        """)

        # Resize columns
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        card.add_widget(table)

        return card