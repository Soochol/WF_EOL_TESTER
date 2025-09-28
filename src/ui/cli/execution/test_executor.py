"""
Test Execution Module

Test execution coordination, result display, and test workflow management.
Handles the complete test execution lifecycle from parameter collection
to result presentation.

Key Features:
- Test execution coordination and workflow management
- DUT information collection with validation
- Comprehensive test result display with Rich formatting
- Progress indication during test execution
- Error handling and user feedback
"""

# Standard library imports
import csv
import glob
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

# Third-party imports
from loguru import logger
from rich.console import Console
from rich.table import Table

# Local application imports
# Local imports - Application layer
from application.use_cases.eol_force_test.main_use_case import (
    EOLForceTestInput,
    EOLForceTestUseCase,
)

# Local imports - Domain layer
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.eol_test_result import EOLTestResult
from domain.value_objects.measurements import TestMeasurements

# Local folder imports
# Local imports - UI modules
from ..interfaces.execution_interface import ITestExecutor
from ..rich_formatter import RichFormatter


# TYPE_CHECKING imports
if TYPE_CHECKING:
    # Local folder imports
    from ..enhanced_cli_integration import EnhancedInputIntegrator


class TestExecutor(ITestExecutor):
    """Test execution coordinator for EOL testing operations.

    Manages the complete test execution workflow including parameter
    collection, test execution, and result presentation.
    """

    def __init__(
        self,
        console: Console,
        formatter: RichFormatter,
        use_case: EOLForceTestUseCase,
        input_integrator: "EnhancedInputIntegrator",
    ):
        """Initialize test executor.

        Args:
            console: Rich console instance for output
            formatter: Rich formatter for professional output
            use_case: EOL test execution use case
            input_integrator: Enhanced input integrator for user interaction
        """
        self._console = console
        self._formatter = formatter
        self._use_case = use_case
        self._input_integrator = input_integrator

    async def execute_eol_test(self) -> None:
        """Execute EOL test with Rich UI feedback.

        Complete test execution workflow including parameter collection,
        test execution, and result display.
        """
        self._formatter.print_header("EOL Test Execution")

        # Get DUT information with Rich prompts
        dut_info = await self._get_dut_info()
        if not dut_info:
            return

        # Create DUT command info
        dut_command_info = DUTCommandInfo(
            dut_id=dut_info["id"],
            model_number=dut_info["model"],
            serial_number=dut_info["serial"],
            manufacturer="Unknown",
        )

        # Create test command
        command = EOLForceTestInput(
            dut_info=dut_command_info,
            operator_id=dut_info["operator"],
        )

        # Show test initiation status
        self._formatter.print_status(
            "Test Initialization",
            "PREPARING",
            details={
                "DUT ID": dut_info["id"],
                "Model": dut_info["model"],
                "Operator": dut_info["operator"],
            },
        )

        # Store DUT info for use in result display
        self._current_dut_info = dut_info

        await self._execute_test_with_progress(command)

    async def _get_dut_info(self) -> Optional[Dict[str, str]]:
        """Collect DUT information using enhanced input system with auto-completion.

        Provides a professional form interface for collecting Device Under Test
        information with validation, auto-completion, and enhanced user experience.

        Returns:
            Dictionary containing validated DUT information, or None if cancelled
        """
        try:
            # Use enhanced input system for DUT information collection
            return await self._input_integrator.get_dut_information()

        except (KeyboardInterrupt, EOFError):
            # Handle user cancellation gracefully
            return None

    async def _execute_test_with_progress(self, command: EOLForceTestInput) -> None:
        """Execute test with comprehensive progress indication and error handling.

        Provides visual feedback during test execution with proper error handling
        and result display. Uses Rich progress indication for professional
        user experience.

        Args:
            command: EOL test command containing test configuration and parameters
        """
        test_result = None

        # Log test execution start
        logger.info("Starting EOL test execution...")

        try:
            # Execute the actual test through the use case
            test_result = await self._use_case.execute(command)

        except KeyboardInterrupt:
            # KeyboardInterrupt from use case - emergency stop already executed
            # Re-raise to allow MenuSystem to handle return to menu
            logger.info("Test execution interrupted by user - emergency stop completed")
            raise
        except Exception as e:
            # Handle test execution errors with clear feedback
            self._formatter.print_message(f"Test execution failed: {str(e)}", message_type="error")
            raise  # Re-raise to allow higher-level error handling

        # Log completion
        logger.info("EOL test execution completed successfully")

        # Display results only if test completed successfully
        if test_result is not None:
            # Display comprehensive test result with Rich formatting
            self._display_rich_test_result(test_result)

            # Wait for user acknowledgment before continuing
            await self._wait_for_user_acknowledgment()

    def _display_rich_test_result(self, result: EOLTestResult) -> None:
        """Display test result with Rich formatting.

        Args:
            result: Test result to display
        """
        self._formatter.print_header("Test Results")

        # Main result status
        status_text = "PASSED" if result.is_passed else "FAILED"
        status_details = {
            "Test ID": str(result.test_id),
            "Status": result.test_status.value.upper(),
            "Duration": result.format_duration(),
            "Measurements": str(result.measurement_count),
        }

        if result.error_message:
            status_details["Error"] = result.error_message

        self._formatter.print_status("Test Execution Result", status_text, details=status_details)

        # Create test results table (single result) with DUT info
        results_table = self._formatter.create_test_results_table(
            [result],
            title="Detailed Test Results",
            show_details=True,
            dut_info=getattr(self, "_current_dut_info", None),
        )
        self._formatter.print_table(results_table)

        # Show test summary if available
        if result.test_summary:
            # Handle both dict and TestMeasurements types
            try:
                if isinstance(result.test_summary, TestMeasurements):
                    self._display_measurements_table(result.test_summary)
                elif isinstance(result.test_summary, dict):
                    self._display_test_summary(result.test_summary)
                else:
                    # Convert to dict representation
                    summary_dict: Dict[str, Any] = {"summary": str(result.test_summary)}
                    self._display_test_summary(summary_dict)
            except Exception as e:
                logger.error(f"Error displaying test summary: {e}")
                # Fallback to string representation
                self._display_test_summary({"summary": str(result.test_summary)})

    def _display_test_summary(self, summary: Dict[str, Any]) -> None:
        """Display test summary with Rich formatting.

        Args:
            summary: Test summary data to display
        """
        if not summary:
            return

        # Create summary panel
        summary_content = []
        for key, value in summary.items():
            if isinstance(value, float):
                summary_content.append(f"• {key}: {value:.3f}")
            else:
                summary_content.append(f"• {key}: {value}")

        if summary_content:
            summary_panel = self._formatter.create_message_panel(
                "\n".join(summary_content), message_type="info", title="📊 Test Summary"
            )
            self._console.print(summary_panel)

    async def _wait_for_user_acknowledgment(
        self, message: str = "Press Enter to continue..."
    ) -> None:
        """Wait for user acknowledgment with enhanced input handling.

        Args:
            message: Message to display while waiting for user input
        """
        try:
            await self._input_integrator.wait_for_acknowledgment(message)
        except (KeyboardInterrupt, EOFError):
            # Handle user interruption gracefully with feedback
            self._console.print("\n[dim]Skipped by user.[/dim]")

    def _format_execution_error(self, error: Exception) -> str:
        """Format execution error message for user-friendly display.

        Converts technical exception information into user-friendly error messages
        that provide clear guidance without exposing internal implementation details.

        Args:
            error: Exception that occurred during test execution

        Returns:
            Formatted error message string appropriate for end-user display
        """
        error_type_name = type(error).__name__
        error_message = str(error)

        # Map technical error types to user-friendly messages
        if "Connection" in error_type_name or "Timeout" in error_type_name:
            return f"Hardware connection failed: {error_message}"
        if "Value" in error_type_name:
            return f"Invalid configuration or data: {error_message}"
        if "Permission" in error_type_name:
            return f"Access denied to hardware resources: {error_message}"
        return f"Test execution failed ({error_type_name}): {error_message}"

    def _categorize_system_error(self, error: Exception) -> str:
        """Categorize system errors for improved debugging and user feedback.

        Analyzes exception types to provide meaningful categorization that helps
        with debugging and provides appropriate user guidance for different
        types of system errors.

        Args:
            error: Exception that occurred during system operation

        Returns:
            Error category string for logging and user feedback purposes
        """
        error_type_name = type(error).__name__

        # Categorize based on error type patterns
        if "Import" in error_type_name or "Module" in error_type_name:
            return "DEPENDENCY"  # Missing or incompatible dependencies
        if "Connection" in error_type_name or "Network" in error_type_name:
            return "NETWORK"  # Network and connection-related issues
        if "Permission" in error_type_name or "Access" in error_type_name:
            return "PERMISSION"  # Access control and permission issues
        if "Memory" in error_type_name or "Resource" in error_type_name:
            return "RESOURCE"  # Resource exhaustion and memory issues
        return "UNKNOWN"  # Unrecognized error types

    def _display_measurements_table(self, measurements: TestMeasurements) -> None:
        """Display TestMeasurements in a formatted table showing cycle, temperature, and force data.

        Args:
            measurements: TestMeasurements object containing all test data
        """
        logger.debug("Starting _display_measurements_table")
        # Try to load cycle data from CSV files, fall back to current measurements if not available
        cycle_data = self._load_cycle_data_from_csv()

        if cycle_data:
            logger.debug(f"Using cycle data from CSV: {len(cycle_data)} entries")
            # Display cycle-based table with separators
            self._display_cycle_table(cycle_data)
        else:
            logger.debug("No cycle data found, falling back to original table format")
            # Fall back to original table format
            self._display_original_table(measurements)

    def _load_cycle_data_from_csv(self) -> List[Dict[str, Any]]:
        """Load cycle data from saved CSV files.

        Returns:
            List of cycle data dictionaries, empty if no files found
        """
        try:
            # Look for cycle measurement files
            csv_pattern = "../logs/EOL Force Test/raw_data/cycle_measurements_*_total*cycles.csv"
            csv_files = glob.glob(csv_pattern)

            if not csv_files:
                logger.debug(f"No cycle measurement CSV files found with pattern: {csv_pattern}")
                return []

            # Use the most recent file
            latest_file = max(csv_files, key=lambda f: Path(f).stat().st_mtime)
            logger.debug(f"Loading cycle data from: {latest_file}")

            # Parse CSV data - each row represents one complete cycle
            cycle_data = []
            with open(latest_file, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        cycle = int(row["Cycle"])
                        logger.debug(f"Processing cycle {cycle} from CSV row: {row}")

                        # Extract force values for each temperature from this cycle
                        forces = {}
                        if "T38_P170" in row and row["T38_P170"]:
                            forces[38.0] = float(row["T38_P170"])
                        if "T52_P170" in row and row["T52_P170"]:
                            forces[52.0] = float(row["T52_P170"])
                        if "T66_P170" in row and row["T66_P170"]:
                            forces[66.0] = float(row["T66_P170"])

                        # Extract timing data from this cycle
                        heating_time = float(row.get("Heating_Time_s", 0.0))
                        cooling_time = float(row.get("Cooling_Time_s", 0.0))

                        logger.debug(f"Extracted forces for cycle {cycle}: {forces}")

                        # Create entries for each temperature in this cycle
                        for temp, force in forces.items():
                            cycle_data.append(
                                {
                                    "cycle": cycle,
                                    "temperature": temp,
                                    "force": force,
                                    "heating_time": heating_time,
                                    "cooling_time": cooling_time,
                                }
                            )
                            logger.debug(
                                f"Added entry: cycle={cycle}, temp={temp}, force={force}, heating={heating_time}s, cooling={cooling_time}s"
                            )

                    except (ValueError, KeyError) as e:
                        logger.debug(f"Skipping invalid row in cycle CSV: {e}")
                        continue

            # Sort by cycle, then by temperature
            cycle_data.sort(key=lambda x: (x["cycle"], x["temperature"]))
            logger.debug(f"Loaded {len(cycle_data)} temperature measurements from cycle CSV")
            return cycle_data

        except Exception as e:
            logger.debug(f"Could not load cycle data from CSV: {e}")
            return []

    def _display_cycle_table(self, cycle_data: List[Dict[str, Any]]) -> None:
        """Display table with cycle information and separators.

        Args:
            cycle_data: List of cycle data dictionaries with cycle, temperature, force
        """
        if not cycle_data:
            logger.debug("No cycle data to display")
            return

        logger.debug(f"Displaying cycle table with {len(cycle_data)} entries")

        # Create table with cycle, temperature, force, and timing columns
        table = Table(title="📊 Test Measurements Summary")
        table.add_column("Cycle", style="magenta", justify="center")
        table.add_column("Temperature", style="cyan", justify="center")
        table.add_column("Force (kgf)", style="yellow", justify="center")
        table.add_column("Heating Time", style="green", justify="center")
        table.add_column("Cooling Time", style="blue", justify="center")

        current_cycle = None

        for data in cycle_data:
            cycle = data["cycle"]
            temperature = data["temperature"]
            force = data["force"]
            heating_time = data.get("heating_time", 0.0)
            cooling_time = data.get("cooling_time", 0.0)

            # Add separator when cycle changes
            if current_cycle is not None and cycle != current_cycle:
                table.add_section()  # This adds a separator line

            current_cycle = cycle

            # Add row for this measurement
            table.add_row(
                str(cycle),
                f"{temperature:.1f}°C",
                f"{force:.2f}",
                f"{heating_time:.2f}s",
                f"{cooling_time:.2f}s",
            )

        # Display the table
        self._console.print()
        self._console.print(table)
        self._console.print()

    def _display_original_table(self, measurements: TestMeasurements) -> None:
        """Display original table format as fallback.

        Args:
            measurements: TestMeasurements object containing all test data
        """
        # Create table with temperature and max force columns
        table = Table(title="📊 Test Measurements Summary")
        table.add_column("Temperature", style="cyan", justify="center")
        table.add_column("Force (kgf)", style="yellow", justify="center")

        # Extract data for each temperature
        temperatures = sorted(measurements.get_temperatures())

        for temp in temperatures:
            temp_measurements = measurements.get_temperature_measurements(temp)
            if temp_measurements:
                try:
                    # Get maximum force value for this temperature
                    _, max_force = temp_measurements.get_force_range()
                    table.add_row(f"{temp:.1f}°C", f"{max_force:.2f}")
                except ValueError:
                    # Skip if no measurements available for this temperature
                    continue

        # Display the table
        self._console.print()
        self._console.print(table)
        self._console.print()
