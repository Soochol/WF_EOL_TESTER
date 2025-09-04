#!/usr/bin/env python3
"""
EOL Tester CLI-Only Entry Point

Pure CLI application without hardware monitoring or web dependencies.
Simplified main application optimized for command-line interface usage.
"""

# Standard library imports
import asyncio
import signal
import sys
from datetime import datetime
from pathlib import Path

# Module imports now work directly since main_cli.py is in the src/ directory
# Third-party imports
from loguru import logger

# Local infrastructure imports - Dependency Injection
from application.containers import ApplicationContainer

# Local UI imports
from ui.cli.enhanced_eol_tester_cli import EnhancedEOLTesterCLI

# Application configuration constants
DEFAULT_LOG_RETENTION_PERIOD = "7 days"
LOGS_DIRECTORY_NAME = "Logs/application"

# Generate date-based log filename to prevent Windows file lock issues
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
EOL_TESTER_CLI_LOG_FILENAME = f"eol_tester_cli_{CURRENT_DATE}.log"


async def main() -> None:
    """CLI-only application entry point with ApplicationContainer dependency injection."""
    # Force unbuffered output for real-time logging (Python environment variable equivalent)
    # This ensures logs appear immediately without keyboard input
    import os

    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

    setup_logging(debug=False)

    try:
        logger.info("Creating CLI-only EOL Tester with ApplicationContainer...")

        # Create and configure dependency injection container
        container = ApplicationContainer.create()
        logger.info("ApplicationContainer configured successfully")

        # Get core services from container
        hardware_services = container.hardware_service_facade()
        configuration_service = container.configuration_service()
        eol_force_test_use_case = container.eol_force_test_use_case()

        logger.info("Core services injected from container")

        # Get Emergency Stop Service from container
        emergency_stop_service = container.emergency_stop_service()
        logger.info("Emergency Stop Service injected from container")

        # Optional hardware connection with graceful fallback
        await setup_optional_hardware_connection(hardware_services)

        # Create and run enhanced command line interface with Rich UI
        try:
            command_line_interface = EnhancedEOLTesterCLI(
                eol_force_test_use_case,
                hardware_services,
                configuration_service,
                emergency_stop_service,
            )
            logger.info("Starting CLI-only EOL Tester application with Rich UI")
            await command_line_interface.run_interactive()
            logger.info("CLI-only EOL Tester application finished")
        except Exception as e:
            logger.error(f"CLI execution failed: {e}")
            raise

    except KeyboardInterrupt:
        logger.info("CLI-only application interrupted by user (Ctrl+C)")
        # Emergency stop is now handled by SessionManager through CLI application
    except Exception:
        logger.exception("Unexpected application error occurred")
        raise


async def setup_optional_hardware_connection(hardware_services) -> None:
    """
    Setup hardware connections with graceful fallback for CLI-only mode.

    This function attempts to connect hardware services but continues
    operation even if hardware is not available.
    """
    try:
        dio = hardware_services.digital_io_service
        is_connected = await dio.is_connected()

        logger.info(f"🔧 Digital I/O status: {'connected' if is_connected else 'disconnected'}")

        if not is_connected:
            logger.info("Attempting to connect Digital I/O service...")
            await dio.connect()
            is_connected = await dio.is_connected()

        if is_connected:
            logger.info("✅ Digital I/O service ready")
            try:
                channels = await dio.get_input_count()
                logger.info(f"🔧 Available input channels: {channels}")
            except Exception as cap_e:
                logger.debug(f"Channel verification skipped: {cap_e}")
        else:
            logger.warning("⚠️ Digital I/O service unavailable")

    except Exception as e:
        logger.warning(f"⚠️ Hardware setup failed: {e}")
        logger.info("💡 CLI will continue in software-only mode")


def setup_logging(debug: bool = False) -> None:
    """
    Configure simplified CLI application logging.

    Sets up lightweight logging optimized for CLI usage with console
    and file output.

    Args:
        debug: Enable debug level logging. Defaults to False (INFO level).
    """
    # Remove default logger
    logger.remove()

    # Console logging setup
    log_level = "DEBUG" if debug else "INFO"

    # Simplified formatter for CLI mode
    def cli_formatter(record):
        message = record["message"]

        # Special formatting for different message types
        if "✅" in message or "🔧" in message:
            # Success and verification messages - green
            return (
                "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
                "<cyan>{name}</cyan> - <green>{message}</green>\n"
            )
        elif "⚠️" in message or "💡" in message:
            # Warning and info messages - yellow
            return (
                "<green>{time:HH:mm:ss}</green> | <yellow><bold>WARNING </bold></yellow> | "
                "<cyan>{name}</cyan> - <yellow>{message}</yellow>\n"
            )
        elif "❌" in message or "🚨" in message:
            # Error messages - red
            return (
                "<green>{time:HH:mm:ss}</green> | <red><bold>ERROR   </bold></red> | "
                "<cyan>{name}</cyan> - <red><bold>{message}</bold></red>\n"
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
        format=cli_formatter,
        enqueue=False,  # Disable background queue for real-time output
        colorize=True,  # Enable color output
        serialize=False,  # Disable serialization for faster output
        backtrace=True,
        diagnose=True,
    )

    # Force immediate stdout/stderr flushing
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(line_buffering=True)  # type: ignore
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore

    # File logging setup
    logs_directory = Path(LOGS_DIRECTORY_NAME)
    logs_directory.mkdir(parents=True, exist_ok=True)

    logger.add(
        logs_directory / EOL_TESTER_CLI_LOG_FILENAME,
        rotation=None,  # No rotation needed - using date-based filenames
        retention=None,  # Manual cleanup - no automatic retention
        enqueue=False,  # Disable queue for consistent timing with console output
        catch=True,  # Prevent logging errors from crashing the application
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
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
        print("\\nSafely exiting CLI-only application after hardware shutdown...")
    except EOFError:
        print("\\nEOF received, exiting...")
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)
