"""
Hardware Control Manager

Provides individual hardware control capabilities with Rich UI integration.
Allows direct control and monitoring of individual hardware components.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional

from loguru import logger
from rich.console import Console
from rich.progress import Progress
from rich.status import Status

from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.mcu import MCUService
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.robot import RobotService
from application.services.hardware_service_facade import HardwareServiceFacade
from domain.enums.mcu_enums import TestMode

from .rich_formatter import RichFormatter
from .rich_utils import RichUIManager


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

    def __init__(self, robot_service: RobotService, formatter: RichFormatter):
        super().__init__(formatter)
        self.robot_service = robot_service
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
                await self.robot_service.connect()
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

        # Enhanced menu options with icons and status
        menu_options = {
            "1": "📊 Show Status",
            "2": "🔌 Connect",
            "3": "❌ Disconnect",
            "4": f"⚙️ Initialize Robot    [Status: {init_status}]",
            "5": f"🚨 Emergency Stop      ⚠️  [Safety Critical]",
            "b": "⬅️  Back to Hardware Menu",
            # Shortcuts
            "s": "📊 Show Status (shortcut)",
            "c": "🔌 Connect (shortcut)",
            "d": "❌ Disconnect (shortcut)",
            "init": "⚙️ Initialize Robot (shortcut)",
            "stop": "🚨 Emergency Stop (shortcut)",
        }

        # Create enhanced title with status
        enhanced_title = (
            f"🤖 Robot Control System\n"
            f"📡 Status: {connection_status}  |  ⚙️ Init: {init_status}  |  {position_info}\n"
            f"[dim]💡 Shortcuts: s=status, c=connect, d=disconnect, init=initialize, stop=emergency[/dim]"
        )

        ui_manager = RichUIManager(self.formatter.console)
        return ui_manager.create_interactive_menu(
            menu_options, 
            title=enhanced_title, 
            prompt="Select Robot operation (number or shortcut)"
        )

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
                # Home primary axis using parameters from .mot file
                primary_axis = await self.robot_service.get_primary_axis_id()
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
            await self.robot_service.emergency_stop()
            self.formatter.print_message(
                "Emergency stop executed", message_type="warning", title="Emergency Stop"
            )

        except Exception as e:
            self.formatter.print_message(f"Emergency stop failed: {str(e)}", message_type="error")


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
                await self.mcu_service.connect()
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

        ui_manager = RichUIManager(self.formatter.console)
        return ui_manager.create_interactive_menu(
            menu_options, 
            title=enhanced_title, 
            prompt="Select MCU operation (number or shortcut)"
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
                await self.loadcell_service.connect()
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
            "5": f"🎌 Zero Calibration    [Reset to 0.000]",
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

        ui_manager = RichUIManager(self.formatter.console)
        return ui_manager.create_interactive_menu(
            menu_options, 
            title=enhanced_title, 
            prompt="Select LoadCell operation (number or shortcut)"
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
            self.formatter.print_message(f"❌ LoadCell command failed: {str(e)}", message_type="error")
            return False

    async def _read_force(self) -> None:
        """Read current force"""
        try:
            force = await self.loadcell_service.read_force()
            self.formatter.print_message(
                f"Current force reading: {force:.3f} {force.unit}", message_type="info", title="Force Reading"
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
            ui_manager = RichUIManager(self.formatter.console)

            initial_force = await self.loadcell_service.read_force()
            initial_panel = self.formatter.create_message_panel(
                f"Force: {initial_force:.3f} {initial_force.unit}", message_type="info", title="🔧 Live Force Reading"
            )

            with ui_manager.live_display(initial_panel, refresh_per_second=2) as live:
                try:
                    while True:
                        force = await self.loadcell_service.read_force()
                        force_panel = self.formatter.create_message_panel(
                            f"Force: {force:.3f} {force.unit}",
                            message_type="info",
                            title="🔧 Live Force Reading",
                        )
                        live.update(force_panel)
                        await asyncio.sleep(0.5)

                except KeyboardInterrupt:
                    pass

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
                await self.power_service.connect()
                if isinstance(progress_display, Status):
                    progress_display.update("Power supply connected successfully")
                    await asyncio.sleep(0.3)  # Show success message briefly

            # Get and display device identity if available
            device_identity = None
            if hasattr(self.power_service, 'get_device_identity'):
                try:
                    device_identity = await self.power_service.get_device_identity()
                except Exception:
                    pass  # Ignore errors getting device identity

            if device_identity:
                self.formatter.print_message(
                    f"Power supply connected successfully", message_type="success"
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
            "1": f"📊 Show Status",
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

        ui_manager = RichUIManager(self.formatter.console)
        return ui_manager.create_interactive_menu(
            menu_options, 
            title=enhanced_title, 
            prompt="Select Power operation (number or shortcut)"
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
                    message_type="warning"
                )
                
                # Ask for confirmation
                confirm = input("\n🔴 Are you sure you want to enable output? (yes/no): ").strip().lower()
                
                if confirm not in ['yes', 'y']:
                    self.formatter.print_message("❌ Output enable cancelled by user", message_type="info")
                    return
                    
            except Exception:
                # If we can't get voltage/current, still ask for confirmation
                self.formatter.print_message(
                    f"⚠️  WARNING: About to enable power output!\n"
                    f"   Ensure all safety precautions are in place.",
                    message_type="warning"
                )
                
                confirm = input("\n🔴 Are you sure you want to enable output? (yes/no): ").strip().lower()
                
                if confirm not in ['yes', 'y']:
                    self.formatter.print_message("❌ Output enable cancelled by user", message_type="info")
                    return

            # Proceed with enabling output
            await self.power_service.enable_output()
            self.formatter.print_message("✅ Power output enabled successfully", message_type="success")

        except Exception as e:
            self.formatter.print_message(f"❌ Failed to enable output: {str(e)}", message_type="error")

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
            self.formatter.console.print(f"[bold cyan]⚡ Set Output Voltage[/bold cyan]")
            self.formatter.console.print(f"[dim]   {current_info}[/dim]")
            self.formatter.console.print(f"[yellow]   Enter new voltage (V) or 'cancel' to abort:[/yellow]")
            
            voltage_input = input("  → ").strip()

            if not voltage_input or voltage_input.lower() == 'cancel':
                self.formatter.print_message("❌ Voltage setting cancelled", message_type="info")
                return

            voltage = float(voltage_input)
            
            # Show what will be set
            self.formatter.print_message(
                f"⚡ Setting voltage: {current_voltage:.2f}V → {voltage:.2f}V",
                message_type="info"
            )
            
            await self.power_service.set_voltage(voltage)

            # Read back the actual voltage set by the device
            try:
                actual_voltage = await self.power_service.get_voltage()
                self.formatter.print_message(
                    f"✅ Voltage set successfully - Actual: {actual_voltage:.2f}V", 
                    message_type="success"
                )
            except Exception:
                self.formatter.print_message(f"✅ Voltage set to {voltage:.2f}V successfully", message_type="success")

        except ValueError:
            self.formatter.print_message("❌ Invalid voltage value - please enter a number", message_type="error")
        except Exception as e:
            self.formatter.print_message(f"❌ Failed to set voltage: {str(e)}", message_type="error")

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
            self.formatter.console.print(f"[bold cyan]🔋 Set Output Current[/bold cyan]")
            self.formatter.console.print(f"[dim]   {current_info}[/dim]")
            self.formatter.console.print(f"[yellow]   Enter new current (A) or 'cancel' to abort:[/yellow]")
            
            current_input = input("  → ").strip()

            if not current_input or current_input.lower() == 'cancel':
                self.formatter.print_message("❌ Current setting cancelled", message_type="info")
                return

            current = float(current_input)
            
            # Show what will be set
            try:
                self.formatter.print_message(
                    f"🔋 Setting current: {current_value:.2f}A → {current:.2f}A",
                    message_type="info"
                )
            except:
                self.formatter.print_message(
                    f"🔋 Setting current to {current:.2f}A",
                    message_type="info"
                )
            
            await self.power_service.set_current(current)

            # Read back the actual current set by the device
            try:
                actual_current = await self.power_service.get_current()
                self.formatter.print_message(
                    f"✅ Current set successfully - Actual: {actual_current:.2f}A", 
                    message_type="success"
                )
            except Exception:
                self.formatter.print_message(f"✅ Current set to {current:.2f}A successfully", message_type="success")

        except ValueError:
            self.formatter.print_message("❌ Invalid current value - please enter a number", message_type="error")
        except Exception as e:
            self.formatter.print_message(f"❌ Failed to set current: {str(e)}", message_type="error")

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
            self.formatter.console.print(f"[bold cyan]🔌 Set Current Limit[/bold cyan]")
            self.formatter.console.print(f"[dim]   {current_info}[/dim]")
            self.formatter.console.print(f"[yellow]   Enter new current limit (A) or 'cancel' to abort:[/yellow]")
            
            current_input = input("  → ").strip()

            if not current_input or current_input.lower() == 'cancel':
                self.formatter.print_message("❌ Current limit setting cancelled", message_type="info")
                return

            current = float(current_input)
            
            # Show what will be set
            try:
                self.formatter.print_message(
                    f"🔌 Setting current limit: {current_limit:.2f}A → {current:.2f}A",
                    message_type="info"
                )
            except:
                self.formatter.print_message(
                    f"🔌 Setting current limit to {current:.2f}A",
                    message_type="info"
                )
            
            await self.power_service.set_current_limit(current)

            # Read back the actual current limit set by the device
            try:
                actual_limit = await self.power_service.get_current_limit()
                self.formatter.print_message(
                    f"✅ Current limit set successfully - Actual: {actual_limit:.2f}A", 
                    message_type="success"
                )
            except Exception:
                self.formatter.print_message(
                    f"✅ Current limit set to {current:.2f}A successfully", message_type="success"
                )

        except ValueError:
            self.formatter.print_message("❌ Invalid current value - please enter a number", message_type="error")
        except Exception as e:
            self.formatter.print_message(
                f"❌ Failed to set current limit: {str(e)}", message_type="error"
            )


class HardwareControlManager:
    """Manages individual hardware control with Rich UI"""

    def __init__(self, hardware_facade: HardwareServiceFacade, console: Optional[Console] = None):
        self.console = console or Console()
        self.formatter = RichFormatter(self.console)
        self.ui_manager = RichUIManager(self.console)

        # Initialize hardware controllers
        self.controllers = {
            "Robot": RobotController(hardware_facade._robot, self.formatter),
            "MCU": MCUController(hardware_facade._mcu, self.formatter),
            "LoadCell": LoadCellController(hardware_facade._loadcell, self.formatter),
            "Power": PowerController(hardware_facade._power, self.formatter),
        }

        logger.info(f"Initialized {len(self.controllers)} hardware controllers")

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

        return self.ui_manager.create_interactive_menu(
            menu_options, title="Hardware Control Center", prompt="Select hardware to control"
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

