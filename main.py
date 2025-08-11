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

# Add src to Python path for consistent imports
current_dir = Path(__file__).parent
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Third-party imports
from loguru import logger  # noqa: E402

# Local application imports - Services  
from application.services.button_monitoring_service import ButtonMonitoringService  # noqa: E402
from application.services.configuration_service import ConfigurationService  # noqa: E402
from application.services.configuration_validator import ConfigurationValidator  # noqa: E402
from application.services.emergency_stop_service import EmergencyStopService  # noqa: E402
from application.services.exception_handler import ExceptionHandler  # noqa: E402
from application.services.hardware_service_facade import HardwareServiceFacade  # noqa: E402
from application.services.repository_service import RepositoryService  # noqa: E402
from application.services.test_result_evaluator import TestResultEvaluator  # noqa: E402

# Local application imports - Use Cases
from application.use_cases.eol_force_test import EOLForceTestUseCase  # noqa: E402
from infrastructure.configuration.json_profile_preference import (  # noqa: E402
    JsonProfilePreference,
)
from infrastructure.configuration.yaml_configuration import (  # noqa: E402
    YamlConfiguration,
)

# Local infrastructure imports
from infrastructure.factory import ServiceFactory  # noqa: E402
from infrastructure.implementation.repositories.json_result_repository import (  # noqa: E402
    JsonResultRepository,
)

# Local UI imports
from ui.cli.enhanced_eol_tester_cli import EnhancedEOLTesterCLI  # noqa: E402

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
            if not await digital_io_service.is_connected():
                logger.info("Connecting Digital I/O service for button monitoring...")
                await digital_io_service.connect()
                logger.info("Digital I/O service connected successfully")
            else:
                logger.info("Digital I/O service already connected")
        except Exception as e:
            logger.warning(f"Failed to connect Digital I/O service: {e}")
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
            hardware_config = await configuration_service.load_hardware_config()

            # Create callback function for button press
            async def button_press_callback():
                """Execute EOL test when both buttons are pressed"""
                logger.info("Button press callback triggered - Starting EOL test...")

                try:
                    # Create DUT command info for test execution
                    from application.use_cases.eol_force_test.main_executor import (  # noqa: E402
                        EOLForceTestCommand,
                    )
                    from domain.value_objects.dut_command_info import DUTCommandInfo  # noqa: E402

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
                logger.critical("Emergency stop callback triggered!")
                try:
                    await emergency_stop_service.execute_emergency_stop()
                except Exception as e:
                    logger.error(f"Emergency stop execution failed: {e}")
                    # Emergency stop failures should not prevent system safety
                    import traceback

                    logger.debug(f"Emergency stop traceback: {traceback.format_exc()}")

            button_monitoring_service = ButtonMonitoringService(
                digital_io_service=digital_io_service,
                hardware_config=hardware_config,
                eol_use_case=eol_force_test_use_case,
                callback=button_press_callback,
            )

            # Set emergency stop callback
            button_monitoring_service.set_emergency_stop_callback(emergency_stop_callback)

            # Start button monitoring in background
            await button_monitoring_service.start_monitoring()
            logger.info("Button monitoring service created and started successfully")
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

    # Custom formatter for noise detection warnings
    def noise_formatter(record):
        if "🔧 NOISE" in record["message"]:
            return (
                "<green>{time:HH:mm:ss}</green> | <yellow><bold>WARNING </bold></yellow> | "
                "<cyan>{name}</cyan> - <yellow><bold>{message}</bold></yellow>\n"
            )
        else:
            return (
                "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
                "<cyan>{name}</cyan> - <level>{message}</level>\n"
            )

    logger.add(
        sys.stderr,
        level=log_level,
        format=noise_formatter,
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
