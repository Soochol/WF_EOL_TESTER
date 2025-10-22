"""
Tower Lamp Service

Industrial tower lamp control service for status indication.
Provides standardized lamp patterns for different system states.
"""

# Standard library imports
# Standard library imports
from enum import Enum
import threading
from typing import Optional, TYPE_CHECKING

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from domain.value_objects.hardware_config import HardwareConfig


if TYPE_CHECKING:
    # Local application imports
    from application.interfaces.hardware.digital_io import DigitalIOService


class LampState(Enum):
    """Tower lamp states"""

    OFF = "off"
    ON = "on"
    BLINKING_SLOW = "blinking_slow"  # 0.5Hz (2초 주기: ON 1초 + OFF 1초)
    BLINKING_FAST = "blinking_fast"  # 2Hz (0.5초 주기: ON 0.25초 + OFF 0.25초)


class SystemStatus(Enum):
    """System status indicators - Simplified tower lamp control"""

    # Basic states
    SYSTEM_IDLE = "system_idle"  # 🟢 Green ON - 프로그램 시작/대기
    SYSTEM_RUNNING = "system_running"  # 🟢 Green ON - 테스트 실행 중

    # Test completion states (manual transition only - no auto-transition)
    TEST_PASS = "test_pass"  # 🟢 Green BLINK (2s) - 테스트 통과
    TEST_FAIL = "test_fail"  # 🟡 Yellow BLINK (2s) + 🟢 Green ON - 테스트 실패

    # Error states (2-stage: BLINK → CLEARED, then START TEST clears all)
    SYSTEM_ERROR = "system_error"  # 🔴 Red BLINK (2s) + 🟢 Green ON (no beep)
    TEST_ERROR_CLEARED = "test_error_cleared"  # 🔴 Red ON + 🟢 Green ON (no beep)

    # Emergency stop states (2-stage: BLINK → CLEARED, then HOME required)
    EMERGENCY_STOP = "emergency_stop"  # 🔴 Red BLINK (2s) + 🟢 Green ON + Beep
    EMERGENCY_CLEARED = "emergency_cleared"  # 🔴 Red ON + 🟢 Green ON (no beep)

    # Safety states (kept for compatibility)
    SAFETY_VIOLATION = "safety_violation"  # 🟡 Yellow BLINK (2s) + 🟢 Green ON (no beep)
    SAFETY_CLEARED = "safety_cleared"  # 🟡 Yellow ON + 🟢 Green ON (no beep)


