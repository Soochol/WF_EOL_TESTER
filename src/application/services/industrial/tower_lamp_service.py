"""
Tower Lamp Service

Industrial tower lamp control service for status indication.
Provides standardized lamp patterns for different system states.
"""

# Standard library imports
# Standard library imports
from enum import Enum
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
    BLINKING_SLOW = "blinking_slow"  # 1Hz (1초 간격)
    BLINKING_FAST = "blinking_fast"  # 2Hz (0.5초 간격)


class SystemStatus(Enum):
    """System status indicators"""

    SYSTEM_IDLE = "system_idle"  # 🟢 Green ON - 시스템 대기
    SYSTEM_INITIALIZING = "system_initializing"  # 🟢 Green BLINK - 초기화 중
    SYSTEM_RUNNING = "system_running"  # 🟢 Green BLINK - 테스트 실행 중
    SYSTEM_WARNING = "system_warning"  # 🟡 Yellow ON - 경고 상태
    SYSTEM_ATTENTION = "system_attention"  # 🟡 Yellow BLINK - 주의 필요
    SYSTEM_ERROR = "system_error"  # 🔴 Red ON - 에러 정지
    SYSTEM_EMERGENCY = "system_emergency"  # 🔴 Red BLINK - 비상 정지
    SAFETY_VIOLATION = "safety_violation"  # 🟡 Yellow BLINK + Beep - 안전센서


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
        Initialize Tower Lamp Service

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

        logger.info(
            f"🚦 TOWER_LAMP: Tower Lamp Service initialized - "
            f"Red: Ch{self.red_lamp_channel}, Yellow: Ch{self.yellow_lamp_channel}, "
            f"Green: Ch{self.green_lamp_channel}, Beep: Ch{self.beep_channel}"
        )

    def _is_event_loop_available(self) -> bool:
        """
        Check if an asyncio event loop is available and running

        Returns:
            True if event loop is available and not closed, False otherwise
        """
        try:
            loop = asyncio.get_running_loop()
            return loop is not None and not loop.is_closed()
        except RuntimeError:
            # No event loop is running
            return False
        except Exception as e:
            logger.debug(f"🚦 TOWER_LAMP: Event loop check failed: {e}")
            return False

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
        elif status == SystemStatus.SYSTEM_INITIALIZING:
            await self._set_system_initializing()
        elif status == SystemStatus.SYSTEM_RUNNING:
            await self._set_system_running()
        elif status == SystemStatus.SYSTEM_WARNING:
            await self._set_system_warning()
        elif status == SystemStatus.SYSTEM_ATTENTION:
            await self._set_system_attention()
        elif status == SystemStatus.SYSTEM_ERROR:
            await self._set_system_error()
        elif status == SystemStatus.SYSTEM_EMERGENCY:
            await self._set_system_emergency()
        elif status == SystemStatus.SAFETY_VIOLATION:
            await self._set_safety_violation()

    async def _set_system_idle(self) -> None:
        """🟢 Green ON - 시스템 대기 중"""
        logger.info("🟢 TOWER_LAMP: System idle - Green lamp ON")
        await self._set_lamp_state(red=LampState.OFF, yellow=LampState.OFF, green=LampState.ON)
        # Turn off beep for idle state
        await self._set_beep(False)

    async def _set_system_initializing(self) -> None:
        """🟢 Green BLINK - 시스템 초기화 중"""
        logger.info("🟢 TOWER_LAMP: System initializing - Green lamp BLINKING")
        await self._set_lamp_state(
            red=LampState.OFF, yellow=LampState.OFF, green=LampState.BLINKING_SLOW
        )
        # Turn off beep for initialization
        await self._set_beep(False)

    async def _set_system_running(self) -> None:
        """🟢 Green BLINK - 테스트 실행 중"""
        logger.info("🟢 TOWER_LAMP: System running - Green lamp BLINKING")
        await self._set_lamp_state(
            red=LampState.OFF, yellow=LampState.OFF, green=LampState.BLINKING_FAST
        )
        # Turn on beep for running indication
        await self._set_beep(True)

    async def _set_system_warning(self) -> None:
        """🟡 Yellow ON - 경고 상태 (일시정지/대기)"""
        logger.info("🟡 TOWER_LAMP: System warning - Yellow lamp ON")
        await self._set_lamp_state(red=LampState.OFF, yellow=LampState.ON, green=LampState.OFF)
        # Turn on beep for warning indication
        await self._set_beep(True)

    async def _set_system_attention(self) -> None:
        """🟡 Yellow BLINK - 주의 필요 상황"""
        logger.info("🟡 TOWER_LAMP: System attention - Yellow lamp BLINKING")
        await self._set_lamp_state(
            red=LampState.OFF, yellow=LampState.BLINKING_SLOW, green=LampState.OFF
        )
        # Turn on beep for attention indication
        await self._set_beep(True)

    async def _set_system_error(self) -> None:
        """🔴 Red ON - 에러로 인한 정지"""
        logger.info("🔴 TOWER_LAMP: System error - Red lamp ON")
        await self._set_lamp_state(red=LampState.ON, yellow=LampState.OFF, green=LampState.OFF)
        # Turn on beep for error indication
        await self._set_beep(True)

    async def _set_system_emergency(self) -> None:
        """🔴 Red BLINK + Continuous Beep - 비상 정지"""
        logger.critical("🚨 TOWER_LAMP: Emergency stop - Red lamp BLINKING + Continuous beep")
        await self._set_lamp_state(
            red=LampState.BLINKING_FAST, yellow=LampState.OFF, green=LampState.OFF
        )
        # Turn on beep for emergency indication
        await self._set_beep(True)

    async def _set_safety_violation(self) -> None:
        """🟡 Yellow BLINK + Beep - 안전센서 미만족"""
        logger.warning("⚠️ TOWER_LAMP: Safety violation - Yellow lamp BLINKING + Warning beep")
        await self._set_lamp_state(
            red=LampState.OFF, yellow=LampState.BLINKING_FAST, green=LampState.OFF
        )
        # Turn on beep for safety violation indication
        await self._set_beep(True)

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

        # Start blinking tasks with enhanced error handling
        try:
            # Get current event loop to ensure tasks are created in the correct loop
            loop = asyncio.get_running_loop()
            logger.debug(f"🚦 TOWER_LAMP: Creating tasks in event loop: {id(loop)}")

            if red in [LampState.BLINKING_SLOW, LampState.BLINKING_FAST]:
                try:
                    self._blinking_tasks["red"] = loop.create_task(
                        self._blink_lamp(self.red_lamp_channel, red)
                    )
                    logger.debug("🚦 TOWER_LAMP: Created red blinking task")
                except Exception as task_e:
                    logger.error(f"🚦 TOWER_LAMP: Failed to create red blinking task: {task_e}")
                    await self._set_lamp_output(self.red_lamp_channel, True)  # Fallback to ON

            if yellow in [LampState.BLINKING_SLOW, LampState.BLINKING_FAST]:
                try:
                    self._blinking_tasks["yellow"] = loop.create_task(
                        self._blink_lamp(self.yellow_lamp_channel, yellow)
                    )
                    logger.debug("🚦 TOWER_LAMP: Created yellow blinking task")
                except Exception as task_e:
                    logger.error(f"🚦 TOWER_LAMP: Failed to create yellow blinking task: {task_e}")
                    await self._set_lamp_output(self.yellow_lamp_channel, True)  # Fallback to ON

            if green in [LampState.BLINKING_SLOW, LampState.BLINKING_FAST]:
                try:
                    self._blinking_tasks["green"] = loop.create_task(
                        self._blink_lamp(self.green_lamp_channel, green)
                    )
                    logger.debug("🚦 TOWER_LAMP: Created green blinking task")
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
        interval = 1.0 if blink_type == LampState.BLINKING_SLOW else 0.5

        try:
            while True:
                # Check if task was cancelled before each operation
                current_task = asyncio.current_task()
                if current_task and current_task.cancelled():
                    break

                await self._set_lamp_output(channel, True)

                # Use asyncio.wait_for with timeout to make cancellation more responsive
                try:
                    await asyncio.wait_for(asyncio.sleep(interval), timeout=interval + 0.1)
                except asyncio.TimeoutError:
                    pass  # Normal timeout, continue

                current_task = asyncio.current_task()
                if current_task and current_task.cancelled():
                    break

                await self._set_lamp_output(channel, False)

                try:
                    await asyncio.wait_for(asyncio.sleep(interval), timeout=interval + 0.1)
                except asyncio.TimeoutError:
                    pass  # Normal timeout, continue

        except asyncio.CancelledError:
            # Task was cancelled, turn off the lamp and exit cleanly
            logger.debug(f"🚦 TOWER_LAMP: Blinking task for channel {channel} cancelled")
            try:
                await self._set_lamp_output(channel, False)
            except Exception as e:
                logger.debug(f"🚦 TOWER_LAMP: Error turning off lamp during cancellation: {e}")
            # Don't re-raise CancelledError to allow clean task destruction
        except Exception as e:
            logger.error(f"🚦 TOWER_LAMP: Error in blink_lamp for channel {channel}: {e}")
        finally:
            # Ensure lamp is off when task ends
            try:
                await self._set_lamp_output(channel, False)
                logger.debug(f"🚦 TOWER_LAMP: Blinking task for channel {channel} finished cleanly")
            except Exception as e:
                logger.debug(f"🚦 TOWER_LAMP: Error in finally block: {e}")

    async def _set_beep(self, beep_on: bool) -> None:
        """Set beep ON or OFF - hardware handles 1-second interval automatically"""
        try:
            if await self.digital_io.is_connected():
                await self.digital_io.write_output(self.beep_channel, beep_on)
                logger.debug(f"🔊 TOWER_LAMP: Beep set to {'ON' if beep_on else 'OFF'}")
        except Exception as e:
            logger.error(f"🔊 TOWER_LAMP: Failed to set beep: {e}")

    async def _stop_all_blinking(self) -> None:
        """Stop all blinking tasks safely without waiting for cancellation"""
        for color, task in list(self._blinking_tasks.items()):
            if not task.done():
                logger.debug(f"🚦 TOWER_LAMP: Cancelling {color} blinking task")
                task.cancel()
                # Don't await the task - just cancel and move on to avoid event loop issues
            else:
                logger.debug(f"🚦 TOWER_LAMP: {color} blinking task already done")

        # Clear the tasks dictionary immediately
        self._blinking_tasks.clear()
        logger.debug("🚦 TOWER_LAMP: All blinking tasks cancelled and cleared")

    async def _stop_current_status(self) -> None:
        """Stop current status indication"""
        logger.debug(f"🚦 TOWER_LAMP: Stopping current status: {self._current_system_status}")

        # Stop all blinking tasks
        await self._stop_all_blinking()

        # Turn off all lamps and beep
        try:
            if await self.digital_io.is_connected():
                await self.digital_io.write_output(self.red_lamp_channel, False)
                await self.digital_io.write_output(self.yellow_lamp_channel, False)
                await self.digital_io.write_output(self.green_lamp_channel, False)
                await self.digital_io.write_output(self.beep_channel, False)
        except Exception as e:
            logger.error(f"🚦 TOWER_LAMP: Failed to turn off lamps: {e}")

        # Reset state tracking
        self._red_state = LampState.OFF
        self._yellow_state = LampState.OFF
        self._green_state = LampState.OFF

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

            # Force clear any remaining tasks
            if self._blinking_tasks:
                logger.debug(
                    f"🚦 TOWER_LAMP: Force clearing {len(self._blinking_tasks)} remaining tasks"
                )
                for color, task in list(self._blinking_tasks.items()):
                    if not task.done():
                        task.cancel()
                        logger.debug(f"🚦 TOWER_LAMP: Force cancelled {color} task")

                self._blinking_tasks.clear()

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
