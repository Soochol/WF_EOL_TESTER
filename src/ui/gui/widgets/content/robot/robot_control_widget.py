"""Robot Control Widget - Modern Design

Modern robot control widget with Material Design 3 styling.
Features 2-column grid layout for space efficiency.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtWidgets import (
    QGridLayout,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.simple_reloadable_container import SimpleReloadableContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.styling import ThemeManager

# Local folder imports
from .event_handlers import RobotEventHandlers
from .state_manager import RobotControlState
from .ui_components import (
    ConnectionGroup,
    EmergencyControlGroup,
    MotionControlGroup,
    ServoControlGroup,
    StatusDisplayGroup,
    create_modern_progress_bar,
)


class RobotControlWidget(QWidget):
    """
    Modern robot control widget with 2-column grid layout.

    Layout Structure:
    ┌─────────────────────────────────────┐
    │  Row 1: Status Card (full width)    │
    ├─────────────────────────────────────┤
    │  Row 2: Connection | Servo Control  │
    ├─────────────────────────────────────┤
    │  Row 3: Motion Control (full width) │
    ├─────────────────────────────────────┤
    │  Row 4: Emergency (full width)      │
    └─────────────────────────────────────┘
    """

    def __init__(
        self,
        container: SimpleReloadableContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.gui_state_manager = state_manager

        # Get robot service
        self.robot_service = container.hardware_service_facade().robot_service

        # Initialize components
        self.theme_manager = ThemeManager()
        self.robot_state = RobotControlState()
        self.event_handlers = RobotEventHandlers(
            robot_service=self.robot_service,
            state=self.robot_state,
            axis_id=0  # Primary axis
        )

        # UI component groups
        self.status_group = StatusDisplayGroup(self.robot_state)
        self.connection_group = ConnectionGroup(self.event_handlers)
        self.servo_group = ServoControlGroup(self.event_handlers)
        self.motion_group = MotionControlGroup(self.event_handlers, self.theme_manager)
        self.emergency_group = EmergencyControlGroup(self.event_handlers)

        # Button references for state management
        self._button_refs: Dict[str, Optional[QPushButton]] = {}

        # Progress bar
        self.progress_bar: Optional[QProgressBar] = None

        # Setup UI and connections
        self._setup_ui()
        self._setup_connections()
        self._setup_state_connections()

    def _setup_ui(self) -> None:
        """Setup modern UI with 2-column grid layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Apply dark background
        self.setStyleSheet(
            """
            RobotControlWidget {
                background-color: #1e1e1e;
            }
        """
        )

        # Grid layout for cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)

        # Row 1: Status Card (full width)
        status_widget = self.status_group.create()
        grid_layout.addWidget(status_widget, 0, 0, 1, 2)  # row 0, col 0, span 1 row, 2 cols

        # Row 2: Connection (left) | Servo Control (right)
        connection_widget = self.connection_group.create()
        grid_layout.addWidget(connection_widget, 1, 0)  # row 1, col 0

        servo_widget = self.servo_group.create()
        grid_layout.addWidget(servo_widget, 1, 1)  # row 1, col 1

        # Row 3: Motion Control (full width)
        motion_widget = self.motion_group.create()
        grid_layout.addWidget(motion_widget, 2, 0, 1, 2)  # row 2, col 0, span 1 row, 2 cols

        # Row 4: Emergency (full width)
        emergency_widget = self.emergency_group.create()
        grid_layout.addWidget(emergency_widget, 3, 0, 1, 2)  # row 3, col 0, span 1 row, 2 cols

        main_layout.addLayout(grid_layout)

        # Progress bar
        self.progress_bar = create_modern_progress_bar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Add stretch to push content to top
        main_layout.addStretch()

        # Store button references for state management
        self._button_refs.update(self.connection_group.get_buttons())
        self._button_refs.update(self.servo_group.get_buttons())
        self._button_refs.update(self.motion_group.get_buttons())
        self._button_refs.update(self.emergency_group.get_buttons())

    def _setup_connections(self) -> None:
        """Setup signal connections between components"""
        # Connect event handler result signals to UI feedback
        self.event_handlers.connect_completed.connect(self._on_connect_completed)
        self.event_handlers.disconnect_completed.connect(self._on_disconnect_completed)
        self.event_handlers.servo_on_completed.connect(self._on_servo_on_completed)
        self.event_handlers.servo_off_completed.connect(self._on_servo_off_completed)
        self.event_handlers.home_completed.connect(self._on_home_completed)
        self.event_handlers.move_completed.connect(self._on_move_completed)
        self.event_handlers.position_read.connect(self._on_position_read)
        self.event_handlers.stop_completed.connect(self._on_stop_completed)
        self.event_handlers.emergency_stop_completed.connect(self._on_emergency_stop_completed)
        self.event_handlers.load_ratio_read.connect(self._on_load_ratio_read)
        self.event_handlers.torque_read.connect(self._on_torque_read)

    def _setup_state_connections(self) -> None:
        """Setup connections between state manager and UI components"""
        # Connect button state changes to actual buttons
        self.robot_state.button_state_changed.connect(self._on_button_state_changed)

        # Connect status changes to GUI state manager and UI feedback
        self.robot_state.status_changed.connect(self._on_status_changed)

        # Connect progress indication
        self.robot_state.progress_changed.connect(self._on_progress_changed)

    def _on_button_state_changed(self, button_name: str, enabled: bool) -> None:
        """Handle button state changes from state manager"""
        if button_name in self._button_refs:
            button = self._button_refs[button_name]
            if button:
                button.setEnabled(enabled)
                button.repaint()
                button.update()

    def _on_status_changed(self, message: str, status_type: str) -> None:
        """Handle status changes"""
        # Log to GUI state manager
        if status_type == "error":
            self.gui_state_manager.add_log_message("ERROR", "ROBOT", message)
        elif status_type == "warning":
            self.gui_state_manager.add_log_message("WARNING", "ROBOT", message)
        else:
            self.gui_state_manager.add_log_message("INFO", "ROBOT", message)

    def _on_progress_changed(self, visible: bool, message: str) -> None:
        """Handle progress indicator changes"""
        if self.progress_bar:
            self.progress_bar.setVisible(visible)
            if visible:
                self.progress_bar.setFormat(message)

    # Event handler result callbacks
    def _on_connect_completed(self, success: bool, message: str) -> None:
        """Handle connect operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "ROBOT", message)
        else:
            QMessageBox.critical(self, "Connection Error", message)

    def _on_disconnect_completed(self, success: bool, message: str) -> None:
        """Handle disconnect operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "ROBOT", message)
        else:
            QMessageBox.critical(self, "Disconnect Error", message)

    def _on_servo_on_completed(self, success: bool, message: str) -> None:
        """Handle servo on operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "ROBOT", message)
        else:
            QMessageBox.critical(self, "Servo Error", message)

    def _on_servo_off_completed(self, success: bool, message: str) -> None:
        """Handle servo off operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "ROBOT", message)
        else:
            QMessageBox.critical(self, "Servo Error", message)

    def _on_home_completed(self, success: bool, message: str) -> None:
        """Handle home operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "ROBOT", message)
        else:
            QMessageBox.critical(self, "Home Error", message)

    def _on_move_completed(self, success: bool, message: str) -> None:
        """Handle move operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "ROBOT", message)
        else:
            QMessageBox.critical(self, "Move Error", message)

    def _on_position_read(self, position: float) -> None:
        """Handle position read result"""
        self.gui_state_manager.add_log_message(
            "INFO",
            "ROBOT",
            f"Current position: {position:.2f} μm"
        )

    def _on_stop_completed(self, success: bool, message: str) -> None:
        """Handle stop operation result"""
        if success:
            self.gui_state_manager.add_log_message("WARNING", "ROBOT", message)
        else:
            QMessageBox.critical(self, "Stop Error", message)

    def _on_emergency_stop_completed(self, success: bool, message: str) -> None:
        """Handle emergency stop operation result"""
        if success:
            QMessageBox.critical(self, "EMERGENCY STOP", message)
        else:
            QMessageBox.critical(self, "Emergency Stop Error", message)

    def _on_load_ratio_read(self, load_ratio: float) -> None:
        """Handle load ratio read result"""
        if load_ratio < 0:
            self.gui_state_manager.add_log_message(
                "ERROR",
                "ROBOT",
                "Failed to read load ratio"
            )
            if self.motion_group.load_ratio_label:
                self.motion_group.load_ratio_label.setText("Error")
                self.motion_group.load_ratio_label.setStyleSheet("""
                    QLabel {
                        color: #FF5722;
                        font-size: 13px;
                        padding: 8px;
                        background-color: rgba(255, 87, 34, 0.1);
                        border-radius: 6px;
                        border: 1px solid rgba(255, 87, 34, 0.3);
                    }
                """)
        else:
            self.gui_state_manager.add_log_message(
                "INFO",
                "ROBOT",
                f"Load ratio: {load_ratio:.2f}%"
            )
            if self.motion_group.load_ratio_label:
                self.motion_group.load_ratio_label.setText(f"{load_ratio:.2f}%")
                self.motion_group.load_ratio_label.setStyleSheet("""
                    QLabel {
                        color: #00D9A5;
                        font-size: 13px;
                        font-weight: 600;
                        padding: 8px;
                        background-color: rgba(0, 217, 165, 0.1);
                        border-radius: 6px;
                        border: 1px solid rgba(0, 217, 165, 0.3);
                    }
                """)

    def _on_torque_read(self, torque: float) -> None:
        """Handle torque read result"""
        if torque < 0:
            self.gui_state_manager.add_log_message(
                "ERROR",
                "ROBOT",
                "Failed to read torque"
            )
            if self.motion_group.torque_label:
                self.motion_group.torque_label.setText("Error")
                self.motion_group.torque_label.setStyleSheet("""
                    QLabel {
                        color: #FF5722;
                        font-size: 13px;
                        padding: 8px;
                        background-color: rgba(255, 87, 34, 0.1);
                        border-radius: 6px;
                        border: 1px solid rgba(255, 87, 34, 0.3);
                    }
                """)
        else:
            self.gui_state_manager.add_log_message(
                "INFO",
                "ROBOT",
                f"Torque: {torque:.2f}"
            )
            if self.motion_group.torque_label:
                self.motion_group.torque_label.setText(f"{torque:.2f}")
                self.motion_group.torque_label.setStyleSheet("""
                    QLabel {
                        color: #00D9A5;
                        font-size: 13px;
                        font-weight: 600;
                        padding: 8px;
                        background-color: rgba(0, 217, 165, 0.1);
                        border-radius: 6px;
                        border: 1px solid rgba(0, 217, 165, 0.3);
                    }
                """)
