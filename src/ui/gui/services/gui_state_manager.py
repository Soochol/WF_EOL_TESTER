"""
GUI State Manager

Manages GUI state and provides interface between GUI and business logic.
"""

# Standard library imports
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
from PySide6.QtCore import QObject, Signal
from loguru import logger

# Local application imports
from application.services.hardware_facade.hardware_service_facade import (
    HardwareServiceFacade,
)


@dataclass
class CycleData:
    """Data class for individual cycle measurement"""

    cycle: int  # Cycle number
    temperature: float  # Temperature in °C
    stroke: float  # Stroke position in mm
    force: float  # Measured force in kgf
    heating_time: int  # Heating time in ms
    cooling_time: int  # Cooling time in ms
    status: str  # Cycle status (PASS/FAIL)


@dataclass
class TestResult:
    """Data class for test results with individual cycle data"""

    test_id: str  # e.g., "1_20251004_165238"
    serial_number: str  # DUT serial number
    status: str  # Overall test status (PASS/FAIL)
    timestamp: datetime  # Test completion time
    duration_seconds: float  # Total test duration
    cycles: List['CycleData']  # List of individual cycle measurements


@dataclass
class HardwareStatus:
    """Data class for hardware status"""

    loadcell_connected: bool = False
    loadcell_value: float = 0.0
    mcu_connected: bool = False
    mcu_port: str = ""
    power_connected: bool = False
    power_voltage: float = 0.0
    power_current: float = 0.0
    robot_connected: bool = False
    robot_homed: bool = False
    robot_position: Dict[str, float] = None  # type: ignore
    digital_io_connected: bool = False
    digital_io_channels: int = 0

    def __post_init__(self):
        if self.robot_position is None:
            self.robot_position = {"x": 0.0, "y": 0.0, "z": 0.0}


@dataclass
class TestProgress:
    """Data class for test progress"""

    current_test: str = ""
    progress_percent: int = 0
    current_cycle: int = 0
    total_cycles: int = 0
    status: str = "Idle"
    elapsed_time: str = "00:00:00"
    estimated_remaining: str = "00:00:00"


