"""Digital Input Control Widget

Main widget for digital input control interface (input-only).
Provides modern UI for reading digital inputs with B-contact logic support.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget
from loguru import logger

# Local application imports
from application.containers.simple_reloadable_container import SimpleReloadableContainer
from ui.gui.services.gui_state_manager import GUIStateManager

# Local folder imports
from .event_handlers import DigitalInputEventHandlers
from .state_manager import DigitalInputControlState
from .ui_components import (
    AllInputsDisplayGroup,
    ConnectionGroup,
    InputControlGroup,
    StatusDisplayGroup,
    create_modern_progress_bar,
)


class DigitalInputControlWidget(QWidget):
    """
    Digital Input Control Widget - Modern Design (Input-only)

    Features:
    - Connection management
    - Single channel input reading
    - All channels input reading
    - B-contact logic support (channels 8, 9)
    - Real-time status display
    """

    def __init__(
        self,
        container: SimpleReloadableContainer,
        state_manager: GUIStateManager,
        executor_thread=None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.gui_state_manager = state_manager
        self.executor_thread = executor_thread

        # Get digital I/O service
        try:
            hardware_facade = self.container.hardware_service_facade()
            self.digital_io_service = hardware_facade.digital_io_service
        except Exception as e:
            logger.error(f"Failed to get digital I/O service: {e}")
            raise

        # Initialize state and event handlers
        self.digital_input_state = DigitalInputControlState()
        self.event_handlers = DigitalInputEventHandlers(
            digital_io_service=self.digital_io_service,
            state=self.digital_input_state,
            executor_thread=executor_thread,
        )

        # UI component groups
        self.status_group = StatusDisplayGroup(self.digital_input_state)
        self.connection_group = ConnectionGroup(self.event_handlers)
        self.input_control_group = InputControlGroup(self.event_handlers, self.digital_input_state)
        self.all_inputs_group = AllInputsDisplayGroup(
            self.digital_input_state, self.event_handlers
        )

        # Setup UI
        self._setup_ui()
        self._connect_signals()

        logger.debug("Digital Input Control Widget initialized")

    def _setup_ui(self) -> None:
        """Setup the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)

        # Add cards in order
        content_layout.addWidget(self.status_group.create())
        content_layout.addWidget(self.connection_group.create())
        content_layout.addWidget(self.input_control_group.create())
        content_layout.addWidget(self.all_inputs_group.create())

        # Progress bar
        self.progress_bar = create_modern_progress_bar()
        self.progress_bar.setVisible(False)
        content_layout.addWidget(self.progress_bar)

        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _connect_signals(self) -> None:
        """Connect state signals to UI updates"""
        # Progress signals
        self.digital_input_state.progress_changed.connect(self._on_progress_changed)

        # Status signals
        self.digital_input_state.status_changed.connect(self._on_status_changed)

        # Button state signals
        self.digital_input_state.button_state_changed.connect(self._on_button_state_changed)

        # Event handler result signals
        self.event_handlers.connect_completed.connect(self._on_connect_completed)
        self.event_handlers.disconnect_completed.connect(self._on_disconnect_completed)

    def _on_progress_changed(self, visible: bool, message: str) -> None:
        """Handle progress indicator changes"""
        self.progress_bar.setVisible(visible)
        if visible:
            self.progress_bar.setFormat(message)

    def _on_status_changed(self, message: str, status_type: str) -> None:
        """Handle status message changes"""
        logger.info(f"[{status_type.upper()}] {message}")

    def _on_button_state_changed(self, button_name: str, enabled: bool) -> None:
        """Handle button state changes"""
        # Get all button references
        all_buttons = {}
        all_buttons.update(self.connection_group.get_buttons())
        all_buttons.update(self.input_control_group.get_buttons())

        # Update button state
        if button_name in all_buttons and all_buttons[button_name]:
            all_buttons[button_name].setEnabled(enabled)

    def _on_connect_completed(self, success: bool, message: str) -> None:
        """Handle connect operation completion"""
        if success:
            self.digital_input_state.show_status(message, "info")
        else:
            self.digital_input_state.show_status(message, "error")

    def _on_disconnect_completed(self, success: bool, message: str) -> None:
        """Handle disconnect operation completion"""
        if success:
            self.digital_input_state.show_status(message, "info")
        else:
            self.digital_input_state.show_status(message, "error")
