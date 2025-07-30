"""
Dashboard Integration Helper for Enhanced EOL Tester CLI

This module provides integration functions and menu handlers to seamlessly
add the hardware monitoring dashboard to the Enhanced CLI system. It handles
dashboard lifecycle, configuration, and provides a user-friendly interface
for dashboard operations.

Key Features:
- Seamless integration with existing Enhanced CLI
- Dashboard configuration and settings management
- Menu integration with proper error handling
- Export functionality with user feedback
- Graceful startup and shutdown handling
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from application.services.hardware_service_facade import HardwareServiceFacade

from .hardware_monitoring_dashboard import (
    HardwareMonitoringDashboard,
    create_dashboard_manager,
)
from .rich_formatter import RichFormatter


class DashboardIntegrator:
    """
    Handles integration of the hardware monitoring dashboard with the Enhanced CLI
    """

    def __init__(
        self, hardware_facade: HardwareServiceFacade, console: Console, formatter: RichFormatter
    ) -> None:
        """
        Initialize the dashboard integrator

        Args:
            hardware_facade: Hardware service facade for data collection
            console: Rich console instance
            formatter: Rich formatter for consistent styling
        """
        self._hardware_facade = hardware_facade
        self._console = console
        self._formatter = formatter
        self._dashboard: Optional[HardwareMonitoringDashboard] = None

        # Default dashboard settings
        self._default_refresh_rate: float = 2.0
        self._export_directory: Path = Path("dashboard_exports")

        # Ensure export directory exists
        self._export_directory.mkdir(exist_ok=True)

    async def show_dashboard_menu(self) -> None:
        """Show the dashboard menu and handle user selections"""
        while True:
            try:
                # Display dashboard menu
                menu_content = """
[bold cyan]1.[/bold cyan] Start Real-time Monitoring Dashboard
[bold cyan]2.[/bold cyan] Configure Dashboard Settings
[bold cyan]3.[/bold cyan] View Last Monitoring Session Data
[bold cyan]4.[/bold cyan] Export Historical Data
[bold cyan]5.[/bold cyan] Dashboard Help & Information
[bold cyan]b.[/bold cyan] Back to Main Menu

Please select an option (1-5, b):"""

                self._console.print("\n")
                menu_panel = self._formatter.create_message_panel(
                    menu_content, message_type="info", title="📊 Hardware Monitoring Dashboard"
                )
                self._console.print(menu_panel)

                # Get user selection
                choice = input().strip().lower()

                if choice == "1":
                    await self._start_monitoring_dashboard()
                elif choice == "2":
                    await self._configure_dashboard_settings()
                elif choice == "3":
                    await self._view_last_session_data()
                elif choice == "4":
                    await self._export_historical_data()
                elif choice == "5":
                    await self._show_dashboard_help()
                elif choice == "b":
                    break
                else:
                    self._formatter.print_message(
                        f"Invalid option '{choice}'. Please select 1-5 or 'b'.",
                        message_type="warning",
                    )

            except (KeyboardInterrupt, EOFError):
                break
            except OSError as e:
                self._formatter.print_message(
                    f"System error in dashboard menu: {str(e)}", message_type="error"
                )
                logger.error("Dashboard menu system error: %s", e)
            except Exception as e:
                self._formatter.print_message(
                    f"Unexpected dashboard menu error: {str(e)}", message_type="error"
                )
                logger.error("Dashboard menu unexpected error: %s", e)

    async def _start_monitoring_dashboard(self) -> None:
        """Start the real-time monitoring dashboard"""
        self._formatter.print_header(
            "Real-time Hardware Monitoring Dashboard", "Live hardware status and metrics display"
        )

        # Show pre-start information
        info_panel = self._formatter.create_message_panel(
            f"""Starting real-time hardware monitoring with the following settings:

• Refresh Rate: {self._default_refresh_rate} seconds
• Data Collection: All connected hardware components
• Display: Live updating dashboard with color-coded status
• Controls: Press Ctrl+C to stop monitoring

