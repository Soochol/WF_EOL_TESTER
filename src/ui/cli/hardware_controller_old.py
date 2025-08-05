"""
Hardware Control Manager - Legacy Compatibility Module

This module has been refactored into a modular controller structure.
Imports from the new controllers package for backward compatibility.

New structure:
- controllers/base/hardware_controller.py - Abstract base class
- controllers/hardware/ - Specialized hardware controllers
- controllers/orchestration/ - Hardware management orchestration

For new development, import directly from the controllers package.
"""

# Legacy compatibility imports - use controllers package for new development
from .controllers import (
    HardwareController,
    RobotController,
    MCUController,
    LoadCellController,
    PowerController,
    HardwareControlManager,
)

from .controllers.base.hardware_controller import simple_interactive_menu

# Re-export for backward compatibility
__all__ = [
    "HardwareController",
    "RobotController",
    "MCUController",
    "LoadCellController",
    "PowerController",
    "HardwareControlManager",
    "simple_interactive_menu",
]


class HardwareController(ABC):
    """Abstract base class for hardware controllers"""

    def __init__(self, formatter: RichFormatter):
        self.formatter = formatter

    @abstractmethod
    async def show_status(self) -> None:
        """Display hardware status"""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to hardware"""

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from hardware"""

    @abstractmethod
    async def show_control_menu(self) -> Optional[str]:
        """Show hardware-specific control menu"""

    @abstractmethod
    async def execute_command(self, command: str) -> bool:
        """Execute hardware-specific command"""


