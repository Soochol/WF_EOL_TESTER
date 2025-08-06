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
            "4": f"⚙️ Initialize Robot (init)    [Status: {init_status}]",
            "5": "🚨 Emergency Stop (stop)      ⚠️  [Safety Critical]",
            "6": "🏠 Home Axis (home)",
            "7": "📍 Move Absolute (abs)",
            "8": "↔️ Move Relative (rel)",
            "9": "⏹️ Stop Motion (stop-motion)",
            "10": "📍 Get Position (pos)",
            "b": "⬅️  Back to Hardware Menu",
        }

        # Create enhanced title with status
        enhanced_title = (
            f"🤖 Robot Control System\n"
            f"📡 Status: {connection_status}  |  ⚙️ Init: {init_status}  |  {position_info}\n"
            f"[dim]💡 Shortcuts: s, c, d, init, stop, home, abs, rel, stop-motion, pos[/dim]"
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
                "init",
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
            elif cmd == "4" or cmd == "init":
                await self._initialize_robot()
            elif cmd == "5" or cmd == "stop":
                await self._emergency_stop()
            elif cmd == "6" or cmd == "home":
                await self._home_axis()
            elif cmd == "7" or cmd == "abs":
                await self._move_absolute()
            elif cmd == "8" or cmd == "rel":
                await self._move_relative()
            elif cmd == "9" or cmd == "stop-motion":
                await self._stop_motion()
            elif cmd == "10" or cmd == "pos":
                await self._get_position()
            else:
                return False
            return True

        except Exception as e:
            self.formatter.print_message(f"❌ Robot command failed: {str(e)}", message_type="error")
            return False

    # Private robot-specific operations
    async def _initialize_robot(self) -> None:
        """Initialize robot system"""

        async def init_operation():
            # Home primary axis using parameters from configuration
            primary_axis = self.axis_id
            await self.robot_service.home_axis(primary_axis)
            return True

        await self._show_progress_with_message(
            "Initializing robot system...",
            init_operation,
            "Robot initialized successfully",
            "Robot initialization failed",
        )

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

            # Get user input for position
            self.formatter.print_message("Enter absolute position parameters:", message_type="info")

            # Use configuration values or defaults
            position = 100.0  # mm - TODO: Could be made configurable
            if self.robot_config:
                velocity = self.robot_config.velocity
                acceleration = self.robot_config.acceleration
                deceleration = self.robot_config.deceleration
            else:
                # Fallback to defaults
                velocity = 200.0  # mm/s
                acceleration = 1000.0  # mm/s²
                deceleration = 1000.0  # mm/s²

            async def move_operation():
                await self.robot_service.move_absolute(
                    position=position,
                    axis_id=primary_axis,
                    velocity=velocity,
                    acceleration=acceleration,
                    deceleration=deceleration,
                )
                return True

            await self._show_progress_with_message(
                f"Moving axis {primary_axis} to position {position}mm...",
                move_operation,
                f"Axis {primary_axis} moved to {position}mm successfully",
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

            # Get user input for distance
            self.formatter.print_message("Enter relative movement parameters:", message_type="info")

            # Use configuration values or defaults
            distance = 10.0  # mm - TODO: Could be made configurable
            if self.robot_config:
                velocity = self.robot_config.velocity
                acceleration = self.robot_config.acceleration
                deceleration = self.robot_config.deceleration
            else:
                # Fallback to defaults
                velocity = 200.0  # mm/s
                acceleration = 1000.0  # mm/s²
                deceleration = 1000.0  # mm/s²

            async def move_operation():
                await self.robot_service.move_relative(
                    distance=distance,
                    axis_id=primary_axis,
                    velocity=velocity,
                    acceleration=acceleration,
                    deceleration=deceleration,
                )
                return True

            await self._show_progress_with_message(
                f"Moving axis {primary_axis} by {distance}mm...",
                move_operation,
                f"Axis {primary_axis} moved by {distance}mm successfully",
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
