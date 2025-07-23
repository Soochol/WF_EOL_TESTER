"""
Hardware Module

This module contains hardware services organized by device type.
Each device type has its own folder with device-specific implementations.
"""

# Factory for creating hardware services (conditional import)
try:
    from infrastructure.hardware.factory import ServiceFactory
except ImportError:
    # Fallback when factory dependencies are not available
    ServiceFactory = None

# Device-specific implementations (conditional imports)
try:
    from infrastructure.hardware.loadcell import BS205LoadCellService, MockLoadCellService
except ImportError:
    BS205LoadCellService = None
    MockLoadCellService = None

try:
    from infrastructure.hardware.power import OdaPowerService, MockPowerService
except ImportError:
    OdaPowerService = None
    MockPowerService = None

try:
    from infrastructure.hardware.mcu import LMAMCUService, MockMCUService
except ImportError:
    LMAMCUService = None
    MockMCUService = None

try:
    from infrastructure.hardware.digital_input import AjinextekInputService, MockInputService
except ImportError:
    AjinextekInputService = None
    MockInputService = None

# Repository implementations
try:
    from infrastructure.repositories import JsonTestRepository
except ImportError:
    JsonTestRepository = None

__all__ = []

# Add factory to exports if available
if ServiceFactory:
    __all__.append('ServiceFactory')

# Add available services to exports
if BS205LoadCellService:
    __all__.extend(['BS205LoadCellService', 'MockLoadCellService'])
    
if OdaPowerService:
    __all__.extend(['OdaPowerService', 'MockPowerService'])
    
if LMAMCUService:
    __all__.extend(['LMAMCUService', 'MockMCUService'])
    
if AjinextekInputService:
    __all__.extend(['AjinextekInputService', 'MockInputService'])
    
if JsonTestRepository:
    __all__.append('JsonTestRepository')