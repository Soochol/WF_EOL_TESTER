"""
LoadCell Hardware Controller

Provides LoadCell-specific control operations including force measurement,
and calibration for BS205 force sensors.
"""

import asyncio
from typing import Optional

from application.interfaces.hardware.loadcell import LoadCellService
from domain.value_objects.hardware_config import LoadCellConfig

from ...rich_formatter import RichFormatter
from ..base.hardware_controller import HardwareController, simple_interactive_menu


class LoadCellController(HardwareController):
    """Controller for LoadCell hardware"""

    def __init__(
        self,
        loadcell_service: LoadCellService,
        formatter: RichFormatter,
        loadcell_config: Optional[LoadCellConfig] = None,
    ):
        super().__init__(formatter)
        self.loadcell_service = loadcell_service
        self.loadcell_config = loadcell_config
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

        async def connect_operation():
            # LoadCell service is configured via dependency injection in HardwareContainer
            # All connection parameters are provided through the constructor
            await self.loadcell_service.connect()
            return True

        return await self._show_progress_with_message(
            "Connecting to LoadCell...",
            connect_operation,
            "LoadCell connected successfully",
            "Failed to connect to LoadCell",
        )

    async def disconnect(self) -> bool:
        """Disconnect from LoadCell"""

        async def disconnect_operation():
            await self.loadcell_service.disconnect()
            return True

        return await self._show_progress_with_message(
            "Disconnecting from LoadCell...",
            disconnect_operation,
            "LoadCell disconnected successfully",
            "Failed to disconnect LoadCell",
            show_time=0.2,
        )

    async def show_control_menu(self) -> Optional[str]:
        """Show enhanced LoadCell control menu with status information"""

        # Get current status information
        try:
            is_connected = await self.loadcell_service.is_connected()
            connection_status = self._format_connection_status(is_connected)

            if is_connected:
                try:
                    # Get current force reading
                    force_value = await self.loadcell_service.read_force()
                    force_info = f"{force_value.value:.3f} {force_value.unit.value}"

                    # Get status information
                    status = await self.loadcell_service.get_status()
                    hardware_type = status.get("hardware_type", "Unknown")
                    device_info = f"{hardware_type}"
                except Exception:
                    force_info = "---.--- kgf"
                    device_info = "Unknown"
            else:
                force_info = "---.--- kgf"
                device_info = "Unknown"

        except Exception:
            connection_status = "Unknown"
            force_info = "---.--- kgf"
            device_info = "Unknown"

        # Enhanced menu options with icons and status
        menu_options = {
            "1": "Connect",
            "2": "Disconnect",
            "3": f"Read Force [{force_info}]",
            "4": "Zero Calibration [Reset to 0.000]",
            "5": "Hold Current Value [Fix Display]",
            "6": "Release Hold [Live Display]",
            "b": "Back to Hardware Menu",
        }

        # Create enhanced title with status
        enhanced_title = (
            f"LoadCell Control System\n"
            f"Status: {connection_status}  |  {force_info}  |  {device_info}\n"
            f"[dim]Use numbers 1-6 to select options, or 'b' to go back[/dim]"
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

            if cmd == "1":
                return await self.connect()
            elif cmd == "2":
                return await self.disconnect()
            elif cmd == "3":
                await self._read_force()
            elif cmd == "4":
                await self._zero_calibration()
            elif cmd == "5":
                await self._hold_current_value()
            elif cmd == "6":
                await self._release_hold()
            else:
                return False
            return True

        except Exception as e:
            self.formatter.print_message(f"LoadCell command failed: {str(e)}", message_type="error")
            return False

    # Private LoadCell-specific operations
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

        async def calibration_operation():
            await self.loadcell_service.zero_calibration()
            return True

        await self._show_progress_with_message(
            "Performing zero calibration...",
            calibration_operation,
            "Zero calibration completed successfully",
            "Zero calibration failed",
            show_time=0.8,  # Show spinner longer for calibration
        )

    async def _hold_current_value(self) -> None:
        """Hold current force value"""

        async def hold_operation():
            await self.loadcell_service.hold()
            return True

        await self._show_progress_with_message(
            "Setting hold on current value...",
            hold_operation,
            "Current value held successfully",
            "Failed to set hold",
            show_time=0.3,
        )

    async def _release_hold(self) -> None:
        """Release hold and return to live display"""

        async def release_operation():
            await self.loadcell_service.hold_release()
            return True

        await self._show_progress_with_message(
            "Releasing hold...",
            release_operation,
            "Hold released - live display active",
            "Failed to release hold",
            show_time=0.3,
        )