class GUIStateManager(QObject):
    """
    GUI State Manager

    Manages application state and provides signals for GUI updates.
    """

    # Signals for GUI updates
    hardware_status_updated = Signal(object)  # HardwareStatus
    test_progress_updated = Signal(object)  # TestProgress
    test_result_added = Signal(object)  # TestResult
    cycle_result_added = Signal(object)  # TestResult for individual cycles
    log_message_received = Signal(str, str, str)  # level, component, message
    system_status_changed = Signal(str)  # status
    temperature_updated = Signal(float)  # temperature

    def __init__(
        self,
        hardware_facade: HardwareServiceFacade,
        configuration_service=None,  # ConfigurationService,
        emergency_stop_service=None,  # EmergencyStopService
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.hardware_facade = hardware_facade
        self.configuration_service = configuration_service
        self.emergency_stop_service = emergency_stop_service

        # State data
        self.hardware_status = HardwareStatus()
        self.test_progress = TestProgress()
        self.test_results: List[TestResult] = []
        self.log_messages: List[Dict[str, str]] = []
        self.system_status = "Initializing"
        self.current_temperature = 25.0

        # Initialize
        self._initialize_state()

        # Setup log capture
        self._setup_log_capture()

    def _initialize_state(self) -> None:
        """Initialize default state"""
        # Mock initial hardware status
        self.hardware_status.loadcell_connected = True
        self.hardware_status.loadcell_value = 12.34
        self.hardware_status.mcu_connected = True
        self.hardware_status.mcu_port = "COM3"
        self.hardware_status.power_connected = True
        self.hardware_status.power_voltage = 24.0
        self.hardware_status.power_current = 5.2
        self.hardware_status.robot_connected = True
        self.hardware_status.robot_homed = True
        self.hardware_status.robot_position = {"x": 100.0, "y": 50.0, "z": 25.0}
        self.hardware_status.digital_io_connected = True
        self.hardware_status.digital_io_channels = 8

        # Set initial system status
        self.system_status = "Ready"

        # Emit initial state
        self.hardware_status_updated.emit(self.hardware_status)
        self.system_status_changed.emit(self.system_status)
        self.temperature_updated.emit(self.current_temperature)

        # Add some sample log messages for testing
        self.add_log_message("INFO", "SYSTEM", "GUI State Manager initialized")
        self.add_log_message("DEBUG", "GUI", "Sample data loaded")

    def get_hardware_status(self) -> HardwareStatus:
        """Get current hardware status"""
        return self.hardware_status

    def get_test_progress(self) -> TestProgress:
        """Get current test progress"""
        return self.test_progress

    def get_test_results(self) -> List[TestResult]:
        """Get all test results"""
        return self.test_results

    def get_log_messages(self) -> List[Dict[str, str]]:
        """Get all log messages"""
        return self.log_messages

    def get_system_status(self) -> str:
        """Get current system status"""
        return self.system_status

    def get_current_temperature(self) -> float:
        """Get current temperature"""
        return self.current_temperature

    def update_hardware_status(self, status: HardwareStatus) -> None:
        """Update hardware status"""
        self.hardware_status = status
        self.hardware_status_updated.emit(status)

    def update_test_progress(self, progress: TestProgress) -> None:
        """Update test progress"""
        self.test_progress = progress
        self.test_progress_updated.emit(progress)

    def add_test_result(self, result: TestResult) -> None:
        """Add a test result"""
        self.test_results.append(result)
        self.test_result_added.emit(result)

    def add_cycle_result(
        self,
        cycle: int,
        total_cycles: int,
        temperature: float,
        stroke: float,
        force: float,
        heating_time: int,
        cooling_time: int,
        status: str,
    ) -> None:
        """
        Add an individual cycle result and emit signal for real-time GUI updates.

        Args:
            cycle: Current cycle number
            total_cycles: Total number of cycles in the test
            temperature: Temperature in °C
            stroke: Stroke position in mm
            force: Measured force in kgf
            heating_time: Heating time in ms
            cooling_time: Cooling time in ms
            status: Cycle status (PASS/FAIL)
        """
        cycle_data = CycleData(
            cycle=cycle,
            temperature=temperature,
            stroke=stroke,
            force=force,
            heating_time=heating_time,
            cooling_time=cooling_time,
            status=status,
        )

        # Emit signal for real-time GUI updates (charts, tables, etc.)
        self.cycle_result_added.emit(cycle_data)

    def add_log_message(self, level: str, component: str, message: str) -> None:
        """Add a log message"""
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "level": level,
            "component": component,
            "message": message,
        }
        self.log_messages.append(log_entry)
        self.log_message_received.emit(level, component, message)

    def set_system_status(self, status: str) -> None:
        """Set system status"""
        self.system_status = status
        self.system_status_changed.emit(status)

    def update_temperature(self, temperature: float) -> None:
        """Update current temperature"""
        self.current_temperature = temperature
        self.temperature_updated.emit(temperature)

    def clear_test_results(self) -> None:
        """Clear all test results"""
        self.test_results.clear()

    def clear_log_messages(self) -> None:
        """Clear all log messages"""
        self.log_messages.clear()

    def load_today_results_from_disk(self, json_dir: str) -> int:
        """
        Load today's test results from JSON files.

        Args:
            json_dir: Directory containing JSON test result files

        Returns:
            Number of results loaded
        """
        from ui.gui.utils.result_loader import load_today_results

        try:
            results = load_today_results(json_dir)

            # Add each result to state manager
            for result in results:
                self.test_results.append(result)
                # Emit signal to update UI
                self.test_result_added.emit(result)

            logger.info(f"📂 Loaded {len(results)} test results from today's files")
            return len(results)

        except Exception as e:
            logger.error(f"Failed to load today's results: {e}")
            return 0

    def _setup_log_capture(self) -> None:
        """Setup log capture from loguru logger"""

        def log_sink(message):
            """Custom sink for capturing log messages"""
            record = message.record
            level = record["level"].name

            # Extract component from extra or use module name
            component = record.get("extra", {}).get("component", "SYSTEM")

            # If no component is set, try to extract from module name
            if component == "SYSTEM" and "module" in record:
                module_parts = record["module"].split(".")
                if len(module_parts) > 1:
                    component = module_parts[-2].upper()  # Get parent module name
                else:
                    component = module_parts[0].upper()

            # Get the actual message
            message_text = record["message"]

            # Add to GUI state manager
            self.add_log_message(level, component, message_text)

        # Add the custom sink to loguru logger
        logger.add(log_sink, level="DEBUG", format="{message}")


    def get_connection_count(self) -> tuple[int, int]:
        """Get connection count (connected, total)"""
        connected = sum(
            [
                self.hardware_status.loadcell_connected,
                self.hardware_status.mcu_connected,
                self.hardware_status.power_connected,
                self.hardware_status.robot_connected,
                self.hardware_status.digital_io_connected,
            ]
        )
        total = 5
        return connected, total

    async def execute_emergency_stop(self) -> None:
        """Execute emergency stop procedure"""
        try:
            logger.critical("🚨 GUI Emergency Stop Request 🚨")

            if self.emergency_stop_service:
                await self.emergency_stop_service.execute_emergency_stop()
                logger.info("✅ Emergency stop completed successfully")

                # Update system state
                self.set_system_status("EMERGENCY STOP")
                self.add_log_message(
                    "CRITICAL", "EMERGENCY", "Emergency stop executed successfully"
                )
            else:
                logger.error("Emergency stop service not available")
                self.add_log_message("ERROR", "EMERGENCY", "Emergency stop service not available")

        except Exception as e:
            logger.error(f"Emergency stop execution failed: {e}")
            self.add_log_message("ERROR", "EMERGENCY", f"Emergency stop failed: {str(e)}")
