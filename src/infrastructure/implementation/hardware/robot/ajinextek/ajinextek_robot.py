"""
AJINEXTEK Robot Service

Integrated service for AJINEXTEK robot hardware control.
Implements the RobotService interface using AXL library.
"""

# Standard library imports
from pathlib import Path
import time
from typing import Any, Dict

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
# 절대 import 사용 (권장)
# src가 Python path에 있을 때 최적의 방법
from application.interfaces.hardware.robot import (
    RobotService,
)
from domain.enums.robot_enums import MotionStatus
from domain.exceptions.hardware_exceptions import (
    HardwareException,
)
from domain.exceptions.robot_exceptions import (
    RobotConnectionError,
    RobotMotionError,
)
from infrastructure.implementation.hardware.robot.ajinextek.constants import (
    HOME_ERR_AMP_FAULT,
    HOME_ERR_GNT_RANGE,
    HOME_ERR_NEG_LIMIT,
    HOME_ERR_NOT_DETECT,
    HOME_ERR_POS_LIMIT,
    HOME_ERR_UNKNOWN,
    HOME_ERR_USER_BREAK,
    HOME_ERR_VELOCITY,
    HOME_SEARCHING,
    HOME_SUCCESS,
    POS_ABS,
    POS_REL,
    SERVO_OFF,
    SERVO_ON,
)
from infrastructure.implementation.hardware.robot.ajinextek.error_codes import (
    AXT_RT_SUCCESS,
    get_error_message,
)


