"""
Hardware implementations for standalone EOL Tester sequence.

Supports both mock (development/testing) and real (production) hardware.
Use HardwareFactory to create hardware instances based on configuration.
"""

from .mock import (
    MockRobotService,
    MockMCUService,
    MockLoadCellService,
    MockPowerService,
    MockDigitalIOService,
    MockLoadCell,
    MockMCU,
    MockPower,
    MockRobot,
    MockDigitalIO,
)
from .factory import HardwareFactory

__all__ = [
    # Factory
    "HardwareFactory",
    # Mock services (original names)
    "MockRobotService",
    "MockMCUService",
    "MockLoadCellService",
    "MockPowerService",
    "MockDigitalIOService",
    # Mock services (short aliases)
    "MockLoadCell",
    "MockMCU",
    "MockPower",
    "MockRobot",
    "MockDigitalIO",
]
