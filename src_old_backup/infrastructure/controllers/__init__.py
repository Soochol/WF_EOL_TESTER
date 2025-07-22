"""
Infrastructure Controllers Module

This module contains direct hardware controllers for hardware control.
Provides direct access to hardware controllers without abstraction layers.

Architecture:
- Direct hardware controllers (BS205Controller, AjinExtekRobotController, etc.)
- Type-safe factory for controller creation
- Hardware-specific exception handling
- Mock controllers for testing
"""

# Direct Hardware Controllers
from .loadcell_controller.bs205.bs205_controller import BS205Controller
from .mcu_controller.lma.lma_controller import LMAController
from .power_controller.oda.oda_power_supply import OdaPowerSupply
from .robot_controller.ajinextek.motion import AjinExtekRobotController
from .dio_controller.ajinextek.dio_controller import AjinExtekDIOController

# Mock Controllers
from .loadcell_controller.mock.mock_bs205_controller import MockBS205Controller
from .mcu_controller.mock.mock_lma_controller import MockLMAController
from .power_controller.mock.mock_oda_power_supply import MockOdaPowerSupply
from .robot_controller.mock.mock_ajinextek_robot_controller import MockAjinExtekRobotController
from .dio_controller.mock.mock_ajinextek_dio_controller import MockAjinExtekDIOController

# Type-Safe Factory
from .factory import HardwareFactory

# Note: Hardware-specific exceptions are now defined within each controller's package
# Use BS205Error, LMAError, RobotError, etc. instead of generic HardwareError

__all__ = [
    # Direct Hardware Controllers
    'BS205Controller',
    'LMAController', 
    'OdaPowerSupply',
    'AjinExtekRobotController',
    'AjinExtekDIOController',
    
    # Mock Controllers
    'MockBS205Controller',
    'MockLMAController',
    'MockOdaPowerSupply',
    'MockAjinExtekRobotController',
    'MockAjinExtekDIOController',
    
    # Type-Safe Factory
    'HardwareFactory',
]