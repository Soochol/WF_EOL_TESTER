"""MCU UI Components

Factory and builder classes for creating modern MCU control UI components.
Uses Material Design 3 components for consistent styling.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from ui.gui.widgets.content.robot.modern_components import (
    ModernButton,
    ModernCard,
    StatusPill,
)

# Local folder imports
from .event_handlers import MCUEventHandlers
from .state_manager import MCUControlState


class StatusDisplayGroup:
    """Status display group with StatusPills"""

    def __init__(self, state: MCUControlState):
        self.state = state
        self.connection_pill: Optional[StatusPill] = None
        self.temperature_pill: Optional[StatusPill] = None
        self.mode_pill: Optional[StatusPill] = None

    def create(self) -> ModernCard:
        """Create status display card with pills"""
        card = ModernCard("📊 MCU Status")

        # Pills layout
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(12)

        # Connection status pill
        self.connection_pill = StatusPill("Connection:")
        self.connection_pill.set_status("Disconnected", "#FF5722")
        pills_layout.addWidget(self.connection_pill)

        # Temperature status pill
        self.temperature_pill = StatusPill("Temperature:")
        self.temperature_pill.set_status("Unknown", "#cccccc")
        pills_layout.addWidget(self.temperature_pill)

        # Mode status pill
        self.mode_pill = StatusPill("Mode:")
        self.mode_pill.set_status("Normal", "#2196F3")
        pills_layout.addWidget(self.mode_pill)

        pills_widget = QWidget()
        pills_widget.setLayout(pills_layout)
        card.add_widget(pills_widget)

        # Connect to state changes
        self.state.connection_changed.connect(self._on_connection_changed)
        self.state.temperature_changed.connect(self._on_temperature_changed)
        self.state.test_mode_changed.connect(self._on_mode_changed)

        return card

    def _on_connection_changed(self, connected: bool) -> None:
        """Update connection status pill"""
        if self.connection_pill:
            if connected:
                self.connection_pill.set_status("Connected", "#00D9A5")
            else:
                self.connection_pill.set_status("Disconnected", "#FF5722")

    def _on_temperature_changed(self, temperature: float) -> None:
        """Update temperature pill"""
        if self.temperature_pill:
            self.temperature_pill.set_status(f"{temperature:.1f}°C", "#FF9800")

    def _on_mode_changed(self, mode: str) -> None:
        """Update mode status pill"""
        if self.mode_pill:
            self.mode_pill.set_status(mode, "#2196F3")


class ConnectionGroup:
    """Connection control group"""

    def __init__(self, event_handlers: MCUEventHandlers):
        self.event_handlers = event_handlers
        self.connect_btn: Optional[QPushButton] = None
        self.disconnect_btn: Optional[QPushButton] = None

    def create(self) -> ModernCard:
        """Create connection control card"""
        card = ModernCard("🔌 Connection Control")

        main_layout = QHBoxLayout()
        main_layout.setSpacing(8)

        self.connect_btn = ModernButton("Connect", "play", "success")
        self.disconnect_btn = ModernButton("Disconnect", "stop", "danger")

        self.connect_btn.clicked.connect(self.event_handlers.on_connect_clicked)
        self.disconnect_btn.clicked.connect(self.event_handlers.on_disconnect_clicked)

        main_layout.addWidget(self.connect_btn)
        main_layout.addWidget(self.disconnect_btn)

        container = QWidget()
        container.setLayout(main_layout)
        card.add_widget(container)

        return card

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references"""
        return {
            "connect": self.connect_btn,
            "disconnect": self.disconnect_btn,
        }


