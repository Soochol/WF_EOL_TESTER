"""
Slash Command Handler for EOL Tester Hardware Control

Comprehensive slash command system that provides powerful hardware control capabilities
through a command-line interface. Supports hardware operations for robot, MCU, loadcell,
and power supply components with Rich-formatted output and comprehensive error handling.

Key Features:
- Command parsing and validation with argument support
- Individual hardware control with standardized interfaces
- Rich-formatted output for status and results
- Error handling with user-friendly messages
- Help system with detailed command documentation
- Support for both interactive and direct execution modes
"""

import asyncio
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.mcu import MCUService, TestMode
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.robot import RobotService

from .config_reader import CLIConfigReader
from .rich_formatter import RichFormatter
from .rich_utils import RichUIManager


class CommandType(Enum):
    """Types of slash commands supported by the system"""

    ROBOT = "/robot"
    MCU = "/mcu"
    LOADCELL = "/loadcell"
    POWER = "/power"
    ALL = "/all"
    HELP = "/help"


@dataclass
class CommandInfo:
    """Information about a parsed command"""

    command_type: CommandType
    subcommand: Optional[str] = None
    arguments: Optional[List[str]] = None
    raw_input: str = ""

    def __post_init__(self):
        if self.arguments is None:
            self.arguments = []


class CommandParser:
    """Parser for slash commands with validation and argument extraction"""

    # Command patterns for validation
    COMMAND_PATTERNS = {
        CommandType.ROBOT: r"^/robot\s+(connect|disconnect|status|init|stop)(?:\s+(.*))?$",
        CommandType.MCU: r"^/mcu\s+(connect|disconnect|status|temp|testmode|fan)(?:\s+(.*))?$",
        CommandType.LOADCELL: (
            r"^/loadcell\s+(connect|disconnect|status|read|zero|monitor)(?:\s+(.*))?$"
        ),
        CommandType.POWER: (
            r"^/power\s+(connect|disconnect|status|on|off|voltage|current)(?:\s+(.*))?$"
        ),
        CommandType.ALL: r"^/all\s+(status)(?:\s+(.*))?$",
        CommandType.HELP: r"^/help(?:\s+(.*))?$",
    }

    # Valid subcommands for each command type
    VALID_SUBCOMMANDS = {
        CommandType.ROBOT: ["connect", "disconnect", "status", "init", "stop"],
        CommandType.MCU: ["connect", "disconnect", "status", "temp", "testmode", "fan"],
        CommandType.LOADCELL: ["connect", "disconnect", "status", "read", "zero", "monitor"],
        CommandType.POWER: ["connect", "disconnect", "status", "on", "off", "voltage", "current"],
        CommandType.ALL: ["status"],
        CommandType.HELP: [],
    }

    def parse_command(self, input_text: str) -> Optional[CommandInfo]:
        """Parse input text into a structured command

        Args:
            input_text: Raw input string from user

        Returns:
            CommandInfo object if parsing successful, None otherwise
        """
        if not input_text or not input_text.strip():
            return None

        input_text = input_text.strip()

        # Try to identify command type
        command_type = self._identify_command_type(input_text)
        if not command_type:
            return None

        # Parse the specific command pattern
        pattern = self.COMMAND_PATTERNS[command_type]
        match = re.match(pattern, input_text, re.IGNORECASE)

        if not match:
            return None

        # Extract subcommand and arguments
        if command_type == CommandType.HELP:
            subcommand = None
            args_str = match.group(1) if match.group(1) else ""
        else:
            subcommand = match.group(1).lower() if match.group(1) else None
            args_str = match.group(2) if len(match.groups()) > 1 and match.group(2) else ""

        # Parse arguments
        arguments = self._parse_arguments(args_str) if args_str else []

        return CommandInfo(
            command_type=command_type,
            subcommand=subcommand,
            arguments=arguments,
            raw_input=input_text,
        )

    def _identify_command_type(self, input_text: str) -> Optional[CommandType]:
        """Identify the command type from input text"""
        input_lower = input_text.lower()

        for cmd_type in CommandType:
            if input_lower.startswith(cmd_type.value):
                return cmd_type

        return None

    def _parse_arguments(self, args_str: str) -> List[str]:
        """Parse argument string into list of arguments"""
        if not args_str:
            return []

        # Simple space-based parsing with quote support
        args = []
        current_arg = ""
        in_quotes = False
        escape_next = False

        for char in args_str:
            if escape_next:
                current_arg += char
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == '"' and not escape_next:
                in_quotes = not in_quotes
            elif char.isspace() and not in_quotes:
                if current_arg:
                    args.append(current_arg)
                    current_arg = ""
            else:
                current_arg += char

        if current_arg:
            args.append(current_arg)

        return args

    def validate_command(self, command_info: CommandInfo) -> bool:
        """Validate that a parsed command is valid

        Args:
            command_info: Parsed command information

        Returns:
            True if command is valid, False otherwise
        """
        if not command_info:
            return False

        # Special case for help command
        if command_info.command_type == CommandType.HELP:
            return True

        # Check if subcommand is valid for the command type
        valid_subs = self.VALID_SUBCOMMANDS.get(command_info.command_type, [])

        if command_info.subcommand not in valid_subs:
            return False

        return True


