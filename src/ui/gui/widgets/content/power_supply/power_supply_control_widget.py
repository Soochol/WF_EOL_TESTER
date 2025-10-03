"""Power Supply Control Widget - Modern Design

Modern power supply control widget with Material Design 3 styling.
Features vertical card layout for clear organization.
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
from ui.gui.utils.styling import ThemeManager

# Local folder imports
from .event_handlers import PowerSupplyEventHandlers
from .state_manager import PowerSupplyControlState
from .ui_components import (
    ConnectionGroup,
    ControlGroup,
    MeasurementGroup,
    StatusDisplayGroup,
    create_modern_progress_bar,
)


class PowerSupplyControlWidget(QWidget):
    """
    Modern power supply control widget with vertical card layout.

    Layout Structure:
    ┌─────────────────────────────────────┐
    │  Row 1: Status Card (full width)    │
    ├─────────────────────────────────────┤
    │  Row 2: Connection Card (full width)│
    ├─────────────────────────────────────┤
    │  Row 3: Control Card (full width)   │
    ├─────────────────────────────────────┤
    │  Row 4: Measurement Card (full)     │
    └─────────────────────────────────────┘
    """

    def __init__(
        self,
        container: SimpleReloadableContainer,
        state_manager: GUIStateManager,
        executor_thread=None,  # TestExecutorThread for unified execution
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.gui_state_manager = state_manager
        self.executor_thread = executor_thread

        # Get power service
        self.power_service = container.hardware_service_facade().power_service

        # Initialize components
        self.theme_manager = ThemeManager()
        self.power_state = PowerSupplyControlState()
        self.event_handlers = PowerSupplyEventHandlers(
            power_service=self.power_service,
            state=self.power_state,
            executor_thread=executor_thread,
        )

        # UI component groups
        self.status_group = StatusDisplayGroup(self.power_state)
        self.connection_group = ConnectionGroup(self.event_handlers)
        self.control_group = ControlGroup(self.event_handlers)
        self.measurement_group = MeasurementGroup(self.event_handlers)

        # Button references for state management
        self._button_refs: Dict[str, Optional[QPushButton]] = {}

        # Progress bar
        self.progress_bar: Optional[QProgressBar] = None

        # Setup UI and connections
        self._setup_ui()
        self._setup_connections()
        self._setup_state_connections()

    def _setup_ui(self) -> None:
        """Setup modern UI with vertical layout and scroll area"""
        # Main widget layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Apply dark background
        self.setStyleSheet(
            """
            PowerSupplyControlWidget {
                background-color: #1e1e1e;
            }
        """
        )

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            """
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
        """
        )

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

        control_widget = self.control_group.create()
        content_layout.addWidget(control_widget)

        measurement_widget = self.measurement_group.create()
        content_layout.addWidget(measurement_widget)

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
        self._button_refs.update(self.control_group.get_buttons())
        self._button_refs.update(self.measurement_group.get_buttons())

    def _setup_connections(self) -> None:
        """Setup signal connections between components"""
        # Connect event handler result signals to UI feedback
        self.event_handlers.connect_completed.connect(self._on_connect_completed)
        self.event_handlers.disconnect_completed.connect(self._on_disconnect_completed)
        self.event_handlers.enable_output_completed.connect(self._on_enable_output_completed)
        self.event_handlers.disable_output_completed.connect(self._on_disable_output_completed)
        self.event_handlers.set_voltage_completed.connect(self._on_set_voltage_completed)
        self.event_handlers.set_current_completed.connect(self._on_set_current_completed)
        self.event_handlers.voltage_read.connect(self._on_voltage_read)
        self.event_handlers.current_read.connect(self._on_current_read)
        self.event_handlers.measurements_read.connect(self._on_measurements_read)

    def _setup_state_connections(self) -> None:
        """Setup connections between state manager and UI components"""
        # Connect button state changes to actual buttons
        self.power_state.button_state_changed.connect(self._on_button_state_changed)

        # Connect status changes to GUI state manager and UI feedback
        self.power_state.status_changed.connect(self._on_status_changed)

        # Connect progress indication
        self.power_state.progress_changed.connect(self._on_progress_changed)

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
            self.gui_state_manager.add_log_message("ERROR", "POWER", message)
        elif status_type == "warning":
            self.gui_state_manager.add_log_message("WARNING", "POWER", message)
        else:
            self.gui_state_manager.add_log_message("INFO", "POWER", message)

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
            self.gui_state_manager.add_log_message("INFO", "POWER", message)
        else:
            QMessageBox.critical(self, "Connection Error", message)

    def _on_disconnect_completed(self, success: bool, message: str) -> None:
        """Handle disconnect operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "POWER", message)
        else:
            QMessageBox.critical(self, "Disconnect Error", message)

    def _on_enable_output_completed(self, success: bool, message: str) -> None:
        """Handle enable output operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "POWER", message)
        else:
            QMessageBox.critical(self, "Output Error", message)

    def _on_disable_output_completed(self, success: bool, message: str) -> None:
        """Handle disable output operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "POWER", message)
        else:
            QMessageBox.critical(self, "Output Error", message)

    def _on_set_voltage_completed(self, success: bool, message: str) -> None:
        """Handle set voltage operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "POWER", message)
        else:
            QMessageBox.critical(self, "Voltage Error", message)

    def _on_set_current_completed(self, success: bool, message: str) -> None:
        """Handle set current operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "POWER", message)
        else:
            QMessageBox.critical(self, "Current Error", message)

    def _on_voltage_read(self, voltage: float) -> None:
        """Handle voltage read result"""
        if voltage < 0:
            self.gui_state_manager.add_log_message("ERROR", "POWER", "Failed to read voltage")
            if self.measurement_group.voltage_label:
                self.measurement_group.voltage_label.setText("Error")
                self.measurement_group.voltage_label.setStyleSheet(
                    """
                    QLabel {
                        color: #FF5722;
                        font-size: 13px;
                        padding: 6px 12px;
                        background-color: rgba(255, 87, 34, 0.1);
                        border-radius: 6px;
                        border: 1px solid rgba(255, 87, 34, 0.3);
                        min-width: 80px;
                    }
                """
                )
        else:
            self.gui_state_manager.add_log_message("INFO", "POWER", f"Voltage: {voltage:.2f}V")
            if self.measurement_group.voltage_label:
                self.measurement_group.voltage_label.setText(f"{voltage:.2f} V")
                self.measurement_group.voltage_label.setStyleSheet(
                    """
                    QLabel {
                        color: #00D9A5;
                        font-size: 13px;
                        font-weight: 600;
                        padding: 6px 12px;
                        background-color: rgba(0, 217, 165, 0.1);
                        border-radius: 6px;
                        border: 1px solid rgba(0, 217, 165, 0.3);
                        min-width: 80px;
                    }
                """
                )

    def _on_current_read(self, current: float) -> None:
        """Handle current read result"""
        if current < 0:
            self.gui_state_manager.add_log_message("ERROR", "POWER", "Failed to read current")
            if self.measurement_group.current_label:
                self.measurement_group.current_label.setText("Error")
                self.measurement_group.current_label.setStyleSheet(
                    """
                    QLabel {
                        color: #FF5722;
                        font-size: 13px;
                        padding: 6px 12px;
                        background-color: rgba(255, 87, 34, 0.1);
                        border-radius: 6px;
                        border: 1px solid rgba(255, 87, 34, 0.3);
                        min-width: 80px;
                    }
                """
                )
        else:
            self.gui_state_manager.add_log_message("INFO", "POWER", f"Current: {current:.3f}A")
            if self.measurement_group.current_label:
                self.measurement_group.current_label.setText(f"{current:.3f} A")
                self.measurement_group.current_label.setStyleSheet(
                    """
                    QLabel {
                        color: #00D9A5;
                        font-size: 13px;
                        font-weight: 600;
                        padding: 6px 12px;
                        background-color: rgba(0, 217, 165, 0.1);
                        border-radius: 6px;
                        border: 1px solid rgba(0, 217, 165, 0.3);
                        min-width: 80px;
                    }
                """
                )

    def _on_measurements_read(self, voltage: float, current: float, power: float) -> None:
        """Handle all measurements read result"""
        if voltage < 0 or current < 0 or power < 0:
            self.gui_state_manager.add_log_message("ERROR", "POWER", "Failed to read measurements")
            return

        # Update all measurement displays
        self.gui_state_manager.add_log_message(
            "INFO", "POWER", f"V: {voltage:.2f}V, I: {current:.3f}A, P: {power:.2f}W"
        )

        # Update voltage
        if self.measurement_group.voltage_label:
            self.measurement_group.voltage_label.setText(f"{voltage:.2f} V")
            self.measurement_group.voltage_label.setStyleSheet(
                """
                QLabel {
                    color: #00D9A5;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 6px 12px;
                    background-color: rgba(0, 217, 165, 0.1);
                    border-radius: 6px;
                    border: 1px solid rgba(0, 217, 165, 0.3);
                    min-width: 80px;
                }
            """
            )

        # Update current
        if self.measurement_group.current_label:
            self.measurement_group.current_label.setText(f"{current:.3f} A")
            self.measurement_group.current_label.setStyleSheet(
                """
                QLabel {
                    color: #00D9A5;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 6px 12px;
                    background-color: rgba(0, 217, 165, 0.1);
                    border-radius: 6px;
                    border: 1px solid rgba(0, 217, 165, 0.3);
                    min-width: 80px;
                }
            """
            )

        # Update power
        if self.measurement_group.power_label:
            self.measurement_group.power_label.setText(f"{power:.2f} W")
            self.measurement_group.power_label.setStyleSheet(
                """
                QLabel {
                    color: #00D9A5;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 6px 12px;
                    background-color: rgba(0, 217, 165, 0.1);
                    border-radius: 6px;
                    border: 1px solid rgba(0, 217, 165, 0.3);
                    min-width: 80px;
                }
            """
            )
