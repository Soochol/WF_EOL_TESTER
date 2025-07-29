"""
Test Command

Handles EOL test execution commands.
"""

from typing import List, Dict, Optional
from loguru import logger

from ui.cli.commands.base import Command, CommandResult
from application.use_cases.eol_force_test import EOLForceTestUseCase, EOLForceTestCommand
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.identifiers import OperatorId


class TestCommand(Command):
    """Command for EOL test operations"""

    def __init__(self, use_case: Optional[EOLForceTestUseCase] = None):
        super().__init__(name="test", description="Execute EOL tests")
        self._use_case = use_case

    def set_use_case(self, use_case: EOLForceTestUseCase) -> None:
        """Set the use case for test execution"""
        self._use_case = use_case

    async def execute(self, args: List[str]) -> CommandResult:
        """
        Execute test command

        Args:
            args: Command arguments (subcommand and parameters)

        Returns:
            CommandResult with test execution results
        """
        if not self._use_case:
            return CommandResult.error("Test system not initialized. Please check configuration.")

        if not args:
            # Interactive test mode
            return await self._interactive_test()

        subcommand = args[0].lower()

        if subcommand == "quick":
            return await self._quick_test(args[1:])
        elif subcommand == "profile":
            return await self._profile_test(args[1:])
        elif subcommand == "help":
            return CommandResult.info(self.get_help())
        else:
            return CommandResult.error(f"Unknown test subcommand: {subcommand}")

    def get_subcommands(self) -> Dict[str, str]:
        """Get available subcommands"""
        return {
            "": "Start interactive EOL test",
            "quick": "Run quick test with default settings",
            "profile <name>": "Run test with specific profile",
            "help": "Show test command help",
        }

    async def _interactive_test(self) -> CommandResult:
        """Run interactive test mode"""
        try:
            # Get DUT information interactively
            print("\\n" + "=" * 60)
            print("EOL Test - Interactive Mode")
            print("=" * 60)

            dut_id = input("Enter DUT ID: ").strip()
            if not dut_id:
                return CommandResult.error("DUT ID is required")

            model_number = input("Enter Model Number (or press Enter for default): ").strip()
            if not model_number:
                model_number = "Unknown"

            serial_number = input("Enter Serial Number (or press Enter for auto): ").strip()
            if not serial_number:
                serial_number = f"{dut_id}_SN"

            operator_id = input("Enter Operator ID: ").strip()
            if not operator_id:
                operator_id = "Unknown"

            # Create DUT command info
            dut_info = DUTCommandInfo(
                dut_id=dut_id,
                model_number=model_number,
                serial_number=serial_number,
                manufacturer="WF",
            )

            # Create and execute test command
            test_command = EOLForceTestCommand(
                dut_info=dut_info, operator_id=OperatorId(operator_id)
            )

            print(f"\\nStarting EOL test for DUT: {dut_id}")
            print("Press Ctrl+C to cancel...")

            # Execute the test
            result = await self._use_case.execute(test_command)

            # Format result
            status_text = "PASS" if result.is_passed else "FAIL"
            message = f"""
Test Completed: {status_text}
DUT ID: {dut_id}
Test Duration: {result.format_duration()}
Total Measurements: {result.measurement_count}
            """

            if result.is_passed:
                return CommandResult.success(message, {"result": result})
            else:
                return CommandResult.error(message, {"result": result})

        except KeyboardInterrupt:
            return CommandResult.warning("Test cancelled by user")
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return CommandResult.error(f"Test execution failed: {str(e)}")

    async def _quick_test(self, args: List[str]) -> CommandResult:
        """Run quick test with minimal input"""
        try:
            # Generate quick test DUT info
            import time

            timestamp = int(time.time())

            dut_info = DUTCommandInfo(
                dut_id=f"QUICK_{timestamp}",
                model_number="QuickTest",
                serial_number=f"QT_{timestamp}",
                manufacturer="WF",
            )

            test_command = EOLForceTestCommand(
                dut_info=dut_info, operator_id=OperatorId("QuickTest")
            )

            print(f"Running quick test for DUT: {dut_info.dut_id}")

            result = await self._use_case.execute(test_command)

            status_text = "PASS" if result.is_passed else "FAIL"
            message = f"Quick test completed: {status_text} (Duration: {result.format_duration()})"

            return CommandResult.success(message, {"result": result})

        except Exception as e:
            logger.error(f"Quick test failed: {e}")
            return CommandResult.error(f"Quick test failed: {str(e)}")

    async def _profile_test(self, args: List[str]) -> CommandResult:
        """Run test with specific profile"""
        if not args:
            return CommandResult.error("Profile name is required. Usage: /test profile <name>")

        profile_name = args[0]

        # TODO: Implement profile-based testing
        return CommandResult.info(f"Profile testing with '{profile_name}' will be implemented soon")