class HardwareCommandHandler:
    """Base class for hardware-specific command handlers"""

    def __init__(self, formatter: RichFormatter):
        self.formatter = formatter

    async def handle_command(self, command_info: CommandInfo) -> bool:
        """Handle a command for this hardware type

        Args:
            command_info: Parsed command information

        Returns:
            True if command executed successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement handle_command")

    def get_help_info(self) -> Dict[str, str]:
        """Get help information for this hardware type

        Returns:
            Dictionary mapping subcommands to descriptions
        """
        raise NotImplementedError("Subclasses must implement get_help_info")


class RobotCommandHandler(HardwareCommandHandler):
    """Command handler for robot hardware operations"""

    def __init__(self, robot_service: RobotService, formatter: RichFormatter, config_reader: Optional[CLIConfigReader] = None):
        super().__init__(formatter)
        self.robot_service = robot_service
        self.config_reader = config_reader
        self._connection_params = self._get_connection_params()

    async def handle_command(self, command_info: CommandInfo) -> bool:
        """Handle robot commands"""
        try:
            subcommand = command_info.subcommand

            if subcommand == "connect":
                return await self._connect()
            if subcommand == "disconnect":
                return await self._disconnect()
            if subcommand == "status":
                await self._show_status()
                return True
            if subcommand == "init":
                return await self._initialize()
            if subcommand == "stop":
                return await self._emergency_stop()

            self.formatter.print_message(
                f"Unknown robot subcommand: {subcommand}", message_type="error"
            )
            return False

        except Exception as e:
            self.formatter.print_message(f"Robot command failed: {str(e)}", message_type="error")
            logger.error(f"Robot command error: {e}")
            return False

    def _get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters from configuration"""
        if self.config_reader:
            try:
                return self.config_reader.get_connection_params("robot")
            except Exception as e:
                logger.warning(f"Failed to load robot config, using defaults: {e}")
        
        # Fallback to hardcoded defaults
        return {"axis_id": 0, "irq_no": 7}
    
    async def _connect(self) -> bool:
        """Connect to robot"""
        try:
            with self.formatter.create_progress_display("Connecting to robot...") as status:
                await self.robot_service.connect(
                    axis_id=self._connection_params.get("axis_id", 0),
                    irq_no=self._connection_params.get("irq_no", 7)
                )
                if isinstance(status, Status):
                    status.update("Robot connected successfully")

            self.formatter.print_message("Robot connected successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to connect to robot: {str(e)}", message_type="error"
            )
            return False

    async def _disconnect(self) -> bool:
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

    async def _show_status(self) -> None:
        """Show robot status"""
        try:
            is_connected = await self.robot_service.is_connected()

            status_details = {
                "Connection": "Connected" if is_connected else "Disconnected",
                "Type": "AJINEXTEK Motion Controller",
                "Axes": "6 DOF",
            }

            if is_connected:
                try:
                    motion_status = await self.robot_service.get_motion_status()
                    status_details["Motion Status"] = motion_status.value
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

    async def _initialize(self) -> bool:
        """Initialize robot system"""
        try:
            with self.formatter.create_progress_display("Initializing robot...") as status:
                # Home primary axis using parameters from .mot file
                primary_axis = await self.robot_service.get_primary_axis_id()
                await self.robot_service.home_axis(primary_axis)
                if isinstance(status, Status):
                    status.update("Robot initialization complete")

            self.formatter.print_message("Robot initialized successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Robot initialization failed: {str(e)}", message_type="error"
            )
            return False

    async def _emergency_stop(self) -> bool:
        """Execute emergency stop"""
        try:
            # Get primary axis and stop it
            primary_axis = await self.robot_service.get_primary_axis_id()
            await self.robot_service.emergency_stop(primary_axis)
            self.formatter.print_message(
                f"Emergency stop executed for axis {primary_axis}",
                message_type="warning",
                title="Emergency Stop",
            )
            return True

        except Exception as e:
            self.formatter.print_message(f"Emergency stop failed: {str(e)}", message_type="error")
            return False

    def get_help_info(self) -> Dict[str, str]:
        """Get robot command help information"""
        return {
            "connect": "Connect to the robot hardware",
            "disconnect": "Disconnect from the robot hardware",
            "status": "Show robot connection and motion status",
            "init": "Initialize the robot system and axis configuration",
            "stop": "Execute emergency stop for immediate motion halt",
        }


