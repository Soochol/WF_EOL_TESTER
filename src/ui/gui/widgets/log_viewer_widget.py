"""
Log Viewer Widget

Widget for displaying system logs with filtering and controls.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class LogViewerWidget(QWidget):
    """
    Log viewer widget for displaying system logs.

    Features:
    - Real-time log display
    - Color-coded log levels
    - Auto-scroll functionality
    - Log level filtering
    - Save and clear operations
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
        self.current_filter = "INFO"
        self.is_paused = False
        self.auto_scroll = True
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self) -> None:
        """Setup the log viewer UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Debug level controls
        controls_layout = self._setup_debug_level_controls()
        layout.addLayout(controls_layout)

        # Log display area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(self._get_monospace_font())
        self.log_display.setStyleSheet(self._get_log_display_style())

        layout.addWidget(self.log_display)

        # Initialize with existing logs
        self._populate_existing_logs()

    def connect_signals(self) -> None:
        """Connect to state manager signals"""
        self.state_manager.log_message_received.connect(self._on_log_message_received)

    def _get_monospace_font(self) -> QFont:
        """Get monospace font for log display"""
        font = QFont("Consolas, Monaco, monospace")
        font.setPointSize(14)
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        return font

    def _get_log_display_style(self) -> str:
        """Get stylesheet for log display"""
        return """
        QTextEdit {
            background-color: #1a1a1a;
            color: #cccccc;
            border: 1px solid #404040;
            selection-background-color: #0078d4;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        """

    def _populate_existing_logs(self) -> None:
        """Populate with existing log messages"""
        existing_logs = self.state_manager.get_log_messages()
        for log_entry in existing_logs:
            self._add_log_entry(
                log_entry["level"],
                log_entry["component"],
                log_entry["message"],
                log_entry["timestamp"],
            )

    def _on_log_message_received(self, level: str, component: str, message: str) -> None:
        """Handle new log message"""
        if not self.is_paused and self._should_display_log(level):
            # Standard library imports
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self._add_log_entry(level, component, message, timestamp)

    def _should_display_log(self, level: str) -> bool:
        """Check if log should be displayed based on current filter"""
        if self.current_filter == "DEBUG":
            # DEBUG mode: Show ALL log levels
            return True
        elif self.current_filter == "INFO":
            # INFO mode: Show all except DEBUG level
            return level in ["CRITICAL", "ERROR", "WARN", "INFO"]
        return True

    def _add_log_entry(self, level: str, component: str, message: str, timestamp: str) -> None:
        """Add a log entry to the display"""
        # Format log entry
        log_line = f"{timestamp} [{level.ljust(5)}] {component.upper()} | {message}"

        # Get color for log level
        color = self._get_level_color(level)

        # Add to display with color
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Insert colored text
        cursor.insertHtml(f'<span style="color: {color};">{log_line}</span><br>')

        # Auto-scroll to bottom if enabled
        if self.auto_scroll:
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _setup_debug_level_controls(self) -> QHBoxLayout:
        """Setup debug level control widgets"""
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 10)

        # Debug level label
        level_label = QLabel("Debug Level:")
        level_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-weight: bold;
                font-size: 14px;
                margin-right: 10px;
            }
        """)

        # Debug level combo box
        self.level_combo = QComboBox()
        self.level_combo.addItems(["DEBUG", "INFO"])
        self.level_combo.setCurrentText("INFO")
        self.level_combo.setMinimumWidth(120)
        self.level_combo.setStyleSheet(self._get_combo_box_style())

        # Connect combo box signal
        self.level_combo.currentTextChanged.connect(self._on_debug_level_changed)

        # Add widgets to layout
        controls_layout.addWidget(level_label)
        controls_layout.addWidget(self.level_combo)
        controls_layout.addStretch()  # Push controls to the left

        return controls_layout

    def _on_debug_level_changed(self, level: str) -> None:
        """Handle debug level combo box change"""
        self.set_log_level_filter(level)

    def _get_combo_box_style(self) -> str:
        """Get stylesheet for combo box"""
        return """
        QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 4px 8px;
            color: #cccccc;
            font-size: 14px;
            min-height: 20px;
        }
        QComboBox:hover {
            border-color: #0078d4;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #cccccc;
            margin-right: 5px;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            selection-background-color: #0078d4;
            color: #cccccc;
        }
        """

    def _get_level_color(self, level: str) -> str:
        """Get color for log level"""
        colors = {
            "CRITICAL": "#ff66ff",  # Magenta
            "ERROR": "#ff4444",    # Red
            "WARN": "#ffaa00",     # Orange
            "INFO": "#cccccc",     # Light gray
            "DEBUG": "#4da6ff",    # Blue
        }
        return colors.get(level, "#cccccc")

    def set_log_level_filter(self, level: str) -> None:
        """Set log level filter"""
        self.current_filter = level
        self._refresh_display()

    def set_paused(self, paused: bool) -> None:
        """Set pause state"""
        self.is_paused = paused

    def clear_logs(self) -> None:
        """Clear all logs from display"""
        self.log_display.clear()
        self.state_manager.clear_log_messages()

    def save_logs(self, file_path: str) -> None:
        """Save logs to file"""
        content = self.log_display.toPlainText()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _refresh_display(self) -> None:
        """Refresh the log display based on current filter"""
        self.log_display.clear()
        existing_logs = self.state_manager.get_log_messages()

        for log_entry in existing_logs:
            if self._should_display_log(log_entry["level"]):
                self._add_log_entry(
                    log_entry["level"],
                    log_entry["component"],
                    log_entry["message"],
                    log_entry["timestamp"],
                )