class TowerLampService:
    """
    Tower Lamp Control Service

    Controls industrial tower lamp (Red/Yellow/Green) and beep for system status indication.
    Follows industrial automation standards for lamp patterns and meanings.
    """

    def __init__(
        self,
        digital_io_service: "DigitalIOService",
        hardware_config: HardwareConfig,
    ):
        """
        Initialize Tower Lamp Service with dedicated event loop thread

        Args:
            digital_io_service: Digital I/O service for lamp control
            hardware_config: Hardware configuration containing lamp channel assignments
        """
        self.digital_io = digital_io_service
        self.hardware_config = hardware_config

        # Get lamp channel assignments from hardware config
        self.red_lamp_channel = hardware_config.digital_io.tower_lamp_red
        self.yellow_lamp_channel = hardware_config.digital_io.tower_lamp_yellow
        self.green_lamp_channel = hardware_config.digital_io.tower_lamp_green
        self.beep_channel = hardware_config.digital_io.beep

        # Current lamp states tracking
        self._red_state = LampState.OFF
        self._yellow_state = LampState.OFF
        self._green_state = LampState.OFF
        self._beep_active = False

        # Blinking control
        self._blinking_tasks = {}
        self._current_system_status: Optional[SystemStatus] = None

        # Dedicated event loop for persistent blinking tasks
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._start_dedicated_event_loop()

        logger.info(
            f"🚦 TOWER_LAMP: Tower Lamp Service initialized - "
            f"Red: Ch{self.red_lamp_channel}, Yellow: Ch{self.yellow_lamp_channel}, "
            f"Green: Ch{self.green_lamp_channel}, Beep: Ch{self.beep_channel}"
        )

    def _start_dedicated_event_loop(self) -> None:
        """Start dedicated event loop thread for blinking tasks"""

        def run_loop():
            """Run event loop in dedicated thread"""
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            logger.info("🚦 TOWER_LAMP: Dedicated event loop started")

            # Run until shutdown event is set
            try:
                self._event_loop.run_forever()
            finally:
                # Clean up pending tasks
                pending = asyncio.all_tasks(self._event_loop)
                for task in pending:
                    task.cancel()
                self._event_loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
                self._event_loop.close()
                logger.info("🚦 TOWER_LAMP: Dedicated event loop stopped")

        self._loop_thread = threading.Thread(
            target=run_loop, daemon=True, name="TowerLampEventLoop"
        )
        self._loop_thread.start()
        logger.info("🚦 TOWER_LAMP: Event loop thread started")

    def _is_event_loop_available(self) -> bool:
        """
        Check if dedicated event loop is available and running

        Returns:
            True if event loop is available and not closed, False otherwise
        """
        return self._event_loop is not None and not self._event_loop.is_closed()

    async def set_system_status(self, status: SystemStatus) -> None:
        """
        Set system status with appropriate lamp pattern

        Args:
            status: System status to display
        """
        logger.info(f"🚦 TOWER_LAMP: Setting system status to {status.value}")

        # Stop current status if different
        if self._current_system_status != status:
            await self._stop_current_status()
            self._current_system_status = status

        # Apply status-specific lamp pattern
        if status == SystemStatus.SYSTEM_IDLE:
            await self._set_system_idle()
        elif status == SystemStatus.SYSTEM_RUNNING:
            await self._set_system_running()
        elif status == SystemStatus.TEST_PASS:
            await self._set_test_pass()
        elif status == SystemStatus.TEST_FAIL:
            await self._set_test_fail()
        elif status == SystemStatus.SYSTEM_ERROR:
            await self._set_system_error()
        elif status == SystemStatus.TEST_ERROR_CLEARED:
            await self._set_test_error_cleared()
        elif status == SystemStatus.EMERGENCY_STOP:
            await self._set_emergency_stop()
        elif status == SystemStatus.EMERGENCY_CLEARED:
            await self._set_emergency_cleared()
        elif status == SystemStatus.SAFETY_VIOLATION:
            await self._set_safety_violation()
        elif status == SystemStatus.SAFETY_CLEARED:
            await self._set_safety_cleared()

    async def _set_system_idle(self) -> None:
        """🟢 Green ON - 프로그램 시작/대기 상태"""
        logger.info("🟢 TOWER_LAMP: System idle - Green lamp ON")
        await self._set_lamp_state(red=LampState.OFF, yellow=LampState.OFF, green=LampState.ON)
        await self._set_beep(False)

    async def _set_system_running(self) -> None:
        """🟢 Green ON - 테스트 실행 중 (점멸 아님)"""
        logger.info("🟢 TOWER_LAMP: System running - Green lamp ON")
        await self._set_lamp_state(red=LampState.OFF, yellow=LampState.OFF, green=LampState.ON)
        await self._set_beep(False)

    async def _set_test_pass(self) -> None:
        """🟢 Green BLINK (2s) - 테스트 통과 + Beep 1초"""
        logger.info("✅ TOWER_LAMP: Test PASS - Green lamp BLINKING (2s cycle) + Beep 1s")
        await self._set_lamp_state(
            red=LampState.OFF, yellow=LampState.OFF, green=LampState.BLINKING_SLOW
        )
        # Beep for 1 second only
        await self._set_beep(True)
        await asyncio.sleep(1.0)
        await self._set_beep(False)
        logger.debug("🔔 TOWER_LAMP: Test PASS beep completed (1s)")
        # No auto-transition - user must press START TEST to clear

    async def _set_test_fail(self) -> None:
        """🟡 Yellow BLINK (2s) + 🟢 Green ON - 테스트 실패 + Beep 1초"""
        logger.info("❌ TOWER_LAMP: Test FAIL - Yellow lamp BLINKING (2s) + Green ON + Beep 1s")
        await self._set_lamp_state(
            red=LampState.OFF, yellow=LampState.BLINKING_SLOW, green=LampState.ON
        )
        # Beep for 1 second only
        await self._set_beep(True)
        await asyncio.sleep(1.0)
        await self._set_beep(False)
        logger.debug("🔔 TOWER_LAMP: Test FAIL beep completed (1s)")
        # No auto-transition - user must press START TEST to clear

    async def _set_system_error(self) -> None:
        """🔴 Red BLINK (2s) + 🟢 Green ON (no beep) - 테스트 에러"""
        logger.error("🔴 TOWER_LAMP: System error - Red lamp BLINKING (2s) + Green ON (no beep)")
        await self._set_lamp_state(
            red=LampState.BLINKING_SLOW, yellow=LampState.OFF, green=LampState.ON
        )
        await self._set_beep(False)

    async def _set_test_error_cleared(self) -> None:
        """🔴 Red ON + 🟢 Green ON (no beep) - 에러 확인됨 (Clear Error 버튼)"""
        logger.info("🟠 TOWER_LAMP: Test error cleared - Red lamp ON + Green ON (no beep)")
        await self._set_lamp_state(red=LampState.ON, yellow=LampState.OFF, green=LampState.ON)
        await self._set_beep(False)

    async def _set_emergency_stop(self) -> None:
        """🔴 Red BLINK (2s) + 🟢 Green ON + Beep - 비상정지 (오직 이것만 beep)"""
        logger.critical("🚨 TOWER_LAMP: Emergency stop - Red lamp BLINKING (2s) + Green ON + Beep")
        await self._set_lamp_state(
            red=LampState.BLINKING_SLOW, yellow=LampState.OFF, green=LampState.ON
        )
        await self._set_beep(True)  # Only Emergency Stop has beep!

    async def _set_emergency_cleared(self) -> None:
        """🔴 Red ON + 🟢 Green ON (no beep) - 비상정지 확인됨 (Clear Error 버튼, HOME 필요)"""
        logger.info("🟠 TOWER_LAMP: Emergency cleared - Red lamp ON + Green ON (no beep)")
        await self._set_lamp_state(red=LampState.ON, yellow=LampState.OFF, green=LampState.ON)
        await self._set_beep(False)

    async def _set_safety_violation(self) -> None:
        """🟡 Yellow BLINK (2s) + 🟢 Green ON (no beep) - 안전 센서 위반"""
        logger.warning(
            "⚠️ TOWER_LAMP: Safety violation - Yellow lamp BLINKING (2s) + Green ON (no beep)"
        )
        await self._set_lamp_state(
            red=LampState.OFF, yellow=LampState.BLINKING_SLOW, green=LampState.ON
        )
        await self._set_beep(False)

    async def _set_safety_cleared(self) -> None:
        """🟡 Yellow ON + 🟢 Green ON (no beep) - 안전 확인됨"""
        logger.info("🟡 TOWER_LAMP: Safety cleared - Yellow lamp ON + Green ON (no beep)")
        await self._set_lamp_state(red=LampState.OFF, yellow=LampState.ON, green=LampState.ON)
        await self._set_beep(False)

    async def _set_lamp_state(
        self,
        red: LampState = LampState.OFF,
        yellow: LampState = LampState.OFF,
        green: LampState = LampState.OFF,
    ) -> None:
        """
        Set individual lamp states

        Args:
            red: Red lamp state
            yellow: Yellow lamp state
            green: Green lamp state
        """
        # Stop any existing blinking tasks
        await self._stop_all_blinking()

        # Update state tracking
        self._red_state = red
        self._yellow_state = yellow
        self._green_state = green

        # Set static states (ON/OFF)
        if red in [LampState.ON, LampState.OFF]:
            await self._set_lamp_output(self.red_lamp_channel, red == LampState.ON)
        if yellow in [LampState.ON, LampState.OFF]:
            await self._set_lamp_output(self.yellow_lamp_channel, yellow == LampState.ON)
        if green in [LampState.ON, LampState.OFF]:
            await self._set_lamp_output(self.green_lamp_channel, green == LampState.ON)

        # Check if event loop is available for blinking tasks
        if not self._is_event_loop_available():
            logger.warning("🚦 TOWER_LAMP: Event loop not available - using static lamp states")
            # Fallback to static states when blinking is requested but event loop unavailable
            fallback_red = red == LampState.ON or red in [
                LampState.BLINKING_SLOW,
                LampState.BLINKING_FAST,
            ]
            fallback_yellow = yellow == LampState.ON or yellow in [
                LampState.BLINKING_SLOW,
                LampState.BLINKING_FAST,
            ]
            fallback_green = green == LampState.ON or green in [
                LampState.BLINKING_SLOW,
                LampState.BLINKING_FAST,
            ]

            await self._set_lamp_output(self.red_lamp_channel, fallback_red)
            await self._set_lamp_output(self.yellow_lamp_channel, fallback_yellow)
            await self._set_lamp_output(self.green_lamp_channel, fallback_green)
            return

        # Start blinking tasks in dedicated event loop
        try:
            # Use dedicated event loop for persistent blinking
            loop = self._event_loop
            if loop is None or loop.is_closed():
                logger.error("🚦 TOWER_LAMP: Dedicated event loop not available!")
                return

            logger.debug(f"🚦 TOWER_LAMP: Creating tasks in dedicated loop: {id(loop)}")

            if red in [LampState.BLINKING_SLOW, LampState.BLINKING_FAST]:
                try:
                    # Submit task to dedicated event loop thread-safely
                    future = asyncio.run_coroutine_threadsafe(
                        self._blink_lamp(self.red_lamp_channel, red), loop
                    )
                    self._blinking_tasks["red"] = future
                    logger.debug("🚦 TOWER_LAMP: Created red blinking task in dedicated loop")
                except Exception as task_e:
                    logger.error(f"🚦 TOWER_LAMP: Failed to create red blinking task: {task_e}")
                    await self._set_lamp_output(self.red_lamp_channel, True)  # Fallback to ON

            if yellow in [LampState.BLINKING_SLOW, LampState.BLINKING_FAST]:
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        self._blink_lamp(self.yellow_lamp_channel, yellow), loop
                    )
                    self._blinking_tasks["yellow"] = future
                    logger.debug("🚦 TOWER_LAMP: Created yellow blinking task in dedicated loop")
                except Exception as task_e:
                    logger.error(f"🚦 TOWER_LAMP: Failed to create yellow blinking task: {task_e}")
                    await self._set_lamp_output(self.yellow_lamp_channel, True)  # Fallback to ON

            if green in [LampState.BLINKING_SLOW, LampState.BLINKING_FAST]:
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        self._blink_lamp(self.green_lamp_channel, green), loop
                    )
                    self._blinking_tasks["green"] = future
                    logger.debug("🚦 TOWER_LAMP: Created green blinking task in dedicated loop")
                except Exception as task_e:
                    logger.error(f"🚦 TOWER_LAMP: Failed to create green blinking task: {task_e}")
                    await self._set_lamp_output(self.green_lamp_channel, True)  # Fallback to ON

        except (RuntimeError, Exception) as e:
            logger.error(f"🚦 TOWER_LAMP: Event loop error during task creation: {e}")
            # If event loop becomes unavailable during operation, fall back to static states
            fallback_red = red == LampState.ON or red in [
                LampState.BLINKING_SLOW,
                LampState.BLINKING_FAST,
            ]
            fallback_yellow = yellow == LampState.ON or yellow in [
                LampState.BLINKING_SLOW,
                LampState.BLINKING_FAST,
            ]
            fallback_green = green == LampState.ON or green in [
                LampState.BLINKING_SLOW,
                LampState.BLINKING_FAST,
            ]

            await self._set_lamp_output(self.red_lamp_channel, fallback_red)
            await self._set_lamp_output(self.yellow_lamp_channel, fallback_yellow)
            await self._set_lamp_output(self.green_lamp_channel, fallback_green)

    async def _set_lamp_output(self, channel: int, state: bool) -> None:
        """
        Set lamp output state with robust error handling

        Args:
            channel: Digital output channel
            state: True for ON, False for OFF
        """
        try:
            # Check if event loop is available before attempting async operations
            if not self._is_event_loop_available():
                logger.warning(
                    f"🚦 TOWER_LAMP: Event loop not available - skipping lamp channel {channel}"
                )
                return

            if await self.digital_io.is_connected():
                await self.digital_io.write_output(channel, state)
                state_str = "ON" if state else "OFF"
                logger.debug(f"🚦 TOWER_LAMP: Channel {channel} set to {state_str}")
            else:
                logger.warning("🚦 TOWER_LAMP: Digital I/O not connected - lamp control skipped")

        except (RuntimeError, asyncio.InvalidStateError) as e:
            # Handle event loop specific errors
            logger.error(f"🚦 TOWER_LAMP: Event loop error setting lamp channel {channel}: {e}")
        except Exception as e:
            # Handle all other errors
            logger.error(f"🚦 TOWER_LAMP: Failed to set lamp channel {channel}: {e}")

    async def _blink_lamp(self, channel: int, blink_type: LampState) -> None:
        """
        Blink lamp with specified pattern

        Args:
            channel: Digital output channel
            blink_type: Blinking pattern (BLINKING_SLOW or BLINKING_FAST)
        """
        # BLINKING_SLOW: 2초 주기 (ON 1초 + OFF 1초)
        # BLINKING_FAST: 0.5초 주기 (ON 0.25초 + OFF 0.25초)
        interval = 2.0 if blink_type == LampState.BLINKING_SLOW else 0.5

        try:
            while True:
                # Check if task was cancelled before each operation
                current_task = asyncio.current_task()
                if current_task and current_task.cancelled():
                    break

                await self._set_lamp_output(channel, True)

                # Use asyncio.wait_for with timeout to make cancellation more responsive
                try:
                    await asyncio.wait_for(
                        asyncio.sleep(interval / 2), timeout=(interval / 2) + 0.1
                    )
                except asyncio.TimeoutError:
                    pass  # Normal timeout, continue

                current_task = asyncio.current_task()
                if current_task and current_task.cancelled():
                    break

                await self._set_lamp_output(channel, False)

                try:
                    await asyncio.wait_for(
                        asyncio.sleep(interval / 2), timeout=(interval / 2) + 0.1
                    )
                except asyncio.TimeoutError:
                    pass  # Normal timeout, continue

        except asyncio.CancelledError:
            # Task was cancelled (usually due to event loop shutdown)
            # GREEN lamp must ALWAYS stay ON, RED/YELLOW turn OFF
            logger.debug(f"🚦 TOWER_LAMP: Blinking task for channel {channel} cancelled")
            try:
                if channel == self.green_lamp_channel:
                    # GREEN must always stay ON
                    await self._set_lamp_output(channel, True)
                    logger.debug(f"🚦 TOWER_LAMP: GREEN lamp kept ON after cancel")
                else:
                    # RED/YELLOW turn OFF when cancelled
                    await self._set_lamp_output(channel, False)
            except Exception as e:
                logger.debug(f"🚦 TOWER_LAMP: Error setting lamp state on cancel: {e}")
        except Exception as e:
            logger.error(f"🚦 TOWER_LAMP: Error in blink_lamp for channel {channel}: {e}")
            # On error, turn off lamp for safety
            try:
                await self._set_lamp_output(channel, False)
            except Exception:
                pass

    async def _set_beep(self, beep_on: bool) -> None:
        """Set beep ON or OFF - hardware handles 1-second interval automatically"""
        try:
            logger.debug(
                f"🔊 TOWER_LAMP: Attempting to set beep to {'ON' if beep_on else 'OFF'}, channel {self.beep_channel}"
            )
            if await self.digital_io.is_connected():
                logger.debug(
                    f"🔊 TOWER_LAMP: Digital I/O is connected, writing to channel {self.beep_channel}"
                )
                await self.digital_io.write_output(self.beep_channel, beep_on)
                logger.debug(f"🔊 TOWER_LAMP: Beep set to {'ON' if beep_on else 'OFF'}")
            else:
                logger.warning("🔊 TOWER_LAMP: Digital I/O not connected - beep control skipped")
        except Exception as e:
            logger.error(f"🔊 TOWER_LAMP: Failed to set beep: {e}")

    async def _stop_all_blinking(self) -> None:
        """Stop all blinking tasks (Futures) safely without waiting for cancellation"""
        for color, future in list(self._blinking_tasks.items()):
            if not future.done():
                logger.debug(f"🚦 TOWER_LAMP: Cancelling {color} blinking future")
                future.cancel()
                # Future.cancel() returns True if cancellation was successful
            else:
                logger.debug(f"🚦 TOWER_LAMP: {color} blinking future already done")

        # Clear the tasks dictionary immediately
        self._blinking_tasks.clear()
        logger.debug("🚦 TOWER_LAMP: All blinking futures cancelled and cleared")

    async def _stop_current_status(self) -> None:
        """Stop current status indication (GREEN always stays ON)"""
        logger.debug(f"🚦 TOWER_LAMP: Stopping current status: {self._current_system_status}")

        # Stop all blinking tasks
        await self._stop_all_blinking()

        # Turn off RED, YELLOW, and BEEP only - GREEN stays ON!
        # GREEN lamp must ALWAYS be ON from program start to program exit
        try:
            if await self.digital_io.is_connected():
                await self.digital_io.write_output(self.red_lamp_channel, False)
                await self.digital_io.write_output(self.yellow_lamp_channel, False)
                # DO NOT turn off GREEN lamp - it must always stay ON!
                await self.digital_io.write_output(self.green_lamp_channel, True)  # Keep GREEN ON
                await self.digital_io.write_output(self.beep_channel, False)
        except Exception as e:
            logger.error(f"🚦 TOWER_LAMP: Failed to turn off lamps: {e}")

        # Reset state tracking (GREEN stays ON)
        self._red_state = LampState.OFF
        self._yellow_state = LampState.OFF
        self._green_state = LampState.ON  # GREEN always ON

    async def shutdown(self) -> None:
        """
        Gracefully shutdown the tower lamp service by stopping all tasks and turning off all lamps
        """
        logger.info("🚦 TOWER_LAMP: Shutting down service...")

        try:
            # Stop all current status and blinking
            await self._stop_current_status()

            # Wait a moment for tasks to finish
            await asyncio.sleep(0.1)

            # Force clear any remaining futures
            if self._blinking_tasks:
                logger.debug(
                    f"🚦 TOWER_LAMP: Force clearing {len(self._blinking_tasks)} remaining futures"
                )
                for color, future in list(self._blinking_tasks.items()):
                    if not future.done():
                        future.cancel()
                        logger.debug(f"🚦 TOWER_LAMP: Force cancelled {color} future")

                self._blinking_tasks.clear()

            # Stop dedicated event loop
            if self._event_loop and not self._event_loop.is_closed():
                logger.info("🚦 TOWER_LAMP: Stopping dedicated event loop...")
                self._event_loop.call_soon_threadsafe(self._event_loop.stop)
                if self._loop_thread and self._loop_thread.is_alive():
                    self._loop_thread.join(timeout=2.0)
                logger.info("🚦 TOWER_LAMP: Dedicated event loop stopped")

            logger.info("🚦 TOWER_LAMP: Service shutdown complete")

        except Exception as e:
            logger.error(f"🚦 TOWER_LAMP: Error during shutdown: {e}")
        self._beep_active = False

    async def turn_off_all(self) -> None:
        """Turn off all lamps and stop all patterns"""
        logger.info("🚦 TOWER_LAMP: Turning off all lamps")
        await self._stop_current_status()
        self._current_system_status = None

    async def get_current_status(self) -> Optional[SystemStatus]:
        """
        Get current system status

        Returns:
            Current system status or None if no status is set
        """
        return self._current_system_status

    async def get_lamp_states(self) -> dict:
        """
        Get current lamp states for diagnostics

        Returns:
            Dictionary containing current lamp states
        """
        return {
            "red_state": self._red_state.value,
            "yellow_state": self._yellow_state.value,
            "green_state": self._green_state.value,
            "beep_active": self._beep_active,
            "system_status": (
                self._current_system_status.value if self._current_system_status else None
            ),
            "active_tasks": list(self._blinking_tasks.keys()),
            "digital_io_connected": await self.digital_io.is_connected(),
        }

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup all tasks"""
        _ = exc_type, exc_val, exc_tb  # Unused parameters
        await self.turn_off_all()
