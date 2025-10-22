"""
Modern Test Control Widget

Beautiful card-based test control interface with Material Design 3.
"""

# Standard library imports
import logging
from typing import Optional

# Third-party imports
from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from application.services.industrial.tower_lamp_service import SystemStatus
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.svg_icon_provider import get_svg_icon_provider
from ui.gui.widgets.log_viewer_widget import LogViewerWidget


class ModernCard(QFrame):
    """Glassmorphism card container"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setup_ui(title)

    def setup_ui(self, title: str):
        """Setup card UI"""
        self.setStyleSheet(
            """
            ModernCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 12px;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(6)  # Reduced from 10 to 6
        layout.setContentsMargins(10, 10, 10, 10)  # Reduced from 15 to 10

        if title:
            # Card title
            title_label = QLabel(title)
            title_label.setStyleSheet(
                """
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 6px;
            """
            )
            layout.addWidget(title_label)

        self.content_layout = layout

    def add_widget(self, widget):
        """Add widget to card content"""
        self.content_layout.addWidget(widget)


class ModernButton(QPushButton):
    """Material Design 3 button"""

    def __init__(self, text: str, icon_name: str = "", color: str = "primary", parent=None):
        super().__init__(text, parent)
        self.color_type = color
        self.icon_name = icon_name
        self.setup_ui()

    def setup_ui(self):
        """Setup button styling"""
        # Set SVG icon
        if self.icon_name:
            svg_provider = get_svg_icon_provider()
            icon = svg_provider.get_icon(self.icon_name, size=20)
            if not icon.isNull():
                self.setIcon(icon)
                self.setIconSize(QSize(20, 20))

        # Color schemes
        colors = {
            "primary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976D2)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #42A5F5, stop:1 #2196F3)",
                "pressed": "#1565C0",
            },
            "success": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00D9A5, stop:1 #00BFA5)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1DE9B6, stop:1 #00D9A5)",
                "pressed": "#00897B",
            },
            "warning": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF9800, stop:1 #F57C00)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFB74D, stop:1 #FF9800)",
                "pressed": "#E65100",
            },
            "danger": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F44336, stop:1 #D32F2F)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #EF5350, stop:1 #F44336)",
                "pressed": "#B71C1C",
            },
            "secondary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #607D8B, stop:1 #455A64)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #78909C, stop:1 #607D8B)",
                "pressed": "#37474F",
            },
        }

        color_scheme = colors.get(self.color_type, colors["primary"])

        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {color_scheme["bg"]};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 600;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background: {color_scheme["hover"]};
            }}
            QPushButton:pressed {{
                background-color: {color_scheme["pressed"]};
            }}
            QPushButton:disabled {{
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.3);
            }}
        """
        )

        self.setCursor(Qt.CursorShape.PointingHandCursor)


class StatusPill(QWidget):
    """Animated status indicator"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_text = "Ready"
        self.status_color = "#00D9A5"
        self.setup_ui()

    def setup_ui(self):
        """Setup status pill UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)

        # Status dot
        self.dot_label = QLabel("●")
        self.dot_label.setStyleSheet(f"color: {self.status_color}; font-size: 14px;")
        layout.addWidget(self.dot_label)

        # Status text
        self.text_label = QLabel(self.status_text)
        self.text_label.setStyleSheet(
            """
            font-size: 13px;
            font-weight: 600;
            color: #ffffff;
        """
        )
        layout.addWidget(self.text_label)

        self.update_style()

    def set_status(self, text: str, color: str):
        """Update status"""
        self.status_text = text
        self.status_color = color
        self.text_label.setText(text)
        self.dot_label.setStyleSheet(f"color: {color}; font-size: 14px;")
        self.update_style()

    def update_style(self):
        """Update pill background"""
        self.setStyleSheet(
            f"""
            StatusPill {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.status_color}20,
                    stop:1 {self.status_color}40);
                border: 1px solid {self.status_color}60;
                border-radius: 20px;
            }}
        """
        )


class ModernTestControlWidget(QWidget):
    """
    Modern test control widget with Material Design 3.
    """

    # Signals
    test_started = Signal()
    test_stopped = Signal()
    test_paused = Signal()
    robot_home_requested = Signal()
    emergency_stop_requested = Signal()

    # Logger
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        executor_thread=None,  # TestExecutorThread for async operations
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.executor_thread = executor_thread

        # Get robot service and industrial system manager from container
        self.robot_service = container.hardware_service_facade().robot_service
        self.industrial_system_manager = container.industrial_system_manager()
        self.axis_id = 0  # Primary axis

        # Get digital I/O setup service and configuration service for brake release
        self.digital_io_setup_service = container.digital_io_setup_service()
        self.configuration_service = container.configuration_service()

        # Serial number management (popup-based)
        self.current_serial_number = ""
        self.require_serial_popup = self._get_serial_popup_setting()

        # Initialize widget attributes (defined before setup_ui)
        self.test_type_combo: QComboBox
        self.start_btn: ModernButton
        self.pause_btn: ModernButton
        self.stop_btn: ModernButton
        self.clear_error_btn: ModernButton
        self.home_btn: ModernButton
        self.emergency_btn: ModernButton
        self.status_pill: StatusPill
        self.progress_bar: QProgressBar
        self.log_viewer: LogViewerWidget

        self.setup_ui()
        self.setup_connections()
        self.setup_status_callback()

    def setup_status_callback(self):
        """Register callback for system status changes"""
        if self.industrial_system_manager:
            self.industrial_system_manager.register_status_change_callback(
                self._on_system_status_changed
            )

    def _on_system_status_changed(self, status: SystemStatus):
        """
        Called when system status changes via callback

        Args:
            status: New system status
        """
        # Third-party imports
        from loguru import logger

        # Only enable Clear Error for EMERGENCY and SAFETY issues
        # Test errors (SYSTEM_ERROR) should NOT require clearing - user can retry immediately
        emergency_states = [
            SystemStatus.EMERGENCY_STOP,  # Emergency Stop only (updated enum name)
            SystemStatus.SAFETY_VIOLATION,  # Safety issues only
        ]

        # Enable button only for emergency/safety states, disable for test errors
        should_enable = status in emergency_states
        self.clear_error_btn.setEnabled(should_enable)

        # Log for debugging
        logger.debug(
            f"🔘 Clear Error button auto-updated: {'ENABLED' if should_enable else 'DISABLED'} (status: {status.value})"
        )

    def _get_serial_popup_setting(self) -> bool:
        """Get serial number popup setting from configuration"""
        # Third-party imports
        from loguru import logger

        try:
            if self.container:
                # Try to get from ConfigurationService (preferred method)
                if hasattr(self.container, "configuration_service"):
                    try:
                        config_service = self.container.configuration_service()
                        # Load application config through service
                        # Third-party imports
                        import asyncio

                        app_config = asyncio.run(config_service.load_application_config())
                        result = app_config.gui.require_serial_number_popup
                        logger.debug(f"Serial popup setting from ConfigurationService: {result}")
                        return result
                    except Exception as e:
                        logger.warning(f"Failed to get setting from ConfigurationService: {e}")

                # Fallback: Try container.config (dependency-injector config)
                if hasattr(self.container, "config"):
                    gui_config = self.container.config.gui()
                    result = gui_config.get("require_serial_number_popup", True)
                    logger.debug(f"Serial popup setting from container.config: {result}")
                    return result

                # Fallback: Try _config_dict (legacy)
                if hasattr(self.container, "_config_dict"):
                    config = self.container._config_dict
                    if isinstance(config, dict):
                        gui_config = config.get("gui", {})
                        if isinstance(gui_config, dict):
                            result = gui_config.get("require_serial_number_popup", True)
                            logger.debug(f"Serial popup setting from _config_dict: {result}")
                            return result
        except Exception as e:
            logger.error(f"Error getting serial popup setting: {e}")

        logger.debug("Using default serial popup setting: True")
        return True  # Default: use popup

    def showEvent(self, event):
        """Override showEvent to log geometry when widget is shown"""
        super().showEvent(event)
        # Log geometry after widget is fully shown
        QTimer.singleShot(200, self._log_geometry_info)

    def setup_ui(self):
        """Setup modern UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)  # Reduced from 12 to 8 to save vertical space
        main_layout.setContentsMargins(10, 10, 10, 10)  # Reduced from 15 to 10

        # Apply dark background
        self.setStyleSheet(
            """
            ModernTestControlWidget {
                background-color: #1e1e1e;
            }
        """
        )

        # Configuration Card (no stretch - fixed size)
        config_card = self.create_configuration_card()
        main_layout.addWidget(config_card, stretch=0)

        # Controls Card (no stretch - fixed size)
        controls_card = self.create_controls_card()
        main_layout.addWidget(controls_card, stretch=0)

        # Status & Progress Card (no stretch - fixed size)
        status_card = self.create_status_card()
        main_layout.addWidget(status_card, stretch=0)

        # Log Viewer Card (stretch=1 - takes all remaining space)
        log_card = self.create_log_card()
        main_layout.addWidget(log_card, stretch=1)

    def create_configuration_card(self) -> ModernCard:
        """Create test configuration card"""
        card = ModernCard("📦 Test Configuration")

        # Test Type & Parameters
        params_layout = QHBoxLayout()

        # Test Type
        type_label = QLabel("Test Sequence:")
        type_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems(
            ["EOL Force Test", "Heating Cooling Time Test", "Simple MCU Test"]
        )
        self.test_type_combo.setStyleSheet(
            """
            QComboBox {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
            }
        """
        )

        params_layout.addWidget(type_label)
        params_layout.addWidget(self.test_type_combo)
        params_layout.addStretch()

        card.add_widget(self.create_layout_widget(params_layout))

        return card

    def create_controls_card(self) -> ModernCard:
        """Create test controls card"""
        card = ModernCard("🎮 Test Controls")

        # Main controls row
        main_controls = QHBoxLayout()
        main_controls.setSpacing(12)

        self.start_btn = ModernButton("Start", "play", "success")
        self.pause_btn = ModernButton("Pause", "pause", "warning")
        self.stop_btn = ModernButton("Stop", "stop", "danger")

        main_controls.addWidget(self.start_btn)
        main_controls.addWidget(self.pause_btn)
        main_controls.addWidget(self.stop_btn)

        card.add_widget(self.create_layout_widget(main_controls))

        # Secondary controls row
        secondary_controls = QHBoxLayout()
        secondary_controls.setSpacing(12)

        self.clear_error_btn = ModernButton("Clear Error", "warning", "warning")
        self.clear_error_btn.setEnabled(False)  # Initially disabled
        self.home_btn = ModernButton("Home", "home", "secondary")
        self.emergency_btn = ModernButton("Emergency Stop", "emergency", "danger")

        secondary_controls.addWidget(self.clear_error_btn)
        secondary_controls.addWidget(self.home_btn)
        secondary_controls.addWidget(self.emergency_btn)

        card.add_widget(self.create_layout_widget(secondary_controls))

        return card

    def create_status_card(self) -> ModernCard:
        """Create status and progress card"""
        card = ModernCard("📊 Status & Progress")

        # Status pill
        self.status_pill = StatusPill()
        card.add_widget(self.status_pill)

        # Modern Progress bar with indeterminate animation (like Robot widget)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)  # Hide text inside progress bar
        self.progress_bar.setFixedHeight(28)  # Reduced from 35 to 28
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)  # Normal mode initially (no animation)
        self.progress_bar.setValue(0)

        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 14px;
                text-align: center;
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3,
                    stop:1 #00D9A5);
                border-radius: 13px;
            }
        """
        )
        card.add_widget(self.progress_bar)

        return card

    def start_indeterminate_progress(self):
        """Start indeterminate progress animation (moving bar)"""
        self.progress_bar.setMaximum(0)  # Indeterminate mode - automatic animation

    def stop_indeterminate_progress(self):
        """Stop indeterminate progress animation"""
        self.progress_bar.setMaximum(100)  # Normal mode - fixed progress
        self.progress_bar.setValue(0)

    def create_log_card(self) -> ModernCard:
        """Create log viewer card"""
        card = ModernCard("📝 Test Logs")

        # Log viewer
        self.log_viewer = LogViewerWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        card.add_widget(self.log_viewer)

        return card

    def create_layout_widget(self, layout):
        """Helper to wrap layout in widget"""
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def setup_connections(self):
        """Setup signal connections"""
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.pause_btn.clicked.connect(self.test_paused.emit)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.clear_error_btn.clicked.connect(self._on_clear_error_clicked)
        self.home_btn.clicked.connect(self._on_home_clicked)
        self.emergency_btn.clicked.connect(self._on_emergency_clicked)

    def _on_start_clicked(self):
        """Handle start button click with serial number popup"""
        # Standard library imports
        from datetime import datetime

        # Third-party imports
        from loguru import logger

        # Re-read popup setting from configuration (allows hot-reload without restart)
        self.require_serial_popup = self._get_serial_popup_setting()

        # Show serial number popup if enabled
        if self.require_serial_popup:
            # Local application imports
            from ui.gui.widgets.dialogs.serial_number_dialog import SerialNumberDialog

            dialog = SerialNumberDialog(default_value=self.current_serial_number, parent=self)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.current_serial_number = dialog.get_serial_number()
            else:
                # User cancelled - don't start test
                return
        else:
            # Auto-generate serial number when popup is disabled
            auto_serial = f"AUTO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            self.current_serial_number = auto_serial
            logger.info(f"Auto-generated serial number (popup disabled): {auto_serial}")

        # Start test animation and emit signal
        self.start_indeterminate_progress()
        self.test_started.emit()

    def _on_stop_clicked(self):
        """Handle stop button click"""
        self.stop_indeterminate_progress()
        self.test_stopped.emit()

    def _on_home_clicked(self):
        """Handle home button click - executes actual robot homing operation"""
        # Third-party imports
        from loguru import logger

        logger.info("🏠 HOME button clicked in ModernTestControlWidget")

        # Validate dependencies
        if not self.robot_service:
            logger.error("Robot service not available")
            self.update_test_status("Robot service not initialized", "❌")
            return

        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.update_test_status("Executor thread not initialized", "❌")
            return

        # Update UI state
        self.start_indeterminate_progress()
        self.home_btn.setEnabled(False)
        self.start_btn.setEnabled(False)

        # Submit homing task to executor thread
        logger.debug("Submitting robot home task to executor thread...")
        self.executor_thread.submit_task("robot_home", self._async_home())

    async def _async_home(self) -> None:
        """Async home operation with automatic connection and servo on"""
        # Third-party imports
        from loguru import logger

        # Type guard: robot_service should be available at this point
        if not self.robot_service:
            logger.error("Robot service became unavailable during homing")
            self.update_test_status("Robot service error", "❌")
            self.home_btn.setEnabled(True)
            self.stop_indeterminate_progress()
            return

        try:
            # Step 1: Check and establish connection
            is_connected = await self.robot_service.is_connected()
            if not is_connected:
                logger.info("Robot not connected - connecting automatically...")
                self.update_test_status("Connecting to robot...", "🔌")
                await self.robot_service.connect()
                logger.info("Robot connected successfully")
                self.update_test_status("Robot connected", "✅")

            # Step 2: Reset servo alarm (emergency stop recovery)
            # This is required after emergency stop to clear alarm state
            logger.info("Resetting servo alarm (emergency stop recovery)...")
            self.update_test_status("Resetting alarm...", "🔄")
            await self.robot_service.reset_servo_alarm(self.axis_id)
            logger.info("Servo alarm reset successfully")
            self.update_test_status("Alarm reset", "✅")

            # Step 3: Release brake (Digital Output Ch0 = HIGH)
            # Required to allow motor to physically move
            logger.info("Releasing servo brake (Digital Output Ch0)...")
            self.update_test_status("Releasing brake...", "🔓")
            hardware_config = await self.configuration_service.load_hardware_config()
            await self.digital_io_setup_service.setup_servo_brake_release(hardware_config)
            logger.info("Servo brake released successfully")
            self.update_test_status("Brake released", "✅")

            # Step 4: Check and enable servo
            # Note: Always enable servo to ensure it's ready (idempotent operation)
            logger.info("Ensuring servo is enabled...")
            self.update_test_status("Enabling servo...", "⚙️")
            await self.robot_service.enable_servo(self.axis_id)
            logger.info("Servo enabled successfully")
            self.update_test_status("Servo enabled", "✅")

            # Step 5: Perform homing
            logger.info(f"Starting robot homing for axis {self.axis_id}...")
            self.update_test_status("Homing robot...", "🏠")
            await self.robot_service.home_axis(self.axis_id)

            # Read position after homing
            position = await self.robot_service.get_position(self.axis_id)
            logger.info(f"Robot homing completed successfully - Position: {position:.2f} μm")

            # Update UI state
            self.update_test_status("Robot Homing Completed", "✅")
            self.start_btn.setEnabled(True)

            # Emit success signal
            self.robot_home_requested.emit()

        except Exception as e:
            logger.error(f"Robot homing failed: {e}", exc_info=True)
            self.update_test_status(f"Robot Homing Failed: {str(e)}", "❌")

        finally:
            # Always re-enable home button and stop progress
            logger.debug("Re-enabling home button after homing operation")
            self.home_btn.setEnabled(True)
            self.stop_indeterminate_progress()

    def _on_clear_error_clicked(self):
        """Handle clear error button click - clears error state (Stage 2 of 3-stage clearing)"""
        # Third-party imports
        from loguru import logger

        logger.info("🔧 CLEAR ERROR button clicked in ModernTestControlWidget")

        # Validate dependencies
        if not self.industrial_system_manager:
            logger.error("Industrial System Manager not available")
            self.update_test_status("Industrial System Manager not initialized", "❌")
            return

        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.update_test_status("Executor thread not initialized", "❌")
            return

        # Update UI state
        self.update_test_status("Clearing error...", "⚠️")
        self.clear_error_btn.setEnabled(False)

        # Submit clear error task to executor thread
        logger.debug("Submitting clear error task to executor thread...")
        self.executor_thread.submit_task("clear_error", self._async_clear_error())

    async def _async_clear_error(self) -> None:
        """Async clear error operation"""
        # Third-party imports
        from loguru import logger

        # Type guard: industrial_system_manager should be available at this point
        if not self.industrial_system_manager:
            logger.error("Industrial System Manager became unavailable during clear error")
            self.update_test_status("Industrial System Manager error", "❌")
            self.clear_error_btn.setEnabled(True)
            return

        try:
            logger.info("Clearing error state (3-stage: BLINK→ON→OFF, Stage 2)...")
            await self.industrial_system_manager.clear_error()
            logger.info("Error cleared successfully")

            # Update UI state - do NOT enable START TEST yet!
            # User must perform homing first after emergency stop
            self.update_test_status("Error Cleared - Press HOME to continue", "✅")
            # Keep START TEST disabled until homing is completed
            self.start_btn.setEnabled(False)

        except Exception as e:
            logger.error(f"Failed to clear error: {e}", exc_info=True)
            self.update_test_status(f"Clear Error Failed: {str(e)}", "❌")
            self.clear_error_btn.setEnabled(True)

    def _on_emergency_clicked(self):
        """Handle emergency stop button click"""
        self.stop_indeterminate_progress()
        self.emergency_stop_requested.emit()

    # Public methods for external control
    def handle_test_completed(self, success: bool = True):
        """Handle test completion - stop animation"""
        self.stop_indeterminate_progress()

    def handle_robot_home_completed(self, success: bool = True):
        """Handle robot home completion - stop animation"""
        self.stop_indeterminate_progress()

    # API compatibility methods
    def get_current_serial_number(self) -> str:
        """Get current serial number (API compatibility)"""
        return self.current_serial_number

    def set_serial_number(self, serial: str) -> None:
        """Set serial number programmatically (API compatibility)"""
        self.current_serial_number = serial

    def update_status(self, status: str, color: str = "#00D9A5"):
        """Update status display"""
        self.status_pill.set_status(status, color)

    def update_progress(self, value: int):
        """Update progress bar"""
        if value > 0:
            self.stop_indeterminate_progress()
        self.progress_bar.setValue(value)

    def update_test_status(
        self, status: str, icon: str = "status_ready", progress: Optional[int] = None
    ):
        """Update test status display (API compatibility method)"""
        # Map icon to color
        color_map = {
            "status_ready": "#00D9A5",
            "status_running": "#2196F3",
            "status_warning": "#FF9800",
            "status_error": "#F44336",
        }
        color = color_map.get(icon, "#00D9A5")
        self.status_pill.set_status(status, color)

        if progress is not None:
            # Stop indeterminate animation when real progress is available
            if progress > 0:
                self.stop_indeterminate_progress()
            self.progress_bar.setValue(progress)
        else:
            # Start indeterminate animation if no progress provided and running
            if icon == "status_running" and self.progress_bar.value() == 0:
                self.start_indeterminate_progress()

    def update_test_progress(self, progress: int, status_text: Optional[str] = None):
        """Update only the progress bar (API compatibility method)"""
        if progress > 0:
            self.stop_indeterminate_progress()
        self.progress_bar.setValue(progress)
        if status_text:
            self.status_pill.text_label.setText(status_text)

    def disable_start_button(self):
        """Disable START TEST button (API compatibility method)"""
        self.start_btn.setEnabled(False)

    def enable_start_button(self):
        """Enable START TEST button (API compatibility method)"""
        self.start_btn.setEnabled(True)

    def disable_home_button(self):
        """Disable HOME button (API compatibility method)"""
        self.home_btn.setEnabled(False)

    def enable_home_button(self):
        """Enable HOME button (API compatibility method)"""
        self.home_btn.setEnabled(True)

    def enable_clear_error_button(self):
        """Enable CLEAR ERROR button (API compatibility method)"""
        self.clear_error_btn.setEnabled(True)

    def disable_clear_error_button(self):
        """Disable CLEAR ERROR button (API compatibility method)"""
        self.clear_error_btn.setEnabled(False)

    # Property accessors for backward compatibility
    @property
    def sequence_combo(self):
        """Get sequence combo box (backward compatibility)"""
        return self.test_type_combo

    def _log_geometry_info(self) -> None:
        """Log screen resolution and widget geometry information for debugging"""
        try:
            # Use loguru for consistency with other GUI logs
            # Third-party imports
            from loguru import logger

            # Geometry debug logging removed for cleaner output
            pass

        except Exception as e:
            # Third-party imports
            from loguru import logger

            logger.error(f"Error logging geometry info: {e}", exc_info=True)
            logger.error(f"Error logging geometry info: {e}", exc_info=True)
