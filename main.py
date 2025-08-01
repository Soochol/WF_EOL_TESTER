"""
EOL Tester Main Entry Point

Simplified main application with direct service creation.
"""

# Standard library imports
import asyncio
import signal
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# Third-party imports
from loguru import logger
from yaml import YAMLError

# Local application imports - Services
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
HARDWARE_CONFIG_FILENAME = "hardware.yaml"


async def main() -> None:
    """Main application entry point with simplified orchestration."""
    setup_logging(debug=False)

    try:
        logger.info("Creating EOL Tester services...")

        # Create configuration services
        yaml_configuration, profile_preference = await create_configuration()

        # Create test result repository
        test_result_repository = await create_repositories()

        # Load hardware configuration
        logger.info(f"Loading hardware configuration from {HARDWARE_CONFIG_FILENAME}...")
        try:
            hardware_config = await yaml_configuration.load_hardware_config()
            hardware_config_dict = hardware_config.to_dict()
        except FileNotFoundError as e:
            logger.error(f"Hardware configuration file not found: {e}")
            sys.exit(1)
        except YAMLError as e:
            logger.error(f"Invalid hardware configuration format: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to load hardware configuration: {e}")
            sys.exit(1)

        # Create services
        hardware_services = None
        try:
            hardware_services = await create_hardware_services(hardware_config_dict)
            
            # Perform one-time startup initialization including robot homing
            logger.info("Performing startup initialization...")
            await hardware_services.startup_initialization()
            
            business_services = await create_business_services(
                yaml_configuration, profile_preference, test_result_repository
            )
        except Exception as e:
            logger.error(f"Failed to create services: {e}")
            
            # Safety: Disable primary axis servo if hardware services were created
            if hardware_services:
                try:
                    primary_axis = await hardware_services._robot.get_primary_axis_id()
                    logger.info("Disabling servo for primary axis %d for safety due to startup failure...", primary_axis)
                    await hardware_services._robot.disable_servo(primary_axis)
                    logger.info("Primary axis servo disabled for safety")
                except Exception as servo_error:
                    logger.error(f"Failed to disable servo during cleanup: {servo_error}")
            
            sys.exit(1)

        (
            configuration_service,
            test_result_service,
            exception_handler,
            configuration_validator,
            test_result_evaluator,
        ) = business_services

        # Create EOL force test use case
        eol_force_test_use_case = EOLForceTestUseCase(
            hardware_services=hardware_services,
            configuration_service=configuration_service,
            configuration_validator=configuration_validator,
            repository_service=test_result_service,
            test_result_evaluator=test_result_evaluator,
            exception_handler=exception_handler,
        )

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
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception:
        logger.exception("Unexpected application error occurred")
        sys.exit(1)


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


async def create_hardware_services(hardware_config_dict: Dict[str, Any]) -> HardwareServiceFacade:
    """Create hardware services from configuration dictionary.

    Args:
        hardware_config_dict: Dictionary containing hardware configuration settings.

    Returns:
        HardwareServiceFacade instance with all hardware services configured.
    """
    robot_service = ServiceFactory.create_robot_service(hardware_config_dict["robot"])
    mcu_service = ServiceFactory.create_mcu_service(hardware_config_dict["mcu"])
    loadcell_service = ServiceFactory.create_loadcell_service(hardware_config_dict["loadcell"])
    power_service = ServiceFactory.create_power_service(hardware_config_dict["power"])
    digital_input_service = ServiceFactory.create_digital_input_service(
        hardware_config_dict["digital_input"]
    )

    return HardwareServiceFacade(
        robot_service=robot_service,
        mcu_service=mcu_service,
        loadcell_service=loadcell_service,
        power_service=power_service,
        digital_input_service=digital_input_service,
    )


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
        configuration=yaml_configuration,
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