class MCUCommandHandler(HardwareCommandHandler):
    """Command handler for MCU hardware operations"""

    def __init__(self, mcu_service: MCUService, formatter: RichFormatter, config_reader: Optional[CLIConfigReader] = None):
        super().__init__(formatter)
        self.mcu_service = mcu_service
        self.config_reader = config_reader
        self._connection_params = self._get_connection_params()

    async def handle_command(self, command_info: CommandInfo) -> bool:
        """Handle MCU commands"""
        try:
            subcommand = command_info.subcommand

            if subcommand == "connect":
                return await self._connect()
            if subcommand == "disconnect":
                return await self._disconnect()
            if subcommand == "status":
                await self._show_status()
                return True
            if subcommand == "temp":
                if command_info.arguments:
                    return await self._set_temperature(command_info.arguments[0])
                await self._get_temperature()
                return True
            if subcommand == "testmode":
                return await self._enter_test_mode()
            if subcommand == "fan":
                if command_info.arguments:
                    return await self._set_fan_speed(command_info.arguments[0])
                self.formatter.print_message(
                    "Fan speed argument required (0-100)", message_type="warning"
                )
                return False

            self.formatter.print_message(
                f"Unknown MCU subcommand: {subcommand}", message_type="error"
            )
            return False

        except Exception as e:
            self.formatter.print_message(f"MCU command failed: {str(e)}", message_type="error")
            logger.error(f"MCU command error: {e}")
            return False

    def _get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters from configuration"""
        if self.config_reader:
            try:
                return self.config_reader.get_connection_params("mcu")
            except Exception as e:
                logger.warning(f"Failed to load MCU config, using defaults: {e}")
        
        # Fallback to hardcoded defaults
        return {
            "port": "/dev/ttyUSB1",
            "baudrate": 115200,
            "timeout": 2.0,
            "bytesize": 8,
            "stopbits": 1,
            "parity": None
        }
    
    async def _connect(self) -> bool:
        """Connect to MCU"""
        try:
            with self.formatter.create_progress_display("Connecting to MCU...") as status:
                await self.mcu_service.connect(
                    port=self._connection_params.get("port", "/dev/ttyUSB1"),
                    baudrate=self._connection_params.get("baudrate", 115200),
                    timeout=self._connection_params.get("timeout", 2.0),
                    bytesize=self._connection_params.get("bytesize", 8),
                    stopbits=self._connection_params.get("stopbits", 1),
                    parity=self._connection_params.get("parity"),
                )
                if isinstance(status, Status):
                    status.update("MCU connected successfully")

            self.formatter.print_message("MCU connected successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to connect to MCU: {str(e)}", message_type="error"
            )
            return False

    async def _disconnect(self) -> bool:
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

    async def _show_status(self) -> None:
        """Show MCU status"""
        try:
            is_connected = await self.mcu_service.is_connected()

            status_details = {
                "Connection": "Connected" if is_connected else "Disconnected",
                "Type": "LMA Temperature Controller",
            }

            if is_connected:
                try:
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

    async def _set_temperature(self, temp_str: str) -> bool:
        """Set operating temperature"""
        try:
            temperature = float(temp_str)
            await self.mcu_service.set_temperature(temperature)
            self.formatter.print_message(
                f"Operating temperature set to {temperature:.2f}°C", message_type="success"
            )
            return True

        except ValueError:
            self.formatter.print_message(
                f"Invalid temperature value: {temp_str}", message_type="error"
            )
            return False
        except Exception as e:
            self.formatter.print_message(
                f"Failed to set temperature: {str(e)}", message_type="error"
            )
            return False

    async def _enter_test_mode(self) -> bool:
        """Enter test mode"""
        try:
            await self.mcu_service.set_test_mode(TestMode.MODE_1)
            self.formatter.print_message("Entered test mode successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to enter test mode: {str(e)}", message_type="error"
            )
            return False

    async def _set_fan_speed(self, speed_str: str) -> bool:
        """Set fan speed"""
        try:
            speed = float(speed_str)
            if not 0 <= speed <= 100:
                self.formatter.print_message(
                    "Fan speed must be between 0-100%", message_type="error"
                )
                return False

            await self.mcu_service.set_fan_speed(speed)
            self.formatter.print_message(f"Fan speed set to {speed:.1f}%", message_type="success")
            return True

        except ValueError:
            self.formatter.print_message(
                f"Invalid fan speed value: {speed_str}", message_type="error"
            )
            return False
        except Exception as e:
            self.formatter.print_message(f"Failed to set fan speed: {str(e)}", message_type="error")
            return False

    def get_help_info(self) -> Dict[str, str]:
        """Get MCU command help information"""
        return {
            "connect": "Connect to the MCU hardware",
            "disconnect": "Disconnect from the MCU hardware",
            "status": "Show MCU connection and temperature status",
            "temp": "Get current temperature or set temperature with argument (°C)",
            "testmode": "Enter test mode for MCU operations",
            "fan": "Set fan speed with argument (0-100%)",
        }


class LoadCellCommandHandler(HardwareCommandHandler):
    """Command handler for LoadCell hardware operations"""

    def __init__(self, loadcell_service: LoadCellService, formatter: RichFormatter, config_reader: Optional[CLIConfigReader] = None):
        super().__init__(formatter)
        self.loadcell_service = loadcell_service
        self.config_reader = config_reader
        self._connection_params = self._get_connection_params()
        self._monitoring = False

    async def handle_command(self, command_info: CommandInfo) -> bool:
        """Handle LoadCell commands"""
        try:
            subcommand = command_info.subcommand

            if subcommand == "connect":
                return await self._connect()
            if subcommand == "disconnect":
                return await self._disconnect()
            if subcommand == "status":
                await self._show_status()
                return True
            if subcommand == "read":
                await self._read_force()
                return True
            if subcommand == "zero":
                return await self._zero_calibration()
            if subcommand == "monitor":
                await self._monitor_force()
                return True

            self.formatter.print_message(
                f"Unknown LoadCell subcommand: {subcommand}", message_type="error"
            )
            return False

        except Exception as e:
            self.formatter.print_message(f"LoadCell command failed: {str(e)}", message_type="error")
            logger.error(f"LoadCell command error: {e}")
            return False

    def _get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters from configuration"""
        if self.config_reader:
            try:
                return self.config_reader.get_connection_params("loadcell")
            except Exception as e:
                logger.warning(f"Failed to load LoadCell config, using defaults: {e}")
        
        # Fallback to hardcoded defaults
        return {
            "port": "/dev/ttyUSB0",
            "baudrate": 9600,
            "timeout": 1.0,
            "bytesize": 8,
            "stopbits": 1,
            "parity": None,
            "indicator_id": 1
        }
    
    async def _connect(self) -> bool:
        """Connect to LoadCell"""
        try:
            with self.formatter.create_progress_display("Connecting to LoadCell...") as status:
                await self.loadcell_service.connect(
                    port=self._connection_params.get("port", "/dev/ttyUSB0"),
                    baudrate=self._connection_params.get("baudrate", 9600),
                    timeout=self._connection_params.get("timeout", 1.0),
                    bytesize=self._connection_params.get("bytesize", 8),
                    stopbits=self._connection_params.get("stopbits", 1),
                    parity=self._connection_params.get("parity"),
                    indicator_id=self._connection_params.get("indicator_id", 1),
                )
                if isinstance(status, Status):
                    status.update("LoadCell connected successfully")

            self.formatter.print_message("LoadCell connected successfully", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to connect to LoadCell: {str(e)}", message_type="error"
            )
            return False

    async def _disconnect(self) -> bool:
        """Disconnect from LoadCell"""
        try:
            self._monitoring = False  # Stop monitoring if active
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

    async def _show_status(self) -> None:
        """Show LoadCell status"""
        try:
            is_connected = await self.loadcell_service.is_connected()

            status_details = {
                "Connection": "Connected" if is_connected else "Disconnected",
                "Type": "BS205 Force Measurement",
            }

            if is_connected:
                try:
                    force = await self.loadcell_service.read_force()
                    status_details["Current Force"] = f"{force:.3f} N"
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

    async def _read_force(self) -> None:
        """Read current force"""
        try:
            force = await self.loadcell_service.read_force()
            self.formatter.print_message(
                f"Current force reading: {force:.3f} N", message_type="info", title="Force Reading"
            )

        except Exception as e:
            self.formatter.print_message(f"Failed to read force: {str(e)}", message_type="error")

    async def _zero_calibration(self) -> bool:
        """Perform zero calibration"""
        try:
            with self.formatter.create_progress_display("Performing zero calibration...") as status:
                await self.loadcell_service.zero_calibration()
                if isinstance(status, Status):
                    status.update("Zero calibration complete")

            self.formatter.print_message(
                "Zero calibration completed successfully", message_type="success"
            )
            return True

        except Exception as e:
            self.formatter.print_message(f"Zero calibration failed: {str(e)}", message_type="error")
            return False

    async def _monitor_force(self) -> None:
        """Monitor force readings in real-time"""
        try:
            self.formatter.print_message(
                "Starting force monitoring. Press Ctrl+C to stop.",
                message_type="info",
                title="Force Monitor",
            )

            ui_manager = RichUIManager(self.formatter.console)

            initial_force = await self.loadcell_service.read_force()
            initial_panel = self.formatter.create_message_panel(
                f"Force: {initial_force:.3f} N", message_type="info", title="Live Force Reading"
            )

            self._monitoring = True
            with ui_manager.live_display(initial_panel, refresh_per_second=2) as live:
                try:
                    while self._monitoring:
                        force = await self.loadcell_service.read_force()
                        force_panel = self.formatter.create_message_panel(
                            f"Force: {force:.3f} N", message_type="info", title="Live Force Reading"
                        )
                        live.update(force_panel)
                        # Get refresh rate from configuration
                        refresh_rate = 0.5  # default
                        if self.config_reader:
                            try:
                                defaults = self.config_reader.get_command_defaults("loadcell")
                                refresh_rate = defaults.get("monitor_refresh_rate", 0.5)
                            except Exception:
                                pass
                        await asyncio.sleep(refresh_rate)

                except KeyboardInterrupt:
                    self._monitoring = False

            self.formatter.print_message("Force monitoring stopped", message_type="info")

        except Exception as e:
            self._monitoring = False
            self.formatter.print_message(f"Force monitoring failed: {str(e)}", message_type="error")

    def get_help_info(self) -> Dict[str, str]:
        """Get LoadCell command help information"""
        return {
            "connect": "Connect to the LoadCell hardware",
            "disconnect": "Disconnect from the LoadCell hardware",
            "status": "Show LoadCell connection and force status",
            "read": "Read current force measurement",
            "zero": "Perform zero calibration on the LoadCell",
            "monitor": "Start real-time force monitoring (Ctrl+C to stop)",
        }


