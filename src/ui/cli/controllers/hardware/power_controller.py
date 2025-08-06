"""
Power Hardware Controller

Provides Power-specific control operations including voltage/current control,
output management, and safety features for ODA power supplies.
"""

from typing import Optional

from application.interfaces.hardware.power import PowerService
from domain.value_objects.hardware_configuration import PowerConfig

from ...rich_formatter import RichFormatter
from ..base.hardware_controller import HardwareController, simple_interactive_menu


class PowerController(HardwareController):
    """Controller for Power hardware"""

    def __init__(self, power_service: PowerService, formatter: RichFormatter, power_config: Optional[PowerConfig] = None):
        super().__init__(formatter)
        self.power_service = power_service
        self.power_config = power_config
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

        async def connect_operation():
            if self.power_config:
                # Use YAML configuration
                await self.power_service.connect(
                    host=self.power_config.host,
                    port=self.power_config.port,
                    timeout=self.power_config.timeout,
                    channel=self.power_config.channel,
                )
            else:
                # Fallback to YAML-compatible defaults if no config available
                # TODO: Fix configuration loading issue - this fallback should not be used
                await self.power_service.connect(
                    host="192.168.11.1", port=5000, timeout=5.0, channel=1  # Match YAML config
                )

            # Get and display device identity if available
            device_identity = None
            if hasattr(self.power_service, "get_device_identity"):
                try:
                    device_identity = await self.power_service.get_device_identity()
                    if device_identity:
                        self.formatter.print_message(
                            f"Device Identity: {device_identity}", message_type="info"
                        )
                except Exception:
                    pass  # Ignore errors getting device identity
            return True

        return await self._show_progress_with_message(
            "Connecting to Power supply...",
            connect_operation,
            "Power supply connected successfully",
            "Failed to connect to Power supply",
        )

    async def disconnect(self) -> bool:
        """Disconnect from Power supply"""

        async def disconnect_operation():
            await self.power_service.disconnect()
            return True

        return await self._show_progress_with_message(
            "Disconnecting from Power supply...",
            disconnect_operation,
            "Power supply disconnected successfully",
            "Failed to disconnect Power supply",
            show_time=0.2,
        )

    async def show_control_menu(self) -> Optional[str]:
        """Show enhanced Power control menu with status information"""

        # Get current status information
        try:
            is_connected = await self.power_service.is_connected()
            connection_status = self._format_connection_status(is_connected)

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

    # Private power-specific operations
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
            except Exception:
                # If we can't get voltage/current, still ask for confirmation
                self.formatter.print_message(
                    "⚠️  WARNING: About to enable power output!\n"
                    "   Ensure all safety precautions are in place.",
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
                current_voltage = 0.0

            # Enhanced voltage input prompt
            self.formatter.console.print("[bold cyan]⚡ Set Output Voltage[/bold cyan]")
            self.formatter.console.print(f"[dim]   {current_info}[/dim]")

            voltage = self._get_user_input_with_validation(
                "Enter new voltage (V):",
                input_type=float,
                validator=lambda x: 0 <= x <= 50,  # Reasonable voltage range
            )

            if voltage is None:
                self.formatter.print_message("❌ Voltage setting cancelled", message_type="info")
                return

            # Show what will be set
            self.formatter.print_message(
                f"⚡ Setting voltage: {current_voltage:.2f}V → {voltage:.2f}V", message_type="info"
            )

            # Type check voltage value
            if isinstance(voltage, (int, float)):
                await self.power_service.set_voltage(float(voltage))
            else:
                raise ValueError("Invalid voltage type")

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
                current_value = 0.0

            # Enhanced current input prompt
            self.formatter.console.print("[bold cyan]🔋 Set Output Current[/bold cyan]")
            self.formatter.console.print(f"[dim]   {current_info}[/dim]")

            current = self._get_user_input_with_validation(
                "Enter new current (A):",
                input_type=float,
                validator=lambda x: 0 <= x <= 10,  # Reasonable current range
            )

            if current is None:
                self.formatter.print_message("❌ Current setting cancelled", message_type="info")
                return

            # Show what will be set
            self.formatter.print_message(
                f"🔋 Setting current: {current_value:.2f}A → {current:.2f}A",
                message_type="info",
            )

            # Type check current value
            if isinstance(current, (int, float)):
                await self.power_service.set_current(float(current))
            else:
                raise ValueError("Invalid current type")

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
                current_limit = 0.0

            # Enhanced current input prompt
            self.formatter.console.print("[bold cyan]🔌 Set Current Limit[/bold cyan]")
            self.formatter.console.print(f"[dim]   {current_info}[/dim]")

            current = self._get_user_input_with_validation(
                "Enter new current limit (A):",
                input_type=float,
                validator=lambda x: 0 <= x <= 10,  # Reasonable current limit range
            )

            if current is None:
                self.formatter.print_message(
                    "❌ Current limit setting cancelled", message_type="info"
                )
                return

            # Show what will be set
            self.formatter.print_message(
                f"🔌 Setting current limit: {current_limit:.2f}A → {current:.2f}A",
                message_type="info",
            )

            # Type check current limit value
            if isinstance(current, (int, float)):
                await self.power_service.set_current_limit(float(current))
            else:
                raise ValueError("Invalid current limit type")

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

        except Exception as e:
            self.formatter.print_message(
                f"❌ Failed to set current limit: {str(e)}", message_type="error"
            )
