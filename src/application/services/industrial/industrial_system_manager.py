"""
Industrial System Manager

Central manager for industrial safety and status indication systems.
Coordinates tower lamp control, safety alerts, and system status management.
"""

# Standard library imports
from typing import Any, Dict, Optional, TYPE_CHECKING, Union

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.services.industrial.safety_alert_service import (
    SafetyAlert,
    SafetyAlertService,
)
from application.services.industrial.tower_lamp_service import (
    SystemStatus,
    TowerLampService,
)
from domain.value_objects.hardware_config import DigitalPin


if TYPE_CHECKING:
    # Local application imports
    from application.services.core.configuration_service import ConfigurationService
    from application.services.hardware_facade import HardwareServiceFacade


class IndustrialSystemManager:
    """
    Industrial System Manager

    Central coordinator for industrial safety and status indication systems.
    Manages tower lamp status, safety alerts, and system state transitions.
    """

    def __init__(
        self,
        hardware_service_facade: "HardwareServiceFacade",
        configuration_service: "ConfigurationService",
        gui_alert_callback=None,
    ):
        """
        Initialize Industrial System Manager

        Args:
            hardware_service_facade: Hardware service facade for accessing all hardware
            configuration_service: Configuration service for loading hardware config
            gui_alert_callback: Optional GUI callback for popup alerts
        """
        self._hardware_service_facade = hardware_service_facade
        self._configuration_service = configuration_service
        self._hardware_config = None
        self._digital_io_service = None

        # Initialize safety alert service (tower lamp will be lazy loaded)
        self.safety_alert_service: Optional[SafetyAlertService] = None
        self.tower_lamp_service: Optional[TowerLampService] = None

        # Set GUI callback for later
        self._gui_alert_callback = gui_alert_callback

        # Safety sensor configurations (will be lazy loaded)
        self.door_sensor: Optional[DigitalPin] = None
        self.clamp_sensor: Optional[DigitalPin] = None
        self.chain_sensor: Optional[DigitalPin] = None

        # System state tracking
        self._current_system_status: Optional[SystemStatus] = None
        self._last_safety_check_result: Optional[SafetyAlert] = None
        self._initialized = False

        # Status change callbacks (for UI synchronization)
        self._status_change_callbacks: list = []

        logger.info("🏭 INDUSTRIAL_MGR: Industrial System Manager initialized")

    async def _ensure_initialized(self) -> None:
        """Ensure all services are initialized lazily"""
        if self._initialized:
            return

        try:
            # Load hardware config
            self._hardware_config = await self._configuration_service.load_hardware_config()

            # Get digital I/O service
            self._digital_io_service = self._hardware_service_facade.digital_io_service

            # Connect Digital I/O service if not already connected
            if not await self._digital_io_service.is_connected():
                logger.info(
                    "🏭 INDUSTRIAL_MGR: Connecting Digital I/O service for tower lamp control..."
                )
                await self._digital_io_service.connect()
                logger.info("🏭 INDUSTRIAL_MGR: Digital I/O service connected successfully")
            else:
                logger.info("🏭 INDUSTRIAL_MGR: Digital I/O service already connected")

            # Initialize tower lamp service
            self.tower_lamp_service = TowerLampService(
                digital_io_service=self._digital_io_service, hardware_config=self._hardware_config
            )

            # Initialize safety alert service
            self.safety_alert_service = SafetyAlertService(
                tower_lamp_service=self.tower_lamp_service
            )

            # Set GUI callback if provided
            if self._gui_alert_callback:
                self.safety_alert_service.set_gui_alert_callback(self._gui_alert_callback)

            # Get safety sensor configurations
            self.door_sensor = self._hardware_config.digital_io.safety_door_closed_sensor
            self.clamp_sensor = self._hardware_config.digital_io.dut_clamp_safety_sensor
            self.chain_sensor = self._hardware_config.digital_io.dut_chain_safety_sensor

            self._initialized = True
            logger.info("🏭 INDUSTRIAL_MGR: Lazy initialization completed")

        except Exception as e:
            logger.error(f"🏭 INDUSTRIAL_MGR: Failed to initialize: {e}")
            raise

    def register_status_change_callback(self, callback):
        """
        Register callback to be called when system status changes

        Args:
            callback: Function to call with SystemStatus parameter
        """
        self._status_change_callbacks.append(callback)
        logger.debug(
            f"🏭 INDUSTRIAL_MGR: Status change callback registered (total: {len(self._status_change_callbacks)})"
        )

    async def initialize_system(self) -> None:
        """Initialize industrial system to idle state - GREEN ON immediately"""
        logger.info("🏭 INDUSTRIAL_MGR: Initializing system...")
        await self._ensure_initialized()
        # Set to IDLE immediately - GREEN lamp turns ON from program start
        await self.set_system_status(SystemStatus.SYSTEM_IDLE)
        logger.info("🏭 INDUSTRIAL_MGR: System initialization complete - GREEN ON")

    async def set_system_status(self, status: SystemStatus) -> None:
        """
        Set system status with tower lamp indication

        Args:
            status: System status to set
        """
        await self._ensure_initialized()
        logger.info(f"🏭 INDUSTRIAL_MGR: Setting system status to {status.value}")

        self._current_system_status = status
        if self.tower_lamp_service:
            await self.tower_lamp_service.set_system_status(status)
        else:
            logger.error("🏭 INDUSTRIAL_MGR: Tower lamp service not initialized")

        # Notify all registered callbacks
        for callback in self._status_change_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.warning(f"🏭 INDUSTRIAL_MGR: Status change callback error: {e}")

    async def check_safety_conditions(self, current_states: Dict[int, bool]) -> bool:
        """
        Check safety sensor conditions and trigger alerts if needed

        Args:
            current_states: Current digital input states (channel -> state)

        Returns:
            True if all safety conditions are satisfied, False otherwise
        """
        await self._ensure_initialized()
        logger.debug("🏭 INDUSTRIAL_MGR: Checking safety conditions...")

        # Validate all required services and sensors are initialized
        if not self.safety_alert_service:
            logger.error("🏭 INDUSTRIAL_MGR: Safety alert service not initialized")
            return False

        if not all([self.door_sensor, self.clamp_sensor, self.chain_sensor]):
            logger.error("🏭 INDUSTRIAL_MGR: Safety sensors not initialized")
            return False

        # Check safety sensors - type ignore is safe due to validation above
        safety_alert = await self.safety_alert_service.check_safety_sensors(
            door_sensor=self.door_sensor,  # type: ignore
            clamp_sensor=self.clamp_sensor,  # type: ignore
            chain_sensor=self.chain_sensor,  # type: ignore
            current_states=current_states,
        )

        # Handle safety violation
        if safety_alert:
            # Only trigger alert if it's a new/different violation
            if (
                not self._last_safety_check_result
                or self._last_safety_check_result.violation_type != safety_alert.violation_type
            ):

                logger.warning(
                    f"🏭 INDUSTRIAL_MGR: Safety violation detected: {safety_alert.title}"
                )
                if self.safety_alert_service:
                    await self.safety_alert_service.trigger_safety_alert(safety_alert)

            self._last_safety_check_result = safety_alert
            return False
        else:
            # Clear previous safety violation if all sensors are now OK
            if self._last_safety_check_result:
                logger.info("🏭 INDUSTRIAL_MGR: Safety conditions restored")
                self._last_safety_check_result = None

                # Return to previous non-safety status if we were in safety violation
                if self.tower_lamp_service:
                    current_status = await self.tower_lamp_service.get_current_status()
                    if current_status == SystemStatus.SAFETY_VIOLATION:
                        await self.set_system_status(SystemStatus.SYSTEM_IDLE)

            return True

    async def handle_emergency_stop(self) -> None:
        """Handle emergency stop activation - RED BLINK + BEEP (only beep source)"""
        await self._ensure_initialized()
        logger.critical("🚨 INDUSTRIAL_MGR: Emergency stop activated!")

        # Set emergency status - RED BLINK + GREEN ON + BEEP
        await self.set_system_status(SystemStatus.EMERGENCY_STOP)

        # Trigger emergency stop alert
        if self.safety_alert_service:
            await self.safety_alert_service.trigger_emergency_stop_alert()

    async def handle_test_start_request(self, current_states: Dict[int, bool]) -> bool:
        """
        Handle test start request - Clear all lamps except GREEN, set to RUNNING

        Args:
            current_states: Current digital input states

        Returns:
            True if test can start (safety conditions OK), False otherwise
        """
        logger.info("🏭 INDUSTRIAL_MGR: Processing test start request...")

        # Check safety conditions
        safety_ok = await self.check_safety_conditions(current_states)

        if safety_ok:
            logger.info("🏭 INDUSTRIAL_MGR: Safety conditions satisfied - test can start")
            # SYSTEM_RUNNING: RED OFF, YELLOW OFF, GREEN ON (clears all previous states)
            await self.set_system_status(SystemStatus.SYSTEM_RUNNING)
            return True
        else:
            logger.warning("🏭 INDUSTRIAL_MGR: Safety conditions not satisfied - test blocked")
            return False

    async def handle_test_completion(self, test_success: bool, test_error: bool = False) -> None:
        """
        Handle test completion with appropriate status indication (no auto-transition)

        Args:
            test_success: Whether test completed successfully
            test_error: Whether test completed with error
        """
        if test_error:
            logger.error("🏭 INDUSTRIAL_MGR: Test completed with error - RED BLINK")
            await self.set_system_status(SystemStatus.SYSTEM_ERROR)
        elif test_success:
            logger.info("🏭 INDUSTRIAL_MGR: Test completed successfully (PASS) - GREEN BLINK")
            await self.set_system_status(SystemStatus.TEST_PASS)
        else:
            logger.warning("🏭 INDUSTRIAL_MGR: Test completed with failure (FAIL) - YELLOW BLINK")
            await self.set_system_status(SystemStatus.TEST_FAIL)
        # No auto-transition - user must press START TEST to clear

    async def clear_error(self) -> None:
        """
        Clear error state - Red BLINK → Red ON, Yellow OFF

        Transitions error states from blinking to steady:
        - SYSTEM_ERROR → TEST_ERROR_CLEARED (Red BLINK → Red ON)
        - EMERGENCY_STOP → EMERGENCY_CLEARED (Red BLINK → Red ON)
        - SAFETY_VIOLATION → SAFETY_CLEARED (Yellow BLINK → Yellow ON)
        - TEST_FAIL → Turn off Yellow (Yellow BLINK → OFF)
        """
        await self._ensure_initialized()

        if not self.tower_lamp_service:
            logger.error("🏭 INDUSTRIAL_MGR: Tower lamp service not initialized")
            return

        current_status = await self.tower_lamp_service.get_current_status()

        if current_status == SystemStatus.SYSTEM_ERROR:
            logger.info("🏭 INDUSTRIAL_MGR: Clearing test error - RED BLINK → RED ON")
            await self.set_system_status(SystemStatus.TEST_ERROR_CLEARED)
        elif current_status == SystemStatus.EMERGENCY_STOP:
            logger.info("🏭 INDUSTRIAL_MGR: Clearing emergency stop - RED BLINK → RED ON, BEEP OFF")
            await self.set_system_status(SystemStatus.EMERGENCY_CLEARED)
        elif current_status == SystemStatus.SAFETY_VIOLATION:
            logger.info("🏭 INDUSTRIAL_MGR: Clearing safety violation - YELLOW BLINK → YELLOW ON")
            await self.set_system_status(SystemStatus.SAFETY_CLEARED)
        elif current_status == SystemStatus.TEST_FAIL:
            logger.info("🏭 INDUSTRIAL_MGR: Clearing test fail - YELLOW OFF")
            await self.set_system_status(SystemStatus.SYSTEM_IDLE)
        else:
            logger.warning(
                f"🏭 INDUSTRIAL_MGR: No active error to clear (current status: {current_status})"
            )

    async def handle_system_error(self, error_message: str = "") -> None:
        """
        Handle system error condition

        Args:
            error_message: Optional error message
        """
        logger.error(f"🏭 INDUSTRIAL_MGR: System error: {error_message}")
        await self.set_system_status(SystemStatus.SYSTEM_ERROR)

    async def get_safety_sensor_status(
        self, current_states: Dict[int, bool]
    ) -> Dict[str, Union[Dict[str, Any], str, bool]]:
        """
        Get detailed safety sensor status for diagnostics

        Args:
            current_states: Current digital input states

        Returns:
            Dictionary with detailed sensor status information
        """
        await self._ensure_initialized()

        def get_sensor_info(sensor: DigitalPin, current_states: Dict[int, bool]) -> Dict:
            channel = sensor.pin_number
            raw_state = current_states.get(channel, False)

            # Apply contact type logic
            if sensor.contact_type == "A":  # A-contact (Normally Open)
                logical_state = raw_state
            else:  # B-contact (Normally Closed)
                logical_state = not raw_state

            return {
                "name": sensor.name,
                "channel": channel,
                "contact_type": sensor.contact_type,
                "edge_type": sensor.edge_type,
                "raw_state": raw_state,
                "logical_state": logical_state,
                "status_ok": logical_state,
            }

        if not all([self.door_sensor, self.clamp_sensor, self.chain_sensor]):
            return {"error": "Safety sensors not initialized"}

        # At this point we know all sensors are not None due to the check above
        assert self.door_sensor is not None
        assert self.clamp_sensor is not None
        assert self.chain_sensor is not None

        return {
            "door_sensor": get_sensor_info(self.door_sensor, current_states),
            "clamp_sensor": get_sensor_info(self.clamp_sensor, current_states),
            "chain_sensor": get_sensor_info(self.chain_sensor, current_states),
            "all_sensors_ok": (
                get_sensor_info(self.door_sensor, current_states)["status_ok"]
                and get_sensor_info(self.clamp_sensor, current_states)["status_ok"]
                and get_sensor_info(self.chain_sensor, current_states)["status_ok"]
            ),
        }

    async def get_system_status(self) -> Dict:
        """
        Get comprehensive system status

        Returns:
            Dictionary with system status information
        """
        return {
            "current_system_status": (
                self._current_system_status.value if self._current_system_status else None
            ),
            "tower_lamp_status": (
                await self.tower_lamp_service.get_lamp_states() if self.tower_lamp_service else {}
            ),
            "has_safety_violation": self._last_safety_check_result is not None,
            "last_safety_violation": (
                self._last_safety_check_result.violation_type.value
                if self._last_safety_check_result
                else None
            ),
            "digital_io_connected": (
                await self._digital_io_service.is_connected() if self._digital_io_service else False
            ),
        }

    async def shutdown_system(self) -> None:
        """Shutdown industrial system safely"""
        logger.info("🏭 INDUSTRIAL_MGR: Shutting down industrial system...")

        # Turn off all lamps and stop all patterns if initialized
        if self.tower_lamp_service:
            await self.tower_lamp_service.turn_off_all()

        # Set all digital outputs to LOW before disconnecting
        if self._initialized and self._digital_io_service:
            try:
                if await self._digital_io_service.is_connected():
                    logger.info("🏭 INDUSTRIAL_MGR: Setting all digital outputs to LOW...")
                    await self._digital_io_service.reset_all_outputs()
                    logger.info("🏭 INDUSTRIAL_MGR: All digital outputs set to LOW")

                    logger.info("🏭 INDUSTRIAL_MGR: Disconnecting Digital I/O service...")
                    await self._digital_io_service.disconnect()
                    logger.info("🏭 INDUSTRIAL_MGR: Digital I/O service disconnected")
            except Exception as e:
                logger.warning(
                    f"🏭 INDUSTRIAL_MGR: Failed to shutdown Digital I/O service cleanly: {e}"
                )

        # Clear state
        self._current_system_status = None
        self._last_safety_check_result = None
        self._initialized = False

        logger.info("🏭 INDUSTRIAL_MGR: Industrial system shutdown complete")

    async def test_system_components(self) -> None:
        """Test all system components (for maintenance/debugging)"""
        logger.info("🏭 INDUSTRIAL_MGR: Testing system components...")

        # Test tower lamp service
        if self.tower_lamp_service:
            logger.info("🚦 Testing tower lamps...")
            for status in SystemStatus:
                logger.info(f"Testing {status.value}...")
                await self.tower_lamp_service.set_system_status(status)
                # In a real test, we might wait for user confirmation here
                await asyncio.sleep(2)  # 2 second delay between tests

        # Test safety alert service
        logger.info("🔒 Testing safety alerts...")
        if self.safety_alert_service:
            await self.safety_alert_service.test_alert_system()

        # Return to idle state
        await self.set_system_status(SystemStatus.SYSTEM_IDLE)

        logger.info("🏭 INDUSTRIAL_MGR: System component testing complete")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_system()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        _ = exc_type, exc_val, exc_tb  # Unused parameters
        await self.shutdown_system()