The dashboard will automatically detect hardware connections and
display real-time metrics for Robot, MCU, LoadCell, and Power systems.""",
            message_type="info",
            title="Dashboard Configuration",
        )
        self._console.print(info_panel)

        # Confirmation prompt
        self._console.print(
            "\n[bold yellow]Press Enter to start monitoring or Ctrl+C to cancel...[/bold yellow]"
        )
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            self._formatter.print_message("Dashboard startup cancelled", message_type="info")
            return

        # Initialize dashboard
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=self._console,
                transient=True,
            ) as progress:
                task = progress.add_task("Initializing dashboard...", total=None)

                # Create dashboard instance
                self._dashboard = create_dashboard_manager(self._hardware_facade, self._console)

                progress.update(task, description="Checking hardware connections...")
                await asyncio.sleep(0.5)  # Brief pause for user experience

                progress.update(task, description="Starting monitoring dashboard...")
                await asyncio.sleep(0.5)

            # Start the dashboard
            await self._dashboard.start_monitoring(refresh_rate=self._default_refresh_rate)

        except KeyboardInterrupt:
            self._formatter.print_message(
                "Dashboard monitoring stopped by user",
                message_type="info",
                title="Monitoring Stopped",
            )
        except ImportError as e:
            self._formatter.print_message(
                f"Missing dashboard component: {str(e)}",
                message_type="error",
                title="Import Error",
            )
            logger.error("Dashboard import error: %s", e)
        except AttributeError as e:
            self._formatter.print_message(
                f"Dashboard method not available: {str(e)}",
                message_type="error",
                title="Method Error",
            )
            logger.error("Dashboard method error: %s", e)
        except OSError as e:
            self._formatter.print_message(
                f"System resource error: {str(e)}",
                message_type="error",
                title="System Error",
            )
            logger.error("Dashboard system error: %s", e)
        except Exception as e:
            self._formatter.print_message(
                f"Unexpected dashboard error: {str(e)}",
                message_type="error",
                title="Dashboard Error",
            )
            logger.error("Dashboard unexpected error: %s", e)

        # Post-monitoring actions
        await self._post_monitoring_actions()

    async def _post_monitoring_actions(self) -> None:
        """Handle actions after monitoring session ends"""
        if not self._dashboard:
            return

        # Check if we have data to export
        history_count = len(self._dashboard.get_metrics_history())

        if history_count > 0:
            self._console.print(
                f"\n[green]Monitoring session completed with {history_count} data points collected.[/green]"
            )

            # Offer to export data
            export_panel = self._formatter.create_message_panel(
                f"""Would you like to export the monitoring session data?

Session Summary:
• Duration: {history_count * self._default_refresh_rate:.0f} seconds
• Data Points: {history_count}
• Last Update: {datetime.now().strftime('%H:%M:%S')}

