"""
Log Event Handlers

Separate event handling logic for log widget operations.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QWidget,
)

# Local application imports
from ui.gui.widgets.log_viewer_widget import LogViewerWidget


class LogEventHandler(QObject):
    """
    Handles events for log widget operations.
    
    Separates event handling logic from UI components for better maintainability.
    """
    
    # Signals to communicate with parent widget
    log_cleared = Signal()
    log_saved = Signal(str)  # Emits file path
    log_paused = Signal(bool)  # Emits pause state
    
    def __init__(self, log_viewer: LogViewerWidget, parent_widget: QWidget):
        super().__init__()
        self.log_viewer = log_viewer
        self.parent_widget = parent_widget
        self.is_paused = False
    
    def handle_level_changed(self, level: str) -> None:
        """
        Handle log level filter change.
        
        Args:
            level: Selected log level (All, INFO, WARN, ERROR, DEBUG)
        """
        self.log_viewer.set_log_level_filter(level)
    
    def handle_clear_clicked(self) -> None:
        """
        Handle clear button click with confirmation dialog.
        """
        reply = QMessageBox.question(
            self.parent_widget,
            "Clear Logs",
            "Are you sure you want to clear all logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log_viewer.clear_logs()
            self.log_cleared.emit()
    
    def handle_save_clicked(self) -> None:
        """
        Handle save button click with file dialog and error handling.
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent_widget,
            "Save Logs",
            "system_logs.txt",
            "Text Files (*.txt);;All Files (*)",
        )
        
        if file_path:
            try:
                self.log_viewer.save_logs(file_path)
                self.log_saved.emit(file_path)
                QMessageBox.information(
                    self.parent_widget,
                    "Save Successful",
                    f"Logs saved to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.parent_widget,
                    "Save Failed",
                    f"Failed to save logs:\n{str(e)}"
                )
    
    def handle_pause_toggled(self, paused: bool) -> None:
        """
        Handle pause button toggle.
        
        Args:
            paused: True if logging should be paused, False to resume
        """
        self.is_paused = paused
        self.log_viewer.set_paused(paused)
        self.log_paused.emit(paused)
    
    def get_pause_state(self) -> bool:
        """
        Get current pause state.
        
        Returns:
            True if logging is paused, False otherwise
        """
        return self.is_paused


class LogEventHandlerFactory:
    """
    Factory for creating log event handlers.
    """
    
    @staticmethod
    def create_handler(
        log_viewer: LogViewerWidget,
        parent_widget: QWidget
    ) -> LogEventHandler:
        """
        Create a configured log event handler.
        
        Args:
            log_viewer: The log viewer widget to control
            parent_widget: Parent widget for dialogs
            
        Returns:
            Configured LogEventHandler instance
        """
        return LogEventHandler(log_viewer, parent_widget)
