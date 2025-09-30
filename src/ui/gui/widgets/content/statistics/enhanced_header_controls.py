"""Enhanced Statistics Header Controls

Sticky header with comprehensive filtering for statistics analysis.
Includes data source scanning, quick date presets, and shared filters.
"""

# Standard library imports
import glob
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Third-party imports
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class EnhancedStatisticsHeaderControls(QFrame):
    """Enhanced header controls with data source scanning and quick filters.

    Features:
    - Data source folder scanning (logs/test_results/json)
    - Quick date range presets (Last 7D, Last 30D, All Time, etc.)
    - Custom date range picker
    - Test status filter (All, Passed, Failed)
    - Serial number search
    - Force range filter
    - Filter summary display
    - Apply/Reset/Export actions
    """

    # Signals
    filter_changed = Signal(dict)  # Emitted when filters change
    refresh_requested = Signal()  # Emitted when refresh is clicked
    export_requested = Signal(str)  # Emitted with export format (PDF, CSV, Excel)

    def __init__(
        self,
        data_folder: str = "logs/test_results/json",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.data_folder = data_folder
        self.total_files = 0
        self.available_date_range = (None, None)
        self.current_preset = "All Time"

        self.setup_ui()
        self.scan_data_folder()

    def setup_ui(self) -> None:
        """Setup the enhanced header UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Modern card styling for header
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)

        # Title and data source
        main_layout.addWidget(self.create_title_section())

        # Quick date presets
        main_layout.addWidget(self.create_date_presets_section())

        # Custom date range
        main_layout.addWidget(self.create_custom_date_section())

        # Additional filters
        main_layout.addWidget(self.create_filters_section())

        # Summary and actions
        main_layout.addWidget(self.create_summary_actions_section())

    def create_title_section(self) -> QWidget:
        """Create title and data source info section."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title_label = QLabel("📊 Statistics Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; padding: 5px;")
        layout.addWidget(title_label)

        # Data source info
        self.data_source_label = QLabel(f"📁 Data Source: {self.data_folder}")
        self.data_source_label.setStyleSheet(
            "color: #cccccc; font-size: 12px; padding: 3px;"
        )
        layout.addWidget(self.data_source_label)

        # Files info
        self.files_info_label = QLabel("Scanning...")
        self.files_info_label.setStyleSheet(
            "color: #aaaaaa; font-size: 11px; padding: 3px;"
        )
        layout.addWidget(self.files_info_label)

        return widget

    def create_date_presets_section(self) -> QGroupBox:
        """Create quick date range preset buttons."""
        group = QGroupBox("📅 Quick Date Filters")
        group.setStyleSheet(self._get_group_style())

        layout = QHBoxLayout(group)
        layout.setSpacing(8)

        # Quick preset buttons
        presets = [
            ("All Time", "all_time"),
            ("Last 7 Days", "last_7d"),
            ("Last 30 Days", "last_30d"),
            ("This Week", "this_week"),
            ("This Month", "this_month"),
            ("Last Month", "last_month"),
        ]

        self.preset_buttons = {}
        for label, preset_id in presets:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, p=preset_id: self.on_preset_clicked(p))
            btn.setStyleSheet(self._get_preset_button_style())
            layout.addWidget(btn)
            self.preset_buttons[preset_id] = btn

        # Set "All Time" as default
        self.preset_buttons["all_time"].setChecked(True)

        return group

    def create_custom_date_section(self) -> QGroupBox:
        """Create custom date range picker."""
        group = QGroupBox("📆 Custom Date Range")
        group.setStyleSheet(self._get_group_style())

        layout = QHBoxLayout(group)
        layout.setSpacing(12)

        # From date
        from_label = QLabel("From:")
        from_label.setStyleSheet("color: #cccccc; font-weight: 500;")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        start_py_date = (datetime.now() - timedelta(days=30)).date()
        self.start_date.setDate(QDate(start_py_date.year, start_py_date.month, start_py_date.day))
        self.start_date.dateChanged.connect(self.on_custom_date_changed)
        self.start_date.setStyleSheet(self._get_date_edit_style())

        # To date
        to_label = QLabel("To:")
        to_label.setStyleSheet("color: #cccccc; font-weight: 500;")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        end_py_date = datetime.now().date()
        self.end_date.setDate(QDate(end_py_date.year, end_py_date.month, end_py_date.day))
        self.end_date.dateChanged.connect(self.on_custom_date_changed)
        self.end_date.setStyleSheet(self._get_date_edit_style())

        layout.addWidget(from_label)
        layout.addWidget(self.start_date)
        layout.addWidget(to_label)
        layout.addWidget(self.end_date)
        layout.addStretch()

        return group

    def create_filters_section(self) -> QGroupBox:
        """Create additional filter controls."""
        group = QGroupBox("🔍 Additional Filters")
        group.setStyleSheet(self._get_group_style())

        layout = QHBoxLayout(group)
        layout.setSpacing(15)

        # Test Status filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: #cccccc; font-weight: 500;")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All Tests", "Passed Only", "Failed Only"])
        self.status_combo.currentTextChanged.connect(self.on_filter_changed)
        self.status_combo.setStyleSheet(self._get_combo_style())

        # Serial number filter
        serial_label = QLabel("Serial:")
        serial_label.setStyleSheet("color: #cccccc; font-weight: 500;")
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("e.g., SN001")
        self.serial_input.textChanged.connect(self.on_filter_changed)
        self.serial_input.setStyleSheet(self._get_line_edit_style())

        layout.addWidget(status_label)
        layout.addWidget(self.status_combo)
        layout.addWidget(serial_label)
        layout.addWidget(self.serial_input)
        layout.addStretch()

        return group

    def create_summary_actions_section(self) -> QWidget:
        """Create filter summary and action buttons."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Summary label
        self.summary_label = QLabel("Ready to analyze...")
        self.summary_label.setStyleSheet("""
            color: #ffffff;
            background-color: rgba(33, 150, 243, 0.2);
            border: 1px solid rgba(33, 150, 243, 0.4);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            font-weight: 500;
        """)
        layout.addWidget(self.summary_label)

        layout.addStretch()

        # Action buttons
        apply_btn = QPushButton("🔄 Apply Filters")
        apply_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_btn.clicked.connect(self.apply_filters)
        apply_btn.setStyleSheet(self._get_action_button_style("#2196F3"))

        reset_btn = QPushButton("↻ Reset")
        reset_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        reset_btn.clicked.connect(self.reset_filters)
        reset_btn.setStyleSheet(self._get_action_button_style("#757575"))

        export_btn = QPushButton("📥 Export")
        export_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        export_btn.clicked.connect(lambda: self.export_requested.emit("PDF"))
        export_btn.setStyleSheet(self._get_action_button_style("#00D9A5"))

        layout.addWidget(apply_btn)
        layout.addWidget(reset_btn)
        layout.addWidget(export_btn)

        return widget

    def scan_data_folder(self) -> None:
        """Scan data folder for JSON files and detect date range."""
        try:
            pattern = str(Path(self.data_folder) / "*.json")
            json_files = glob.glob(pattern)
            self.total_files = len(json_files)

            if self.total_files == 0:
                self.files_info_label.setText(
                    f"⚠️ No JSON files found in {self.data_folder}"
                )
                return

            # Extract date range from files
            dates = []
            for file_path in json_files[:50]:  # Sample first 50 for performance
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "start_time" in data:
                            timestamp = datetime.fromisoformat(
                                data["start_time"].replace("Z", "+00:00")
                            )
                            dates.append(timestamp.date())
                except Exception:
                    continue

            if dates:
                min_date = min(dates)
                max_date = max(dates)
                self.available_date_range = (min_date, max_date)
                self.files_info_label.setText(
                    f"✅ {self.total_files} files found | "
                    f"Date range: {min_date} to {max_date}"
                )
            else:
                self.files_info_label.setText(
                    f"✅ {self.total_files} files found | Date range: Unknown"
                )

        except Exception as e:
            self.files_info_label.setText(f"❌ Error scanning folder: {e}")

    def on_preset_clicked(self, preset_id: str) -> None:
        """Handle quick preset button click."""
        # Uncheck all other buttons
        for btn_id, btn in self.preset_buttons.items():
            btn.setChecked(btn_id == preset_id)

        self.current_preset = preset_id

        # Calculate date range based on preset
        today = datetime.now().date()
        if preset_id == "all_time":
            if self.available_date_range[0]:
                start_date = self.available_date_range[0]
                end_date = self.available_date_range[1] or today
            else:
                start_date = today - timedelta(days=365)
                end_date = today
        elif preset_id == "last_7d":
            start_date = today - timedelta(days=7)
            end_date = today
        elif preset_id == "last_30d":
            start_date = today - timedelta(days=30)
            end_date = today
        elif preset_id == "this_week":
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif preset_id == "this_month":
            start_date = today.replace(day=1)
            end_date = today
        elif preset_id == "last_month":
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            start_date = last_day_last_month.replace(day=1)
            end_date = last_day_last_month
        else:
            return

        # Update date pickers
        self.start_date.setDate(QDate(start_date.year, start_date.month, start_date.day))
        self.end_date.setDate(QDate(end_date.year, end_date.month, end_date.day))

    def on_custom_date_changed(self) -> None:
        """Handle custom date picker change."""
        # Uncheck all preset buttons
        for btn in self.preset_buttons.values():
            btn.setChecked(False)
        self.current_preset = "custom"

    def on_filter_changed(self) -> None:
        """Handle filter control change."""
        pass  # Can add auto-apply here if needed

    def apply_filters(self) -> None:
        """Apply current filters and emit signal."""
        filters = self.get_current_filters()
        self.update_summary(filters)
        self.filter_changed.emit(filters)

    def reset_filters(self) -> None:
        """Reset all filters to default."""
        # Reset to All Time preset
        self.preset_buttons["all_time"].setChecked(True)
        self.on_preset_clicked("all_time")

        # Reset other filters
        self.status_combo.setCurrentText("All Tests")
        self.serial_input.clear()

        # Apply reset filters
        self.apply_filters()

    def get_current_filters(self) -> Dict[str, Any]:
        """Get current filter settings.

        Returns:
            Dict with filter criteria
        """
        return {
            "preset": self.current_preset,
            "start_date": self.start_date.date().toPython(),
            "end_date": self.end_date.date().toPython(),
            "status": self.status_combo.currentText(),
            "serial": self.serial_input.text().strip(),
        }

    def update_summary(self, filters: Dict[str, Any]) -> None:
        """Update filter summary display.

        Args:
            filters: Current filter settings
        """
        status_map = {
            "All Tests": "All",
            "Passed Only": "Passed",
            "Failed Only": "Failed",
        }
        status = status_map.get(filters["status"], "All")

        date_range = f"{filters['start_date']} ~ {filters['end_date']}"
        serial_text = f" | Serial: {filters['serial']}" if filters['serial'] else ""

        self.summary_label.setText(
            f"📊 {status} tests | {date_range}{serial_text}"
        )

    def _get_group_style(self) -> str:
        """Get group box styling."""
        return """
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                color: #2196F3;
                border: 1px solid rgba(33, 150, 243, 0.3);
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background-color: transparent;
            }
        """

    def _get_preset_button_style(self) -> str:
        """Get preset button styling."""
        return """
            QPushButton {
                background-color: rgba(33, 150, 243, 0.1);
                color: #2196F3;
                border: 1px solid rgba(33, 150, 243, 0.3);
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.2);
            }
            QPushButton:checked {
                background-color: rgba(33, 150, 243, 0.3);
                border: 1px solid #2196F3;
                font-weight: 600;
            }
        """

    def _get_date_edit_style(self) -> str:
        """Get date edit styling."""
        return """
            QDateEdit {
                background-color: rgba(255, 255, 255, 0.05);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QDateEdit:focus {
                border: 1px solid #2196F3;
                background-color: rgba(33, 150, 243, 0.1);
            }
        """

    def _get_combo_style(self) -> str:
        """Get combo box styling."""
        return """
            QComboBox {
                background-color: rgba(255, 255, 255, 0.05);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                min-width: 120px;
            }
            QComboBox:focus {
                border: 1px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
            }
        """

    def _get_line_edit_style(self) -> str:
        """Get line edit styling."""
        return """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                min-width: 150px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
                background-color: rgba(33, 150, 243, 0.1);
            }
        """

    def _get_action_button_style(self, color: str) -> str:
        """Get action button styling."""
        return f"""
            QPushButton {{
                background-color: {color};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color)};
            }}
        """

    def _lighten_color(self, color: str) -> str:
        """Lighten a hex color."""
        # Simple lightening by adding 20 to each RGB component
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 20)
        g = min(255, g + 20)
        b = min(255, b + 20)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, color: str) -> str:
        """Darken a hex color."""
        # Simple darkening by subtracting 20 from each RGB component
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - 20)
        g = max(0, g - 20)
        b = max(0, b - 20)
        return f"#{r:02x}{g:02x}{b:02x}"