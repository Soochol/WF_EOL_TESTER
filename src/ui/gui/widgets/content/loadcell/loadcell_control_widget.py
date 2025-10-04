"""Loadcell Control Widget - Modern Design

Modern loadcell control widget with Material Design 3 styling.
Features vertical layout for space efficiency.
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
from .event_handlers import LoadcellEventHandlers
from .state_manager import LoadcellControlState
from .ui_components import (
    ConnectionGroup,
    create_modern_progress_bar,
    HoldControlGroup,
    MeasurementGroup,
    StatusDisplayGroup,
)


class LoadcellControlWidget(QWidget):
    """
    Modern loadcell control widget with vertical layout.

    Layout Structure:
    ┌─────────────────────────────────────┐
    │  Row 1: Status Card (full width)    │
    ├─────────────────────────────────────┤
    │  Row 2: Connection Card             │
    ├─────────────────────────────────────┤
    │  Row 3: Measurement Card            │
    ├─────────────────────────────────────┤
    │  Row 4: Hold Control Card           │
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

        # Get loadcell service
        self.loadcell_service = container.hardware_service_facade().loadcell_service

        # Initialize components
        self.theme_manager = ThemeManager()
        self.loadcell_state = LoadcellControlState()
        self.event_handlers = LoadcellEventHandlers(
            loadcell_service=self.loadcell_service,
            state=self.loadcell_state,
            executor_thread=executor_thread,  # ✅ Pass executor to event handlers
        )

        # UI component groups
        self.status_group = StatusDisplayGroup(self.loadcell_state)
        self.connection_group = ConnectionGroup(self.event_handlers)
        self.measurement_group = MeasurementGroup(self.event_handlers)
        self.hold_group = HoldControlGroup(self.event_handlers)

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
            LoadcellControlWidget {
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

        measurement_widget = self.measurement_group.create()
        content_layout.addWidget(measurement_widget)

        hold_widget = self.hold_group.create()
        content_layout.addWidget(hold_widget)

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
        self._button_refs.update(self.measurement_group.get_buttons())
        self._button_refs.update(self.hold_group.get_buttons())

    def _setup_connections(self) -> None:
        """Setup signal connections between components"""
        # Connect event handler result signals to UI feedback
        self.event_handlers.connect_completed.connect(self._on_connect_completed)
        self.event_handlers.disconnect_completed.connect(self._on_disconnect_completed)
        self.event_handlers.zero_calibration_completed.connect(self._on_zero_calibration_completed)
        self.event_handlers.force_read.connect(self._on_force_read)
        self.event_handlers.peak_force_read.connect(self._on_peak_force_read)
        self.event_handlers.hold_completed.connect(self._on_hold_completed)
        self.event_handlers.hold_release_completed.connect(self._on_hold_release_completed)

    def _setup_state_connections(self) -> None:
        """Setup state change connections to update UI"""
        # Button state changes
        self.loadcell_state.button_state_changed.connect(self._on_button_state_changed)

        # Progress indicator
        self.loadcell_state.progress_changed.connect(self._on_progress_changed)

        # Status updates
        self.loadcell_state.status_changed.connect(self._on_status_changed)

    # Event handler result callbacks
    def _on_connect_completed(self, success: bool, message: str) -> None:
        """Handle connect operation completion"""
        if not success:
            QMessageBox.warning(self, "Connection Failed", message)

    def _on_disconnect_completed(self, success: bool, message: str) -> None:
        """Handle disconnect operation completion"""
        if not success:
            QMessageBox.warning(self, "Disconnection Failed", message)

    def _on_zero_calibration_completed(self, success: bool, message: str) -> None:
        """Handle zero calibration completion"""
        if success:
            QMessageBox.information(self, "Calibration Success", message)
        else:
            QMessageBox.warning(self, "Calibration Failed", message)

    def _on_force_read(self, force: float) -> None:
        """Handle force reading"""
        # Force is already updated in state and displayed in pills

    def _on_peak_force_read(self, peak_force: float) -> None:
        """Handle peak force reading"""
        # Peak force is already updated in state and displayed in pills

    def _on_hold_completed(self, success: bool, message: str) -> None:
        """Handle hold operation completion"""
        if not success:
            QMessageBox.warning(self, "Hold Failed", message)

    def _on_hold_release_completed(self, success: bool, message: str) -> None:
        """Handle hold release completion"""
        if not success:
            QMessageBox.warning(self, "Release Failed", message)

    # State change callbacks
    def _on_button_state_changed(self, button_name: str, enabled: bool) -> None:
        """Update button enabled state"""
        button = self._button_refs.get(button_name)
        if button:
            button.setEnabled(enabled)

    def _on_progress_changed(self, visible: bool, message: str) -> None:
        """Update progress indicator"""
        if self.progress_bar:
            self.progress_bar.setVisible(visible)

    def _on_status_changed(self, message: str, status_type: str) -> None:
        """Handle status message updates"""
        # Status is displayed in pills, no additional action needed
