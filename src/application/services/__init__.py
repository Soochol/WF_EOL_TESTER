"""
Application Services Package

Reorganized services following domain-driven design principles:
- core: Configuration, repository, exception handling
- hardware: Hardware management and coordination
- test: Test execution and evaluation services
- monitoring: Safety and monitoring services
"""

# Local folder imports
# Core services
from .core import (
    ConfigurationService,
    ConfigurationValidator,
    ExceptionHandler,
    RepositoryService,
)

# Main facade (from hardware_facade package)
from .hardware_facade import HardwareServiceFacade

# Monitoring services
from .monitoring import (
    DIOMonitoringService,
    EmergencyStopService,
    PowerMonitor,
)

# Hardware services (all integrated into facade)
# Test services
from .test import (
    TestResultEvaluator,
)


__all__ = [
    # Core services
    "ConfigurationService",
    "ConfigurationValidator",
    "RepositoryService",
    "ExceptionHandler",
    # Hardware services
    "HardwareServiceFacade",
    # Test services
    "TestResultEvaluator",
    "PowerMonitor",
    # Monitoring services
    "EmergencyStopService",
    "DIOMonitoringService",
]
