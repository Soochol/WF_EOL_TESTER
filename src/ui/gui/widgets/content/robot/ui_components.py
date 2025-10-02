"""Robot UI Components - Modern Design

Factory and builder classes for creating modern robot control UI components.
Uses Material Design 3 components for consistent styling.
"""

# Standard library imports
from typing import Dict, Optional

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
from .event_handlers import RobotEventHandlers
from .modern_components import ModernButton, ModernCard, StatusPill
from .state_manager import RobotControlState


class StatusDisplayGroup:
    """Status display group with StatusPills"""

    def __init__(self, state: RobotControlState):
        self.state = state
        self.connection_pill: Optional[StatusPill] = None
        self.position_pill: Optional[StatusPill] = None
        self.servo_pill: Optional[StatusPill] = None

    def create(self) -> ModernCard:
        """Create status display card with pills"""
        card = ModernCard("📊 Robot Status")

        # Pills layout
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(12)

        # Connection status pill
        self.connection_pill = StatusPill("Connection:")
        self.connection_pill.set_status("Disconnected", "#FF5722")
        pills_layout.addWidget(self.connection_pill)

        # Position status pill
        self.position_pill = StatusPill("Position:")
        self.position_pill.set_status("Unknown", "#cccccc")
        pills_layout.addWidget(self.position_pill)

        # Servo status pill
        self.servo_pill = StatusPill("Servo:")
        self.servo_pill.set_status("Disabled", "#FFC107")
        pills_layout.addWidget(self.servo_pill)

        pills_widget = QWidget()
        pills_widget.setLayout(pills_layout)
        card.add_widget(pills_widget)

        # Connect to state changes
        self.state.connection_changed.connect(self._on_connection_changed)
        self.state.position_changed.connect(self._on_position_changed)
        self.state.servo_changed.connect(self._on_servo_changed)

        return card

    def _on_connection_changed(self, connected: bool) -> None:
        """Update connection status pill"""
        if self.connection_pill:
            if connected:
                self.connection_pill.set_status("Connected", "#00D9A5")
            else:
                self.connection_pill.set_status("Disconnected", "#FF5722")

    def _on_position_changed(self, position: float) -> None:
        """Update position pill"""
        if self.position_pill:
            self.position_pill.set_status(f"{position:.2f} μm", "#2196F3")

    def _on_servo_changed(self, enabled: bool) -> None:
        """Update servo status pill"""
        if self.servo_pill:
            if enabled:
                self.servo_pill.set_status("Enabled", "#00D9A5")
            else:
                self.servo_pill.set_status("Disabled", "#FFC107")


class ConnectionGroup:
    """Connection control group"""

    def __init__(self, event_handlers: RobotEventHandlers):
        self.event_handlers = event_handlers
        self.connect_btn: Optional[QPushButton] = None
        self.disconnect_btn: Optional[QPushButton] = None

    def create(self) -> ModernCard:
        """Create connection card with modern buttons"""
        card = ModernCard("🔌 Connection")

        # Buttons layout
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.connect_btn = ModernButton("Connect", "play", "success")
        self.disconnect_btn = ModernButton("Disconnect", "stop", "danger")

        self.connect_btn.clicked.connect(self.event_handlers.on_connect_clicked)
        self.disconnect_btn.clicked.connect(self.event_handlers.on_disconnect_clicked)

        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)

        buttons_widget = QWidget()
        buttons_widget.setLayout(layout)
        card.add_widget(buttons_widget)

        return card

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references"""
        return {
            "connect": self.connect_btn,
            "disconnect": self.disconnect_btn,
        }


class ServoControlGroup:
    """Servo control group"""

    def __init__(self, event_handlers: RobotEventHandlers):
        self.event_handlers = event_handlers
        self.servo_on_btn: Optional[QPushButton] = None
        self.servo_off_btn: Optional[QPushButton] = None

    def create(self) -> ModernCard:
        """Create servo control card"""
        card = ModernCard("⚙️ Servo Control")

        # Buttons layout
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.servo_on_btn = ModernButton("Servo ON", "play", "success")
        self.servo_off_btn = ModernButton("Servo OFF", "pause", "warning")

        self.servo_on_btn.clicked.connect(self.event_handlers.on_servo_on_clicked)
        self.servo_off_btn.clicked.connect(self.event_handlers.on_servo_off_clicked)

        layout.addWidget(self.servo_on_btn)
        layout.addWidget(self.servo_off_btn)

        buttons_widget = QWidget()
        buttons_widget.setLayout(layout)
        card.add_widget(buttons_widget)

        return card

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references"""
        return {
            "servo_on": self.servo_on_btn,
            "servo_off": self.servo_off_btn,
        }


