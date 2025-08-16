"""
Error handling middleware for FastAPI

Provides centralized error handling and logging for the API.
"""

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from domain.exceptions.configuration_exceptions import (
    MissingConfigurationException,
)
from domain.exceptions.hardware_exceptions import (
    HardwareConnectionException,
)
from domain.exceptions.test_exceptions import (
    TestExecutionException,
)
from domain.exceptions.validation_exceptions import (
    ValidationException,
)


async def domain_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle domain-specific exceptions"""
    logger.error(f"Domain exception in {request.url.path}: {exc}")

    if isinstance(exc, ValidationException):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": str(exc),
                "details": {
                    "field": exc.field_name if hasattr(exc, "field_name") else None,
                    "value": str(exc.value) if hasattr(exc, "value") else None,
                },
            },
        )

    elif isinstance(exc, MissingConfigurationException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "Missing Configuration",
                "message": str(exc),
                "details": {
                    "missing_parameters": (
                        exc.missing_parameters if hasattr(exc, "missing_parameters") else None
                    ),
                    "config_source": exc.config_source if hasattr(exc, "config_source") else None,
                },
            },
        )

    elif isinstance(exc, HardwareConnectionException):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Hardware Connection Error",
                "message": str(exc),
                "details": exc.details if hasattr(exc, "details") else None,
            },
        )

    elif isinstance(exc, TestExecutionException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Test Execution Error",
                "message": str(exc),
                "details": {
                    "test_id": exc.test_id if hasattr(exc, "test_id") else None,
                },
            },
        )

    # Generic domain exception
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Domain Error", "message": str(exc), "type": type(exc).__name__},
    )


async def http_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle HTTP exceptions"""
    if not isinstance(exc, HTTPException):
        # Fallback for non-HTTPException
        logger.error(f"Non-HTTP exception passed to HTTP handler in {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Unexpected Error", "message": "Internal server error"},
        )

    logger.warning(f"HTTP exception in {request.url.path}: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Error", "message": exc.detail, "status_code": exc.status_code},
    )


async def general_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected exception in {request.url.path}: {exc}", exc_info=True)

    # Don't expose internal error details in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": str(id(request)),  # Simple request ID for tracking
        },
    )


def add_error_handlers(app: FastAPI) -> None:
    """Add error handlers to FastAPI application"""

    # Domain-specific exceptions
    app.add_exception_handler(ValidationException, domain_exception_handler)
    app.add_exception_handler(MissingConfigurationException, domain_exception_handler)
    app.add_exception_handler(HardwareConnectionException, domain_exception_handler)
    app.add_exception_handler(TestExecutionException, domain_exception_handler)

    # HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Catch-all for unexpected exceptions
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Error handlers registered")
