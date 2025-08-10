"""
Pydantic models for WebSocket message types
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WebSocketMessage(BaseModel):
    """Base WebSocket message model"""
    type: str = Field(..., description="Message type")
    timestamp: str = Field(..., description="Message timestamp")
    data: Dict[str, Any] = Field(..., description="Message payload")


class DigitalInputMessage(BaseModel):
    """WebSocket message for digital input updates"""
    type: str = Field("digital_input", description="Message type")
    timestamp: str = Field(..., description="Update timestamp")
    inputs: Dict[int, bool] = Field(..., description="Digital input states (channel -> state)")
    changed_channels: List[int] = Field(..., description="Channels that changed since last update")


class TestLogMessage(BaseModel):
    """WebSocket message for test execution logs"""
    type: str = Field("test_log", description="Message type")
    timestamp: str = Field(..., description="Log timestamp")
    test_id: str = Field(..., description="Test execution ID")
    level: str = Field(..., description="Log level (INFO, WARNING, ERROR)")
    message: str = Field(..., description="Log message")
    component: Optional[str] = Field(None, description="Component that generated the log")
    progress_percentage: Optional[float] = Field(None, description="Test progress if available")


class SystemStatusMessage(BaseModel):
    """WebSocket message for system status updates"""
    type: str = Field("system_status", description="Message type")
    timestamp: str = Field(..., description="Status timestamp")
    hardware_status: Dict[str, bool] = Field(..., description="Hardware connection status")
    test_running: bool = Field(..., description="Whether a test is currently running")
    emergency_stop: bool = Field(..., description="Emergency stop status")
    active_test_id: Optional[str] = Field(None, description="ID of currently running test")
    system_load: Optional[Dict[str, float]] = Field(None, description="System resource usage")


class TestProgressMessage(BaseModel):
    """WebSocket message for test progress updates"""
    type: str = Field("test_progress", description="Message type")
    timestamp: str = Field(..., description="Update timestamp")
    test_id: str = Field(..., description="Test execution ID")
    status: str = Field(..., description="Test status")
    progress_percentage: float = Field(..., description="Progress percentage (0-100)")
    current_step: str = Field(..., description="Current test step description")
    measurements_completed: int = Field(..., description="Number of measurements completed")
    total_measurements: int = Field(..., description="Total number of measurements")
    estimated_remaining_seconds: Optional[float] = Field(None, description="Estimated time remaining")
    current_temperature: Optional[float] = Field(None, description="Current test temperature")
    current_position: Optional[float] = Field(None, description="Current robot position")


class HardwareEventMessage(BaseModel):
    """WebSocket message for hardware events"""
    type: str = Field("hardware_event", description="Message type")
    timestamp: str = Field(..., description="Event timestamp")
    hardware_type: str = Field(..., description="Hardware type (robot, mcu, power, etc.)")
    event_type: str = Field(..., description="Event type (connected, disconnected, error, etc.)")
    message: str = Field(..., description="Event description")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional event data")


class ErrorMessage(BaseModel):
    """WebSocket message for error notifications"""
    type: str = Field("error", description="Message type")
    timestamp: str = Field(..., description="Error timestamp")
    error_code: Optional[str] = Field(None, description="Error code if available")
    message: str = Field(..., description="Error message")
    component: Optional[str] = Field(None, description="Component that generated the error")
    severity: str = Field("error", description="Error severity (warning, error, critical)")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class WebSocketSubscription(BaseModel):
    """WebSocket subscription request model"""
    action: str = Field(..., description="Subscription action (subscribe, unsubscribe)")
    channels: List[str] = Field(..., description="Channels to subscribe/unsubscribe")
    filters: Optional[Dict[str, Any]] = Field(None, description="Message filters")


class WebSocketResponse(BaseModel):
    """WebSocket response model"""
    type: str = Field("response", description="Message type")
    timestamp: str = Field(..., description="Response timestamp")
    success: bool = Field(..., description="Whether the operation succeeded")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
