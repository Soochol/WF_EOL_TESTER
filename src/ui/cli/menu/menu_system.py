"""
Menu System Module

Menu display, navigation, and user choice handling for the CLI interface.
Provides a professional menu system with enhanced user experience and
integration with other CLI components.

Key Features:
- Professional menu display with Rich formatting
- Enhanced user input handling with validation
- Menu navigation and choice processing
- Integration with test execution and hardware control
- Graceful error handling and user feedback
"""

# Standard library imports
from typing import TYPE_CHECKING, Optional

# Third-party imports
from loguru import logger
from rich.console import Console

# Local imports
from ..interfaces.menu_interface import IMenuSystem
from ..rich_formatter import RichFormatter

# TYPE_CHECKING imports
if TYPE_CHECKING:
    from ..enhanced_cli_integration import EnhancedMenuSystem
    from ..execution.test_executor import TestExecutor
    from ..session.session_manager import SessionManager


class MenuSystem(IMenuSystem):
    """Menu display and navigation system for CLI application.

    Manages menu presentation, user choice collection, and navigation
    flow with professional Rich UI formatting.
    """

    def __init__(
        self, console: Console, formatter: RichFormatter, enhanced_menu: "EnhancedMenuSystem", emergency_stop_service=None
    ):
        """Initialize menu system.

        Args:
            console: Rich console instance for output
            formatter: Rich formatter for professional output
            enhanced_menu: Enhanced menu system for input handling
            emergency_stop_service: Emergency stop service for hardware safety (optional)
        """
        self._console = console
        self._formatter = formatter
        self._enhanced_menu = enhanced_menu
        self._emergency_stop_service = emergency_stop_service
        self._session_manager: Optional["SessionManager"] = None
        self._test_executor: Optional["TestExecutor"] = None
        self._usecase_manager = None
        self._hardware_manager = None

    def set_session_manager(self, session_manager: "SessionManager") -> None:
        """Set session manager for session control.

        Args:
            session_manager: Session manager instance
        """
        self._session_manager = session_manager

    def set_test_executor(self, test_executor: "TestExecutor") -> None:
        """Set test executor for test operations.

        Args:
            test_executor: Test executor instance
        """
        self._test_executor = test_executor

    def set_usecase_manager(self, usecase_manager) -> None:
        """Set usecase manager for advanced operations.

        Args:
            usecase_manager: UseCase manager instance
        """
        self._usecase_manager = usecase_manager

    def set_hardware_manager(self, hardware_manager) -> None:
        """Set hardware manager for hardware control.

        Args:
            hardware_manager: Hardware manager instance
        """
        self._hardware_manager = hardware_manager

    async def show_main_menu(self) -> None:
        """Display the enhanced main menu with advanced input features.

        Shows the main menu and processes user selections with comprehensive
        error handling and navigation control.
        """
        try:
            # Use enhanced menu system for user input
            choice = await self._enhanced_menu.show_main_menu_enhanced()

            if not choice:
                # User cancelled (Ctrl+C) or no input - exit gracefully
                if self._session_manager:
                    self._session_manager.stop_session()
                self._formatter.print_message(
                    "Exiting EOL Tester... Goodbye!", message_type="info", title="Goodbye"
                )
                return

            # Process menu selection
            await self._process_menu_choice(choice)

        except (KeyboardInterrupt, EOFError):
            logger.info("MenuSystem: KeyboardInterrupt caught, re-raising to SessionManager")
            if self._session_manager:
                self._session_manager.stop_session()
            # Re-raise KeyboardInterrupt so SessionManager can handle emergency stop
            raise

    async def _process_menu_choice(self, choice: str) -> None:
        """Process user menu choice and execute corresponding action.

        Args:
            choice: User's menu selection
        """
        try:
            if choice == "1":
                await self._execute_eol_test()
            elif choice == "2":
                await self._execute_simple_mcu_test()
            elif choice == "3":
                await self._execute_heating_cooling_test()
            elif choice == "4":
                await self._execute_robot_home()
            elif choice == "5":
                await self._hardware_control_center()
            elif choice == "6":
                if self._session_manager:
                    self._session_manager.stop_session()
                self._formatter.print_message(
                    "Thank you for using EOL Tester!", message_type="success", title="Goodbye"
                )
            else:
                self._formatter.print_message(
                    f"Invalid option '{choice}'. Please select a number between 1-6.",
                    message_type="warning",
                )
        except Exception as e:
            self._formatter.print_message(
                f"Error processing menu choice: {str(e)}", message_type="error"
            )
            logger.error(f"Menu choice processing error: {e}")

    async def _execute_eol_test(self) -> None:
        """Execute EOL test through test executor.

        Delegates EOL test execution to the test executor component
        with proper error handling.
        """
        if not self._test_executor:
            self._formatter.print_message(
                "Test executor not available. Please check system configuration.",
                message_type="error",
                title="Test Executor Unavailable",
            )
            return

        try:
            await self._test_executor.execute_eol_test()
        except KeyboardInterrupt:
            logger.info("EOL Force Test interrupted by user (Ctrl+C)")
            self._formatter.print_message(
                "Test interrupted by user. Returning to main menu...", 
                message_type="warning", 
                title="Test Interrupted"
            )
        except Exception as e:
            self._formatter.print_message(f"Test execution error: {str(e)}", message_type="error")
            logger.error(f"EOL test execution error: {e}")

    async def _execute_simple_mcu_test(self) -> None:
        """Execute Simple MCU Test through usecase manager.

        Delegates Simple MCU Test execution to the usecase manager component
        with proper error handling.
        """
        if not self._usecase_manager:
            self._formatter.print_message(
                "UseCase manager not available. Please check system configuration.",
                message_type="error",
                title="UseCase Manager Unavailable",
            )
            return

        try:
            self._formatter.print_header(
                "Simple MCU Test", "Direct MCU communication testing sequence"
            )

            # Create Simple MCU Test UseCase instance
            from application.use_cases.system_tests import SimpleMCUTestUseCase

            # Try to get hardware services from the test executor's use case
            hardware_services = None
            if self._test_executor:
                # Access the use case from test executor (if available)
                try:
                    # Get hardware services from the test executor
                    # Access hardware services through the use case
                    if hasattr(self._test_executor, "_use_case"):
                        use_case = getattr(self._test_executor, "_use_case")
                        if hasattr(use_case, "_hardware_services"):
                            hardware_services = getattr(use_case, "_hardware_services")
                except AttributeError:
                    pass

            # Try to get hardware services from hardware manager
            if not hardware_services and self._hardware_manager:
                try:
                    if hasattr(self._hardware_manager, "get_hardware_services"):
                        hardware_services = self._hardware_manager.get_hardware_services()
                    elif hasattr(self._hardware_manager, "_hardware_facade"):
                        hardware_services = getattr(self._hardware_manager, "_hardware_facade")
                except AttributeError:
                    pass

            if not hardware_services:
                self._formatter.print_message(
                    "Hardware services not available for Simple MCU Test.",
                    message_type="error",
                    title="Hardware Services Unavailable",
                )
                return

            # Get configuration service from usecase manager
            configuration_service = getattr(self._usecase_manager, "configuration_service", None)
            if not configuration_service:
                self._formatter.print_message(
                    "Configuration service not available for Simple MCU Test.",
                    message_type="error",
                    title="Configuration Service Unavailable",
                )
                return

            # Create Simple MCU Test UseCase instance with emergency stop service
            simple_mcu_usecase = SimpleMCUTestUseCase(hardware_services, configuration_service, self._emergency_stop_service)

            # Execute Simple MCU Test through usecase manager
            result = await self._usecase_manager.execute_usecase(
                "Simple MCU Test", simple_mcu_usecase
            )

            if result:
                # Wait for user acknowledgment
                await self._wait_for_user_acknowledgment()
            else:
                self._formatter.print_message(
                    "Simple MCU Test was cancelled or failed.",
                    message_type="info",
                    title="Test Cancelled",
                )

        except KeyboardInterrupt:
            logger.info("Simple MCU Test interrupted by user (Ctrl+C)")
            self._formatter.print_message(
                "Test interrupted by user. Returning to main menu...", 
                message_type="warning", 
                title="Test Interrupted"
            )
        except Exception as e:
            self._formatter.print_message(
                f"Simple MCU Test execution failed: {str(e)}",
                message_type="error",
                title="Simple MCU Test Failed",
            )
            logger.error(f"Simple MCU Test execution error: {e}")

    async def _execute_usecase_menu(self) -> None:
        """Display UseCase selection menu and execute selected UseCase.

        Provides access to advanced UseCase execution system with
        comprehensive menu and selection handling.
        """
        if not self._usecase_manager:
            self._formatter.print_message(
                "UseCase manager not available. Please check system configuration.",
                message_type="error",
                title="UseCase Manager Unavailable",
            )
            return

        try:
            self._formatter.print_header(
                "UseCase Execution System", "Advanced UseCase selection and execution"
            )

            # Show available UseCases
            self._usecase_manager.list_usecases()

            # Get user selection
            selection = self._usecase_manager.show_usecase_menu()
            if not selection:
                return

            # Execute selected UseCase
            result = await self._usecase_manager.execute_usecase_by_selection(
                selection, {"EOL Force Test": None}  # Will be populated by caller
            )

            if result:
                # Wait for user acknowledgment
                await self._wait_for_user_acknowledgment()

        except Exception as e:
            self._formatter.print_message(
                f"UseCase execution error: {str(e)}", message_type="error"
            )
            logger.error(f"UseCase execution error: {e}")

    async def _execute_heating_cooling_test(self) -> None:
        """Execute Heating/Cooling Time Test through usecase manager.

        Delegates Heating/Cooling Time Test execution to the usecase manager component
        with proper error handling.
        """
        if not self._usecase_manager:
            self._formatter.print_message(
                "UseCase manager not available. Please check system configuration.",
                message_type="error",
                title="UseCase Manager Unavailable",
            )
            return

        try:
            self._formatter.print_header(
                "Heating/Cooling Time Test", "MCU temperature transition timing measurement"
            )

            # Create Heating/Cooling Time Test UseCase instance
            from application.use_cases.heating_cooling_time_test import (
                HeatingCoolingTimeTestUseCase,
            )

            # Try to get hardware services from the test executor's use case
            hardware_services = None
            if self._test_executor:
                # Access the use case from test executor (if available)
                try:
                    # Get hardware services from the test executor
                    # Access hardware services through the use case
                    if hasattr(self._test_executor, "_use_case"):
                        use_case = getattr(self._test_executor, "_use_case")
                        if hasattr(use_case, "_hardware_services"):
                            hardware_services = getattr(use_case, "_hardware_services")
                except AttributeError:
                    pass

            # Try to get hardware services from hardware manager
            if not hardware_services and self._hardware_manager:
                try:
                    if hasattr(self._hardware_manager, "get_hardware_services"):
                        hardware_services = self._hardware_manager.get_hardware_services()
                    elif hasattr(self._hardware_manager, "_hardware_facade"):
                        hardware_services = getattr(self._hardware_manager, "_hardware_facade")
                except AttributeError:
                    pass

            if not hardware_services:
                self._formatter.print_message(
                    "Hardware services not available for Heating/Cooling Test.",
                    message_type="error",
                    title="Hardware Services Unavailable",
                )
                return

            # Get configuration service from usecase manager
            configuration_service = getattr(self._usecase_manager, "configuration_service", None)
            if not configuration_service:
                self._formatter.print_message(
                    "Configuration service not available for Heating/Cooling Test.",
                    message_type="error",
                    title="Configuration Service Unavailable",
                )
                return

            # Create controller for user interaction
            from ui.cli.controllers.test.heating_cooling_test_controller import (
                HeatingCoolingTestController,
            )

            heating_cooling_usecase = HeatingCoolingTimeTestUseCase(
                hardware_services, configuration_service, self._emergency_stop_service
            )
            controller = HeatingCoolingTestController(
                heating_cooling_usecase, self._formatter, self._console
            )

            # Get cycle count from configuration file
            cycle_count = controller.get_cycle_count_from_config()

            self._formatter.print_message(
                f"Starting test with {cycle_count} cycles...", message_type="info"
            )

            # Run the test through controller
            await controller.run_test(cycle_count)

            # Wait for user acknowledgment
            await self._wait_for_user_acknowledgment()

        except KeyboardInterrupt:
            logger.info("Heating/Cooling Time Test interrupted by user (Ctrl+C)")
            self._formatter.print_message(
                "Test interrupted by user. Returning to main menu...", 
                message_type="warning", 
                title="Test Interrupted"
            )
        except Exception as e:
            logger.error(f"Heating/Cooling Time Test execution error: {e}")
            self._formatter.print_message(
                f"Heating/Cooling Time Test error: {str(e)}",
                message_type="error",
                title="Test Error",
            )

    async def _execute_robot_home(self) -> None:
        """Execute Robot Home operation.

        Performs robot homing operation to move the robot to its reference position.
        """
        if not self._hardware_manager:
            self._formatter.print_message(
                "Hardware manager not available. Please check system configuration.",
                message_type="error",
                title="Hardware Manager Unavailable",
            )
            return

        try:
            self._formatter.print_header("Robot Home Operation", "Moving robot to home position")

            # Execute robot home operation and get result
            success = await self._hardware_manager.execute_robot_home()

            if success:
                self._formatter.print_message(
                    "Robot home operation completed successfully.",
                    message_type="success",
                    title="Robot Home Complete",
                )
            else:
                self._formatter.print_message(
                    "Robot home operation failed. Check the logs for details.",
                    message_type="error",
                    title="Robot Home Failed",
                )

            # Wait for user acknowledgment
            await self._wait_for_user_acknowledgment()

        except KeyboardInterrupt:
            logger.info("Robot Home operation interrupted by user (Ctrl+C)")
            self._formatter.print_message(
                "Operation interrupted by user. Returning to main menu...", 
                message_type="warning", 
                title="Operation Interrupted"
            )
        except Exception as e:
            self._formatter.print_message(
                f"Robot home operation failed: {str(e)}",
                message_type="error",
                title="Robot Home Failed",
            )
            logger.error(f"Robot home execution error: {e}")

    async def _hardware_control_center(self) -> None:
        """Hardware Control Center - Individual hardware control interface.

        Provides access to individual hardware component control and monitoring
        through the hardware control manager.
        """
        if not self._hardware_manager:
            self._formatter.print_message(
                "Hardware Control Center is not available. Hardware facade not initialized.",
                message_type="error",
                title="Hardware Control Unavailable",
            )
            return

        try:
            self._formatter.print_header(
                "Hardware Control Center", "Individual hardware component control and monitoring"
            )

            while True:
                try:
                    selection = await self._hardware_manager.show_hardware_menu()
                    if not selection or selection == "b":
                        break

                    await self._hardware_manager.execute_hardware_control(selection)

                except (KeyboardInterrupt, EOFError):
                    break
                except Exception as e:
                    self._formatter.print_message(
                        f"Hardware control error: {str(e)}", message_type="error"
                    )
                    logger.error(f"Hardware control error: {e}")

        except Exception as e:
            self._formatter.print_message(
                f"Hardware control center error: {str(e)}", message_type="error"
            )
            logger.error(f"Hardware control center error: {e}")

    async def _wait_for_user_acknowledgment(
        self, message: str = "Press Enter to continue..."
    ) -> None:
        """Wait for user acknowledgment with enhanced input handling.

        Args:
            message: Message to display while waiting for user input
        """
        try:
            # This would integrate with the enhanced input system
            # For now, use simple input
            input(f"\n{message}")
        except KeyboardInterrupt:
            # Re-raise KeyboardInterrupt to allow SessionManager to handle emergency stop
            self._console.print("\n[dim]Interrupted by user - triggering emergency stop.[/dim]")
            raise
        except EOFError:
            # Handle EOF gracefully
            self._console.print("\n[dim]Skipped by user.[/dim]")
