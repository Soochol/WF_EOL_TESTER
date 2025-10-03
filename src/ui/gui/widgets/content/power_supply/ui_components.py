"""Power Supply UI Components - Modern Design

Factory and builder classes for creating modern power supply control UI components.
Uses Material Design 3 components for consistent styling.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from ui.gui.utils.styling import ThemeManager

# Local folder imports
from .event_handlers import PowerSupplyEventHandlers
from .modern_components import ModernButton, ModernCard, StatusPill
from .state_manager import PowerSupplyControlState


class StatusDisplayGroup:
    """Status display group with StatusPills"""

    def __init__(self, state: PowerSupplyControlState):
        self.state = state
        self.connection_pill: Optional[StatusPill] = None
        self.output_pill: Optional[StatusPill] = None

    def create(self) -> ModernCard:
        """Create status display card with pills"""
        card = ModernCard("⚡ Power Supply Status")

        # Pills layout
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(12)

        # Connection status pill
        self.connection_pill = StatusPill("Connection:")
        self.connection_pill.set_status("Disconnected", "#FF5722")
        pills_layout.addWidget(self.connection_pill)

        # Output status pill
        self.output_pill = StatusPill("Output:")
        self.output_pill.set_status("Disabled", "#FFC107")
        pills_layout.addWidget(self.output_pill)

        pills_widget = QWidget()
        pills_widget.setLayout(pills_layout)
        card.add_widget(pills_widget)

        # Connect to state changes
        self.state.connection_changed.connect(self._on_connection_changed)
        self.state.output_changed.connect(self._on_output_changed)

        return card

    def _on_connection_changed(self, connected: bool) -> None:
        """Update connection status pill"""
        if self.connection_pill:
            if connected:
                self.connection_pill.set_status("Connected", "#00D9A5")
            else:
                self.connection_pill.set_status("Disconnected", "#FF5722")

    def _on_output_changed(self, enabled: bool) -> None:
        """Update output status pill"""
        if self.output_pill:
            if enabled:
                self.output_pill.set_status("Enabled", "#00D9A5")
            else:
                self.output_pill.set_status("Disabled", "#FFC107")


class ConnectionGroup:
    """Connection and output control group"""

    def __init__(self, event_handlers: PowerSupplyEventHandlers):
        self.event_handlers = event_handlers
        self.connect_button: Optional[ModernButton] = None
        self.disconnect_button: Optional[ModernButton] = None
        self.enable_output_button: Optional[ModernButton] = None
        self.disable_output_button: Optional[ModernButton] = None

    def create(self) -> ModernCard:
        """Create connection control card"""
        card = ModernCard("🔌 Connection & Output Control")

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

        # Enable output button
        self.enable_output_button = ModernButton("Enable Output", "power", "success")
        self.enable_output_button.clicked.connect(self.event_handlers.on_enable_output_clicked)
        self.enable_output_button.setEnabled(False)
        buttons_layout.addWidget(self.enable_output_button, 1, 0)

        # Disable output button
        self.disable_output_button = ModernButton("Disable Output", "power_off", "warning")
        self.disable_output_button.clicked.connect(self.event_handlers.on_disable_output_clicked)
        self.disable_output_button.setEnabled(False)
        buttons_layout.addWidget(self.disable_output_button, 1, 1)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        card.add_widget(buttons_widget)

        return card

    def get_buttons(self) -> dict:
        """Get button references"""
        return {
            "connect": self.connect_button,
            "disconnect": self.disconnect_button,
            "enable_output": self.enable_output_button,
            "disable_output": self.disable_output_button,
        }


class ControlGroup:
    """Voltage and current control group"""

    def __init__(self, event_handlers: PowerSupplyEventHandlers):
        self.event_handlers = event_handlers
        self.voltage_spinbox: Optional[QDoubleSpinBox] = None
        self.current_spinbox: Optional[QDoubleSpinBox] = None
        self.set_voltage_button: Optional[ModernButton] = None
        self.set_current_button: Optional[ModernButton] = None

    def create(self) -> ModernCard:
        """Create control card"""
        card = ModernCard("⚙️ Voltage & Current Control")

        # Control layout
        control_layout = QGridLayout()
        control_layout.setSpacing(8)

        # Voltage control
        voltage_label = QLabel("Voltage (V):")
        voltage_label.setStyleSheet("color: #cccccc; font-size: 13px; font-weight: 600;")
        control_layout.addWidget(voltage_label, 0, 0)

        self.voltage_spinbox = QDoubleSpinBox()
        self.voltage_spinbox.setRange(0.0, 30.0)
        self.voltage_spinbox.setValue(5.0)
        self.voltage_spinbox.setDecimals(2)
        self.voltage_spinbox.setSuffix(" V")
        self.voltage_spinbox.setStyleSheet(self._get_spinbox_style())
        control_layout.addWidget(self.voltage_spinbox, 0, 1)

        self.set_voltage_button = ModernButton("Set Voltage", "bolt", "primary")
        self.set_voltage_button.clicked.connect(self._on_set_voltage)
        self.set_voltage_button.setEnabled(False)
        control_layout.addWidget(self.set_voltage_button, 0, 2)

        # Current control
        current_label = QLabel("Current (A):")
        current_label.setStyleSheet("color: #cccccc; font-size: 13px; font-weight: 600;")
        control_layout.addWidget(current_label, 1, 0)

        self.current_spinbox = QDoubleSpinBox()
        self.current_spinbox.setRange(0.0, 10.0)
        self.current_spinbox.setValue(1.0)
        self.current_spinbox.setDecimals(3)
        self.current_spinbox.setSuffix(" A")
        self.current_spinbox.setStyleSheet(self._get_spinbox_style())
        control_layout.addWidget(self.current_spinbox, 1, 1)

        self.set_current_button = ModernButton("Set Current", "flash", "primary")
        self.set_current_button.clicked.connect(self._on_set_current)
        self.set_current_button.setEnabled(False)
        control_layout.addWidget(self.set_current_button, 1, 2)

        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        card.add_widget(control_widget)

        return card

    def _on_set_voltage(self) -> None:
        """Handle set voltage button click"""
        if self.voltage_spinbox:
            voltage = self.voltage_spinbox.value()
            self.event_handlers.on_set_voltage_clicked(voltage)

    def _on_set_current(self) -> None:
        """Handle set current button click"""
        if self.current_spinbox:
            current = self.current_spinbox.value()
            self.event_handlers.on_set_current_clicked(current)

    def _get_spinbox_style(self) -> str:
        """Get spinbox stylesheet"""
        return """
            QDoubleSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
                min-width: 120px;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #2196F3;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #3d3d3d;
                border: none;
                width: 16px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #4d4d4d;
            }
        """

    def get_buttons(self) -> dict:
        """Get button references"""
        return {
            "set_voltage": self.set_voltage_button,
            "set_current": self.set_current_button,
        }


class MeasurementGroup:
    """Measurement display group"""

    def __init__(self, event_handlers: PowerSupplyEventHandlers):
        self.event_handlers = event_handlers
        self.voltage_label: Optional[QLabel] = None
        self.current_label: Optional[QLabel] = None
        self.power_label: Optional[QLabel] = None
        self.get_voltage_button: Optional[ModernButton] = None
        self.get_current_button: Optional[ModernButton] = None
        self.get_all_button: Optional[ModernButton] = None

    def create(self) -> ModernCard:
        """Create measurement card"""
        card = ModernCard("📊 Measurements")

        # Measurement display layout
        measurement_layout = QGridLayout()
        measurement_layout.setSpacing(8)

        # Voltage measurement
        voltage_title = QLabel("Voltage:")
        voltage_title.setStyleSheet("color: #999999; font-size: 12px;")
        measurement_layout.addWidget(voltage_title, 0, 0)

        self.voltage_label = QLabel("-- V")
        self.voltage_label.setStyleSheet(self._get_measurement_label_style())
        measurement_layout.addWidget(self.voltage_label, 0, 1)

        self.get_voltage_button = ModernButton("Read", "visibility", "secondary")
        self.get_voltage_button.clicked.connect(self.event_handlers.on_get_voltage_clicked)
        self.get_voltage_button.setEnabled(False)
        measurement_layout.addWidget(self.get_voltage_button, 0, 2)

        # Current measurement
        current_title = QLabel("Current:")
        current_title.setStyleSheet("color: #999999; font-size: 12px;")
        measurement_layout.addWidget(current_title, 1, 0)

        self.current_label = QLabel("-- A")
        self.current_label.setStyleSheet(self._get_measurement_label_style())
        measurement_layout.addWidget(self.current_label, 1, 1)

        self.get_current_button = ModernButton("Read", "visibility", "secondary")
        self.get_current_button.clicked.connect(self.event_handlers.on_get_current_clicked)
        self.get_current_button.setEnabled(False)
        measurement_layout.addWidget(self.get_current_button, 1, 2)

        # Power measurement
        power_title = QLabel("Power:")
        power_title.setStyleSheet("color: #999999; font-size: 12px;")
        measurement_layout.addWidget(power_title, 2, 0)

        self.power_label = QLabel("-- W")
        self.power_label.setStyleSheet(self._get_measurement_label_style())
        measurement_layout.addWidget(self.power_label, 2, 1)

        # Get all measurements button
        self.get_all_button = ModernButton("Read All", "refresh", "primary")
        self.get_all_button.clicked.connect(self.event_handlers.on_get_all_measurements_clicked)
        self.get_all_button.setEnabled(False)
        measurement_layout.addWidget(self.get_all_button, 2, 2)

        measurement_widget = QWidget()
        measurement_widget.setLayout(measurement_layout)
        card.add_widget(measurement_widget)

        return card

    def _get_measurement_label_style(self) -> str:
        """Get measurement label stylesheet"""
        return """
            QLabel {
                color: #cccccc;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 12px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                min-width: 80px;
            }
        """

    def get_buttons(self) -> dict:
        """Get button references"""
        return {
            "get_voltage": self.get_voltage_button,
            "get_current": self.get_current_button,
            "get_all_measurements": self.get_all_button,
        }


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
