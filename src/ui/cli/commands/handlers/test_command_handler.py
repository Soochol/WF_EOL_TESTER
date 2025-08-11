"""Test Command Handler

Enhanced test command handler with dependency injection support and
integration with the new command system architecture.
"""

from typing import Dict, List, Optional, Tuple, cast

from loguru import logger

from application.use_cases.eol_force_test import (
    EOLForceTestCommand,
    EOLForceTestUseCase,
)
from domain.value_objects.dut_command_info import DUTCommandInfo
from ui.cli.commands.core.base_command import BaseCommand
from ui.cli.commands.interfaces.command_interface import (
    CommandMetadata,
    CommandResult,
    ICommandExecutionContext,
)
from ui.cli.interfaces.formatter_interface import IFormatter
from ui.cli.interfaces.validation_interface import IInputValidator


class TestCommandHandler(BaseCommand):
    """Enhanced test command handler with dependency injection.

    Handles EOL test execution with comprehensive validation,
    user-friendly interfaces, and robust error handling.
    """

    def __init__(
        self,
        use_case: Optional[EOLForceTestUseCase] = None,
        formatter: Optional[IFormatter] = None,
        validator: Optional[IInputValidator] = None,
    ):
        """Initialize test command handler.

        Args:
            use_case: EOL test use case for execution
            formatter: UI formatter for output
            validator: Input validator for user input
        """
        metadata = CommandMetadata(
            name="test",
            description="Execute EOL tests with interactive and automated modes",
            category="testing",
            aliases=["t", "eol-test"],
            examples=[
                "/test - Start interactive EOL test",
                "/test quick - Run quick test with defaults",
                "/test profile production - Run test with production profile",
                "/test help - Show detailed help",
            ],
            help_text="Execute End-of-Line (EOL) tests for device validation. "
            "Supports interactive mode for step-by-step testing and "
            "automated modes for batch processing.",
            version="2.0.0",
            author="WF Test System",
        )

        super().__init__(metadata)

        self._use_case = use_case
        self._formatter = formatter
        self._validator = validator

        logger.debug("Initialized enhanced test command handler")

    async def execute(
        self,
        args: List[str],
        context: ICommandExecutionContext,
    ) -> CommandResult:
        """Execute test command with enhanced context.

        Args:
            args: Command arguments
            context: Execution context with services and session data

        Returns:
            CommandResult with test execution results
        """
        # Check for help request first
        help_result = self.handle_help_request(args)
        if help_result:
            return help_result

        # Validate that test system is available
        if not self._use_case:
            try:
                # Try to get use case from context
                self._use_case = context.get_service(EOLForceTestUseCase)
            except ValueError:
                return CommandResult.error(
                    "Test system not initialized. Please check system configuration and ensure "
                    "all required components are properly configured.",
                    error_details={
                        "reason": "missing_test_system",
                        "suggestion": "Check hardware connections and system configuration",
                    },
                )

        # Get services from context if not provided in constructor
        if not self._formatter:
            try:
                self._formatter = context.get_service(IFormatter)
            except ValueError:
                logger.warning("IFormatter not available, using basic output")

        if not self._validator:
            try:
                self._validator = context.get_service(IInputValidator)
            except ValueError:
                logger.warning("IInputValidator not available, using basic validation")

        # Route to appropriate subcommand
        if not args:
            return await self._interactive_test(context)

        subcommand = args[0].lower()

        if subcommand == "quick":
            return await self._quick_test(args[1:], context)
        elif subcommand == "profile":
            return await self._profile_test(args[1:], context)
        else:
            return CommandResult.error(
                f"Unknown test subcommand: {subcommand}",
                error_details={
                    "valid_subcommands": list(self.get_subcommands().keys()),
                    "suggestion": "Use '/test help' for available options",
                },
            )

    def get_subcommands(self) -> Dict[str, str]:
        """Get available subcommands with descriptions.

        Returns:
            Dictionary mapping subcommand names to descriptions
        """
        return {
            "": "Start interactive EOL test with step-by-step guidance",
            "quick": "Run quick test with default settings and auto-generated test data",
            "profile": "Run test with specific configuration profile (usage: /test profile <name>)",
        }

    def validate_args(self, args: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate command arguments.

        Args:
            args: Arguments to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Base validation
        is_valid, error = super().validate_args(args)
        if not is_valid:
            return is_valid, error

        # Subcommand validation
        if args:
            subcommand = args[0].lower()
            valid_subcommands = ["quick", "profile", "help"]

            if subcommand not in valid_subcommands:
                return (
                    False,
                    f"Invalid subcommand '{subcommand}'. Valid options: {', '.join(valid_subcommands)}",
                )

            # Profile subcommand requires profile name
            if subcommand == "profile":
                if len(args) < 2:
                    return (
                        False,
                        "Profile subcommand requires a profile name. Usage: /test profile <name>",
                    )

        return True, None

    async def _interactive_test(self, context: ICommandExecutionContext) -> CommandResult:
        """Run interactive test mode with enhanced validation.

        Args:
            context: Execution context

        Returns:
            CommandResult with test execution results
        """
        try:
            # Display header
            if self._formatter:
                self._formatter.print_header(
                    "EOL Test - Interactive Mode", "Step-by-step device testing with guided input"
                )
            else:
                print("\n" + "=" * 60)
                print("EOL Test - Interactive Mode")
                print("=" * 60)

            # Collect DUT information with validation
            dut_id = await self._get_validated_input(
                "Enter DUT ID",
                "dut_id",
                required=True,
                context=context,
            )
            if not dut_id:
                return CommandResult.error("DUT ID is required for test execution")

            model_number = await self._get_validated_input(
                "Enter Model Number (or press Enter for default)",
                "model_number",
                required=False,
                context=context,
            )
            if not model_number:
                model_number = "Unknown"

            serial_number = await self._get_validated_input(
                "Enter Serial Number (or press Enter for auto-generation)",
                "serial_number",
                required=False,
                context=context,
            )
            if not serial_number:
                serial_number = f"{dut_id}_SN"

            operator_id = await self._get_validated_input(
                "Enter Operator ID",
                "operator_id",
                required=True,
                context=context,
            )
            if not operator_id:
                operator_id = "Unknown"

            # Create DUT command info
            dut_info = DUTCommandInfo(
                dut_id=dut_id,
                model_number=model_number,
                serial_number=serial_number,
                manufacturer="WF",
            )

            # Create test command
            test_command = EOLForceTestCommand(
                dut_info=dut_info,
                operator_id=operator_id,
            )

            # Display test information
            if self._formatter:
                self._formatter.print_message(
                    f"Starting EOL test for DUT: {dut_id}\n"
                    f"Model: {model_number}\n"
                    f"Serial: {serial_number}\n"
                    f"Operator: {operator_id}",
                    "info",
                    "Test Configuration",
                )
                self._formatter.print_message("Press Ctrl+C to cancel test execution", "warning")
            else:
                print(f"\nStarting EOL test for DUT: {dut_id}")
                print(f"Model: {model_number}, Serial: {serial_number}, Operator: {operator_id}")
                print("Press Ctrl+C to cancel...")

            # Execute the test
            use_case = cast(EOLForceTestUseCase, self._use_case)
            result = await use_case.execute(test_command)

            # Format and return result
            return self._format_test_result(result, dut_id, "Interactive")

        except KeyboardInterrupt:
            return CommandResult.warning(
                "Test cancelled by user",
                data={"reason": "user_cancellation", "stage": "interactive_input"},
            )
        except Exception as e:
            logger.error(f"Interactive test execution failed: {e}")
            return CommandResult.error(
                f"Interactive test execution failed: {str(e)}",
                error_details={
                    "exception_type": type(e).__name__,
                    "stage": "interactive_execution",
                },
            )

    async def _quick_test(
        self, args: List[str], context: ICommandExecutionContext
    ) -> CommandResult:
        """Run quick test with auto-generated data.

        Args:
            args: Additional arguments (currently unused)
            context: Execution context

        Returns:
            CommandResult with test execution results
        """
        try:
            import time

            # Generate test data
            timestamp = int(time.time())

            dut_info = DUTCommandInfo(
                dut_id=f"QUICK_{timestamp}",
                model_number="QuickTest",
                serial_number=f"QT_{timestamp}",
                manufacturer="WF",
            )

            test_command = EOLForceTestCommand(
                dut_info=dut_info,
                operator_id="QuickTest",
            )

            # Display quick test info
            if self._formatter:
                self._formatter.print_message(
                    f"Running quick test for DUT: {dut_info.dut_id}", "info", "Quick Test Mode"
                )
            else:
                print(f"Running quick test for DUT: {dut_info.dut_id}")

            # Execute test
            use_case = cast(EOLForceTestUseCase, self._use_case)
            result = await use_case.execute(test_command)

            return self._format_test_result(result, dut_info.dut_id, "Quick")

        except Exception as e:
            logger.error(f"Quick test execution failed: {e}")
            return CommandResult.error(
                f"Quick test execution failed: {str(e)}",
                error_details={
                    "exception_type": type(e).__name__,
                    "stage": "quick_execution",
                },
            )

    async def _profile_test(
        self, args: List[str], context: ICommandExecutionContext
    ) -> CommandResult:
        """Run test with specific profile.

        Args:
            args: Profile arguments
            context: Execution context

        Returns:
            CommandResult with test execution results
        """
        if not args:
            return CommandResult.error(
                "Profile name is required. Usage: /test profile <name>",
                error_details={
                    "suggestion": "Specify a profile name, e.g., '/test profile production'"
                },
            )

        profile_name = args[0]

        # Profile-based testing will be implemented in future versions
        # This feature will allow users to create custom test profiles with
        # specific configurations for different DUT types and test scenarios
        return CommandResult.info(
            f"Profile testing with '{profile_name}' will be implemented in a future version.\n"
            "This feature will support custom test configurations including:\n"
            "- Device-specific test parameters\n"
            "- Custom measurement thresholds\n"
            "- Automated test sequences\n"
            "- Integration with test management systems",
            data={"profile_name": profile_name, "status": "planned_feature"},
        )

    async def _get_validated_input(
        self,
        prompt: str,
        input_type: str,
        required: bool,
        context: ICommandExecutionContext,
    ) -> Optional[str]:
        """Get validated input from user.

        Args:
            prompt: Input prompt
            input_type: Type of input for validation
            required: Whether input is required
            context: Execution context

        Returns:
            Validated input or None if cancelled/invalid
        """
        if self._validator:
            return self._validator.get_validated_input(
                prompt + ": ",
                input_type,
                required=required,
                max_attempts=3,
            )
        else:
            # Fallback to basic input
            try:
                user_input = input(prompt + ": ").strip()
                if required and not user_input:
                    print("This field is required.")
                    return None
                return user_input if user_input else None
            except (EOFError, KeyboardInterrupt):
                return None

    def _format_test_result(self, result, dut_id: str, test_mode: str) -> CommandResult:
        """Format test result for display.

        Args:
            result: Test execution result
            dut_id: DUT identifier
            test_mode: Test mode (Interactive, Quick, Profile)

        Returns:
            Formatted CommandResult
        """
        status_text = "PASS" if result.is_passed else "FAIL"

        message = f"""
Test Completed: {status_text}
Mode: {test_mode}
DUT ID: {dut_id}
Test Duration: {result.format_duration()}
Total Measurements: {result.measurement_count}
"""

        result_data = {
            "result": result,
            "dut_id": dut_id,
            "test_mode": test_mode,
            "status": status_text,
            "passed": result.is_passed,
            "duration": result.format_duration(),
            "measurement_count": result.measurement_count,
        }

        if self._formatter:
            # Use rich formatting if available
            self._formatter.print_message(
                message.strip(),
                "success" if result.is_passed else "error",
                f"Test Result - {status_text}",
            )

        if result.is_passed:
            return CommandResult.success(message.strip(), result_data)
        else:
            return CommandResult.error(message.strip(), result_data)
