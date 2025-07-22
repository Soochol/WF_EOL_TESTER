"""
Dependency Injection Container

Manages dependency injection and object lifecycle for Clean Architecture components.
"""

from typing import Dict, Any, Optional
from loguru import logger

# Domain imports
from ..domain.entities.eol_test import EOLTest
from ..domain.entities.measurement import Measurement
from ..domain.entities.hardware_device import HardwareDevice

# Application layer imports
from ..application.interfaces.loadcell_service import LoadCellService
from ..application.interfaces.power_service import PowerService
from ..application.interfaces.mcu_service import MCUService
from ..application.interfaces.input_service import InputService
from ..application.interfaces.test_repository import TestRepository
from ..application.interfaces.measurement_repository import MeasurementRepository
from ..application.use_cases.execute_eol_test_use_case import ExecuteEOLTestUseCase

# Infrastructure layer imports
from ..infrastructure.service_implementations.loadcell_service_impl import LoadCellServiceImpl
from ..infrastructure.service_implementations.power_service_impl import PowerServiceImpl
from ..infrastructure.service_implementations.mcu_service_impl import MCUServiceImpl
from ..infrastructure.service_implementations.input_service_impl import InputServiceImpl
from ..infrastructure.controllers.loadcell_controller.bs205.bs205_controller import BS205Controller
from ..infrastructure.controllers.power_controller.oda.oda_power_supply import OdaPowerSupply
from ..infrastructure.controllers.dio_controller.ajinextek.dio_controller import AjinextekDIOController
from ..infrastructure.controllers.mcu_controller.lma.lma_controller import LMAController

# Adapter imports
from ..infrastructure.adapters.interfaces.loadcell_adapter import LoadCellAdapter
from ..infrastructure.adapters.interfaces.power_adapter import PowerAdapter
from ..infrastructure.adapters.interfaces.input_adapter import InputAdapter
from ..infrastructure.adapters.interfaces.mcu_adapter import MCUAdapter
from ..infrastructure.adapters.adapter_factory import AdapterFactory

# Presentation layer imports
from ..presentation.controllers.eol_test_controller import EOLTestController
from ..presentation.controllers.hardware_controller import HardwareController
from ..presentation.cli.eol_test_cli import EOLTestCLI
from ..presentation.cli.hardware_cli import HardwareCLI
from ..presentation.api.eol_test_api import EOLTestAPI
from ..presentation.api.hardware_api import HardwareAPI


