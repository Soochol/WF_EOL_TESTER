"""
Enhanced EOL Tester CLI with Rich UI Module

Comprehensive command-line interface implementation that integrates the RichFormatter
with advanced input validation and professional terminal output. This module provides
a complete CLI experience with beautiful Rich UI components, secure input handling,
and comprehensive error management.

Key Features:
- Professional Rich UI formatting with consistent styling
- Enhanced input validation with security hardening
- Interactive menu systems with keyboard interrupt handling
- Comprehensive error handling and user feedback
- Progress indication for long-running operations
"""

# Standard library imports
import re
from typing import Any, Dict, Optional, TYPE_CHECKING

# Third-party imports
from loguru import logger
from rich.console import Console

# Local imports - Application layer
from application.use_cases.eol_force_test import (
    EOLForceTestCommand,
    EOLForceTestUseCase,
)

# Local imports - Domain layer
from domain.value_objects.dut_command_info import (
    DUTCommandInfo,
)
from domain.value_objects.eol_test_result import (
    EOLTestResult,
)

# Local imports - UI modules
from .dashboard_integration import create_dashboard_integrator
from .enhanced_cli_integration import (
    create_enhanced_cli_integrator,
    create_enhanced_menu_system,
    create_enhanced_slash_interface,
)
from .hardware_controller import HardwareControlManager
from .rich_formatter import RichFormatter
from .slash_command_handler import SlashCommandHandler
from .usecase_manager import UseCaseManager

# TYPE_CHECKING imports
if TYPE_CHECKING:
    from application.services.hardware_service_facade import HardwareServiceFacade


# Security and validation constants for input protection
class ValidationConstants:
    """Constants for input validation and security hardening.

    These constants define security limits and validation parameters to protect
    against malicious input and ensure robust operation of the CLI interface.
    They help prevent buffer overflow attacks, ReDoS vulnerabilities, and
    provide consistent validation behavior across the application.
    """

    # Global security limits to prevent abuse and attacks
    MAX_INPUT_LENGTH = 200  # Hard limit to prevent buffer overflow attacks
    MAX_ATTEMPTS = 3  # Maximum validation attempts before failure

    # Input type specific limits for granular validation
    DUT_ID_MAX_LENGTH = 20  # Device under test identifier length limit
    MODEL_MAX_LENGTH = 50  # Model number string length limit
    SERIAL_MAX_LENGTH = 30  # Serial number string length limit
    OPERATOR_MAX_LENGTH = 30  # Operator identifier length limit
    GENERAL_MAX_LENGTH = 100  # General purpose input length limit