class PowerCommandHandler(HardwareCommandHandler):
    """Command handler for Power hardware operations"""

    def __init__(self, power_service: PowerService, formatter: RichFormatter, config_reader: Optional[CLIConfigReader] = None):
        super().__init__(formatter)
        self.power_service = power_service
        self.config_reader = config_reader
        self._connection_params = self._get_connection_params()

    async def handle_command(self, command_info: CommandInfo) -> bool:
        """Handle Power commands"""
        try:
            subcommand = command_info.subcommand

            if subcommand == "connect":
                return await self._connect()
            if subcommand == "disconnect":
                return await self._disconnect()
            if subcommand == "status":
                await self._show_status()
                return True
            if subcommand == "on":
                return await self._enable_output()
            if subcommand == "off":
                return await self._disable_output()
            if subcommand == "voltage":
                if command_info.arguments:
                    return await self._set_voltage(command_info.arguments[0])
                await self._get_voltage()
                return True
            if subcommand == "current":
                if command_info.arguments:
                    return await self._set_current_limit(command_info.arguments[0])
                await self._get_current()
                return True

            self.formatter.print_message(
                f"Unknown Power subcommand: {subcommand}", message_type="error"
            )
            return False

        except Exception as e:
            self.formatter.print_message(f"Power command failed: {str(e)}", message_type="error")
            logger.error(f"Power command error: {e}")
            return False

    def _get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters from configuration"""
        if self.config_reader:
            try:
                return self.config_reader.get_connection_params("power")
            except Exception as e:
                logger.warning(f"Failed to load Power config, using defaults: {e}")
        
        # Fallback to hardcoded defaults
        return {
            "host": "192.168.1.100",
            "port": 5025,
            "timeout": 5.0,
            "channel": 1
        }
    
    async def _connect(self) -> bool:
        """Connect to Power supply"""
        try:
            with self.formatter.create_progress_display("Connecting to Power supply...") as status:
                await self.power_service.connect(
                    host=self._connection_params.get("host", "192.168.1.100"),
                    port=self._connection_params.get("port", 5025),
                    timeout=self._connection_params.get("timeout", 5.0),
                    channel=self._connection_params.get("channel", 1)
                )
                if isinstance(status, Status):
                    status.update("Power supply connected successfully")

            self.formatter.print_message(
                "Power supply connected successfully", message_type="success"
            )
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to connect to Power supply: {str(e)}", message_type="error"
            )
            return False

    async def _disconnect(self) -> bool:
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

    async def _show_status(self) -> None:
        """Show Power status"""
        try:
            is_connected = await self.power_service.is_connected()

            status_details = {
                "Connection": "Connected" if is_connected else "Disconnected",
                "Type": "ODA Power Supply",
            }

            if is_connected:
                try:
                    voltage = await self.power_service.get_voltage()
                    current = await self.power_service.get_current()
                    is_output_on = await self.power_service.is_output_enabled()

                    status_details["Voltage"] = f"{voltage:.2f}V"
                    status_details["Current"] = f"{current:.3f}A"
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

    async def _enable_output(self) -> bool:
        """Enable power output"""
        try:
            await self.power_service.enable_output()
            self.formatter.print_message("Power output enabled", message_type="success")
            return True

        except Exception as e:
            self.formatter.print_message(f"Failed to enable output: {str(e)}", message_type="error")
            return False

    async def _disable_output(self) -> bool:
        """Disable power output"""
        try:
            await self.power_service.disable_output()
            self.formatter.print_message(
                "Power output disabled", message_type="warning", title="Output Disabled"
            )
            return True

        except Exception as e:
            self.formatter.print_message(
                f"Failed to disable output: {str(e)}", message_type="error"
            )
            return False

    async def _get_voltage(self) -> None:
        """Get current voltage"""
        try:
            voltage = await self.power_service.get_voltage()
            self.formatter.print_message(
                f"Current voltage: {voltage:.2f}V", message_type="info", title="Voltage Reading"
            )

        except Exception as e:
            self.formatter.print_message(f"Failed to get voltage: {str(e)}", message_type="error")

    async def _set_voltage(self, voltage_str: str) -> bool:
        """Set output voltage"""
        try:
            voltage = float(voltage_str)
            await self.power_service.set_voltage(voltage)
            self.formatter.print_message(f"Voltage set to {voltage:.2f}V", message_type="success")
            return True

        except ValueError:
            self.formatter.print_message(
                f"Invalid voltage value: {voltage_str}", message_type="error"
            )
            return False
        except Exception as e:
            self.formatter.print_message(f"Failed to set voltage: {str(e)}", message_type="error")
            return False

    async def _get_current(self) -> None:
        """Get current reading"""
        try:
            current = await self.power_service.get_current()
            self.formatter.print_message(
                f"Current reading: {current:.3f}A", message_type="info", title="Current Reading"
            )

        except Exception as e:
            self.formatter.print_message(f"Failed to get current: {str(e)}", message_type="error")

    async def _set_current_limit(self, current_str: str) -> bool:
        """Set current limit"""
        try:
            current = float(current_str)
            await self.power_service.set_current_limit(current)
            self.formatter.print_message(
                f"Current limit set to {current:.3f}A", message_type="success"
            )
            return True

        except ValueError:
            self.formatter.print_message(
                f"Invalid current value: {current_str}", message_type="error"
            )
            return False
        except Exception as e:
            self.formatter.print_message(
                f"Failed to set current limit: {str(e)}", message_type="error"
            )
            return False

    def get_help_info(self) -> Dict[str, str]:
        """Get Power command help information"""
        return {
            "connect": "Connect to the Power supply hardware",
            "disconnect": "Disconnect from the Power supply hardware",
            "status": "Show Power supply connection and output status",
            "on": "Enable power output",
            "off": "Disable power output",
            "voltage": "Get current voltage or set voltage with argument (V)",
            "current": "Get current reading or set current limit with argument (A)",
        }


class SlashCommandHandler:
    """Main slash command handler that coordinates all hardware command handlers"""

    def __init__(
        self,
        *,
        robot_service: RobotService,
        mcu_service: MCUService,
        loadcell_service: LoadCellService,
        power_service: PowerService,
        console: Optional[Console] = None,
        config_reader: Optional[CLIConfigReader] = None,
    ):
        self.console = console or Console()
        self.formatter = RichFormatter(self.console)
        self.parser = CommandParser()
        self.config_reader = config_reader or CLIConfigReader()

        # Initialize hardware command handlers with configuration
        self.handlers = {
            CommandType.ROBOT: RobotCommandHandler(robot_service, self.formatter, self.config_reader),
            CommandType.MCU: MCUCommandHandler(mcu_service, self.formatter, self.config_reader),
            CommandType.LOADCELL: LoadCellCommandHandler(loadcell_service, self.formatter, self.config_reader),
            CommandType.POWER: PowerCommandHandler(power_service, self.formatter, self.config_reader),
        }

        logger.info("Slash command handler initialized with all hardware services and configuration")

    async def execute_command(self, input_text: str) -> bool:
        """Execute a slash command

        Args:
            input_text: Raw command input from user

        Returns:
            True if command executed successfully, False otherwise
        """
        # Parse the command
        command_info = self.parser.parse_command(input_text)

        if not command_info:
            self.formatter.print_message(
                "Invalid command format. Type '/help' for available commands.", message_type="error"
            )
            return False

        # Validate the command
        if not self.parser.validate_command(command_info):
            self.formatter.print_message(
                f"Invalid command: {command_info.raw_input}", message_type="error"
            )
            return False

        try:
            # Handle special commands
            if command_info.command_type == CommandType.HELP:
                self._show_help(command_info.arguments)
                return True
            if command_info.command_type == CommandType.ALL:
                if command_info.subcommand == "status":
                    await self._show_all_status()
                    return True

            # Handle hardware-specific commands
            handler = self.handlers.get(command_info.command_type)
            if handler:
                return await handler.handle_command(command_info)

            self.formatter.print_message(
                f"No handler available for command type: {command_info.command_type.value}",
                message_type="error",
            )
            return False

        except Exception as e:
            self.formatter.print_message(f"Error executing command: {str(e)}", message_type="error")
            logger.error(f"Command execution error: {e}")
            return False

    async def _show_all_status(self) -> None:
        """Show status of all hardware components"""
        self.formatter.print_header("All Hardware Status", "Overview of all hardware components")

        # Execute status commands for all hardware types
        hardware_commands = [
            (CommandType.ROBOT, "status"),
            (CommandType.MCU, "status"),
            (CommandType.LOADCELL, "status"),
            (CommandType.POWER, "status"),
        ]

        for cmd_type, subcommand in hardware_commands:
            try:
                command_info = CommandInfo(
                    command_type=cmd_type,
                    subcommand=subcommand,
                    arguments=[],
                    raw_input=f"{cmd_type.value} {subcommand}",
                )

                handler = self.handlers.get(cmd_type)
                if handler:
                    await handler.handle_command(command_info)
                    self.console.print("")  # Add spacing

            except Exception as e:
                self.formatter.print_message(
                    f"Failed to get {cmd_type.value} status: {str(e)}", message_type="error"
                )

    def _show_help(self, args: Optional[List[str]]) -> None:
        """Show help information for commands"""
        if (
            args
            and len(args) > 0
            and args[0].lower() in [cmd.value.replace("/", "") for cmd in CommandType]
        ):
            # Show help for specific command
            cmd_name = f"/{args[0].lower()}"
            cmd_type = None

            for ct in CommandType:
                if ct.value == cmd_name:
                    cmd_type = ct
                    break

            if cmd_type and cmd_type in self.handlers:
                self._show_specific_help(cmd_type, self.handlers[cmd_type])
            else:
                self._show_general_help()
        else:
            # Show general help
            self._show_general_help()

    def _show_general_help(self) -> None:
        """Show general help with all available commands"""
        self.formatter.print_header("Slash Command Help", "Available hardware control commands")

        # Create help table
        table = Table(title="Available Commands")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Subcommands", style="green")
        table.add_column("Description", style="white")

        # Add robot commands
        robot_subs = ", ".join(self.parser.VALID_SUBCOMMANDS[CommandType.ROBOT])
        table.add_row("/robot", robot_subs, "Control robot hardware (AJINEXTEK)")

        # Add MCU commands
        mcu_subs = ", ".join(self.parser.VALID_SUBCOMMANDS[CommandType.MCU])
        table.add_row("/mcu", mcu_subs, "Control MCU hardware (LMA Temperature)")

        # Add LoadCell commands
        loadcell_subs = ", ".join(self.parser.VALID_SUBCOMMANDS[CommandType.LOADCELL])
        table.add_row("/loadcell", loadcell_subs, "Control LoadCell hardware (BS205)")

        # Add Power commands
        power_subs = ", ".join(self.parser.VALID_SUBCOMMANDS[CommandType.POWER])
        table.add_row("/power", power_subs, "Control Power supply hardware (ODA)")

        # Add special commands
        table.add_row("/all", "status", "Show all hardware status")
        table.add_row("/help", "[command]", "Show help information")

        self.console.print(table)

        # Add usage examples
        examples_panel = Panel(
            """[bold cyan]Usage Examples:[/bold cyan]
