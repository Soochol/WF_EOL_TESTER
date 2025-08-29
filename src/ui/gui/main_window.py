"""
Main Window for WF EOL Tester GUI

Industrial-themed main application window with header, side menu,
content area, and status bar integration.
"""

from typing import Any, Dict, Optional

from loguru import logger
from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from application.containers.application_container import ApplicationContainer
from ui.gui.components.content_area import ContentAreaWidget
from ui.gui.components.header import HeaderWidget
from ui.gui.components.side_menu import SideMenuWidget
from ui.gui.components.status_bar import StatusBarWidget
from ui.gui.services.gui_state_manager import (
    ConnectionStatus,
    GUIStateManager,
    TestStatus,
)
from ui.gui.utils.styling import ThemeManager


class MainWindow(QMainWindow):
    """
    Main application window for WF EOL Tester

    Provides industrial-themed interface with:
    - Header with title and status indicators
    - Left side navigation menu
    - Central content area with stackable panels
    - Bottom status bar with hardware status
    """

    # Custom signals
    closing = Signal()

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize main window

        Args:
            container: Application dependency injection container
            state_manager: GUI state management service
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.state_manager = state_manager
        self.theme_manager = ThemeManager()

        # Initialize components
        self.header_widget: Optional[HeaderWidget] = None
        self.side_menu_widget: Optional[SideMenuWidget] = None
        self.content_area_widget: Optional[ContentAreaWidget] = None
        self.status_bar_widget: Optional[StatusBarWidget] = None

        # Initialize UI
        self.setup_window()
        self.create_widgets()
        self.setup_layout()
        self.connect_signals()
        self.setup_keyboard_shortcuts()

        # Initialize state
        self.load_window_settings()
        self.state_manager.load_configuration()

        logger.info("Main window initialized")

    def setup_window(self) -> None:
        """Setup main window properties"""
        # Window properties
        self.setWindowTitle("WF EOL Tester")
        self.setMinimumSize(QSize(1200, 800))
        self.resize(QSize(1400, 900))

        # Window flags for industrial application
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        # Center window on screen
        self.center_on_screen()

        logger.debug("Main window setup completed")

    def center_on_screen(self) -> None:
        """Center window on the primary screen"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.geometry()
            x = (screen_geometry.width() - window_geometry.width()) // 2
            y = (screen_geometry.height() - window_geometry.height()) // 2
            self.move(x, y)

    def create_widgets(self) -> None:
        """Create all child widgets"""
        # Create header
        self.header_widget = HeaderWidget(state_manager=self.state_manager, parent=self)

        # Create side menu
        self.side_menu_widget = SideMenuWidget(state_manager=self.state_manager, parent=self)

        # Create content area
        self.content_area_widget = ContentAreaWidget(
            container=self.container, state_manager=self.state_manager, parent=self
        )

        # Create custom status bar
        self.status_bar_widget = StatusBarWidget(state_manager=self.state_manager, parent=self)

        logger.debug("All widgets created")

    def setup_layout(self) -> None:
        """Setup main window layout"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add header
        if self.header_widget:
            main_layout.addWidget(self.header_widget)

        # Create horizontal splitter for content
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)

        # Add side menu to splitter
        if self.side_menu_widget:
            content_splitter.addWidget(self.side_menu_widget)

        # Add content area to splitter
        if self.content_area_widget:
            content_splitter.addWidget(self.content_area_widget)

        # Set splitter proportions (side menu: content = 1:4)
        content_splitter.setSizes([250, 1000])
        content_splitter.setStretchFactor(0, 0)  # Side menu fixed
        content_splitter.setStretchFactor(1, 1)  # Content area stretches

        # Add splitter to main layout
        main_layout.addWidget(content_splitter)

        # Set custom status bar
        if self.status_bar_widget:
            self.setStatusBar(self.status_bar_widget)

        logger.debug("Main window layout setup completed")

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        # State manager signals
        if self.state_manager:
            self.state_manager.panel_changed.connect(self.on_panel_changed)
            self.state_manager.test_status_changed.connect(self.on_test_status_changed)
            self.state_manager.hardware_status_changed.connect(self.on_hardware_status_changed)
            self.state_manager.system_message_added.connect(self.on_system_message_added)

        # Component signals
        if self.side_menu_widget:
            self.side_menu_widget.panel_requested.connect(self.state_manager.navigate_to_panel)
            self.side_menu_widget.exit_requested.connect(self.close)

        if self.content_area_widget:
            self.content_area_widget.status_message.connect(self.show_status_message)

        logger.debug("Signals connected")

    def setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts"""
        # Exit shortcut
        exit_action = QAction(self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        self.addAction(exit_action)

        # Emergency stop shortcut
        emergency_stop_action = QAction(self)
        emergency_stop_action.setShortcut(QKeySequence("F1"))
        emergency_stop_action.triggered.connect(self.emergency_stop)
        self.addAction(emergency_stop_action)

        # Refresh shortcut
        refresh_action = QAction(self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.refresh_status)
        self.addAction(refresh_action)

        logger.debug("Keyboard shortcuts setup completed")

    def load_window_settings(self) -> None:
        """Load window settings from configuration"""
        # This could be expanded to load window geometry from config
        # For now, just ensure reasonable defaults
        pass

    def save_window_settings(self) -> None:
        """Save window settings to configuration"""
        # This could be expanded to save window geometry to config
        pass

    # === EVENT HANDLERS ===

    def on_panel_changed(self, panel_name: str) -> None:
        """
        Handle panel change

        Args:
            panel_name: Name of the new active panel
        """
        self.show_status_message(f"Switched to {panel_name}")
        logger.debug(f"Panel changed to: {panel_name}")

    def on_test_status_changed(self, status: str) -> None:
        """
        Handle test status change

        Args:
            status: New test status
        """
        if self.header_widget:
            self.header_widget.update_test_status(status)

        # Update window title with test status
        base_title = "WF EOL Tester"
        if status != "idle":
            self.setWindowTitle(f"{base_title} - {status.title()}")
        else:
            self.setWindowTitle(base_title)

        logger.debug(f"Test status changed to: {status}")

    def on_hardware_status_changed(self, hardware_status) -> None:
        """
        Handle hardware status change

        Args:
            hardware_status: New hardware status object
        """
        if self.header_widget:
            self.header_widget.update_hardware_status(hardware_status)

        # Log significant status changes
        overall_status = hardware_status.overall_status
        if overall_status == ConnectionStatus.ERROR:
            self.show_status_message("Hardware connection error detected", 5000)
        elif overall_status == ConnectionStatus.CONNECTED:
            self.show_status_message("All hardware connected", 3000)

    def on_system_message_added(self, message: str) -> None:
        """
        Handle new system message

        Args:
            message: New system message
        """
        if self.status_bar_widget:
            self.status_bar_widget.show_message(message, 2000)

    # === PUBLIC METHODS ===

    def show_status_message(self, message: str, timeout: int = 2000) -> None:
        """
        Show status message in status bar

        Args:
            message: Message to show
            timeout: Timeout in milliseconds
        """
        if self.status_bar_widget:
            self.status_bar_widget.show_message(message, timeout)

    def show_error_message(self, title: str, message: str) -> None:
        """
        Show error message dialog

        Args:
            title: Dialog title
            message: Error message
        """
        QMessageBox.critical(self, title, message)

    def show_warning_message(self, title: str, message: str) -> None:
        """
        Show warning message dialog

        Args:
            title: Dialog title
            message: Warning message
        """
        QMessageBox.warning(self, title, message)

    def show_info_message(self, title: str, message: str) -> None:
        """
        Show information message dialog

        Args:
            title: Dialog title
            message: Information message
        """
        QMessageBox.information(self, title, message)

    def emergency_stop(self) -> None:
        """Handle emergency stop request"""
        try:
            # Stop any running tests
            if self.state_manager.test_status in [TestStatus.RUNNING, TestStatus.PREPARING]:
                self.state_manager.set_test_status(TestStatus.CANCELLED, "Emergency stop activated")

            # Notify content area
            if self.content_area_widget:
                self.content_area_widget.emergency_stop()

            self.show_status_message("Emergency stop activated", 5000)
            logger.warning("Emergency stop activated by user")

        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            self.show_error_message(
                "Emergency Stop Error", f"Failed to execute emergency stop: {e}"
            )

    def refresh_status(self) -> None:
        """Refresh all status information"""
        try:
            # Trigger hardware status update
            if self.state_manager:
                # Force immediate status update
                QTimer.singleShot(100, lambda: self.state_manager._update_hardware_status())

            # Refresh content area
            if self.content_area_widget:
                self.content_area_widget.refresh_current_panel()

            self.show_status_message("Status refreshed", 2000)
            logger.info("Status refresh triggered by user")

        except Exception as e:
            logger.error(f"Status refresh failed: {e}")
            self.show_error_message("Refresh Error", f"Failed to refresh status: {e}")

    # === WINDOW EVENTS ===

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event

        Args:
            event: Close event
        """
        # Check if test is running
        if self.state_manager and self.state_manager.test_status == TestStatus.RUNNING:
            reply = QMessageBox.question(
                self,
                "Test Running",
                "A test is currently running. Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

        # Save settings
        try:
            self.save_window_settings()

            # Emit closing signal
            self.closing.emit()

            # Stop any running operations
            if self.state_manager:
                self.state_manager.reset_test_state()

            logger.info("Main window closing")
            event.accept()

        except Exception as e:
            logger.error(f"Error during window close: {e}")
            event.accept()  # Still close despite errors

    def resizeEvent(self, event) -> None:
        """Handle window resize event"""
        super().resizeEvent(event)

        # Update component layouts if needed
        if self.content_area_widget:
            self.content_area_widget.handle_resize()

    def showEvent(self, event) -> None:
        """Handle window show event"""
        super().showEvent(event)

        # Initialize components after window is shown
        QTimer.singleShot(100, self._post_show_initialization)

    def _post_show_initialization(self) -> None:
        """Post-show initialization tasks"""
        try:
            # Initialize content area
            if self.content_area_widget:
                self.content_area_widget.initialize_panels()

            # Navigate to default panel
            if self.state_manager:
                self.state_manager.navigate_to_panel("dashboard")

            logger.info("Post-show initialization completed")

        except Exception as e:
            logger.error(f"Post-show initialization failed: {e}")
            self.show_error_message("Initialization Error", f"Post-show initialization failed: {e}")

    def set_theme(self, theme_name: str) -> None:
        """
        Set application theme

        Args:
            theme_name: Name of theme to apply
        """
        try:
            if theme_name == "industrial":
                self.theme_manager.apply_industrial_theme(self)
            elif theme_name == "terminal":
                self.theme_manager.apply_terminal_theme(self)
            else:
                logger.warning(f"Unknown theme: {theme_name}")
                return

            self.show_status_message(f"Theme changed to {theme_name}", 2000)
            logger.info(f"Theme changed to: {theme_name}")

        except Exception as e:
            logger.error(f"Theme change failed: {e}")
            self.show_error_message("Theme Error", f"Failed to change theme: {e}")