Export options:
• [bold green]y[/bold green] - Export session data to file
• [bold red]n[/bold red] - Discard session data
• [bold yellow]v[/bold yellow] - View session summary first""",
                message_type="info",
                title="Export Session Data?",
            )
            self._console.print(export_panel)

            try:
                choice: str = input("Your choice (y/n/v): ").strip().lower()

                if choice == "y":
                    await self._export_current_session()
                elif choice == "v":
                    await self._show_session_summary()
                    # Ask again after showing summary
                    export_choice: str = input("Export data? (y/n): ").strip().lower()
                    if export_choice == "y":
                        await self._export_current_session()
                else:
                    self._formatter.print_message("Session data discarded", message_type="info")

            except (KeyboardInterrupt, EOFError):
                self._formatter.print_message("Session data discarded", message_type="info")
        else:
            self._formatter.print_message("No monitoring data collected", message_type="warning")

    async def _export_current_session(self) -> None:
        """Export current session data"""
        if not self._dashboard:
            return

        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self._export_directory / f"monitoring_session_{timestamp}.json"

            # Export data
            exported_file = self._dashboard.export_snapshot(str(filename))

            self._formatter.print_message(
                f"Session data exported successfully to: {exported_file}",
                message_type="success",
                title="Export Complete",
            )

        except PermissionError as e:
            self._formatter.print_message(
                f"Permission denied for export: {str(e)}",
                message_type="error",
                title="Permission Error",
            )
            logger.error("Session export permission error: %s", e)
        except FileNotFoundError as e:
            self._formatter.print_message(
                f"Export directory not found: {str(e)}",
                message_type="error",
                title="Directory Error",
            )
            logger.error("Session export directory error: %s", e)
        except OSError as e:
            self._formatter.print_message(
                f"System error during export: {str(e)}",
                message_type="error",
                title="System Error",
            )
            logger.error("Session export system error: %s", e)
        except Exception as e:
            self._formatter.print_message(
                f"Unexpected export error: {str(e)}",
                message_type="error",
                title="Export Failed",
            )
            logger.error("Session export unexpected error: %s", e)

    async def _show_session_summary(self) -> None:
        """Show summary of current monitoring session"""
        if not self._dashboard:
            return

        history = self._dashboard.get_metrics_history()
        if not history:
            self._formatter.print_message("No session data available", message_type="warning")
            return

        # Calculate session statistics
        duration: float = len(history) * self._default_refresh_rate
        start_time: datetime = datetime.fromtimestamp(history[0].timestamp)
        end_time: datetime = datetime.fromtimestamp(history[-1].timestamp)

        # Connection statistics
        robot_uptime: float = sum(1 for m in history if m.robot_connected) / len(history) * 100
        mcu_uptime: float = sum(1 for m in history if m.mcu_connected) / len(history) * 100
        loadcell_uptime: float = (
            sum(1 for m in history if m.loadcell_connected) / len(history) * 100
        )
        power_uptime: float = sum(1 for m in history if m.power_connected) / len(history) * 100

        # Create summary table
        summary_table = Table(title="Monitoring Session Summary", box=None)
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Value", style="cyan")

        summary_table.add_row("Session Duration", f"{duration:.0f} seconds")
        summary_table.add_row("Start Time", start_time.strftime("%Y-%m-%d %H:%M:%S"))
        summary_table.add_row("End Time", end_time.strftime("%Y-%m-%d %H:%M:%S"))
        summary_table.add_row("Data Points", str(len(history)))
        summary_table.add_row("", "")  # Separator
        summary_table.add_row("Robot Uptime", f"{robot_uptime:.1f}%")
        summary_table.add_row("MCU Uptime", f"{mcu_uptime:.1f}%")
        summary_table.add_row("LoadCell Uptime", f"{loadcell_uptime:.1f}%")
        summary_table.add_row("Power Uptime", f"{power_uptime:.1f}%")

        self._console.print("\n")
        self._console.print(summary_table)

        # Show latest metrics
        latest = history[-1]
        status_panel = self._formatter.create_message_panel(
            f"""Latest Hardware Status:

Robot: {'Connected' if latest.robot_connected else 'Disconnected'}
  Position: {latest.robot_position:.3f} mm (if connected)

MCU: {'Connected' if latest.mcu_connected else 'Disconnected'}
  Temperature: {latest.mcu_temperature:.1f}°C (if connected)

LoadCell: {'Connected' if latest.loadcell_connected else 'Disconnected'}
  Force: {latest.loadcell_force:.4f} N (if connected)

Power: {'Connected' if latest.power_connected else 'Disconnected'}
  Voltage: {latest.power_voltage:.2f} V (if connected)
  Output: {'Enabled' if latest.power_output_enabled else 'Disabled'}""",
            message_type="info",
            title="Current Hardware Status",
        )
        self._console.print(status_panel)

    async def _configure_dashboard_settings(self) -> None:
        """Configure dashboard settings"""
        self._formatter.print_header("Dashboard Settings Configuration")

        # Show current settings
        settings_table = Table(title="Current Settings", box=None)
        settings_table.add_column("Setting", style="bold")
        settings_table.add_column("Value", style="cyan")

        settings_table.add_row("Refresh Rate", f"{self._default_refresh_rate} seconds")
        settings_table.add_row("Export Directory", str(self._export_directory))

        self._console.print(settings_table)
        self._console.print()

        # Configuration menu
        config_menu = """
