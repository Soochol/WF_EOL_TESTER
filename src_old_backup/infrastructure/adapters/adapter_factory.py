"""
Adapter Factory

Factory pattern implementation for creating hardware adapters based on configuration.
Simplifies adapter instantiation and configuration management.
"""

from typing import Dict, Any, Optional
from loguru import logger

# Adapter interfaces
from .interfaces.loadcell_adapter import LoadCellAdapter
from .interfaces.power_adapter import PowerAdapter
from .interfaces.input_adapter import InputAdapter
from .interfaces.mcu_adapter import MCUAdapter

# LoadCell adapters
from .implementations.loadcell.bs205_adapter import BS205Adapter
from .implementations.loadcell.mock_loadcell_adapter import MockLoadCellAdapter

# Power adapters
from .implementations.power.oda_adapter import OdaAdapter
from .implementations.power.mock_power_adapter import MockPowerAdapter

# Input adapters
from .implementations.input.ajinextek_dio_adapter import AjinextekDIOAdapter

# MCU adapters
from .implementations.mcu.lma_adapter import LMAAdapter
from .implementations.mcu.mock_mcu_adapter import MockMCUAdapter

# Controllers (for real hardware adapters)
from ..controllers.loadcell_controller.bs205.bs205_controller import BS205Controller
from ..controllers.power_controller.oda.oda_power_supply import OdaPowerSupply
from ..controllers.dio_controller.ajinextek.dio_controller import DIOController
from ..controllers.mcu_controller.lma.lma_controller import LMAController