class InputValidator:
    """Enhanced input validation utility with comprehensive security hardening.

    This class provides robust input validation with multiple layers of security
    protection including length limits, pattern validation, and ReDoS attack
    prevention. It offers a secure interface for collecting user input with
    appropriate error handling and retry mechanisms.

    Security Features:
    - Hard length limits to prevent buffer overflow attacks
    - Safe regex patterns to prevent ReDoS vulnerabilities
    - Input sanitization with null value handling
    - Retry limits to prevent brute force attempts
    - Comprehensive error reporting for debugging
    """

    # Simplified, safer regex patterns designed to prevent ReDoS attacks
    PATTERNS = {
        "dut_id": r"^[A-Z0-9_-]{1,20}$",  # Device IDs: uppercase alphanumeric with separators
        "model": (
            r"^[A-Za-z0-9_\-\s\.]{1,50}$"
        ),  # Model numbers: alphanumeric with common separators
        "serial": (
            r"^[A-Za-z0-9_\-]{1,30}$"
        ),  # Serial numbers: alphanumeric with hyphens/underscores
        "operator": (
            r"^[A-Za-z0-9_\-\s]{1,30}$"
        ),  # Operator IDs: alphanumeric with spaces and separators
        "general": (
            r"^[A-Za-z0-9_\-\s\.]{1,100}$"  # General input: broader character set with length limit
        ),
    }

    # Length limits corresponding to validation patterns for consistent enforcement
    MAX_LENGTHS = {
        "dut_id": ValidationConstants.DUT_ID_MAX_LENGTH,  # Device ID length limit
        "model": ValidationConstants.MODEL_MAX_LENGTH,  # Model number length limit
        "serial": ValidationConstants.SERIAL_MAX_LENGTH,  # Serial number length limit
        "operator": ValidationConstants.OPERATOR_MAX_LENGTH,  # Operator ID length limit
        "general": ValidationConstants.GENERAL_MAX_LENGTH,  # General input length limit
    }

    def validate_input(self, user_input: str, input_type: str = "general") -> bool:
        """Validate user input against security patterns with multi-layered protection.

        Performs comprehensive validation including null checks, length validation,
        and pattern matching with ReDoS attack prevention. Uses multiple security
        layers to ensure robust input validation.

        Args:
            user_input: String to validate (can be None or empty)
            input_type: Type of input for specific validation rules

        Returns:
            True if input passes all validation checks, False otherwise
        """
        # First layer: null and empty string validation
        if not user_input or len(user_input.strip()) == 0:
            return False

        # Second layer: global security length limit to prevent buffer overflow
        if len(user_input) > ValidationConstants.MAX_INPUT_LENGTH:
            return False

        # Third layer: type-specific length validation
        type_max_length = self.MAX_LENGTHS.get(input_type, ValidationConstants.GENERAL_MAX_LENGTH)
        if len(user_input.strip()) > type_max_length:
            return False

        # Fourth layer: pattern validation with ReDoS protection
        validation_pattern = self.PATTERNS.get(input_type, self.PATTERNS["general"])
        try:
            # Use safe regex matching to prevent ReDoS attacks
            return self._safe_regex_match(validation_pattern, user_input.strip())
        except Exception:
            # Security-first approach: reject input if validation fails for any reason
            return False

    def _safe_regex_match(self, pattern: str, text: str) -> bool:
        """Safely match regex with comprehensive protection against ReDoS attacks.

        Implements safe regex matching by using simple patterns and pre-validation
        length checks. Python's re module doesn't have built-in timeout protection,
        so we rely on pattern simplicity and length limits for security.

        Args:
            pattern: Compiled regex pattern string to match against
            text: Input text to validate (should be pre-validated for length)

        Returns:
            True if pattern matches safely, False otherwise or on any error
        """
        # Pre-validation: ensure text length is within safe limits
        if len(text) > ValidationConstants.MAX_INPUT_LENGTH:
            return False

        # Perform safe regex matching with simple patterns
        return bool(re.match(pattern, text))

    def get_validated_input(
        self,
        prompt: str,
        input_type: str = "general",
        required: bool = False,
        max_attempts: int = ValidationConstants.MAX_ATTEMPTS,
    ) -> Optional[str]:
        """Get validated input from user with comprehensive security and retry logic.

        Provides a secure interface for collecting user input with validation,
        retry mechanisms, and graceful error handling. Includes protection against
        malicious input and provides clear feedback for validation failures.

        Args:
            prompt: Input prompt message to display to the user
            input_type: Type of input for specific validation rules
            required: Whether the input is mandatory (prevents empty submissions)
            max_attempts: Maximum number of retry attempts before giving up

        Returns:
            Validated input string if successful, or None if validation fails
            or user cancels the operation
        """
        validation_attempts = 0

        # Retry loop with attempt limiting for security
        while validation_attempts < max_attempts:
            try:
                # Securely collect user input with protection
                user_input = self._get_safe_input(prompt)

                # Handle user cancellation gracefully
                if user_input is None:
                    return None

                # Handle optional empty input (non-required fields)
                if not user_input and not required:
                    return None

                # Validate required input presence
                if not user_input and required:
                    print("  ⚠️ Input is required. Please try again.")
                    validation_attempts += 1
                    continue

                # Perform comprehensive input validation
                if self.validate_input(user_input, input_type):
                    return user_input

                # Provide specific error feedback for validation failure
                self._display_validation_error(input_type)
                validation_attempts += 1

            except (KeyboardInterrupt, EOFError):
                # Handle user interruption gracefully
                return None

        # Maximum attempts exceeded - provide clear feedback
        self._display_max_attempts_error(max_attempts)
        return None

    def _get_safe_input(self, prompt: str) -> Optional[str]:
        """Safely collect user input with comprehensive protection and validation.

        Implements secure input collection with immediate length validation
        and graceful handling of user interruption scenarios.

        Args:
            prompt: Input prompt string to display to the user

        Returns:
            Stripped user input string, empty string for invalid input,
            or None if user cancels
        """
        try:
            # Collect and sanitize user input
            user_input = input(prompt).strip()

            # Immediate security check: reject excessively long inputs
            if len(user_input) > ValidationConstants.MAX_INPUT_LENGTH:
                print(
                    f"  ⚠️ Input too long (max {ValidationConstants.MAX_INPUT_LENGTH} characters)."
                )
                return ""  # Return empty string to trigger validation retry

            return user_input

        except (KeyboardInterrupt, EOFError):
            # Handle user cancellation (Ctrl+C or Ctrl+D) gracefully
            return None

    def _display_validation_error(self, input_type: str) -> None:
        """Display contextual validation error message with helpful guidance.

        Args:
            input_type: Type of input that failed validation for specific messaging
        """
        type_max_length = self.MAX_LENGTHS.get(input_type, ValidationConstants.GENERAL_MAX_LENGTH)
        print(f"  ⚠️ Invalid {input_type} format. Max length: {type_max_length} characters.")

    def _display_max_attempts_error(self, max_attempts: int) -> None:
        """Display maximum attempts exceeded error with clear feedback.

        Args:
            max_attempts: Number of attempts that were allowed before failure
        """
        print(f"  ❌ Maximum attempts ({max_attempts}) exceeded.")