[bold cyan]1.[/bold cyan] Change Refresh Rate (1-10 seconds)
[bold cyan]2.[/bold cyan] Change Export Directory
[bold cyan]3.[/bold cyan] Reset to Defaults
[bold cyan]b.[/bold cyan] Back to Dashboard Menu

Select option (1-3, b):"""

        self._console.print(Panel(config_menu, title="Configuration Options"))

        try:
            choice = input().strip().lower()

            if choice == "1":
                await self._configure_refresh_rate()
            elif choice == "2":
                await self._configure_export_directory()
            elif choice == "3":
                await self._reset_dashboard_settings()
            elif choice != "b":
                self._formatter.print_message(
                    f"Invalid option '{choice}'. Please select 1-3 or 'b'.", message_type="warning"
                )

        except (KeyboardInterrupt, EOFError):
            pass

    async def _configure_refresh_rate(self) -> None:
        """Configure dashboard refresh rate"""
        self._console.print(
            f"[bold cyan]Current refresh rate:[/bold cyan] {self._default_refresh_rate:.1f} seconds"
        )
        self._console.print("[dim]Enter new refresh rate (1.0 - 10.0 seconds):[/dim]")

        try:
            rate_input: str = input("New refresh rate: ").strip()
            rate: float = float(rate_input)

            if 1.0 <= rate <= 10.0:
                self._default_refresh_rate = rate
                self._formatter.print_message(
                    f"Refresh rate updated to {rate:.1f} seconds", message_type="success"
                )
            else:
                self._formatter.print_message(
                    "Refresh rate must be between 1.0 and 10.0 seconds", message_type="error"
                )
        except ValueError:
            self._formatter.print_message(
                "Invalid number format. Please enter a decimal number.", message_type="error"
            )
        except (KeyboardInterrupt, EOFError):
            pass

    async def _configure_export_directory(self) -> None:
        """Configure export directory"""
        self._console.print(
            f"[bold cyan]Current export directory:[/bold cyan] {self._export_directory}"
        )
        self._console.print("[dim]Enter new export directory path:[/dim]")

        try:
            path_input: str = input("New export directory: ").strip()

            if path_input:
                new_path: Path = Path(path_input)
                try:
                    new_path.mkdir(parents=True, exist_ok=True)
                    self._export_directory = new_path
                    self._formatter.print_message(
                        f"Export directory updated to: {new_path}", message_type="success"
                    )
                except PermissionError as e:
                    self._formatter.print_message(
                        f"Permission denied to create directory: {str(e)}", message_type="error"
                    )
                except OSError as e:
                    self._formatter.print_message(
                        f"System error creating directory: {str(e)}", message_type="error"
                    )
                except Exception as e:
                    self._formatter.print_message(
                        f"Unexpected error creating directory: {str(e)}", message_type="error"
                    )
            else:
                self._formatter.print_message(
                    "Directory path cannot be empty", message_type="warning"
                )

        except (KeyboardInterrupt, EOFError):
            pass

    async def _reset_dashboard_settings(self) -> None:
        """Reset dashboard settings to defaults"""
        self._console.print("[bold yellow]Reset all dashboard settings to defaults?[/bold yellow]")

        try:
            confirm = input("Confirm reset (y/n): ").strip().lower()

            if confirm == "y":
                self._default_refresh_rate = 2.0
                self._export_directory = Path("dashboard_exports")
                self._export_directory.mkdir(exist_ok=True)

                self._formatter.print_message(
                    "Dashboard settings reset to defaults", message_type="success"
                )
            else:
                self._formatter.print_message("Settings reset cancelled", message_type="info")

        except (KeyboardInterrupt, EOFError):
            pass

    async def _view_last_session_data(self) -> None:
        """View data from the last monitoring session"""
        if not self._dashboard or not self._dashboard.get_metrics_history():
            self._formatter.print_message(
                "No monitoring session data available. Start a monitoring session first.",
                message_type="warning",
                title="No Data",
            )
            return

        await self._show_session_summary()

        # Wait for user acknowledgment
        self._console.print("\n[dim]Press Enter to continue...[/dim]")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            pass

    async def _export_historical_data(self) -> None:
        """Export historical monitoring data"""
        if not self._dashboard or not self._dashboard.get_metrics_history():
            self._formatter.print_message(
                "No historical data available to export", message_type="warning", title="No Data"
            )
            return

        try:
            # Export with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self._export_directory / f"historical_data_{timestamp}.json"

            exported_file = self._dashboard.export_snapshot(str(filename))

            self._formatter.print_message(
                f"Historical data exported to: {exported_file}",
                message_type="success",
                title="Export Complete",
            )

        except Exception as e:
            self._formatter.print_message(
                f"Failed to export historical data: {str(e)}",
                message_type="error",
                title="Export Failed",
            )
            logger.error("Historical data export error: %s", e)

    async def _show_dashboard_help(self) -> None:
        """Show dashboard help and information"""
        self._formatter.print_header("Hardware Monitoring Dashboard Help")

        help_content = """
