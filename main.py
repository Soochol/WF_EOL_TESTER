"""
EOL Tester Main Entry Point

Simplified main application with direct service creation.
"""

# Standard library imports
import asyncio
import signal
import sys
from pathlib import Path
from typing import Tuple

# Add src directory to Python path for module imports
sys.path.append("src")

# Third-party imports
from loguru import logger

# Local application imports - Services
from application.services.button_monitoring_service import DIOMonitoringService
from application.services.configuration_service import ConfigurationService
from application.services.configuration_validator import ConfigurationValidator
from application.services.emergency_stop_service import EmergencyStopService
from application.services.exception_handler import ExceptionHandler
from application.services.hardware_service_facade import HardwareServiceFacade
from application.services.repository_service import RepositoryService
from application.services.test_result_evaluator import TestResultEvaluator

# Local application imports - Use Cases
from application.use_cases.eol_force_test.main_executor import EOLForceTestUseCase

# Local infrastructure imports
from infrastructure.configuration.json_profile_preference import JsonProfilePreference
from infrastructure.configuration.yaml_configuration import YamlConfiguration
from infrastructure.factory import ServiceFactory
from infrastructure.implementation.repositories.json_result_repository import (
    JsonResultRepository,
)

# Local UI imports
from ui.cli.enhanced_eol_tester_cli import EnhancedEOLTesterCLI

# Application configuration constants
DEFAULT_LOG_ROTATION_SIZE = "10 MB"
DEFAULT_LOG_RETENTION_PERIOD = "7 days"
LOGS_DIRECTORY_NAME = "logs"
EOL_TESTER_LOG_FILENAME = "eol_tester.log"


