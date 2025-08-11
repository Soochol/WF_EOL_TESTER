# -*- coding: utf-8 -*-
"""
Hardware API Models - WF EOL Tester Web API

This module defines Pydantic models for hardware-related API operations:
- HardwareStatus - Status information for hardware components
- HardwareCommand - Commands sent to hardware components
- HardwareConfig - Hardware configuration settings
- HardwareError - Error information from hardware components
- ComponentStatus - Individual component status details
- EmergencyStopResponse - Response from emergency stop operation
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    """Hardware component types"""

    ROBOT = "robot"
    LOADCELL = "loadcell"
    MCU = "mcu"
    DIGITAL_IO = "digital_io"
    POWER = "power"


class ComponentStatus(str, Enum):
    """Component status values"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    BUSY = "busy"
    READY = "ready"


class HardwareStatus(BaseModel):
    """Hardware component status information"""

    component_type: ComponentType
    status: ComponentStatus
    connected: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    last_updated: datetime
    properties: Dict[str, Any] = {}

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class HardwareCommand(BaseModel):
    """Command to be sent to hardware component"""

    action: str = Field(..., description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    timeout: Optional[int] = Field(default=30, description="Command timeout in seconds")


class HardwareConfig(BaseModel):
    """Hardware configuration settings"""

    robot_config: Dict[str, Any] = {}
    loadcell_config: Dict[str, Any] = {}
    mcu_config: Dict[str, Any] = {}
    digital_io_config: Dict[str, Any] = {}
    power_config: Dict[str, Any] = {}


class HardwareError(BaseModel):
    """Hardware error information"""

    component_type: ComponentType
    error_code: str
    error_message: str
    timestamp: datetime
    severity: str = "error"


class EmergencyStopResponse(BaseModel):
    """Response from emergency stop operation"""

    success: bool
    message: str
    stopped_components: List[ComponentType]
    timestamp: datetime
