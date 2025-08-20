"""
FastAPI Web Server for WF EOL Tester

Main FastAPI application that provides REST API endpoints and WebSocket support
for the WF EOL Tester web interface. Integrates with Clean Architecture.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from loguru import logger

from application.containers import ApplicationContainer
from ui.api.middleware.error_handler import add_error_handlers
from ui.api.routes import (
    config_router,
    hardware_router,
    status_router,
    test_router,
    websocket_router,
)


# Ultra No-Cache StaticFiles for development - COMPLETELY DISABLE CACHING
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope) -> Response:
        response = await super().get_response(path, scope)

        # ULTRA STRONG no-cache headers - DISABLE ALL CACHING
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate, max-age=0, private"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["Last-Modified"] = "Thu, 01 Jan 1970 00:00:00 GMT"
        response.headers["ETag"] = f"nocache-{hash(path)}-{hash(str(__import__('time').time()))}"
        response.headers["X-Cache-Disabled"] = "true"
        response.headers["Vary"] = "Accept-Encoding, User-Agent"

        return response


# Global application state
app_state: Dict[str, Any] = {
    "hardware_connected": False,
    "test_running": False,
    "emergency_stop": False,
}


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting WF EOL Tester API server...")

    try:
        # Initialize dependency injection container with safe config loading
        container = ApplicationContainer.load_config_safely("configuration/application.yaml")

        # NOTE: Wire the container after FastAPI app initialization
        # This avoids FastAPI signature parsing conflicts during import
        # Routes are already imported at module level
        container.wire(
            modules=[
                "ui.api.routes.hardware",
                "ui.api.routes.config",
                "ui.api.routes.status",
                "ui.api.routes.test",
                "ui.api.routes.websocket",
            ]
        )

        # Store container in app state for access in routes
        fastapi_app.state.container = container
        fastapi_app.state.app_state = app_state

        logger.info("API server started successfully with dependency injection")
        yield

    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        raise
    finally:
        logger.info("Shutting down API server...")

        # Cleanup resources
        try:
            if hasattr(fastapi_app.state, "container"):
                # Get hardware services for cleanup
                hardware_services = container.hardware_service_facade()
                if hardware_services:
                    await hardware_services.shutdown_hardware()
                    logger.info("Hardware services shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

        logger.info("API server shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="WF EOL Tester API",
    description="REST API and WebSocket server for WF EOL Tester web interface",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handling middleware
add_error_handlers(app)


# Add health endpoint before routers
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "WF EOL Tester API", "version": "1.0.0"}


# Include API routers
app.include_router(hardware_router, prefix="/api/hardware", tags=["Hardware Control"])
app.include_router(test_router, prefix="/api/tests", tags=["Test Execution"])
app.include_router(config_router, prefix="/api/config", tags=["Configuration"])
app.include_router(status_router, prefix="/api/status", tags=["System Status"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

# Serve static files and web interface
# Fix path: main.py is in src/ui/api/, web files are in src/ui/web/
web_path = Path(__file__).parent.parent / "web"
static_path = web_path / "static"

# Try fallback path if default doesn't work
if not web_path.exists() or not (web_path / "index.html").exists():
    web_path = Path("/home/blessp/my_code/WF_EOL_TESTER/src/ui/web")
    static_path = web_path / "static"

if web_path.exists() and (web_path / "index.html").exists():
    # Mount static files first (if they exist)
    if static_path.exists():
        app.mount("/static", NoCacheStaticFiles(directory=str(static_path)), name="static")
        logger.info(f"Static files served from: {static_path}")
    else:
        logger.warning(f"Static files directory not found: {static_path}")

    # Mount templates directory
    templates_path = web_path / "templates"
    if templates_path.exists():
        app.mount("/templates", NoCacheStaticFiles(directory=str(templates_path)), name="templates")
        logger.info(f"Templates served from: {templates_path}")
    else:
        logger.warning(f"Templates directory not found: {templates_path}")

    # Mount web interface at root (must be last mount)
    app.mount("/", NoCacheStaticFiles(directory=str(web_path), html=True), name="web")
    logger.info(f"Web interface served from: {web_path}")
else:
    logger.error(f"Web interface directory or index.html not found at: {web_path}")
    if web_path.exists():
        # List files in web directory for debugging
        web_files = list(web_path.iterdir())
        logger.info(f"Files in web directory: {[f.name for f in web_files]}")
    else:
        logger.error(f"Web directory does not exist at: {web_path}")


if __name__ == "__main__":
    import uvicorn

    # Configure logging with date-based filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    api_server_log_filename = f"logs/api_server_{current_date}.log"

    logger.add(
        api_server_log_filename,
        rotation=None,  # No rotation needed - using date-based filenames
        retention=None,  # Manual cleanup - no automatic retention
        enqueue=True,  # Background thread processing to prevent file lock conflicts
        catch=True,  # Prevent logging errors from crashing the application
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    )

    # Run the server (use environment variables for consistency)
    host = os.getenv("WF_HOST", "127.0.0.1")
    port = int(os.getenv("WF_PORT", "8080"))  # Changed to match your previous usage

    print(f"Server configuration: {host}:{port}, reload=True")
    print(f"Static files served from: {static_path}")
    print(f"Web interface served from: {web_path}")

    uvicorn.run("ui.api.main:app", host=host, port=port, reload=True, log_level="info")
