"""
EOL Force Test Sequence Package (Standalone)

This package provides the End-of-Line force test sequence implementation.
It can run in two modes:

1. Standalone Mode (Mock Hardware):
   - Uses built-in mock hardware implementations
   - Only requires loguru (no station-service-sdk needed)
   - Suitable for testing and development

2. Integrated Mode (Real Hardware):
   - Requires wf-eol-tester main project
   - Uses real hardware implementations
   - For production use

Usage:
    # Run from CLI (standalone mode)
    python -m eol_tester --start

    # Use programmatically
    from eol_tester import EOLForceTestSequence, ExecutionContext, create_standalone_hardware_adapter

    context = ExecutionContext(
        execution_id="test001",
        serial_number="DUT001",
        parameters={"voltage": 18.0, ...},
    )
    sequence = EOLForceTestSequence(context)
    result = await sequence._execute()
"""

from __future__ import annotations

import sys

# Configure loguru to output to stdout instead of stderr (before any other imports)
from loguru import logger

logger.remove()  # Remove default stderr handler
logger.add(
    sys.stdout,
    format="{time:HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    colorize=True,
)

# Import main sequence class and ExecutionContext
from .sequence import EOLForceTestSequence, ExecutionContext

# Import hardware adapter and factory functions
from .hardware_adapter import (
    EOLHardwareAdapter,
    create_standalone_hardware_adapter,
)

# Try to import integration function (only available with main project)
try:
    from .hardware_adapter import create_hardware_adapter_from_container
except ImportError:
    create_hardware_adapter_from_container = None

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
    "create_hardware_adapter_from_container",
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
