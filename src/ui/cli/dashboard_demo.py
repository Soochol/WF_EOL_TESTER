#!/usr/bin/env python3
"""
Hardware Monitoring Dashboard Demonstration

This script demonstrates the comprehensive real-time hardware monitoring dashboard
functionality. It can be run standalone to show the dashboard capabilities with
mock hardware, or integrated into the Enhanced CLI system.

Features demonstrated:
- Real-time hardware status monitoring
- Live metrics display with color-coded indicators
- Professional Rich UI formatting
- Error handling and recovery
- Data export functionality
"""

import asyncio
import sys
from pathlib import Path

# Third-party imports
from loguru import logger
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent
sys.path.insert(0, str(src_dir))

# Local application imports (must be after path setup)
# pylint: disable=wrong-import-position
from infrastructure.factory import (
    create_hardware_service_facade,  # pylint: disable=wrong-import-position
)
from ui.cli.dashboard_integration import (
    create_dashboard_integrator,  # pylint: disable=wrong-import-position
)
from ui.cli.hardware_monitoring_dashboard import (
    demo_dashboard,  # pylint: disable=wrong-import-position
)
from ui.cli.rich_formatter import RichFormatter  # pylint: disable=wrong-import-position


class DashboardDemo:
    """
    Comprehensive dashboard demonstration class
    """

    def __init__(self) -> None:
        self.console = Console()
        self.formatter = RichFormatter(self.console)

    async def run_demo(self) -> None:
        """Run the complete dashboard demonstration"""
        logger.info("Starting dashboard demonstration")

        # Show demo header
        self._show_demo_header()

        # Get user choice for demo mode
        demo_choice = self._get_demo_choice()

        if demo_choice == "1":
            logger.info("User selected live dashboard demo")
            await self._run_live_dashboard_demo()
        elif demo_choice == "2":
            logger.info("User selected integration demo")
            await self._run_integration_demo()
        elif demo_choice == "3":
            logger.info("User selected configuration demo")
            await self._run_configuration_demo()
        else:
            logger.info("Dashboard demo cancelled by user")
            self.console.print("[yellow]Demo cancelled[/yellow]")

    def _show_demo_header(self) -> None:
        """Show demonstration header"""
        header_text = Text.assemble(
            ("Hardware Monitoring Dashboard Demo", "bold white"),
            "\n\n",
            ("This demonstration shows the comprehensive real-time hardware monitoring", "dim"),
            "\n",
            ("capabilities of the EOL Tester system with Rich UI formatting.", "dim"),
        )

        header_panel = Panel(
            Align.center(header_text),
            style="bright_blue",
            title="🚀 Dashboard Demo",
            padding=(1, 2),
        )

        self.console.print(header_panel)
        self.console.print()

    def _get_demo_choice(self) -> str:
        """Get user choice for demo mode"""
        choice_panel = Panel(
            """[bold cyan]Demo Options:[/bold cyan]

[bold green]1.[/bold green] Live Dashboard Demo
   • Real-time monitoring with mock hardware
   • Shows live data updates and status indicators
   • Interactive dashboard with color-coded status

[bold green]2.[/bold green] Integration Demo
   • Shows CLI integration features
   • Configuration options and settings
   • Export functionality demonstration

[bold green]3.[/bold green] Configuration Demo
   • Dashboard settings and options
   • Export directory configuration
   • Refresh rate adjustment

[bold green]4.[/bold green] Exit Demo

Please select an option (1-4):""",
            title="Choose Demo Mode",
            style="bright_white",
        )

        self.console.print(choice_panel)

        try:
            choice = input("Your choice: ").strip()
            return choice
        except (KeyboardInterrupt, EOFError):
            return "4"

    async def _run_live_dashboard_demo(self) -> None:
        """Run live dashboard demonstration"""
        self.console.print("[bold green]Starting Live Dashboard Demo...[/bold green]")
        self.console.print()

        # Show information about the demo
        info_panel = Panel(
            """[bold]Live Dashboard Demo Information[/bold]

This demo will start the real-time hardware monitoring dashboard using mock hardware.
You'll see:

• Live connection status for all hardware components
• Real-time metrics updates (temperature, position, force, power)
• Color-coded status indicators
• Professional dashboard layout

The demo uses mock hardware, so all data is simulated but demonstrates the actual
dashboard functionality you'll see with real hardware.

[bold yellow]Controls during demo:[/bold yellow]
• Press Ctrl+C to stop the dashboard and return to this menu
• The dashboard updates automatically at the configured refresh rate
• All data is simulated but represents real hardware behavior

Press Enter to start the dashboard or Ctrl+C to cancel...""",
            title="Live Dashboard Demo",
            style="blue",
        )

        self.console.print(info_panel)

        try:
            input()
        except (KeyboardInterrupt, EOFError):
            self.console.print("[yellow]Demo cancelled[/yellow]")
            return

        # Create hardware facade with mock hardware
        try:
            self.console.print("[dim]Setting up mock hardware...[/dim]")

            # Use factory to create hardware facade
            logger.debug("Creating hardware service facade with mock hardware")
            hardware_facade = create_hardware_service_facade(config_path=None, use_mock=True)

            self.console.print("[dim]Starting dashboard...[/dim]")
            self.console.print()

            # Run the dashboard demo
            logger.info("Starting live dashboard with mock hardware")
            await demo_dashboard(hardware_facade)

        except ImportError as e:
            logger.error("Missing dependency for live dashboard demo: %s", e)
            self.formatter.print_message(
                f"Missing dependency: {str(e)}", message_type="error", title="Import Error"
            )
            self.console.print(
                "\n[yellow]Please ensure all required packages are installed.[/yellow]"
            )
        except FileNotFoundError as e:
            logger.error("Configuration file not found for dashboard demo: %s", e)
            self.formatter.print_message(
                f"Configuration file not found: {str(e)}", message_type="error", title="File Error"
            )
        except KeyboardInterrupt:
            logger.info("Live dashboard demo interrupted by user")
            self.console.print("\n[yellow]Demo interrupted by user[/yellow]")
        except Exception as e:
            logger.error("Live dashboard demo failed with unexpected error: %s", e)
            self.formatter.print_message(
                f"Demo failed: {str(e)}", message_type="error", title="Demo Error"
            )
            self.console.print("\n[dim]Check the logs for more details.[/dim]")

    async def _run_integration_demo(self) -> None:
        """Run integration demonstration"""
        self.console.print("[bold green]Integration Demo[/bold green]")
        self.console.print()

        info_panel = Panel(
            """[bold]Dashboard Integration Features[/bold]

The dashboard integrates seamlessly with the Enhanced CLI system:

[bold cyan]Menu Integration:[/bold cyan]
• Added as option 4 in the main CLI menu
• "Real-time Monitoring Dashboard"
• Full integration with existing CLI systems

[bold cyan]Configuration Management:[/bold cyan]
• Configurable refresh rates (1-10 seconds)
• Customizable export directory
• Settings persistence during CLI session

[bold cyan]Data Export Features:[/bold cyan]
• JSON format with complete metrics history
• Timestamped filenames for organization
• Session summaries with uptime statistics

[bold cyan]Error Handling:[/bold cyan]
• Graceful hardware disconnection handling
• Automatic retry logic for failed connections
• User-friendly error messages and recovery

[bold cyan]Professional UI:[/bold cyan]
• Consistent Rich formatting with CLI theme
• Color-coded status indicators
• Interactive menus and controls""",
            title="Integration Features",
            style="green",
        )

        self.console.print(info_panel)

        # Show integration example
        try:
            logger.debug("Creating hardware facade for integration demo")
            hardware_facade = create_hardware_service_facade(use_mock=True)
            create_dashboard_integrator(hardware_facade, self.console, self.formatter)

            self.console.print()
            self.console.print("[bold]Integration Example - Configuration Menu:[/bold]")

            # This would normally show the actual configuration menu
            # For demo purposes, we'll just show what it looks like
            demo_panel = Panel(
                """[bold cyan]Dashboard Settings Configuration[/bold cyan]

Current Settings:
• Refresh Rate: 2.0 seconds
• Export Directory: ./dashboard_exports

Configuration Options:
1. Change Refresh Rate (1-10 seconds)
2. Change Export Directory
3. Reset to Defaults
b. Back to Dashboard Menu

[dim]This is a demonstration of the actual configuration interface[/dim]""",
                title="Configuration Demo",
                style="cyan",
            )

            self.console.print(demo_panel)

        except ImportError as e:
            logger.error("Missing integration component for dashboard demo: %s", e)
            self.formatter.print_message(
                f"Missing integration component: {str(e)}",
                message_type="error",
                title="Import Error",
            )
        except Exception as e:
            logger.error("Integration demo failed with unexpected error: %s", e)
            self.formatter.print_message(
                f"Integration demo failed: {str(e)}",
                message_type="error",
                title="Integration Error",
            )

        self.console.print("\n[dim]Press Enter to continue...[/dim]")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            pass

    async def _run_configuration_demo(self) -> None:
        """Run configuration demonstration"""
        self.console.print("[bold green]Configuration Demo[/bold green]")
        self.console.print()

        config_panel = Panel(
            """[bold]Dashboard Configuration Options[/bold]

[bold cyan]Refresh Rate Configuration:[/bold cyan]
• Range: 1.0 - 10.0 seconds
• Default: 2.0 seconds
• Affects data collection frequency and UI update rate
• Lower rates provide more responsive monitoring
• Higher rates reduce system load

[bold cyan]Export Directory Configuration:[/bold cyan]
• Default: ./dashboard_exports
• Customizable to any accessible directory
• Creates directory if it doesn't exist
• Used for session data and snapshot exports

[bold cyan]Data Management:[/bold cyan]
• Automatic history limiting (100 data points max)
• Memory-efficient data storage
• JSON export format with metadata
• Session summaries with statistics

[bold cyan]Reset Options:[/bold cyan]
• Reset all settings to defaults
• Confirmation required for safety
• Immediate effect on current session

[bold yellow]Example Configuration Values:[/bold yellow]
• Refresh Rate: 1.5 seconds (responsive monitoring)
• Export Directory: /home/user/eol_data/dashboard
• Memory Limit: 100 data points (approximately 3-17 minutes of data)

The configuration system ensures optimal performance while providing
flexibility for different monitoring scenarios and system requirements.""",
            title="Configuration Details",
            style="magenta",
        )

        self.console.print(config_panel)

        self.console.print("\n[dim]Press Enter to continue...[/dim]")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            pass


async def main() -> None:
    """Main demo function"""
    try:
        demo = DashboardDemo()
        await demo.run_demo()
    except KeyboardInterrupt:
        logger.info("Dashboard demo interrupted by user")
        print("\n[yellow]Demo interrupted by user[/yellow]")
    except ImportError as e:
        logger.error("Import error in dashboard demo main: %s", e)
        print(f"[red]Import error: {e}[/red]")
        print("[yellow]Please ensure all required dependencies are installed.[/yellow]")
    except Exception as e:
        logger.error("Dashboard demo main failed with unexpected error: %s", e)
        print(f"[red]Demo failed: {e}[/red]")
        print("[dim]Run with debug mode for more details.[/dim]")


if __name__ == "__main__":
    asyncio.run(main())
