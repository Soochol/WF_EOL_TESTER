"""Digital Input UI Components - Modern Design

Factory and builder classes for creating modern digital input control UI components.
Uses Material Design 3 components for consistent styling.
Input-only version (no output controls).
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Qt
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

# Local application imports
from ui.gui.widgets.content.robot.modern_components import ModernButton, ModernCard, StatusPill

# Local folder imports
from .event_handlers import DigitalInputEventHandlers
from .state_manager import DigitalInputControlState


class StatusDisplayGroup:
    """Status display group with StatusPills"""

    def __init__(self, state: DigitalInputControlState):
        self.state = state
        self.connection_pill: Optional[StatusPill] = None

    def create(self) -> ModernCard:
        """Create status display card with pills"""
        card = ModernCard("🔌 Digital Input Status")

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

    def __init__(self, event_handlers: DigitalInputEventHandlers):
        self.event_handlers = event_handlers
        self.connect_button: Optional[ModernButton] = None
        self.disconnect_button: Optional[ModernButton] = None

    def create(self) -> ModernCard:
        """Create connection control card"""
        card = ModernCard("🔗 Connection Control")

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        # Connect button
        self.connect_button = ModernButton("Connect", "link", "primary")
        self.connect_button.clicked.connect(self.event_handlers.on_connect_clicked)
        buttons_layout.addWidget(self.connect_button)

        # Disconnect button
        self.disconnect_button = ModernButton("Disconnect", "link_off", "secondary")
        self.disconnect_button.clicked.connect(self.event_handlers.on_disconnect_clicked)
        self.disconnect_button.setEnabled(False)
        buttons_layout.addWidget(self.disconnect_button)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        card.add_widget(buttons_widget)

        return card

    def get_buttons(self) -> dict:
        """Get button references"""
        return {
            "connect": self.connect_button,
            "disconnect": self.disconnect_button,
        }


class InputControlGroup:
    """Input channel control group"""

    def __init__(self, event_handlers: DigitalInputEventHandlers, state: DigitalInputControlState):
        self.event_handlers = event_handlers
        self.state = state
        self.channel_combo: Optional[QComboBox] = None
        self.read_button: Optional[ModernButton] = None
        self.status_label: Optional[QLabel] = None
        self.raw_status_label: Optional[QLabel] = None
        self.contact_type_label: Optional[QLabel] = None

    def create(self) -> ModernCard:
        """Create input control card"""
        card = ModernCard("📡 Input Channel Control")

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
        self.channel_combo.addItems([f"CH{i}" for i in range(32)])  # Default 32 channels
        self.channel_combo.currentIndexChanged.connect(self._on_channel_changed)
        selector_layout.addWidget(self.channel_combo)

        selector_layout.addStretch()

        control_layout.addLayout(selector_layout)

        # Status indicators
        status_grid = QGridLayout()
        status_grid.setSpacing(8)

        # Raw state
        raw_label = QLabel("Raw State:")
        raw_label.setStyleSheet("color: #999999; font-size: 12px;")
        status_grid.addWidget(raw_label, 0, 0)

        self.raw_status_label = QLabel("UNKNOWN")
        self.raw_status_label.setStyleSheet(self._get_status_label_style("#999999"))
        status_grid.addWidget(self.raw_status_label, 0, 1)

        # Actual state
        actual_label = QLabel("Actual State:")
        actual_label.setStyleSheet("color: #999999; font-size: 12px;")
        status_grid.addWidget(actual_label, 1, 0)

        self.status_label = QLabel("UNKNOWN")
        self.status_label.setStyleSheet(self._get_status_label_style("#999999"))
        status_grid.addWidget(self.status_label, 1, 1)

        # Contact type
        contact_label = QLabel("Contact Type:")
        contact_label.setStyleSheet("color: #999999; font-size: 12px;")
        status_grid.addWidget(contact_label, 2, 0)

        self.contact_type_label = QLabel("A-contact (NO)")
        self.contact_type_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        status_grid.addWidget(self.contact_type_label, 2, 1)

        control_layout.addLayout(status_grid)

        # Control button
        self.read_button = ModernButton("Read Input", "visibility", "primary")
        self.read_button.clicked.connect(self._on_read_input)
        self.read_button.setEnabled(False)
        control_layout.addWidget(self.read_button)

        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        card.add_widget(control_widget)

        # Connect to event handler signals
        self.event_handlers.input_read.connect(self._on_input_read)
        self.state.connection_changed.connect(self._on_connection_changed)

        return card

    def _on_channel_changed(self, index: int) -> None:
        """Update contact type display when channel changes"""
        if index in [8, 9]:
            self.contact_type_label.setText("B-contact (NC)")
        else:
            self.contact_type_label.setText("A-contact (NO)")

    def _on_read_input(self) -> None:
        """Handle read input button click"""
        if self.channel_combo:
            channel = self.channel_combo.currentIndex()
            self.event_handlers.on_read_input_clicked(channel)

    def _on_input_read(self, channel: int, raw_state: bool, actual_state: bool) -> None:
        """Update status when input is read"""
        if self.channel_combo and self.status_label and self.raw_status_label:
            current_channel = self.channel_combo.currentIndex()
            if channel == current_channel:
                # Update raw state
                if raw_state:
                    self.raw_status_label.setText("HIGH")
                    self.raw_status_label.setStyleSheet(self._get_status_label_style("#00D9A5"))
                else:
                    self.raw_status_label.setText("LOW")
                    self.raw_status_label.setStyleSheet(self._get_status_label_style("#666666"))

                # Update actual state
                if actual_state:
                    self.status_label.setText("HIGH")
                    self.status_label.setStyleSheet(self._get_status_label_style("#00D9A5"))
                else:
                    self.status_label.setText("LOW")
                    self.status_label.setStyleSheet(self._get_status_label_style("#666666"))

    def _on_connection_changed(self, connected: bool) -> None:
        """Update channel count when connected"""
        if connected and self.channel_combo:
            # Update channel count
            channel_count = self.state.input_count
            current_index = self.channel_combo.currentIndex()
            self.channel_combo.clear()
            self.channel_combo.addItems([f"CH{i}" for i in range(channel_count)])
            if current_index < channel_count:
                self.channel_combo.setCurrentIndex(current_index)

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
            "read_input": self.read_button,
        }


class AllInputsDisplayGroup:
    """Display all input states"""

    def __init__(self, state: DigitalInputControlState, event_handlers: DigitalInputEventHandlers):
        self.state = state
        self.event_handlers = event_handlers
        self.input_indicators = []

    def create(self) -> ModernCard:
        """Create all inputs display card"""
        card = ModernCard("📊 All Input States")

        # Read all button
        read_all_button = ModernButton("Read All Inputs", "refresh_cw", "primary")
        read_all_button.clicked.connect(self.event_handlers.on_read_all_inputs_clicked)
        card.add_widget(read_all_button)

        # Connect to state changes to enable/disable button
        self.state.connection_changed.connect(
            lambda connected: read_all_button.setEnabled(connected)
        )

        # Scroll area for channels
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(250)
        scroll_area.setStyleSheet("""
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
        """)

        # Content widget
        content_widget = QWidget()
        content_layout = QGridLayout(content_widget)
        content_layout.setSpacing(6)

        # Create 32 channel indicators (default)
        for i in range(32):
            label = QLabel(f"CH{i}:")
            label.setStyleSheet("color: #999999; font-size: 11px;")
            content_layout.addWidget(label, i // 4, (i % 4) * 2)

            indicator = QLabel("●")
            indicator.setStyleSheet("color: #666666; font-size: 14px;")
            content_layout.addWidget(indicator, i // 4, (i % 4) * 2 + 1)

            self.input_indicators.append(indicator)

        scroll_area.setWidget(content_widget)
        card.add_widget(scroll_area)

        # Connect to state changes
        self.state.input_changed.connect(self._on_input_changed)
        self.state.all_inputs_changed.connect(self._on_all_inputs_changed)

        return card

    def _on_input_changed(self, channel: int, state: bool) -> None:
        """Update single indicator"""
        if 0 <= channel < len(self.input_indicators):
            indicator = self.input_indicators[channel]
            if state:
                indicator.setStyleSheet("color: #00D9A5; font-size: 14px;")
            else:
                indicator.setStyleSheet("color: #666666; font-size: 14px;")

    def _on_all_inputs_changed(self, states: list) -> None:
        """Update all indicators"""
        for i, state in enumerate(states):
            if i < len(self.input_indicators):
                self._on_input_changed(i, state)


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
