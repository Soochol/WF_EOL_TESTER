"""
Dependency Injection Container for FastAPI

Manages dependency injection for the FastAPI application,
integrating with the existing Clean Architecture components.
"""

from functools import lru_cache
from typing import Optional

from loguru import logger

from application.services.configuration_service import ConfigurationService
from application.services.hardware_service_facade import HardwareServiceFacade
from application.use_cases.eol_force_test import EOLForceTestUseCase
from application.use_cases.robot_home import RobotHomeUseCase
from infrastructure.implementation.configuration.yaml_configuration import (
    YamlConfiguration,
)
from infrastructure.implementation.hardware.digital_io.mock.mock_digital_io import (
    MockDigitalIO,
)
from infrastructure.implementation.hardware.loadcell.mock.mock_loadcell import (
    MockLoadCell,
)
from infrastructure.implementation.hardware.mcu.mock.mock_mcu import MockMCU
from infrastructure.implementation.hardware.power.mock.mock_power import MockPower
from infrastructure.implementation.hardware.robot.mock.mock_robot import MockRobot


class DIContainer:
    """
    Dependency Injection Container
    
    Manages the creation and lifecycle of all application dependencies.
    Uses singleton pattern for services that should be shared across requests.
    """
    
    def __init__(self):
        self._hardware_service_facade: Optional[HardwareServiceFacade] = None
        self._configuration_service: Optional[ConfigurationService] = None
        self._eol_force_test_use_case: Optional[EOLForceTestUseCase] = None
        self._robot_home_use_case: Optional[RobotHomeUseCase] = None
        
    def hardware_service_facade(self) -> HardwareServiceFacade:
        """Get or create hardware service facade"""
        if self._hardware_service_facade is None:
            logger.info("Initializing hardware services...")
            
            # For now, use mock implementations
            # In production, these would be configured based on hardware_configuration.yaml
            robot_service = MockRobot()
            mcu_service = MockMCU()
            loadcell_service = MockLoadCell()
            power_service = MockPower()
            digital_io_service = MockDigitalIO()
            
            self._hardware_service_facade = HardwareServiceFacade(
                robot_service=robot_service,
                mcu_service=mcu_service,
                loadcell_service=loadcell_service,
                power_service=power_service,
                digital_io_service=digital_io_service,
            )
            
            logger.info("Hardware service facade initialized")
            
        return self._hardware_service_facade
    
    def configuration_service(self) -> ConfigurationService:
        """Get or create configuration service"""
        if self._configuration_service is None:
            logger.info("Initializing configuration service...")
            
            # Create YAML configuration implementation
            yaml_config = YamlConfiguration()
            
            # For now, no profile preference (can be added later)
            self._configuration_service = ConfigurationService(
                configuration=yaml_config,
                profile_preference=None,
            )
            
            logger.info("Configuration service initialized")
            
        return self._configuration_service
    
    def eol_force_test_use_case(self) -> EOLForceTestUseCase:
        """Get or create EOL force test use case"""
        if self._eol_force_test_use_case is None:
            logger.info("Initializing EOL force test use case...")
            
            hardware_services = self.hardware_service_facade()
            config_service = self.configuration_service()
            
            self._eol_force_test_use_case = EOLForceTestUseCase(
                hardware_services=hardware_services,
                config_service=config_service,
            )
            
            logger.info("EOL force test use case initialized")
            
        return self._eol_force_test_use_case
    
    def robot_home_use_case(self) -> RobotHomeUseCase:
        """Get or create robot home use case"""
        if self._robot_home_use_case is None:
            logger.info("Initializing robot home use case...")
            
            hardware_services = self.hardware_service_facade()
            
            self._robot_home_use_case = RobotHomeUseCase(
                hardware_services=hardware_services,
            )
            
            logger.info("Robot home use case initialized")
            
        return self._robot_home_use_case
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up dependency container...")
        
        try:
            if self._hardware_service_facade:
                await self._hardware_service_facade.shutdown_hardware()
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        logger.info("Dependency container cleanup completed")


# Global container instance
_container: Optional[DIContainer] = None


@lru_cache()
def get_container() -> DIContainer:
    """Get the global dependency injection container"""
    global _container
    if _container is None:
        _container = DIContainer()
        logger.info("Dependency injection container created")
    return _container


def reset_container():
    """Reset the container (mainly for testing)"""
    global _container
    _container = None
    get_container.cache_clear()
