"""Digital Output UI Components - Modern Design

Factory and builder classes for creating modern digital output control UI components.
Uses Material Design 3 components for consistent styling.
Output-only version (no input controls).
"""

# Standard library imports
from typing import Dict, List, Optional

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# Local folder imports
from .event_handlers import DigitalOutputEventHandlers
from .modern_components import ModernButton, ModernCard, StatusPill
from .state_manager import DigitalOutputControlState


class StatusDisplayGroup:
    """Status display group with StatusPills"""

    def __init__(self, state: DigitalOutputControlState):
        self.state = state
        self.connection_pill: Optional[StatusPill] = None

    def create(self) -> ModernCard:
        """Create status display card with pills"""
        card = ModernCard("🔌 Digital Output Status")

        # Pills layout
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(12)

        # Connection status pill
        self.connection_pill = StatusPill("Connection:")
        self.connection_pill.set_status("Disconnected", "#FF5722")
        pills_layout.addWidget(self.connection_pill)

        pills_layout.addStretch()

        pills_widget = QWidget()
        pills_widget.setLayout(pills_layout)
        card.add_widget(pills_widget)

        # Connect to state changes
        self.state.connection_changed.connect(self._on_connection_changed)

        return card

    def _on_connection_changed(self, connected: bool) -> None:
        """Update connection status pill"""
        if self.connection_pill:
            if connected:
                self.connection_pill.set_status("Connected", "#00D9A5")
            else:
                self.connection_pill.set_status("Disconnected", "#FF5722")


class ConnectionGroup:
    """Connection control group"""

    def __init__(self, event_handlers: DigitalOutputEventHandlers):
        self.event_handlers = event_handlers
        self.connect_button: Optional[ModernButton] = None
        self.disconnect_button: Optional[ModernButton] = None
        self.reset_all_button: Optional[ModernButton] = None

    def create(self) -> ModernCard:
        """Create connection control card"""
        card = ModernCard("🔗 Connection Control")

        # Buttons layout
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(8)

        # Connect button
        self.connect_button = ModernButton("Connect", "link", "primary")
        self.connect_button.clicked.connect(self.event_handlers.on_connect_clicked)
        buttons_layout.addWidget(self.connect_button, 0, 0)

        # Disconnect button
        self.disconnect_button = ModernButton("Disconnect", "link_off", "secondary")
        self.disconnect_button.clicked.connect(self.event_handlers.on_disconnect_clicked)
        self.disconnect_button.setEnabled(False)
        buttons_layout.addWidget(self.disconnect_button, 0, 1)

        # Reset all outputs button
        self.reset_all_button = ModernButton("Reset All Outputs", "refresh_cw", "warning")
        self.reset_all_button.clicked.connect(self.event_handlers.on_reset_all_outputs_clicked)
        self.reset_all_button.setEnabled(False)
        buttons_layout.addWidget(self.reset_all_button, 1, 0, 1, 2)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        card.add_widget(buttons_widget)

        return card

    def get_buttons(self) -> dict:
        """Get button references"""
        return {
            "connect": self.connect_button,
            "disconnect": self.disconnect_button,
            "reset_all_outputs": self.reset_all_button,
        }


