"""MCU Control Widget - Modern Design

Modern MCU control widget with Material Design 3 styling.
Features vertical layout with grouped controls.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtWidgets import (
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.simple_reloadable_container import SimpleReloadableContainer
from ui.gui.services.gui_state_manager import GUIStateManager

# Local folder imports
from .event_handlers import MCUEventHandlers
from .state_manager import MCUControlState
from .ui_components import (
    AdvancedControlGroup,
    ConnectionGroup,
    StatusDisplayGroup,
    TemperatureControlGroup,
    create_modern_progress_bar,
)


class MCUControlWidget(QWidget):
    """
    Modern MCU control widget with vertical layout.

    Layout Structure:
    ┌─────────────────────────────────────┐
    │  Row 1: Status Card (full width)    │
    ├─────────────────────────────────────┤
    │  Row 2: Connection Control          │
    ├─────────────────────────────────────┤
    │  Row 3: Temperature Control         │
    ├─────────────────────────────────────┤
    │  Row 4: Advanced Control            │
    └─────────────────────────────────────┘
    """

    def __init__(
        self,
        container: SimpleReloadableContainer,
        state_manager: GUIStateManager,
        executor_thread=None,  # ✅ TestExecutorThread for unified execution
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.gui_state_manager = state_manager
        self.executor_thread = executor_thread  # ✅ Store executor thread

        # Get MCU service
        self.mcu_service = container.hardware_service_facade().mcu_service

        # Initialize components
        self.mcu_state = MCUControlState()
        self.event_handlers = MCUEventHandlers(
            mcu_service=self.mcu_service,
            state=self.mcu_state,
            executor_thread=executor_thread,  # ✅ Pass executor to event handlers
        )

        # UI component groups
        self.status_group = StatusDisplayGroup(self.mcu_state)
        self.connection_group = ConnectionGroup(self.event_handlers)
        self.temperature_group = TemperatureControlGroup(self.event_handlers)
        self.advanced_group = AdvancedControlGroup(self.event_handlers)

        # Button references for state management
        self._button_refs: Dict[str, Optional[QPushButton]] = {}

        # Progress bar
        self.progress_bar: Optional[QProgressBar] = None

        # Setup UI and connections
        self._setup_ui()
        self._setup_connections()
        self._setup_state_connections()

    def _setup_ui(self) -> None:
        """Setup modern UI with 1-column layout and scroll area"""
        # Main widget layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Apply dark background
        self.setStyleSheet(
            """
            MCUControlWidget {
                background-color: #1e1e1e;
            }
        """
        )

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Create content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Create all cards in vertical layout
        status_widget = self.status_group.create()
        content_layout.addWidget(status_widget)

        connection_widget = self.connection_group.create()
        content_layout.addWidget(connection_widget)

        temperature_widget = self.temperature_group.create()
        content_layout.addWidget(temperature_widget)

        advanced_widget = self.advanced_group.create()
        content_layout.addWidget(advanced_widget)

        # Progress bar
        self.progress_bar = create_modern_progress_bar()
        self.progress_bar.setVisible(False)
        content_layout.addWidget(self.progress_bar)

        # Add stretch to push content to top
        content_layout.addStretch()

        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Store button references for state management
        self._button_refs.update(self.connection_group.get_buttons())
        self._button_refs.update(self.temperature_group.get_buttons())
        self._button_refs.update(self.advanced_group.get_buttons())

    def _setup_connections(self) -> None:
        """Setup signal connections between components"""
        # Connect event handler result signals to UI feedback
        self.event_handlers.connect_completed.connect(self._on_connect_completed)
        self.event_handlers.disconnect_completed.connect(self._on_disconnect_completed)
        self.event_handlers.temperature_read.connect(self._on_temperature_read)
        self.event_handlers.test_mode_completed.connect(self._on_test_mode_completed)
        self.event_handlers.operating_temp_set.connect(self._on_operating_temp_set)
        self.event_handlers.cooling_temp_set.connect(self._on_cooling_temp_set)
        self.event_handlers.upper_temp_set.connect(self._on_upper_temp_set)
        self.event_handlers.fan_speed_set.connect(self._on_fan_speed_set)
        self.event_handlers.boot_wait_completed.connect(self._on_boot_wait_completed)
        self.event_handlers.heating_completed.connect(self._on_heating_completed)
        self.event_handlers.cooling_completed.connect(self._on_cooling_completed)

    def _setup_state_connections(self) -> None:
        """Setup connections between state manager and UI components"""
        # Connect button state changes to actual buttons
        self.mcu_state.button_state_changed.connect(self._on_button_state_changed)

        # Connect status changes to GUI state manager and UI feedback
        self.mcu_state.status_changed.connect(self._on_status_changed)

        # Connect progress indication
        self.mcu_state.progress_changed.connect(self._on_progress_changed)

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
            self.gui_state_manager.add_log_message("ERROR", "MCU", message)
        elif status_type == "warning":
            self.gui_state_manager.add_log_message("WARNING", "MCU", message)
        else:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)

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
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Connection Error", message)

    def _on_disconnect_completed(self, success: bool, message: str) -> None:
        """Handle disconnect operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Disconnect Error", message)

    def _on_temperature_read(self, temperature: float) -> None:
        """Handle temperature read result"""
        if temperature < -900:  # Error indicator
            self.gui_state_manager.add_log_message(
                "ERROR",
                "MCU",
                "Failed to read temperature"
            )
            if self.temperature_group.current_temp_label:
                self.temperature_group.current_temp_label.setText("Error")
                self.temperature_group.current_temp_label.setStyleSheet("""
                    QLabel {
                        color: #FF5722;
                        font-size: 14px;
                        padding: 6px 12px;
                        background-color: rgba(255, 87, 34, 0.1);
                        border-radius: 6px;
                        border: 1px solid rgba(255, 87, 34, 0.3);
                        min-width: 60px;
                    }
                """)
        else:
            self.gui_state_manager.add_log_message(
                "INFO",
                "MCU",
                f"Current temperature: {temperature:.1f}°C"
            )
            if self.temperature_group.current_temp_label:
                self.temperature_group.current_temp_label.setText(f"{temperature:.1f}°C")
                self.temperature_group.current_temp_label.setStyleSheet("""
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
                """)

    def _on_test_mode_completed(self, success: bool, message: str) -> None:
        """Handle test mode operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Test Mode Error", message)

    def _on_operating_temp_set(self, success: bool, message: str) -> None:
        """Handle operating temperature set result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Temperature Error", message)

    def _on_cooling_temp_set(self, success: bool, message: str) -> None:
        """Handle cooling temperature set result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Temperature Error", message)

    def _on_upper_temp_set(self, success: bool, message: str) -> None:
        """Handle upper temperature set result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Temperature Error", message)

    def _on_fan_speed_set(self, success: bool, message: str) -> None:
        """Handle fan speed set result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Fan Speed Error", message)

    def _on_boot_wait_completed(self, success: bool, message: str) -> None:
        """Handle boot wait operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Boot Wait Error", message)

    def _on_heating_completed(self, success: bool, message: str) -> None:
        """Handle heating operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Heating Error", message)

    def _on_cooling_completed(self, success: bool, message: str) -> None:
        """Handle cooling operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "MCU", message)
        else:
            QMessageBox.critical(self, "Cooling Error", message)