/robot connect          - Connect to robot hardware
/mcu temp 85.0         - Set MCU temperature to 85°C
/loadcell monitor      - Start real-time force monitoring
/power voltage 24.0    - Set power supply to 24V
/all status            - Show all hardware status
/help robot            - Show detailed robot command help""",
            title="Examples",
            border_style="green",
        )
        self.console.print("\n")
        self.console.print(examples_panel)

    def _show_specific_help(self, cmd_type: CommandType, handler: HardwareCommandHandler) -> None:
        """Show detailed help for a specific command type"""
        help_info = handler.get_help_info()

        self.formatter.print_header(
            f"{cmd_type.value.upper()} Command Help", f"Detailed help for {cmd_type.value} commands"
        )

        # Create detailed help table
        table = Table(title=f"{cmd_type.value} Subcommands")
        table.add_column("Subcommand", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        for subcommand, description in help_info.items():
            table.add_row(subcommand, description)

        self.console.print(table)

        # Add specific usage examples
        examples = self._get_command_examples(cmd_type)
        if examples:
            examples_panel = Panel(examples, title="Usage Examples", border_style="green")
            self.console.print("\n")
            self.console.print(examples_panel)

    def _get_command_examples(self, cmd_type: CommandType) -> str:
        """Get usage examples for a specific command type"""
        examples = {
            CommandType.ROBOT: (
                """[bold cyan]Robot Command Examples:[/bold cyan]