class OutputControlGroup:
    """Output channel control group"""

    def __init__(
        self, event_handlers: DigitalOutputEventHandlers, state: DigitalOutputControlState
    ):
        self.event_handlers = event_handlers
        self.state = state
        self.channel_combo: Optional[QComboBox] = None
        self.set_high_button: Optional[ModernButton] = None
        self.set_low_button: Optional[ModernButton] = None
        self.read_button: Optional[ModernButton] = None
        self.status_label: Optional[QLabel] = None

    def create(self) -> ModernCard:
        """Create output control card"""
        card = ModernCard("⚡ Output Channel Control")

        # Control layout
        control_layout = QVBoxLayout()
        control_layout.setSpacing(12)

        # Channel selector
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(8)

        channel_label = QLabel("Channel:")
        channel_label.setStyleSheet("color: #cccccc; font-size: 13px; font-weight: 600;")
        selector_layout.addWidget(channel_label)

        self.channel_combo = QComboBox()
        self.channel_combo.setStyleSheet(self._get_combo_style())
        self.channel_combo.addItems([f"CH{i}" for i in range(32)])  # 32 channels
        selector_layout.addWidget(self.channel_combo)

        # Status indicator
        status_label_title = QLabel("Status:")
        status_label_title.setStyleSheet("color: #999999; font-size: 12px;")
        selector_layout.addWidget(status_label_title)

        self.status_label = QLabel("UNKNOWN")
        self.status_label.setStyleSheet(self._get_status_label_style("#999999"))
        selector_layout.addWidget(self.status_label)

        selector_layout.addStretch()

        control_layout.addLayout(selector_layout)

        # Control buttons
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(8)

        self.set_high_button = ModernButton("Set HIGH", "arrow_up", "success")
        self.set_high_button.clicked.connect(self._on_set_high)
        self.set_high_button.setEnabled(False)
        buttons_layout.addWidget(self.set_high_button, 0, 0)

        self.set_low_button = ModernButton("Set LOW", "arrow_down", "secondary")
        self.set_low_button.clicked.connect(self._on_set_low)
        self.set_low_button.setEnabled(False)
        buttons_layout.addWidget(self.set_low_button, 0, 1)

        self.read_button = ModernButton("Read State", "visibility", "primary")
        self.read_button.clicked.connect(self._on_read_output)
        self.read_button.setEnabled(False)
        buttons_layout.addWidget(self.read_button, 1, 0, 1, 2)

        control_layout.addLayout(buttons_layout)

        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        card.add_widget(control_widget)

        # Connect to state changes
        self.state.output_changed.connect(self._on_output_changed)
        self.state.connection_changed.connect(self._on_connection_changed)

        return card

    def _on_set_high(self) -> None:
        """Handle set HIGH button click"""
        if self.channel_combo:
            channel = self.channel_combo.currentIndex()
            self.event_handlers.on_write_output_clicked(channel, True)

    def _on_set_low(self) -> None:
        """Handle set LOW button click"""
        if self.channel_combo:
            channel = self.channel_combo.currentIndex()
            self.event_handlers.on_write_output_clicked(channel, False)

    def _on_read_output(self) -> None:
        """Handle read output button click"""
        if self.channel_combo:
            channel = self.channel_combo.currentIndex()
            self.event_handlers.on_read_output_clicked(channel)

    def _on_output_changed(self, channel: int, state: bool) -> None:
        """Update status when output changes"""
        if self.channel_combo and self.status_label:
            current_channel = self.channel_combo.currentIndex()
            if channel == current_channel:
                if state:
                    self.status_label.setText("HIGH")
                    self.status_label.setStyleSheet(self._get_status_label_style("#00D9A5"))
                else:
                    self.status_label.setText("LOW")
                    self.status_label.setStyleSheet(self._get_status_label_style("#999999"))

    def _on_connection_changed(self, connected: bool) -> None:
        """Update channel count when connected"""
        if connected and self.channel_combo:
            # Update channel count
            channel_count = self.state.output_count
            self.channel_combo.clear()
            self.channel_combo.addItems([f"CH{i}" for i in range(channel_count)])

    def _get_combo_style(self) -> str:
        """Get combo box stylesheet"""
        return """
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
                min-width: 100px;
            }
            QComboBox:focus {
                border: 1px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #cccccc;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #2196F3;
                border: 1px solid #555555;
            }
        """

    def _get_status_label_style(self, color: str) -> str:
        """Get status label stylesheet"""
        return f"""
            QLabel {{
                color: {color};
                font-size: 13px;
                font-weight: 600;
                padding: 4px 12px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                border: 1px solid {color}60;
                min-width: 60px;
            }}
        """

    def get_buttons(self) -> dict:
        """Get button references"""
        return {
            "write_output": self.set_high_button,  # Use set_high as representative
            "read_output": self.read_button,
        }