async def main() -> None:
    """Main application entry point with simplified orchestration."""
    setup_logging(debug=False)

    try:
        logger.info("Creating EOL Tester services...")

        # Create configuration services
        yaml_configuration, profile_preference = await create_configuration()

        # Create test result repository
        test_result_repository = await create_repositories()

        # Load hardware model
        hardware_model = await yaml_configuration.load_hardware_model()

        # Create digital I/O service first (needed by both hardware facade and button monitoring)
        hw_model_dict = hardware_model.to_dict()
        digital_io_service = ServiceFactory.create_digital_io_service(
            {"model": hw_model_dict["digital_io"]}
        )

        # Connect digital I/O service if not already connected (needed for button monitoring)
        try:
            connection_status = await digital_io_service.is_connected()
            logger.info(f"🔧 VERIFICATION: Digital I/O service connection status: {connection_status}")
            
            if not connection_status:
                logger.info("Connecting Digital I/O service for button monitoring...")
                await digital_io_service.connect()
                connection_status = await digital_io_service.is_connected()
                logger.info(f"Digital I/O service connected successfully. Final status: {connection_status}")
            else:
                logger.info("Digital I/O service already connected")
                
            # Verify I/O capabilities
            try:
                input_count = await digital_io_service.get_input_count()
                logger.info(f"🔧 VERIFICATION: Available input channels: {input_count}")
            except Exception as cap_e:
                logger.warning(f"Could not verify I/O capabilities: {cap_e}")
                
        except Exception as e:
            logger.error(f"❌ VERIFICATION: Failed to connect Digital I/O service: {e}")
            logger.warning("Button monitoring may not work properly without Digital I/O connection")

        # Create services
        hardware_services = None
        try:
            # Create hardware services based on hardware model specifications
            hw_model_dict = hardware_model.to_dict()

            # Create services directly using model dictionary
            robot_service = ServiceFactory.create_robot_service({"model": hw_model_dict["robot"]})
            mcu_service = ServiceFactory.create_mcu_service({"model": hw_model_dict["mcu"]})
            loadcell_service = ServiceFactory.create_loadcell_service(
                {"model": hw_model_dict["loadcell"]}
            )
            power_service = ServiceFactory.create_power_service({"model": hw_model_dict["power"]})

            hardware_services = HardwareServiceFacade(
                robot_service=robot_service,
                mcu_service=mcu_service,
                loadcell_service=loadcell_service,
                power_service=power_service,
                digital_io_service=digital_io_service,
            )

            (
                configuration_service,
                test_result_service,
                exception_handler,
                configuration_validator,
                test_result_evaluator,
            ) = await create_business_services(
                yaml_configuration, profile_preference, test_result_repository
            )
        except Exception as e:
            logger.error(f"Failed to create services: {e}")
            sys.exit(1)

        # Create EOL force test use case
        eol_force_test_use_case = EOLForceTestUseCase(
            hardware_services=hardware_services,
            configuration_service=configuration_service,
            configuration_validator=configuration_validator,
            repository_service=test_result_service,
            test_result_evaluator=test_result_evaluator,
            exception_handler=exception_handler,
        )

        # Create Emergency Stop Service
        emergency_stop_service = EmergencyStopService(
            hardware_facade=hardware_services,
            eol_use_case=eol_force_test_use_case,
        )

        # Create button monitoring service for dual button triggering and emergency stop
        button_monitoring_service = None
        try:
            logger.info("🔧 VERIFICATION: Loading hardware configuration for button monitoring...")
            hardware_config = await configuration_service.load_hardware_config()
            
            # Verify hardware configuration details
            logger.info(f"🔧 VERIFICATION: Hardware config loaded successfully")
            logger.info(f"  - Emergency stop button: pin {hardware_config.digital_io.emergency_stop_button.pin_number}, "
                       f"type {hardware_config.digital_io.emergency_stop_button.contact_type}, "
                       f"edge {hardware_config.digital_io.emergency_stop_button.edge_type}")
            logger.info(f"  - Left button: pin {hardware_config.digital_io.operator_start_button_left.pin_number}, "
                       f"type {hardware_config.digital_io.operator_start_button_left.contact_type}, "
                       f"edge {hardware_config.digital_io.operator_start_button_left.edge_type}")
            logger.info(f"  - Right button: pin {hardware_config.digital_io.operator_start_button_right.pin_number}, "
                       f"type {hardware_config.digital_io.operator_start_button_right.contact_type}, "
                       f"edge {hardware_config.digital_io.operator_start_button_right.edge_type}")
            logger.info(f"  - Safety sensors: door pin {hardware_config.digital_io.safety_door_closed_sensor.pin_number}, "
                       f"clamp pin {hardware_config.digital_io.dut_clamp_safety_sensor.pin_number}, "
                       f"chain pin {hardware_config.digital_io.dut_chain_safety_sensor.pin_number}")

            # Create callback function for button press
            async def start_button_callback():
                """Execute EOL test when both buttons are pressed"""
                logger.info("🎯 VERIFICATION: Button press callback triggered - Starting EOL test...")
                logger.info("🎯 VERIFICATION: Callback function successfully invoked")

                try:
                    # Create DUT command info for test execution
                    from application.use_cases.eol_force_test.main_executor import (
                        EOLForceTestCommand,
                    )
                    from domain.value_objects.dut_command_info import (
                        DUTCommandInfo,
                    )

                    # Default DUT info for button-triggered tests
                    dut_info = DUTCommandInfo(
                        dut_id="BUTTON_TEST_001",
                        model_number="AUTO_TRIGGER",
                        serial_number="BTN_" + str(int(__import__("time").time())),
                        manufacturer="Button Trigger",
                    )

                    # Create command
                    command = EOLForceTestCommand(dut_info=dut_info, operator_id="BUTTON_OPERATOR")

                    # Execute test
                    logger.info(f"Starting EOL test for DUT: {dut_info.dut_id}")
                    result = await eol_force_test_use_case.execute(command)

                    logger.info(
                        f"EOL test completed - Status: {result.test_status}, Passed: {result.is_passed}"
                    )

                except Exception as e:
                    logger.error(f"Failed to execute EOL test via button press: {e}")
                    # More specific error handling could be added here based on exception types
                    import traceback

                    logger.debug(f"Button test execution traceback: {traceback.format_exc()}")

            # Create emergency stop callback
            async def emergency_stop_callback():
                """Execute emergency stop procedure when emergency button is pressed"""
                logger.critical("🚨 VERIFICATION: Emergency stop callback triggered!")
                logger.critical("🚨 VERIFICATION: Emergency callback function successfully invoked")
                try:
                    await emergency_stop_service.execute_emergency_stop()
                except Exception as e:
                    logger.error(f"Emergency stop execution failed: {e}")
                    # Emergency stop failures should not prevent system safety
                    import traceback

                    logger.debug(f"Emergency stop traceback: {traceback.format_exc()}")

            logger.info("🔧 VERIFICATION: Creating DIOMonitoringService...")
            logger.info("🔧 VERIFICATION: Callback functions prepared - start_button_callback, emergency_stop_callback")
            
            button_monitoring_service = DIOMonitoringService(
                digital_io_service=digital_io_service,
                hardware_config=hardware_config,
                eol_use_case=eol_force_test_use_case,
                callback=start_button_callback,
                emergency_stop_callback=emergency_stop_callback,
            )
            
            logger.info("🔧 VERIFICATION: DIOMonitoringService instance created successfully")

            # Start button monitoring in background
            logger.info("🔧 VERIFICATION: Starting button monitoring in background...")
            await button_monitoring_service.start_monitoring()
            logger.info("✅ VERIFICATION: Button monitoring service created and started successfully")
            
            # Verify monitoring status
            is_monitoring = button_monitoring_service.is_monitoring()
            logger.info(f"🔧 VERIFICATION: Monitoring active status: {is_monitoring}")
            
            # Run comprehensive verification report
            logger.info("🔍 VERIFICATION: Running comprehensive verification report...")
            await button_monitoring_service.print_verification_report()
        except Exception as e:
            logger.warning(f"Failed to create button monitoring service: {e}")
            button_monitoring_service = None

        # Create and run enhanced command line interface with Rich UI
        try:
            command_line_interface = EnhancedEOLTesterCLI(
                eol_force_test_use_case, hardware_services, configuration_service
            )
            logger.info("Starting Enhanced EOL Tester application with Rich UI")
            await command_line_interface.run_interactive()
            logger.info("Enhanced EOL Tester application finished")
        except Exception as e:
            logger.error(f"CLI execution failed: {e}")
            raise
        finally:
            # Cleanup button monitoring service
            if button_monitoring_service:
                try:
                    await button_monitoring_service.stop_monitoring()
                    logger.info("Button monitoring service stopped")
                except Exception as e:
                    logger.error(f"Error stopping button monitoring service: {e}")

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception:
        logger.exception("Unexpected application error occurred")
        raise


