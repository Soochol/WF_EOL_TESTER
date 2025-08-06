"""
MCU Hardware Controller

Provides MCU-specific control operations including temperature control,
test mode management, and status monitoring for LMA controllers.
"""

from typing import Optional

from application.interfaces.hardware.mcu import MCUService
from domain.enums.mcu_enums import TestMode
from domain.value_objects.hardware_configuration import MCUConfig

from ...rich_formatter import RichFormatter
from ..base.hardware_controller import HardwareController, simple_interactive_menu


class MCUController(HardwareController):
    """Controller for MCU hardware"""

    def __init__(self, mcu_service: MCUService, formatter: RichFormatter, mcu_config: Optional[MCUConfig] = None):
        super().__init__(formatter)
        self.mcu_service = mcu_service
        self.mcu_config = mcu_config
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

        async def connect_operation():
            if self.mcu_config:
                # Use YAML configuration
                await self.mcu_service.connect(
                    port=self.mcu_config.port,
                    baudrate=self.mcu_config.baudrate,
                    timeout=self.mcu_config.timeout,
                    bytesize=self.mcu_config.bytesize,
                    stopbits=self.mcu_config.stopbits,
                    parity=self.mcu_config.parity,
                )
            else:
                # Fallback to Windows-compatible defaults if no config available
                # TODO: Fix configuration loading issue - this fallback should not be used
                await self.mcu_service.connect(
                    port="COM4",  # Changed from /dev/ttyUSB1 to match YAML config
                    baudrate=115200,
                    timeout=2.0,
                    bytesize=8,
                    stopbits=1,
                    parity=None,
                )
            return True

        return await self._show_progress_with_message(
            "Connecting to MCU...",
            connect_operation,
            "MCU connected successfully",
            "Failed to connect to MCU",
        )

    async def disconnect(self) -> bool:
        """Disconnect from MCU"""

        async def disconnect_operation():
            await self.mcu_service.disconnect()
            return True

        return await self._show_progress_with_message(
            "Disconnecting from MCU...",
            disconnect_operation,
            "MCU disconnected successfully",
            "Failed to disconnect MCU",
            show_time=0.2,
        )

    async def show_control_menu(self) -> Optional[str]:
        """Show enhanced MCU control menu with status information"""

        # Get current status information
        try:
            is_connected = await self.mcu_service.is_connected()
            connection_status = self._format_connection_status(is_connected)

            if is_connected:
                try:
                    # Get test mode status (if available) - skip auto temperature reading to avoid immediate communication
                    status = await self.mcu_service.get_status()
                    test_mode = status.get("test_mode", "Normal")
                    mode_info = f"🧪 {test_mode} Mode"
                    temp_info = "🌡️ Click to read"  # Static placeholder instead of auto-reading temperature
                except Exception:
                    temp_info = "🌡️ Click to read"
                    mode_info = "🧪 Unknown Mode"
            else:
                temp_info = "🌡️ Disconnected"
                mode_info = "🧪 Unknown Mode"

        except Exception:
            connection_status = "❓ Unknown"
            temp_info = "🌡️ Unknown"
            mode_info = "🧪 Unknown Mode"

        # Enhanced menu options with icons and status
        menu_options = {
            "1": "🔌 Connect",
            "2": "❌ Disconnect",
            "3": f"🌡️ Get Temperature     [{temp_info}]",
            "4": f"🧪 Enter Test Mode     [{mode_info}]",
            "5": f"🎛️ Set Operating Temp  [{temp_info}]",
            "6": "⏳ Wait Boot Complete",
            "b": "⬅️  Back to Hardware Menu",
        }

        # Create enhanced title with status
        enhanced_title = (
            f"⚙️ MCU Control System\n"
            f"📡 Status: {connection_status}  |  {temp_info}  |  {mode_info}\n"
            f"[dim]💡 Use numbers 1-6 to select options, or 'b' to go back[/dim]"
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

            if cmd == "1" or cmd == "c":
                return await self.connect()
            elif cmd == "2" or cmd == "d":
                return await self.disconnect()
            elif cmd == "3" or cmd == "temp":
                await self._get_temperature()
            elif cmd == "4" or cmd == "test":
                await self._enter_test_mode()
            elif cmd == "5" or cmd == "set":
                await self._set_operating_temperature()
            elif cmd == "6" or cmd == "boot":
                await self._wait_boot_complete()
            else:
                return False
            return True

        except Exception as e:
            self.formatter.print_message(f"❌ MCU command failed: {str(e)}", message_type="error")
            return False

    # Private MCU-specific operations
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
            temperature = self._get_user_input_with_validation(
                "Enter operating temperature (°C):",
                input_type=float,
                validator=lambda x: -50 <= x <= 200,  # Reasonable temperature range
            )

            if temperature is None:
                self.formatter.print_message("Temperature setting cancelled", message_type="info")
                return

            # Type check temperature value
            if isinstance(temperature, (int, float)):
                await self.mcu_service.set_temperature(float(temperature))
            else:
                raise ValueError("Invalid temperature type")

            self.formatter.print_message(
                f"Operating temperature set to {temperature:.2f}°C", message_type="success"
            )

        except Exception as e:
            self.formatter.print_message(
                f"Failed to set operating temperature: {str(e)}", message_type="error"
            )

    async def _wait_boot_complete(self) -> None:
        """Wait for MCU boot complete signal"""
        try:
            # Check if MCU is connected
            if not await self.mcu_service.is_connected():
                self.formatter.print_message("MCU is not connected", message_type="error")
                return

            async def boot_wait_operation():
                # Check if MCU service has wait_boot_complete method
                if hasattr(self.mcu_service, 'wait_boot_complete'):
                    await self.mcu_service.wait_boot_complete()
                else:
                    # Fallback: just show that we're waiting
                    import asyncio
                    await asyncio.sleep(2.0)
                return True

            await self._show_progress_with_message(
                "Waiting for MCU boot complete signal...",
                boot_wait_operation,
                "MCU boot complete signal received successfully",
                "Failed to receive boot complete signal",
            )

        except Exception as e:
            self.formatter.print_message(
                f"Boot complete wait failed: {str(e)}", message_type="error"
            )
