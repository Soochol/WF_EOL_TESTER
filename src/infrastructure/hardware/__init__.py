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
    from infrastructure.hardware.loadcell import BS205LoadCellAdapter, MockLoadCellAdapter
except ImportError:
    BS205LoadCellAdapter = None
    MockLoadCellAdapter = None

try:
    from infrastructure.hardware.power import OdaPowerAdapter, MockPowerAdapter
except ImportError:
    OdaPowerAdapter = None
    MockPowerAdapter = None

try:
    from infrastructure.hardware.mcu import LMAMCUAdapter, MockMCUAdapter
except ImportError:
    LMAMCUAdapter = None
    MockMCUAdapter = None

try:
    from infrastructure.hardware.digital_input import AjinextekInputAdapter, MockInputAdapter
except ImportError:
    AjinextekInputAdapter = None
    MockInputAdapter = None

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
if BS205LoadCellAdapter:
    __all__.extend(['BS205LoadCellAdapter', 'MockLoadCellAdapter'])
    
if OdaPowerAdapter:
    __all__.extend(['OdaPowerAdapter', 'MockPowerAdapter'])
    
if LMAMCUAdapter:
    __all__.extend(['LMAMCUAdapter', 'MockMCUAdapter'])
    
if AjinextekInputAdapter:
    __all__.extend(['AjinextekInputAdapter', 'MockInputAdapter'])
    
if JsonTestRepository:
    __all__.append('JsonTestRepository')