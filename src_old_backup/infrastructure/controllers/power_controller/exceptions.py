"""
Power Supply Controller Exceptions

All power supply controller exception definitions
"""

from typing import Optional


class PowerSupplyError(Exception):
    """Base power supply error"""

    def __init__(self, message: str, controller_type: str = "unknown", hardware_id: Optional[str] = None, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.controller_type = controller_type
        self.hardware_id = hardware_id
        self.details = details
        self.hardware_type = f"Power Supply ({controller_type})"
        
    def __str__(self) -> str:
        base_msg = self.message
        if self.details:
            base_msg = f"{base_msg}. Details: {self.details}"
        
        hardware_info = self.hardware_type
        if self.hardware_id:
            hardware_info += f" ({self.hardware_id})"
        return f"{hardware_info}: {base_msg}"


# ============================================================================
# ODA Power Supply Specific Errors
# ============================================================================

class ODAError(PowerSupplyError):
    """Base ODA power supply error"""

    def __init__(self, message: str, error_code: int = 0, command: str = ""):
        super().__init__(message, "ODA")
        self.error_code = error_code
        self.command = command

    def __str__(self) -> str:
        base_msg = self.message
        if self.command:
            base_msg = f"{self.command}: {base_msg}"
        if self.error_code:
            base_msg = f"{base_msg} (Error Code: {self.error_code})"
        return f"{self.hardware_type}: {base_msg}"


class ODAConnectionError(ODAError):
    """ODA TCP connection errors"""
    pass


class ODAOperationError(ODAError):
    """ODA SCPI operation errors (voltage/current setting, measurement, etc.)"""
    pass


class ODACommunicationError(ODAError):
    """ODA SCPI communication errors (command/response issues)"""
    pass
