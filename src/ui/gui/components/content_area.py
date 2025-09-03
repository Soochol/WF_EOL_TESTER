"""
Content Area Widget for WF EOL Tester GUI

Central content area with stackable panels for different application functions.
"""

from typing import Any, Dict, Optional

from loguru import logger
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from application.containers.application_container import ApplicationContainer
from ui.gui.panels.config_panel import ConfigPanel
from ui.gui.panels.dashboard_panel import DashboardPanel
from ui.gui.panels.eol_test_panel import EOLTestPanel
from ui.gui.panels.hardware_panel import HardwarePanel
from ui.gui.panels.mcu_test_panel import MCUTestPanel
from ui.gui.services.gui_state_manager import GUIStateManager


class ContentAreaWidget(QWidget):
    """
    Content area widget with stackable panels

    Manages different application panels and handles navigation
    between them based on menu selection.
    """

    # Signals
    status_message = Signal(str)  # message
    panel_changed = Signal(str)  # panel_id

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize content area widget

        Args:
            container: Application dependency injection container
            state_manager: GUI state manager
            parent: Parent widget
        """
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.state_manager = state_manager

        # Panel management
        self.stacked_widget: Optional[QStackedWidget] = None
        self.panels: Dict[str, QWidget] = {}
        self.current_panel_id: Optional[str] = None

        # Header components
        self.panel_title_label: Optional[QLabel] = None
        self.panel_subtitle_label: Optional[QLabel] = None

        # Setup UI
        self.setup_ui()
        self.setup_layout()
        self.connect_signals()

        logger.debug("Content area widget initialized")

    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set widget properties
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create stacked widget for panels
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Create panel header
        self.panel_title_label = QLabel("Dashboard")
        self.panel_title_label.setProperty("class", "panel-title")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        self.panel_title_label.setFont(title_font)

        self.panel_subtitle_label = QLabel("System Overview")
        self.panel_subtitle_label.setProperty("class", "panel-subtitle")
        subtitle_font = QFont("Arial", 11)
        self.panel_subtitle_label.setFont(subtitle_font)

        # Style header labels
        self.panel_title_label.setStyleSheet(
            """
            QLabel {
                color: #2C3E50;
                padding: 8px 0px 4px 0px;
            }
        """
        )

        self.panel_subtitle_label.setStyleSheet(
            """
            QLabel {
                color: #7F8C8D;
                padding: 0px 0px 8px 0px;
            }
        """
        )

    def setup_layout(self) -> None:
        """Setup widget layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(8)

        # Header section
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        if self.panel_title_label:
            header_layout.addWidget(self.panel_title_label)

        if self.panel_subtitle_label:
            header_layout.addWidget(self.panel_subtitle_label)

        # Add header separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #BDC3C7; margin: 4px 0px;")
        header_layout.addWidget(separator)

        # Add header to main layout
        main_layout.addWidget(header_widget)

        # Add stacked widget
        if self.stacked_widget:
            main_layout.addWidget(self.stacked_widget)

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        if self.state_manager:
            self.state_manager.panel_changed.connect(self.on_panel_change_requested)

    def initialize_panels(self) -> None:
        """Initialize all application panels"""
        try:
            # Create dashboard panel
            dashboard_panel = DashboardPanel(
                container=self.container, state_manager=self.state_manager, parent=self
            )
            self.add_panel("dashboard", dashboard_panel, "Dashboard", "System Overview")

            # Create EOL test panel
            eol_test_panel = EOLTestPanel(
                container=self.container, state_manager=self.state_manager, parent=self
            )
            self.add_panel(
                "eol_test", eol_test_panel, "EOL Force Test", "End-of-Line Force Testing"
            )

            # Create MCU test panel
            mcu_test_panel = MCUTestPanel(
                container=self.container, state_manager=self.state_manager, parent=self
            )
            self.add_panel(
                "mcu_test", mcu_test_panel, "Simple MCU Test", "Basic MCU Communication Test"
            )

            # Create hardware control panel
            hardware_panel = HardwarePanel(
                container=self.container, state_manager=self.state_manager, parent=self
            )
            self.add_panel(
                "hardware", hardware_panel, "Hardware Control", "Manual Hardware Operations"
            )

            # Create configuration panel
            config_panel = ConfigPanel(
                container=self.container, state_manager=self.state_manager, parent=self
            )
            self.add_panel("configuration", config_panel, "Configuration", "System Settings")

            # Set default panel
            self.show_panel("dashboard")

            logger.info(f"Initialized {len(self.panels)} panels")

        except Exception as e:
            logger.error(f"Panel initialization failed: {e}")
            self.status_message.emit(f"Panel initialization failed: {e}")

    def add_panel(
        self, panel_id: str, panel_widget: QWidget, title: str, subtitle: str = ""
    ) -> None:
        """
        Add panel to content area

        Args:
            panel_id: Unique panel identifier
            panel_widget: Panel widget to add
            title: Panel display title
            subtitle: Panel subtitle
        """
        if panel_id in self.panels:
            logger.warning(f"Panel {panel_id} already exists, replacing")

        # Store panel reference
        self.panels[panel_id] = panel_widget

        # Store panel metadata
        panel_widget.setProperty("panel_id", panel_id)
        panel_widget.setProperty("panel_title", title)
        panel_widget.setProperty("panel_subtitle", subtitle)

        # Add to stacked widget
        if self.stacked_widget:
            self.stacked_widget.addWidget(panel_widget)

        # Connect panel signals if available
        if hasattr(panel_widget, "status_message"):
            panel_widget.status_message.connect(self.status_message.emit)

        logger.debug(f"Added panel: {panel_id} - {title}")

    def show_panel(self, panel_id: str) -> None:
        """
        Show specific panel

        Args:
            panel_id: ID of panel to show
        """
        if panel_id not in self.panels:
            logger.error(f"Panel {panel_id} not found")
            self.status_message.emit(f"Panel {panel_id} not found")
            return

        panel_widget = self.panels[panel_id]

        # Switch to panel
        if self.stacked_widget:
            self.stacked_widget.setCurrentWidget(panel_widget)

        # Update header
        self.update_panel_header(panel_widget)

        # Update current panel tracking
        self.current_panel_id = panel_id

        # Notify panel of activation if it has an activate method
        if hasattr(panel_widget, "activate_panel"):
            try:
                panel_widget.activate_panel()
            except Exception as e:
                logger.error(f"Panel activation failed for {panel_id}: {e}")

        # Emit signal
        self.panel_changed.emit(panel_id)

        logger.debug(f"Switched to panel: {panel_id}")

    def update_panel_header(self, panel_widget: QWidget) -> None:
        """
        Update panel header based on panel metadata

        Args:
            panel_widget: Panel widget to get metadata from
        """
        title = panel_widget.property("panel_title") or "Unknown Panel"
        subtitle = panel_widget.property("panel_subtitle") or ""

        if self.panel_title_label:
            self.panel_title_label.setText(title)

        if self.panel_subtitle_label:
            self.panel_subtitle_label.setText(subtitle)
            self.panel_subtitle_label.setVisible(bool(subtitle))

    def on_panel_change_requested(self, panel_id: str) -> None:
        """
        Handle panel change request from state manager

        Args:
            panel_id: ID of requested panel
        """
        self.show_panel(panel_id)

    def get_current_panel_id(self) -> Optional[str]:
        """
        Get current active panel ID

        Returns:
            Current panel ID or None
        """
        return self.current_panel_id

    def get_current_panel_widget(self) -> Optional[QWidget]:
        """
        Get current active panel widget

        Returns:
            Current panel widget or None
        """
        if self.current_panel_id:
            return self.panels.get(self.current_panel_id)
        return None

    def refresh_current_panel(self) -> None:
        """Refresh the current active panel"""
        current_panel = self.get_current_panel_widget()
        if current_panel and hasattr(current_panel, "refresh_panel"):
            try:
                current_panel.refresh_panel()
                self.status_message.emit("Panel refreshed")
                logger.debug(f"Refreshed panel: {self.current_panel_id}")
            except Exception as e:
                logger.error(f"Panel refresh failed: {e}")
                self.status_message.emit(f"Panel refresh failed: {e}")
        else:
            self.status_message.emit("Panel does not support refresh")

    def emergency_stop(self) -> None:
        """Handle emergency stop request"""
        current_panel = self.get_current_panel_widget()
        if current_panel and hasattr(current_panel, "emergency_stop"):
            try:
                current_panel.emergency_stop()
                logger.info(f"Emergency stop executed on panel: {self.current_panel_id}")
            except Exception as e:
                logger.error(f"Emergency stop failed on panel {self.current_panel_id}: {e}")

        # Also notify all panels with emergency_stop capability
        for panel_id, panel_widget in self.panels.items():
            if hasattr(panel_widget, "emergency_stop") and panel_id != self.current_panel_id:
                try:
                    panel_widget.emergency_stop()
                except Exception as e:
                    logger.error(f"Emergency stop failed on panel {panel_id}: {e}")

    def handle_resize(self) -> None:
        """Handle content area resize"""
        # Notify current panel of resize if it supports it
        current_panel = self.get_current_panel_widget()
        if current_panel and hasattr(current_panel, "handle_resize"):
            try:
                current_panel.handle_resize()
            except Exception as e:
                logger.error(f"Panel resize handling failed: {e}")

    def get_panel_count(self) -> int:
        """
        Get total number of panels

        Returns:
            Number of panels
        """
        return len(self.panels)

    def get_panel_list(self) -> Dict[str, str]:
        """
        Get list of available panels

        Returns:
            Dict mapping panel IDs to titles
        """
        panel_list = {}
        for panel_id, panel_widget in self.panels.items():
            title = panel_widget.property("panel_title") or panel_id
            panel_list[panel_id] = title
        return panel_list

    def enable_panel(self, panel_id: str, enabled: bool = True) -> None:
        """
        Enable or disable a panel

        Args:
            panel_id: Panel ID to enable/disable
            enabled: Whether to enable the panel
        """
        if panel_id in self.panels:
            self.panels[panel_id].setEnabled(enabled)
            logger.debug(f"Panel {panel_id} {'enabled' if enabled else 'disabled'}")
        else:
            logger.warning(f"Cannot enable/disable unknown panel: {panel_id}")

    def remove_panel(self, panel_id: str) -> bool:
        """
        Remove a panel from the content area

        Args:
            panel_id: Panel ID to remove

        Returns:
            True if panel was removed, False if not found
        """
        if panel_id not in self.panels:
            return False

        # Get panel widget
        panel_widget = self.panels[panel_id]

        # Remove from stacked widget
        if self.stacked_widget:
            self.stacked_widget.removeWidget(panel_widget)

        # Clean up panel
        panel_widget.setParent(None)
        panel_widget.deleteLater()

        # Remove from tracking
        del self.panels[panel_id]

        # Switch to dashboard if this was the current panel
        if self.current_panel_id == panel_id:
            if "dashboard" in self.panels:
                self.show_panel("dashboard")
            elif self.panels:
                # Show first available panel
                first_panel_id = next(iter(self.panels.keys()))
                self.show_panel(first_panel_id)
            else:
                self.current_panel_id = None

        logger.info(f"Removed panel: {panel_id}")
        return True