class AdapterFactory:
    """Factory for creating hardware adapters based on configuration"""
    
    @staticmethod
    def create_loadcell_adapter(
        config: Dict[str, Any], 
        controller: Optional[BS205Controller] = None
    ) -> LoadCellAdapter:
        """
        Create LoadCell adapter based on configuration
        
        Args:
            config: LoadCell configuration
            controller: Optional pre-configured controller instance
            
        Returns:
            LoadCellAdapter implementation
            
        Raises:
            ValueError: If adapter type is unknown
        """
        adapter_type = config.get('type', 'mock')
        
        if adapter_type == 'bs205':
            if controller is None:
                controller = BS205Controller(
                    indicator_id=1,
                    connection_info=config.get('connection', {})
                )
            return BS205Adapter(controller)
            
        elif adapter_type == 'mock':
            return MockLoadCellAdapter()
            
        else:
            raise ValueError(f"Unknown LoadCell adapter type: {adapter_type}")
    
    @staticmethod
    def create_power_adapter(
        config: Dict[str, Any], 
        controller: Optional[OdaPowerSupply] = None
    ) -> PowerAdapter:
        """
        Create Power adapter based on configuration
        
        Args:
            config: Power supply configuration
            controller: Optional pre-configured controller instance
            
        Returns:
            PowerAdapter implementation
            
        Raises:
            ValueError: If adapter type is unknown
        """
        adapter_type = config.get('type', 'mock')
        
        if adapter_type == 'oda':
            if controller is None:
                controller = OdaPowerSupply(
                    connection_info=config.get('connection', {})
                )
            return OdaAdapter(controller)
            
        elif adapter_type == 'mock':
            return MockPowerAdapter()
            
        else:
            raise ValueError(f"Unknown Power adapter type: {adapter_type}")
    
    @staticmethod
    def create_input_adapter(
        config: Dict[str, Any], 
        controller: Optional[DIOController] = None
    ) -> InputAdapter:
        """
        Create Input adapter based on configuration
        
        Args:
            config: DIO/Input configuration
            controller: Optional pre-configured controller instance
            
        Returns:
            InputAdapter implementation
            
        Raises:
            ValueError: If adapter type is unknown
        """
        adapter_type = config.get('type', 'ajinextek')
        
        if adapter_type == 'ajinextek':
            if controller is None:
                connection_info = config.get('connection', {})
                controller = DIOController(
                    library_path=connection_info.get('library_path', ''),
                    device_id=connection_info.get('device_id', 0)
                )
            return AjinextekDIOAdapter(controller)
            
        else:
            raise ValueError(f"Unknown Input adapter type: {adapter_type}")
    
    @staticmethod
    def create_mcu_adapter(
        config: Dict[str, Any], 
        controller: Optional[LMAController] = None
    ) -> MCUAdapter:
        """
        Create MCU adapter based on configuration
        
        Args:
            config: MCU configuration
            controller: Optional pre-configured controller instance
            
        Returns:
            MCUAdapter implementation
            
        Raises:
            ValueError: If adapter type is unknown
        """
        adapter_type = config.get('type', 'mock')
        
        if adapter_type == 'lma':
            if controller is None:
                connection_info = config.get('connection', {})
                controller = LMAController(
                    port=connection_info.get('port', 'COM3'),
                    baudrate=connection_info.get('baudrate', 9600),
                    timeout=connection_info.get('timeout', 1.0)
                )
            return LMAAdapter(controller)
            
        elif adapter_type == 'mock':
            return MockMCUAdapter()
            
        else:
            raise ValueError(f"Unknown MCU adapter type: {adapter_type}")
    
    @staticmethod
    def create_all_adapters(hardware_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create all adapters based on hardware configuration
        
        Args:
            hardware_config: Complete hardware configuration
            
        Returns:
            Dictionary of adapter instances
        """
        adapters = {}
        
        try:
            # Create LoadCell adapter
            if 'loadcell' in hardware_config:
                loadcell_adapter = AdapterFactory.create_loadcell_adapter(
                    hardware_config['loadcell']
                )
                adapters['loadcell'] = loadcell_adapter
                logger.info(f"Created LoadCell adapter: {loadcell_adapter.vendor}")
            
            # Create Power adapter
            if 'power_supply' in hardware_config:
                power_adapter = AdapterFactory.create_power_adapter(
                    hardware_config['power_supply']
                )
                adapters['power'] = power_adapter
                logger.info(f"Created Power adapter: {power_adapter.vendor}")
            
            # Create Input adapter
            if 'dio' in hardware_config:
                input_adapter = AdapterFactory.create_input_adapter(
                    hardware_config['dio']
                )
                adapters['input'] = input_adapter
                logger.info(f"Created Input adapter: {input_adapter.vendor}")
            
            # Create MCU adapter
            if 'mcu' in hardware_config:
                mcu_adapter = AdapterFactory.create_mcu_adapter(
                    hardware_config['mcu']
                )
                adapters['mcu'] = mcu_adapter
                logger.info(f"Created MCU adapter: {mcu_adapter.vendor}")
            
            logger.info(f"Created {len(adapters)} hardware adapters")
            return adapters
            
        except Exception as e:
            logger.error(f"Failed to create adapters: {e}")
            raise
    
    @staticmethod
    def validate_configuration(hardware_config: Dict[str, Any]) -> bool:
        """
        Validate hardware configuration for adapter creation
        
        Args:
            hardware_config: Hardware configuration to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        required_sections = ['loadcell', 'power_supply']
        
        for section in required_sections:
            if section not in hardware_config:
                raise ValueError(f"Missing required configuration section: {section}")
            
            section_config = hardware_config[section]
            if 'type' not in section_config:
                raise ValueError(f"Missing 'type' in {section} configuration")
        
        # Validate LoadCell configuration
        loadcell_config = hardware_config['loadcell']
        if loadcell_config['type'] == 'bs205':
            if 'connection' not in loadcell_config:
                raise ValueError("BS205 requires connection configuration")
        
        # Validate Power configuration
        power_config = hardware_config['power_supply']
        if power_config['type'] == 'oda':
            if 'connection' not in power_config:
                raise ValueError("ODA requires connection configuration")
        
        # Validate DIO configuration (optional)
        if 'dio' in hardware_config:
            dio_config = hardware_config['dio']
            if 'type' not in dio_config:
                raise ValueError("Missing 'type' in dio configuration")
            
            if dio_config['type'] == 'ajinextek':
                if 'connection' not in dio_config:
                    raise ValueError("Ajinextek DIO requires connection configuration")
        
        # Validate MCU configuration (optional)
        if 'mcu' in hardware_config:
            mcu_config = hardware_config['mcu']
            if 'type' not in mcu_config:
                raise ValueError("Missing 'type' in mcu configuration")
            
            if mcu_config['type'] == 'lma':
                if 'connection' not in mcu_config:
                    raise ValueError("LMA MCU requires connection configuration")
        
        logger.info("Hardware configuration validation passed")
        return True