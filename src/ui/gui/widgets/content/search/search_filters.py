"""
Search Filters Panel

UI for filtering database search results.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from ui.gui.styles.common_styles import (
    BACKGROUND_MEDIUM,
    BORDER_DEFAULT,
    BORDER_FOCUS,
    get_button_style,
    get_groupbox_style,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class SearchFiltersPanel(QWidget):
    """
    Search filters panel for database queries.

    Signals:
        search_requested: Emitted when search button is clicked
        filters_cleared: Emitted when clear button is clicked
        delete_requested: Emitted when delete button is clicked
    """

    search_requested = Signal(dict)  # filters dict
    filters_cleared = Signal()
    delete_requested = Signal()  # Delete button clicked

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the filters UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Group box for filters
        filter_group = QGroupBox("Search Filters")
        filter_group.setStyleSheet(get_groupbox_style())
        group_layout = QVBoxLayout(filter_group)
        group_layout.setSpacing(15)

        # Row 1: Serial Number + Date Range
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)

        # Serial Number
        serial_label = QLabel("Serial Number:")
        serial_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 500;")
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Enter serial number (partial match)...")
        self.serial_input.setMinimumWidth(200)
        self.serial_input.setStyleSheet(self._get_lineedit_style())

        row1_layout.addWidget(serial_label)
        row1_layout.addWidget(self.serial_input)
        row1_layout.addSpacing(30)

        # Start Date
        # Third-party imports
        from PySide6.QtCore import QDate

        start_label = QLabel("Start Date:")
        start_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 500;")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setStyleSheet(self._get_dateedit_style())

        row1_layout.addWidget(start_label)
        row1_layout.addWidget(self.start_date)

        # End Date
        end_label = QLabel("End Date:")
        end_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 500;")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setStyleSheet(self._get_dateedit_style())

        row1_layout.addWidget(end_label)
        row1_layout.addWidget(self.end_date)
        row1_layout.addStretch()

        group_layout.addLayout(row1_layout)

        # Row 2: Buttons only (Status filter removed - not available in raw_measurements)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)

        # Search button
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.setStyleSheet(get_button_style())
        self.search_btn.clicked.connect(self._on_search_clicked)

        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet(self._get_clear_button_style())
        self.clear_btn.clicked.connect(self._on_clear_clicked)

        # Delete Selected button
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.setStyleSheet(self._get_delete_button_style())
        self.delete_btn.setEnabled(False)  # Initially disabled
        self.delete_btn.clicked.connect(self._on_delete_clicked)

        row2_layout.addWidget(self.search_btn)
        row2_layout.addWidget(self.clear_btn)
        row2_layout.addWidget(self.delete_btn)
        row2_layout.addStretch()

        group_layout.addLayout(row2_layout)

        layout.addWidget(filter_group)

    def _on_search_clicked(self) -> None:
        """Handle search button click"""
        filters = self.get_filters()
        self.search_requested.emit(filters)

    def _on_clear_clicked(self) -> None:
        """Handle clear button click"""
        # Third-party imports
        from PySide6.QtCore import QDate

        self.serial_input.clear()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())
        # status_combo removed - not available in raw_measurements
        self.filters_cleared.emit()

    def _on_delete_clicked(self) -> None:
        """Handle delete button click"""
        self.delete_requested.emit()

    def get_filters(self) -> Dict:
        """Get current filter values"""
        return {
            "serial_number": self.serial_input.text().strip() or None,
            "start_date": self.start_date.date().toPython(),
            "end_date": self.end_date.date().toPython(),
            # Status filter removed - not available in raw_measurements
        }

    def _get_lineedit_style(self) -> str:
        """Get line edit stylesheet"""
        return f"""
        QLineEdit {{
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_SECONDARY};
            border: 1px solid {BORDER_DEFAULT};
            border-radius: 4px;
            padding: 6px 12px;
            min-height: 28px;
            font-size: 13px;
        }}
        QLineEdit:hover {{
            border-color: {BORDER_FOCUS};
        }}
        QLineEdit:focus {{
            border-color: {BORDER_FOCUS};
            outline: none;
        }}
        """

    def _get_dateedit_style(self) -> str:
        """Get date edit stylesheet"""
        return f"""
        QDateEdit {{
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_SECONDARY};
            border: 1px solid {BORDER_DEFAULT};
            border-radius: 4px;
            padding: 6px 12px;
            min-height: 28px;
            min-width: 120px;
        }}
        QDateEdit:hover {{
            border-color: {BORDER_FOCUS};
        }}
        QDateEdit:focus {{
            border-color: {BORDER_FOCUS};
            outline: none;
        }}
        QDateEdit::drop-down {{
            border: none;
            width: 20px;
        }}
        QDateEdit::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {TEXT_SECONDARY};
            margin-right: 5px;
        }}
        """

    def _get_clear_button_style(self) -> str:
        """Get clear button stylesheet"""
        return f"""
        QPushButton {{
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_SECONDARY};
            border: 1px solid {BORDER_DEFAULT};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
            min-width: 80px;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {BORDER_DEFAULT};
            color: {TEXT_PRIMARY};
        }}
        QPushButton:pressed {{
            background-color: {BORDER_DEFAULT};
        }}
        """

    def _get_delete_button_style(self) -> str:
        """Get delete button stylesheet (red/warning style)"""
        return f"""
            QPushButton {{
                background-color: #8B0000;  /* Dark red */
                color: {TEXT_PRIMARY};
                border: 1px solid #A52A2A;  /* Brown-red border */
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: #A52A2A;  /* Lighter red on hover */
                border-color: #CD5C5C;
            }}
            QPushButton:pressed {{
                background-color: #660000;  /* Darker red when pressed */
            }}
            QPushButton:disabled {{
                background-color: {BACKGROUND_MEDIUM};
                color: {TEXT_SECONDARY};
                border-color: {BORDER_DEFAULT};
            }}
        """

    def set_delete_button_enabled(self, enabled: bool) -> None:
        """Enable or disable the delete button"""
        self.delete_btn.setEnabled(enabled)