class MotionControlGroup:
    """Motion control group"""

    def __init__(self, event_handlers: RobotEventHandlers, theme_manager: ThemeManager):
        self.event_handlers = event_handlers
        self.theme_manager = theme_manager

        # Buttons
        self.home_btn: Optional[QPushButton] = None
        self.abs_move_btn: Optional[QPushButton] = None
        self.rel_move_btn: Optional[QPushButton] = None
        self.get_pos_btn: Optional[QPushButton] = None
        self.stop_btn: Optional[QPushButton] = None
        self.get_load_ratio_btn: Optional[QPushButton] = None
        self.get_torque_btn: Optional[QPushButton] = None

        # Input fields
        self.abs_pos_input: Optional[QDoubleSpinBox] = None
        self.abs_vel_input: Optional[QDoubleSpinBox] = None
        self.rel_pos_input: Optional[QDoubleSpinBox] = None
        self.rel_vel_input: Optional[QDoubleSpinBox] = None

        # Result labels
        self.load_ratio_label: Optional[QLabel] = None
        self.torque_label: Optional[QLabel] = None

    def create(self) -> ModernCard:
        """Create motion control card"""
        card = ModernCard("🎮 Motion Control")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        # Home button
        self.home_btn = ModernButton("Home Axis", "home", "primary")
        self.home_btn.clicked.connect(self.event_handlers.on_home_clicked)
        main_layout.addWidget(self.home_btn)

        # Absolute and Relative move in 2 columns
        move_grid = QGridLayout()
        move_grid.setSpacing(12)

        # Absolute Move (Left column)
        abs_widget = self._create_move_widget("Absolute Move", "abs")
        move_grid.addWidget(abs_widget, 0, 0)

        # Relative Move (Right column)
        rel_widget = self._create_move_widget("Relative Move", "rel")
        move_grid.addWidget(rel_widget, 0, 1)

        move_container = QWidget()
        move_container.setLayout(move_grid)
        main_layout.addWidget(move_container)

        # Position and Stop controls
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        self.get_pos_btn = ModernButton("Get Position", "target", "secondary")
        self.stop_btn = ModernButton("Stop Motion", "stop", "danger")

        self.get_pos_btn.clicked.connect(self.event_handlers.on_get_position_clicked)
        self.stop_btn.clicked.connect(self.event_handlers.on_stop_clicked)

        control_layout.addWidget(self.get_pos_btn)
        control_layout.addWidget(self.stop_btn)

        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        main_layout.addWidget(control_widget)

        # Diagnostic controls
        diagnostic_layout = QVBoxLayout()
        diagnostic_layout.setSpacing(8)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.get_load_ratio_btn = ModernButton("Get Load Ratio", "chart-line", "info")
        self.get_torque_btn = ModernButton("Get Torque", "bolt", "info")

        self.get_load_ratio_btn.clicked.connect(self.event_handlers.on_get_load_ratio_clicked)
        self.get_torque_btn.clicked.connect(self.event_handlers.on_get_torque_clicked)

        buttons_layout.addWidget(self.get_load_ratio_btn)
        buttons_layout.addWidget(self.get_torque_btn)

        diagnostic_layout.addLayout(buttons_layout)

        # Result labels layout
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(12)

        self.load_ratio_label = QLabel("--")
        self.load_ratio_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 13px;
                padding: 8px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        self.load_ratio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.torque_label = QLabel("--")
        self.torque_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 13px;
                padding: 8px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        self.torque_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        labels_layout.addWidget(self.load_ratio_label)
        labels_layout.addWidget(self.torque_label)

        diagnostic_layout.addLayout(labels_layout)

        diagnostic_widget = QWidget()
        diagnostic_widget.setLayout(diagnostic_layout)
        main_layout.addWidget(diagnostic_widget)

        container = QWidget()
        container.setLayout(main_layout)
        card.add_widget(container)

        return card

    def _create_move_widget(self, title: str, move_type: str) -> QWidget:
        """Create absolute or relative move widget"""
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 12px;
            }}
        """)

        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            """
            font-size: 13px;
            font-weight: 600;
            color: #cccccc;
            background: transparent;
            border: none;
        """
        )
        layout.addWidget(title_label)

        # Grid layout for inputs
        grid = QGridLayout()
        grid.setSpacing(8)

        # Position/Distance input
        label_text = "Position (μm):" if move_type == "abs" else "Distance (μm):"
        pos_label = QLabel(label_text)
        pos_label.setStyleSheet("color: #999999; font-size: 12px;")
        pos_input = self._create_input_spinbox(default=10000.0)

        # Velocity input
        vel_label = QLabel("Velocity (μm/s):")
        vel_label.setStyleSheet("color: #999999; font-size: 12px;")
        vel_input = self._create_input_spinbox(min_val=1.0, max_val=100000.0, default=1000.0, decimals=1)

        # Move button
        move_btn = ModernButton(f"Move {move_type.upper()}", "arrow-right", "secondary")

        if move_type == "abs":
            self.abs_pos_input = pos_input
            self.abs_vel_input = vel_input
            self.abs_move_btn = move_btn
            move_btn.clicked.connect(self._on_abs_move_clicked)
        else:
            self.rel_pos_input = pos_input
            self.rel_vel_input = vel_input
            self.rel_move_btn = move_btn
            move_btn.clicked.connect(self._on_rel_move_clicked)

        grid.addWidget(pos_label, 0, 0)
        grid.addWidget(pos_input, 0, 1)
        grid.addWidget(vel_label, 1, 0)
        grid.addWidget(vel_input, 1, 1)

        layout.addLayout(grid)
        layout.addWidget(move_btn)

        return container

    def _create_input_spinbox(
        self,
        min_val: float = 0.0,
        max_val: float = 500000.0,
        default: float = 10000.0,
        decimals: int = 2
    ) -> QDoubleSpinBox:
        """Create styled double spinbox"""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setDecimals(decimals)
        spinbox.setValue(default)
        spinbox.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
                font-size: 12px;
            }}
            QDoubleSpinBox:focus {{
                border: 2px solid #2196F3;
                background-color: rgba(33, 150, 243, 0.1);
            }}
        """)
        return spinbox

    def _on_abs_move_clicked(self) -> None:
        """Handle absolute move button click"""
        if self.abs_pos_input and self.abs_vel_input:
            position = self.abs_pos_input.value()
            velocity = self.abs_vel_input.value()
            self.event_handlers.on_move_absolute(position, velocity)

    def _on_rel_move_clicked(self) -> None:
        """Handle relative move button click"""
        if self.rel_pos_input and self.rel_vel_input:
            distance = self.rel_pos_input.value()
            velocity = self.rel_vel_input.value()
            self.event_handlers.on_move_relative(distance, velocity)

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references"""
        return {
            "home": self.home_btn,
            "move_abs": self.abs_move_btn,
            "move_rel": self.rel_move_btn,
            "get_position": self.get_pos_btn,
            "stop": self.stop_btn,
            "get_load_ratio": self.get_load_ratio_btn,
            "get_torque": self.get_torque_btn,
        }


class EmergencyControlGroup:
    """Emergency control group"""

    def __init__(self, event_handlers: RobotEventHandlers):
        self.event_handlers = event_handlers
        self.emergency_btn: Optional[QPushButton] = None

    def create(self) -> ModernCard:
        """Create emergency control card"""
        card = ModernCard("🚨 Emergency")

        # Large emergency button
        self.emergency_btn = ModernButton("EMERGENCY STOP", "emergency", "danger")
        self.emergency_btn.setMinimumHeight(55)
        self.emergency_btn.clicked.connect(self.event_handlers.on_emergency_stop_clicked)

        card.add_widget(self.emergency_btn)

        return card

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references"""
        return {"emergency": self.emergency_btn}


def create_modern_progress_bar() -> QProgressBar:
    """Create modern styled progress bar"""
    progress = QProgressBar()
    progress.setMinimum(0)
    progress.setMaximum(0)  # Indeterminate
    progress.setTextVisible(True)
    progress.setFixedHeight(35)
    progress.setStyleSheet(
        """
        QProgressBar {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 17px;
            text-align: center;
            color: #ffffff;
            font-weight: 600;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2196F3, stop:1 #00D9A5);
            border-radius: 16px;
        }
    """
    )
    return progress
