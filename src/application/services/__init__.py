"""
Application Services Package

Reorganized services following domain-driven design principles:
- core: Configuration, repository, exception handling
- hardware: Hardware management and coordination  
- test: Test execution and evaluation services
- monitoring: Safety and monitoring services
"""

# Core services
from .core import (
    ConfigurationService,
    ConfigurationValidator,
    RepositoryService,
    ExceptionHandler,
)

# Hardware services
from .hardware import (
    HardwareConnectionManager,
    HardwareInitializationService,
    HardwareTestExecutor,
    HardwareVerificationService,
)

# Test services  
from .test import (
    TestResultEvaluator,
    PowerMonitor,
)

# Monitoring services
from .monitoring import (
    EmergencyStopService,
    DIOMonitoringService,
)

# Main facade (backward compatibility)
from .hardware_service_facade import HardwareServiceFacade

__all__ = [
    # Core services
    "ConfigurationService",
    "ConfigurationValidator", 
    "RepositoryService",
    "ExceptionHandler",
    
    # Hardware services
    "HardwareConnectionManager",
    "HardwareInitializationService", 
    "HardwareTestExecutor",
    "HardwareVerificationService",
    "HardwareServiceFacade",
    
    # Test services
    "TestResultEvaluator",
    "PowerMonitor",
    
    # Monitoring services
    "EmergencyStopService",
    "DIOMonitoringService",
]