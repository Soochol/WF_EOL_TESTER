"""
Robot Controller Exceptions

All robot controller exception definitions
"""

from typing import Optional


class RobotError(Exception):
    """Base robot controller error"""
    
    def __init__(self, message: str, controller_type: str = "unknown", hardware_id: Optional[str] = None, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.controller_type = controller_type
        self.hardware_id = hardware_id
        self.details = details

    def __str__(self) -> str:
        base_msg = self.message
        if self.details:
            base_msg = f"{base_msg}. Details: {self.details}"

        hardware_info = f"Robot ({self.controller_type})"
        if self.hardware_id:
            hardware_info += f" ({self.hardware_id})"
        return f"{hardware_info}: {base_msg}"


class RobotConnectionError(RobotError):
    """Base robot controller error"""
    
    def __init__(self, message: str, controller_type: str = "unknown", **kwargs):
        super().__init__(message, f"Robot ({controller_type})", **kwargs)


class RobotConnectionError(RobotError):
    """Generic robot connection error"""
    
    def __init__(self, message: str, controller_type: str = "unknown", **kwargs):
        super().__init__(message, controller_type, **kwargs)


# ============================================================================
# AJINEXTEK AXL Robot Specific Errors
# ============================================================================

class AXLError(RobotError):
    """Base AJINEXTEK AXL error"""
    
    def __init__(self, message: str, error_code: int = 0, function_name: str = ""):
        super().__init__(message, "AJINEXTEK AXL")
        self.error_code = error_code
        self.function_name = function_name
        
    def __str__(self) -> str:
        base_msg = self.message
        if self.function_name:
            base_msg = f"{self.function_name}: {base_msg}"
        if self.error_code:
            base_msg = f"{base_msg} (Error Code: {self.error_code})"
        return f"{self.hardware_type}: {base_msg}"


class AXLConnectionError(AXLError):
    """AXL library connection/initialization errors"""
    pass


class AXLMotionError(AXLError):
    """AXL motion operation errors"""
    pass


# ============================================================================
# Future Robot Vendors (for expansion)
# ============================================================================

class ABBError(RobotError):
    """ABB robot errors"""
    
    def __init__(self, message: str, robot_id: str = "", program_name: str = ""):
        super().__init__(message, "ABB")
        self.robot_id = robot_id
        self.program_name = program_name


class KUKAError(RobotError):
    """KUKA robot errors"""
    
    def __init__(self, message: str, robot_id: str = "", program_name: str = ""):
        super().__init__(message, "KUKA")
        self.robot_id = robot_id
        self.program_name = program_name


class UniversalRobotsError(RobotError):
    """Universal Robots (UR) errors"""
    
    def __init__(self, message: str, robot_model: str = "", script_name: str = ""):
        super().__init__(message, "Universal Robots")
        self.robot_model = robot_model
        self.script_name = script_name


class FANUCError(RobotError):
    """FANUC robot errors"""
    
    def __init__(self, message: str, controller_id: str = "", program_name: str = ""):
        super().__init__(message, "FANUC")
        self.controller_id = controller_id
        self.program_name = program_name


# ============================================================================
# Convenience functions for creating common exceptions
# ============================================================================

def create_axl_connection_error(error_code: int, function_name: str, error_message: str) -> AXLConnectionError:
    """Create a standardized AXL connection error"""
    return AXLConnectionError(error_message, error_code, function_name)


def create_axl_motion_error(error_code: int, function_name: str, error_message: str) -> AXLMotionError:
    """Create a standardized AXL motion error"""
    return AXLMotionError(error_message, error_code, function_name)