"""
Heating/Cooling Time Test Controller

CLI controller for managing heating/cooling time measurement tests.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from application.use_cases.heating_cooling_time_test import (
    HeatingCoolingTimeTestCommand,
    HeatingCoolingTimeTestResult,
    HeatingCoolingTimeTestUseCase,
)
from domain.value_objects.heating_cooling_configuration import HeatingCoolingConfiguration
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
            # Display test header
            self.formatter.print_header("Heating/Cooling Time Test")
            self.formatter.print_message(f"Test cycles: {repeat_count}")
            self.formatter.print_message("This test measures MCU temperature transition times")

            # Create and execute command
            command = HeatingCoolingTimeTestCommand(
                operator_id="cli_user", repeat_count=repeat_count
            )

            # Show progress during test execution
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True,
            ) as progress:
                task = progress.add_task("Running heating/cooling test...", total=None)

                result = await self.use_case.execute(command)

                progress.update(task, description="Test completed!")

            # Display results
            self._display_test_results(result)

            # Save results to file
            await self._save_results_to_file(result)

        except Exception as e:
            self.formatter.print_message(f"Test execution failed: {str(e)}", message_type="error")

    def _display_test_results(self, result: HeatingCoolingTimeTestResult) -> None:
        """Display test results in formatted tables"""

        if not result.is_passed:
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
            "Average ACK Time", f"{avg_heating_ack:.1f}ms", f"{avg_cooling_ack:.1f}ms"
        )
        stats_table.add_row("Average Total Time", f"{avg_heating:.1f}ms", f"{avg_cooling:.1f}ms")
        stats_table.add_row(
            "Average Power",
            f"{stats.get('full_cycle_average_power_watts', 0):.1f}W",
            f"{stats.get('full_cycle_average_power_watts', 0):.1f}W",
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
            heating_table.add_column("ACK Time (ms)", style="yellow")
            heating_table.add_column("Total Time (ms)", style="bright_green")
            heating_table.add_column("Avg Power (W)", style="red")
            heating_table.add_column("Energy (Wh)", style="magenta")
            heating_table.add_column("Timestamp", style="dim")

            for i, measurement in enumerate(heating_measurements, 1):
                # Use full cycle power data instead of individual measurement power data
                full_cycle_power = measurements.get("full_cycle_power_data", {})
                heating_table.add_row(
                    str(i),
                    measurement.get("transition", "N/A"),
                    f"{measurement.get('ack_duration_ms', 0):.1f}",
                    f"{measurement.get('total_duration_ms', 0):.1f}",
                    f"{full_cycle_power.get('average_power_watts', 0):.1f}",
                    f"{full_cycle_power.get('total_energy_wh', 0):.4f}",
                    measurement.get("timestamp", "N/A")[:19].replace("T", " "),
                )

            self.console.print(heating_table)

        if cooling_measurements:
            self.console.print("\n[bold blue]Cooling Measurements[/bold blue]")
            cooling_table = Table(title="Cooling Cycle Details")
            cooling_table.add_column("Cycle", style="cyan")
            cooling_table.add_column("Transition", style="white")
            cooling_table.add_column("ACK Time (ms)", style="yellow")
            cooling_table.add_column("Total Time (ms)", style="bright_blue")
            cooling_table.add_column("Avg Power (W)", style="red")
            cooling_table.add_column("Energy (Wh)", style="magenta")
            cooling_table.add_column("Timestamp", style="dim")

            for i, measurement in enumerate(cooling_measurements, 1):
                # Use full cycle power data instead of individual measurement power data
                full_cycle_power = measurements.get("full_cycle_power_data", {})
                cooling_table.add_row(
                    str(i),
                    measurement.get("transition", "N/A"),
                    f"{measurement.get('ack_duration_ms', 0):.1f}",
                    f"{measurement.get('total_duration_ms', 0):.1f}",
                    f"{full_cycle_power.get('average_power_watts', 0):.1f}",
                    f"{full_cycle_power.get('total_energy_wh', 0):.4f}",
                    measurement.get("timestamp", "N/A")[:19].replace("T", " "),
                )

            self.console.print(cooling_table)

    def _display_full_cycle_power_analysis(self, measurements: Dict) -> None:
        """Display full cycle power analysis"""
        
        full_cycle_power = measurements.get("full_cycle_power_data", {})
        if not full_cycle_power or full_cycle_power.get("sample_count", 0) == 0:
            return

        self.console.print("\n[bold cyan]Full Cycle Power Analysis[/bold cyan]")
        
        power_analysis_table = Table(title="Complete Test Power Measurements")
        power_analysis_table.add_column("Metric", style="cyan")
        power_analysis_table.add_column("Value", style="white")
        power_analysis_table.add_column("Details", style="dim")
        
        avg_power = full_cycle_power.get("average_power_watts", 0)
        peak_power = full_cycle_power.get("peak_power_watts", 0)
        min_power = full_cycle_power.get("min_power_watts", 0)
        total_energy = full_cycle_power.get("total_energy_wh", 0)
        duration = full_cycle_power.get("duration_seconds", 0)
        samples = full_cycle_power.get("sample_count", 0)
        
        power_analysis_table.add_row(
            "Average Power", 
            f"{avg_power:.1f}W", 
            "Mean power throughout entire test"
        )
        power_analysis_table.add_row(
            "Peak Power", 
            f"{peak_power:.1f}W", 
            "Maximum instantaneous power"
        )
        power_analysis_table.add_row(
            "Minimum Power", 
            f"{min_power:.1f}W", 
            "Lowest instantaneous power"
        )
        power_analysis_table.add_row(
            "Total Energy", 
            f"{total_energy:.4f}Wh", 
            "Complete test energy consumption"
        )
        power_analysis_table.add_row(
            "Measurement Duration", 
            f"{duration:.1f}s", 
            f"Power monitoring period"
        )
        power_analysis_table.add_row(
            "Sample Count", 
            str(samples), 
            f"Data points collected at 0.5s intervals"
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

        # Cost calculation (Korean electricity rate: ~150 KRW/kWh)
        electricity_rate = 150.0  # KRW per kWh
        total_cost = total_energy * electricity_rate / 1000  # Convert Wh to kWh

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
        power_table.add_row("Estimated Cost", f"₩{total_cost:.4f}")

        # Annual cost estimation (assuming 8 hours/day operation)
        cycles_per_hour = (
            60
            / (
                (stats.get("average_heating_time_ms", 0) + stats.get("average_cooling_time_ms", 0))
                / 1000
                / 60
            )
            if stats.get("average_heating_time_ms", 0) + stats.get("average_cooling_time_ms", 0) > 0
            else 0
        )
        annual_cost = total_cost * cycles_per_hour * 8 * 365 if cycles_per_hour > 0 else 0
        power_table.add_row(
            "Annual Cost Estimate", f"₩{annual_cost:.0f}" if annual_cost > 0 else "N/A"
        )

        self.console.print(power_table)

    async def _save_results_to_file(self, result: HeatingCoolingTimeTestResult) -> None:
        """Save test results to JSON file"""
        try:
            # Create results directory
            results_dir = Path("ResultsLog/heating_cooling")
            results_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"heating_cooling_test_{timestamp}_{result.test_id}.json"
            file_path = results_dir / filename

            # Prepare data for JSON
            json_data = {
                "test_id": str(result.test_id),
                "test_type": "heating_cooling_time_test",
                "timestamp": datetime.now().isoformat(),
                "test_status": result.test_status.name,
                "is_passed": result.is_passed,
                "execution_duration_seconds": result.execution_duration.seconds,
                "measurements": result.measurements,
                "error_message": result.error_message,
            }

            # Save to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

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
• [yellow]ACK Time:[/yellow] Time from command sent to ACK received (~40-50ms)
• [green]Total Time:[/green] Time from command sent to temperature reached (~8-18 seconds)

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
• Results saved to ResultsLog/heating_cooling/ directory
"""

        self.console.print(help_text)

    def get_cycle_count_from_config(self) -> int:
        """Get cycle count from configuration file"""
        config_file = Path("configuration/heating_cooling_time_test.yaml")
        
        try:
            if config_file.exists():
                self.formatter.print_message(f"Loading cycle count from {config_file}", message_type="info")
                with open(config_file, 'r', encoding='utf-8') as f:
                    yaml_data = yaml.safe_load(f)
                
                repeat_count = yaml_data.get('repeat_count', 1)
                self.formatter.print_message(f"Configuration: {repeat_count} cycles", message_type="info")
                return repeat_count
            else:
                self.formatter.print_message("Configuration file not found, using default: 1 cycle", message_type="warning")
                return 1
                
        except Exception as e:
            self.formatter.print_message(f"Failed to load configuration: {e}, using default: 1 cycle", message_type="warning")
            return 1
