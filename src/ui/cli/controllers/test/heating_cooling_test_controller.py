"""
Heating/Cooling Time Test Controller

CLI controller for managing heating/cooling time measurement tests.
"""

# Standard library imports
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, Optional

# Third-party imports
from rich.console import Console
from rich.table import Table
import yaml

# Local application imports
from application.use_cases.heating_cooling_time_test import (
    HeatingCoolingTimeTestInput,
    HeatingCoolingTimeTestResult,
    HeatingCoolingTimeTestUseCase,
)
from ui.cli.rich_formatter import RichFormatter


class HeatingCoolingTestController:
    """Controller for Heating/Cooling Time Tests"""

    def __init__(
        self,
        use_case: HeatingCoolingTimeTestUseCase,
        formatter: RichFormatter,
        console: Optional[Console] = None,
    ):
        """
        Initialize Heating/Cooling Test Controller

        Args:
            use_case: Heating/cooling time test use case
            formatter: Rich formatter for output
            console: Rich console for output (optional)
        """
        self.use_case = use_case
        self.formatter = formatter
        self.console = console or Console()

    async def run_test(self, repeat_count: int = 1) -> None:
        """
        Run heating/cooling time measurement test

        Args:
            repeat_count: Number of heating/cooling cycles to perform
        """
        try:

            # Brief pause to ensure panels are fully rendered before log output begins
            # Third-party imports
            import asyncio

            await asyncio.sleep(0.1)

            # Create and execute command
            command = HeatingCoolingTimeTestInput(operator_id="cli_user", repeat_count=repeat_count)

            # Execute test without spinner to avoid log interference
            result = await self.use_case.execute(command)

            # Display results
            self._display_test_results(result)

            # Save results to file
            await self._save_results_to_file(result)

        except KeyboardInterrupt:
            self.formatter.print_message(
                "Test interrupted by user. Cleaning up hardware...", message_type="warning"
            )
            # Use case cleanup will be handled by BaseUseCase's finally block and custom cleanup
            raise
        except Exception as e:
            self.formatter.print_message(f"Test execution failed: {str(e)}", message_type="error")

    def _display_test_results(self, result: HeatingCoolingTimeTestResult) -> None:
        """Display test results in formatted tables"""

        if not result.is_success:
            self.formatter.print_message(
                f"Test failed: {result.error_message}", message_type="error"
            )
            return

        measurements = result.measurements
        config = measurements.get("configuration", {})
        stats = measurements.get("statistics", {})

        # Test Summary
        self.formatter.print_message("Test Summary", message_type="info", title="Test Summary")

        summary_table = Table(title="Test Configuration & Results")
        summary_table.add_column("Parameter", style="cyan")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Test ID", str(result.test_id))
        summary_table.add_row("Test Duration", result.format_duration())
        summary_table.add_row(
            "Temperature Range",
            f"{config.get('standby_temperature', 'N/A')}°C ↔ {config.get('activation_temperature', 'N/A')}°C",
        )
        summary_table.add_row(
            "Power Supply", f"{config.get('voltage', 'N/A')}V / {config.get('current', 'N/A')}A"
        )
        summary_table.add_row("Fan Speed", str(config.get("fan_speed", "N/A")))
        summary_table.add_row("Cycles Performed", str(stats.get("total_cycles", "N/A")))

        self.console.print(summary_table)

        # Statistics Summary
        self.console.print("\n[bold cyan]Performance Statistics[/bold cyan]")

        stats_table = Table(title="Timing Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Heating", style="yellow")
        stats_table.add_column("Cooling", style="bright_cyan")

        avg_heating = stats.get("average_heating_time_ms", 0)
        avg_cooling = stats.get("average_cooling_time_ms", 0)
        avg_heating_ack = stats.get("average_heating_ack_ms", 0)
        avg_cooling_ack = stats.get("average_cooling_ack_ms", 0)

        stats_table.add_row(
            "Average ACK Time", f"{avg_heating_ack/1000:.3f}s", f"{avg_cooling_ack/1000:.3f}s"
        )
        stats_table.add_row(
            "Average Total Time", f"{avg_heating/1000:.1f}s", f"{avg_cooling/1000:.1f}s"
        )
        stats_table.add_row(
            "Cycles Completed",
            str(stats.get("total_heating_cycles", 0)),
            str(stats.get("total_cooling_cycles", 0)),
        )

        self.console.print(stats_table)

        # Full Cycle Power Analysis
        self._display_full_cycle_power_analysis(measurements)

        # Power Consumption Summary
        self._display_power_summary(stats)

        # Detailed measurements (if requested)
        if result.heating_count > 0 or result.cooling_count > 0:
            self._display_detailed_measurements(measurements)

    def _display_detailed_measurements(self, measurements: Dict) -> None:
        """Display detailed measurement data"""

        heating_measurements = measurements.get("heating_measurements", [])
        cooling_measurements = measurements.get("cooling_measurements", [])

        if heating_measurements:
            self.console.print("\n[bold yellow]Heating Measurements[/bold yellow]")
            heating_table = Table(title="Heating Cycle Details")
            heating_table.add_column("Cycle", style="cyan")
            heating_table.add_column("Transition", style="white")
            heating_table.add_column("ACK Time (s)", style="yellow")
            heating_table.add_column("Total Time (s)", style="bright_green")
            heating_table.add_column("Timestamp", style="dim")

            for i, measurement in enumerate(heating_measurements, 1):
                heating_table.add_row(
                    str(i),
                    measurement.get("transition", "N/A"),
                    f"{measurement.get('ack_duration_ms', 0)/1000:.3f}",
                    f"{measurement.get('total_duration_ms', 0)/1000:.1f}",
                    measurement.get("timestamp", "N/A")[:19].replace("T", " "),
                )

            self.console.print(heating_table)

        if cooling_measurements:
            self.console.print("\n[bold blue]Cooling Measurements[/bold blue]")
            cooling_table = Table(title="Cooling Cycle Details")
            cooling_table.add_column("Cycle", style="cyan")
            cooling_table.add_column("Transition", style="white")
            cooling_table.add_column("ACK Time (s)", style="yellow")
            cooling_table.add_column("Total Time (s)", style="bright_cyan")
            cooling_table.add_column("Timestamp", style="dim")

            for i, measurement in enumerate(cooling_measurements, 1):
                cooling_table.add_row(
                    str(i),
                    measurement.get("transition", "N/A"),
                    f"{measurement.get('ack_duration_ms', 0)/1000:.3f}",
                    f"{measurement.get('total_duration_ms', 0)/1000:.1f}",
                    measurement.get("timestamp", "N/A")[:19].replace("T", " "),
                )

            self.console.print(cooling_table)

    def _display_full_cycle_power_analysis(self, measurements: Dict) -> None:
        """Display full cycle power analysis"""

        full_cycle_power = measurements.get("full_cycle_power_data", {})
        if not full_cycle_power or full_cycle_power.get("sample_count", 0) == 0:
            return

        # Get configuration information for accurate interval display
        config = measurements.get("configuration", {})
        power_monitoring_interval = config.get("power_monitoring_interval", 0.5)

        self.console.print("\n[bold cyan]Full Cycle Power Analysis[/bold cyan]")

        power_analysis_table = Table(title="Complete Test Power Measurements")
        power_analysis_table.add_column("Metric", style="cyan")
        power_analysis_table.add_column("Value", style="white")
        power_analysis_table.add_column("Details", style="dim")

        avg_power = full_cycle_power.get("average_power_watts", 0)
        peak_power = full_cycle_power.get("peak_power_watts", 0)
        min_power = full_cycle_power.get("min_power_watts", 0)
        total_energy = full_cycle_power.get("total_energy_wh", 0)
        samples = full_cycle_power.get("sample_count", 0)

        # Use full monitoring period (includes delays) to match energy calculation basis
        duration = full_cycle_power.get("duration_seconds", 0)

        power_analysis_table.add_row(
            "Average Power", f"{avg_power:.1f}W", "Mean power throughout entire test"
        )
        power_analysis_table.add_row(
            "Peak Power", f"{peak_power:.1f}W", "Maximum instantaneous power"
        )
        power_analysis_table.add_row(
            "Minimum Power", f"{min_power:.1f}W", "Lowest instantaneous power"
        )
        power_analysis_table.add_row(
            "Total Energy", f"{total_energy:.4f}Wh", "Energy consumed during complete test cycle"
        )
        power_analysis_table.add_row(
            "Measurement Duration",
            f"{duration:.1f}s",
            "Complete power monitoring period (includes delays)",
        )
        power_analysis_table.add_row(
            "Sample Count",
            str(samples),
            f"Data points collected at {power_monitoring_interval}s intervals",
        )

        self.console.print(power_analysis_table)

    def _display_power_summary(self, stats: Dict) -> None:
        """Display power consumption summary"""

        self.console.print("\n[bold green]Power Consumption Analysis[/bold green]")

        power_table = Table(title="Energy Efficiency Summary")
        power_table.add_column("Metric", style="cyan")
        power_table.add_column("Value", style="white")

        total_energy = stats.get("total_energy_consumed_wh", 0)
        # Full cycle monitoring doesn't separate heating/cooling energy
        heating_energy = total_energy / 2 if total_energy > 0 else 0  # Approximate split
        cooling_energy = total_energy / 2 if total_energy > 0 else 0  # Approximate split
        power_ratio = stats.get("power_ratio_heating_to_cooling", 0)

        power_table.add_row("Total Energy Consumed", f"{total_energy:.3f} Wh")
        power_table.add_row(
            "Heating Energy",
            (
                f"{heating_energy:.3f} Wh ({heating_energy/total_energy*100:.1f}%)"
                if total_energy > 0
                else "0 Wh"
            ),
        )
        power_table.add_row(
            "Cooling Energy",
            (
                f"{cooling_energy:.3f} Wh ({cooling_energy/total_energy*100:.1f}%)"
                if total_energy > 0
                else "0 Wh"
            ),
        )
        power_table.add_row(
            "Power Ratio (H:C)", f"{power_ratio:.1f}:1" if power_ratio > 0 else "N/A"
        )

        self.console.print(power_table)

    async def _save_results_to_file(self, result: HeatingCoolingTimeTestResult) -> None:
        """Save test results to JSON file"""
        try:
            self.formatter.print_message("Starting to save test results to file...", message_type="info")
            self.formatter.print_message(f"Test success status: {result.is_success}", message_type="info")
            self.formatter.print_message(f"Test ID: {result.test_id}", message_type="info")

            # Create results directory
            results_dir = Path("logs/Heating Cooling Test/power_measurements")
            self.formatter.print_message(f"Creating directory: {results_dir.absolute()}", message_type="info")
            results_dir.mkdir(parents=True, exist_ok=True)
            self.formatter.print_message(f"Directory created successfully: {results_dir.exists()}", message_type="info")

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"heating_cooling_test_{timestamp}_{result.test_id}.json"
            file_path = results_dir / filename
            self.formatter.print_message(f"Generated file path: {file_path.absolute()}", message_type="info")

            # Prepare data for JSON
            json_data = {
                "test_id": str(result.test_id),
                "test_type": "heating_cooling_time_test",
                "timestamp": datetime.now().isoformat(),
                "test_status": result.test_status.name,
                "is_passed": result.is_success,
                "execution_duration_seconds": (
                    result.execution_duration.seconds if result.execution_duration else 0
                ),
                "measurements": result.measurements,
                "error_message": result.error_message,
            }

            # Save to file
            self.formatter.print_message("Writing JSON data to file...", message_type="info")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            self.formatter.print_message(f"File written successfully. Size: {file_path.stat().st_size} bytes", message_type="info")
            self.formatter.print_message(f"Results saved to: {file_path}", message_type="success")

        except Exception as e:
            self.formatter.print_message(
                f"Failed to save results to file: {e}", message_type="warning"
            )

    def show_help(self) -> None:
        """Show help information about the heating/cooling test"""

        help_text = """
[bold cyan]Heating/Cooling Time Test[/bold cyan]

This test measures the time taken for MCU temperature transitions:
• [yellow]Heating:[/yellow] Standby Temperature → Activation Temperature
• [blue]Cooling:[/blue] Activation Temperature → Standby Temperature

[bold]What is measured:[/bold]
• [yellow]ACK Time:[/yellow] Time from command sent to ACK received (~0.040-0.050s)
• [green]Total Time:[/green] Time from command sent to temperature reached (~8-18s)

[bold]Test Process:[/bold]
1. Connect and setup Power Supply + MCU
2. Wait for MCU boot completion
3. Set initial temperature to standby
4. Perform specified number of heating/cooling cycles
5. Measure and record all timing data
6. Calculate statistics and save results

[bold]Configuration:[/bold]
• Temperature range from test profile (default: 38°C ↔ 52°C)
• Power supply settings from configuration
• Fan speed and timing delays from configuration

[bold]Results:[/bold]
• Detailed timing measurements for each cycle
• Average performance statistics
• Results saved to logs/Heating Cooling Test/power_measurements/ directory
"""

        self.console.print(help_text)

    def get_cycle_count_from_config(self) -> int:
        """Get cycle count from configuration file"""
        config_file = Path("configuration/heating_cooling_time_test.yaml")

        try:
            if config_file.exists():
                self.formatter.print_message(
                    f"Loading cycle count from {config_file}", message_type="info"
                )

                with open(config_file, "r", encoding="utf-8") as f:
                    yaml_data = yaml.safe_load(f)

                repeat_count = yaml_data.get("repeat_count", 1)
                self.formatter.print_message(
                    f"Configuration: {repeat_count} cycles", message_type="info"
                )
                return repeat_count
            else:
                self.formatter.print_message(
                    "Configuration file not found, using default: 1 cycle", message_type="warning"
                )
                return 1

        except Exception as e:
            self.formatter.print_message(
                f"Failed to load configuration: {e}, using default: 1 cycle", message_type="warning"
            )
            return 1
