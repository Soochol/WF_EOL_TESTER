"""
Real-time Hardware Monitoring Dashboard for EOL Tester CLI

This module provides a comprehensive real-time dashboard for monitoring all hardware
components in the EOL testing system. Features include live status updates, key
metrics display, interactive controls, and professional Rich UI formatting.

Key Features:
- Real-time hardware status monitoring with color-coded indicators
- Live metrics display for Robot, MCU, LoadCell, and Power components
- Interactive controls with configurable refresh rates
- Professional dashboard layout with Rich components
- Error recovery and graceful hardware disconnection handling
- Export functionality for monitoring snapshots
- Memory-efficient data collection and display updates
"""

import asyncio
import json
import time
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from loguru import logger

from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.mcu import MCUService
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.robot import RobotService
from application.services.hardware_service_facade import HardwareServiceFacade


@dataclass
class HardwareMetrics:
    """Data class for storing hardware metrics snapshot"""

    timestamp: float
    robot_connected: bool
    mcu_connected: bool
    loadcell_connected: bool
    power_connected: bool
    robot_position: Optional[float] = None
    robot_velocity: Optional[float] = None
    robot_motion_status: Optional[str] = None
    robot_is_moving: bool = False
    mcu_temperature: Optional[float] = None
    mcu_fan_speed: Optional[float] = None
    mcu_test_mode: Optional[str] = None
    loadcell_force: Optional[float] = None
    loadcell_raw_value: Optional[float] = None
    power_voltage: Optional[float] = None
    power_current: Optional[float] = None
    power_output_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for export"""
        return asdict(self)


class HardwareDataCollector:
    """Handles safe data collection from hardware components"""

    def __init__(self, hardware_facade: HardwareServiceFacade):
        self._hardware = hardware_facade
        self._last_successful_data = HardwareMetrics(
            timestamp=time.time(),
            robot_connected=False,
            mcu_connected=False,
            loadcell_connected=False,
            power_connected=False,
        )

    async def collect_metrics(self) -> HardwareMetrics:
        """Collect current hardware metrics with error handling"""
        current_time = time.time()

        # Initialize metrics with current timestamp
        metrics = HardwareMetrics(
            timestamp=current_time,
            robot_connected=False,
            mcu_connected=False,
            loadcell_connected=False,
            power_connected=False,
        )

        # Collect data from each hardware component with individual error handling
        await self._collect_robot_data(metrics)
        await self._collect_mcu_data(metrics)
        await self._collect_loadcell_data(metrics)
        await self._collect_power_data(metrics)

        # Update last successful data cache
        self._last_successful_data = metrics
        return metrics

    async def _collect_robot_data(self, metrics: HardwareMetrics) -> None:
        """Collect robot data with error handling"""
        try:
            services = self._hardware.get_hardware_services()
            robot_service = services["robot"]

            metrics.robot_connected = await robot_service.is_connected()

            if metrics.robot_connected:
                # Type narrow to ensure we have a RobotService
                if isinstance(robot_service, RobotService):
                    # Get position for primary axis (axis 0)
                    try:
                        metrics.robot_position = await robot_service.get_position(0)
                        metrics.robot_velocity = await robot_service.get_velocity(0)
                        metrics.robot_is_moving = await robot_service.is_moving(0)

                        motion_status = await robot_service.get_motion_status()
                        metrics.robot_motion_status = (
                            motion_status.value if motion_status else "UNKNOWN"
                        )
                    except Exception as e:
                        logger.debug(f"Could not get detailed robot data: {e}")
                        metrics.robot_motion_status = "ERROR"

        except Exception as e:
            logger.debug(f"Robot data collection failed: {e}")
            metrics.robot_connected = False

    async def _collect_mcu_data(self, metrics: HardwareMetrics) -> None:
        """Collect MCU data with error handling"""
        try:
            services = self._hardware.get_hardware_services()
            mcu_service = services["mcu"]

            metrics.mcu_connected = await mcu_service.is_connected()

            if metrics.mcu_connected:
                # Type narrow to ensure we have an MCUService
                if isinstance(mcu_service, MCUService):
                    try:
                        metrics.mcu_temperature = await mcu_service.get_temperature()
                        metrics.mcu_fan_speed = await mcu_service.get_fan_speed()

                        test_mode = await mcu_service.get_test_mode()
                        metrics.mcu_test_mode = test_mode.value if test_mode else "UNKNOWN"
                    except Exception as e:
                        logger.debug(f"Could not get detailed MCU data: {e}")
                        metrics.mcu_test_mode = "ERROR"

        except Exception as e:
            logger.debug(f"MCU data collection failed: {e}")
            metrics.mcu_connected = False

    async def _collect_loadcell_data(self, metrics: HardwareMetrics) -> None:
        """Collect LoadCell data with error handling"""
        try:
            services = self._hardware.get_hardware_services()
            loadcell_service = services["loadcell"]

            metrics.loadcell_connected = await loadcell_service.is_connected()

            if metrics.loadcell_connected:
                # Type narrow to ensure we have a LoadCellService
                if isinstance(loadcell_service, LoadCellService):
                    try:
                        force_value = await loadcell_service.read_force()
                        metrics.loadcell_force = force_value.value if force_value else None
                        metrics.loadcell_raw_value = await loadcell_service.read_raw_value()
                    except Exception as e:
                        logger.debug(f"Could not get detailed LoadCell data: {e}")

        except Exception as e:
            logger.debug(f"LoadCell data collection failed: {e}")
            metrics.loadcell_connected = False

    async def _collect_power_data(self, metrics: HardwareMetrics) -> None:
        """Collect Power data with error handling"""
        try:
            services = self._hardware.get_hardware_services()
            power_service = services["power"]

            metrics.power_connected = await power_service.is_connected()

            if metrics.power_connected:
                # Type narrow to ensure we have a PowerService
                if isinstance(power_service, PowerService):
                    try:
                        metrics.power_voltage = await power_service.get_voltage()
                        metrics.power_current = await power_service.get_current()
                        metrics.power_output_enabled = await power_service.is_output_enabled()
                    except Exception as e:
                        logger.debug(f"Could not get detailed Power data: {e}")

        except Exception as e:
            logger.debug(f"Power data collection failed: {e}")
            metrics.power_connected = False


class DashboardRenderer:
    """Handles dashboard layout and rendering"""

    def __init__(self, console: Console):
        self._console = console
        self._start_time = time.time()

    def create_dashboard_layout(
        self, metrics: HardwareMetrics, refresh_rate: float, is_paused: bool
    ) -> Layout:
        """Create the main dashboard layout"""
        layout = Layout()

        # Split into header and main content
        layout.split_column(Layout(name="header", size=3), Layout(name="main"))

        # Split main content into status and hardware sections
        layout["main"].split_column(Layout(name="status", size=7), Layout(name="hardware"))

        # Split hardware section into two columns
        layout["hardware"].split_row(Layout(name="left_column"), Layout(name="right_column"))

        # Populate layout sections
        layout["header"].update(self._create_header_panel(refresh_rate, is_paused))
        layout["status"].update(self._create_status_summary(metrics))
        layout["left_column"].update(self._create_left_column(metrics))
        layout["right_column"].update(self._create_right_column(metrics))

        return layout

    def _create_header_panel(self, refresh_rate: float, is_paused: bool) -> Panel:
        """Create dashboard header with title and controls"""
        uptime = time.time() - self._start_time
        uptime_str = (
            f"{int(uptime // 3600):02d}:{int((uptime % 3600) // 60):02d}:{int(uptime % 60):02d}"
        )

        status_text = "[red]PAUSED[/red]" if is_paused else "[green]RUNNING[/green]"

        header_content = Text.assemble(
            ("Hardware Monitoring Dashboard", "bold white"),
            "\n",
            f"Status: {status_text} | ",
            f"Refresh: {refresh_rate:.1f}s | ",
            f"Uptime: {uptime_str} | ",
            f"Last Update: {datetime.now().strftime('%H:%M:%S')}",
        )

        return Panel(Align.center(header_content), style="bright_blue", box=box.DOUBLE)

    def _create_status_summary(self, metrics: HardwareMetrics) -> Panel:
        """Create overall system status summary"""
        # Count connected hardware
        connected_count = sum(
            [
                metrics.robot_connected,
                metrics.mcu_connected,
                metrics.loadcell_connected,
                metrics.power_connected,
            ]
        )
        total_count = 4

        # Determine overall status
        if connected_count == total_count:
            overall_status = "[green]ALL SYSTEMS ONLINE[/green]"
            status_color = "green"
        elif connected_count > 0:
            overall_status = (
                f"[yellow]PARTIAL CONNECTIVITY ({connected_count}/{total_count})[/yellow]"
            )
            status_color = "yellow"
        else:
            overall_status = "[red]ALL SYSTEMS OFFLINE[/red]"
            status_color = "red"

        # Create status table
        status_table = Table(show_header=False, box=None, padding=(0, 1))
        status_table.add_column("Component", style="bold")
        status_table.add_column("Status")
        status_table.add_column("Details", style="dim")

        # Robot status
        robot_status = (
            "[green]CONNECTED[/green]" if metrics.robot_connected else "[red]DISCONNECTED[/red]"
        )
        robot_details = ""
        if metrics.robot_connected and metrics.robot_position is not None:
            robot_details = f"Pos: {metrics.robot_position:.2f}mm"
            if metrics.robot_is_moving:
                robot_details += " [yellow](MOVING)[/yellow]"

        # MCU status
        mcu_status = (
            "[green]CONNECTED[/green]" if metrics.mcu_connected else "[red]DISCONNECTED[/red]"
        )
        mcu_details = ""
        if metrics.mcu_connected and metrics.mcu_temperature is not None:
            mcu_details = f"Temp: {metrics.mcu_temperature:.1f}°C"

        # LoadCell status
        loadcell_status = (
            "[green]CONNECTED[/green]" if metrics.loadcell_connected else "[red]DISCONNECTED[/red]"
        )
        loadcell_details = ""
        if metrics.loadcell_connected and metrics.loadcell_force is not None:
            loadcell_details = f"Force: {metrics.loadcell_force:.3f}N"

        # Power status
        power_status = (
            "[green]CONNECTED[/green]" if metrics.power_connected else "[red]DISCONNECTED[/red]"
        )
        power_details = ""
        if metrics.power_connected and metrics.power_voltage is not None:
            power_details = f"{metrics.power_voltage:.2f}V"
            if metrics.power_output_enabled:
                power_details += " [green](ON)[/green]"
            else:
                power_details += " [red](OFF)[/red]"

        status_table.add_row("Robot", robot_status, robot_details)
        status_table.add_row("MCU", mcu_status, mcu_details)
        status_table.add_row("LoadCell", loadcell_status, loadcell_details)
        status_table.add_row("Power", power_status, power_details)

        return Panel(
            Columns(
                [Panel(Align.center(overall_status), style=status_color, width=30), status_table],
                equal=False,
            ),
            title="System Status Overview",
            style="bright_white",
        )

    def _create_left_column(self, metrics: HardwareMetrics) -> Layout:
        """Create left column with Robot and MCU panels"""
        layout = Layout()
        layout.split_column(
            Layout(self._create_robot_panel(metrics)), Layout(self._create_mcu_panel(metrics))
        )
        return layout

    def _create_right_column(self, metrics: HardwareMetrics) -> Layout:
        """Create right column with LoadCell and Power panels"""
        layout = Layout()
        layout.split_column(
            Layout(self._create_loadcell_panel(metrics)), Layout(self._create_power_panel(metrics))
        )
        return layout

    def _create_robot_panel(self, metrics: HardwareMetrics) -> Panel:
        """Create Robot status panel"""
        if not metrics.robot_connected:
            content = "[red]Robot Disconnected[/red]\n\nNo data available"
            style = "red"
        else:
            lines = ["[green]Robot Connected[/green]\n"]

            if metrics.robot_position is not None:
                lines.append(f"Position: [cyan]{metrics.robot_position:.3f} mm[/cyan]")
            else:
                lines.append("Position: [dim]N/A[/dim]")

            if metrics.robot_velocity is not None:
                lines.append(f"Velocity: [cyan]{metrics.robot_velocity:.2f} mm/s[/cyan]")
            else:
                lines.append("Velocity: [dim]N/A[/dim]")

            if metrics.robot_motion_status:
                status_color = "green" if metrics.robot_motion_status == "IDLE" else "yellow"
                lines.append(
                    f"Motion Status: [{status_color}]{metrics.robot_motion_status}[/{status_color}]"
                )
            else:
                lines.append("Motion Status: [dim]N/A[/dim]")

            # Add movement indicator
            if metrics.robot_is_moving:
                lines.append("\n[yellow]⚡ Moving[/yellow]")
            else:
                lines.append("\n[green]⏹ Stationary[/green]")

            content = "\n".join(lines)
            style = "green"

        return Panel(content, title="🤖 Robot Controller", style=style, padding=(1, 2))

    def _create_mcu_panel(self, metrics: HardwareMetrics) -> Panel:
        """Create MCU status panel"""
        if not metrics.mcu_connected:
            content = "[red]MCU Disconnected[/red]\n\nNo data available"
            style = "red"
        else:
            lines = ["[green]MCU Connected[/green]\n"]

            if metrics.mcu_temperature is not None:
                temp_color = (
                    "red"
                    if metrics.mcu_temperature > 80
                    else "yellow" if metrics.mcu_temperature > 60 else "green"
                )
                lines.append(
                    f"Temperature: [{temp_color}]{metrics.mcu_temperature:.1f}°C[/{temp_color}]"
                )
            else:
                lines.append("Temperature: [dim]N/A[/dim]")

            if metrics.mcu_fan_speed is not None:
                lines.append(f"Fan Speed: [cyan]{metrics.mcu_fan_speed:.1f}%[/cyan]")
            else:
                lines.append("Fan Speed: [dim]N/A[/dim]")

            if metrics.mcu_test_mode:
                lines.append(f"Test Mode: [magenta]{metrics.mcu_test_mode}[/magenta]")
            else:
                lines.append("Test Mode: [dim]N/A[/dim]")

            # Add temperature status indicator
            if metrics.mcu_temperature is not None:
                if metrics.mcu_temperature > 80:
                    lines.append("\n[red]🔥 High Temperature[/red]")
                elif metrics.mcu_temperature > 60:
                    lines.append("\n[yellow]⚠ Warm[/yellow]")
                else:
                    lines.append("\n[green]❄ Normal Temperature[/green]")

            content = "\n".join(lines)
            style = "green"

        return Panel(content, title="🔧 MCU Controller", style=style, padding=(1, 2))

    def _create_loadcell_panel(self, metrics: HardwareMetrics) -> Panel:
        """Create LoadCell status panel"""
        if not metrics.loadcell_connected:
            content = "[red]LoadCell Disconnected[/red]\n\nNo data available"
            style = "red"
        else:
            lines = ["[green]LoadCell Connected[/green]\n"]

            if metrics.loadcell_force is not None:
                force_color = (
                    "red"
                    if abs(metrics.loadcell_force) > 10
                    else "yellow" if abs(metrics.loadcell_force) > 5 else "green"
                )
                lines.append(
                    f"Force: [{force_color}]{metrics.loadcell_force:.4f} N[/{force_color}]"
                )
            else:
                lines.append("Force: [dim]N/A[/dim]")

            if metrics.loadcell_raw_value is not None:
                lines.append(f"Raw Value: [cyan]{metrics.loadcell_raw_value:.0f}[/cyan]")
            else:
                lines.append("Raw Value: [dim]N/A[/dim]")

            lines.append("Calibration: [green]Active[/green]")

            # Add force level indicator
            if metrics.loadcell_force is not None:
                abs_force = abs(metrics.loadcell_force)
                if abs_force > 10:
                    lines.append("\n[red]⚠ High Force Detected[/red]")
                elif abs_force > 5:
                    lines.append("\n[yellow]⚡ Moderate Force[/yellow]")
                else:
                    lines.append("\n[green]✓ Normal Force Range[/green]")

            content = "\n".join(lines)
            style = "green"

        return Panel(content, title="⚖ Load Cell Sensor", style=style, padding=(1, 2))

    def _create_power_panel(self, metrics: HardwareMetrics) -> Panel:
        """Create Power status panel"""
        if not metrics.power_connected:
            content = "[red]Power Supply Disconnected[/red]\n\nNo data available"
            style = "red"
        else:
            lines = ["[green]Power Supply Connected[/green]\n"]

            if metrics.power_voltage is not None:
                voltage_color = (
                    "red" if metrics.power_voltage > 25 or metrics.power_voltage < 20 else "green"
                )
                lines.append(
                    f"Voltage: [{voltage_color}]{metrics.power_voltage:.2f} V[/{voltage_color}]"
                )
            else:
                lines.append("Voltage: [dim]N/A[/dim]")

            if metrics.power_current is not None:
                current_color = (
                    "red"
                    if metrics.power_current > 3
                    else "yellow" if metrics.power_current > 2 else "green"
                )
                lines.append(
                    f"Current: [{current_color}]{metrics.power_current:.3f} A[/{current_color}]"
                )
            else:
                lines.append("Current: [dim]N/A[/dim]")

            # Output status
            if metrics.power_output_enabled:
                lines.append("Output: [green]ENABLED[/green]")
                lines.append("\n[green]⚡ Power Active[/green]")
            else:
                lines.append("Output: [red]DISABLED[/red]")
                lines.append("\n[red]⏹ Power Inactive[/red]")

            content = "\n".join(lines)
            style = "green"

        return Panel(content, title="🔌 Power Supply", style=style, padding=(1, 2))


class HardwareMonitoringDashboard:
    """
    Comprehensive real-time hardware monitoring dashboard

    Features:
    - Real-time hardware status monitoring with Rich UI
    - Interactive controls (pause/resume, refresh rate adjustment)
    - Data export functionality
    - Memory-efficient operation with error recovery
    - Professional dashboard layout with color-coded indicators
    """

    def __init__(self, hardware_facade: HardwareServiceFacade, console: Optional[Console] = None):
        """
        Initialize the hardware monitoring dashboard

        Args:
            hardware_facade: Hardware service facade for data collection
            console: Rich console instance (creates new if None)
        """
        self._hardware_facade = hardware_facade
        self._console = console or Console()
        self._data_collector = HardwareDataCollector(hardware_facade)
        self._renderer = DashboardRenderer(self._console)

        # Dashboard state
        self._running = False
        self._paused = False
        self._refresh_rate = 2.0  # Default 2 second refresh
        self._metrics_history: List[HardwareMetrics] = []
        self._max_history_size = 100  # Keep last 100 metrics for export

    async def start_monitoring(self, refresh_rate: float = 2.0) -> None:
        """
        Start the real-time monitoring dashboard

        Args:
            refresh_rate: Refresh interval in seconds (1-10 seconds)
        """
        # Validate refresh rate
        self._refresh_rate = max(1.0, min(10.0, refresh_rate))

        logger.info(f"Starting hardware monitoring dashboard (refresh: {self._refresh_rate}s)")

        try:
            self._running = True
            self._paused = False

            with Live(
                self._create_loading_panel(),
                console=self._console,
                refresh_per_second=2,
                screen=True,
            ) as live:

                # Show controls information
                self._show_controls_info()

                # Main monitoring loop
                while self._running:
                    if not self._paused:
                        # Collect current metrics
                        try:
                            metrics = await self._data_collector.collect_metrics()
                            self._add_to_history(metrics)

                            # Update dashboard display
                            dashboard_layout = self._renderer.create_dashboard_layout(
                                metrics, self._refresh_rate, self._paused
                            )
                            live.update(dashboard_layout)

                        except Exception as e:
                            logger.error(f"Error collecting metrics: {e}")
                            # Continue with last known data

                    # Wait for next refresh
                    await asyncio.sleep(self._refresh_rate)

        except KeyboardInterrupt:
            logger.info("Dashboard monitoring stopped by user")
        except Exception as e:
            logger.error(f"Dashboard monitoring error: {e}")
        finally:
            self._running = False
            logger.info("Hardware monitoring dashboard stopped")

    def _create_loading_panel(self) -> Panel:
        """Create loading panel for dashboard initialization"""
        return Panel(
            Align.center(
                Text.assemble(
                    ("Initializing Hardware Monitoring Dashboard...", "bold yellow"),
                    "\n\n",
                    ("Collecting initial hardware data...", "dim"),
                )
            ),
            title="Loading",
            style="yellow",
        )

    def _show_controls_info(self) -> None:
        """Show dashboard controls information"""
        controls_panel = Panel(
            Text.assemble(
                ("Dashboard Controls", "bold white"),
                "\n\n",
                ("Press Ctrl+C to exit dashboard", "green"),
                "\n",
                ("Use the Hardware Control Center for interactive commands", "dim"),
            ),
            title="Controls",
            style="blue",
        )
        self._console.print(controls_panel)
        self._console.print()

    def _add_to_history(self, metrics: HardwareMetrics) -> None:
        """Add metrics to history with size limiting"""
        self._metrics_history.append(metrics)

        # Limit history size for memory efficiency
        if len(self._metrics_history) > self._max_history_size:
            self._metrics_history = self._metrics_history[-self._max_history_size :]

    def stop_monitoring(self) -> None:
        """Stop the monitoring dashboard"""
        self._running = False
        logger.info("Dashboard stop requested")

    def pause_monitoring(self) -> None:
        """Pause data collection (display continues)"""
        self._paused = True
        logger.info("Dashboard monitoring paused")

    def resume_monitoring(self) -> None:
        """Resume data collection"""
        self._paused = False
        logger.info("Dashboard monitoring resumed")

    def set_refresh_rate(self, rate: float) -> None:
        """
        Set dashboard refresh rate

        Args:
            rate: Refresh rate in seconds (1-10 seconds)
        """
        self._refresh_rate = max(1.0, min(10.0, rate))
        logger.info(f"Dashboard refresh rate set to {self._refresh_rate}s")

    def export_snapshot(self, filename: Optional[str] = None) -> str:
        """
        Export current monitoring data to file

        Args:
            filename: Output filename (generates timestamp-based name if None)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hardware_monitoring_snapshot_{timestamp}.json"

        # Prepare export data
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "refresh_rate": self._refresh_rate,
            "metrics_count": len(self._metrics_history),
            "metrics_history": [metrics.to_dict() for metrics in self._metrics_history],
        }

        # Write to file
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Monitoring snapshot exported to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Failed to export snapshot: {e}")
            raise

    def get_current_metrics(self) -> Optional[HardwareMetrics]:
        """Get the most recent metrics"""
        return self._metrics_history[-1] if self._metrics_history else None

    def get_metrics_history(self) -> List[HardwareMetrics]:
        """Get metrics history"""
        return self._metrics_history.copy()

    @asynccontextmanager
    async def monitoring_session(self, refresh_rate: float = 2.0) -> AsyncIterator[None]:
        """
        Context manager for monitoring sessions

        Args:
            refresh_rate: Refresh interval in seconds
        """
        monitoring_task: Optional[asyncio.Task[None]] = None
        try:
            # Start monitoring in background task
            monitoring_task = asyncio.create_task(self.start_monitoring(refresh_rate))
            yield
        finally:
            # Stop monitoring
            self.stop_monitoring()
            if monitoring_task is not None and not monitoring_task.done():
                monitoring_task.cancel()
                try:
                    await monitoring_task
                except asyncio.CancelledError:
                    pass


# Example usage and integration functions
async def demo_dashboard(hardware_facade: HardwareServiceFacade) -> None:
    """
    Demonstration of the hardware monitoring dashboard

    Args:
        hardware_facade: Hardware service facade instance
    """
    console = Console()
    dashboard = HardwareMonitoringDashboard(hardware_facade, console)

    console.print("[bold green]Starting Hardware Monitoring Dashboard Demo[/bold green]")
    console.print("Press Ctrl+C to stop monitoring\n")

    try:
        await dashboard.start_monitoring(refresh_rate=1.0)
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard demo stopped by user[/yellow]")

    # Export snapshot after demo
    try:
        snapshot_file = dashboard.export_snapshot()
        console.print(f"[green]Monitoring data exported to: {snapshot_file}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to export snapshot: {e}[/red]")


def create_dashboard_manager(
    hardware_facade: HardwareServiceFacade, console: Console
) -> HardwareMonitoringDashboard:
    """
    Factory function to create a configured dashboard manager

    Args:
        hardware_facade: Hardware service facade instance
        console: Rich console instance

    Returns:
        Configured HardwareMonitoringDashboard instance
    """
    return HardwareMonitoringDashboard(hardware_facade, console)
