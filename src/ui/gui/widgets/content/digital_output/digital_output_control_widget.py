"""Digital Output Control Widget - Modern Design

Modern digital output control widget with Material Design 3 styling.
Output-only version (no input controls).
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
from .event_handlers import DigitalOutputEventHandlers
from .state_manager import DigitalOutputControlState
from .ui_components import (
    AllOutputsDisplayGroup,
    ConnectionGroup,
    LEDToggleGrid,
    OutputControlGroup,
    StatusDisplayGroup,
    create_modern_progress_bar,
)


class DigitalOutputControlWidget(QWidget):
    """
    Modern digital output control widget with vertical card layout (output-only).

    Layout Structure:
    ┌─────────────────────────────────────┐
    │  Row 1: Status Card (full width)    │
    ├─────────────────────────────────────┤
    │  Row 2: Connection Card (full width)│
    ├─────────────────────────────────────┤
    │  Row 3: Output Control Card (full)  │
    ├─────────────────────────────────────┤
    │  Row 4: All Outputs Display (full)  │
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

        # Get digital I/O service
        self.digital_io_service = container.hardware_service_facade().digital_io_service

        # Initialize components
        self.theme_manager = ThemeManager()
        self.output_state = DigitalOutputControlState()
        self.event_handlers = DigitalOutputEventHandlers(
            digital_io_service=self.digital_io_service,
            state=self.output_state,
            executor_thread=executor_thread,
        )

        # UI component groups
        self.status_group = StatusDisplayGroup(self.output_state)
        self.connection_group = ConnectionGroup(self.event_handlers)
        self.output_control_group = OutputControlGroup(self.event_handlers, self.output_state)
        self.led_toggle_grid = LEDToggleGrid(self.event_handlers, self.output_state)
        self.all_outputs_group = AllOutputsDisplayGroup(self.output_state, self.event_handlers)

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
            DigitalOutputControlWidget {
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

        # LED Toggle Grid (new main control)
        led_toggle_widget = self.led_toggle_grid.create()
        content_layout.addWidget(led_toggle_widget)

        output_control_widget = self.output_control_group.create()
        content_layout.addWidget(output_control_widget)

        all_outputs_widget = self.all_outputs_group.create()
        content_layout.addWidget(all_outputs_widget)

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
        self._button_refs.update(self.output_control_group.get_buttons())

    def _setup_connections(self) -> None:
        """Setup signal connections between components"""
        # Connect event handler result signals to UI feedback
        self.event_handlers.connect_completed.connect(self._on_connect_completed)
        self.event_handlers.disconnect_completed.connect(self._on_disconnect_completed)
        self.event_handlers.output_written.connect(self._on_output_written)
        self.event_handlers.output_read.connect(self._on_output_read)
        self.event_handlers.all_outputs_reset.connect(self._on_all_outputs_reset)

    def _setup_state_connections(self) -> None:
        """Setup connections between state manager and UI components"""
        # Connect button state changes to actual buttons
        self.output_state.button_state_changed.connect(self._on_button_state_changed)

        # Connect status changes to GUI state manager and UI feedback
        self.output_state.status_changed.connect(self._on_status_changed)

        # Connect progress indication
        self.output_state.progress_changed.connect(self._on_progress_changed)

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
            self.gui_state_manager.add_log_message("ERROR", "DIGITAL_OUT", message)
        elif status_type == "warning":
            self.gui_state_manager.add_log_message("WARNING", "DIGITAL_OUT", message)
        else:
            self.gui_state_manager.add_log_message("INFO", "DIGITAL_OUT", message)

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
            self.gui_state_manager.add_log_message("INFO", "DIGITAL_OUT", message)
        else:
            QMessageBox.critical(self, "Connection Error", message)

    def _on_disconnect_completed(self, success: bool, message: str) -> None:
        """Handle disconnect operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "DIGITAL_OUT", message)
        else:
            QMessageBox.critical(self, "Disconnect Error", message)

    def _on_output_written(self, success: bool, message: str) -> None:
        """Handle output write operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "DIGITAL_OUT", message)
        else:
            QMessageBox.warning(self, "Write Error", message)

    def _on_output_read(self, channel: int, state: bool) -> None:
        """Handle output read result"""
        level_str = "HIGH" if state else "LOW"
        self.gui_state_manager.add_log_message(
            "INFO", "DIGITAL_OUT", f"Output CH{channel}: {level_str}"
        )

    def _on_all_outputs_reset(self, success: bool, message: str) -> None:
        """Handle reset all outputs operation result"""
        if success:
            self.gui_state_manager.add_log_message("INFO", "DIGITAL_OUT", message)
        else:
            QMessageBox.warning(self, "Reset Error", message)
