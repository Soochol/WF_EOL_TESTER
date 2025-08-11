"""
Pydantic models for API requests and responses
"""

from .config_models import (
    ConfigurationResponse,
    ConfigurationUpdateRequest,
    ProfileListResponse,
    ProfileUsageResponse,
)
from .hardware_models import (
    HardwareStatusResponse,
    RobotControlRequest,
    RobotStatusResponse,
    PowerControlRequest,
    PowerStatusResponse,
    MCUControlRequest,
    MCUStatusResponse,
    LoadCellResponse,
    DigitalIORequest,
    DigitalIOResponse,
    HardwareConnectionRequest,
    HardwareInitializationRequest,
)
from .test_models import (
    TestExecutionRequest,
    TestExecutionResponse,
    RobotHomeRequest,
    RobotHomeResponse,
)
from .websocket_models import (
    WebSocketMessage,
    DigitalInputMessage,
    TestLogMessage,
    SystemStatusMessage,
    TestProgressMessage,
    HardwareEventMessage,
    ErrorMessage,
    WebSocketSubscription,
    WebSocketResponse,
)

__all__ = [
    # Hardware models
    "HardwareStatusResponse",
    "RobotControlRequest",
    "RobotStatusResponse",
    "PowerControlRequest",
    "PowerStatusResponse",
    "MCUControlRequest",
    "MCUStatusResponse",
    "LoadCellResponse",
    "DigitalIORequest",
    "DigitalIOResponse",
    "HardwareConnectionRequest",
    "HardwareInitializationRequest",
    # Test models
    "TestExecutionRequest",
    "TestExecutionResponse",
    "RobotHomeRequest",
    "RobotHomeResponse",
    # Configuration models
    "ConfigurationResponse",
    "ConfigurationUpdateRequest",
    "ProfileListResponse",
    "ProfileUsageResponse",
    # WebSocket models
    "WebSocketMessage",
    "DigitalInputMessage",
    "TestLogMessage",
    "SystemStatusMessage",
    "TestProgressMessage",
    "HardwareEventMessage",
    "ErrorMessage",
    "WebSocketSubscription",
    "WebSocketResponse",
]