def setup_logging(debug: bool = False) -> None:
    """
    Configure application logging with console and file output.

    Sets up structured logging with rotation and compression for file logs,
    and colored console output with appropriate log levels.

    Args:
        debug: Enable debug level logging. Defaults to False (INFO level).
    """
    # Remove default logger
    logger.remove()

    # Console logging setup
    log_level = "DEBUG" if debug else "INFO"

    # Custom formatter for noise detection warnings and MCU packet logs
    def custom_formatter(record):
        message = record["message"]
        
        if "🔧 NOISE" in message:
            # Noise detection warnings - yellow bold
            return (
                "<green>{time:HH:mm:ss}</green> | <yellow><bold>WARNING </bold></yellow> | "
                "<cyan>{name}</cyan> - <yellow><bold>{message}</bold></yellow>\n"
            )
        elif "PC -> MCU:" in message:
            # MCU transmission packets - magenta bold
            return (
                "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
                "<cyan>{name}</cyan> - <magenta><bold>{message}</bold></magenta>\n"
            )
        elif "PC <- MCU:" in message:
            # MCU reception packets - green
            return (
                "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
                "<cyan>{name}</cyan> - <green>{message}</green>\n"
            )
        else:
            # Default format
            return (
                "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
                "<cyan>{name}</cyan> - <level>{message}</level>\n"
            )

    logger.add(
        sys.stderr,
        level=log_level,
        format=custom_formatter,
    )

    # File logging setup
    logs_directory = Path(LOGS_DIRECTORY_NAME)
    logs_directory.mkdir(exist_ok=True)

    logger.add(
        logs_directory / EOL_TESTER_LOG_FILENAME,
        rotation=DEFAULT_LOG_ROTATION_SIZE,
        retention=DEFAULT_LOG_RETENTION_PERIOD,
        compression="zip",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
    )


async def create_configuration() -> Tuple[YamlConfiguration, JsonProfilePreference]:
    """Create configuration-related services.

    Returns:
        Tuple containing yaml_configuration and profile_preference services.
    """
    yaml_configuration = YamlConfiguration()
    profile_preference = JsonProfilePreference()
    return yaml_configuration, profile_preference


async def create_repositories() -> JsonResultRepository:
    """Create repository for storing test results.

    Returns:
        JsonResultRepository instance for test result storage.
    """
    test_result_repository = JsonResultRepository()
    return test_result_repository


async def create_business_services(
    yaml_configuration: YamlConfiguration,
    profile_preference: JsonProfilePreference,
    test_result_repository: JsonResultRepository,
) -> Tuple[
    ConfigurationService,
    RepositoryService,
    ExceptionHandler,
    ConfigurationValidator,
    TestResultEvaluator,
]:
    """Create business logic services.

    Args:
        yaml_configuration: YAML configuration service instance.
        profile_preference: JSON profile preference service instance.
        test_result_repository: JSON test result repository instance.

    Returns:
        Tuple containing all business service instances.
    """
    configuration_service = ConfigurationService(
        configuration=yaml_configuration,  # test_configuration, hardware_configuration
        profile_preference=profile_preference,
    )

    test_result_service = RepositoryService(test_repository=test_result_repository)
    exception_handler = ExceptionHandler()
    configuration_validator = ConfigurationValidator()
    test_result_evaluator = TestResultEvaluator()

    return (
        configuration_service,
        test_result_service,
        exception_handler,
        configuration_validator,
        test_result_evaluator,
    )


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""

    def signal_handler(signum, frame):
        """Handle termination signals"""
        _ = frame  # Unused parameter
        signal_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM",
        }

        # Add Windows-specific signals if available
        if hasattr(signal, "SIGBREAK"):
            signal_names[signal.SIGBREAK] = "SIGBREAK (Ctrl+Break)"  # type: ignore[attr-defined]

        signal_name = signal_names.get(signum, f"Signal {signum}")
        print(f"\\nReceived {signal_name}, exiting...")
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Windows-specific signal handling
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal_handler)  # type: ignore[attr-defined]


if __name__ == "__main__":
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers()

    # Use asyncio.run for Python 3.7+ compatibility
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nExiting...")
    except EOFError:
        print("\\nEOF received, exiting...")
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)
