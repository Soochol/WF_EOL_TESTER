"""Results Header Controls

Advanced header controls for results analysis and data export.
"""

# Standard library imports
from typing import Optional, List, Dict, Any

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDateEdit,
    QSpinBox,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class ResultsHeaderControls(QWidget):
    """Advanced header controls for results analysis.
    
    Provides filtering, analysis, and export capabilities for test results.
    """
    
    # Signals
    filter_changed = Signal(dict)  # Emitted when filters change
    export_requested = Signal(str)  # Emitted when export is requested
    analysis_requested = Signal(str)  # Emitted when analysis is requested
    
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
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title section
        title_layout = self.create_title_section()
        main_layout.addLayout(title_layout)
        
        # Controls section
        controls_layout = self.create_controls_section()
        main_layout.addLayout(controls_layout)
        
    def create_title_section(self) -> QHBoxLayout:
        """Create the title section with page title and summary stats."""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Page title
        title_label = QLabel("Test Results Analysis")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Add stretch to push summary to the right
        layout.addStretch()
        
        # Summary statistics
        self.summary_label = QLabel("Total Tests: 0 | Passed: 0 | Failed: 0")
        summary_font = QFont()
        summary_font.setPointSize(11)
        self.summary_label.setFont(summary_font)
        self.summary_label.setStyleSheet(
            "color: #cccccc; background-color: #2d2d2d; "
            "padding: 6px 12px; border-radius: 4px;"
        )
        layout.addWidget(self.summary_label)
        
        return layout
        
    def create_controls_section(self) -> QHBoxLayout:
        """Create the controls section with filters and actions."""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Filter group
        filter_group = self.create_filter_group()
        layout.addWidget(filter_group)
        
        # Analysis group
        analysis_group = self.create_analysis_group()
        layout.addWidget(analysis_group)
        
        # Export group
        export_group = self.create_export_group()
        layout.addWidget(export_group)
        
        # Add stretch to fill remaining space
        layout.addStretch()
        
        return layout
        
    def create_filter_group(self) -> QGroupBox:
        """Create filter controls group."""
        group = QGroupBox("Filters")
        group.setStyleSheet(
            "QGroupBox { "
            "    font-weight: bold; "
            "    color: #ffffff; "
            "    border: 1px solid #404040; "
            "    border-radius: 6px; "
            "    margin-top: 8px; "
            "    padding-top: 5px; "
            "} "
            "QGroupBox::title { "
            "    subcontrol-origin: margin; "
            "    left: 10px; "
            "    padding: 0 8px 0 8px; "
            "    background-color: #1e1e1e; "
            "}"
        )
        
        layout = QHBoxLayout(group)
        layout.setSpacing(8)
        
        # Test type filter
        type_label = QLabel("Type:")
        type_label.setStyleSheet("color: #cccccc; font-weight: normal;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All", "Force Test", "Temperature Test", "MCU Test"])
        self.type_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)
        
        # Status filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: #cccccc; font-weight: normal;")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Passed", "Failed", "Aborted"])
        self.status_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(status_label)
        layout.addWidget(self.status_combo)
        
        # Date range
        date_label = QLabel("Days:")
        date_label.setStyleSheet("color: #cccccc; font-weight: normal;")
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        self.days_spin.setSuffix(" days")
        self.days_spin.valueChanged.connect(self.on_filter_changed)
        layout.addWidget(date_label)
        layout.addWidget(self.days_spin)
        
        return group
        
    def create_analysis_group(self) -> QGroupBox:
        """Create analysis controls group."""
        group = QGroupBox("Analysis")
        group.setStyleSheet(
            "QGroupBox { "
            "    font-weight: bold; "
            "    color: #ffffff; "
            "    border: 1px solid #404040; "
            "    border-radius: 6px; "
            "    margin-top: 8px; "
            "    padding-top: 5px; "
            "} "
            "QGroupBox::title { "
            "    subcontrol-origin: margin; "
            "    left: 10px; "
            "    padding: 0 8px 0 8px; "
            "    background-color: #1e1e1e; "
            "}"
        )
        
        layout = QHBoxLayout(group)
        layout.setSpacing(8)
        
        # Statistics button
        stats_btn = QPushButton("Statistics")
        stats_btn.setToolTip("Show detailed statistics and trends")
        stats_btn.clicked.connect(lambda: self.analysis_requested.emit("statistics"))
        layout.addWidget(stats_btn)
        
        # Trends button
        trends_btn = QPushButton("Trends")
        trends_btn.setToolTip("Analyze test trends over time")
        trends_btn.clicked.connect(lambda: self.analysis_requested.emit("trends"))
        layout.addWidget(trends_btn)
        
        # Compare button
        compare_btn = QPushButton("Compare")
        compare_btn.setToolTip("Compare test results")
        compare_btn.clicked.connect(lambda: self.analysis_requested.emit("compare"))
        layout.addWidget(compare_btn)
        
        return group
        
    def create_export_group(self) -> QGroupBox:
        """Create export controls group."""
        group = QGroupBox("Export")
        group.setStyleSheet(
            "QGroupBox { "
            "    font-weight: bold; "
            "    color: #ffffff; "
            "    border: 1px solid #404040; "
            "    border-radius: 6px; "
            "    margin-top: 8px; "
            "    padding-top: 5px; "
            "} "
            "QGroupBox::title { "
            "    subcontrol-origin: margin; "
            "    left: 10px; "
            "    padding: 0 8px 0 8px; "
            "    background-color: #1e1e1e; "
            "}"
        )
        
        layout = QHBoxLayout(group)
        layout.setSpacing(8)
        
        # Export format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet("color: #cccccc; font-weight: normal;")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "Excel", "PDF", "JSON"])
        layout.addWidget(format_label)
        layout.addWidget(self.format_combo)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.setToolTip("Export filtered results")
        export_btn.clicked.connect(self.on_export_clicked)
        layout.addWidget(export_btn)
        
        return group
        
    def on_filter_changed(self) -> None:
        """Handle filter changes."""
        filters = {
            "type": self.type_combo.currentText(),
            "status": self.status_combo.currentText(),
            "days": self.days_spin.value(),
        }
        self.filter_changed.emit(filters)
        
    def on_export_clicked(self) -> None:
        """Handle export button click."""
        format_type = self.format_combo.currentText().lower()
        self.export_requested.emit(format_type)
        
    def update_summary(self, total: int, passed: int, failed: int) -> None:
        """Update summary statistics display."""
        self.summary_label.setText(
            f"Total Tests: {total} | Passed: {passed} | Failed: {failed}"
        )
        
    def get_current_filters(self) -> Dict[str, Any]:
        """Get current filter settings."""
        return {
            "type": self.type_combo.currentText(),
            "status": self.status_combo.currentText(),
            "days": self.days_spin.value(),
        }
        
    def reset_filters(self) -> None:
        """Reset all filters to default values."""
        self.type_combo.setCurrentText("All")
        self.status_combo.setCurrentText("All")
        self.days_spin.setValue(30)