class AllOutputsDisplayGroup:
    """Display all output states"""

    def __init__(self, state: DigitalOutputControlState, event_handlers):
        self.state = state
        self.event_handlers = event_handlers
        self.output_indicators = []

    def create(self) -> ModernCard:
        """Create all outputs display card"""
        card = ModernCard("📊 All Output States")

        # Read All Outputs button
        read_all_button = ModernButton("Read All Outputs", "refresh_cw", "primary")
        read_all_button.clicked.connect(self.event_handlers.on_read_all_outputs_clicked)
        card.add_widget(read_all_button)

        # Connect to state changes to enable/disable button
        self.state.connection_changed.connect(
            lambda connected: read_all_button.setEnabled(connected)
        )

        # Scroll area for channels
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 4px;
            }
        """
        )

        # Content widget
        content_widget = QWidget()
        content_layout = QGridLayout(content_widget)
        content_layout.setSpacing(4)

        # Create 32 channel indicators (8 rows x 4 columns)
        for i in range(32):
            row = i // 4
            col = (i % 4) * 2

            label = QLabel(f"CH{i}:")
            label.setStyleSheet("color: #999999; font-size: 11px;")
            content_layout.addWidget(label, row, col)

            indicator = QLabel("●")
            indicator.setStyleSheet("color: #666666; font-size: 14px;")
            content_layout.addWidget(indicator, row, col + 1)

            self.output_indicators.append(indicator)

        scroll_area.setWidget(content_widget)
        card.add_widget(scroll_area)

        # Connect to state changes
        self.state.output_changed.connect(self._on_output_changed)
        self.state.all_outputs_changed.connect(self._on_all_outputs_changed)

        return card

    def _on_output_changed(self, channel: int, state: bool) -> None:
        """Update single indicator"""
        if 0 <= channel < len(self.output_indicators):
            indicator = self.output_indicators[channel]
            if state:
                indicator.setStyleSheet("color: #00D9A5; font-size: 16px;")
            else:
                indicator.setStyleSheet("color: #666666; font-size: 16px;")

    def _on_all_outputs_changed(self, states: list) -> None:
        """Update all indicators"""
        for i, state in enumerate(states):
            if i < len(self.output_indicators):
                self._on_output_changed(i, state)


class ClickableIndicator(QLabel):
    """Clickable LED indicator that acts as a toggle button (All Output States style)"""

    clicked = Signal(int, bool)  # channel, new_state

    def __init__(self, channel: int, parent=None):
        super().__init__("●", parent)
        self.channel = channel
        self.state = False  # Default OFF
        self.enabled = False
        self.setStyleSheet("color: #666666; font-size: 16px;")

    def mousePressEvent(self, event):
        """Handle mouse click to toggle state"""
        if self.enabled:
            self.state = not self.state
            self._update_style()
            self.clicked.emit(self.channel, self.state)
        super().mousePressEvent(event)

    def set_state(self, state: bool):
        """Set indicator state programmatically"""
        self.state = state
        self._update_style()

    def set_enabled(self, enabled: bool):
        """Enable/disable indicator clicks"""
        self.enabled = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _update_style(self):
        """Update indicator appearance based on state"""
        if self.state:
            self.setStyleSheet("color: #00D9A5; font-size: 16px;")
        else:
            self.setStyleSheet("color: #666666; font-size: 16px;")


class LEDToggleGrid(QWidget):
    """Grid of 32 clickable LED indicators for digital output control (All Output States style)"""

    def __init__(self, event_handlers, state, parent=None):
        super().__init__(parent)
        self.event_handlers = event_handlers
        self.state = state
        self.indicators: Dict[int, ClickableIndicator] = {}
        self._setup_ui()

        # Connect to state changes
        self.state.output_changed.connect(self._on_output_changed)
        self.state.all_outputs_changed.connect(self._on_all_outputs_changed)
        self.state.connection_changed.connect(self._on_connection_changed)

    def _setup_ui(self):
        """Setup LED toggle grid UI - matching All Output States style"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area for LED grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 4px;
            }
        """
        )

        # Content widget
        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)
        grid_layout.setSpacing(4)

        # Create 32 channel indicators (8 rows x 4 columns) - same as All Output States
        for i in range(32):
            row = i // 4
            col = (i % 4) * 2

            # Channel label
            label = QLabel(f"CH{i}:")
            label.setStyleSheet("color: #999999; font-size: 11px;")
            grid_layout.addWidget(label, row, col)

            # Clickable indicator
            indicator = ClickableIndicator(i)
            indicator.clicked.connect(self._on_indicator_clicked)
            indicator.set_enabled(False)  # Disabled until connected
            self.indicators[i] = indicator
            grid_layout.addWidget(indicator, row, col + 1)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _on_indicator_clicked(self, channel: int, state: bool):
        """Handle indicator click to toggle output"""
        self.event_handlers.on_write_output_clicked(channel, state)

    def _on_output_changed(self, channel: int, state: bool):
        """Update indicator when output changes"""
        if channel in self.indicators:
            indicator = self.indicators[channel]
            indicator.blockSignals(True)  # Prevent recursive signal
            indicator.set_state(state)
            indicator.blockSignals(False)

    def _on_all_outputs_changed(self, states: List[bool]):
        """Update all indicators when all outputs change"""
        for i, state in enumerate(states):
            if i < 32:
                self._on_output_changed(i, state)

    def _on_connection_changed(self, connected: bool):
        """Enable/disable indicators based on connection state"""
        for indicator in self.indicators.values():
            indicator.set_enabled(connected)

    def create(self) -> ModernCard:
        """Create LED toggle grid card"""
        card = ModernCard("💡 LED Toggle Control (32 Channels)")
        card.add_widget(self)
        return card


def create_modern_progress_bar() -> QProgressBar:
    """Create modern styled progress bar"""
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 0)  # Indeterminate progress
    progress_bar.setTextVisible(True)
    progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
    progress_bar.setStyleSheet(
        """
        QProgressBar {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            text-align: center;
            background-color: #2d2d2d;
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
            min-height: 24px;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2196F3, stop:1 #64B5F6);
            border-radius: 8px;
        }
    """
    )
    return progress_bar
