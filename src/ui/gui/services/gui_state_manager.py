"""
GUI State Management Service

Manages application state, hardware status, and UI component synchronization.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger
from PySide6.QtCore import QObject, QTimer, Signal

from application.services.configuration_service import ConfigurationService
from application.services.hardware_service_facade import HardwareServiceFacade


class ConnectionStatus(Enum):
    """Hardware connection status enumeration"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class TestStatus(Enum):
    """Test execution status enumeration"""

    IDLE = "idle"
    PREPARING = "preparing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class HardwareStatus:
    """Hardware status data class"""

    robot_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    mcu_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    loadcell_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    power_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    digital_io_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def overall_status(self) -> ConnectionStatus:
        """Get overall hardware status"""
        statuses = [
            self.robot_status,
            self.mcu_status,
            self.loadcell_status,
            self.power_status,
            self.digital_io_status,
        ]

        if any(status == ConnectionStatus.ERROR for status in statuses):
            return ConnectionStatus.ERROR
        elif any(status == ConnectionStatus.CONNECTING for status in statuses):
            return ConnectionStatus.CONNECTING
        elif all(status == ConnectionStatus.CONNECTED for status in statuses):
            return ConnectionStatus.CONNECTED
        else:
            return ConnectionStatus.DISCONNECTED


@dataclass
class ApplicationState:
    """Main application state data class"""

    current_panel: str = "dashboard"
    test_status: TestStatus = TestStatus.IDLE
    hardware_status: HardwareStatus = field(default_factory=HardwareStatus)
    test_progress: int = 0
    test_message: str = ""
    last_test_result: Optional[Dict[str, Any]] = None
    system_messages: List[str] = field(default_factory=list)
    configuration_loaded: bool = False


