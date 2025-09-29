"""Test Control Widget (Refactored)

Main test control widget with modular architecture and separation of concerns.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QLineEdit, QPushButton, QVBoxLayout, QWidget

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.styling import ThemeManager
from ui.gui.widgets.log_viewer_widget import LogViewerWidget
from .event_handlers import TestControlEventHandlers
from .state_manager import TestControlState
from .ui_components import (
    UIComponentFactory,
    TestSequenceGroup,
    TestParametersGroup,
    TestControlsGroup,
    TestStatusGroup,
    TestLogsGroup,
)


class TestControlWidget(QWidget):
    """
    Refactored test control widget with modular architecture.
    
    Features:
    - Separation of concerns with dedicated classes for state, events, and UI
    - Centralized state management
    - Reusable UI components
    - Consistent styling through theme manager
    - Maintainable and testable code structure
    """
    
    # Signals (maintain API compatibility)
    test_started = Signal()
    test_stopped = Signal()
    test_paused = Signal()
    robot_home_requested = Signal()
    emergency_stop_requested = Signal()
    
    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        
        # Store dependencies
        self.container = container
        self.gui_state_manager = state_manager
        
        # Initialize components
        self.theme_manager = ThemeManager()
        self.test_state = TestControlState()
        self.event_handlers = TestControlEventHandlers(self.test_state)
        self.ui_factory = UIComponentFactory(self.theme_manager)
        
        # UI component groups
        self.sequence_group = TestSequenceGroup(self.ui_factory, self.event_handlers)
        self.parameters_group = TestParametersGroup(self.ui_factory, self.event_handlers)
        self.controls_group = TestControlsGroup(self.ui_factory, self.event_handlers)
        self.status_group = TestStatusGroup(self.ui_factory, self.test_state)
        self.logs_group = TestLogsGroup(self.container, self.gui_state_manager)
        
        # Button references for backward compatibility
        self._button_refs: Dict[str, Optional[QPushButton]] = {}
        
        # Setup UI and connections
        self._setup_ui()
        self._setup_connections()
        self._setup_state_connections()
    
    def _setup_ui(self) -> None:
        """Setup the modular UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create and add component groups
        sequence_widget = self.sequence_group.create()
        main_layout.addWidget(sequence_widget)
        
        parameters_widget = self.parameters_group.create()
        main_layout.addWidget(parameters_widget)
        
        controls_widget = self.controls_group.create()
        main_layout.addWidget(controls_widget)
        
        status_widget = self.status_group.create()
        main_layout.addWidget(status_widget)
        
        logs_widget = self.logs_group.create()
        main_layout.addWidget(logs_widget, 1)  # Give logs section stretch factor
        
        # Store button references for API compatibility
        self._button_refs = self.controls_group.get_buttons()
        
        # Apply theme
        self.theme_manager.apply_industrial_theme(self)
    
    def _setup_connections(self) -> None:
        """Setup signal connections between components"""
        # Forward event handler signals to maintain API compatibility
        self.event_handlers.test_started.connect(self.test_started.emit)
        self.event_handlers.test_stopped.connect(self.test_stopped.emit)
        self.event_handlers.test_paused.connect(self.test_paused.emit)
        self.event_handlers.robot_home_requested.connect(self.robot_home_requested.emit)
        self.event_handlers.emergency_stop_requested.connect(self.emergency_stop_requested.emit)
    
    def _setup_state_connections(self) -> None:
        """Setup connections between state manager and UI components"""
        # Connect button state changes to actual buttons
        self.test_state.button_state_changed.connect(self._on_button_state_changed)
        
        # Connect state changes for special handling
        self.test_state.status_changed.connect(self._on_status_changed)
    
    def _on_button_state_changed(self, button_name: str, enabled: bool) -> None:
        """Handle button state changes from state manager"""
        if button_name in self._button_refs:
            button = self._button_refs[button_name]
            if button:  # Add None check
                button.setEnabled(enabled)

                # Set tooltips for disabled buttons
                if not enabled:
                    if button_name == "start":
                        button.setToolTip("Robot homing required after Emergency Stop")
                    elif button_name == "home":
                        button.setToolTip("HOME unavailable during test execution")
                else:
                    button.setToolTip("")

                # Force visual update
                button.repaint()
                button.update()
    
    def _on_status_changed(self, status: str, icon: str, progress: Optional[int]) -> None:
        """Handle status changes for special cases"""
        # Select serial number field for easy editing after test completion
        if "completed" in status.lower() or "success" in status.lower():
            if hasattr(self.parameters_group, 'serial_edit') and self.parameters_group.serial_edit:
                self.parameters_group.serial_edit.selectAll()
                self.parameters_group.serial_edit.setFocus()
    
    # API Compatibility Methods (maintain existing interface)
    
    def update_test_status(
        self, status: str, icon: str = "status_ready", progress: Optional[int] = None
    ) -> None:
        """Update test status display (API compatibility method)"""
        self.test_state.update_status(status, icon, progress)
    
    def update_test_progress(self, progress: int, status_text: Optional[str] = None) -> None:
        """Update only the progress bar (API compatibility method)"""
        if status_text:
            self.test_state.update_status(status_text, self.test_state.current_icon, progress)
        else:
            self.test_state.update_status(self.test_state.current_status, self.test_state.current_icon, progress)
    
    def disable_start_button(self) -> None:
        """Disable START TEST button (API compatibility method)"""
        self.test_state.set_button_enabled("start", False)
    
    def enable_start_button(self) -> None:
        """Enable START TEST button (API compatibility method)"""
        self.test_state.set_button_enabled("start", True)
    
    def disable_home_button(self) -> None:
        """Disable HOME button (API compatibility method)"""
        self.test_state.set_button_enabled("home", False)
    
    def enable_home_button(self) -> None:
        """Enable HOME button (API compatibility method)"""
        self.test_state.set_button_enabled("home", True)
    
    # Property accessors for backward compatibility
    
    @property
    def sequence_combo(self) -> Optional[QComboBox]:
        """Get sequence combo box (backward compatibility)"""
        return self.sequence_group.sequence_combo

    @property
    def serial_edit(self) -> Optional[QLineEdit]:
        """Get serial edit field (backward compatibility)"""
        return self.parameters_group.serial_edit

    @property
    def start_btn(self) -> Optional[QPushButton]:
        """Get start button (backward compatibility)"""
        return self._button_refs.get("start")
    
    @property
    def home_btn(self) -> Optional[QPushButton]:
        """Get home button (backward compatibility)"""
        return self._button_refs.get("home")

    @property
    def pause_btn(self) -> Optional[QPushButton]:
        """Get pause button (backward compatibility)"""
        return self._button_refs.get("pause")

    @property
    def stop_btn(self) -> Optional[QPushButton]:
        """Get stop button (backward compatibility)"""
        return self._button_refs.get("stop")
    
    @property
    def emergency_btn(self) -> Optional[QPushButton]:
        """Get emergency button (backward compatibility)"""
        return self._button_refs.get("emergency")
    
    @property
    def status_label(self):
        """Get status label (backward compatibility)"""
        return self.status_group.status_label
    
    @property
    def status_icon(self):
        """Get status icon (backward compatibility)"""
        return self.status_group.status_icon
    
    @property
    def progress_bar(self):
        """Get progress bar (backward compatibility)"""
        return self.status_group.progress_bar
    
    @property
    def log_viewer(self) -> Optional[LogViewerWidget]:
        """Get log viewer (backward compatibility)"""
        return self.logs_group.log_viewer
    
    # Public Methods for External Control
    
    def handle_test_completed(self, success: bool = True) -> None:
        """Handle test completion from external controllers"""
        self.event_handlers.handle_test_completed(success)
    
    def handle_robot_homing_completed(self, success: bool = True) -> None:
        """Handle robot homing completion from external controllers"""
        self.event_handlers.handle_robot_homing_completed(success)
    
    def get_current_test_sequence(self) -> str:
        """Get currently selected test sequence"""
        return self.test_state.current_sequence
    
    def get_current_serial_number(self) -> str:
        """Get current serial number"""
        return self.test_state.current_serial
    
    def reset_to_ready_state(self) -> None:
        """Reset widget to ready state for new test"""
        self.test_state.reset_to_ready()
