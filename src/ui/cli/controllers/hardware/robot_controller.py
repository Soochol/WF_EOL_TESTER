"""
Robot Hardware Controller

Provides robot-specific control operations including movement,
positioning, and status monitoring for AJINEXTEK motion controllers.
"""

import asyncio
from typing import Optional

from rich.status import Status

from application.interfaces.hardware.robot import RobotService
from domain.value_objects.hardware_configuration import RobotConfig

from ...rich_formatter import RichFormatter
from ..base.hardware_controller import HardwareController, simple_interactive_menu


class RobotController(HardwareController):
    """Controller for Robot hardware"""

    def __init__(self, robot_service: RobotService, formatter: RichFormatter, robot_config: Optional[RobotConfig] = None):
        super().__init__(formatter)
        self.robot_service = robot_service
        self.robot_config = robot_config
        # Extract axis_id for backward compatibility
        self.axis_id = robot_config.axis_id if robot_config else 0
        self.name = "Robot Control System"

    async def show_status(self) -> None:
        """Display robot status"""
        try:
            is_connected = await self.robot_service.is_connected()

            status_details = {
                "Connection": "Connected" if is_connected else "Disconnected",
                "Type": "AJINEXTEK Motion Controller",
            }

            if is_connected:
                try:
                    # Get additional status information if connected
                    motion_status = await self.robot_service.get_motion_status()
                    status_details["Motion Status"] = motion_status.value
                    status_details["Axes"] = "6 DOF"
                except Exception as e:
                    status_details["Status Error"] = str(e)

            self.formatter.print_status(
                "Robot Hardware Status",
                "CONNECTED" if is_connected else "DISCONNECTED",
                details=status_details,
            )

        except Exception as e:
            self.formatter.print_message(
                f"Failed to get robot status: {str(e)}", message_type="error"
            )

    async def connect(self) -> bool:
        """Connect to robot"""

        async def connect_operation():
            if self.robot_config:
                # Use YAML configuration
                await self.robot_service.connect(
                    axis_id=self.robot_config.axis_id,
                    irq_no=self.robot_config.irq_no
                )
            else:
                # Fallback to defaults if no config available
                await self.robot_service.connect(axis_id=0, irq_no=7)
            return True

        return await self._show_progress_with_message(
            "Connecting to robot...",
            connect_operation,
            "Robot connected successfully",
            "Failed to connect to robot",
        )

    async def disconnect(self) -> bool:
        """Disconnect from robot"""

        async def disconnect_operation():
            await self.robot_service.disconnect()
            return True

        return await self._show_progress_with_message(
            "Disconnecting from robot...",
            disconnect_operation,
            "Robot disconnected successfully",
            "Failed to disconnect robot",
            show_time=0.2,
        )

    async def show_control_menu(self) -> Optional[str]:
        """Show enhanced Robot control menu with status information"""

        # Get current status information
        try:
            is_connected = await self.robot_service.is_connected()
            connection_status = self._format_connection_status(is_connected)

            if is_connected:
                try:
                    # Get robot status information
                    status = await self.robot_service.get_status()
                    is_initialized = status.get("initialized", False)
                    current_position = status.get("position", "Unknown")

                    init_status = "🟢 Ready" if is_initialized else "🔴 Not Initialized"
                    position_info = f"📍 {current_position}"
                except Exception:
                    init_status = "❓ Unknown"
                    position_info = "📍 Unknown"
            else:
                init_status = "🔴 Not Initialized"
                position_info = "📍 Unknown"

        except Exception:
            connection_status = "❓ Unknown"
            init_status = "❓ Unknown"
            position_info = "📍 Unknown"

        # Enhanced menu options with icons, status, and shortcuts in descriptions
        menu_options = {
            "1": "📊 Show Status (s)",
            "2": "🔌 Connect (c)",
            "3": "❌ Disconnect (d)",
            "4": "✅ Servo On (servo-on)       ⚡ [Enable Motor]",
            "5": "❌ Servo Off (servo-off)     ⚠️  [Disable Motor]",
            "6": "🚨 Emergency Stop (stop)      ⚠️  [Safety Critical]",
            "7": "🏠 Home Axis (home)",
            "8": "📍 Move Absolute (abs)",
            "9": "↔️ Move Relative (rel)",
            "10": "⏹️ Stop Motion (stop-motion)",
            "11": "📍 Get Position (pos)",
            "b": "⬅️  Back to Hardware Menu",
        }

        # Create enhanced title with status
        enhanced_title = (
            f"🤖 Robot Control System\n"
            f"📡 Status: {connection_status}  |  ⚙️ Init: {init_status}  |  {position_info}\n"
            f"[dim]💡 Shortcuts: s, c, d, servo-on, servo-off, stop, home, abs, rel, stop-motion, pos[/dim]"
        )

        # Get user input with custom validation that includes shortcuts
        while True:
            choice = simple_interactive_menu(
                self.formatter.console,
                menu_options,
                enhanced_title,
                "Select Robot operation (number or shortcut)",
            )

            # If choice is None (cancelled/interrupted), return None
            if choice is None:
                return None

            # Check if it's a valid choice or shortcut
            valid_shortcuts = [
                "s",
                "c",
                "d",
                "servo-on",
                "servo-off",
                "stop",
                "home",
                "abs",
                "rel",
                "stop-motion",
                "pos",
            ]
            if choice in menu_options or choice in valid_shortcuts:
                return choice

            # If we get here, it's an invalid option - the menu will show the error and loop
            # The ui_manager.create_interactive_menu already showed an error, so we just continue

    async def execute_command(self, command: str) -> bool:
        """Execute robot command with support for shortcuts"""
        try:
            # Normalize command input
            cmd = command.strip().lower()

            if cmd == "1" or cmd == "s":
                await self.show_status()
            elif cmd == "2" or cmd == "c":
                return await self.connect()
            elif cmd == "3" or cmd == "d":
                return await self.disconnect()
            elif cmd == "4" or cmd == "servo-on":
                await self._servo_on()
            elif cmd == "5" or cmd == "servo-off":
                await self._servo_off()
            elif cmd == "6" or cmd == "stop":
                await self._emergency_stop()
            elif cmd == "7" or cmd == "home":
                await self._home_axis()
            elif cmd == "8" or cmd == "abs":
                await self._move_absolute()
            elif cmd == "9" or cmd == "rel":
                await self._move_relative()
            elif cmd == "10" or cmd == "stop-motion":
                await self._stop_motion()
            elif cmd == "11" or cmd == "pos":
                await self._get_position()
            else:
                return False
            return True

        except Exception as e:
            self.formatter.print_message(f"❌ Robot command failed: {str(e)}", message_type="error")
            return False

    # Private robot-specific operations
    async def _servo_on(self) -> None:
        """Enable servo (motor power on)"""
        try:
            primary_axis = self.axis_id

            async def servo_on_operation():
                await self.robot_service.enable_servo(primary_axis)
                return True

            await self._show_progress_with_message(
                f"Enabling servo for axis {primary_axis}...",
                servo_on_operation,
                f"Servo enabled successfully for axis {primary_axis}",
                "Servo enable failed",
            )

        except Exception as e:
            self.formatter.print_message(f"Servo enable failed: {str(e)}", message_type="error")

    async def _servo_off(self) -> None:
        """Disable servo (motor power off)"""
        try:
            primary_axis = self.axis_id

            async def servo_off_operation():
                await self.robot_service.disable_servo(primary_axis)
                return True

            await self._show_progress_with_message(
                f"Disabling servo for axis {primary_axis}...",
                servo_off_operation,
                f"Servo disabled successfully for axis {primary_axis}",
                "Servo disable failed",
            )

        except Exception as e:
            self.formatter.print_message(f"Servo disable failed: {str(e)}", message_type="error")

    async def _emergency_stop(self) -> None:
        """Execute emergency stop"""
        try:
            # Get primary axis and stop it
            primary_axis = self.axis_id
            await self.robot_service.emergency_stop(primary_axis)
            self.formatter.print_message(
                f"Emergency stop executed for axis {primary_axis}",
                message_type="warning",
                title="Emergency Stop",
            )

        except Exception as e:
            self.formatter.print_message(f"Emergency stop failed: {str(e)}", message_type="error")

    async def _home_axis(self) -> None:
        """Home axis to origin position"""
        try:
            # Check if robot is connected
            if not await self.robot_service.is_connected():
                self.formatter.print_message("Robot is not connected", message_type="error")
                return

            primary_axis = self.axis_id

            async def home_operation():
                await self.robot_service.home_axis(primary_axis)
                return True

            await self._show_progress_with_message(
                f"Homing axis {primary_axis} to origin...",
                home_operation,
                f"Axis {primary_axis} homed successfully",
                "Homing failed",
            )

        except Exception as e:
            self.formatter.print_message(f"Homing failed: {str(e)}", message_type="error")

    async def _move_absolute(self) -> None:
        """Move axis to absolute position"""
        try:
            # Check if robot is connected
            if not await self.robot_service.is_connected():
                self.formatter.print_message("Robot is not connected", message_type="error")
                return

            primary_axis = self.axis_id

            # Get user input for position and motion parameters
            self.formatter.print_message("🎯 Absolute Position Move Setup", message_type="info")
            
            # Get target position from user
            position = self._get_user_input_with_validation(
                "Enter target position (mm):",
                input_type=float,
                validator=lambda x: -1000.0 <= x <= 1000.0,  # Reasonable position range
            )
            if position is None:
                self.formatter.print_message("❌ Move cancelled", message_type="info")
                return
            
            # Get default values from config or use fallbacks
            default_velocity = self.robot_config.velocity if self.robot_config else 200.0
            default_acceleration = self.robot_config.acceleration if self.robot_config else 1000.0
            default_deceleration = self.robot_config.deceleration if self.robot_config else 1000.0
            
            # Get velocity from user (with default)
            velocity = self._get_user_input_with_validation(
                f"Enter velocity (mm/s) [default: {default_velocity:.1f}]:",
                input_type=float,
                validator=lambda x: 1.0 <= x <= 1000.0,  # Reasonable velocity range
                default_value=default_velocity,
            )
            if velocity is None:
                velocity = default_velocity
            
            # Get acceleration from user (with default)
            acceleration = self._get_user_input_with_validation(
                f"Enter acceleration (mm/s²) [default: {default_acceleration:.1f}]:",
                input_type=float,
                validator=lambda x: 100.0 <= x <= 10000.0,  # Reasonable acceleration range
                default_value=default_acceleration,
            )
            if acceleration is None:
                acceleration = default_acceleration
            
            # Get deceleration from user (with default)
            deceleration = self._get_user_input_with_validation(
                f"Enter deceleration (mm/s²) [default: {default_deceleration:.1f}]:",
                input_type=float,
                validator=lambda x: 100.0 <= x <= 10000.0,  # Reasonable deceleration range
                default_value=default_deceleration,
            )
            if deceleration is None:
                deceleration = default_deceleration

            async def move_operation():
                await self.robot_service.move_absolute(
                    position=position,
                    axis_id=primary_axis,
                    velocity=velocity,
                    acceleration=acceleration,
                    deceleration=deceleration,
                )
                return True

            # Show motion parameters summary
            self.formatter.print_message(
                f"📊 Motion Parameters:\n"
                f"   Target Position: {position:.2f} mm\n"
                f"   Velocity: {velocity:.1f} mm/s\n"
                f"   Acceleration: {acceleration:.1f} mm/s²\n"
                f"   Deceleration: {deceleration:.1f} mm/s²",
                message_type="info"
            )
            
            await self._show_progress_with_message(
                f"Moving axis {primary_axis} to position {position:.2f}mm...",
                move_operation,
                f"Axis {primary_axis} moved to {position:.2f}mm successfully",
                "Absolute move failed",
            )

        except Exception as e:
            self.formatter.print_message(f"Absolute move failed: {str(e)}", message_type="error")

    async def _move_relative(self) -> None:
        """Move axis by relative distance"""
        try:
            # Check if robot is connected
            if not await self.robot_service.is_connected():
                self.formatter.print_message("Robot is not connected", message_type="error")
                return

            primary_axis = self.axis_id

            # Get user input for distance and motion parameters
            self.formatter.print_message("🎯 Relative Position Move Setup", message_type="info")
            
            # Get relative distance from user
            distance = self._get_user_input_with_validation(
                "Enter relative distance (mm):",
                input_type=float,
                validator=lambda x: -500.0 <= x <= 500.0,  # Reasonable relative distance range
            )
            if distance is None:
                self.formatter.print_message("❌ Move cancelled", message_type="info")
                return
            
            # Get default values from config or use fallbacks
            default_velocity = self.robot_config.velocity if self.robot_config else 200.0
            default_acceleration = self.robot_config.acceleration if self.robot_config else 1000.0
            default_deceleration = self.robot_config.deceleration if self.robot_config else 1000.0
            
            # Get velocity from user (with default)
            velocity = self._get_user_input_with_validation(
                f"Enter velocity (mm/s) [default: {default_velocity:.1f}]:",
                input_type=float,
                validator=lambda x: 1.0 <= x <= 1000.0,  # Reasonable velocity range
                default_value=default_velocity,
            )
            if velocity is None:
                velocity = default_velocity
            
            # Get acceleration from user (with default)
            acceleration = self._get_user_input_with_validation(
                f"Enter acceleration (mm/s²) [default: {default_acceleration:.1f}]:",
                input_type=float,
                validator=lambda x: 100.0 <= x <= 10000.0,  # Reasonable acceleration range
                default_value=default_acceleration,
            )
            if acceleration is None:
                acceleration = default_acceleration
            
            # Get deceleration from user (with default)
            deceleration = self._get_user_input_with_validation(
                f"Enter deceleration (mm/s²) [default: {default_deceleration:.1f}]:",
                input_type=float,
                validator=lambda x: 100.0 <= x <= 10000.0,  # Reasonable deceleration range
                default_value=default_deceleration,
            )
            if deceleration is None:
                deceleration = default_deceleration

            async def move_operation():
                await self.robot_service.move_relative(
                    distance=distance,
                    axis_id=primary_axis,
                    velocity=velocity,
                    acceleration=acceleration,
                    deceleration=deceleration,
                )
                return True

            # Show motion parameters summary
            self.formatter.print_message(
                f"📊 Motion Parameters:\\n"
                f"   Relative Distance: {distance:.2f} mm\\n"
                f"   Velocity: {velocity:.1f} mm/s\\n"
                f"   Acceleration: {acceleration:.1f} mm/s²\\n"
                f"   Deceleration: {deceleration:.1f} mm/s²",
                message_type="info"
            )

            await self._show_progress_with_message(
                f"Moving axis {primary_axis} by {distance:.2f}mm...",
                move_operation,
                f"Axis {primary_axis} moved by {distance:.2f}mm successfully",
                "Relative move failed",
            )

        except Exception as e:
            self.formatter.print_message(f"Relative move failed: {str(e)}", message_type="error")

    async def _stop_motion(self) -> None:
        """Stop motion on primary axis"""
        try:
            # Check if robot is connected
            if not await self.robot_service.is_connected():
                self.formatter.print_message("Robot is not connected", message_type="error")
                return

            primary_axis = self.axis_id

            async def stop_operation():
                # Use deceleration from config or default
                if self.robot_config:
                    deceleration = self.robot_config.deceleration
                else:
                    deceleration = 1000.0  # mm/s²
                await self.robot_service.stop_motion(primary_axis, deceleration)
                return True

            await self._show_progress_with_message(
                f"Stopping motion on axis {primary_axis}...",
                stop_operation,
                f"Motion stopped on axis {primary_axis}",
                "Stop motion failed",
                show_time=0.2,
            )

        except Exception as e:
            self.formatter.print_message(f"Stop motion failed: {str(e)}", message_type="error")

    async def _get_position(self) -> None:
        """Get current position of primary axis"""
        try:
            # Check if robot is connected
            if not await self.robot_service.is_connected():
                self.formatter.print_message("Robot is not connected", message_type="error")
                return

            primary_axis = self.axis_id

            async def get_pos_operation():
                return await self.robot_service.get_position(primary_axis)

            with self.formatter.create_progress_display(
                f"Reading position of axis {primary_axis}...", show_spinner=True
            ) as progress_display:
                if isinstance(progress_display, Status):
                    progress_display.update("Reading position...")
                await asyncio.sleep(0.2)  # Show spinner briefly

                position = await get_pos_operation()

                if isinstance(progress_display, Status):
                    progress_display.update("Position read successfully")
                    await asyncio.sleep(0.3)  # Show success message briefly

            # Display position information
            position_details = {
                "Axis": f"Axis {primary_axis}",
                "Current Position": f"{position:.3f} mm",
                "Status": "Position read successfully",
            }

            self.formatter.print_status(
                "Robot Position Information", "POSITION_READ", details=position_details
            )

        except Exception as e:
            self.formatter.print_message(f"Get position failed: {str(e)}", message_type="error")
