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
        # Parse ANSI colors and convert to HTML
        colored_message = self._parse_ansi_colors(message)

        # Format log entry with timestamp and level
        from html import escape
        timestamp_part = escape(timestamp)
        level_part = escape(level.ljust(5))
        component_part = escape(component.upper())

        # Get color for log level
        level_color = self._get_level_color(level)

        # Build HTML with proper color application
        log_html = (
            f'<span style="color: #00D9A5;">{timestamp_part}</span> '  # Green timestamp
            f'<span style="color: {level_color};">[{level_part}]</span> '  # Level-colored level
            f'<span style="color: #4da6ff;">{component_part}</span> | '  # Blue component
            f'{colored_message}'  # Message with preserved ANSI colors
        )

        # Add to display with color
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Insert colored text
        cursor.insertHtml(f'{log_html}<br>')

        # Auto-scroll to bottom if enabled
        if self.auto_scroll:
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _parse_ansi_colors(self, text: str) -> str:
        """Parse ANSI color codes and convert to HTML spans with colors"""
        import re
        from html import escape

        # ANSI to HTML color mapping (matching loguru's default colors)
        ansi_colors = {
            '30': '#000000',  # Black
            '31': '#ff4444',  # Red
            '32': '#00D9A5',  # Green (matching timestamp)
            '33': '#ffaa00',  # Yellow
            '34': '#4da6ff',  # Blue (matching component)
            '35': '#ff66ff',  # Magenta
            '36': '#00D9A5',  # Cyan
            '37': '#cccccc',  # White
            '90': '#666666',  # Bright Black (Gray)
            '91': '#ff6666',  # Bright Red
            '92': '#00ffaa',  # Bright Green
            '93': '#ffdd00',  # Bright Yellow
            '94': '#66aaff',  # Bright Blue
            '95': '#ff99ff',  # Bright Magenta
            '96': '#00ffff',  # Bright Cyan
            '97': '#ffffff',  # Bright White
        }

        # Pattern to match ANSI codes
        ansi_pattern = re.compile(r'\x1b\[([0-9;]+)m')

        result = []
        last_pos = 0
        current_color = None

        for match in ansi_pattern.finditer(text):
            # Add text before this ANSI code
            if match.start() > last_pos:
                text_segment = text[last_pos:match.start()]
                escaped_text = escape(text_segment)

                if current_color:
                    result.append(f'<span style="color: {current_color};">{escaped_text}</span>')
                else:
                    result.append(escaped_text)

            # Parse ANSI code
            codes = match.group(1).split(';')

            # Reset code (0 or empty)
            if '0' in codes or match.group(1) == '':
                current_color = None
            else:
                # Look for color codes
                for code in codes:
                    if code in ansi_colors:
                        current_color = ansi_colors[code]
                        break

            last_pos = match.end()

        # Add remaining text
        if last_pos < len(text):
            text_segment = text[last_pos:]
            escaped_text = escape(text_segment)

            if current_color:
                result.append(f'<span style="color: {current_color};">{escaped_text}</span>')
            else:
                result.append(escaped_text)

        return ''.join(result)

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
