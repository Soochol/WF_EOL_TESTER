"""
Logs Widget

Refactored logs viewer page with modular architecture.
Uses separated components for UI controls and event handling.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.widgets.content.logs import (
    LogControlsFactory,
    LogEventHandlerFactory,
)
from ui.gui.widgets.content.shared.styles import CommonStyles
from ui.gui.widgets.log_viewer_widget import LogViewerWidget


class LogsWidget(QWidget):
    """
    Refactored logs widget for viewing system logs.

    Uses modular components for:
    - UI controls (filters, buttons)
    - Event handling (separated from UI)
    - Styling (shared common styles)
    - Factory patterns for component creation
    """

    log_cleared = Signal()
    log_saved = Signal(str)  # Emits file path
    log_paused = Signal(bool)  # Emits pause state

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self._setup_components()
        self._setup_ui()
        self._connect_signals()

    def _setup_components(self) -> None:
        """Initialize components and event handlers"""
        # Create log viewer first
        self.log_viewer = LogViewerWidget(
            container=self.container,
            state_manager=self.state_manager,
        )

        # Create event handler
        self.event_handler = LogEventHandlerFactory.create_handler(
            log_viewer=self.log_viewer, parent_widget=self
        )

    def _setup_ui(self) -> None:
        """Setup the logs UI using modular components"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header with controls using factory
        header_group = LogControlsFactory.create_header_group(
            level_change_callback=self.event_handler.handle_level_changed,
            clear_callback=self.event_handler.handle_clear_clicked,
            save_callback=self.event_handler.handle_save_clicked,
            pause_callback=self.event_handler.handle_pause_toggled,
            parent=self,
        )
        main_layout.addWidget(header_group)

        # Log viewer
        main_layout.addWidget(self.log_viewer)

        # Apply shared styling
        self.setStyleSheet(CommonStyles.get_complete_style())

    def _connect_signals(self) -> None:
        """Connect event handler signals to widget signals"""
        # Forward signals from event handler to external listeners
        self.event_handler.log_cleared.connect(self.log_cleared.emit)
        self.event_handler.log_saved.connect(self.log_saved.emit)
        self.event_handler.log_paused.connect(self.log_paused.emit)

    def get_pause_state(self) -> bool:
        """
        Get current pause state.

        Returns:
            True if logging is paused, False otherwise
        """
        return self.event_handler.get_pause_state()
