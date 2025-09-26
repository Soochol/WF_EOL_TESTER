"""
Logs Widget

Logs viewer page with log display and controls.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.widgets.log_viewer_widget import LogViewerWidget


class LogsWidget(QWidget):
    """
    Logs widget for viewing system logs.

    Provides log filtering, clearing, saving, and pause functionality.
    """

    log_cleared = Signal()
    log_saved = Signal(str)  # Emits file path
    log_paused = Signal(bool)  # Emits pause state

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.is_paused = False
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the logs UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header with controls
        header_group = self.create_header_group()
        main_layout.addWidget(header_group)

        # Log viewer
        self.log_viewer = LogViewerWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        main_layout.addWidget(self.log_viewer)

        # Apply styling
        self.setStyleSheet(self._get_widget_style())

    def create_header_group(self) -> QGroupBox:
        """Create header group with log controls"""
        group = QGroupBox("System Logs")
        group.setFont(self._get_group_font())
        layout = QHBoxLayout(group)
        layout.setSpacing(10)

        # Log level filter
        layout.addWidget(QLabel("Log Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["All", "INFO", "WARN", "ERROR", "DEBUG"])
        self.level_combo.setCurrentText("All")
        self.level_combo.currentTextChanged.connect(self._on_level_changed)
        layout.addWidget(self.level_combo)

        # Stretch to separate controls
        layout.addStretch()

        # Control buttons
        self.clear_btn = QPushButton("🗑️ CLEAR")
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        layout.addWidget(self.clear_btn)

        self.save_btn = QPushButton("💾 SAVE")
        self.save_btn.clicked.connect(self._on_save_clicked)
        layout.addWidget(self.save_btn)

        self.pause_btn = QPushButton("⏸ PAUSE")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        layout.addWidget(self.pause_btn)

        return group

    def _on_level_changed(self, level: str) -> None:
        """Handle log level filter change"""
        self.log_viewer.set_log_level_filter(level)

    def _on_clear_clicked(self) -> None:
        """Handle clear button click"""
        reply = QMessageBox.question(
            self,
            "Clear Logs",
            "Are you sure you want to clear all logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.log_viewer.clear_logs()
            self.log_cleared.emit()

    def _on_save_clicked(self) -> None:
        """Handle save button click"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Logs",
            "system_logs.txt",
            "Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                self.log_viewer.save_logs(file_path)
                self.log_saved.emit(file_path)
                QMessageBox.information(self, "Save Successful", f"Logs saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Failed", f"Failed to save logs:\n{str(e)}")

    def _on_pause_clicked(self) -> None:
        """Handle pause button click"""
        self.is_paused = not self.is_paused
        self.pause_btn.setText("▶ RESUME" if self.is_paused else "⏸ PAUSE")
        self.log_viewer.set_paused(self.is_paused)
        self.log_paused.emit(self.is_paused)

    def _get_group_font(self) -> QFont:
        """Get font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def _get_widget_style(self) -> str:
        """Get widget stylesheet"""
        return """
        LogsWidget {
            background-color: #1e1e1e;
            color: #cccccc;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #404040;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QLabel {
            color: #cccccc;
            font-size: 14px;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: 1px solid #106ebe;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
            min-width: 80px;
            min-height: 30px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QPushButton:checked {
            background-color: #cc6600;
            border-color: #aa5500;
        }
        QComboBox {
            background-color: #2d2d2d;
            color: #cccccc;
            border: 1px solid #404040;
            border-radius: 3px;
            padding: 5px;
            min-width: 80px;
            min-height: 25px;
        }
        QComboBox:hover {
            border-color: #0078d4;
        }
        """
