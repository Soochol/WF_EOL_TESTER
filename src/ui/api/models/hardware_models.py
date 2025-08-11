"""
Pydantic models for hardware control API endpoints
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

__all__ = [
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
]


class HardwareStatusResponse(BaseModel):
    """Response model for hardware status"""

    robot: bool
    mcu: bool
    power: bool
    loadcell: bool
    digital_io: bool
    overall_status: str = Field(..., description="Overall hardware status")

    @classmethod
    def from_status_dict(cls, status: Dict[str, bool]) -> "HardwareStatusResponse":
        """Create response from status dictionary"""
        all_connected = all(status.values())
        overall_status = (
            "connected" if all_connected else "partial" if any(status.values()) else "disconnected"
        )

        return cls(
            robot=status.get("robot", False),
            mcu=status.get("mcu", False),
            power=status.get("power", False),
            loadcell=status.get("loadcell", False),
            digital_io=status.get("digital_io", False),
            overall_status=overall_status,
        )


class RobotControlRequest(BaseModel):
    """Request model for robot control operations"""

    operation: str = Field(
        ..., description="Operation to perform: 'home', 'move', 'enable', 'disable'"
    )
    axis_id: Optional[int] = Field(0, description="Robot axis ID")
    position: Optional[float] = Field(None, description="Target position in micrometers")
    velocity: Optional[float] = Field(None, description="Movement velocity")
    acceleration: Optional[float] = Field(None, description="Movement acceleration")
    deceleration: Optional[float] = Field(None, description="Movement deceleration")


class RobotStatusResponse(BaseModel):
    """Response model for robot status"""

    connected: bool
    axis_id: int
    current_position: Optional[float] = Field(None, description="Current position in micrometers")
    is_homed: Optional[bool] = Field(None, description="Whether axis is homed")
    servo_enabled: Optional[bool] = Field(None, description="Whether servo is enabled")
    is_moving: Optional[bool] = Field(None, description="Whether robot is currently moving")
    error_message: Optional[str] = None


class PowerControlRequest(BaseModel):
    """Request model for power supply control"""

    operation: str = Field(
        ..., description="Operation: 'enable', 'disable', 'set_voltage', 'set_current'"
    )
    voltage: Optional[float] = Field(None, description="Voltage to set")
    current: Optional[float] = Field(None, description="Current to set")
    current_limit: Optional[float] = Field(None, description="Current limit to set")


class PowerStatusResponse(BaseModel):
    """Response model for power supply status"""

    connected: bool
    output_enabled: bool
    voltage: Optional[float] = Field(None, description="Current voltage setting")
    current: Optional[float] = Field(None, description="Current setting")
    measured_voltage: Optional[float] = Field(None, description="Measured output voltage")
    measured_current: Optional[float] = Field(None, description="Measured output current")
    error_message: Optional[str] = None


class MCUControlRequest(BaseModel):
    """Request model for MCU control operations"""

    operation: str = Field(
        ..., description="Operation: 'set_temperature', 'set_fan_speed', 'test_mode'"
    )
    temperature: Optional[float] = Field(None, description="Target temperature")
    fan_speed: Optional[int] = Field(None, description="Fan speed (0-10)")
    test_mode: Optional[int] = Field(None, description="Test mode number")


class MCUStatusResponse(BaseModel):
    """Response model for MCU status"""

    connected: bool
    boot_complete: Optional[bool] = Field(None, description="Whether MCU boot is complete")
    current_temperature: Optional[float] = Field(None, description="Current temperature")
    target_temperature: Optional[float] = Field(None, description="Target temperature")
    fan_speed: Optional[int] = Field(None, description="Current fan speed")
    test_mode: Optional[int] = Field(None, description="Current test mode")
    error_message: Optional[str] = None


class LoadCellResponse(BaseModel):
    """Response model for load cell readings"""

    connected: bool
    force_value: Optional[float] = Field(None, description="Current force reading")
    unit: Optional[str] = Field(None, description="Force unit (e.g., 'N', 'kg')")
    is_holding: Optional[bool] = Field(None, description="Whether load cell is holding reading")
    error_message: Optional[str] = None


class DigitalIORequest(BaseModel):
    """Request model for digital I/O operations"""

    operation: str = Field(
        ..., description="Operation: 'read_input', 'write_output', 'read_all_inputs'"
    )
    channel: Optional[int] = Field(None, description="Channel number")
    value: Optional[bool] = Field(None, description="Output value for write operations")


class DigitalIOResponse(BaseModel):
    """Response model for digital I/O status"""

    connected: bool
    inputs: Optional[Dict[int, bool]] = Field(None, description="Digital input states")
    outputs: Optional[Dict[int, bool]] = Field(None, description="Digital output states")
    channel_value: Optional[bool] = Field(None, description="Value for specific channel operation")
    error_message: Optional[str] = None


class HardwareConnectionRequest(BaseModel):
    """Request model for hardware connection operations"""

    operation: str = Field(..., description="Operation: 'connect', 'disconnect'")
    hardware_types: Optional[List[str]] = Field(
        None, description="Specific hardware to connect/disconnect"
    )


class HardwareInitializationRequest(BaseModel):
    """Request model for hardware initialization"""

    profile_name: Optional[str] = Field(None, description="Configuration profile to use")
    force_reconnect: bool = Field(False, description="Force reconnection of hardware")