class TemperatureControlGroup:
    """Temperature control group"""

    def __init__(self, event_handlers: MCUEventHandlers):
        self.event_handlers = event_handlers

        # Buttons
        self.read_temp_btn: Optional[QPushButton] = None
        self.set_operating_btn: Optional[QPushButton] = None
        self.set_cooling_btn: Optional[QPushButton] = None
        self.set_upper_btn: Optional[QPushButton] = None

        # Input fields
        self.operating_temp_input: Optional[QDoubleSpinBox] = None
        self.cooling_temp_input: Optional[QDoubleSpinBox] = None
        self.upper_temp_input: Optional[QDoubleSpinBox] = None

        # Display label
        self.current_temp_label: Optional[QLabel] = None

    def create(self) -> ModernCard:
        """Create temperature control card"""
        card = ModernCard("🌡️ Temperature Control")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Current temperature display
        temp_display_layout = QHBoxLayout()
        temp_display_layout.setSpacing(8)

        label = QLabel("Current:")
        label.setStyleSheet("color: #cccccc; font-size: 13px; font-weight: 600;")
        temp_display_layout.addWidget(label)

        self.read_temp_btn = ModernButton("Read", "thermometer", "primary")
        self.read_temp_btn.clicked.connect(self.event_handlers.on_read_temperature_clicked)
        temp_display_layout.addWidget(self.read_temp_btn)

        self.current_temp_label = QLabel("--°C")
        self.current_temp_label.setStyleSheet(
            """
            QLabel {
                color: #FF9800;
                font-size: 14px;
                font-weight: 600;
                padding: 6px 12px;
                background-color: rgba(255, 152, 0, 0.1);
                border-radius: 6px;
                border: 1px solid rgba(255, 152, 0, 0.3);
                min-width: 60px;
            }
        """
        )
        temp_display_layout.addWidget(self.current_temp_label)
        temp_display_layout.addStretch()
        main_layout.addLayout(temp_display_layout)

        # Operating temperature
        op_layout = QHBoxLayout()
        op_layout.setSpacing(8)

        op_label = QLabel("Operating:")
        op_label.setStyleSheet("color: #cccccc; font-size: 13px; min-width: 70px;")
        op_layout.addWidget(op_label)

        self.operating_temp_input = self._create_temp_spinbox()
        self.operating_temp_input.setValue(60.0)
        op_layout.addWidget(self.operating_temp_input)

        self.set_operating_btn = ModernButton("Set", "check", "success")
        self.set_operating_btn.clicked.connect(
            lambda input_widget=self.operating_temp_input: (
                self.event_handlers.on_set_operating_temperature(input_widget.value())
                if input_widget else None
            )
        )
        op_layout.addWidget(self.set_operating_btn)
        main_layout.addLayout(op_layout)

        # Cooling temperature
        cool_layout = QHBoxLayout()
        cool_layout.setSpacing(8)

        cool_label = QLabel("Cooling:")
        cool_label.setStyleSheet("color: #cccccc; font-size: 13px; min-width: 70px;")
        cool_layout.addWidget(cool_label)

        self.cooling_temp_input = self._create_temp_spinbox()
        self.cooling_temp_input.setValue(25.0)
        cool_layout.addWidget(self.cooling_temp_input)

        self.set_cooling_btn = ModernButton("Set", "check", "primary")
        self.set_cooling_btn.clicked.connect(
            lambda input_widget=self.cooling_temp_input: (
                self.event_handlers.on_set_cooling_temperature(input_widget.value())
                if input_widget else None
            )
        )
        cool_layout.addWidget(self.set_cooling_btn)
        main_layout.addLayout(cool_layout)

        # Upper temperature limit
        upper_layout = QHBoxLayout()
        upper_layout.setSpacing(8)

        upper_label = QLabel("Upper Limit:")
        upper_label.setStyleSheet("color: #cccccc; font-size: 13px; min-width: 70px;")
        upper_layout.addWidget(upper_label)

        self.upper_temp_input = self._create_temp_spinbox()
        self.upper_temp_input.setValue(80.0)
        upper_layout.addWidget(self.upper_temp_input)

        self.set_upper_btn = ModernButton("Set", "check", "warning")
        self.set_upper_btn.clicked.connect(
            lambda input_widget=self.upper_temp_input: (
                self.event_handlers.on_set_upper_temperature(input_widget.value())
                if input_widget else None
            )
        )
        upper_layout.addWidget(self.set_upper_btn)
        main_layout.addLayout(upper_layout)

        container = QWidget()
        container.setLayout(main_layout)
        card.add_widget(container)

        return card

    def _create_temp_spinbox(self) -> QDoubleSpinBox:
        """Create temperature spinbox with common settings"""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(-50.0, 200.0)
        spinbox.setSingleStep(1.0)
        spinbox.setDecimals(1)
        spinbox.setStyleSheet(
            """
            QDoubleSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                min-width: 80px;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #2196F3;
            }
        """
        )
        return spinbox

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references"""
        return {
            "read_temp": self.read_temp_btn,
            "set_operating_temp": self.set_operating_btn,
            "set_cooling_temp": self.set_cooling_btn,
            "set_upper_temp": self.set_upper_btn,
        }


class AdvancedControlGroup:
    """Advanced control group"""

    def __init__(self, event_handlers: MCUEventHandlers):
        self.event_handlers = event_handlers

        # Buttons
        self.enter_test_mode_btn: Optional[QPushButton] = None
        self.wait_boot_btn: Optional[QPushButton] = None
        self.start_heating_btn: Optional[QPushButton] = None
        self.start_cooling_btn: Optional[QPushButton] = None
        self.set_fan_speed_btn: Optional[QPushButton] = None

        # Input fields
        self.fan_speed_slider: Optional[QSlider] = None
        self.fan_speed_label: Optional[QLabel] = None
        self.heating_op_temp_input: Optional[QDoubleSpinBox] = None
        self.heating_standby_temp_input: Optional[QDoubleSpinBox] = None
        self.heating_hold_time_input: Optional[QSpinBox] = None

    def create(self) -> ModernCard:
        """Create advanced control card"""
        card = ModernCard("🎮 Advanced Control")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Test mode and boot control
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)

        self.enter_test_mode_btn = ModernButton("Enter Test Mode", "activity", "warning")
        self.enter_test_mode_btn.clicked.connect(self.event_handlers.on_enter_test_mode_clicked)
        control_layout.addWidget(self.enter_test_mode_btn)

        self.wait_boot_btn = ModernButton("Wait Boot", "clock", "secondary")
        self.wait_boot_btn.clicked.connect(self.event_handlers.on_wait_boot_clicked)
        control_layout.addWidget(self.wait_boot_btn)

        main_layout.addLayout(control_layout)

        # Heating parameters
        heating_label = QLabel("Standby Heating Parameters:")
        heating_label.setStyleSheet("color: #999999; font-size: 12px; margin-top: 8px;")
        main_layout.addWidget(heating_label)

        # Operating temp for heating
        heating_op_layout = QHBoxLayout()
        heating_op_layout.setSpacing(8)
        op_label = QLabel("Operating:")
        op_label.setStyleSheet("color: #cccccc; font-size: 12px; min-width: 70px;")
        heating_op_layout.addWidget(op_label)
        self.heating_op_temp_input = self._create_temp_spinbox()
        self.heating_op_temp_input.setValue(60.0)
        heating_op_layout.addWidget(self.heating_op_temp_input)
        heating_op_layout.addStretch()
        main_layout.addLayout(heating_op_layout)

        # Standby temp for heating
        heating_standby_layout = QHBoxLayout()
        heating_standby_layout.setSpacing(8)
        standby_label = QLabel("Standby:")
        standby_label.setStyleSheet("color: #cccccc; font-size: 12px; min-width: 70px;")
        heating_standby_layout.addWidget(standby_label)
        self.heating_standby_temp_input = self._create_temp_spinbox()
        self.heating_standby_temp_input.setValue(40.0)
        heating_standby_layout.addWidget(self.heating_standby_temp_input)
        heating_standby_layout.addStretch()
        main_layout.addLayout(heating_standby_layout)

        # Hold time for heating
        heating_hold_layout = QHBoxLayout()
        heating_hold_layout.setSpacing(8)
        hold_label = QLabel("Hold Time:")
        hold_label.setStyleSheet("color: #cccccc; font-size: 12px; min-width: 70px;")
        heating_hold_layout.addWidget(hold_label)
        self.heating_hold_time_input = QSpinBox()
        self.heating_hold_time_input.setRange(1000, 60000)
        self.heating_hold_time_input.setSingleStep(1000)
        self.heating_hold_time_input.setValue(60000)
        self.heating_hold_time_input.setSuffix(" ms")
        self.heating_hold_time_input.setStyleSheet(
            """
            QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 1px solid #2196F3;
            }
        """
        )
        heating_hold_layout.addWidget(self.heating_hold_time_input)
        heating_hold_layout.addStretch()
        main_layout.addLayout(heating_hold_layout)

        # Heating/Cooling buttons
        heating_cooling_layout = QHBoxLayout()
        heating_cooling_layout.setSpacing(8)

        self.start_heating_btn = ModernButton("Start Heating", "zap", "warning")
        self.start_heating_btn.clicked.connect(
            lambda op_temp=self.heating_op_temp_input, standby_temp=self.heating_standby_temp_input, hold_time=self.heating_hold_time_input: (
                self.event_handlers.on_start_heating(
                    op_temp.value(),
                    standby_temp.value(),
                    hold_time.value(),
                )
                if op_temp and standby_temp and hold_time else None
            )
        )
        heating_cooling_layout.addWidget(self.start_heating_btn)

        self.start_cooling_btn = ModernButton("Start Cooling", "wind", "primary")
        self.start_cooling_btn.clicked.connect(self.event_handlers.on_start_cooling_clicked)
        heating_cooling_layout.addWidget(self.start_cooling_btn)

        main_layout.addLayout(heating_cooling_layout)

        # Fan speed control
        fan_layout = QVBoxLayout()
        fan_layout.setSpacing(6)

        fan_header_layout = QHBoxLayout()
        fan_header_layout.setSpacing(8)

        fan_label = QLabel("Fan Speed:")
        fan_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        fan_header_layout.addWidget(fan_label)

        self.fan_speed_label = QLabel("5")
        self.fan_speed_label.setStyleSheet(
            """
            QLabel {
                color: #2196F3;
                font-size: 14px;
                font-weight: 600;
                padding: 4px 10px;
                background-color: rgba(33, 150, 243, 0.1);
                border-radius: 6px;
                min-width: 30px;
            }
        """
        )
        fan_header_layout.addWidget(self.fan_speed_label)
        fan_header_layout.addStretch()

        self.set_fan_speed_btn = ModernButton("Set", "check", "success")
        self.set_fan_speed_btn.clicked.connect(
            lambda slider=self.fan_speed_slider: (
                self.event_handlers.on_set_fan_speed(slider.value()) if slider else None
            )
        )
        fan_header_layout.addWidget(self.set_fan_speed_btn)

        fan_layout.addLayout(fan_header_layout)

        # Fan speed slider
        self.fan_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.fan_speed_slider.setRange(0, 10)
        self.fan_speed_slider.setValue(5)
        self.fan_speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.fan_speed_slider.setTickInterval(1)
        self.fan_speed_slider.valueChanged.connect(
            lambda val, label=self.fan_speed_label: (
                label.setText(str(val)) if label else None
            )
        )
        self.fan_speed_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                background: #2d2d2d;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 2px solid #1976D2;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #42A5F5;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #1976D2);
                border-radius: 3px;
            }
        """
        )
        fan_layout.addWidget(self.fan_speed_slider)

        main_layout.addLayout(fan_layout)

        container = QWidget()
        container.setLayout(main_layout)
        card.add_widget(container)

        return card

    def _create_temp_spinbox(self) -> QDoubleSpinBox:
        """Create temperature spinbox with common settings"""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(30.0, 80.0)
        spinbox.setSingleStep(1.0)
        spinbox.setDecimals(1)
        spinbox.setStyleSheet(
            """
            QDoubleSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
                min-width: 70px;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #2196F3;
            }
        """
        )
        return spinbox

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references"""
        return {
            "enter_test_mode": self.enter_test_mode_btn,
            "wait_boot": self.wait_boot_btn,
            "start_heating": self.start_heating_btn,
            "start_cooling": self.start_cooling_btn,
            "set_fan_speed": self.set_fan_speed_btn,
        }


def create_modern_progress_bar() -> QProgressBar:
    """Create modern styled progress bar"""
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 0)  # Indeterminate progress
    progress_bar.setTextVisible(True)
    progress_bar.setFormat("Processing...")
    progress_bar.setStyleSheet(
        """
        QProgressBar {
            background-color: #2d2d2d;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            height: 24px;
            text-align: center;
            color: #ffffff;
            font-size: 12px;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2196F3, stop:1 #1976D2);
            border-radius: 7px;
        }
    """
    )
    return progress_bar
