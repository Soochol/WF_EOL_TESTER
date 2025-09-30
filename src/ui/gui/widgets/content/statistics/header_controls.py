"""Statistics Header Controls

Fixed header with filtering and refresh controls for the statistics page.
"""

# Standard library imports
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Third-party imports
from PySide6.QtCore import QDate, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class StatisticsHeaderControls(QWidget):
    """Fixed header controls for statistics filtering and refresh.

    Provides:
    - Date range filtering
    - Test status filtering (All, Passed, Failed)
    - Refresh button
    - Current filter summary display
    """

    # Signals
    filter_changed = Signal(dict)  # Emitted when filters change
    refresh_requested = Signal()  # Emitted when refresh button is clicked

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

    def setup_ui(self) -> None:
        """Setup the header controls UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title section
        title_layout = self.create_title_section()
        main_layout.addLayout(title_layout)

        # Filter controls section
        filter_layout = self.create_filter_section()
        main_layout.addLayout(filter_layout)

    def create_title_section(self) -> QHBoxLayout:
        """Create the title section with page title and summary."""
        layout = QHBoxLayout()
        layout.setSpacing(15)

        # Page title (store as instance variable for dynamic updates)
        self.title_label = QLabel("EOL Force Test Statistics")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        layout.addWidget(self.title_label)

        # Add stretch to push summary to the right
        layout.addStretch()

        # Summary label
        self.summary_label = QLabel("Loading statistics...")
        summary_font = QFont()
        summary_font.setPointSize(11)
        self.summary_label.setFont(summary_font)
        self.summary_label.setStyleSheet(
            "color: #cccccc; background-color: #2d2d2d; " "padding: 6px 12px; border-radius: 4px;"
        )
        layout.addWidget(self.summary_label)

        return layout

    def create_filter_section(self) -> QHBoxLayout:
        """Create the filter controls section."""
        layout = QHBoxLayout()
        layout.setSpacing(15)

        # Date range filter group
        date_group = self.create_date_filter_group()
        layout.addWidget(date_group)

        # Status filter group
        status_group = self.create_status_filter_group()
        layout.addWidget(status_group)

        # Actions group
        actions_group = self.create_actions_group()
        layout.addWidget(actions_group)

        # Add stretch to fill remaining space
        layout.addStretch()

        return layout

    def create_date_filter_group(self) -> QGroupBox:
        """Create date range filter controls."""
        group = QGroupBox("Date Range")
        group.setStyleSheet(self._get_group_box_style())

        layout = QHBoxLayout(group)
        layout.setSpacing(8)

        # Start date
        start_label = QLabel("From:")
        start_label.setStyleSheet("color: #cccccc; font-weight: normal;")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        start_py_date = (datetime.now() - timedelta(days=30)).date()
        self.start_date.setDate(QDate(start_py_date.year, start_py_date.month, start_py_date.day))
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.dateChanged.connect(self.on_filter_changed)
        layout.addWidget(start_label)
        layout.addWidget(self.start_date)

        # End date
        end_label = QLabel("To:")
        end_label.setStyleSheet("color: #cccccc; font-weight: normal;")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        end_py_date = datetime.now().date()
        self.end_date.setDate(QDate(end_py_date.year, end_py_date.month, end_py_date.day))
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.dateChanged.connect(self.on_filter_changed)
        layout.addWidget(end_label)
        layout.addWidget(self.end_date)

        return group

    def create_status_filter_group(self) -> QGroupBox:
        """Create test status filter controls."""
        group = QGroupBox("Test Status")
        group.setStyleSheet(self._get_group_box_style())

        layout = QHBoxLayout(group)
        layout.setSpacing(8)

        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: #cccccc; font-weight: normal;")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Passed", "Failed"])
        self.status_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(status_label)
        layout.addWidget(self.status_combo)

        return group

    def create_actions_group(self) -> QGroupBox:
        """Create action buttons group."""
        group = QGroupBox("Actions")
        group.setStyleSheet(self._get_group_box_style())

        layout = QHBoxLayout(group)
        layout.setSpacing(8)

        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.setToolTip("Reload statistics from test results")
        refresh_btn.clicked.connect(self.on_refresh_clicked)
        layout.addWidget(refresh_btn)

        # Reset filters button
        reset_btn = QPushButton("Reset Filters")
        reset_btn.setToolTip("Reset all filters to default values")
        reset_btn.clicked.connect(self.reset_filters)
        layout.addWidget(reset_btn)

        return group

    def _get_group_box_style(self) -> str:
        """Get consistent group box styling."""
        return """
            QGroupBox {
                font-weight: bold;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #1e1e1e;
            }
        """

    def on_filter_changed(self) -> None:
        """Handle filter changes."""
        filters = self.get_current_filters()
        self.filter_changed.emit(filters)

    def on_refresh_clicked(self) -> None:
        """Handle refresh button click."""
        self.refresh_requested.emit()

    def get_current_filters(self) -> Dict[str, Any]:
        """Get current filter settings.

        Returns:
            Dict with keys: start_date, end_date, status
        """
        return {
            "start_date": self.start_date.date().toPython(),
            "end_date": self.end_date.date().toPython(),
            "status": self.status_combo.currentText(),
        }

    def reset_filters(self) -> None:
        """Reset all filters to default values."""
        start_py_date = (datetime.now() - timedelta(days=30)).date()
        self.start_date.setDate(QDate(start_py_date.year, start_py_date.month, start_py_date.day))
        end_py_date = datetime.now().date()
        self.end_date.setDate(QDate(end_py_date.year, end_py_date.month, end_py_date.day))
        self.status_combo.setCurrentText("All")

    def set_title(self, title: str) -> None:
        """Update the page title dynamically.

        Args:
            title: New title text to display
        """
        if hasattr(self, "title_label"):
            self.title_label.setText(title)

    def update_summary(self, total_tests: int, total_files: int) -> None:
        """Update summary statistics display.

        Args:
            total_tests: Total number of tests analyzed
            total_files: Total number of JSON files parsed
        """
        self.summary_label.setText(f"Files: {total_files} | Tests: {total_tests}")