/robot connect         - Connect to robot hardware
/robot init           - Initialize robot system
/robot status         - Show robot connection status
/robot stop           - Execute emergency stop"""
            ),
            CommandType.MCU: (
                """[bold cyan]MCU Command Examples:[/bold cyan]
/mcu connect          - Connect to MCU hardware
/mcu temp             - Get current temperature
/mcu temp 85.0        - Set temperature to 85°C
/mcu fan 75           - Set fan speed to 75%
/mcu testmode         - Enter test mode"""
            ),
            CommandType.LOADCELL: (
                """[bold cyan]LoadCell Command Examples:[/bold cyan]
/loadcell connect     - Connect to LoadCell hardware
/loadcell read        - Read current force
/loadcell zero        - Perform zero calibration
/loadcell monitor     - Start real-time monitoring"""
            ),
            CommandType.POWER: (
                """[bold cyan]Power Command Examples:[/bold cyan]
/power connect        - Connect to Power supply
/power on             - Enable power output
/power voltage 24.0   - Set voltage to 24V
/power current 2.5    - Set current limit to 2.5A
/power status         - Show power supply status"""
            ),
        }

        return examples.get(cmd_type, "")

    def is_slash_command(self, input_text: str) -> bool:
        """Check if input text is a slash command

        Args:
            input_text: Input text to check

        Returns:
            True if input is a slash command, False otherwise
        """
        if not input_text:
            return False

        return input_text.strip().startswith("/")
