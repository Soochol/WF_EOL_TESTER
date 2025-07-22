"""
MCU Controller Exceptions

All MCU controller exception definitions
"""

from typing import Optional


class MCUError(Exception):
    """Base MCU controller error"""

    def __init__(self, message: str, controller_type: str = "unknown", hardware_id: Optional[str] = None, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.controller_type = controller_type
        self.hardware_id = hardware_id
        self.details = details
        self.hardware_type = f"MCU ({controller_type})"
        
    def __str__(self) -> str:
        base_msg = self.message
        if self.details:
            base_msg = f"{base_msg}. Details: {self.details}"
        
        hardware_info = self.hardware_type
        if self.hardware_id:
            hardware_info += f" ({self.hardware_id})"
        return f"{hardware_info}: {base_msg}"


# ============================================================================
# LMA MCU Specific Errors
# ============================================================================

class LMAError(MCUError):
    """Base LMA MCU error"""

    def __init__(self, message: str, error_code: int = 0, frame_data: str = ""):
        super().__init__(message, "LMA")
        self.error_code = error_code
        self.frame_data = frame_data

    def __str__(self) -> str:
        base_msg = self.message
        if self.frame_data:
            base_msg = f"{base_msg} (Frame: {self.frame_data})"
        if self.error_code:
            base_msg = f"{base_msg} (Error Code: {self.error_code})"
        return f"{self.hardware_type}: {base_msg}"


class LMACommunicationError(LMAError):
    """LMA UART communication errors (timeout, frame error, checksum)"""
    pass


class LMAProtocolError(LMAError):
    """LMA protocol errors (invalid command, unexpected response)"""
    pass


class LMAHardwareError(LMAError):
    """LMA hardware faults (temperature sensor, fan, power)"""
    pass


class LMAOperationError(LMAError):
    """LMA operation errors (invalid parameter, mode, timeout)"""
    pass


class LMASafetyError(LMAError):
    """LMA safety errors (over temperature, thermal runaway, emergency stop)"""
    pass


# Note: Direct exception instantiation is preferred in this codebase
# Example usage:
#   raise LMACommunicationError(f"Communication failed: {details}")
#   raise LMAOperationError(f"Operation failed: {error}")
#   raise LMAHardwareError(f"Hardware fault: {fault}", error_code=code)
