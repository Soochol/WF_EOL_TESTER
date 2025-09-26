"""
Log Handler Service

Service to bridge CLI logging to GUI display.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
from PySide6.QtCore import QObject, Signal
from loguru import logger

# Local application imports
from ui.gui.services.gui_state_manager import GUIStateManager


class GUILogHandler:
    """
    Custom log handler for bridging Loguru logs to GUI.

    Captures log messages and forwards them to the GUI state manager.
    """

    def __init__(self, state_manager: GUIStateManager):
        self.state_manager = state_manager

    def __call__(self, message: Dict[str, Any]) -> None:
        """Handle log message"""
        try:
            record = message.get("record", {})
            if not record:
                return

            # Extract log information
            level = record.get("level", {}).get("name", "INFO")
            message_text = record.get("message", "")
            module_name = record.get("module", "UNKNOWN")

            # Map module name to component
            component = self._get_component_name(module_name)

            # Forward to GUI state manager
            self.state_manager.add_log_message(level, component, message_text)

        except Exception as e:
            # Don't let logging errors crash the application
            print(f"Error in GUI log handler: {e}")

    def _get_component_name(self, module_name: str) -> str:
        """Map module name to component name"""
        component_map = {
            # Hardware components
            "loadcell": "LOADCELL",
            "mcu": "MCU",
            "power": "POWER",
            "robot": "ROBOT",
            "digital_io": "DIGITAL_IO",
            # Application components
            "test": "TEST",
            "gui": "GUI",
            "hardware": "HARDWARE",
            "configuration": "CONFIG",
            "main": "SYSTEM",
            # Infrastructure
            "adapters": "HARDWARE",
            "repositories": "DATA",
            "factories": "FACTORY",
            # Default
            "unknown": "SYSTEM",
        }

        # Try to match module name to component
        for key, component in component_map.items():
            if key in module_name.lower():
                return component

        return "SYSTEM"


class LogBridgeService(QObject):
    """
    Service to configure logging bridge between CLI and GUI.

    Sets up Loguru handlers to forward logs to GUI components.
    """

    log_configured = Signal()

    def __init__(self, state_manager: GUIStateManager, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.state_manager = state_manager
        self.gui_handler = GUILogHandler(state_manager)
        self.handler_id = None

    def setup_gui_logging(self) -> None:
        """Setup GUI logging handler"""
        try:
            # Add GUI handler to loguru
            self.handler_id = logger.add(
                self.gui_handler,  # type: ignore[arg-type]
                level="INFO",
                format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{module}</cyan> | "
                "<level>{message}</level>",
                colorize=False,
                backtrace=False,
                diagnose=False,
            )

            # Add some initial log messages
            logger.info("GUI logging system initialized")
            logger.info("Log handler configured successfully")

            self.log_configured.emit()

        except Exception as e:
            print(f"Failed to setup GUI logging: {e}")

    def add_sample_logs(self) -> None:
        """Add sample log messages for demonstration"""
        # Hardware connection logs
        logger.info("Loadcell connected successfully on port COM1")
        logger.info("MCU Ready on COM3, baudrate 115200")
        logger.info("Power supply online: 24.0V / 5.2A")
        logger.info("Robot homed at X:100 Y:50 Z:25")
        logger.info("Digital I/O channels initialized: 8/8 active")

        # Test sequence logs
        logger.info("Starting EOL Force Test sequence")
        logger.info("Serial Number: SN123456789")
        logger.info("Test parameters: Force=5.0kgf, Cycles=100, Temp=25°C")

        # Sample test progress logs
        logger.info("Cycle 1 started")
        logger.info("Force measurement: 4.98 kgf (Target: 5.0 kgf)")
        logger.info("Cycle 1: PASS")

        # Warning log
        logger.warning("Temperature slightly elevated: 24.3°C")

        # Error log
        logger.error("Cycle 4 FAILED: Force 5.21 kgf exceeds tolerance")

        # Debug log
        logger.debug("Hardware status check completed")

        logger.info("Sample logs added to GUI display")

    def shutdown(self) -> None:
        """Shutdown the log bridge"""
        if self.handler_id is not None:
            try:
                logger.remove(self.handler_id)
                logger.info("GUI log handler removed")
            except Exception as e:
                print(f"Error removing log handler: {e}")
            finally:
                self.handler_id = None