[bold]Real-time Hardware Monitoring Dashboard[/bold]

The dashboard provides live monitoring of all hardware components in the EOL testing system:

[bold cyan]Features:[/bold cyan]
• Real-time status updates for Robot, MCU, LoadCell, and Power components
• Color-coded connection indicators (Green=Connected, Red=Disconnected)
• Live metrics display with current values and status information
• Automatic error recovery and connection retry logic
• Session data export for analysis and reporting

[bold cyan]Hardware Components Monitored:[/bold cyan]

[bold]Robot Controller:[/bold]
  • Connection status and position readings
  • Motion status and velocity information
  • Movement detection with real-time indicators

[bold]MCU (Microcontroller):[/bold]
  • Temperature readings with warning indicators
  • Fan speed and test mode status
  • Thermal status warnings (Normal/Warm/High)

[bold]LoadCell Sensor:[/bold]
  • Real-time force measurements in Newtons
  • Raw ADC values and calibration status
  • Force level indicators and warnings

[bold]Power Supply:[/bold]
  • Voltage and current measurements
  • Output enable/disable status
  • Power level warnings and indicators

[bold cyan]Dashboard Controls:[/bold cyan]
• Press Ctrl+C to stop monitoring and return to menu
• Data is automatically collected at the configured refresh rate
• All session data is stored for potential export

[bold cyan]Configuration Options:[/bold cyan]
• Refresh Rate: 1-10 seconds (default: 2 seconds)
• Export Directory: Customizable location for exported data
• Settings persist during the current CLI session

[bold cyan]Data Export:[/bold cyan]
• JSON format with timestamps and complete metrics history
• Includes session metadata and configuration information
• Suitable for analysis, reporting, and troubleshooting

[bold yellow]Note:[/bold yellow] The dashboard works with both real hardware and mock
implementations for testing purposes. Connection failures are handled
gracefully with automatic retry attempts."""

        help_panel = Panel(
            help_content, title="Dashboard Help & Information", style="bright_white", padding=(1, 2)
        )

        self._console.print(help_panel)

        # Wait for user acknowledgment
        self._console.print("\n[dim]Press Enter to continue...[/dim]")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            pass


def create_dashboard_integrator(
    hardware_facade: HardwareServiceFacade, console: Console, formatter: RichFormatter
) -> DashboardIntegrator:
    """
    Factory function to create a configured dashboard integrator

    Args:
        hardware_facade: Hardware service facade instance
        console: Rich console instance
        formatter: Rich formatter instance

    Returns:
        Configured DashboardIntegrator instance
    """
    return DashboardIntegrator(hardware_facade, console, formatter)
