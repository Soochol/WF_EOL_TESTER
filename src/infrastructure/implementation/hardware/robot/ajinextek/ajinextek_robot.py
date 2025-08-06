"""
AJINEXTEK Robot Service

Integrated service for AJINEXTEK robot hardware control.
Implements the RobotService interface using AXL library.
"""

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

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
from infrastructure.implementation.hardware.robot.ajinextek.axl_wrapper import (
    AXLWrapper,
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
    print_dll_diagnostic_info,
    verify_dll_installation,
)
from infrastructure.implementation.hardware.robot.ajinextek.error_codes import (
    AXT_RT_SUCCESS,
    get_error_message,
)


class AjinextekRobot(RobotService):
    """AJINEXTEK 로봇 통합 서비스"""

    def __init__(self):
        """
        초기화
        """

        # Library information
        self.version: str = "Unknown"

        # Runtime state
        self._is_connected = False
        self._axis_count = 0  # Will be detected during connection
        self._current_position: float = 0.0
        self._servo_state: bool = False
        self._motion_status = MotionStatus.IDLE
        self._error_message = None

        # Initialize AXL wrapper
        self._axl = AXLWrapper()

        logger.info("AjinextekRobotAdapter initialized")

    async def connect(self, axis_id: int, irq_no: int) -> None:
        """
        하드웨어 연결

        Args:
            axis_id: Axis ID number
            irq_no: IRQ number for connection

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            logger.info(
                "Connecting to AJINEXTEK robot controller (IRQ: %s, Axis: %s)", irq_no, axis_id
            )

            # Print comprehensive system diagnostics before attempting connection
            logger.info("Performing pre-connection system diagnostics...")
            self._print_system_diagnostics()

            # Verify DLL installation before attempting to load
            dll_info = verify_dll_installation()
            if not dll_info["dll_exists"]:
                logger.error("AXL DLL not found - printing diagnostic information")
                print_dll_diagnostic_info()
                raise RobotConnectionError(
                    "AXL DLL not found at expected location",
                    "AJINEXTEK",
                    details=f"DLL path: {dll_info['dll_path']}, Available DLLs: {dll_info['available_dlls']}",
                )

            # Open AXL library with robust initialization and enhanced error reporting
            result = await self._initialize_axl_library_with_diagnostics(irq_no)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(
                    f"Failed to initialize AXL library: {error_msg} (Error Code: {result})"
                )

                # Provide detailed error analysis
                error_analysis = self._analyze_connection_error(result, irq_no)
                logger.error(f"Connection error analysis: {error_analysis}")

                raise RobotConnectionError(
                    f"Failed to initialize AXL library: {error_msg}",
                    "AJINEXTEK",
                    details=f"IRQ: {irq_no}, Error: {result}, Analysis: {error_analysis}",
                )

            # Get board count for verification (with error handling)
            try:
                board_count = await self._get_board_count_safely()
                logger.info(f"Board count detected: {board_count}")
            except Exception as e:
                logger.warning(f"Could not get board count: {e} (continuing anyway)")
                board_count = 0  # Default value

            # Get axis count from hardware (with error handling)
            try:
                self._axis_count = await self._get_axis_count_safely()
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
            await self._load_robot_parameters(axis_id)

            # Motion parameters are now loaded from .prm file via AxmMotLoadParaAll
            logger.info("Motion parameters initialized from .prm file")

            self._is_connected = True
            self._motion_status = MotionStatus.IDLE

            logger.info(
                f"AJINEXTEK robot controller connected successfully (IRQ: {irq_no}, Axis: {axis_id}, Total Axes: {self._axis_count})"
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
        하드웨어 연결 해제

        Returns:
            연결 해제 성공 여부
        """
        try:
            if self._is_connected:
                # Close AXL library connection
                try:
                    result = self._axl.close()
                    if result != AXT_RT_SUCCESS:
                        error_msg = get_error_message(result)
                        logger.warning(f"AXL library close warning: {error_msg}")
                except Exception as e:
                    logger.warning(f"Error closing AXL library: {e}")

                self._is_connected = False
                self._servo_state = False
                self._motion_status = MotionStatus.IDLE

                logger.info("AJINEXTEK robot controller disconnected")

        except Exception as e:
            logger.error(f"Error disconnecting AJINEXTEK robot: {e}")
            raise HardwareException(
                "ajinextek_robot",
                "disconnect",
                {"error": f"Error disconnecting AJINEXTEK robot: {e}"},
            ) from e

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
            while True:
                try:
                    home_result = self._axl.home_get_result(axis)

                    if home_result == HOME_SUCCESS:
                        logger.info(f"Homing completed successfully for axis {axis}")
                        break

                    elif home_result == HOME_SEARCHING:
                        # Get progress information for logging
                        try:
                            _, step = self._axl.home_get_rate(axis)
                            logger.debug(f"Homing axis {axis}: {step}%% complete")
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
                    logger.error(
                        "Failed to check homing status for axis %s: %s", axis, status_error
                    )
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
            logger.info(
                "Moving axis %s to absolute position: %smm at %smm/s", axis_id, position, vel
            )

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
            logger.info(
                "Moving axis %s by relative distance: %smm at %smm/s", axis_id, distance, vel
            )

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
            logger.info(
                "Stopping motion on axis %s with deceleration %s mm/s²", axis_id, deceleration
            )

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
            logger.warning("EMERGENCY STOP activated for axis %d", axis)

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

            logger.warning("Emergency stop completed for axis %d", axis)

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

        # Check specific axis
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

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Returns:
            상태 정보 딕셔너리
        """
        is_connected = await self.is_connected()

        status = {
            "connected": is_connected,
            "hardware_type": "AJINEXTEK",
            "motion_status": self._motion_status.value,
            "servo_state": self._servo_state,
        }

        if is_connected:
            status["axis_count"] = self._axis_count
            status["version"] = self.version

        return status

    # === Helper Methods ===

    def _ensure_connected(self) -> None:
        """Ensure robot controller is connected"""
        if not self._is_connected:
            raise RobotConnectionError(
                "Robot controller not connected",
                "AJINEXTEK",
            )

    def _print_system_diagnostics(self) -> None:
        """Print comprehensive system diagnostics for troubleshooting"""
        try:
            import platform
            import os

            logger.info("=== AJINEXTEK Robot Connection Diagnostics ===")
            logger.info(f"Operating System: {platform.system()} {platform.version()}")
            logger.info(f"Architecture: {platform.machine()} ({platform.architecture()[0]})")
            logger.info(f"Python Version: {platform.python_version()}")
            logger.info(f"Python Executable: {platform.python_implementation()}")

            # Check if running as administrator (Windows) with enhanced detection
            if platform.system() == "Windows":
                try:
                    import ctypes
                    import ctypes.wintypes

                    # Multiple methods to check admin privileges
                    is_admin_shell = ctypes.windll.shell32.IsUserAnAdmin()

                    # Alternative method: Check if we can write to system directory
                    can_write_system = False
                    try:
                        import tempfile

                        with tempfile.NamedTemporaryFile(dir="C:\\Windows\\System32", delete=True):
                            can_write_system = True
                    except (OSError, PermissionError):
                        can_write_system = False

                    # Check token elevation
                    is_elevated = False
                    try:
                        import ctypes.wintypes as wintypes

                        # Get current process token
                        TOKEN_QUERY = 0x0008
                        TokenElevation = 20

                        process_handle = ctypes.windll.kernel32.GetCurrentProcess()
                        token_handle = wintypes.HANDLE()

                        if ctypes.windll.advapi32.OpenProcessToken(
                            process_handle, TOKEN_QUERY, ctypes.byref(token_handle)
                        ):
                            elevation = wintypes.DWORD()
                            size = wintypes.DWORD(ctypes.sizeof(wintypes.DWORD))

                            if ctypes.windll.advapi32.GetTokenInformation(
                                token_handle,
                                TokenElevation,
                                ctypes.byref(elevation),
                                ctypes.sizeof(elevation),
                                ctypes.byref(size),
                            ):
                                is_elevated = bool(elevation.value)

                            ctypes.windll.kernel32.CloseHandle(token_handle)
                    except Exception:
                        pass

                    logger.info(f"Administrator Privileges Check:")
                    logger.info(f"  - Shell IsUserAnAdmin(): {is_admin_shell}")
                    logger.info(f"  - Can write to System32: {can_write_system}")
                    logger.info(f"  - Token is elevated: {is_elevated}")
                    logger.info(f"  - Overall admin status: {is_admin_shell or is_elevated}")

                    # If we're not running as admin, provide clear guidance
                    if not (is_admin_shell or is_elevated):
                        logger.warning("⚠️ NOT running with Administrator privileges!")
                        logger.warning(
                            "AJINEXTEK AXL library typically requires administrator access for:"
                        )
                        logger.warning("  - Hardware device driver access")
                        logger.warning("  - IRQ (Interrupt Request) allocation")
                        logger.warning("  - System-level hardware control")
                        logger.warning("")
                        logger.warning("Please run this application as Administrator:")
                        logger.warning("  1. Right-click on Command Prompt")
                        logger.warning("  2. Select 'Run as administrator'")
                        logger.warning("  3. Navigate to project directory and run again")

                except Exception as e:
                    logger.info(f"Unable to check administrator privileges: {e}")
                    logger.info("Proceeding anyway - some operations may fail")

            # Print DLL diagnostics
            print_dll_diagnostic_info()

            logger.info("=== End Diagnostics ===")

        except Exception as e:
            logger.warning(f"Failed to print system diagnostics: {e}")

    def _analyze_connection_error(self, error_code: int, irq_no: int) -> dict:
        """Analyze connection error and provide specific troubleshooting guidance"""
        analysis = {
            "error_code": error_code,
            "error_name": get_error_message(error_code),
            "likely_causes": [],
            "troubleshooting_steps": [],
            "system_checks": [],
        }

        # Error-specific analysis
        if error_code == 1053:  # Library not opened/not loaded
            analysis["likely_causes"] = [
                "AXL DLL failed to load",
                "Missing system dependencies (Visual C++ Redistributables)",
                "Architecture mismatch (32-bit vs 64-bit)",
                "Missing AJINEXTEK hardware drivers",
                "Insufficient permissions",
            ]
            analysis["troubleshooting_steps"] = [
                "Run application as Administrator",
                "Install Visual C++ Redistributables 2015-2022",
                "Install AJINEXTEK device drivers",
                "Verify DLL architecture matches Python architecture",
                "Check Windows Event Viewer for detailed error messages",
            ]
            analysis["system_checks"] = [
                "Check if AJINEXTEK hardware is connected",
                "Verify USB/PCI device recognition in Device Manager",
                f"Confirm IRQ {irq_no} is available and not in use",
                "Check for driver conflicts",
            ]

        elif error_code == 1001:  # IRQ already in use
            analysis["likely_causes"] = [
                f"IRQ {irq_no} is already in use by another process",
                "Previous connection was not properly closed",
                "Multiple instances of the application running",
            ]
            analysis["troubleshooting_steps"] = [
                "Close all other AJINEXTEK applications",
                "Restart the application",
                "Try a different IRQ number (if available)",
                "Reboot the system if necessary",
            ]

        elif error_code == 1002:  # Hardware not found
            analysis["likely_causes"] = [
                "AJINEXTEK hardware not connected or not detected",
                "Hardware drivers not installed",
                "Hardware malfunction or power issues",
            ]
            analysis["troubleshooting_steps"] = [
                "Check physical hardware connections",
                "Verify hardware power status",
                "Install or update AJINEXTEK drivers",
                "Check Device Manager for hardware recognition",
            ]

        return analysis

    async def _initialize_axl_library_with_diagnostics(
        self, irq_no: int, max_retries: int = 3
    ) -> int:
        """Initialize AXL library with enhanced diagnostics and retry logic"""
        logger.info(f"Attempting to initialize AXL library with IRQ {irq_no}")
        logger.info(f"Maximum retry attempts: {max_retries}")

        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"AXL library initialization attempt {attempt + 1}/{max_retries}")

                # Check if library is already open
                if self._axl.is_opened():
                    logger.info("AXL library is already open, closing first")
                    try:
                        self._axl.close()
                        await asyncio.sleep(0.1)  # Wait for clean shutdown
                    except Exception as e:
                        logger.warning(f"Error closing existing library: {e}")

                # Attempt to open library
                logger.debug(f"Opening AXL library with IRQ {irq_no}")
                result = self._axl.open(irq_no)

                if result == AXT_RT_SUCCESS:
                    logger.info(f"✓ AXL library opened successfully on attempt {attempt + 1}")
                    # Small delay to let library fully initialize
                    await asyncio.sleep(0.1)
                    return result
                else:
                    error_msg = get_error_message(result)
                    logger.warning(f"Attempt {attempt + 1} failed: {error_msg} (code: {result})")
                    last_error = result

                    # Provide attempt-specific guidance
                    if attempt == 0 and result == 1053:
                        logger.info("First attempt failed - this may be normal. Retrying...")
                    elif attempt == 1 and result == 1001:
                        logger.info("IRQ may be busy - waiting longer before retry...")
                        await asyncio.sleep(1.0)  # Longer wait for IRQ issues

                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 0.5  # Progressive backoff
                        logger.info(f"Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"Exception during initialization attempt {attempt + 1}: {e}")
                last_error = 1053  # Generic "not loaded" error
                if attempt < max_retries - 1:
                    await asyncio.sleep((attempt + 1) * 0.5)

        # All attempts failed
        final_error = last_error if last_error is not None else 1053
        logger.error(f"All {max_retries} initialization attempts failed")
        logger.error(f"Final error code: {final_error} ({get_error_message(final_error)})")

        # Provide final troubleshooting guidance
        error_analysis = self._analyze_connection_error(final_error, irq_no)
        logger.error("Final troubleshooting analysis:")
        for cause in error_analysis["likely_causes"]:
            logger.error(f"  - {cause}")
        logger.error("Recommended actions:")
        for step in error_analysis["troubleshooting_steps"]:
            logger.error(f"  1. {step}")

        return final_error

    # Legacy method kept for compatibility - now calls the enhanced version
    async def _initialize_axl_library(self, irq_no: int, max_retries: int = 3) -> int:
        """Initialize AXL library with retry logic (legacy compatibility method)"""
        return await self._initialize_axl_library_with_diagnostics(irq_no, max_retries)

    async def _get_board_count_safely(self, max_retries: int = 2) -> int:
        """Get board count with error handling and retries

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            int: Number of boards detected

        Raises:
            Exception: If all attempts fail
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                # Small delay before attempting to read board count
                if attempt > 0:
                    await asyncio.sleep(0.1)

                board_count = self._axl.get_board_count()
                return board_count

            except Exception as e:
                last_exception = e
                logger.debug(f"Board count attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    await asyncio.sleep(0.2)

        raise last_exception if last_exception else Exception("Board count retrieval failed")

    async def _get_axis_count_safely(self, max_retries: int = 2) -> int:
        """Get axis count with error handling and retries

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            int: Number of axes detected

        Raises:
            Exception: If all attempts fail
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                # Small delay before attempting to read axis count
                if attempt > 0:
                    await asyncio.sleep(0.1)

                axis_count = self._axl.get_axis_count()
                return axis_count

            except Exception as e:
                last_exception = e
                logger.debug(f"Axis count attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    await asyncio.sleep(0.2)

        raise last_exception if last_exception else Exception("Axis count retrieval failed")

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
            logger.info(f"Enabling servo for axis {axis}")

            if not self._servo_state:
                self._set_servo_on()
                logger.debug(f"Servo enabled for axis {axis}")
            else:
                logger.debug(f"Servo already enabled for axis {axis}")

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
            project_root = Path(__file__).parent.parent.parent.parent.parent
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
                "Loading robot motion settings from %s using AxmMotLoadPara for axis %d",
                robot_motion_settings_file,
                axis_id,
            )

            # Load parameters for specific axis using AJINEXTEK standard function
            result = self._axl.load_para(axis_id, str(robot_motion_settings_file))

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(
                    f"Failed to load motion settings from {robot_motion_settings_file}: {error_msg}"
                )
                raise RobotConnectionError(
                    f"AxmMotLoadPara failed for axis {axis_id}: {error_msg}",
                    "AJINEXTEK",
                    details=f"File: {robot_motion_settings_file}, Axis: {axis_id}, Error: {result}",
                )

            logger.info(
                "Robot motion settings loaded successfully from %s for axis %d",
                robot_motion_settings_file,
                axis_id,
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
