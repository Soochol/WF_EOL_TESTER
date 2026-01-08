"""
EOL Force Test Sequence Package

This package provides the End-of-Line force test sequence implementation
using the station-service-sdk v2 framework.

Usage:
    # Run from CLI
    python -m eol_tester --start

    # Use programmatically
    from eol_tester import EOLForceTestSequence
    from station_service_sdk import ExecutionContext

    context = ExecutionContext(
        execution_id="test001",
        serial_number="DUT001",
        parameters={"voltage": 18.0},
    )
    sequence = EOLForceTestSequence(context)
    result = await sequence._execute()
"""

from __future__ import annotations

# Configure loguru to disable default stderr handler
# This prevents duplicate logging when running under station-service
# SDK's emit_log is the primary logging mechanism
import sys
from loguru import logger

logger.remove()  # Remove default stderr handler
logger.add(sys.stdout, level="DEBUG")  # Output to stdout (not stderr) to avoid [WARNING] [stderr] prefix

# Re-export ExecutionContext from SDK for convenience
from station_service_sdk import ExecutionContext

# Import main sequence class
from .sequence import EOLForceTestSequence

# Import hardware adapter and factory functions
from .hardware_adapter import (
    EOLHardwareAdapter,
    create_standalone_hardware_adapter,
)

# Import domain value objects for convenience
from .domain.value_objects import (
    TestConfiguration,
    HardwareConfig,
    DUTCommandInfo,
    TestMeasurements,
    CycleResult,
    PassCriteria,
)

# Import hardware interfaces
from .interfaces import (
    RobotService,
    MCUService,
    LoadCellService,
    PowerService,
    DigitalIOService,
)

# Import mock implementations
from .hardware.mock import (
    MockRobotService,
    MockMCUService,
    MockLoadCellService,
    MockPowerService,
    MockDigitalIOService,
)

__all__ = [
    # Main sequence
    "EOLForceTestSequence",
    "ExecutionContext",
    # Hardware adapter
    "EOLHardwareAdapter",
    "create_standalone_hardware_adapter",
    # Value objects
    "TestConfiguration",
    "HardwareConfig",
    "DUTCommandInfo",
    "TestMeasurements",
    "CycleResult",
    "PassCriteria",
    # Interfaces
    "RobotService",
    "MCUService",
    "LoadCellService",
    "PowerService",
    "DigitalIOService",
    # Mock implementations
    "MockRobotService",
    "MockMCUService",
    "MockLoadCellService",
    "MockPowerService",
    "MockDigitalIOService",
]

__version__ = "1.0.0"
