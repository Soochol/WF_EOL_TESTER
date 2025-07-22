"""
Loadcell Controller Exceptions

All loadcell controller exception definitions
"""

from typing import Optional


class LoadcellError(Exception):
    """Base loadcell controller error"""

    def __init__(self, message: str, controller_type: str = "unknown", hardware_id: Optional[str] = None, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.controller_type = controller_type
        self.hardware_id = hardware_id
        self.details = details
        self.hardware_type = f"Loadcell ({controller_type})"
        
    def __str__(self) -> str:
        base_msg = self.message
        if self.details:
            base_msg = f"{base_msg}. Details: {self.details}"
        
        hardware_info = self.hardware_type
        if self.hardware_id:
            hardware_info += f" ({self.hardware_id})"
        return f"{hardware_info}: {base_msg}"


# ============================================================================
# BS205 Loadcell Specific Errors
# ============================================================================

class BS205Error(LoadcellError):
    """Base BS205 loadcell error"""

    def __init__(self, message: str, indicator_id: int = 0, command: str = "", port: Optional[str] = None):
        super().__init__(message, "BS205")
        self.indicator_id = indicator_id
        self.command = command
        self.port = port

    def __str__(self) -> str:
        base_msg = self.message
        if self.command:
            base_msg = f"{self.command}: {base_msg}"
        if self.indicator_id:
            base_msg = f"{base_msg} (Indicator ID: {self.indicator_id})"
        if self.port:
            base_msg = f"{base_msg} (Port: {self.port})"
        return f"{self.hardware_type}: {base_msg}"


class BS205ConnectionError(BS205Error):
    """BS205 serial connection errors"""
    pass


class BS205CommunicationError(BS205Error):
    """BS205 protocol communication errors (frame errors, checksum, timeout)"""
    pass


class BS205OperationError(BS205Error):
    """BS205 operation errors (measurement, calibration, configuration)"""
    pass


class BS205ValidationError(BS205Error):
    """BS205 parameter validation errors"""
    pass
