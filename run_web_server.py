#!/usr/bin/env python3
"""
Web Server Runner for WF EOL Tester

Standalone script to run the FastAPI web server for development and production.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import uvicorn
else:
    try:
        import uvicorn
    except ImportError:
        uvicorn = None

from loguru import logger

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Remove default logger
logger.remove()

# Add console logging
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Add file logging with date-based filename
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Generate date-based log filename to prevent Windows file lock issues
current_date = datetime.now().strftime("%Y-%m-%d")
web_server_log_filename = f"web_server_{current_date}.log"

logger.add(
    log_dir / web_server_log_filename,
    rotation=None,     # No rotation needed - using date-based filenames
    retention=None,    # Manual cleanup - no automatic retention
    enqueue=True,      # Background thread processing to prevent file lock conflicts
    catch=True,        # Prevent logging errors from crashing the application
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
)


def main():
    """Main entry point"""
    if uvicorn is None:
        logger.error("uvicorn is not installed. Please install it with: pip install uvicorn")
        sys.exit(1)

    logger.info("Starting WF EOL Tester Web Server...")

    # Configuration - Force hardcoded settings (ignore environment variables)
    host = "0.0.0.0"  # Allow external access - HARDCODED
    port = 8004  # Use port 8004 to avoid conflicts - HARDCODED
    reload = True  # Enable reload for development - HARDCODED

    # Force environment variables for consistency
    os.environ["WF_HOST"] = host
    os.environ["WF_PORT"] = str(port)
    os.environ["WF_RELOAD"] = "true"

    logger.info(f"Server configuration: {host}:{port}, reload={reload}")
    # Run the server
    uvicorn.run(
        "ui.api.main:app", host=host, port=port, reload=reload, log_level="info", access_log=True
    )


if __name__ == "__main__":
    main()
