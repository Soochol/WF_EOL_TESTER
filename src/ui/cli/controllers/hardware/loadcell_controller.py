"""
LoadCell Hardware Controller

Provides LoadCell-specific control operations including force measurement,
calibration, and real-time monitoring for BS205 force sensors.
"""

import asyncio
from typing import Optional

from application.interfaces.hardware.loadcell import LoadCellService
from ..base.hardware_controller import HardwareController, simple_interactive_menu
from ...rich_formatter import RichFormatter


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
        async def connect_operation():
            await self.loadcell_service.connect(
                port="/dev/ttyUSB0",
                baudrate=9600,
                timeout=1.0,
                bytesize=8,
                stopbits=1,
                parity=None,
                indicator_id=1,
            )
            return True

        return await self._show_progress_with_message(
            "Connecting to LoadCell...",
            connect_operation,
            "LoadCell connected successfully",
            "Failed to connect to LoadCell"
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
            show_time=0.2
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
            show_time=0.8  # Show spinner longer for calibration
        )

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