class GUIStateManager(QObject):
    """
    GUI State Manager

    Central state management for the GUI application.
    Handles hardware status monitoring, test state tracking,
    and UI component synchronization.
    """

    # State change signals
    panel_changed = Signal(str)  # current_panel
    test_status_changed = Signal(str)  # test_status
    test_progress_changed = Signal(int, str)  # progress, message
    hardware_status_changed = Signal(object)  # HardwareStatus
    system_message_added = Signal(str)  # message
    configuration_changed = Signal()

    def __init__(
        self, hardware_facade: HardwareServiceFacade, configuration_service: ConfigurationService
    ):
        """
        Initialize GUI state manager

        Args:
            hardware_facade: Hardware service facade
            configuration_service: Configuration service
        """
        super().__init__()

        self._hardware_facade = hardware_facade
        self._configuration_service = configuration_service
        self._state = ApplicationState()

        # Status monitoring timer
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_hardware_status)
        self._status_timer.start(1000)  # Update every second

        # Message cleanup timer
        self._message_timer = QTimer()
        self._message_timer.timeout.connect(self._cleanup_old_messages)
        self._message_timer.start(30000)  # Cleanup every 30 seconds

        logger.info("GUI State Manager initialized")

    @property
    def current_state(self) -> ApplicationState:
        """Get current application state"""
        return self._state

    @property
    def current_panel(self) -> str:
        """Get current active panel"""
        return self._state.current_panel

    @property
    def test_status(self) -> TestStatus:
        """Get current test status"""
        return self._state.test_status

    @property
    def hardware_status(self) -> HardwareStatus:
        """Get current hardware status"""
        return self._state.hardware_status

    def navigate_to_panel(self, panel_name: str) -> None:
        """
        Navigate to a specific panel

        Args:
            panel_name: Name of the panel to navigate to
        """
        if panel_name != self._state.current_panel:
            self._state.current_panel = panel_name
            self.panel_changed.emit(panel_name)
            self.add_system_message(f"Navigated to {panel_name}")
            logger.info(f"Panel changed to: {panel_name}")

    def set_test_status(self, status: TestStatus, message: str = "") -> None:
        """
        Update test status

        Args:
            status: New test status
            message: Optional status message
        """
        if status != self._state.test_status:
            self._state.test_status = status
            self._state.test_message = message
            self.test_status_changed.emit(status.value)

            # Log status changes
            if message:
                logger.info(f"Test status: {status.value} - {message}")
                self.add_system_message(f"Test {status.value}: {message}")
            else:
                logger.info(f"Test status: {status.value}")
                self.add_system_message(f"Test {status.value}")

    def update_test_progress(self, progress: int, message: str = "") -> None:
        """
        Update test progress

        Args:
            progress: Progress percentage (0-100)
            message: Optional progress message
        """
        progress = max(0, min(100, progress))  # Clamp to 0-100

        if progress != self._state.test_progress or message != self._state.test_message:
            self._state.test_progress = progress
            self._state.test_message = message
            self.test_progress_changed.emit(progress, message)

            if message:
                logger.debug(f"Test progress: {progress}% - {message}")

    def set_test_result(self, result: Dict[str, Any]) -> None:
        """
        Store test result

        Args:
            result: Test result data
        """
        self._state.last_test_result = result

        # Update test status based on result
        if result.get("is_passed", False):
            self.set_test_status(TestStatus.COMPLETED, "Test passed successfully")
        else:
            self.set_test_status(TestStatus.FAILED, "Test failed")

        logger.info(f"Test result stored: {result.get('test_id', 'unknown')}")

    def add_system_message(self, message: str) -> None:
        """
        Add system message

        Args:
            message: Message to add
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        self._state.system_messages.append(formatted_message)

        # Keep only last 100 messages
        if len(self._state.system_messages) > 100:
            self._state.system_messages = self._state.system_messages[-100:]

        self.system_message_added.emit(formatted_message)

    def get_system_messages(self, count: int = 50) -> List[str]:
        """
        Get recent system messages

        Args:
            count: Number of recent messages to return

        Returns:
            List of recent system messages
        """
        return self._state.system_messages[-count:] if count > 0 else self._state.system_messages

    def clear_system_messages(self) -> None:
        """Clear all system messages"""
        self._state.system_messages.clear()
        self.add_system_message("System messages cleared")

    def reset_test_state(self) -> None:
        """Reset test-related state"""
        self._state.test_status = TestStatus.IDLE
        self._state.test_progress = 0
        self._state.test_message = ""
        self._state.last_test_result = None

        self.test_status_changed.emit(TestStatus.IDLE.value)
        self.test_progress_changed.emit(0, "")

        self.add_system_message("Test state reset")
        logger.info("Test state reset")

    async def check_hardware_connections(self) -> HardwareStatus:
        """
        Check all hardware connections asynchronously

        Returns:
            Updated hardware status
        """
        try:
            # Check each hardware component
            status = HardwareStatus()

            # Robot status
            try:
                if self._hardware_facade.robot_service:
                    # Simple connection check - adjust based on actual service API
                    status.robot_status = ConnectionStatus.CONNECTED
                else:
                    status.robot_status = ConnectionStatus.DISCONNECTED
            except Exception:
                status.robot_status = ConnectionStatus.ERROR

            # MCU status
            try:
                if self._hardware_facade.mcu_service:
                    status.mcu_status = ConnectionStatus.CONNECTED
                else:
                    status.mcu_status = ConnectionStatus.DISCONNECTED
            except Exception:
                status.mcu_status = ConnectionStatus.ERROR

            # Load cell status
            try:
                if self._hardware_facade.loadcell_service:
                    status.loadcell_status = ConnectionStatus.CONNECTED
                else:
                    status.loadcell_status = ConnectionStatus.DISCONNECTED
            except Exception:
                status.loadcell_status = ConnectionStatus.ERROR

            # Power supply status
            try:
                if self._hardware_facade.power_service:
                    status.power_status = ConnectionStatus.CONNECTED
                else:
                    status.power_status = ConnectionStatus.DISCONNECTED
            except Exception:
                status.power_status = ConnectionStatus.ERROR

            # Digital IO status
            try:
                if self._hardware_facade.digital_io_service:
                    status.digital_io_status = ConnectionStatus.CONNECTED
                else:
                    status.digital_io_status = ConnectionStatus.DISCONNECTED
            except Exception:
                status.digital_io_status = ConnectionStatus.ERROR

            status.last_updated = datetime.now()
            return status

        except Exception as e:
            logger.error(f"Hardware status check failed: {e}")
            return HardwareStatus()  # All disconnected

    def _update_hardware_status(self) -> None:
        """Update hardware status (called by timer)"""
        # Use thread pool to run async operation
        import threading
        from concurrent.futures import ThreadPoolExecutor

        def run_async_update():
            try:
                # Create new event loop for thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self._async_hardware_status_update())
                finally:
                    loop.close()
            except Exception as e:
                logger.error(f"Hardware status update thread failed: {e}")

        # Run in background thread
        thread = threading.Thread(target=run_async_update, daemon=True)
        thread.start()

    async def _async_hardware_status_update(self) -> None:
        """Async hardware status update"""
        try:
            new_status = await self.check_hardware_connections()

            # Check if status changed
            if (
                new_status.robot_status != self._state.hardware_status.robot_status
                or new_status.mcu_status != self._state.hardware_status.mcu_status
                or new_status.loadcell_status != self._state.hardware_status.loadcell_status
                or new_status.power_status != self._state.hardware_status.power_status
                or new_status.digital_io_status != self._state.hardware_status.digital_io_status
            ):

                self._state.hardware_status = new_status
                self.hardware_status_changed.emit(new_status)

                # Log significant status changes
                overall_status = new_status.overall_status
                if overall_status != self._state.hardware_status.overall_status:
                    logger.info(f"Hardware overall status: {overall_status.value}")

        except Exception as e:
            logger.error(f"Async hardware status update failed: {e}")

    def _cleanup_old_messages(self) -> None:
        """Clean up old system messages"""
        # Keep only messages from last hour
        current_time = datetime.now()
        cutoff_time = (
            current_time.replace(hour=current_time.hour - 1)
            if current_time.hour > 0
            else current_time.replace(hour=23, day=current_time.day - 1)
        )

        # Simple cleanup - just limit to 100 messages
        if len(self._state.system_messages) > 100:
            self._state.system_messages = self._state.system_messages[-50:]

    def load_configuration(self) -> None:
        """Load application configuration"""
        try:
            # Use thread pool to run async operation
            import threading

            def run_async_config_load():
                try:
                    # Create new event loop for thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self._async_load_configuration())
                    finally:
                        loop.close()
                except Exception as e:
                    logger.error(f"Configuration load thread failed: {e}")
                    self.add_system_message(f"Configuration load failed: {e}")

            # Run in background thread
            thread = threading.Thread(target=run_async_config_load, daemon=True)
            thread.start()

        except Exception as e:
            logger.error(f"Configuration load failed: {e}")
            self.add_system_message(f"Configuration load failed: {e}")

    async def _async_load_configuration(self) -> None:
        """Async configuration loading"""
        try:
            # Load hardware configuration
            hardware_config = await self._configuration_service.load_hardware_config()

            # Load application configuration
            app_config = await self._configuration_service.load_application_config()

            self._state.configuration_loaded = True
            self.configuration_changed.emit()
            self.add_system_message("Configuration loaded successfully")

            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Async configuration load failed: {e}")
            self.add_system_message(f"Configuration load failed: {e}")
