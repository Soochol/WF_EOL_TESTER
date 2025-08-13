"""
Button Monitoring Service

Service for monitoring operator start buttons and triggering callbacks
when both buttons are pressed simultaneously.
"""

import asyncio
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Union

from loguru import logger

from application.interfaces.hardware.digital_io import DigitalIOService
from domain.value_objects.hardware_configuration import HardwareConfiguration

if TYPE_CHECKING:
    from application.use_cases.eol_force_test.main_executor import EOLForceTestUseCase


class DIOMonitoringService:
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
        emergency_stop_callback: Optional[
            Union[Callable[[], None], Callable[[], Awaitable[None]]]
        ] = None,
    ):
        """
        Initialize button monitoring service

        Args:
            digital_io_service: Digital I/O service for reading button states
            hardware_config: Hardware configuration containing button channel assignments
            eol_use_case: EOL test use case to check execution state
            callback: Optional callback function to execute when buttons are pressed
            emergency_stop_callback: Optional callback function to execute when emergency stop is pressed
        """
        self.digital_io = digital_io_service
        self.hardware_config = hardware_config
        self.eol_use_case = eol_use_case
        self.callback = callback
        self.emergency_stop_callback = emergency_stop_callback

        # Digital pin configurations from hardware config
        self.emergency_stop_pin = hardware_config.digital_io.emergency_stop_button
        self.left_button_pin = hardware_config.digital_io.operator_start_button_left
        self.right_button_pin = hardware_config.digital_io.operator_start_button_right
        self.clamp_sensor_pin = hardware_config.digital_io.dut_clamp_safety_sensor
        self.chain_sensor_pin = hardware_config.digital_io.dut_chain_safety_sensor
        self.door_sensor_pin = hardware_config.digital_io.safety_door_closed_sensor

        # Events for signaling button presses
        self.button_pressed_event = asyncio.Event()
        self.emergency_stop_event = asyncio.Event()

        # Monitoring state
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False

        # State tracking for edge detection
        self._previous_states: Dict[int, bool] = {}
        self._first_read = True
        
        # Edge-based dual button press detection
        self._left_button_edge_time: Optional[float] = None
        self._right_button_edge_time: Optional[float] = None
        self._dual_press_window = 0.2  # 200ms window for dual press detection
        self._edge_cleanup_task: Optional[asyncio.Task] = None

        # Build channel configuration from DigitalPin objects
        logger.info("🔧 DIO_INIT: Building channel configuration from DigitalPin objects...")
        self._channel_config = self._build_channel_config()
        logger.info(
            f"🔧 DIO_INIT: Channel configuration built - {len(self._channel_config)} channels configured"
        )

        # Safety parameters
        self._debounce_time = 2.0  # seconds
        self._polling_interval = 0.1  # seconds
        logger.info(
            f"🔧 DIO_INIT: Safety parameters set - debounce: {self._debounce_time}s, polling: {self._polling_interval}s"
        )

        # Log detailed channel configuration
        for channel, config in self._channel_config.items():
            pin = config["pin"]
            action_type = "callback" if config["action"] else "monitoring only"
            logger.info(
                f"🔧 DIO_INIT: Channel {channel} -> {pin.name} "
                f"(pin {pin.pin_number}, {pin.contact_type}-contact, {pin.edge_type} edge, {action_type})"
            )

        logger.info(
            f"✅ DIOMonitoringService initialized - "
            f"Left button: channel {self.left_button_pin.pin_number}, "
            f"Right button: channel {self.right_button_pin.pin_number}, "
            f"Emergency stop: channel {self.emergency_stop_pin.pin_number}, "
            f"Clamp safety sensor: channel {self.clamp_sensor_pin.pin_number}, "
            f"Chain safety sensor: channel {self.chain_sensor_pin.pin_number}, "
            f"Door safety sensor: channel {self.door_sensor_pin.pin_number}"
        )

    async def start_monitoring(self) -> None:
        """
        Start monitoring button inputs in the background

        Creates an asyncio task that continuously monitors the button states
        and triggers events/callbacks when both buttons are pressed.
        """
        logger.info("🔧 DIO_START: Attempting to start button monitoring...")

        if self._is_monitoring:
            logger.warning("⚠️ DIO_START: Button monitoring is already active")
            return

        # Verify digital I/O connection before starting
        try:
            connection_status = await self.digital_io.is_connected()
            logger.info(f"🔧 DIO_START: Digital I/O connection status: {connection_status}")
        except Exception as e:
            logger.error(f"❌ DIO_START: Failed to check Digital I/O connection: {e}")

        logger.info("🔧 DIO_START: Creating monitoring task...")
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("✅ DIO_START: Button monitoring service started successfully")
        logger.info(
            f"🔧 DIO_START: Monitoring parameters - polling interval: {self._polling_interval}s, debounce time: {self._debounce_time}s"
        )

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

        # Cancel edge cleanup task if running
        if self._edge_cleanup_task and not self._edge_cleanup_task.done():
            self._edge_cleanup_task.cancel()
            try:
                await self._edge_cleanup_task
            except asyncio.CancelledError:
                pass

        self._monitoring_task = None
        self._edge_cleanup_task = None
        
        # Clear edge times
        self._left_button_edge_time = None
        self._right_button_edge_time = None
        
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

    def _build_channel_config(self) -> Dict[int, Dict[str, Any]]:
        """
        Build channel configuration mapping from DigitalPin objects

        Returns:
            Dictionary mapping pin numbers to their configuration and actions
        """
        return {
            self.emergency_stop_pin.pin_number: {
                "pin": self.emergency_stop_pin,
                "action": self._handle_emergency_stop,
            },
            self.left_button_pin.pin_number: {
                "pin": self.left_button_pin,
                "action": self._handle_left_button_press,
            },
            self.right_button_pin.pin_number: {
                "pin": self.right_button_pin,
                "action": self._handle_right_button_press,
            },
            self.clamp_sensor_pin.pin_number: {
                "pin": self.clamp_sensor_pin,
                "action": None,  # Safety sensors don't have individual actions
            },
            self.chain_sensor_pin.pin_number: {"pin": self.chain_sensor_pin, "action": None},
            self.door_sensor_pin.pin_number: {"pin": self.door_sensor_pin, "action": None},
        }

    async def _read_all_channels(self) -> List[bool]:
        """
        Read all input channels

        Returns:
            List of boolean values representing all input states (index = channel number)
        """
        try:
            # Read all input channels at once
            all_states = await self.digital_io.read_all_inputs()

            logger.debug(f"Read all inputs: {len(all_states)} channels")
            return all_states

        except Exception as e:
            logger.error(f"Error reading all input channels: {e}")
            # Return safe default states on error (assume 32 channels)
            return [False] * 32

    def _detect_channel_edges(
        self, current_raw_states: List[bool], previous_raw_states: List[bool]
    ) -> List[int]:
        """
        Detect edge events for configured channels based on their contact type and edge type

        Args:
            current_raw_states: Current raw channel states (list, index = channel number)
            previous_raw_states: Previous raw channel states (list, index = channel number)

        Returns:
            List of channel numbers that had their configured edge events
        """
        edge_channels = []

        # Ensure previous_raw_states has same length as current
        if len(previous_raw_states) != len(current_raw_states):
            previous_raw_states = [False] * len(current_raw_states)

        for channel, config in self._channel_config.items():
            pin = config["pin"]

            # Safely get current and previous states (bounds check)
            if channel >= len(current_raw_states):
                continue

            current_raw = current_raw_states[channel]
            previous_raw = (
                previous_raw_states[channel] if channel < len(previous_raw_states) else False
            )

            # Apply contact type logic
            if pin.contact_type == "A":  # A-contact (Normally Open)
                current_logical = current_raw
                previous_logical = previous_raw
            else:  # B-contact (Normally Closed)
                current_logical = not current_raw
                previous_logical = not previous_raw

            # Check for configured edge type
            edge_detected = False
            if pin.edge_type == "rising":
                edge_detected = not previous_logical and current_logical
            elif pin.edge_type == "falling":
                edge_detected = previous_logical and not current_logical
            elif pin.edge_type == "both":
                edge_detected = previous_logical != current_logical

            if edge_detected:
                edge_channels.append(channel)
                logger.debug(
                    f"Edge detected on {pin.name} (channel {channel}): {pin.edge_type} edge, contact_type={pin.contact_type}"
                )

        return edge_channels

    async def _process_button_cycle(self) -> None:
        """Process a single button monitoring cycle with batch read and edge detection"""
        # Check if digital I/O service is connected
        if not await self.digital_io.is_connected():
            logger.warning("⚠️ DIO_CYCLE: Digital I/O service not connected, waiting...")
            await asyncio.sleep(1.0)
            return

        # Read all input channels
        current_raw_states = await self._read_all_channels()

        # Log channel count on first read
        if self._first_read:
            logger.info(
                f"🔧 DIO_CYCLE: First read completed - {len(current_raw_states)} channels read"
            )

        # Get previous states for edge detection (convert dict back to list for consistency)
        if self._first_read:
            previous_raw_states = [False] * len(current_raw_states)
        else:
            # Convert dict back to list format, maintaining channel order
            previous_raw_states = [
                self._previous_states.get(i, False) for i in range(len(current_raw_states))
            ]

        # Detect edge events on any configured channels
        edge_channels = self._detect_channel_edges(current_raw_states, previous_raw_states)

        # Log edge detection results (only when edges are detected to avoid spam)
        if edge_channels:
            logger.info(f"🎯 DIO_CYCLE: Edge detected on channels: {edge_channels}")
            for channel in edge_channels:
                config = self._channel_config[channel]
                pin = config["pin"]
                logger.info(
                    f"🎯 DIO_CYCLE: Channel {channel} ({pin.name}) - {pin.edge_type} edge detected"
                )

        # Process edge events by priority
        for channel in edge_channels:
            config = self._channel_config[channel]
            action = config["action"]

            if channel == self.emergency_stop_pin.pin_number:
                logger.critical("🚨 EMERGENCY STOP BUTTON PRESSED! 🚨")
                logger.critical(
                    f"🚨 DIO_CYCLE: Emergency stop action triggered on channel {channel}"
                )
                await action()
                break  # Emergency stop has highest priority

            elif channel in [self.left_button_pin.pin_number, self.right_button_pin.pin_number]:
                # Handle operator button presses
                button_name = "left" if channel == self.left_button_pin.pin_number else "right"
                logger.info(
                    f"🎯 DIO_CYCLE: {button_name.title()} button pressed (channel {channel}) - checking dual press conditions"
                )
                await self._handle_operator_button_press(channel, current_raw_states)

        # Store current states as previous for next cycle (convert list to dict indexed by channel)
        self._previous_states = dict(enumerate(current_raw_states))
        self._first_read = False

        # Apply polling interval
        await asyncio.sleep(self._polling_interval)

    async def _handle_operator_button_press(
        self, pressed_channel: int, current_raw_states: List[bool]
    ) -> None:
        """
        Handle operator button press - use edge-based dual button press detection

        Args:
            pressed_channel: Channel number of the button that was pressed
            current_raw_states: Current raw states of all channels (list, index = channel number)
        """
        import time
        
        logger.info(f"🎯 DIO_BUTTON: Processing button press edge on channel {pressed_channel}")
        
        current_time = time.time()
        left_ch = self.left_button_pin.pin_number
        right_ch = self.right_button_pin.pin_number

        # Record edge detection time for this button
        if pressed_channel == left_ch:
            self._left_button_edge_time = current_time
            button_name = "Left"
        elif pressed_channel == right_ch:
            self._right_button_edge_time = current_time
            button_name = "Right"
        else:
            logger.warning(f"🎯 DIO_BUTTON: Unknown button channel {pressed_channel}")
            return

        logger.info(f"🎯 DIO_BUTTON: {button_name} button edge detected at {current_time:.3f}")

        # Check for dual button press within the time window
        dual_press_detected = False
        
        if self._left_button_edge_time and self._right_button_edge_time:
            time_diff = abs(self._left_button_edge_time - self._right_button_edge_time)
            logger.info(f"🎯 DIO_BUTTON: Time difference between button edges: {time_diff:.3f}s")
            
            if time_diff <= self._dual_press_window:
                dual_press_detected = True
                logger.info(
                    f"🎯 DIO_BUTTON: ✅ DUAL BUTTON PRESS DETECTED! "
                    f"Left: {self._left_button_edge_time:.3f}, Right: {self._right_button_edge_time:.3f}, "
                    f"Diff: {time_diff:.3f}s (window: {self._dual_press_window}s)"
                )
            else:
                logger.info(
                    f"🎯 DIO_BUTTON: Time window exceeded for dual press "
                    f"(diff: {time_diff:.3f}s > window: {self._dual_press_window}s)"
                )

        if dual_press_detected:
            # Check safety conditions
            clamp_ch = self.clamp_sensor_pin.pin_number
            chain_ch = self.chain_sensor_pin.pin_number
            door_ch = self.door_sensor_pin.pin_number

            clamp_ok = current_raw_states[clamp_ch] if clamp_ch < len(current_raw_states) else False
            chain_ok = current_raw_states[chain_ch] if chain_ch < len(current_raw_states) else False
            door_ok = current_raw_states[door_ch] if door_ch < len(current_raw_states) else False

            logger.info(f"🔒 DIO_SAFETY: Safety sensor states - Clamp (ch{clamp_ch}): {clamp_ok}")
            logger.info(f"🔒 DIO_SAFETY: Safety sensor states - Chain (ch{chain_ch}): {chain_ok}")
            logger.info(f"🔒 DIO_SAFETY: Safety sensor states - Door (ch{door_ch}): {door_ok}")

            if clamp_ok and chain_ok and door_ok:
                logger.info(
                    "✅ DIO_SAFETY: All safety sensors satisfied! Proceeding with callback execution..."
                )
                
                # Clear edge times after successful dual press
                self._left_button_edge_time = None
                self._right_button_edge_time = None
                
                await self._handle_button_press()
            else:
                logger.warning(
                    f"❌ DIO_SAFETY: Safety sensors not satisfied - "
                    f"Clamp: {clamp_ok}, Chain: {chain_ok}, Door: {door_ok}"
                )
                logger.warning("❌ DIO_SAFETY: Dual button press BLOCKED due to safety conditions")
                
                # Clear edge times after blocked attempt
                self._left_button_edge_time = None
                self._right_button_edge_time = None
        else:
            pin_name = self._channel_config[pressed_channel]["pin"].name
            logger.info(
                f"🎯 DIO_BUTTON: Single button edge detected ({pin_name}) - waiting for dual press within {self._dual_press_window}s"
            )
            
            # Start or restart edge cleanup timer
            await self._start_edge_cleanup_timer()
    
    async def _start_edge_cleanup_timer(self) -> None:
        """Start edge cleanup timer to clear edge times after dual press window expires"""
        # Cancel existing cleanup task if running
        if self._edge_cleanup_task and not self._edge_cleanup_task.done():
            self._edge_cleanup_task.cancel()
            
        # Start new cleanup task
        self._edge_cleanup_task = asyncio.create_task(self._edge_cleanup_worker())
    
    async def _edge_cleanup_worker(self) -> None:
        """Worker task to clean up edge times after timeout"""
        try:
            # Wait for dual press window + small buffer
            await asyncio.sleep(self._dual_press_window + 0.1)
            
            # Clear edge times if no dual press occurred
            if self._left_button_edge_time or self._right_button_edge_time:
                logger.debug("🎯 DIO_BUTTON: Clearing edge times after timeout")
                self._left_button_edge_time = None
                self._right_button_edge_time = None
                
        except asyncio.CancelledError:
            # Task was cancelled, which is normal when new edges are detected
            pass

    async def _handle_left_button_press(self) -> None:
        """Handle left button individual press (for future use)"""
        logger.debug("Left button pressed")

    async def _handle_right_button_press(self) -> None:
        """Handle right button individual press (for future use)"""
        logger.debug("Right button pressed")

    async def _handle_button_press(self) -> None:
        """Handle dual button press event with safety confirmation"""
        logger.info("🚀 DIO_CALLBACK: Starting dual button press handler...")
        logger.info(
            f"🚀 DIO_CALLBACK: Dual button press confirmed with all safety sensors satisfied! "
            f"Buttons - Left: {self.left_button_pin.pin_number}, Right: {self.right_button_pin.pin_number}, "
            f"Safety sensors - Clamp: {self.clamp_sensor_pin.pin_number}, Chain: {self.chain_sensor_pin.pin_number}, "
            f"Door: {self.door_sensor_pin.pin_number}"
        )

        # Check if EOL test is currently running to prevent duplicate execution
        if self.eol_use_case and self.eol_use_case.is_running():
            logger.warning("⚠️ DIO_CALLBACK: EOL test is already running, ignoring button press")
            logger.warning("⚠️ DIO_CALLBACK: Applying debounce period before allowing next press")
            # Still apply debounce period to prevent rapid checks
            await asyncio.sleep(self._debounce_time)
            return

        logger.info("🚀 DIO_CALLBACK: EOL test not running - proceeding with callback execution")

        # Signal event
        self.button_pressed_event.set()
        logger.info("🚀 DIO_CALLBACK: Button pressed event signaled")

        # Execute callback if provided
        logger.info("🚀 DIO_CALLBACK: Executing callback function...")
        await self._execute_callback()
        logger.info("🚀 DIO_CALLBACK: Callback execution completed")

        # Debouncing - prevent rapid repeated triggers
        logger.info(f"🚀 DIO_CALLBACK: Starting debounce period ({self._debounce_time}s)...")
        await asyncio.sleep(self._debounce_time)

        # Clear event after debounce period
        self.button_pressed_event.clear()
        logger.info(
            f"✅ DIO_CALLBACK: Button debounce period completed ({self._debounce_time}s) - ready for next press"
        )

    async def _execute_callback(self) -> None:
        """Execute the button press callback"""
        logger.info("🎯 CALLBACK_EXEC: Starting callback execution...")

        if not self.callback:
            logger.warning("⚠️ CALLBACK_EXEC: No callback function provided - skipping execution")
            return

        logger.info("🎯 CALLBACK_EXEC: Callback function found - determining execution type...")

        try:
            if asyncio.iscoroutinefunction(self.callback):
                logger.info("🎯 CALLBACK_EXEC: Executing async callback function...")
                await self.callback()
            else:
                logger.info("🎯 CALLBACK_EXEC: Executing sync callback function...")
                self.callback()
            logger.info("✅ CALLBACK_EXEC: Button press callback executed successfully")
        except Exception as e:
            logger.error(f"❌ CALLBACK_EXEC: Error executing button press callback: {e}")
            import traceback

            logger.debug(
                f"❌ CALLBACK_EXEC: Callback execution traceback: {traceback.format_exc()}"
            )

    def set_callback(
        self, callback: Union[Callable[[], None], Callable[[], Awaitable[None]]]
    ) -> None:
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
                    "left_channel": self.left_button_pin.pin_number,
                    "right_channel": self.right_button_pin.pin_number,
                    "emergency_stop_channel": self.emergency_stop_pin.pin_number,
                }

            # Read raw button states
            left_state_raw = await self.digital_io.read_input(self.left_button_pin.pin_number)
            right_state_raw = await self.digital_io.read_input(self.right_button_pin.pin_number)
            emergency_stop_state = await self.digital_io.read_input(
                self.emergency_stop_pin.pin_number
            )
            clamp_sensor_state = await self.digital_io.read_input(self.clamp_sensor_pin.pin_number)
            chain_sensor_state = await self.digital_io.read_input(self.chain_sensor_pin.pin_number)
            door_sensor_state = await self.digital_io.read_input(self.door_sensor_pin.pin_number)

            # Apply B-contact logic for start buttons (pressed = not raw_state)
            left_button_pressed = not left_state_raw
            right_button_pressed = not right_state_raw

            return {
                "connected": True,
                "left_button": left_button_pressed,
                "right_button": right_button_pressed,
                "left_button_raw": left_state_raw,
                "right_button_raw": right_state_raw,
                "emergency_stop": emergency_stop_state,
                "left_channel": self.left_button_pin.pin_number,
                "right_channel": self.right_button_pin.pin_number,
                "emergency_stop_channel": self.emergency_stop_pin.pin_number,
                "both_pressed": left_button_pressed and right_button_pressed,
                "clamp_safety_sensor": clamp_sensor_state,
                "chain_safety_sensor": chain_sensor_state,
                "door_safety_sensor": door_sensor_state,
                "clamp_sensor_channel": self.clamp_sensor_pin.pin_number,
                "chain_sensor_channel": self.chain_sensor_pin.pin_number,
                "door_sensor_channel": self.door_sensor_pin.pin_number,
                "emergency_stop_active": emergency_stop_state,
                "safety_sensors_satisfied": (
                    clamp_sensor_state and chain_sensor_state and door_sensor_state
                ),
                "all_conditions_met": (
                    left_button_pressed
                    and right_button_pressed
                    and clamp_sensor_state
                    and chain_sensor_state
                    and door_sensor_state
                ),
                "monitoring": self._is_monitoring,
                "debounce_time": self._debounce_time,
                "polling_interval": self._polling_interval,
            }
        except Exception as e:
            logger.error(f"Error reading button states: {e}")
            return {
                "connected": False,
                "error": str(e),
                "left_channel": self.left_button_pin.pin_number,
                "right_channel": self.right_button_pin.pin_number,
                "emergency_stop_channel": self.emergency_stop_pin.pin_number,
                "clamp_sensor_channel": self.clamp_sensor_pin.pin_number,
                "chain_sensor_channel": self.chain_sensor_pin.pin_number,
                "door_sensor_channel": self.door_sensor_pin.pin_number,
            }

    async def _handle_emergency_stop(self) -> None:
        """Handle emergency stop button press with immediate hardware safety actions"""
        logger.critical(
            f"🚨 EMERGENCY STOP ACTIVATED! Channel: {self.emergency_stop_pin.pin_number} 🚨"
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
        logger.critical("🚨 EMERGENCY_CALLBACK: Starting emergency stop callback execution...")

        # For emergency stop, we need a dedicated callback
        # This will be set when integrating with main application
        if hasattr(self, "emergency_stop_callback") and self.emergency_stop_callback:
            logger.critical("🚨 EMERGENCY_CALLBACK: Emergency stop callback found - executing...")
            try:
                if asyncio.iscoroutinefunction(self.emergency_stop_callback):
                    logger.critical(
                        "🚨 EMERGENCY_CALLBACK: Executing async emergency stop callback..."
                    )
                    await self.emergency_stop_callback()
                else:
                    logger.critical(
                        "🚨 EMERGENCY_CALLBACK: Executing sync emergency stop callback..."
                    )
                    self.emergency_stop_callback()
                logger.critical(
                    "✅ EMERGENCY_CALLBACK: Emergency stop callback executed successfully"
                )
            except Exception as e:
                logger.error(f"❌ EMERGENCY_CALLBACK: Error executing emergency stop callback: {e}")
                import traceback

                logger.debug(
                    f"❌ EMERGENCY_CALLBACK: Emergency callback traceback: {traceback.format_exc()}"
                )
        else:
            logger.warning(
                "⚠️ EMERGENCY_CALLBACK: No emergency stop callback configured - only logging emergency stop"
            )

    def is_monitoring(self) -> bool:
        """
        Check if button monitoring is active

        Returns:
            True if monitoring is active, False otherwise
        """
        return self._is_monitoring

    async def get_detailed_status(self) -> dict:
        """
        Get comprehensive status information for troubleshooting

        Returns:
            Dictionary containing detailed status information
        """
        logger.info("🔍 VERIFICATION_TOOL: Gathering detailed status information...")

        status = {
            "monitoring_active": self._is_monitoring,
            "digital_io_connected": False,
            "channel_config": {},
            "current_states": {},
            "callback_configured": self.callback is not None,
            "emergency_callback_configured": (
                hasattr(self, "emergency_stop_callback")
                and self.emergency_stop_callback is not None
            ),
            "debounce_time": self._debounce_time,
            "polling_interval": self._polling_interval,
            "first_read": self._first_read,
            "task_status": "unknown",
        }

        try:
            # Check Digital I/O connection
            status["digital_io_connected"] = await self.digital_io.is_connected()

            # Get input count if connected
            if status["digital_io_connected"]:
                status["input_count"] = await self.digital_io.get_input_count()

                # Read current states
                current_raw_states = await self._read_all_channels()
                status["total_channels_read"] = len(current_raw_states)

                # Process each configured channel
                for channel, config in self._channel_config.items():
                    pin = config["pin"]
                    raw_state = (
                        current_raw_states[channel] if channel < len(current_raw_states) else False
                    )

                    # Apply contact type logic
                    if pin.contact_type == "A":
                        logical_state = raw_state
                    else:
                        logical_state = not raw_state

                    status["channel_config"][channel] = {
                        "pin_name": pin.name,
                        "pin_number": pin.pin_number,
                        "contact_type": pin.contact_type,
                        "edge_type": pin.edge_type,
                        "raw_state": raw_state,
                        "logical_state": logical_state,
                        "has_action": config["action"] is not None,
                    }

                # Check dual button press condition
                left_ch = self.left_button_pin.pin_number
                right_ch = self.right_button_pin.pin_number
                left_pressed = (
                    not current_raw_states[left_ch] if left_ch < len(current_raw_states) else False
                )
                right_pressed = (
                    not current_raw_states[right_ch]
                    if right_ch < len(current_raw_states)
                    else False
                )

                status["dual_button_condition"] = {
                    "left_pressed": left_pressed,
                    "right_pressed": right_pressed,
                    "both_pressed": left_pressed and right_pressed,
                }

                # Check safety conditions
                clamp_ch = self.clamp_sensor_pin.pin_number
                chain_ch = self.chain_sensor_pin.pin_number
                door_ch = self.door_sensor_pin.pin_number

                clamp_ok = (
                    current_raw_states[clamp_ch] if clamp_ch < len(current_raw_states) else False
                )
                chain_ok = (
                    current_raw_states[chain_ch] if chain_ch < len(current_raw_states) else False
                )
                door_ok = (
                    current_raw_states[door_ch] if door_ch < len(current_raw_states) else False
                )

                status["safety_conditions"] = {
                    "clamp_ok": clamp_ok,
                    "chain_ok": chain_ok,
                    "door_ok": door_ok,
                    "all_satisfied": clamp_ok and chain_ok and door_ok,
                }

                status["ready_for_callback"] = (
                    left_pressed
                    and right_pressed
                    and clamp_ok
                    and chain_ok
                    and door_ok
                    and status["callback_configured"]
                )

            # Check monitoring task status
            if self._monitoring_task:
                if self._monitoring_task.done():
                    if self._monitoring_task.exception():
                        status["task_status"] = f"failed: {self._monitoring_task.exception()}"
                    else:
                        status["task_status"] = "completed"
                else:
                    status["task_status"] = "running"
            else:
                status["task_status"] = "not_created"

        except Exception as e:
            status["status_error"] = str(e)
            logger.error(f"❌ VERIFICATION_TOOL: Error gathering status: {e}")

        logger.info("✅ VERIFICATION_TOOL: Detailed status gathered successfully")
        return status

    async def print_verification_report(self) -> None:
        """
        Print a comprehensive verification report to the logs
        """
        logger.info("📋 VERIFICATION_REPORT: Starting comprehensive verification report...")
        logger.info("=" * 80)
        logger.info("🔍 DIOMonitoringService Verification Report")
        logger.info("=" * 80)

        status = await self.get_detailed_status()

        # Service Status
        logger.info("📊 SERVICE STATUS:")
        logger.info(f"  - Monitoring Active: {status['monitoring_active']}")
        logger.info(f"  - Digital I/O Connected: {status['digital_io_connected']}")
        logger.info(f"  - Task Status: {status['task_status']}")
        logger.info(f"  - Callback Configured: {status['callback_configured']}")
        logger.info(f"  - Emergency Callback Configured: {status['emergency_callback_configured']}")

        # Timing Parameters
        logger.info("⏱️  TIMING PARAMETERS:")
        logger.info(f"  - Polling Interval: {status['polling_interval']}s")
        logger.info(f"  - Debounce Time: {status['debounce_time']}s")

        # Channel Configuration
        if "channel_config" in status:
            logger.info("🔧 CHANNEL CONFIGURATION:")
            for channel, config in status["channel_config"].items():
                logger.info(
                    f"  - Channel {channel}: {config['pin_name']} "
                    f"(pin {config['pin_number']}, {config['contact_type']}-contact, "
                    f"{config['edge_type']} edge) -> "
                    f"Raw: {config['raw_state']}, Logical: {config['logical_state']}"
                )

        # Button States
        if "dual_button_condition" in status:
            logger.info("🎯 BUTTON STATES:")
            dual = status["dual_button_condition"]
            logger.info(f"  - Left Button Pressed: {dual['left_pressed']}")
            logger.info(f"  - Right Button Pressed: {dual['right_pressed']}")
            logger.info(f"  - Dual Press Detected: {dual['both_pressed']}")

        # Safety Conditions
        if "safety_conditions" in status:
            logger.info("🔒 SAFETY CONDITIONS:")
            safety = status["safety_conditions"]
            logger.info(f"  - Clamp Sensor OK: {safety['clamp_ok']}")
            logger.info(f"  - Chain Sensor OK: {safety['chain_ok']}")
            logger.info(f"  - Door Sensor OK: {safety['door_ok']}")
            logger.info(f"  - All Safety Conditions Met: {safety['all_satisfied']}")

        # Overall Readiness
        if "ready_for_callback" in status:
            logger.info("🚀 CALLBACK READINESS:")
            logger.info(f"  - Ready for Callback Execution: {status['ready_for_callback']}")

        # Errors
        if "status_error" in status:
            logger.error(f"❌ STATUS ERROR: {status['status_error']}")

        logger.info("=" * 80)
        logger.info("📋 VERIFICATION_REPORT: Report completed")
        logger.info("=" * 80)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_monitoring()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        _ = exc_type, exc_val, exc_tb  # Unused parameters
        await self.stop_monitoring()
