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
from typing import Any, Dict, Optional, TYPE_CHECKING

# Third-party imports
from loguru import logger
from rich.console import Console

# Local application imports
# Local imports - Application layer
from application.use_cases.eol_force_test.main_use_case import (
    EOLForceTestInput,
    EOLForceTestUseCase,
)

# Local imports - Domain layer
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.eol_test_result import EOLTestResult

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
                if isinstance(result.test_summary, dict):
                    self._display_test_summary(result.test_summary)
                else:
                    # Convert TestMeasurements to dict representation
                    summary_dict: Dict[str, Any] = {"summary": str(result.test_summary)}
                    self._display_test_summary(summary_dict)
            except Exception:
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
