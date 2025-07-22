"""
Type-Safe Hardware Factory

Unified factory for creating hardware controllers with type-safe enum-based mappings.
Eliminates magic strings and provides compile-time verification.
"""

from typing import Dict, Any, List, Callable
from enum import Enum
from loguru import logger

# Removed HardwareControllerBase - using concrete types instead
# Define factory-specific exceptions locally
class HardwareInitializationError(Exception):
    """Raised when hardware initialization fails"""
    def __init__(self, message: str, details: str = ""):
        super().__init__(message)
        self.message = message
        self.details = details
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message
from ..configuration.models.hardware_config import (
    HardwareConfig,
    RobotConnectionConfig,
    DIOConnectionConfig,
    LoadcellConnectionConfig,
    PowerSupplyConnectionConfig,
    MCUConnectionConfig
)

# Import all controller classes (real implementations)
from .robot_controller.ajinextek.motion import AjinextekRobotController
from .dio_controller.ajinextek.dio_controller import AjinextekDIOController
from .loadcell_controller.bs205.bs205_controller import BS205Controller
from .power_controller.oda.oda_power_supply import OdaPowerSupply
from .mcu_controller.lma.lma_controller import LMAController

# Import all mock controller classes
from .robot_controller.mock.mock_ajinextek_robot_controller import MockAjinextekRobotController
from .dio_controller.mock.mock_ajinextek_dio_controller import MockAjinextekDIOController
from .loadcell_controller.mock.mock_bs205_controller import MockBS205Controller
from .power_controller.mock.mock_oda_power_supply import MockOdaPowerSupply
from .mcu_controller.mock.mock_lma_controller import MockLMAController


class HardwareType(Enum):
    """Type-safe hardware type enumeration"""
    ROBOT = "robot"
    DIO = "dio"
    LOADCELL = "loadcell"
    POWER_SUPPLY = "power_supply"
    MCU = "mcu"


class HardwareFactory:
    """Type-safe hardware factory with dynamic dispatch"""
    
    # Hardware initialization order (dependency-safe)
    INITIALIZATION_ORDER: List[HardwareType] = [
        HardwareType.ROBOT,
        HardwareType.DIO,
        HardwareType.LOADCELL,
        HardwareType.POWER_SUPPLY,
        HardwareType.MCU
    ]
    
    def __init__(self):
        """Initialize factory with controller creation mapping"""
        self._controller_factory: Dict[HardwareType, Callable[[Any], Any]] = {
            HardwareType.ROBOT: self._create_robot,
            HardwareType.DIO: self._create_dio,
            HardwareType.LOADCELL: self._create_loadcell,
            HardwareType.POWER_SUPPLY: self._create_power_supply,
            HardwareType.MCU: self._create_mcu
        }
    
    def create_controller(self, hardware_type: HardwareType, hardware_config: HardwareConfig):
        """Create a hardware controller instance with dynamic dispatch"""
        try:
            logger.debug(f"Creating {hardware_type.value} controller")
            
            # Get config section using Pydantic attribute access
            controller_config = getattr(hardware_config, hardware_type.value)
            
            if not controller_config:
                raise ValueError(f"Missing configuration section: {hardware_type.value}")
            
            # Dynamic dispatch - no if/elif chains! Pass Pydantic model directly
            factory_func = self._controller_factory[hardware_type]
            return factory_func(controller_config)
                
        except Exception as e:
            logger.error(f"Failed to create {hardware_type.value} controller: {e}")
            raise HardwareInitializationError(
                f"Failed to create {hardware_type.value} controller", details=str(e)
            )
    
    
    def _create_robot(self, config: RobotConnectionConfig):
        """Create robot controller (real or mock based on config)"""
        from ..configuration.models.hardware_config import HardwareControllerType
        
        if config.type == HardwareControllerType.MOCK:
            logger.info("Creating mock robot controller")
            return MockAjinextekRobotController(irq_no=config.irq_no)
        elif config.type == HardwareControllerType.AJINEXTEK:
            logger.info("Creating AJINEXTEK robot controller")
            return AjinextekRobotController(irq_no=config.irq_no)
        else:
            raise ValueError(f"Unsupported robot controller type: {config.type}")
    
    def _create_dio(self, config: DIOConnectionConfig):
        """Create DIO controller (real or mock based on config)"""
        from ..configuration.models.hardware_config import HardwareControllerType
        
        if config.type == HardwareControllerType.MOCK:
            logger.info("Creating mock DIO controller")
            return MockAjinextekDIOController(irq_no=config.irq_no)
        elif config.type == HardwareControllerType.AJINEXTEK:
            logger.info("Creating AJINEXTEK DIO controller")
            return AjinextekDIOController(irq_no=config.irq_no)
        else:
            raise ValueError(f"Unsupported DIO controller type: {config.type}")
    
    def _create_loadcell(self, config: LoadcellConnectionConfig):
        """Create loadcell controller (real or mock based on config)"""
        from ..configuration.models.hardware_config import HardwareControllerType
        
        if config.type == HardwareControllerType.MOCK:
            logger.info("Creating mock loadcell controller")
            # Mock doesn't require actual port, but we'll pass it for consistency
            return MockBS205Controller(
                port=config.port or "MOCK_PORT",
                indicator_id=config.indicator_id,
                baudrate=config.baudrate,
                timeout=config.timeout
            )
        elif config.type == HardwareControllerType.BS205:
            if not config.port:
                raise ValueError("Missing required 'port' for BS205 loadcell controller")
            
            logger.info("Creating BS205 loadcell controller")
            return BS205Controller(
                port=config.port,
                indicator_id=config.indicator_id,
                baudrate=config.baudrate,
                timeout=config.timeout
            )
        else:
            raise ValueError(f"Unsupported loadcell controller type: {config.type}")
    
    def _create_power_supply(self, config: PowerSupplyConnectionConfig):
        """Create power supply controller (real or mock based on config)"""
        from ..configuration.models.hardware_config import HardwareControllerType
        
        if config.type == HardwareControllerType.MOCK:
            logger.info("Creating mock power supply controller")
            # Mock doesn't require actual host, but we'll pass it for consistency
            return MockOdaPowerSupply(
                host=config.host or "mock.host",
                port=config.port,
                timeout=config.timeout
            )
        elif config.type == HardwareControllerType.ODA:
            if not config.host:
                raise ValueError("Missing required 'host' for ODA power supply controller")
            
            logger.info("Creating ODA power supply controller")
            return OdaPowerSupply(
                host=config.host,
                port=config.port,
                timeout=config.timeout
            )
        else:
            raise ValueError(f"Unsupported power supply controller type: {config.type}")
    
    def _create_mcu(self, config: MCUConnectionConfig):
        """Create MCU controller (real or mock based on config)"""
        from ..configuration.models.hardware_config import HardwareControllerType
        
        if config.type == HardwareControllerType.MOCK:
            logger.info("Creating mock MCU controller")
            # Mock doesn't require actual port, but we'll pass it for consistency
            return MockLMAController(
                port=config.port or "MOCK_PORT",
                baudrate=config.baudrate,
                timeout=config.timeout
            )
        elif config.type == HardwareControllerType.LMA:
            if not config.port:
                raise ValueError("Missing required 'port' for LMA MCU controller")
            
            logger.info("Creating LMA MCU controller")
            return LMAController(
                port=config.port,
                baudrate=config.baudrate,
                timeout=config.timeout
            )
        else:
            raise ValueError(f"Unsupported MCU controller type: {config.type}")


# Global factory instance
hardware_factory = HardwareFactory()