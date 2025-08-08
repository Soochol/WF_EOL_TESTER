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

# Third-party imports
from loguru import logger

# Local application imports - Services
from src.application.services.button_monitoring_service import ButtonMonitoringService
from src.application.services.configuration_service import ConfigurationService
from src.application.services.configuration_validator import ConfigurationValidator
from src.application.services.exception_handler import ExceptionHandler
from src.application.services.hardware_service_facade import HardwareServiceFacade
from src.application.services.repository_service import RepositoryService
from src.application.services.test_result_evaluator import TestResultEvaluator

# Local application imports - Use Cases
from src.application.use_cases.eol_force_test import EOLForceTestUseCase

# Local infrastructure imports
from src.infrastructure.factory import ServiceFactory
from src.infrastructure.implementation.configuration.json_profile_preference import (
    JsonProfilePreference,
)
from src.infrastructure.implementation.configuration.yaml_configuration import (
    YamlConfiguration,
)
from src.infrastructure.implementation.repositories.json_result_repository import (
    JsonResultRepository,
)

# Local UI imports
from src.ui.cli.enhanced_eol_tester_cli import EnhancedEOLTesterCLI

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

        # Create services
        hardware_services = None
        try:
            # Create hardware services based on hardware model specifications
            hw_model_dict = hardware_model.to_dict()
            
            # Create services directly using model dictionary
            robot_service = ServiceFactory.create_robot_service({"model": hw_model_dict["robot"]})
            mcu_service = ServiceFactory.create_mcu_service({"model": hw_model_dict["mcu"]})
            loadcell_service = ServiceFactory.create_loadcell_service({"model": hw_model_dict["loadcell"]})
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

        # Create button monitoring service for dual button triggering
        button_monitoring_service = None
        try:
            hardware_config = await configuration_service.load_hardware_config()

            # Create callback function for button press
            async def button_press_callback():
                """Execute EOL test when both buttons are pressed"""
                logger.info("Button press callback triggered - Starting EOL test...")
                
                try:
                    # Create DUT command info for test execution
                    from src.domain.value_objects.dut_command_info import DUTCommandInfo
                    from src.application.use_cases.eol_force_test.main_executor import EOLForceTestCommand
                    
                    # Default DUT info for button-triggered tests
                    dut_info = DUTCommandInfo(
                        dut_id="BUTTON_TEST_001",
                        model_number="AUTO_TRIGGER", 
                        serial_number="BTN_" + str(int(__import__('time').time())),
                        manufacturer="Button Trigger"
                    )
                    
                    # Create command
                    command = EOLForceTestCommand(
                        dut_info=dut_info,
                        operator_id="BUTTON_OPERATOR"
                    )
                    
                    # Execute test
                    logger.info(f"Starting EOL test for DUT: {dut_info.dut_id}")
                    result = await eol_force_test_use_case.execute(command)
                    
                    logger.info(f"EOL test completed - Status: {result.test_status}, Passed: {result.is_passed}")
                    
                except Exception as e:
                    logger.error(f"Failed to execute EOL test via button press: {e}")
                    # More specific error handling could be added here based on exception types
                    import traceback
                    logger.debug(f"Button test execution traceback: {traceback.format_exc()}")

            button_monitoring_service = ButtonMonitoringService(
                digital_io_service=digital_io_service,
                hardware_config=hardware_config,
                eol_use_case=eol_force_test_use_case,
                callback=button_press_callback,
            )

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
    logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
            "<cyan>{name}</cyan> - <level>{message}</level>"
        ),
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
