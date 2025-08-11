"""
Core Interfaces

Core interfaces for the EOL Tester application.
"""

# Import interfaces with error handling for Windows compatibility
__all__ = []

# Hardware interfaces
try:
    from application.interfaces.hardware.loadcell import LoadCellService
    __all__.append("LoadCellService")
except ImportError:
    pass

try:
    from application.interfaces.hardware.power import PowerService
    __all__.append("PowerService")
except ImportError:
    pass

try:
    from application.interfaces.hardware.robot import RobotService
    __all__.append("RobotService")
except ImportError:
    pass

try:
    from application.interfaces.hardware.mcu import MCUService
    __all__.append("MCUService")
except ImportError:
    pass

try:
    from application.interfaces.hardware.digital_io import DigitalIOService
    __all__.append("DigitalIOService")
except ImportError:
    pass

# Configuration interfaces
try:
    from application.interfaces.configuration.configuration import Configuration
    __all__.append("Configuration")
except ImportError:
    pass

try:
    from application.interfaces.configuration.profile_preference import ProfilePreference
    __all__.append("ProfilePreference")
except ImportError:
    pass

# Repository interfaces
try:
    from application.interfaces.repository.test_result_repository import TestResultRepository
    __all__.append("TestResultRepository")
except ImportError:
    pass