class DependencyContainer:
    """Dependency injection container for Clean Architecture components"""
    
    def __init__(self, configuration: Optional[Dict[str, Any]] = None):
        """
        Initialize dependency container
        
        Args:
            configuration: Application configuration (optional)
        """
        self._configuration = configuration or {}
        self._instances = {}
        self._singletons = set()
        
        # Register default configuration
        self._setup_default_configuration()
        
        logger.info("Dependency container initialized")
    
    def _setup_default_configuration(self) -> None:
        """Setup default configuration values"""
        defaults = {
            'hardware': {
                'loadcell': {
                    'type': 'bs205',  # or 'mock'
                    'connection': {
                        'port': 'COM3',
                        'baudrate': 9600,
                        'timeout': 1.0
                    }
                },
                'power_supply': {
                    'type': 'oda',  # or 'mock'
                    'connection': {
                        'host': '192.168.1.100',
                        'port': 8080,
                        'timeout': 5.0
                    }
                },
                'dio': {
                    'type': 'ajinextek',
                    'connection': {
                        'irq_no': 7
                    }
                },
                'mcu': {
                    'type': 'lma',  # or 'mock'
                    'connection': {
                        'port': 'COM4',
                        'baudrate': 9600,
                        'timeout': 1.0
                    }
                }
            },
            'application': {
                'test_timeout': 300,  # seconds
                'measurement_precision': 3,  # decimal places
                'auto_save': True
            }
        }
        
        # Merge with provided configuration
        for key, value in defaults.items():
            if key not in self._configuration:
                self._configuration[key] = value
            elif isinstance(value, dict) and isinstance(self._configuration[key], dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in self._configuration[key]:
                        self._configuration[key][sub_key] = sub_value
    
    def register_singleton(self, interface_type: type, instance: Any) -> None:
        """
        Register singleton instance
        
        Args:
            interface_type: Interface or class type
            instance: Instance to register
        """
        self._instances[interface_type] = instance
        self._singletons.add(interface_type)
        logger.debug(f"Registered singleton: {interface_type.__name__}")
    
    def register_transient(self, interface_type: type, factory_func) -> None:
        """
        Register transient factory
        
        Args:
            interface_type: Interface or class type
            factory_func: Factory function to create instances
        """
        self._instances[interface_type] = factory_func
        logger.debug(f"Registered transient: {interface_type.__name__}")
    
    def resolve(self, interface_type: type) -> Any:
        """
        Resolve dependency instance
        
        Args:
            interface_type: Interface or class type to resolve
            
        Returns:
            Instance of the requested type
            
        Raises:
            ValueError: If type is not registered
        """
        if interface_type not in self._instances:
            raise ValueError(f"Type {interface_type.__name__} is not registered")
        
        if interface_type in self._singletons:
            # Return singleton instance
            return self._instances[interface_type]
        else:
            # Create new instance using factory
            factory = self._instances[interface_type]
            return factory()
    
    def setup_infrastructure_layer(self) -> None:
        """Setup infrastructure layer dependencies"""
        logger.info("Setting up infrastructure layer dependencies")
        
        # Setup hardware controllers
        self._setup_hardware_controllers()
        
        # Setup hardware adapters
        self._setup_hardware_adapters()
        
        # Setup service implementations
        self._setup_service_implementations()
        
        # Setup repositories (mock implementations for now)
        self._setup_repositories()
    
    def _setup_hardware_controllers(self) -> None:
        """Setup hardware controller instances"""
        # LoadCell controller
        loadcell_config = self._configuration['hardware']['loadcell']
        if loadcell_config['type'] == 'bs205':
            bs205_controller = BS205Controller(
                indicator_id=1,
                connection_info=loadcell_config['connection']
            )
            self.register_singleton(BS205Controller, bs205_controller)
        
        # Power supply controller
        power_config = self._configuration['hardware']['power_supply']
        if power_config['type'] == 'oda':
            oda_power_supply = OdaPowerSupply(
                connection_info=power_config['connection']
            )
            self.register_singleton(OdaPowerSupply, oda_power_supply)
        
        # DIO controller
        if 'dio' in self._configuration['hardware']:
            dio_config = self._configuration['hardware']['dio']
            if dio_config['type'] == 'ajinextek':
                dio_controller = AjinextekDIOController(
                    irq_no=dio_config['connection'].get('irq_no', 7)
                )
                self.register_singleton(AjinextekDIOController, dio_controller)
        
        # MCU controller
        if 'mcu' in self._configuration['hardware']:
            mcu_config = self._configuration['hardware']['mcu']
            if mcu_config['type'] == 'lma':
                lma_controller = LMAController(
                    port=mcu_config['connection']['port'],
                    baudrate=mcu_config['connection']['baudrate'],
                    timeout=mcu_config['connection']['timeout']
                )
                self.register_singleton(LMAController, lma_controller)
        
        logger.info("Hardware controllers registered")
    
    def _setup_hardware_adapters(self) -> None:
        """Setup hardware adapter instances using AdapterFactory"""
        # Validate configuration first
        try:
            AdapterFactory.validate_configuration(self._configuration['hardware'])
        except ValueError as e:
            logger.error(f"Invalid hardware configuration: {e}")
            raise
        
        # LoadCell adapter
        loadcell_config = self._configuration['hardware']['loadcell']
        def create_loadcell_adapter():
            if loadcell_config['type'] == 'bs205':
                controller = self.resolve(BS205Controller)
                return AdapterFactory.create_loadcell_adapter(loadcell_config, controller)
            else:
                return AdapterFactory.create_loadcell_adapter(loadcell_config)
        
        self.register_transient(LoadCellAdapter, create_loadcell_adapter)
        
        # Power adapter
        power_config = self._configuration['hardware']['power_supply']
        def create_power_adapter():
            if power_config['type'] == 'oda':
                controller = self.resolve(OdaPowerSupply)
                return AdapterFactory.create_power_adapter(power_config, controller)
            else:
                return AdapterFactory.create_power_adapter(power_config)
        
        self.register_transient(PowerAdapter, create_power_adapter)
        
        # DIO Input adapter (optional)
        if 'dio' in self._configuration['hardware']:
            dio_config = self._configuration['hardware']['dio']
            def create_input_adapter():
                if dio_config['type'] == 'ajinextek':
                    controller = self.resolve(AjinextekDIOController)
                    return AdapterFactory.create_input_adapter(dio_config, controller)
                else:
                    return AdapterFactory.create_input_adapter(dio_config)
            
            self.register_transient(InputAdapter, create_input_adapter)
        
        # MCU adapter (optional)
        if 'mcu' in self._configuration['hardware']:
            mcu_config = self._configuration['hardware']['mcu']
            def create_mcu_adapter():
                if mcu_config['type'] == 'lma':
                    controller = self.resolve(LMAController)
                    return AdapterFactory.create_mcu_adapter(mcu_config, controller)
                else:
                    return AdapterFactory.create_mcu_adapter(mcu_config)
            
            self.register_transient(MCUAdapter, create_mcu_adapter)
        
        logger.info("Hardware adapters registered using AdapterFactory")
    
    def _setup_service_implementations(self) -> None:
        """Setup service implementation instances"""
        # LoadCell service
        def create_loadcell_service():
            loadcell_adapter = self.resolve(LoadCellAdapter)
            return LoadCellServiceImpl(loadcell_adapter)
        
        self.register_transient(LoadCellService, create_loadcell_service)
        
        # Power service
        def create_power_service():
            power_adapter = self.resolve(PowerAdapter)
            return PowerServiceImpl(power_adapter)
        
        self.register_transient(PowerService, create_power_service)
        
        # MCU service (optional)
        if 'mcu' in self._configuration['hardware']:
            def create_mcu_service():
                mcu_adapter = self.resolve(MCUAdapter)
                return MCUServiceImpl(mcu_adapter)
            
            self.register_transient(MCUService, create_mcu_service)
        
        # Input service (optional)
        if 'dio' in self._configuration['hardware']:
            def create_input_service():
                input_adapter = self.resolve(InputAdapter)
                return InputServiceImpl(input_adapter)
            
            self.register_transient(InputService, create_input_service)
        
        logger.info("Service implementations registered")
    
    def _setup_repositories(self) -> None:
        """Setup repository implementations (mock for now)"""
        # Test repository (mock implementation)
        class MockTestRepository:
            async def save(self, test: EOLTest) -> EOLTest:
                logger.debug(f"Mock: Saving test {test.test_id}")
                return test
            
            async def update(self, test: EOLTest) -> EOLTest:
                logger.debug(f"Mock: Updating test {test.test_id}")
                return test
            
            async def find_by_id(self, test_id) -> Optional[EOLTest]:
                logger.debug(f"Mock: Finding test {test_id}")
                return None
        
        # Measurement repository (mock implementation)
        class MockMeasurementRepository:
            async def save(self, measurement: Measurement) -> Measurement:
                logger.debug(f"Mock: Saving measurement {measurement.measurement_id}")
                return measurement
            
            async def find_by_id(self, measurement_id) -> Optional[Measurement]:
                logger.debug(f"Mock: Finding measurement {measurement_id}")
                return None
            
            async def find_by_test_id(self, test_id) -> list:
                logger.debug(f"Mock: Finding measurements for test {test_id}")
                return []
        
        self.register_singleton(TestRepository, MockTestRepository())
        self.register_singleton(MeasurementRepository, MockMeasurementRepository())
        
        logger.info("Mock repositories registered")
    
    def setup_application_layer(self) -> None:
        """Setup application layer dependencies"""
        logger.info("Setting up application layer dependencies")
        
        # Use cases
        def create_execute_eol_test_use_case():
            test_repository = self.resolve(TestRepository)
            measurement_repository = self.resolve(MeasurementRepository)
            loadcell_service = self.resolve(LoadCellService)
            power_service = self.resolve(PowerService)
            
            return ExecuteEOLTestUseCase(
                test_repository=test_repository,
                measurement_repository=measurement_repository,
                loadcell_service=loadcell_service,
                power_service=power_service
            )
        
        self.register_transient(ExecuteEOLTestUseCase, create_execute_eol_test_use_case)
        
        logger.info("Application layer use cases registered")
    
    def setup_presentation_layer(self) -> None:
        """Setup presentation layer dependencies"""
        logger.info("Setting up presentation layer dependencies")
        
        # Controllers
        def create_eol_test_controller():
            execute_eol_test_use_case = self.resolve(ExecuteEOLTestUseCase)
            return EOLTestController(execute_eol_test_use_case)
        
        def create_hardware_controller():
            loadcell_service = self.resolve(LoadCellService)
            power_service = self.resolve(PowerService)
            return HardwareController(loadcell_service, power_service)
        
        self.register_transient(EOLTestController, create_eol_test_controller)
        self.register_transient(HardwareController, create_hardware_controller)
        
        # CLI interfaces
        def create_eol_test_cli():
            eol_test_controller = self.resolve(EOLTestController)
            return EOLTestCLI(eol_test_controller)
        
        def create_hardware_cli():
            hardware_controller = self.resolve(HardwareController)
            return HardwareCLI(hardware_controller)
        
        self.register_transient(EOLTestCLI, create_eol_test_cli)
        self.register_transient(HardwareCLI, create_hardware_cli)
        
        # API interfaces
        def create_eol_test_api():
            eol_test_controller = self.resolve(EOLTestController)
            return EOLTestAPI(eol_test_controller)
        
        def create_hardware_api():
            hardware_controller = self.resolve(HardwareController)
            return HardwareAPI(hardware_controller)
        
        self.register_transient(EOLTestAPI, create_eol_test_api)
        self.register_transient(HardwareAPI, create_hardware_api)
        
        logger.info("Presentation layer components registered")
    
    def initialize_all_layers(self) -> None:
        """Initialize all application layers"""
        logger.info("Initializing all application layers")
        
        try:
            self.setup_infrastructure_layer()
            self.setup_application_layer()
            self.setup_presentation_layer()
            
            logger.info("All application layers initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application layers: {e}")
            raise
    
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._configuration
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def shutdown(self) -> None:
        """Cleanup resources and shutdown container"""
        logger.info("Shutting down dependency container")
        
        # Cleanup hardware connections via adapters
        try:
            if LoadCellAdapter in self._instances:
                adapter = self.resolve(LoadCellAdapter)
                if hasattr(adapter, 'disconnect'):
                    import asyncio
                    asyncio.run(adapter.disconnect())
        except Exception as e:
            logger.warning(f"Error disconnecting LoadCell adapter: {e}")
        
        try:
            if PowerAdapter in self._instances:
                adapter = self.resolve(PowerAdapter)
                if hasattr(adapter, 'disconnect'):
                    import asyncio
                    asyncio.run(adapter.disconnect())
        except Exception as e:
            logger.warning(f"Error disconnecting Power adapter: {e}")
        
        try:
            if InputAdapter in self._instances:
                adapter = self.resolve(InputAdapter)
                if hasattr(adapter, 'disconnect'):
                    import asyncio
                    asyncio.run(adapter.disconnect())
        except Exception as e:
            logger.warning(f"Error disconnecting Input adapter: {e}")
        
        try:
            if MCUAdapter in self._instances:
                adapter = self.resolve(MCUAdapter)
                if hasattr(adapter, 'disconnect'):
                    import asyncio
                    asyncio.run(adapter.disconnect())
        except Exception as e:
            logger.warning(f"Error disconnecting MCU adapter: {e}")
        
        # Clear instances
        self._instances.clear()
        self._singletons.clear()
        
        logger.info("Dependency container shutdown complete")