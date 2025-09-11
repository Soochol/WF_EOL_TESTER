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


def maximize_console_window() -> None:
    """Maximize the console window on Windows."""
    try:
        import os
        if os.name == 'nt':  # Windows only
            import ctypes
            from ctypes import wintypes
            
            # Get console window handle
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            
            # Get console window
            hwnd = kernel32.GetConsoleWindow()
            if hwnd:
                # SW_MAXIMIZE = 3
                user32.ShowWindow(hwnd, 3)
                # Also set focus to the window
                user32.SetForegroundWindow(hwnd)
    except Exception as e:
        # Silently ignore errors - maximizing is not critical
        pass


async def main() -> None:
    """CLI-only application entry point with ApplicationContainer dependency injection."""
    # Force unbuffered output for real-time logging (Python environment variable equivalent)
    # This ensures logs appear immediately without keyboard input
    import os

    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

    # Maximize console window at startup
    maximize_console_window()

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
            # Default format with proper Rich markup for each level
            level_name = record.get("level", {}).get("name", "INFO")
            if level_name == "INFO":
                level_color = "blue"
            elif level_name == "WARNING":
                level_color = "yellow"
            elif level_name == "ERROR":
                level_color = "red"
            elif level_name == "DEBUG":
                level_color = "dim"
            else:
                level_color = "white"
                
            return (
                f"<green>{{time:HH:mm:ss}}</green> | <{level_color}>{{level: <8}}</{level_color}> | "
                f"<cyan>{{name}}</cyan> - <{level_color}>{{message}}</{level_color}>\n"
            )

    # Create Rich Console for log output to prevent conflicts with Rich panels
    from rich.console import Console
    rich_console = Console(
        file=sys.stderr,
        force_terminal=True,
        width=120,  # Wider width to accommodate long module names
        color_system="auto",
        legacy_windows=False
    )
    
    def rich_log_handler(message):
        """Custom loguru handler that outputs through Rich Console"""
        try:
            from rich.text import Text
            
            # Extract record for direct formatting
            record = message.record
            
            # Create Rich Text object with colors
            text = Text()
            
            # Time (green)
            time_str = record["time"].strftime("%H:%M:%S")
            text.append(time_str, style="green")
            text.append(" | ")
            
            # Level (colored by level)
            level_name = record["level"].name
            level_color = {
                "DEBUG": "dim",
                "INFO": "blue", 
                "SUCCESS": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold red"
            }.get(level_name, "white")
            
            text.append(f"{level_name: <8}", style=level_color)
            text.append(" | ")
            
            # Module name (cyan)
            text.append(record["name"], style="cyan")
            text.append(" - ")
            
            # Message (same color as level)
            text.append(str(record["message"]), style=level_color)
            
            rich_console.print(text)
        except Exception as e:
            # Fallback to stderr if Rich fails
            sys.stderr.write(f"Rich error: {e}\n")
            sys.stderr.write(str(message))
            sys.stderr.flush()
    
    logger.add(
        rich_log_handler,
        level=log_level,
        format="{message}",  # Simple format, Rich Text handles the formatting
        enqueue=False,  # Disable background queue for real-time output
        colorize=False,  # Disable loguru coloring, use Rich colors instead
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
        """Handle termination signals and cancel all asyncio tasks"""
        _ = frame  # Unused parameter
        signal_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM",
        }

        # Add Windows-specific signals if available
        if hasattr(signal, "SIGBREAK"):
            signal_names[signal.SIGBREAK] = "SIGBREAK (Ctrl+Break)"  # type: ignore[attr-defined]

        signal_name = signal_names.get(signum, f"Signal {signum}")
        print(f"\\nReceived {signal_name}, cancelling all tasks for emergency stop...")
        
        # Cancel all running asyncio tasks (this will raise CancelledError in tasks)
        try:
            loop = asyncio.get_running_loop()
            for task in asyncio.all_tasks(loop):
                if not task.done():
                    task.cancel()
                    print(f"Cancelled task: {task.get_name()}")
        except RuntimeError:
            # No event loop running
            pass
        
        # Don't raise KeyboardInterrupt here - let CancelledError propagate naturally
        # The BaseUseCase will convert CancelledError to KeyboardInterrupt for consistent handling

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Windows-specific signal handling
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal_handler)  # type: ignore[attr-defined]


if __name__ == "__main__":
    # Setup signal handlers to cancel asyncio tasks and trigger emergency stop
    setup_signal_handlers()

    # Use asyncio.run with better KeyboardInterrupt handling
    try:
        asyncio.run(main(), debug=False)
    except KeyboardInterrupt:
        print("\\nEmergency stop executed - hardware safely shutdown")
    except asyncio.CancelledError:
        print("\\nEmergency stop executed - hardware safely shutdown")
    except EOFError:
        print("\\nEOF received, exiting...")
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)
