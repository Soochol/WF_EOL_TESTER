"""
EOL Tester Main Entry Point

Simplified main application with direct service creation.
"""

# Standard library imports
import asyncio
import signal
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to Python path for module imports
# This is required because main.py is in the root directory and all source code is in src/
sys.path.append("src")

# Third-party imports
from loguru import logger

# Local application imports - Services (only needed for Button Monitoring and Emergency Stop)
from application.services.button_monitoring_service import DIOMonitoringService
from application.services.emergency_stop_service import EmergencyStopService

# Local infrastructure imports - New Dependency Injection
from infrastructure.containers import ApplicationContainer

# Local UI imports
from ui.cli.enhanced_eol_tester_cli import EnhancedEOLTesterCLI

# Application configuration constants
DEFAULT_LOG_RETENTION_PERIOD = "7 days"
LOGS_DIRECTORY_NAME = "logs"

# Generate date-based log filename to prevent Windows file lock issues
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
EOL_TESTER_LOG_FILENAME = f"eol_tester_{CURRENT_DATE}.log"


async def main() -> None:
    """Main application entry point with ApplicationContainer dependency injection."""
    setup_logging(debug=False)

    try:
        logger.info("Creating EOL Tester with ApplicationContainer...")

        # Create and configure dependency injection container
        container = ApplicationContainer()
        container.config.from_yaml("configuration/application.yaml")

        logger.info("ApplicationContainer configured successfully")

        # Get services from container
        hardware_services = container.hardware_service_facade()
        configuration_service = container.configuration_service()
        eol_force_test_use_case = container.eol_force_test_use_case()

        logger.info("Core services injected from container")

        # Get digital I/O service from hardware facade (needed for button monitoring)
        digital_io_service = hardware_services.digital_io_service

        # Connect digital I/O service if not already connected (needed for button monitoring)
        try:
            connection_status = await digital_io_service.is_connected()
            logger.info(
                f"🔧 VERIFICATION: Digital I/O service connection status: {connection_status}"
            )

            if not connection_status:
                logger.info("Connecting Digital I/O service for button monitoring...")
                await digital_io_service.connect()
                connection_status = await digital_io_service.is_connected()
                logger.info(
                    f"Digital I/O service connected successfully. Final status: {connection_status}"
                )
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

        # Services are now injected from the ApplicationContainer
        logger.info("All services successfully injected from ApplicationContainer")

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
            logger.info("🔧 VERIFICATION: Hardware config loaded successfully")
            logger.info(
                f"  - Emergency stop button: pin {hardware_config.digital_io.emergency_stop_button.pin_number}, "
                f"type {hardware_config.digital_io.emergency_stop_button.contact_type}, "
                f"edge {hardware_config.digital_io.emergency_stop_button.edge_type}"
            )
            logger.info(
                f"  - Left button: pin {hardware_config.digital_io.operator_start_button_left.pin_number}, "
                f"type {hardware_config.digital_io.operator_start_button_left.contact_type}, "
                f"edge {hardware_config.digital_io.operator_start_button_left.edge_type}"
            )
            logger.info(
                f"  - Right button: pin {hardware_config.digital_io.operator_start_button_right.pin_number}, "
                f"type {hardware_config.digital_io.operator_start_button_right.contact_type}, "
                f"edge {hardware_config.digital_io.operator_start_button_right.edge_type}"
            )
            logger.info(
                f"  - Safety sensors: door pin {hardware_config.digital_io.safety_door_closed_sensor.pin_number}, "
                f"clamp pin {hardware_config.digital_io.dut_clamp_safety_sensor.pin_number}, "
                f"chain pin {hardware_config.digital_io.dut_chain_safety_sensor.pin_number}"
            )

            # Create callback function for button press
            async def start_button_callback():
                """Execute EOL test when both buttons are pressed"""
                logger.info(
                    "🎯 VERIFICATION: Button press callback triggered - Starting EOL test..."
                )
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
            logger.info(
                "🔧 VERIFICATION: Callback functions prepared - start_button_callback, emergency_stop_callback"
            )

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
            logger.info(
                "✅ VERIFICATION: Button monitoring service created and started successfully"
            )

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
        # Services are now injected from ApplicationContainer
        try:
            command_line_interface = EnhancedEOLTesterCLI(
                eol_force_test_use_case, hardware_services, configuration_service
            )
            logger.info(
                "Starting Enhanced EOL Tester application with Rich UI (ApplicationContainer)"
            )
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
        rotation=None,  # No rotation needed - using date-based filenames
        retention=None,  # Manual cleanup - no automatic retention
        enqueue=True,  # Background thread processing to prevent file lock conflicts
        catch=True,  # Prevent logging errors from crashing the application
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
    )


# Service creation functions completely removed - now using ApplicationContainer for dependency injection
# The following functions are no longer needed:
# - create_configuration()
# - create_repositories()
# - create_business_services()
# All services are now injected via ApplicationContainer from configuration/application.yaml


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
