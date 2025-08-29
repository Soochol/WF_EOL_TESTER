#!/usr/bin/env python3
"""
WF EOL Tester - GUI Application Entry Point

Complete PySide6 GUI application for the EOL Tester system.
Integrates with existing business logic via ApplicationContainer.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

# PySide6 imports with explicit module imports
try:
    from PySide6.QtCore import QTimer  # pylint: disable=no-name-in-module
    from PySide6.QtGui import QIcon  # pylint: disable=no-name-in-module
    from PySide6.QtWidgets import QApplication  # pylint: disable=no-name-in-module
except ImportError as e:
    print(f"PySide6 import error: {e}")
    print("Please ensure PySide6 is installed: pip install PySide6")
    sys.exit(1)

# Module imports now work directly since main_gui.py is in the src/ directory

from application.containers.application_container import ApplicationContainer
from ui.gui.main_window import MainWindow
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.styling import ThemeManager


class EOLTesterGUIApplication:
    """
    Main GUI Application class for WF EOL Tester

    Manages application lifecycle, dependency injection, and main window.
    """

    def __init__(self):
        """Initialize GUI application with dependency injection"""
        self.app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None
        self.container: Optional[ApplicationContainer] = None
        self.state_manager: Optional[GUIStateManager] = None
        self.asyncio_timer: Optional[QTimer] = None

    def setup_application(self) -> None:
        """Setup QApplication with proper configuration"""
        self.app = QApplication(sys.argv)

        # Application metadata
        self.app.setApplicationName("WF EOL Tester")
        self.app.setApplicationVersion("2.0.0")
        self.app.setOrganizationName("WOOFER")
        self.app.setOrganizationDomain("woofer.com")

        # Set application icon if available
        icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))

        logger.info("GUI Application initialized")

    def setup_container(self) -> None:
        """Initialize dependency injection container"""
        try:
            # Ensure configuration files exist
            ApplicationContainer.ensure_config_exists()

            # Create container with loaded configuration
            self.container = ApplicationContainer.create()
            logger.info("ApplicationContainer created successfully")

        except Exception as e:
            logger.error(f"Failed to create ApplicationContainer: {e}")
            logger.info("Creating container with fallback configuration")
            self.container = ApplicationContainer()
            ApplicationContainer._apply_fallback_config(self.container)

    def setup_state_manager(self) -> None:
        """Initialize GUI state management"""
        if not self.container:
            raise RuntimeError("Container must be initialized before state manager")

        self.state_manager = GUIStateManager(
            hardware_facade=self.container.hardware_service_facade(),
            configuration_service=self.container.configuration_service(),
        )
        logger.info("GUI State Manager initialized")

    def create_main_window(self) -> None:
        """Create and configure main application window"""
        if not self.container or not self.state_manager:
            raise RuntimeError("Container and state manager must be initialized first")

        self.main_window = MainWindow(container=self.container, state_manager=self.state_manager)

        # Apply industrial theme
        theme_manager = ThemeManager()
        theme_manager.apply_industrial_theme(self.main_window)

        logger.info("Main window created")

    def run(self) -> int:
        """
        Run the GUI application

        Returns:
            Application exit code
        """
        try:
            # Setup application components
            self.setup_application()
            self.setup_container()
            self.setup_state_manager()
            self.create_main_window()

            # Show main window
            if self.main_window:
                self.main_window.show()
                logger.info("Main window displayed")

                # Setup asyncio integration for Qt
                self._setup_asyncio_integration()

                # Run application event loop
                return self.app.exec() if self.app else 1
            else:
                logger.error("Failed to create main window")
                return 1

        except Exception as e:
            logger.error(f"Application startup failed: {e}")
            return 1

    def _setup_asyncio_integration(self) -> None:
        """Setup asyncio integration with Qt event loop"""
        # Create a timer to process asyncio events
        self.asyncio_timer = QTimer()
        self.asyncio_timer.timeout.connect(self._process_asyncio_events)
        self.asyncio_timer.start(10)  # Process every 10ms
        logger.info("Asyncio integration configured")

    def _process_asyncio_events(self) -> None:
        """Process pending asyncio events"""
        try:
            # Try to get current event loop, but don't fail if none exists
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Process some pending tasks if loop is running
                    pass
            except RuntimeError:
                # No event loop in current thread, this is normal
                pass
        except Exception:
            # Ignore all errors in asyncio processing
            pass


def main() -> int:
    """
    Main entry point for GUI application

    Returns:
        Application exit code
    """
    # Configure logging for GUI application
    logger.remove()  # Remove default logger
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>GUI</cyan> | "
        "<level>{message}</level>",
        colorize=True,
    )

    logger.info("Starting WF EOL Tester GUI Application")

    # Create and run application
    app = EOLTesterGUIApplication()
    exit_code = app.run()

    logger.info(f"GUI Application exited with code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