class AjinextekRobot(RobotService):
    """AJINEXTEK 로봇 통합 서비스"""

    SERVICE_NAME = "AjinextekRobot"

    def __init__(self, axis_id: int, irq_no: int):
        """
        초기화

        Args:
            axis_id: Axis ID number
            irq_no: IRQ number for connection
        """

        # Connection parameters
        self._axis_id = axis_id
        self._irq_no = irq_no

        # Library information
        self.version: str = "Unknown"

        # Runtime state
        self._is_connected = False
        self._axis_count = 0  # Will be detected during connection
        self._current_position: float = 0.0
        self._servo_state: bool = False
        self._motion_status = MotionStatus.IDLE
        self._error_message = None

        # Initialize AXL wrapper (싱글톤 인스턴스 사용)
        # Local application imports
        from infrastructure.implementation.hardware.robot.ajinextek.axl_wrapper import (
            AXLWrapper,
        )

        self._axl = AXLWrapper.get_instance()

        logger.info("AjinextekRobotAdapter initialized")

    async def connect(self) -> None:
        """
        하드웨어 연결

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            logger.info(
                f"Connecting to AJINEXTEK robot controller (IRQ: {self._irq_no}, Axis: {self._axis_id})"
            )

            # Verify DLL installation before attempting to load
            # Note: This verification can be skipped if DLL is properly installed
            # dll_info = verify_dll_installation()
            # if not dll_info["dll_exists"]:
            #     logger.error("AXL DLL not found - printing diagnostic information")
            #     print_dll_diagnostic_info()
            #     raise RobotConnectionError(
            #         "AXL DLL not found at expected location",
            #         "AJINEXTEK",
            #         details=f"DLL path: {dll_info['dll_path']}, Available DLLs: {dll_info['available_dlls']}",
            #     )

            # 중앙화된 연결 관리 사용 (서비스 이름으로 추적)
            self._axl.connect(self._irq_no, service_name=self.SERVICE_NAME)

            # Get board count for verification (with error handling)
            try:
                board_count = self._axl.get_board_count()
                logger.info(f"Board count detected: {board_count}")
            except Exception as e:
                logger.warning(f"Could not get board count: {e} (continuing anyway)")
                board_count = 0  # Default value

            # Get axis count from hardware (with error handling)
            try:
                self._axis_count = self._axl.get_axis_count()
                logger.info(f"Detected axis count: {self._axis_count}")
            except Exception as e:
                logger.warning(f"Could not get axis count: {e} (using default: 1)")
                self._axis_count = 1  # Default to single axis

            # Get library version for info
            try:
                self.version = self._axl.get_lib_version()
                logger.info(f"AXL Library version: {self.version}")
            except Exception:
                pass  # Library version is not critical

            # Initialize position tracking and servo state for single axis
            self._current_position = 0.0
            self._servo_state = False

            # Software limits are now managed by robot controller via .mot file

            # Load robot parameters from configuration file for this axis
            await self._load_robot_parameters(self._axis_id)

            # Motion parameters are now loaded from .prm file via AxmMotLoadParaAll
            logger.info("Motion parameters initialized from .prm file")

            self._is_connected = True
            self._motion_status = MotionStatus.IDLE

            logger.info(
                f"AJINEXTEK robot controller connected successfully (IRQ: {self._irq_no}, Axis: {self._axis_id}, Total Axes: {self._axis_count})"
            )

        except Exception as e:
            self._is_connected = False
            if isinstance(e, RobotConnectionError):
                # Re-raise RobotConnectionError as-is to preserve error context
                raise
            else:
                logger.error(f"Failed to connect to AJINEXTEK robot: {e}")
                raise RobotConnectionError(
                    f"Robot controller initialization failed: {e}",
                    "AJINEXTEK",
                    details=str(e),
                ) from e

    async def disconnect(self) -> None:
        """
        하드웨어 연결 해제 with guaranteed cleanup

        Note:
            Always completes cleanup even if errors occur to prevent resource leaks
        """
        disconnect_error = None

        try:
            if self._is_connected:
                try:
                    # 중앙화된 연결 해제 사용 (서비스 이름으로 추적)
                    self._axl.disconnect(service_name=self.SERVICE_NAME)
                    logger.debug("Ajinextek robot AXL disconnect completed")
                except Exception as axl_error:
                    disconnect_error = axl_error
                    logger.warning(f"Error during Ajinextek robot AXL disconnect: {axl_error}")
                    # Continue with cleanup even if AXL disconnect fails

        except Exception as e:
            logger.error(f"Unexpected error disconnecting Ajinextek robot: {e}")
            disconnect_error = e

        finally:
            # Always perform cleanup to prevent resource leaks
            self._is_connected = False
            self._servo_state = False
            self._motion_status = MotionStatus.IDLE

            if disconnect_error:
                logger.warning(f"Ajinextek robot disconnected with errors: {disconnect_error}")
            else:
                logger.info("Ajinextek robot controller disconnected successfully")

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    async def home_axis(self, axis: int) -> None:
        """
        Home specified axis using parameters from robot_motion_settings.mot file

        All homing parameters (ORIGINMODE, ORIGINDIR, ORIGINLEVEL, ORIGINOFFSET,
        ORIGINVEL1, ORIGINVEL2) are already configured in the robot controller
        via AxmMotLoadParaAll from the robot_motion_settings.mot parameter file.

        Args:
            axis: Axis number (0-based)

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If homing fails
            RobotValidationError: If axis parameters are invalid
        """
        # Ensure robot is connected
        self._ensure_connected()

        # Ensure servo is enabled
        self._ensure_servo_enabled()

        try:
            logger.info(
                f"Starting homing for axis {axis} using robot_motion_settings.mot parameters"
            )
            self._motion_status = MotionStatus.HOMING

            # Start homing using parameters already loaded from robot_motion_settings.mot file
            result = self._axl.home_set_start(axis)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to start homing for axis {axis}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to start homing for axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )

            logger.debug(
                f"Started homing for axis {axis} using robot_motion_settings.mot parameters"
            )

            # Monitor homing status using AJINEXTEK standard pattern
            loop_count = 0
            while True:
                try:
                    home_result = self._axl.home_get_result(axis)
                    loop_count += 1

                    # Log every 10 iterations to avoid log spam
                    if loop_count % 10 == 1:
                        logger.info(
                            f"Homing axis {axis}: home_get_result = 0x{home_result:02X} (loop {loop_count})"
                        )

                    if home_result == HOME_SUCCESS:
                        logger.info(f"Homing completed successfully for axis {axis}")
                        break

                    elif home_result == HOME_SEARCHING:
                        # Get progress information for logging
                        try:
                            _, step = self._axl.home_get_rate(axis)
                            if loop_count % 10 == 1:
                                logger.info(f"Homing axis {axis}: {step}% complete")
                        except Exception:
                            pass  # Progress info is optional

                        # Continue monitoring
                        await asyncio.sleep(0.1)
                        continue

                    # Handle homing errors
                    error_messages = {
                        HOME_ERR_UNKNOWN: "Unknown axis number",
                        HOME_ERR_GNT_RANGE: "Gantry offset out of range",
                        HOME_ERR_USER_BREAK: "User stopped homing",
                        HOME_ERR_VELOCITY: "Invalid velocity setting",
                        HOME_ERR_AMP_FAULT: "Servo amplifier alarm",
                        HOME_ERR_NEG_LIMIT: "Negative limit sensor detected",
                        HOME_ERR_POS_LIMIT: "Positive limit sensor detected",
                        HOME_ERR_NOT_DETECT: "Home sensor not detected",
                    }

                    error_msg = error_messages.get(
                        home_result, f"Unknown homing error: 0x{home_result:02X}"
                    )
                    logger.error(
                        "Homing failed for axis %s: %s (0x%02X)",
                        axis,
                        error_msg,
                        home_result,
                    )
                    raise RobotMotionError(
                        f"Homing failed for axis {axis}: {error_msg}",
                        "AJINEXTEK",
                    )

                except Exception as status_error:
                    if isinstance(status_error, RobotMotionError):
                        raise
                    logger.error(f"Failed to check homing status for axis {axis}: {status_error}")
                    raise RobotMotionError(
                        f"Failed to check homing status for axis {axis}: {status_error}",
                        "AJINEXTEK",
                    ) from status_error

            # Update position to zero after successful homing
            self._current_position = 0.0
            self._motion_status = MotionStatus.IDLE
            logger.info(f"Axis {axis} homing completed successfully")

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            self._motion_status = MotionStatus.ERROR
            raise
        except Exception as e:
            logger.error(f"Homing failed on axis {axis}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Homing failed on axis {axis}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    # home_all_axes method removed - use individual home_axis() for each axis in separate threads

    async def move_absolute(
        self,
        position: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        지정된 축을 절대 위치로 이동

        Args:
            position: 절대 위치 (mm)
            axis_id: Axis ID number
            velocity: Motion velocity
            acceleration: Motion acceleration
            deceleration: Motion deceleration

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If movement fails
            RobotValidationError: If axis parameters are invalid
        """
        # Ensure robot is connected
        self._ensure_connected()

        # Ensure servo is enabled
        self._ensure_servo_enabled()

        # Use parameters directly
        vel = velocity
        accel = acceleration
        decel = deceleration

        try:
            logger.info(f"Moving axis {axis_id} to absolute position: {position}mm at {vel}mm/s")

            self._motion_status = MotionStatus.MOVING

            # Set absolute positioning mode
            self._set_absolute_mode(axis_id)

            # Start absolute position move
            result = self._axl.move_start_pos(axis_id, position, vel, accel, decel)

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error(f"Failed to start movement on axis {axis_id}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to start movement on axis {axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

            # Wait for motion to complete
            await self._wait_for_motion_complete(axis_id, timeout=30.0)

            # Update current position for this axis
            self._current_position = position

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Axis {axis_id} absolute move completed successfully")

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Absolute move failed on axis {axis_id}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Absolute move failed on axis {axis_id}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def move_relative(
        self,
        distance: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        Move axis by relative distance (interface implementation)

        Args:
            distance: Distance to move in mm
            axis_id: Axis ID number
            velocity: Motion velocity
            acceleration: Motion acceleration
            deceleration: Motion deceleration

        Raises:
            HardwareOperationError: If movement fails
            RobotValidationError: If axis parameters are invalid
        """
        # Ensure robot is connected
        self._ensure_connected()

        # Ensure servo is enabled
        self._ensure_servo_enabled()

        # Use parameters directly
        vel = velocity
        accel = acceleration
        decel = deceleration

        try:
            logger.info(f"Moving axis {axis_id} by relative distance: {distance}mm at {vel}mm/s")

            self._motion_status = MotionStatus.MOVING

            # Set relative positioning mode
            self._set_relative_mode(axis_id)

            # Start relative position move (distance, not absolute position)
            result = self._axl.move_start_pos(axis_id, distance, vel, accel, decel)

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error(f"Failed to start relative movement on axis {axis_id}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to start relative movement on axis {axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

            # Wait for motion to complete
            await self._wait_for_motion_complete(axis_id, timeout=30.0)

            # Update current position cache
            new_position = await self.get_current_position(axis_id)
            self._current_position = new_position

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Axis {axis_id} relative move completed successfully")

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Relative move failed on axis {axis_id}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Relative move failed on axis {axis_id}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def get_current_position(self, axis: int) -> float:
        """
        지정된 축의 현재 위치 조회

        Args:
            axis: 축 번호 (0부터 시작) - must match this robot instance's axis_id

        Returns:
            현재 위치 (mm)

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or doesn't match this robot's axis_id
        """
        self._ensure_connected()

        try:
            position = self._axl.get_act_pos(axis)

            # Update cached position
            self._current_position = position

            return position

        except Exception as e:
            logger.warning(f"Failed to get position for axis {axis}: {e}")
            # Use cached position as fallback
            return self._current_position

    # get_all_positions method removed - use individual get_position() for each axis

    async def get_motion_status(self) -> MotionStatus:
        """
        모션 상태 조회

        Returns:
            현재 모션 상태
        """
        return self._motion_status

    async def stop_motion(self, axis_id: int, deceleration: float) -> None:
        """
        지정된 축의 모션 정지

        Args:
            axis_id: Axis ID number
            deceleration: Deceleration value for stopping

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If stop operation fails
            RobotValidationError: If axis parameters are invalid
        """
        # Ensure robot is connected
        self._ensure_connected()

        # Ensure servo is enabled
        self._ensure_servo_enabled()

        try:
            logger.info(f"Stopping motion on axis {axis_id} with deceleration {deceleration} mm/s²")

            result = self._axl.move_stop(axis_id, deceleration)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to stop axis {axis_id}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to stop axis {axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

            # Update motion status - only set to IDLE if all axes are stopped
            # For now, we'll assume this axis is stopped
            logger.info(f"Axis {axis_id} motion stopped successfully")

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Unexpected error stopping axis {axis_id}: {e}")
            raise RobotMotionError(
                f"Unexpected error stopping axis {axis_id}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def emergency_stop(self, axis: int) -> None:
        """
        Emergency stop motion immediately for specific axis

        Args:
            axis: Specific axis to stop - must match this robot instance's axis_id

        Raises:
            HardwareException: If emergency stop fails
            RobotValidationError: If axis parameters are invalid
        """

        self._ensure_connected()

        try:
            # Stop specific axis
            logger.info(f"EMERGENCY STOP activated for axis {axis}")

            # Use true emergency stop (immediate stop without deceleration)
            result = self._axl.move_emergency_stop(axis)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to emergency stop axis {axis}: {error_msg}")
                raise HardwareException(
                    "ajinextek_robot",
                    "emergency_stop",
                    {"axis": axis, "error": error_msg},
                )

            # Turn off servo for safety
            try:
                self._set_servo_off()
                self._servo_state = False
            except Exception as e:
                logger.warning(f"Failed to turn off servo {axis} during emergency stop: {e}")

            logger.info(f"Emergency stop completed for axis {axis}")

        except Exception as e:
            logger.error(f"Emergency stop failed for axis {axis}: {e}")
            raise HardwareException(
                "ajinextek_robot",
                "emergency_stop",
                {"error": f"Emergency stop failed for axis {axis}: {e}"},
            ) from e

    async def get_position(self, axis: int) -> float:
        """
        Get current position of axis

        Args:
            axis: Axis number - must match this robot instance's axis_id

        Returns:
            Current position in mm

        Raises:
            RobotValidationError: If axis parameters are invalid
        """

        return await self.get_current_position(axis)

    async def is_moving(self, axis: int) -> bool:
        """
        Check if axis is currently moving

        Args:
            axis: Axis to check - must match this robot instance's axis_id

        Returns:
            True if moving, False otherwise

        Raises:
            RobotValidationError: If axis parameters are invalid
        """
        self._ensure_connected()

        try:
            # Check actual hardware motion status
            is_moving = self._axl.read_in_motion(axis)
            logger.debug(f"Hardware motion check for axis {axis}: {is_moving}")
            return is_moving
        except Exception as e:
            logger.warning(f"Failed to read motion status for axis {axis}: {e}")
            # Fallback to internal status if hardware read fails
            return self._motion_status == MotionStatus.MOVING

    async def get_axis_count(self) -> int:
        """
        축 개수 조회

        Returns:
            축 개수
        """
        return self._axis_count

    async def check_servo_alarm(self, axis: int) -> bool:
        """
        Check servo alarm status for specified axis

        Args:
            axis: Axis number to check - must match this robot instance's axis_id

        Returns:
            True if alarm is active, False otherwise

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or doesn't match this robot's axis_id
        """
        self._ensure_connected()

        try:
            return self._axl.read_servo_alarm(axis)
        except Exception as e:
            logger.warning(f"Failed to read servo alarm for axis {axis}: {e}")
            return False  # Default to no alarm if read fails

    async def check_limit_sensors(self, axis: int) -> Dict[str, bool]:
        """
        Check limit sensor status for specified axis

        Args:
            axis: Axis number to check - must match this robot instance's axis_id

        Returns:
            Dictionary with 'positive_limit' and 'negative_limit' status

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or doesn't match this robot's axis_id
        """
        self._ensure_connected()

        try:
            pos_limit, neg_limit = self._axl.read_limit_status(axis)
            return {
                "positive_limit": pos_limit,
                "negative_limit": neg_limit,
            }
        except Exception as e:
            logger.warning(f"Failed to read limit sensors for axis {axis}: {e}")
            return {"positive_limit": False, "negative_limit": False}

    async def get_status(self, axis_id: int = 0) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Args:
            axis_id: 위치를 조회할 축 번호 (기본값: 0)

        Returns:
            상태 정보 딕셔너리
        """
        is_connected = await self.is_connected()

        status = {
            "connected": is_connected,
            "hardware_type": "AJINEXTEK",
            "motion_status": self._motion_status.value,
            "servo_state": self._servo_state,
            "servo_enabled": self._servo_state,  # API 호환성을 위한 필드 추가
            "is_moving": False,  # Will be updated below for connected hardware
            "is_homed": True,  # AJINEXTEK robot의 homed 상태 (실제 구현 시 조건 확인 필요)
        }

        if is_connected:
            status["axis_count"] = self._axis_count
            status["version"] = self.version

            # Check actual hardware motion status
            try:
                is_moving = await self.is_moving(axis_id)
                status["is_moving"] = is_moving
                logger.debug(f"Hardware motion status for axis {axis_id}: {is_moving}")
            except Exception as e:
                logger.warning(f"Failed to get motion status for axis {axis_id}: {e}")
                status["is_moving"] = self._motion_status == MotionStatus.MOVING

            # Position 정보도 추가 (실제 하드웨어에서 읽어오는 로직 필요)
            try:
                current_pos = await self.get_position(axis_id)
                status["position"] = current_pos
                status["current_position"] = current_pos
            except Exception as e:
                logger.warning(f"Failed to get current position for axis {axis_id}: {e}")
                status["position"] = 0.0
                status["current_position"] = 0.0

        return status

    async def get_load_ratio(self, axis: int, ratio_type: int = 0) -> float:
        """
        Get servo load ratio

        Args:
            axis: Axis number
            ratio_type: Monitor selection
                0x00 - Accumulated load ratio (default)
                0x01 - Regenerative load ratio
                0x02 - Reference Torque load ratio

        Returns:
            Load ratio in percentage

        Raises:
            HardwareOperationError: If read operation fails
        """
        self._ensure_connected()

        try:
            # Set load ratio monitoring type
            result = self._axl.status_set_read_servo_load_ratio(axis, ratio_type)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.warning(f"Load ratio monitoring not supported: {error_msg}")
                raise HardwareException(
                    "ajinextek_robot",
                    "get_load_ratio_set",
                    {
                        "axis": axis,
                        "ratio_type": ratio_type,
                        "error": f"Not supported: {error_msg}",
                    },
                )

            # Read load ratio
            load_ratio = self._axl.status_read_servo_load_ratio(axis)
            logger.debug(f"Load ratio (type {ratio_type}) for axis {axis}: {load_ratio}%")
            return load_ratio

        except Exception as e:
            # Check if it's an AXLError (function not available)
            error_str = str(e)
            if "not available" in error_str.lower():
                logger.warning(f"Load ratio feature not available: {e}")
                raise HardwareException(
                    "ajinextek_robot",
                    "get_load_ratio",
                    {
                        "axis": axis,
                        "ratio_type": ratio_type,
                        "error": "Feature not available in AXL version",
                    },
                ) from e
            else:
                logger.error(f"Failed to read load ratio for axis {axis}: {e}")
                raise HardwareException(
                    "ajinextek_robot",
                    "get_load_ratio",
                    {"axis": axis, "ratio_type": ratio_type, "error": str(e)},
                ) from e

    async def get_torque(self, axis: int) -> float:
        """
        Get current torque value

        Args:
            axis: Axis number

        Returns:
            Current torque value

        Raises:
            HardwareOperationError: If read operation fails
        """
        self._ensure_connected()

        try:
            # Read torque value
            torque = self._axl.status_read_torque(axis)
            logger.debug(f"Torque for axis {axis}: {torque}")
            return torque

        except Exception as e:
            # Check if it's an AXLError (function not available)
            error_str = str(e)
            if "not available" in error_str.lower():
                logger.warning(f"Torque reading feature not available: {e}")
                raise HardwareException(
                    "ajinextek_robot",
                    "get_torque",
                    {"axis": axis, "error": "Feature not available in AXL version"},
                ) from e
            else:
                logger.error(f"Failed to read torque for axis {axis}: {e}")
                raise HardwareException(
                    "ajinextek_robot",
                    "get_torque",
                    {"axis": axis, "error": str(e)},
                ) from e

    # === Helper Methods ===

    def _ensure_connected(self) -> None:
        """Ensure robot controller is connected"""
        if not self._is_connected:
            raise RobotConnectionError(
                "Robot controller not connected",
                "AJINEXTEK",
            )

    # Legacy method kept for compatibility
    async def _initialize_axl_library(self, irq_no: int, max_retries: int = 3) -> int:
        """Initialize AXL library with retry logic (legacy compatibility method)"""
        if self._axl.is_opened():
            return AXT_RT_SUCCESS
        return self._axl.open(irq_no)

    def _ensure_servo_enabled(self) -> None:
        """Ensure servo is enabled before motion operations"""
        if not self._servo_state:
            raise RobotMotionError(
                "Servo is not enabled - cannot perform motion operations. Call enable_servo() first.",
                "AJINEXTEK",
            )

    def _set_absolute_mode(self, axis: int) -> None:
        """Set axis to absolute positioning mode using AxmMotSetAbsRelMode

        Args:
            axis: Axis number to set to absolute mode

        Raises:
            RobotMotionError: If mode setting fails
        """
        try:
            result = self._axl.set_abs_rel_mode(axis, POS_ABS)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set absolute mode for axis {axis}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to set absolute mode for axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )
            logger.debug(f"Set axis {axis} to absolute positioning mode")
        except Exception as e:
            logger.error(f"Error setting absolute mode for axis {axis}: {e}")
            raise RobotMotionError(
                f"Error setting absolute mode for axis {axis}: {e}",
                "AJINEXTEK",
            ) from e

    def _set_relative_mode(self, axis: int) -> None:
        """Set axis to relative positioning mode using AxmMotSetAbsRelMode

        Args:
            axis: Axis number to set to relative mode

        Raises:
            RobotMotionError: If mode setting fails
        """
        try:
            result = self._axl.set_abs_rel_mode(axis, POS_REL)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set relative mode for axis {axis}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to set relative mode for axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )
            logger.debug(f"Set axis {axis} to relative positioning mode")
        except Exception as e:
            logger.error(f"Error setting relative mode for axis {axis}: {e}")
            raise RobotMotionError(
                f"Error setting relative mode for axis {axis}: {e}",
                "AJINEXTEK",
            ) from e

    def _set_servo_on(self) -> None:
        """Turn servo on for primary axis"""
        self._ensure_connected()

        try:
            # Use primary axis (default axis 0)
            primary_axis = 0
            result = self._axl.servo_on(primary_axis, SERVO_ON)
            if result == AXT_RT_SUCCESS:
                self._servo_state = True
                logger.debug(f"Servo {primary_axis} turned ON")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to turn on servo {primary_axis}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to turn on servo {primary_axis}: {error_msg}",
                    "AJINEXTEK",
                )

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to turn on servo {primary_axis}: {e}")
            raise RobotMotionError(
                f"Failed to turn on servo {primary_axis}: {e}",
                "AJINEXTEK",
            ) from e

    def _set_servo_off(self) -> None:
        """Turn servo off for primary axis"""
        self._ensure_connected()

        try:
            # Use primary axis (default axis 0)
            primary_axis = 0
            result = self._axl.servo_on(primary_axis, SERVO_OFF)
            if result == AXT_RT_SUCCESS:
                self._servo_state = False
                logger.debug(f"Servo {primary_axis} turned OFF")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to turn off servo {primary_axis}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to turn off servo {primary_axis}: {error_msg}",
                    "AJINEXTEK",
                )

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to turn off servo {primary_axis}: {e}")
            raise RobotMotionError(
                f"Failed to turn off servo {primary_axis}: {e}",
                "AJINEXTEK",
            ) from e

    async def enable_servo(self, axis: int) -> None:
        """
        Enable servo for specific axis

        This method enables servo motor for the specified axis only.
        Should be called before attempting motion operations on the axis.

        Args:
            axis: Axis number to enable servo for - must match this robot instance's axis_id

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If servo enable operation fails
            RobotValidationError: If axis parameters are invalid
        """
        self._ensure_connected()

        try:
            logger.info(f"⚙️ Enabling servo for axis {axis}")
            logger.debug(f"Current servo state (cached): {self._servo_state}")

            # Check servo alarm before enabling
            try:
                alarm_status = await self.check_servo_alarm(axis)
                if alarm_status:
                    logger.warning(
                        f"⚠️ Servo alarm is ACTIVE for axis {axis} - servo enable may fail. "
                        f"Consider calling reset_servo_alarm() first."
                    )
            except Exception as e:
                logger.debug(f"Could not check servo alarm before enable: {e}")

            # Always attempt servo enable (idempotent operation)
            # Don't skip based on cached state - hardware state is source of truth
            logger.debug(f"Calling AxmServoOn for axis {axis}")
            self._set_servo_on()

            # Verify servo is actually enabled by reading hardware state
            try:
                # Small delay for hardware to respond
                await asyncio.sleep(0.05)

                # Read actual servo state from hardware using wrapper method
                actual_servo_on = self._axl.is_servo_on(axis)
                logger.info(
                    f"Hardware servo state after enable: {'ON' if actual_servo_on else 'OFF'}"
                )

                if not actual_servo_on:
                    logger.error(
                        f"❌ Servo enable FAILED for axis {axis} - hardware reports servo is still OFF. "
                        f"Possible causes: servo alarm active, emergency stop flag not cleared, "
                        f"or hardware fault."
                    )
                    raise RobotMotionError(
                        f"Servo enable failed for axis {axis} - hardware verification shows servo is OFF",
                        "AJINEXTEK",
                    )
                else:
                    logger.info(f"✅ Servo enabled successfully for axis {axis}")

            except RobotMotionError:
                raise
            except Exception as e:
                logger.warning(f"Could not verify servo state after enable: {e}")
                # Continue anyway - servo might still be on

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to enable servo for axis {axis}: {e}")
            raise RobotMotionError(
                f"Failed to enable servo for axis {axis}: {e}",
                "AJINEXTEK",
            ) from e

    async def disable_servo(self, axis: int) -> None:
        """
        Disable servo for specific axis

        This method disables servo motor for the specified axis.
        Should be called during shutdown or emergency situations.

        Args:
            axis: Axis number to disable servo for - must match this robot instance's axis_id

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If servo disable operation fails
            RobotValidationError: If axis parameters are invalid
        """
        self._ensure_connected()

        try:
            logger.info(f"Disabling servo for axis {axis}")

            if self._servo_state:
                self._set_servo_off()
                logger.debug(f"Servo disabled for axis {axis}")
            else:
                logger.debug(f"Servo already disabled for axis {axis}")

        except Exception as e:
            logger.error(f"Failed to disable servo for axis {axis}: {e}")
            # Don't raise exception for disable failures during shutdown
            logger.warning(f"Servo disable failed for axis {axis}, continuing...")

    async def reset_servo_alarm(self, axis: int) -> None:
        """
        Reset servo alarm status (required after emergency stop).

        After emergency stop (AxmMoveEStop), the Ajinextek controller enters servo
        alarm state and servo cannot be re-enabled until alarm is reset. This method
        pulses the alarm reset signal to clear the alarm state.

        Args:
            axis: Axis number to reset alarm for

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If alarm reset operation fails
        """
        self._ensure_connected()

        try:
            logger.info(f"🔧 Resetting servo alarm for axis {axis} (emergency stop recovery)")

            # Check current alarm status before reset
            try:
                alarm_status_before = await self.check_servo_alarm(axis)
                logger.info(
                    f"Servo alarm status BEFORE reset: {'ACTIVE' if alarm_status_before else 'CLEAR'}"
                )
            except Exception as e:
                logger.warning(f"Could not read alarm status before reset: {e}")
                alarm_status_before = None

            # Force servo state to False since emergency stop turned it off
            logger.debug(f"Forcing servo state to False for axis {axis}")
            self._servo_state = False

            # Pulse reset signal: ON → wait → OFF
            logger.debug(f"Sending alarm reset pulse ON for axis {axis}")
            result = self._axl.servo_alarm_reset(axis, 1)  # ON
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to reset servo alarm (ON) for axis {axis}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to reset servo alarm (ON) for axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )

            # Hold reset signal for 200ms (increased from 50ms for hardware stability)
            logger.debug(f"Holding alarm reset pulse for 200ms")
            await asyncio.sleep(0.2)

            logger.debug(f"Sending alarm reset pulse OFF for axis {axis}")
            result = self._axl.servo_alarm_reset(axis, 0)  # OFF
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to reset servo alarm (OFF) for axis {axis}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to reset servo alarm (OFF) for axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )

            # Wait for hardware to stabilize after alarm reset (critical for servo enable)
            logger.debug(f"Waiting 100ms for hardware stabilization after alarm reset")
            await asyncio.sleep(0.1)

            # Verify alarm was cleared
            try:
                alarm_status_after = await self.check_servo_alarm(axis)
                logger.info(
                    f"Servo alarm status AFTER reset: {'ACTIVE' if alarm_status_after else 'CLEAR'}"
                )
                if alarm_status_after:
                    logger.warning(
                        f"⚠️ Servo alarm still ACTIVE after reset for axis {axis} - servo may not enable properly"
                    )
            except Exception as e:
                logger.warning(f"Could not verify alarm status after reset: {e}")

            logger.info(f"✅ Servo alarm reset completed for axis {axis}")

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to reset servo alarm for axis {axis}: {e}")
            raise RobotMotionError(
                f"Failed to reset servo alarm for axis {axis}: {e}",
                "AJINEXTEK",
            ) from e

    async def _wait_for_motion_complete(self, axis: int, timeout: float = 30.0) -> None:
        """
        Wait for specified axis to stop moving

        Args:
            axis: Axis number to wait for
            timeout: Maximum wait time in seconds

        Raises:
            RobotMotionError: If axis doesn't stop within timeout or status check fails
        """
        self._ensure_connected()

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                is_moving = self._axl.read_in_motion(axis)
                if not is_moving:
                    logger.debug(f"Axis {axis} stopped successfully")
                    return
            except Exception as e:
                logger.error(f"Failed to check motion status for axis {axis}: {e}")
                raise RobotMotionError(
                    f"Failed to check motion status for axis {axis}: {e}",
                    "AJINEXTEK",
                ) from e

            await asyncio.sleep(0.01)  # Check every 10ms

        logger.warning(f"Timeout waiting for axis {axis} to stop")
        raise RobotMotionError(
            f"Timeout waiting for axis {axis} to stop after {timeout} seconds",
            "AJINEXTEK",
        )

    async def _load_robot_parameters(self, axis_id: int) -> None:
        """
        Load robot parameters from AJINEXTEK standard parameter file using AxmMotLoadPara

        Args:
            axis_id: Axis number to load parameters for (this robot's assigned axis)

        Raises:
            RobotConnectionError: If parameter loading fails
        """
        try:
            # Use absolute path to ensure file is found regardless of working directory
            project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
            robot_motion_settings_file = (
                project_root / "configuration" / "robot_motion_settings.mot"
            )

            if not robot_motion_settings_file.exists():
                logger.error(f"Robot motion settings file not found: {robot_motion_settings_file}")
                raise RobotConnectionError(
                    f"Required robot motion settings file not found: {robot_motion_settings_file}",
                    "AJINEXTEK",
                    details=f"Motion settings file path: {robot_motion_settings_file}",
                )

            logger.info(
                f"Loading robot motion settings from {robot_motion_settings_file} using AxmMotLoadParaAll"
            )

            # Load parameters for all axes using AJINEXTEK standard function
            result = self._axl.load_para_all(str(robot_motion_settings_file))

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(
                    f"Failed to load motion settings from {robot_motion_settings_file}: {error_msg}"
                )
                raise RobotConnectionError(
                    f"AxmMotLoadParaAll failed: {error_msg}",
                    "AJINEXTEK",
                    details=f"File: {robot_motion_settings_file}, Error: {result}",
                )

            logger.info(
                f"Robot motion settings loaded successfully from {robot_motion_settings_file} for all axes"
            )

        except RobotConnectionError:
            # Re-raise connection errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Failed to load robot parameters: {e}")
            raise RobotConnectionError(
                f"Robot parameters loading failed: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e
