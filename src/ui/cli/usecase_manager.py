"""
UseCase Discovery and Execution System

Provides dynamic discovery and execution of available UseCases with Rich UI integration.
Designed to be extensible as new UseCases are added to the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from loguru import logger
from rich.console import Console

from application.use_cases.eol_force_test import (
    EOLForceTestCommand,
    EOLForceTestUseCase,
)
from domain.value_objects.dut_command_info import DUTCommandInfo

from .enhanced_input_manager import EnhancedInputManager
from .rich_formatter import RichFormatter
from .rich_utils import RichUIManager


class UseCaseInfo:
    """Information about a discovered UseCase"""

    def __init__(
        self,
        *,
        name: str,
        description: str,
        use_case_class: Type,
        command_class: Optional[Type] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.description = description
        self.use_case_class = use_case_class
        self.command_class = command_class
        self.parameters = parameters or {}


class UseCaseExecutor(ABC):
    """Abstract base class for UseCase executors"""

    @abstractmethod
    async def execute(self, use_case_instance: Any, formatter: RichFormatter) -> Any:
        """Execute the UseCase with Rich UI feedback"""

    @abstractmethod
    async def get_parameters(self, formatter: RichFormatter) -> Optional[Any]:
        """Collect parameters needed for UseCase execution"""


class EOLForceTestExecutor(UseCaseExecutor):
    """Executor for EOL Force Test UseCase"""

    def __init__(self, configuration_service: Optional[Any] = None):
        self.configuration_service = configuration_service

    async def execute(
        self, use_case_instance: EOLForceTestUseCase, formatter: RichFormatter
    ) -> Any:
        """Execute EOL Force Test with Rich UI feedback"""
        # Get test parameters from user
        command = await self.get_parameters(formatter)
        if not command:
            return None

        # Show test initiation status
        formatter.print_status(
            "Test Initialization",
            "PREPARING",
            details={
                "DUT ID": command.dut_info.dut_id,
                "Model": command.dut_info.model_number,
                "Operator": command.operator_id,
            },
        )

        # Execute test without additional spinner (managed by enhanced_eol_tester_cli)
        try:
            result = await use_case_instance.execute(command)

            # Display results
            self._display_test_result(result, formatter)
            return result

        except Exception as e:
            formatter.print_message(f"Test execution failed: {str(e)}", message_type="error")
            raise

    async def get_parameters(self, formatter: RichFormatter) -> Optional[EOLForceTestCommand]:
        """Collect DUT information for EOL test using Enhanced Input Manager"""
        try:
            # Create Enhanced Input Manager
            input_manager = EnhancedInputManager(
                formatter.console, 
                formatter,
                configuration_service=self.configuration_service
            )

            # Use the enhanced DUT info collection
            dut_info = await input_manager.get_dut_info_interactive()
            if not dut_info:
                return None

            # Create DUT command info
            dut_command_info = DUTCommandInfo(
                dut_id=dut_info["id"],
                model_number=dut_info["model"],
                serial_number=dut_info["serial"],
                manufacturer="Unknown",
            )

            # Create and return command
            command = EOLForceTestCommand(
                dut_info=dut_command_info,
                operator_id=dut_info["operator"],
            )

            return command

        except (KeyboardInterrupt, EOFError):
            formatter.print_message("DUT information collection cancelled by user", "info")
            return None

    def _display_test_result(self, result: Any, formatter: RichFormatter) -> None:
        """Display test result with Rich formatting"""
        formatter.print_header("Test Results")

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

        formatter.print_status("Test Execution Result", status_text, details=status_details)

        # Create test results table
        results_table = formatter.create_test_results_table(
            [result], title="Detailed Test Results", show_details=True
        )
        formatter.print_table(results_table)


class UseCaseManager:
    """Manages UseCase discovery and execution with Rich UI"""

    def __init__(self, console: Optional[Console] = None, configuration_service: Optional[Any] = None):
        self.console = console or Console()
        self.formatter = RichFormatter(self.console)
        self.ui_manager = RichUIManager(self.console)
        self.discovered_usecases: List[UseCaseInfo] = []
        self.executors: Dict[str, UseCaseExecutor] = {}
        self.configuration_service = configuration_service

        # Initialize with known UseCases
        self._initialize_usecases()

    def _initialize_usecases(self) -> None:
        """Initialize known UseCases and their executors"""
        # EOL Force Test UseCase
        eol_usecase_info = UseCaseInfo(
            name="EOL Force Test",
            description="Execute End-of-Line force testing on Device Under Test",
            use_case_class=EOLForceTestUseCase,
            command_class=EOLForceTestCommand,
        )

        self.discovered_usecases.append(eol_usecase_info)
        self.executors[eol_usecase_info.name] = EOLForceTestExecutor(self.configuration_service)

        logger.info(f"Initialized {len(self.discovered_usecases)} UseCases")

    def discover_usecases(self) -> List[UseCaseInfo]:
        """Discover available UseCases dynamically"""
        # For future expansion, this could scan the use_cases package
        # and automatically discover new UseCase classes
        return self.discovered_usecases.copy()

    def show_usecase_menu(self) -> Optional[str]:
        """Display UseCase selection menu"""
        if not self.discovered_usecases:
            self.formatter.print_message(
                "No UseCases available.", message_type="warning", title="No UseCases Found"
            )
            return None

        # Create menu options
        menu_options = {}
        for i, usecase_info in enumerate(self.discovered_usecases, 1):
            menu_options[str(i)] = f"{usecase_info.name} - {usecase_info.description}"
        menu_options["b"] = "Back to Main Menu"

        # Show menu
        selected = self.ui_manager.create_interactive_menu(
            menu_options, title="Select UseCase to Execute", prompt="Please select a UseCase"
        )

        return selected

    async def execute_usecase(self, usecase_name: str, use_case_instance: Any) -> Optional[Any]:
        """Execute a specific UseCase by name"""
        # Find the UseCase info
        usecase_info = None
        for info in self.discovered_usecases:
            if info.name == usecase_name:
                usecase_info = info
                break

        if not usecase_info:
            self.formatter.print_message(
                f"UseCase '{usecase_name}' not found.", message_type="error"
            )
            return None

        # Get the executor
        executor = self.executors.get(usecase_name)
        if not executor:
            self.formatter.print_message(
                f"No executor found for UseCase '{usecase_name}'.", message_type="error"
            )
            return None

        # Execute the UseCase
        try:
            self.formatter.print_header(f"Executing: {usecase_info.name}", usecase_info.description)

            result = await executor.execute(use_case_instance, self.formatter)

            if result:
                self.formatter.print_message(
                    "UseCase execution completed successfully.",
                    message_type="success",
                    title="Execution Complete",
                )

            return result

        except Exception as e:
            self.formatter.print_message(
                f"UseCase execution failed: {str(e)}", message_type="error", title="Execution Error"
            )
            logger.error(f"UseCase execution error: {e}")
            return None

    async def execute_usecase_by_selection(
        self, selection: str, use_case_instances: Dict[str, Any]
    ) -> Optional[Any]:
        """Execute UseCase based on user selection"""
        if selection == "b":
            return None

        try:
            index = int(selection) - 1
            if 0 <= index < len(self.discovered_usecases):
                usecase_info = self.discovered_usecases[index]

                # Get the appropriate use case instance
                use_case_instance = use_case_instances.get(usecase_info.name)
                if not use_case_instance:
                    self.formatter.print_message(
                        f"UseCase instance not available for '{usecase_info.name}'.",
                        message_type="error",
                    )
                    return None

                return await self.execute_usecase(usecase_info.name, use_case_instance)

            self.formatter.print_message(
                "Invalid selection. Please try again.", message_type="warning"
            )
            return None

        except ValueError:
            self.formatter.print_message(
                "Invalid selection. Please enter a number.", message_type="warning"
            )
            return None

    def get_usecase_info(self, usecase_name: str) -> Optional[UseCaseInfo]:
        """Get information about a specific UseCase"""
        for info in self.discovered_usecases:
            if info.name == usecase_name:
                return info
        return None

    def list_usecases(self) -> None:
        """Display list of available UseCases"""
        if not self.discovered_usecases:
            self.formatter.print_message(
                "No UseCases available.", message_type="info", title="UseCase List"
            )
            return

        self.formatter.print_header("Available UseCases")

        for i, usecase_info in enumerate(self.discovered_usecases, 1):
            status_details = {
                "Description": usecase_info.description,
                "Class": usecase_info.use_case_class.__name__,
            }

            if usecase_info.command_class:
                status_details["Command Class"] = usecase_info.command_class.__name__

            self.formatter.print_status(
                f"{i}. {usecase_info.name}", "AVAILABLE", details=status_details
            )
