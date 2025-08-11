"""
Button Monitoring Service

Service for monitoring operator start buttons and triggering callbacks
when both buttons are pressed simultaneously.
"""

import asyncio
from typing import TYPE_CHECKING, Callable, Optional, Union, Awaitable

from loguru import logger

from src.application.interfaces.hardware.digital_io import DigitalIOService
from src.domain.value_objects.hardware_configuration import HardwareConfiguration

if TYPE_CHECKING:
    from application.use_cases.eol_force_test.main_executor import EOLForceTestUseCase


class ButtonMonitoringService:
    """
    Service for monitoring dual operator start buttons

    Monitors two digital input channels for simultaneous button presses
    and executes a callback function when both buttons are pressed together.
    Implements industrial safety patterns with debouncing.
    """

    def __init__(
        self,
        digital_io_service: DigitalIOService,
        hardware_config: HardwareConfiguration,
        eol_use_case: Optional["EOLForceTestUseCase"] = None,
        callback: Optional[Union[Callable[[], None], Callable[[], Awaitable[None]]]] = None,
    ):
        """
        Initialize button monitoring service

        Args:
            digital_io_service: Digital I/O service for reading button states
            hardware_config: Hardware configuration containing button channel assignments
            eol_use_case: EOL test use case to check execution state
            callback: Optional callback function to execute when buttons are pressed
        """
        self.digital_io = digital_io_service
        self.hardware_config = hardware_config
        self.eol_use_case = eol_use_case
        self.callback = callback

        # Button channels from configuration
        self.left_button_channel = hardware_config.digital_io.operator_start_button_left
        self.right_button_channel = hardware_config.digital_io.operator_start_button_right

        # Safety sensor channels from configuration
        self.clamp_sensor_channel = hardware_config.digital_io.dut_clamp_safety_sensor
        self.chain_sensor_channel = hardware_config.digital_io.dut_chain_safety_sensor
        self.door_sensor_channel = hardware_config.digital_io.safety_door_closed_sensor
        
        # Emergency stop button channel from configuration
        self.emergency_stop_channel = hardware_config.digital_io.emergency_stop_button

        # Events for signaling button presses
        self.button_pressed_event = asyncio.Event()
        self.emergency_stop_event = asyncio.Event()

        # Monitoring state
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False

        # Safety parameters
        self._debounce_time = 2.0  # seconds
        self._polling_interval = 0.1  # seconds

        logger.info(
            f"ButtonMonitoringService initialized - "
            f"Left button: channel {self.left_button_channel}, "
            f"Right button: channel {self.right_button_channel}, "
            f"Emergency stop: channel {self.emergency_stop_channel}, "
            f"Clamp safety sensor: channel {self.clamp_sensor_channel}, "
            f"Chain safety sensor: channel {self.chain_sensor_channel}, "
            f"Door safety sensor: channel {self.door_sensor_channel}"
        )

    async def start_monitoring(self) -> None:
        """
        Start monitoring button inputs in the background

        Creates an asyncio task that continuously monitors the button states
        and triggers events/callbacks when both buttons are pressed.
        """
        if self._is_monitoring:
            logger.warning("Button monitoring is already active")
            return

        logger.info("Starting button monitoring service...")
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("Button monitoring service started")

    async def stop_monitoring(self) -> None:
        """
        Stop monitoring button inputs

        Cancels the monitoring task and cleans up resources.
        """
        if not self._is_monitoring:
            logger.warning("Button monitoring is not active")
            return

        logger.info("Stopping button monitoring service...")
        self._is_monitoring = False

        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        self._monitoring_task = None
        logger.info("Button monitoring service stopped")

    async def _monitor_loop(self) -> None:
        """
        Main monitoring loop (internal)

        Continuously polls button states and detects simultaneous presses.
        Implements debouncing and safety interlocks.
        """
        logger.info(
            f"Button monitoring loop started - polling every {self._polling_interval}s, "
            f"debounce time: {self._debounce_time}s"
        )

        try:
            while self._is_monitoring:
                try:
                    await self._process_button_cycle()
                except Exception as e:
                    logger.error(f"Error in button monitoring loop: {e}")
                    await asyncio.sleep(1.0)  # Error recovery delay

        except asyncio.CancelledError:
            logger.info("Button monitoring loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in button monitoring loop: {e}")
        finally:
            logger.info("Button monitoring loop ended")

    async def _check_safety_sensors(self) -> bool:
        """
        Check if all safety sensors are active

        Returns:
            True if all safety sensors (clamp, chain, door) are active, False otherwise
        """
        try:
            clamp_sensor_active = await self.digital_io.read_input(self.clamp_sensor_channel)
            chain_sensor_active = await self.digital_io.read_input(self.chain_sensor_channel)
            door_sensor_active = await self.digital_io.read_input(self.door_sensor_channel)

            logger.debug(
                f"Safety sensor states - Clamp: {clamp_sensor_active}, "
                f"Chain: {chain_sensor_active}, Door: {door_sensor_active}"
            )

            return clamp_sensor_active and chain_sensor_active and door_sensor_active
        except Exception as e:
            logger.error(f"Error reading safety sensors: {e}")
            return False

    async def _process_button_cycle(self) -> None:
        """Process a single button monitoring cycle"""
        # Check if digital I/O service is connected
        if not await self.digital_io.is_connected():
            logger.warning("Digital I/O service not connected, waiting...")
            await asyncio.sleep(1.0)
            return

        # Read emergency stop button first (highest priority)
        emergency_stop_pressed = await self.digital_io.read_input(self.emergency_stop_channel)
        
        if emergency_stop_pressed:
            logger.critical("🚨 EMERGENCY STOP BUTTON PRESSED! 🚨")
            await self._handle_emergency_stop()
            return  # Skip other button checks during emergency

        # Read both operator start button states
        left_button_pressed = await self.digital_io.read_input(self.left_button_channel)
        right_button_pressed = await self.digital_io.read_input(self.right_button_channel)

        # Check for simultaneous press (industrial safety requirement)
        if left_button_pressed and right_button_pressed:
            # Check safety sensors before proceeding
            if await self._check_safety_sensors():
                await self._handle_button_press()
            else:
                logger.warning(
                    "Both buttons pressed but safety sensors not satisfied - "
                    "DUT must be properly clamped, chained, and safety door must be closed"
                )
                # Apply polling interval to prevent rapid warnings
                await asyncio.sleep(self._polling_interval)
        else:
            # Polling interval
            await asyncio.sleep(self._polling_interval)

    async def _handle_button_press(self) -> None:
        """Handle dual button press event with safety confirmation"""
        logger.info(
            f"Dual button press detected with all safety sensors satisfied! "
            f"Buttons - Left: {self.left_button_channel}, Right: {self.right_button_channel}, "
            f"Safety sensors - Clamp: {self.clamp_sensor_channel}, Chain: {self.chain_sensor_channel}, "
            f"Door: {self.door_sensor_channel}"
        )

        # Check if EOL test is currently running to prevent duplicate execution
        if self.eol_use_case and self.eol_use_case.is_running():
            logger.info("EOL test is already running, ignoring button press")
            # Still apply debounce period to prevent rapid checks
            await asyncio.sleep(self._debounce_time)
            return

        # Signal event
        self.button_pressed_event.set()

        # Execute callback if provided
        await self._execute_callback()

        # Debouncing - prevent rapid repeated triggers
        await asyncio.sleep(self._debounce_time)

        # Clear event after debounce period
        self.button_pressed_event.clear()

        logger.debug(f"Button debounce period completed ({self._debounce_time}s)")

    async def _execute_callback(self) -> None:
        """Execute the button press callback"""
        if not self.callback:
            return

        try:
            if asyncio.iscoroutinefunction(self.callback):
                await self.callback()
            else:
                self.callback()
            logger.info("Button press callback executed successfully")
        except Exception as e:
            logger.error(f"Error executing button press callback: {e}")

    def set_callback(self, callback: Union[Callable[[], None], Callable[[], Awaitable[None]]]) -> None:
        """
        Set or update the callback function

        Args:
            callback: Function to call when buttons are pressed
        """
        self.callback = callback
        logger.info("Button press callback updated")

    def set_debounce_time(self, debounce_time: float) -> None:
        """
        Set button debounce time

        Args:
            debounce_time: Debounce time in seconds
        """
        if debounce_time < 0.1:
            raise ValueError("Debounce time must be at least 0.1 seconds")

        self._debounce_time = debounce_time
        logger.info(f"Button debounce time set to {debounce_time}s")

    def set_polling_interval(self, polling_interval: float) -> None:
        """
        Set button polling interval

        Args:
            polling_interval: Polling interval in seconds
        """
        if polling_interval < 0.01:
            raise ValueError("Polling interval must be at least 0.01 seconds")

        self._polling_interval = polling_interval
        logger.info(f"Button polling interval set to {polling_interval}s")

    async def get_button_states(self) -> dict:
        """
        Get current button states for diagnostics

        Returns:
            Dictionary containing current button states and configuration
        """
        try:
            if not await self.digital_io.is_connected():
                return {
                    "connected": False,
                    "left_button": None,
                    "right_button": None,
                    "emergency_stop": None,
                    "left_channel": self.left_button_channel,
                    "right_channel": self.right_button_channel,
                    "emergency_stop_channel": self.emergency_stop_channel,
                }

            left_state = await self.digital_io.read_input(self.left_button_channel)
            right_state = await self.digital_io.read_input(self.right_button_channel)
            emergency_stop_state = await self.digital_io.read_input(self.emergency_stop_channel)
            clamp_sensor_state = await self.digital_io.read_input(self.clamp_sensor_channel)
            chain_sensor_state = await self.digital_io.read_input(self.chain_sensor_channel)
            door_sensor_state = await self.digital_io.read_input(self.door_sensor_channel)

            return {
                "connected": True,
                "left_button": left_state,
                "right_button": right_state,
                "emergency_stop": emergency_stop_state,
                "left_channel": self.left_button_channel,
                "right_channel": self.right_button_channel,
                "emergency_stop_channel": self.emergency_stop_channel,
                "both_pressed": left_state and right_state,
                "clamp_safety_sensor": clamp_sensor_state,
                "chain_safety_sensor": chain_sensor_state,
                "door_safety_sensor": door_sensor_state,
                "clamp_sensor_channel": self.clamp_sensor_channel,
                "chain_sensor_channel": self.chain_sensor_channel,
                "door_sensor_channel": self.door_sensor_channel,
                "emergency_stop_active": emergency_stop_state,
                "safety_sensors_satisfied": clamp_sensor_state and chain_sensor_state and door_sensor_state,
                "all_conditions_met": left_state and right_state and clamp_sensor_state and chain_sensor_state and door_sensor_state,
                "monitoring": self._is_monitoring,
                "debounce_time": self._debounce_time,
                "polling_interval": self._polling_interval,
            }
        except Exception as e:
            logger.error(f"Error reading button states: {e}")
            return {
                "connected": False,
                "error": str(e),
                "left_channel": self.left_button_channel,
                "right_channel": self.right_button_channel,
                "emergency_stop_channel": self.emergency_stop_channel,
                "clamp_sensor_channel": self.clamp_sensor_channel,
                "chain_sensor_channel": self.chain_sensor_channel,
                "door_sensor_channel": self.door_sensor_channel,
            }

    async def _handle_emergency_stop(self) -> None:
        """Handle emergency stop button press with immediate hardware safety actions"""
        logger.critical(
            f"🚨 EMERGENCY STOP ACTIVATED! Channel: {self.emergency_stop_channel} 🚨"
        )
        
        # Signal emergency stop event
        self.emergency_stop_event.set()
        
        # Execute emergency stop callback if provided
        await self._execute_emergency_stop_callback()
        
        # Emergency stops typically don't have debounce period - immediate action required
        # But we clear the event after handling
        self.emergency_stop_event.clear()
        
        logger.critical("Emergency stop handling completed")

    async def _execute_emergency_stop_callback(self) -> None:
        """Execute emergency stop specific callback if available"""
        # For emergency stop, we need a dedicated callback
        # This will be set when integrating with main application
        if hasattr(self, 'emergency_stop_callback') and self.emergency_stop_callback:
            try:
                if asyncio.iscoroutinefunction(self.emergency_stop_callback):
                    await self.emergency_stop_callback()
                else:
                    self.emergency_stop_callback()
                logger.info("Emergency stop callback executed successfully")
            except Exception as e:
                logger.error(f"Error executing emergency stop callback: {e}")
        else:
            logger.warning("No emergency stop callback configured - only logging emergency stop")

    def set_emergency_stop_callback(self, callback: Union[Callable[[], None], Callable[[], Awaitable[None]]]) -> None:
        """
        Set emergency stop callback function
        
        Args:
            callback: Function to call when emergency stop is pressed
        """
        self.emergency_stop_callback = callback
        logger.info("Emergency stop callback configured")

    def is_monitoring(self) -> bool:
        """
        Check if button monitoring is active

        Returns:
            True if monitoring is active, False otherwise
        """
        return self._is_monitoring

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_monitoring()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        _ = exc_type, exc_val, exc_tb  # Unused parameters
        await self.stop_monitoring()