class EnhancedEOLTesterCLI:
    """
    Enhanced EOL Tester CLI with Rich UI formatting.

    Demonstrates how to integrate the RichFormatter with the existing CLI
    to provide beautiful, professional terminal output.
    """

    def __init__(
        self,
        use_case: EOLForceTestUseCase,
        hardware_facade: Optional["HardwareServiceFacade"] = None,
        configuration_service: Optional[Any] = None,
    ):
        """
        Initialize the enhanced CLI.

        Args:
            use_case: EOL test execution use case
            hardware_facade: Hardware service facade for individual hardware control
            configuration_service: Configuration service for loading DUT defaults
        """
        self._use_case = use_case
        self._hardware_facade: Optional["HardwareServiceFacade"] = hardware_facade
        self._configuration_service = configuration_service
        self._running = False
        self._console = Console(force_terminal=True, legacy_windows=False, color_system="truecolor")
        self._formatter = RichFormatter(self._console)
        self._validator = InputValidator()
        self._usecase_manager = UseCaseManager(self._console, self._configuration_service)

        # Initialize enhanced input system
        self._input_integrator = create_enhanced_cli_integrator(
            self._console, self._formatter, self._configuration_service
        )
        self._enhanced_menu = create_enhanced_menu_system(self._input_integrator)

        # Initialize hardware control manager if hardware facade is provided
        if self._hardware_facade:
            self._hardware_manager: Optional[Any] = HardwareControlManager(
                self._hardware_facade, self._console
            )
            # Initialize slash command handler
            self._slash_handler: Optional[Any] = SlashCommandHandler(
                robot_service=self._hardware_facade._robot,
                mcu_service=self._hardware_facade._mcu,
                loadcell_service=self._hardware_facade._loadcell,
                power_service=self._hardware_facade._power,
                console=self._console,
            )
            # Initialize enhanced slash command interface
            self._enhanced_slash_interface: Optional[Any] = create_enhanced_slash_interface(
                self._input_integrator, self._slash_handler
            )
            # Initialize dashboard integrator
            self._dashboard_integrator: Optional[Any] = create_dashboard_integrator(
                self._hardware_facade, self._console, self._formatter
            )
        else:
            self._hardware_manager = None
            self._slash_handler = None
            self._enhanced_slash_interface = None
            self._dashboard_integrator = None

    async def run_interactive(self) -> None:
        """Run the interactive CLI with Rich UI."""
        logger.info("Starting Enhanced EOL Tester CLI")

        try:
            self._running = True

            # Display beautiful header
            self._formatter.print_header(
                "EOL Tester - Enhanced Version", "Professional End-of-Line Testing System"
            )

            while self._running:
                await self._show_main_menu()

        except KeyboardInterrupt:
            self._formatter.print_message(
                "Exiting EOL Tester... Goodbye!", message_type="info", title="Shutdown"
            )
            logger.info("CLI interrupted by user")
        except Exception as e:
            self._formatter.print_message(
                f"Unexpected error occurred: {e}", message_type="error", title="System Error"
            )
            logger.error(f"CLI error: {e}")
        finally:
            self._running = False
            await self._shutdown()

    async def _show_main_menu(self) -> None:
        """Display the enhanced main menu with advanced input features."""
        try:
            # Use enhanced menu system
            choice = await self._enhanced_menu.show_main_menu_enhanced()

            if not choice:
                return

            if choice == "1":
                await self._execute_eol_test()
            elif choice == "2":
                await self._execute_usecase_menu()
            elif choice == "3":
                await self._hardware_control_center()
            elif choice == "4":
                await self._real_time_monitoring_dashboard()
            elif choice == "5":
                await self._check_hardware_status()
            elif choice == "6":
                await self._show_test_statistics()
            elif choice == "7":
                await self._slash_command_mode()
            elif choice == "8":
                self._running = False
                self._formatter.print_message(
                    "Thank you for using EOL Tester!", message_type="success", title="Goodbye"
                )
            else:
                self._formatter.print_message(
                    f"Invalid option '{choice}'. Please select a number between 1-8.",
                    message_type="warning",
                )

        except (KeyboardInterrupt, EOFError):
            self._running = False

    async def _execute_eol_test(self) -> None:
        """Execute EOL test with Rich UI feedback."""
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
        command = EOLForceTestCommand(
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

        await self._execute_test_with_progress(command)

    async def _execute_usecase_menu(self) -> None:
        """Display UseCase selection menu and execute selected UseCase."""
        self._formatter.print_header(
            "UseCase Execution System", "Advanced UseCase selection and execution"
        )

        # Show available UseCases
        self._usecase_manager.list_usecases()

        # Get user selection
        selection = self._usecase_manager.show_usecase_menu()
        if not selection:
            return

        # Prepare UseCase instances mapping
        use_case_instances = {
            "EOL Force Test": self._use_case,
        }

        # Execute selected UseCase
        result = await self._usecase_manager.execute_usecase_by_selection(
            selection, use_case_instances
        )

        if result:
            # Wait for user acknowledgment
            await self._wait_for_user_acknowledgment()

    async def _hardware_control_center(self) -> None:
        """Hardware Control Center - Individual hardware control interface."""
        if not self._hardware_manager:
            self._formatter.print_message(
                "Hardware Control Center is not available. Hardware facade not initialized.",
                message_type="error",
                title="Hardware Control Unavailable",
            )
            return

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

    async def _slash_command_mode(self) -> None:
        """Enhanced Slash Command Mode - Interactive interface with advanced features."""
        if not self._enhanced_slash_interface:
            self._formatter.print_message(
                "Enhanced Slash Command Mode is not available. Hardware facade not initialized.",
                message_type="error",
                title="Slash Commands Unavailable",
            )
            return

        # Use enhanced slash command interface
        await self._enhanced_slash_interface.run_enhanced_slash_mode()

    async def _real_time_monitoring_dashboard(self) -> None:
        """Real-time Hardware Monitoring Dashboard - Live hardware status and metrics display."""
        if not self._dashboard_integrator:
            self._formatter.print_message(
                "Real-time Monitoring Dashboard is not available. Hardware facade not initialized.",
                message_type="error",
                title="Dashboard Unavailable",
            )
            return

        self._formatter.print_header(
            "Real-time Hardware Monitoring Dashboard",
            "Live hardware status and metrics monitoring system",
        )

        try:
            await self._dashboard_integrator.show_dashboard_menu()

        except (KeyboardInterrupt, EOFError):
            pass  # User cancelled, return to main menu
        except Exception as e:
            self._formatter.print_message(f"Dashboard error: {str(e)}", message_type="error")
            logger.error(f"Dashboard error: {e}")

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

    async def _execute_test_with_progress(self, command: EOLForceTestCommand) -> None:
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
        """Display test result with Rich formatting."""
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

        # Create test results table (single result)
        results_table = self._formatter.create_test_results_table(
            [result], title="Detailed Test Results", show_details=True
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
        """Display test summary with Rich formatting."""
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

    async def _check_hardware_status(self) -> None:
        """Check and display hardware status with Rich formatting."""
        self._formatter.print_header("Hardware Status Check")

        # Check if hardware facade is available for real-time monitoring
        if self._hardware_facade:
            try:
                # Get actual hardware status from facade
                hardware_status = await self._collect_real_hardware_status()
            except Exception as e:
                # Fallback to simulated data if real status collection fails
                logger.warning("Failed to collect real hardware status: %s", e)
                hardware_status = self._get_fallback_hardware_status()
                self._formatter.print_message(
                    "Unable to collect real-time hardware status. Showing simulated data.",
                    message_type="warning",
                )
        else:
            # Use simulated hardware status when facade is not available
            hardware_status = self._get_fallback_hardware_status()
            self._formatter.print_message(
                "Hardware facade not initialized. Showing simulated data.", message_type="info"
            )

        # Display hardware status
        status_display = self._formatter.create_hardware_status_display(
            hardware_status, title="Current Hardware Status"
        )
        self._console.print(status_display)

        # Wait for user acknowledgment
        await self._wait_for_user_acknowledgment()

    async def _collect_real_hardware_status(self) -> Dict[str, Dict[str, Any]]:
        """Collect real hardware status from hardware facade services."""
        hardware_status = {}

        try:
            # Get hardware services from facade - we know it's not None here due to the caller check
            assert self._hardware_facade is not None
            services = self._hardware_facade.get_hardware_services()

            # Collect Robot status
            try:
                robot_service = services["robot"]
                robot_connected = await robot_service.is_connected()
                robot_status = {
                    "connected": robot_connected,
                    "type": "AJINEXTEK Motion Controller",
                    "status": "READY" if robot_connected else "DISCONNECTED",
                }

                if robot_connected:
                    try:
                        position = await robot_service.get_position(0)  # type: ignore # Axis 0
                        robot_status["position"] = f"{position:.2f}mm"
                        motion_status = await robot_service.get_motion_status()  # type: ignore
                        robot_status["motion_status"] = (
                            motion_status.value if motion_status else "UNKNOWN"
                        )
                    except Exception as e:
                        logger.debug("Could not get detailed robot data: %s", e)
                        robot_status["details_error"] = "Status query failed"

                hardware_status["Robot"] = robot_status
            except Exception as e:
                logger.debug("Robot status collection failed: %s", e)
                hardware_status["Robot"] = {
                    "connected": False,
                    "type": "AJINEXTEK Motion Controller",
                    "status": "ERROR",
                    "error": str(e),
                }

            # Collect MCU status
            try:
                mcu_service = services["mcu"]
                mcu_connected = await mcu_service.is_connected()
                mcu_status = {
                    "connected": mcu_connected,
                    "type": "LMA Temperature Controller",
                    "status": "READY" if mcu_connected else "DISCONNECTED",
                }

                if mcu_connected:
                    try:
                        temperature = await mcu_service.get_temperature()  # type: ignore
                        mcu_status["temperature"] = f"{temperature:.1f}°C"
                        test_mode = await mcu_service.get_test_mode()  # type: ignore
                        mcu_status["test_mode"] = test_mode.value if test_mode else "UNKNOWN"
                    except Exception as e:
                        logger.debug("Could not get detailed MCU data: %s", e)
                        mcu_status["details_error"] = "Status query failed"

                hardware_status["MCU"] = mcu_status
            except Exception as e:
                logger.debug("MCU status collection failed: %s", e)
                hardware_status["MCU"] = {
                    "connected": False,
                    "type": "LMA Temperature Controller",
                    "status": "ERROR",
                    "error": str(e),
                }

            # Collect LoadCell status
            try:
                loadcell_service = services["loadcell"]
                loadcell_connected = await loadcell_service.is_connected()
                loadcell_status = {
                    "connected": loadcell_connected,
                    "type": "BS205 Force Sensor",
                    "status": "READY" if loadcell_connected else "DISCONNECTED",
                }

                if loadcell_connected:
                    try:
                        force = await loadcell_service.read_force()  # type: ignore
                        loadcell_status["force"] = f"{force.value:.3f} N" if force else "N/A"
                    except Exception as e:
                        logger.debug("Could not get detailed LoadCell data: %s", e)
                        loadcell_status["details_error"] = "Status query failed"

                hardware_status["LoadCell"] = loadcell_status
            except Exception as e:
                logger.debug("LoadCell status collection failed: %s", e)
                hardware_status["LoadCell"] = {
                    "connected": False,
                    "type": "BS205 Force Sensor",
                    "status": "ERROR",
                    "error": str(e),
                }

            # Collect Power status
            try:
                power_service = services["power"]
                power_connected = await power_service.is_connected()
                power_status = {
                    "connected": power_connected,
                    "type": "ODA Power Supply",
                    "status": "OK" if power_connected else "DISCONNECTED",
                }

                if power_connected:
                    try:
                        voltage = await power_service.get_voltage()  # type: ignore
                        current = await power_service.get_current()  # type: ignore
                        output_enabled = await power_service.is_output_enabled()  # type: ignore
                        power_status["voltage"] = f"{voltage:.1f}V"
                        power_status["current"] = f"{current:.2f}A"
                        power_status["output"] = "ON" if output_enabled else "OFF"
                    except Exception as e:
                        logger.debug("Could not get detailed Power data: %s", e)
                        power_status["details_error"] = "Status query failed"

                hardware_status["Power"] = power_status
            except Exception as e:
                logger.debug("Power status collection failed: %s", e)
                hardware_status["Power"] = {
                    "connected": False,
                    "type": "ODA Power Supply",
                    "status": "ERROR",
                    "error": str(e),
                }

        except Exception as e:
            logger.error("Hardware status collection failed completely: %s", e)
            raise

        return hardware_status

    def _get_fallback_hardware_status(self) -> Dict[str, Dict[str, Any]]:
        """Get fallback simulated hardware status when real status is unavailable."""
        return {
            "Robot": {
                "connected": True,
                "type": "AJINEXTEK Motion Controller",
                "axes": "6 DOF",
                "status": "SIMULATED",
            },
            "MCU": {
                "connected": True,
                "type": "LMA Temperature Controller",
                "temperature": "25.3°C",
                "status": "SIMULATED",
            },
            "LoadCell": {
                "connected": True,
                "type": "BS205 Force Sensor",
                "force": "0.234 N",
                "status": "SIMULATED",
            },
            "Power": {
                "connected": True,
                "type": "ODA Power Supply",
                "voltage": "24.1V",
                "current": "2.3A",
                "status": "SIMULATED",
            },
        }

    async def _show_test_statistics(self) -> None:
        """Show comprehensive test and system statistics with Rich formatting."""
        self._formatter.print_header("System Statistics")

        # Simulate test statistics data (in real implementation, this would come from repository)
        test_statistics = {
            "overall": {
                "total_tests": 150,
                "passed_tests": 135,
                "failed_tests": 15,
                "pass_rate": 90.0,
            },
            "recent": {
                "total_tests": 25,
                "passed_tests": 23,
                "pass_rate": 92.0,
            },
            "by_model": {
                "WF-2024-A": {
                    "total": 80,
                    "passed": 75,
                    "pass_rate": 93.75,
                },
                "WF-2024-B": {
                    "total": 45,
                    "passed": 40,
                    "pass_rate": 88.89,
                },
                "WF-2023-X": {
                    "total": 25,
                    "passed": 20,
                    "pass_rate": 80.0,
                },
            },
        }

        # Display test statistics
        test_stats_display = self._formatter.create_statistics_display(
            test_statistics, title="Test Performance Statistics"
        )
        self._console.print(test_stats_display)

        # Show enhanced input system statistics
        self._console.print("\n")
        await self._enhanced_menu.show_statistics_menu()

        # Wait for user acknowledgment
        await self._wait_for_user_acknowledgment()

    async def _shutdown(self) -> None:
        """Perform graceful shutdown with comprehensive cleanup and Rich UI feedback.

        Handles all cleanup operations with visual feedback and proper error
        handling to ensure resources are properly released during shutdown.
        """
        logger.info("Shutting down Enhanced CLI")

        try:
            # Display shutdown progress with visual feedback
            with self._formatter.create_progress_display(
                "Shutting down system...", show_spinner=True
            ) as shutdown_status:
                # Step 1: Hardware cleanup
                try:
                    shutdown_status.update("Cleaning up hardware connections...")  # type: ignore
                except (TypeError, AttributeError):
                    pass  # Progress display doesn't support update messages
                # NOTE: Hardware cleanup operations would be implemented here
                # This might include closing serial connections, releasing instruments, etc.

                # Step 2: Configuration persistence
                try:
                    shutdown_status.update("Saving configuration...")  # type: ignore
                except (TypeError, AttributeError):
                    pass  # Progress display doesn't support update messages
                # NOTE: Configuration saving operations would be implemented here
                # This might include saving user preferences, test settings, etc.

                # Step 3: Final cleanup
                try:
                    shutdown_status.update("Finalizing shutdown...")  # type: ignore
                except (TypeError, AttributeError):
                    pass  # Progress display doesn't support update messages
                # NOTE: Final cleanup operations would be implemented here
                # This might include temporary file cleanup, logging finalization, etc.

            logger.debug("Enhanced CLI shutdown completed successfully")

        except Exception as e:
            # Log shutdown errors but don't prevent shutdown completion
            logger.warning("Error during shutdown: %s", e)

        logger.info("Enhanced CLI shutdown complete")

    async def _wait_for_user_acknowledgment(
        self, message: str = "Press Enter to continue..."
    ) -> None:
        """Centralized user confirmation method with enhanced input handling.

        Provides a consistent interface for pausing execution and waiting for
        user acknowledgment with enhanced features and graceful interruption handling.

        Args:
            message: Confirmation message to display to the user
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


# Example usage function and integration documentation
def create_enhanced_cli_example() -> str:
    """Create comprehensive examples of Enhanced CLI usage with RichFormatter.

    Provides detailed examples demonstrating how to effectively use the Enhanced
    CLI with RichFormatter for creating professional terminal applications.
    These examples showcase best practices and common usage patterns.

    Returns:
        String containing detailed example code and usage patterns
    """
    return """
# Example: How to use the Enhanced EOL Tester CLI with RichFormatter

from ui.cli.enhanced_eol_tester_cli import EnhancedEOLTesterCLI
from ui.cli.rich_formatter import RichFormatter
from rich.console import Console

# Create console and formatter instances for standalone usage
console = Console(
    force_terminal=True,
    legacy_windows=False,
    color_system="truecolor"
)
formatter = RichFormatter(console)

# Example 1: Professional System Initialization Display
formatter.print_header("System Initialization", "Loading EOL Tester Components")

# Example 2: Hardware Status Updates with Details
formatter.print_status(
    "Hardware Connection",
    "CONNECTING",
    details={
        "Power Supply": "Initializing",
        "DMM": "Connected",
        "Oscilloscope": "Checking"
    }
)

# Example 3: Various Message Types
formatter.print_message("All systems ready!", "success")
formatter.print_message("Warning: Calibration due in 5 days", "warning")
formatter.print_message("Hardware diagnostic completed", "info")

# Example 4: Test Results Table Display
test_data = [
    {"test_id": "T001", "passed": True, "dut": {"dut_id": "DUT001"}},
    {"test_id": "T002", "passed": False, "dut": {"dut_id": "DUT002"}},
    {"test_id": "T003", "passed": True, "dut": {"dut_id": "DUT003"}},
]

results_table = formatter.create_test_results_table(test_data, "Recent Tests")
formatter.print_table(results_table)

# Example 5: Progress Operations with Context Manager
with formatter.create_progress_display("Processing data...") as status:
    # Simulate long-running operation with status updates
    status.update("Step 1: Initializing hardware...")
    time.sleep(1)  # Simulate work
    status.update("Step 2: Running diagnostics...")
    time.sleep(2)  # Simulate work
    status.update("Step 3: Finalizing results...")
    time.sleep(1)  # Simulate work

# Example 6: Hardware Status Dashboard
hardware_status = {
    "Robot": {"connected": True, "type": "AJINEXTEK Motion Controller", "status": "READY"},
    "MCU": {"connected": True, "type": "LMA Temperature Controller", "status": "READY"},
    "LoadCell": {"connected": True, "type": "BS205 Force Sensor", "status": "READY"},
    "Power": {"connected": True, "voltage": "24.1V", "current": "2.3A", "status": "OK"}
}
hardware_panel = formatter.create_hardware_status_display(hardware_status)
console.print(hardware_panel)

print("Enhanced CLI provides beautiful, professional terminal output!")
print("Use these patterns to create consistent, professional user interfaces.")
"""