class RobotController(HardwareController):
    """Controller for Robot hardware"""

    def __init__(self, robot_service: RobotService, formatter: RichFormatter, axis_id: int = 0):
        super().__init__(formatter)
        self.robot_service = robot_service
        self.axis_id = axis_id
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
        try:
            with self.formatter.create_progress_display(
                "Connecting to robot...", show_spinner=True
            ) as progress_display:
                # Ensure minimum display time for spinner visibility
                await asyncio.sleep(0.5)  # Show spinner for at least 500ms
                await self.robot_service.connect(axis_id=0, irq_no=7)
                # Handle different types returned by create_progress_display
                if isinstance(progress_display, Status):
                    progress_display.update("Robot connected successfully")
                    await asyncio.sleep(0.3)  # Show success message briefly
                elif isinstance(progress_display, Progress):
                    # Progress objects need task_id, but we don't use this case here
                    # since no total_steps was provided to create_progress_display
                    pass

            self.formatter.print_message("Robot connected successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to connect to robot: {str(e)}", message_type="error"
            )
            return False

    async def disconnect(self) -> bool:
        """Disconnect from robot"""
        try:
            await self.robot_service.disconnect()
            self.formatter.print_message("Robot disconnected successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to disconnect robot: {str(e)}", message_type="error"
            )
            return False

    async def show_control_menu(self) -> Optional[str]:
        """Show enhanced Robot control menu with status information"""

        # Get current status information
        try:
            is_connected = await self.robot_service.is_connected()
            connection_status = "🟢 Connected" if is_connected else "🔴 Disconnected"

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

    async def _initialize_robot(self) -> None:
        """Initialize robot system"""
        try:
            with self.formatter.create_progress_display(
                "Initializing robot system...", show_spinner=True
            ) as progress_display:
                if isinstance(progress_display, Status):
                    progress_display.update("Initializing robot...")
                await asyncio.sleep(0.5)  # Show spinner for visibility
                # Home primary axis using parameters from configuration
                primary_axis = self.axis_id
                await self.robot_service.home_axis(primary_axis)
                if isinstance(progress_display, Status):
                    progress_display.update("Robot initialization complete")
                    await asyncio.sleep(0.3)  # Show success message briefly

            self.formatter.print_message("Robot initialized successfully", message_type="success")

        except Exception as e:
            self.formatter.print_message(
                f"Robot initialization failed: {str(e)}", message_type="error"
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

            # Get primary axis for homing
            primary_axis = self.axis_id

            with self.formatter.create_progress_display(
                f"Homing axis {primary_axis} to origin...", show_spinner=True
            ) as progress_display:
                if isinstance(progress_display, Status):
                    progress_display.update(f"Moving axis {primary_axis} to home position...")
                await asyncio.sleep(0.5)  # Show spinner for visibility

                await self.robot_service.home_axis(primary_axis)

                if isinstance(progress_display, Status):
                    progress_display.update("Homing complete")
                    await asyncio.sleep(0.3)  # Show success message briefly

            self.formatter.print_message(
                f"Axis {primary_axis} homed successfully", message_type="success"
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

            # Get primary axis
            primary_axis = self.axis_id

            # Get user input for position
            self.formatter.print_message("Enter absolute position parameters:", message_type="info")

            # For simplicity, use default values. In a real application, you'd prompt for input
            position = 100.0  # mm
            velocity = 200.0  # mm/s
            acceleration = 1000.0  # mm/s²
            deceleration = 1000.0  # mm/s²

            with self.formatter.create_progress_display(
                f"Moving axis {primary_axis} to position {position}mm...", show_spinner=True
            ) as progress_display:
                if isinstance(progress_display, Status):
                    progress_display.update(f"Moving to {position}mm...")
                await asyncio.sleep(0.5)  # Show spinner for visibility

                await self.robot_service.move_absolute(
                    position=position,
                    axis_id=primary_axis,
                    velocity=velocity,
                    acceleration=acceleration,
                    deceleration=deceleration,
                )

                if isinstance(progress_display, Status):
                    progress_display.update("Movement complete")
                    await asyncio.sleep(0.3)  # Show success message briefly

            self.formatter.print_message(
                f"Axis {primary_axis} moved to {position}mm successfully", message_type="success"
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

            # Get primary axis
            primary_axis = self.axis_id

            # Get user input for distance
            self.formatter.print_message("Enter relative movement parameters:", message_type="info")

            # For simplicity, use default values. In a real application, you'd prompt for input
            distance = 10.0  # mm
            velocity = 200.0  # mm/s
            acceleration = 1000.0  # mm/s²
            deceleration = 1000.0  # mm/s²

            with self.formatter.create_progress_display(
                f"Moving axis {primary_axis} by {distance}mm...", show_spinner=True
            ) as progress_display:
                if isinstance(progress_display, Status):
                    progress_display.update(f"Moving by {distance}mm...")
                await asyncio.sleep(0.5)  # Show spinner for visibility

                await self.robot_service.move_relative(
                    distance=distance,
                    axis_id=primary_axis,
                    velocity=velocity,
                    acceleration=acceleration,
                    deceleration=deceleration,
                )

                if isinstance(progress_display, Status):
                    progress_display.update("Movement complete")
                    await asyncio.sleep(0.3)  # Show success message briefly

            self.formatter.print_message(
                f"Axis {primary_axis} moved by {distance}mm successfully", message_type="success"
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

            # Get primary axis
            primary_axis = self.axis_id

            with self.formatter.create_progress_display(
                f"Stopping motion on axis {primary_axis}...", show_spinner=True
            ) as progress_display:
                if isinstance(progress_display, Status):
                    progress_display.update("Stopping motion...")
                await asyncio.sleep(0.2)  # Show spinner briefly

                # Use default deceleration from robot config
                deceleration = 1000.0  # mm/s²
                await self.robot_service.stop_motion(primary_axis, deceleration)

                if isinstance(progress_display, Status):
                    progress_display.update("Motion stopped")
                    await asyncio.sleep(0.3)  # Show success message briefly

            self.formatter.print_message(
                f"Motion stopped on axis {primary_axis}", message_type="success"
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

            # Get primary axis
            primary_axis = self.axis_id

            with self.formatter.create_progress_display(
                f"Reading position of axis {primary_axis}...", show_spinner=True
            ) as progress_display:
                if isinstance(progress_display, Status):
                    progress_display.update("Reading position...")
                await asyncio.sleep(0.2)  # Show spinner briefly

                position = await self.robot_service.get_position(primary_axis)

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


class MCUController(HardwareController):
    """Controller for MCU hardware"""

    def __init__(self, mcu_service: MCUService, formatter: RichFormatter):
        super().__init__(formatter)
        self.mcu_service = mcu_service
        self.name = "MCU Control System"

    async def show_status(self) -> None:
        """Display MCU status"""
        try:
            is_connected = await self.mcu_service.is_connected()

            status_details = {
                "Connection": "Connected" if is_connected else "Disconnected",
                "Type": "LMA Temperature Controller",
            }

            if is_connected:
                try:
                    # Get temperature information if connected
                    temperature = await self.mcu_service.get_temperature()
                    status_details["Temperature"] = f"{temperature:.2f}°C"
                    status_details["Test Mode"] = "Available"
                except Exception as e:
                    status_details["Status Error"] = str(e)

            self.formatter.print_status(
                "MCU Hardware Status",
                "CONNECTED" if is_connected else "DISCONNECTED",
                details=status_details,
            )

        except Exception as e:
            self.formatter.print_message(
                f"Failed to get MCU status: {str(e)}", message_type="error"
            )

    async def connect(self) -> bool:
        """Connect to MCU"""
        try:
            with self.formatter.create_progress_display(
                "Connecting to MCU...", show_spinner=True
            ) as progress_display:
                await asyncio.sleep(0.5)  # Show spinner for visibility
                await self.mcu_service.connect(
                    port="/dev/ttyUSB1",
                    baudrate=115200,
                    timeout=2.0,
                    bytesize=8,
                    stopbits=1,
                    parity=None,
                )
                if isinstance(progress_display, Status):
                    progress_display.update("MCU connected successfully")
                    await asyncio.sleep(0.3)  # Show success message briefly

            self.formatter.print_message("MCU connected successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to connect to MCU: {str(e)}", message_type="error"
            )
            return False

    async def disconnect(self) -> bool:
        """Disconnect from MCU"""
        try:
            await self.mcu_service.disconnect()
            self.formatter.print_message("MCU disconnected successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to disconnect MCU: {str(e)}", message_type="error"
            )
            return False

    async def show_control_menu(self) -> Optional[str]:
        """Show enhanced MCU control menu with status information"""

        # Get current status information
        try:
            is_connected = await self.mcu_service.is_connected()
            connection_status = "🟢 Connected" if is_connected else "🔴 Disconnected"

            if is_connected:
                try:
                    # Get MCU status information
                    temperature = await self.mcu_service.get_temperature()
                    temp_info = f"🌡️ {temperature:.1f}°C"

                    # Get test mode status (if available)
                    status = await self.mcu_service.get_status()
                    test_mode = status.get("test_mode", "Normal")
                    mode_info = f"🧪 {test_mode} Mode"
                except Exception:
                    temp_info = "🌡️ --.-°C"
                    mode_info = "🧪 Unknown Mode"
            else:
                temp_info = "🌡️ --.-°C"
                mode_info = "🧪 Unknown Mode"

        except Exception:
            connection_status = "❓ Unknown"
            temp_info = "🌡️ --.-°C"
            mode_info = "🧪 Unknown Mode"

        # Enhanced menu options with icons and status
        menu_options = {
            "1": "📊 Show Status",
            "2": "🔌 Connect",
            "3": "❌ Disconnect",
            "4": f"🌡️ Get Temperature     [{temp_info}]",
            "5": f"🧪 Enter Test Mode     [{mode_info}]",
            "6": f"🎛️ Set Operating Temp  [{temp_info}]",
            "b": "⬅️  Back to Hardware Menu",
            # Shortcuts
            "s": "📊 Show Status (shortcut)",
            "c": "🔌 Connect (shortcut)",
            "d": "❌ Disconnect (shortcut)",
            "temp": "🌡️ Get Temperature (shortcut)",
            "test": "🧪 Enter Test Mode (shortcut)",
            "set": "🎛️ Set Operating Temp (shortcut)",
        }

        # Create enhanced title with status
        enhanced_title = (
            f"⚙️ MCU Control System\n"
            f"📡 Status: {connection_status}  |  {temp_info}  |  {mode_info}\n"
            f"[dim]💡 Shortcuts: s=status, c=connect, d=disconnect, temp=temperature, test=testmode[/dim]"
        )

        return simple_interactive_menu(
            self.formatter.console,
            menu_options,
            enhanced_title,
            "Select MCU operation (number or shortcut)",
        )

    async def execute_command(self, command: str) -> bool:
        """Execute MCU command with support for shortcuts"""
        try:
            # Normalize command input
            cmd = command.strip().lower()

            if cmd == "1" or cmd == "s":
                await self.show_status()
            elif cmd == "2" or cmd == "c":
                return await self.connect()
            elif cmd == "3" or cmd == "d":
                return await self.disconnect()
            elif cmd == "4" or cmd == "temp":
                await self._get_temperature()
            elif cmd == "5" or cmd == "test":
                await self._enter_test_mode()
            elif cmd == "6" or cmd == "set":
                await self._set_operating_temperature()
            else:
                return False
            return True

        except Exception as e:
            self.formatter.print_message(f"❌ MCU command failed: {str(e)}", message_type="error")
            return False

    async def _get_temperature(self) -> None:
        """Get current temperature"""
        try:
            temperature = await self.mcu_service.get_temperature()
            self.formatter.print_message(
                f"Current temperature: {temperature:.2f}°C",
                message_type="info",
                title="Temperature Reading",
            )

        except Exception as e:
            self.formatter.print_message(
                f"Failed to get temperature: {str(e)}", message_type="error"
            )

    async def _enter_test_mode(self) -> None:
        """Enter test mode"""
        try:
            await self.mcu_service.set_test_mode(TestMode.MODE_1)
            self.formatter.print_message("Entered test mode successfully", message_type="success")

        except Exception as e:
            self.formatter.print_message(
                f"Failed to enter test mode: {str(e)}", message_type="error"
            )

    async def _set_operating_temperature(self) -> None:
        """Set operating temperature"""
        try:
            # Get temperature from user
            self.formatter.console.print("[bold cyan]Enter operating temperature (°C):[/bold cyan]")
            temp_input = input("  → ").strip()

            if not temp_input:
                self.formatter.print_message("Temperature input required", message_type="warning")
                return

            temperature = float(temp_input)
            await self.mcu_service.set_temperature(temperature)

            self.formatter.print_message(
                f"Operating temperature set to {temperature:.2f}°C", message_type="success"
            )

        except ValueError:
            self.formatter.print_message("Invalid temperature value", message_type="error")
        except Exception as e:
            self.formatter.print_message(
                f"Failed to set operating temperature: {str(e)}", message_type="error"
            )


class LoadCellController(HardwareController):
    """Controller for LoadCell hardware"""

    def __init__(self, loadcell_service: LoadCellService, formatter: RichFormatter):
        super().__init__(formatter)
        self.loadcell_service = loadcell_service
        self.name = "LoadCell Control System"

    async def show_status(self) -> None:
        """Display LoadCell status"""
        try:
            is_connected = await self.loadcell_service.is_connected()

            status_details = {
                "Connection": "Connected" if is_connected else "Disconnected",
                "Type": "BS205 Force Measurement",
            }

            if is_connected:
                try:
                    # Get force reading if connected
                    force = await self.loadcell_service.read_force()
                    status_details["Current Force"] = f"{force:.3f} {force.unit}"
                    status_details["Status"] = "Ready"
                except Exception as e:
                    status_details["Status Error"] = str(e)

            self.formatter.print_status(
                "LoadCell Hardware Status",
                "CONNECTED" if is_connected else "DISCONNECTED",
                details=status_details,
            )

        except Exception as e:
            self.formatter.print_message(
                f"Failed to get LoadCell status: {str(e)}", message_type="error"
            )

    async def connect(self) -> bool:
        """Connect to LoadCell"""
        try:
            with self.formatter.create_progress_display(
                "Connecting to LoadCell...", show_spinner=True
            ) as progress_display:
                await asyncio.sleep(0.5)  # Show spinner for visibility
                await self.loadcell_service.connect(
                    port="/dev/ttyUSB0",
                    baudrate=9600,
                    timeout=1.0,
                    bytesize=8,
                    stopbits=1,
                    parity=None,
                    indicator_id=1,
                )
                if isinstance(progress_display, Status):
                    progress_display.update("LoadCell connected successfully")
                    await asyncio.sleep(0.3)  # Show success message briefly

            self.formatter.print_message("LoadCell connected successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to connect to LoadCell: {str(e)}", message_type="error"
            )
            return False

    async def disconnect(self) -> bool:
        """Disconnect from LoadCell"""
        try:
            await self.loadcell_service.disconnect()
            self.formatter.print_message(
                "LoadCell disconnected successfully", message_type="success"
            )
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to disconnect LoadCell: {str(e)}", message_type="error"
            )
            return False

    async def show_control_menu(self) -> Optional[str]:
        """Show enhanced LoadCell control menu with status information"""

        # Get current status information
        try:
            is_connected = await self.loadcell_service.is_connected()
            connection_status = "🟢 Connected" if is_connected else "🔴 Disconnected"

            if is_connected:
                try:
                    # Get current force reading
                    force_value = await self.loadcell_service.read_force()
                    force_info = f"⚖️ {force_value.value:.3f} {force_value.unit.value}"

                    # Get status information
                    status = await self.loadcell_service.get_status()
                    hardware_type = status.get("hardware_type", "Unknown")
                    device_info = f"📱 {hardware_type}"
                except Exception:
                    force_info = "⚖️ ---.--- kgf"
                    device_info = "📱 Unknown"
            else:
                force_info = "⚖️ ---.--- kgf"
                device_info = "📱 Unknown"

        except Exception:
            connection_status = "❓ Unknown"
            force_info = "⚖️ ---.--- kgf"
            device_info = "📱 Unknown"

        # Enhanced menu options with icons and status
        menu_options = {
            "1": "📊 Show Status",
            "2": "🔌 Connect",
            "3": "❌ Disconnect",
            "4": f"⚖️ Read Force          [{force_info}]",
            "5": "🎌 Zero Calibration    [Reset to 0.000]",
            "6": f"📊 Monitor Force (Live) [{force_info}]",
            "b": "⬅️  Back to Hardware Menu",
            # Shortcuts
            "s": "📊 Show Status (shortcut)",
            "c": "🔌 Connect (shortcut)",
            "d": "❌ Disconnect (shortcut)",
            "read": "⚖️ Read Force (shortcut)",
            "zero": "🎌 Zero Calibration (shortcut)",
            "live": "📊 Monitor Force Live (shortcut)",
        }

        # Create enhanced title with status
        enhanced_title = (
            f"⚖️ LoadCell Control System\n"
            f"📡 Status: {connection_status}  |  {force_info}  |  {device_info}\n"
            f"[dim]💡 Shortcuts: s=status, c=connect, d=disconnect, read=force, zero=calibrate, live=monitor[/dim]"
        )

        return simple_interactive_menu(
            self.formatter.console,
            menu_options,
            enhanced_title,
            "Select LoadCell operation (number or shortcut)",
        )

    async def execute_command(self, command: str) -> bool:
        """Execute LoadCell command with support for shortcuts"""
        try:
            # Normalize command input
            cmd = command.strip().lower()

            if cmd == "1" or cmd == "s":
                await self.show_status()
            elif cmd == "2" or cmd == "c":
                return await self.connect()
            elif cmd == "3" or cmd == "d":
                return await self.disconnect()
            elif cmd == "4" or cmd == "read":
                await self._read_force()
            elif cmd == "5" or cmd == "zero":
                await self._zero_calibration()
            elif cmd == "6" or cmd == "live":
                await self._monitor_force()
            else:
                return False
            return True

        except Exception as e:
            self.formatter.print_message(
                f"❌ LoadCell command failed: {str(e)}", message_type="error"
            )
            return False

    async def _read_force(self) -> None:
        """Read current force"""
        try:
            force = await self.loadcell_service.read_force()
            self.formatter.print_message(
                f"Current force reading: {force:.3f} {force.unit}",
                message_type="info",
                title="Force Reading",
            )

        except Exception as e:
            self.formatter.print_message(f"Failed to read force: {str(e)}", message_type="error")

    async def _zero_calibration(self) -> None:
        """Perform zero calibration"""
        try:
            with self.formatter.create_progress_display(
                "Performing zero calibration...", show_spinner=True
            ) as progress_display:
                await asyncio.sleep(0.8)  # Show spinner longer for calibration
                await self.loadcell_service.zero_calibration()
                if isinstance(progress_display, Status):
                    progress_display.update("Zero calibration complete")
                    await asyncio.sleep(0.3)  # Show success message briefly

            self.formatter.print_message(
                "Zero calibration completed successfully", message_type="success"
            )

        except Exception as e:
            self.formatter.print_message(f"Zero calibration failed: {str(e)}", message_type="error")

    async def _monitor_force(self) -> None:
        """Monitor force readings in real-time"""
        try:
            self.formatter.print_message(
                "Starting force monitoring. Press Ctrl+C to stop.",
                message_type="info",
                title="Force Monitor",
            )

            # Create live display for force monitoring
            self.formatter.print_message(
                "Starting live force monitoring (Ctrl+C to stop)...", "info"
            )

            try:
                while True:
                    force = await self.loadcell_service.read_force()
                    self.formatter.print_message(
                        f"Force: {force:.3f} {force.unit}", message_type="info"
                    )
                    await asyncio.sleep(0.5)

            except KeyboardInterrupt:
                self.formatter.print_message("Force monitoring stopped", message_type="info")

        except Exception as e:
            self.formatter.print_message(f"Force monitoring failed: {str(e)}", message_type="error")


class PowerController(HardwareController):
    """Controller for Power hardware"""

    def __init__(self, power_service: PowerService, formatter: RichFormatter):
        super().__init__(formatter)
        self.power_service = power_service
        self.name = "Power Control System"

    async def show_status(self) -> None:
        """Display Power status"""
        try:
            is_connected = await self.power_service.is_connected()

            status_details = {
                "Connection": "Connected" if is_connected else "Disconnected",
                "Type": "ODA Power Supply",
            }

            if is_connected:
                try:
                    # Get power readings if connected
                    voltage = await self.power_service.get_voltage()
                    current = await self.power_service.get_current()
                    is_output_on = await self.power_service.is_output_enabled()

                    status_details["Voltage"] = f"{voltage:.2f}V"
                    status_details["Current"] = f"{current:.2f}A"
                    status_details["Output"] = "ON" if is_output_on else "OFF"
                except Exception as e:
                    status_details["Status Error"] = str(e)

            self.formatter.print_status(
                "Power Hardware Status",
                "CONNECTED" if is_connected else "DISCONNECTED",
                details=status_details,
            )

        except Exception as e:
            self.formatter.print_message(
                f"Failed to get Power status: {str(e)}", message_type="error"
            )

    async def connect(self) -> bool:
        """Connect to Power supply"""
        try:
            with self.formatter.create_progress_display(
                "Connecting to Power supply...", show_spinner=True
            ) as progress_display:
                await asyncio.sleep(0.5)  # Show spinner for visibility
                await self.power_service.connect(
                    host="192.168.1.100", port=5025, timeout=5.0, channel=1
                )
                if isinstance(progress_display, Status):
                    progress_display.update("Power supply connected successfully")
                    await asyncio.sleep(0.3)  # Show success message briefly

            # Get and display device identity if available
            device_identity = None
            if hasattr(self.power_service, "get_device_identity"):
                try:
                    device_identity = await self.power_service.get_device_identity()
                except Exception:
                    pass  # Ignore errors getting device identity

            if device_identity:
                self.formatter.print_message(
                    "Power supply connected successfully", message_type="success"
                )
                self.formatter.print_message(
                    f"Device Identity: {device_identity}", message_type="info"
                )
            else:
                self.formatter.print_message(
                    "Power supply connected successfully", message_type="success"
                )
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to connect to Power supply: {str(e)}", message_type="error"
            )
            return False

    async def disconnect(self) -> bool:
        """Disconnect from Power supply"""
        try:
            await self.power_service.disconnect()
            self.formatter.print_message(
                "Power supply disconnected successfully", message_type="success"
            )
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to disconnect Power supply: {str(e)}", message_type="error"
            )
            return False

    async def show_control_menu(self) -> Optional[str]:
        """Show enhanced Power control menu with status information"""

        # Get current status information
        try:
            is_connected = await self.power_service.is_connected()
            connection_status = "🟢 Connected" if is_connected else "🔴 Disconnected"

            if is_connected:
                try:
                    # Get current settings and output status
                    voltage = await self.power_service.get_voltage()
                    current = await self.power_service.get_current()
                    is_output_on = await self.power_service.is_output_enabled()
                    output_status = "🟢 ON" if is_output_on else "🔴 OFF"

                    voltage_info = f"⚡ {voltage:.2f}V"
                    current_info = f"🔌 {current:.2f}A"
                except Exception:
                    voltage_info = "⚡ --.-V"
                    current_info = "🔌 --.-A"
                    output_status = "❓ Unknown"
            else:
                voltage_info = "⚡ --.-V"
                current_info = "🔌 --.-A"
                output_status = "🔴 OFF"

        except Exception:
            connection_status = "❓ Unknown"
            voltage_info = "⚡ --.-V"
            current_info = "🔌 --.-A"
            output_status = "❓ Unknown"

        # Enhanced menu options with icons and grouping
        menu_options = {
            "1": "📊 Show Status",
            "2": "🔌 Connect",
            "3": "❌ Disconnect",
            "4": f"✅ Enable Output      ⚠️  [Current: {output_status}]",
            "5": f"🛑 Disable Output     [Current: {output_status}]",
            "6": f"⚡ Set Voltage        [{voltage_info}]",
            "7": f"🔋 Set Current        [{current_info}]",
            "8": f"🔌 Set Current Limit  [{current_info}]",
            "b": "⬅️  Back to Hardware Menu",
            # Additional shortcuts
            "s": "📊 Show Status (shortcut)",
            "c": "🔌 Connect (shortcut)",
            "d": "❌ Disconnect (shortcut)",
            "on": "✅ Enable Output (shortcut)",
            "off": "🛑 Disable Output (shortcut)",
            "v": "⚡ Set Voltage (shortcut)",
            "curr": "🔋 Set Current (shortcut)",
            "i": "🔌 Set Current Limit (shortcut)",
        }

        # Create enhanced title with status and shortcuts info
        enhanced_title = (
            f"🔋 ODA Power Supply Control\n"
            f"📡 Status: {connection_status}  |  🔌 Output: {output_status}  |  ⚡ {voltage_info}  |  🔌 {current_info}\n"
            f"[dim]💡 Shortcuts: s=status, c=connect, d=disconnect, on=enable, off=disable, v=voltage, curr=current, i=current-limit[/dim]"
        )

        return simple_interactive_menu(
            self.formatter.console,
            menu_options,
            enhanced_title,
            "Select Power operation (number or shortcut)",
        )

    async def execute_command(self, command: str) -> bool:
        """Execute Power command with support for shortcuts"""
        try:
            # Normalize command input
            cmd = command.strip().lower()

            # Number-based commands (original)
            if cmd == "1" or cmd == "s":
                await self.show_status()
            elif cmd == "2" or cmd == "c":
                return await self.connect()
            elif cmd == "3" or cmd == "d":
                return await self.disconnect()
            elif cmd == "4" or cmd == "on":
                await self._enable_output()
            elif cmd == "5" or cmd == "off":
                await self._disable_output()
            elif cmd == "6" or cmd == "v":
                await self._set_voltage()
            elif cmd == "7" or cmd == "curr":
                await self._set_current()
            elif cmd == "8" or cmd == "i":
                await self._set_current_limit()
            else:
                return False
            return True

        except Exception as e:
            self.formatter.print_message(f"❌ Power command failed: {str(e)}", message_type="error")
            return False

    async def _enable_output(self) -> None:
        """Enable power output with safety confirmation"""
        try:
            # Get current voltage for safety warning
            try:
                voltage = await self.power_service.get_voltage()
                current = await self.power_service.get_current()

                # Show safety warning with current settings
                self.formatter.print_message(
                    f"⚠️  WARNING: About to enable HIGH VOLTAGE output!\n"
                    f"   Current settings: ⚡ {voltage:.2f}V, 🔌 {current:.2f}A\n"
                    f"   Ensure all safety precautions are in place.",
                    message_type="warning",
                )

                # Ask for confirmation
                confirm = (
                    input("\n🔴 Are you sure you want to enable output? (yes/no): ").strip().lower()
                )

                if confirm not in ["yes", "y"]:
                    self.formatter.print_message(
                        "❌ Output enable cancelled by user", message_type="info"
                    )
                    return

            except Exception:
                # If we can't get voltage/current, still ask for confirmation
                self.formatter.print_message(
                    "⚠️  WARNING: About to enable power output!\n"
                    "   Ensure all safety precautions are in place.",
                    message_type="warning",
                )

                confirm = (
                    input("\n🔴 Are you sure you want to enable output? (yes/no): ").strip().lower()
                )

                if confirm not in ["yes", "y"]:
                    self.formatter.print_message(
                        "❌ Output enable cancelled by user", message_type="info"
                    )
                    return

            # Proceed with enabling output
            await self.power_service.enable_output()
            self.formatter.print_message(
                "✅ Power output enabled successfully", message_type="success"
            )

        except Exception as e:
            self.formatter.print_message(
                f"❌ Failed to enable output: {str(e)}", message_type="error"
            )

    async def _disable_output(self) -> None:
        """Disable power output"""
        try:
            await self.power_service.disable_output()
            self.formatter.print_message(
                "Power output disabled", message_type="warning", title="Output Disabled"
            )

        except Exception as e:
            self.formatter.print_message(
                f"Failed to disable output: {str(e)}", message_type="error"
            )

    async def _set_voltage(self) -> None:
        """Set output voltage with enhanced UX"""
        try:
            # Get current voltage for reference
            try:
                current_voltage = await self.power_service.get_voltage()
                current_info = f"⚡ Current: {current_voltage:.2f}V"
            except Exception:
                current_info = "⚡ Current: Unknown"

            # Enhanced voltage input prompt
            self.formatter.console.print("[bold cyan]⚡ Set Output Voltage[/bold cyan]")
            self.formatter.console.print(f"[dim]   {current_info}[/dim]")
            self.formatter.console.print(
                "[yellow]   Enter new voltage (V) or 'cancel' to abort:[/yellow]"
            )

            voltage_input = input("  → ").strip()

            if not voltage_input or voltage_input.lower() == "cancel":
                self.formatter.print_message("❌ Voltage setting cancelled", message_type="info")
                return

            voltage = float(voltage_input)

            # Show what will be set
            self.formatter.print_message(
                f"⚡ Setting voltage: {current_voltage:.2f}V → {voltage:.2f}V", message_type="info"
            )

            await self.power_service.set_voltage(voltage)

            # Read back the actual voltage set by the device
            try:
                actual_voltage = await self.power_service.get_voltage()
                self.formatter.print_message(
                    f"✅ Voltage set successfully - Actual: {actual_voltage:.2f}V",
                    message_type="success",
                )
            except Exception:
                self.formatter.print_message(
                    f"✅ Voltage set to {voltage:.2f}V successfully", message_type="success"
                )

        except ValueError:
            self.formatter.print_message(
                "❌ Invalid voltage value - please enter a number", message_type="error"
            )
        except Exception as e:
            self.formatter.print_message(
                f"❌ Failed to set voltage: {str(e)}", message_type="error"
            )

    async def _set_current(self) -> None:
        """Set output current with enhanced UX"""
        try:
            # Get current value for reference
            try:
                current_value = await self.power_service.get_current()
                current_info = f"🔋 Current: {current_value:.2f}A"
            except Exception:
                current_info = "🔋 Current: Unknown"

            # Enhanced current input prompt
            self.formatter.console.print("[bold cyan]🔋 Set Output Current[/bold cyan]")
            self.formatter.console.print(f"[dim]   {current_info}[/dim]")
            self.formatter.console.print(
                "[yellow]   Enter new current (A) or 'cancel' to abort:[/yellow]"
            )

            current_input = input("  → ").strip()

            if not current_input or current_input.lower() == "cancel":
                self.formatter.print_message("❌ Current setting cancelled", message_type="info")
                return

            current = float(current_input)

            # Show what will be set
            try:
                self.formatter.print_message(
                    f"🔋 Setting current: {current_value:.2f}A → {current:.2f}A",
                    message_type="info",
                )
            except Exception:
                self.formatter.print_message(
                    f"🔋 Setting current to {current:.2f}A", message_type="info"
                )

            await self.power_service.set_current(current)

            # Read back the actual current set by the device
            try:
                actual_current = await self.power_service.get_current()
                self.formatter.print_message(
                    f"✅ Current set successfully - Actual: {actual_current:.2f}A",
                    message_type="success",
                )
            except Exception:
                self.formatter.print_message(
                    f"✅ Current set to {current:.2f}A successfully", message_type="success"
                )

        except ValueError:
            self.formatter.print_message(
                "❌ Invalid current value - please enter a number", message_type="error"
            )
        except Exception as e:
            self.formatter.print_message(
                f"❌ Failed to set current: {str(e)}", message_type="error"
            )

    async def _set_current_limit(self) -> None:
        """Set current limit with enhanced UX"""
        try:
            # Get current limit for reference
            try:
                current_limit = await self.power_service.get_current_limit()
                current_info = f"🔌 Current Limit: {current_limit:.2f}A"
            except Exception:
                current_info = "🔌 Current Limit: Unknown"

            # Enhanced current input prompt
            self.formatter.console.print("[bold cyan]🔌 Set Current Limit[/bold cyan]")
            self.formatter.console.print(f"[dim]   {current_info}[/dim]")
            self.formatter.console.print(
                "[yellow]   Enter new current limit (A) or 'cancel' to abort:[/yellow]"
            )

            current_input = input("  → ").strip()

            if not current_input or current_input.lower() == "cancel":
                self.formatter.print_message(
                    "❌ Current limit setting cancelled", message_type="info"
                )
                return

            current = float(current_input)

            # Show what will be set
            try:
                self.formatter.print_message(
                    f"🔌 Setting current limit: {current_limit:.2f}A → {current:.2f}A",
                    message_type="info",
                )
            except Exception:
                self.formatter.print_message(
                    f"🔌 Setting current limit to {current:.2f}A", message_type="info"
                )

            await self.power_service.set_current_limit(current)

            # Read back the actual current limit set by the device
            try:
                actual_limit = await self.power_service.get_current_limit()
                self.formatter.print_message(
                    f"✅ Current limit set successfully - Actual: {actual_limit:.2f}A",
                    message_type="success",
                )
            except Exception:
                self.formatter.print_message(
                    f"✅ Current limit set to {current:.2f}A successfully", message_type="success"
                )

        except ValueError:
            self.formatter.print_message(
                "❌ Invalid current value - please enter a number", message_type="error"
            )
        except Exception as e:
            self.formatter.print_message(
                f"❌ Failed to set current limit: {str(e)}", message_type="error"
            )


class HardwareControlManager:
    """Manages individual hardware control with Rich UI"""

    def __init__(
        self,
        hardware_facade: HardwareServiceFacade,
        console: Optional[Console] = None,
        configuration_service: Optional[ConfigurationService] = None,
    ):
        self.console = console or Console()
        self.formatter = RichFormatter(self.console)
        self.configuration_service = configuration_service
        # self.ui_manager = RichUIManager(self.console)  # Removed

        # Load hardware configuration to get axis_id
        self.axis_id = self._load_robot_axis_id()

        # Initialize hardware controllers
        self.controllers = {
            "Robot": RobotController(hardware_facade._robot, self.formatter, self.axis_id),
            "MCU": MCUController(hardware_facade._mcu, self.formatter),
            "LoadCell": LoadCellController(hardware_facade._loadcell, self.formatter),
            "Power": PowerController(hardware_facade._power, self.formatter),
        }

        logger.info(f"Initialized {len(self.controllers)} hardware controllers")

    def _load_robot_axis_id(self) -> int:
        """Load robot axis_id from hardware configuration"""
        try:
            if self.configuration_service:
                import asyncio

                # Get the current event loop or create a new one
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context but need to run sync
                        # This is a limitation - we'll use a default and log a warning
                        logger.warning(
                            "Cannot load hardware config in running event loop, using default axis_id=0"
                        )
                        return 0
                    else:
                        hw_config = loop.run_until_complete(
                            self.configuration_service.load_hardware_config()
                        )
                        return hw_config.robot.axis_id
                except RuntimeError:
                    # No event loop running, create one
                    hw_config = asyncio.run(self.configuration_service.load_hardware_config())
                    return hw_config.robot.axis_id
            else:
                logger.warning("No configuration service available, using default axis_id=0")
                return 0
        except Exception as e:
            logger.error(f"Failed to load robot axis_id from configuration: {e}")
            logger.info("Using default axis_id=0")
            return 0

    async def show_hardware_menu(self) -> Optional[str]:
        """Display hardware selection menu"""
        menu_options = {
            "1": "Robot Control",
            "2": "MCU Control",
            "3": "LoadCell Control",
            "4": "Power Control",
            "5": "All Hardware Status",
            "b": "Back to Main Menu",
        }

        return simple_interactive_menu(
            self.console, menu_options, "Hardware Control Center", "Select hardware to control"
        )

    async def execute_hardware_control(self, selection: str) -> None:
        """Execute hardware control based on selection"""
        if selection == "b":
            return

        if selection == "5":
            await self._show_all_hardware_status()
            return

        # Map selection to controller
        controller_map = {"1": "Robot", "2": "MCU", "3": "LoadCell", "4": "Power"}

        controller_name = controller_map.get(selection)
        if not controller_name:
            self.formatter.print_message("Invalid selection", message_type="warning")
            return

        controller = self.controllers[controller_name]
        await self._run_hardware_controller(controller)

    async def _run_hardware_controller(self, controller: HardwareController) -> None:
        """Run hardware controller loop"""
        self.formatter.print_header(
            getattr(controller, "name", "Hardware"),
            f"Individual control for {getattr(controller, 'name', 'Hardware').split()[0]} hardware",
        )

        while True:
            try:
                selection = await controller.show_control_menu()
                if not selection or selection == "b":
                    break

                await controller.execute_command(selection)
                # All operations return to menu immediately - no pauses

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                self.formatter.print_message(
                    f"Hardware control error: {str(e)}", message_type="error"
                )
                logger.error(f"Hardware control error: {e}")

    async def _show_all_hardware_status(self) -> None:
        """Show status of all hardware components"""
        self.formatter.print_header("All Hardware Status", "Overview of all hardware components")

        for name, controller in self.controllers.items():
            try:
                await controller.show_status()
                self.formatter.console.print("")  # Add spacing
            except Exception as e:
                self.formatter.print_message(
                    f"Failed to get {name} status: {str(e)}", message_type="error"
                )

    def get_controller(self, name: str) -> Optional[HardwareController]:
        """Get specific hardware controller by name"""
        return self.controllers.get(name)

    def list_controllers(self) -> List[str]:
        """Get list of available controller names"""
        return list(self.controllers.keys())
