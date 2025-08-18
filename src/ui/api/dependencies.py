"""
Dependency Injection Container for FastAPI

Manages dependency injection for the FastAPI application,
integrating with the existing Clean Architecture components.
"""

from functools import lru_cache
from typing import Optional

from loguru import logger

from application.services.configuration_service import ConfigurationService
from application.services.configuration_validator import ConfigurationValidator
from application.services.exception_handler import ExceptionHandler
from application.services.hardware_service_facade import HardwareServiceFacade
from application.services.repository_service import RepositoryService
from application.services.test_result_evaluator import TestResultEvaluator
from application.use_cases.eol_force_test import EOLForceTestUseCase
from application.use_cases.robot_home import RobotHomeUseCase
from infrastructure.implementation.configuration.yaml_configuration import (
    YamlConfiguration,
)


class DIContainer:
    """
    Dependency Injection Container

    Manages the creation and lifecycle of all application dependencies.
    Uses singleton pattern for services that should be shared across requests.
    """

    def __init__(self):
        self._hardware_service_facade: Optional[HardwareServiceFacade] = None
        self._configuration_service: Optional[ConfigurationService] = None
        self._configuration_validator: Optional[ConfigurationValidator] = None
        self._test_result_evaluator: Optional[TestResultEvaluator] = None
        self._repository_service: Optional[RepositoryService] = None
        self._exception_handler: Optional[ExceptionHandler] = None
        self._eol_force_test_use_case: Optional[EOLForceTestUseCase] = None
        # Note: robot_home_use_case is created fresh each time with current config

    async def hardware_service_facade(self) -> HardwareServiceFacade:
        """Get or create hardware service facade"""
        if self._hardware_service_facade is None:
            logger.info("Initializing hardware services...")

            # Load hardware model configuration (following CLI pattern)
            from infrastructure.factory import ServiceFactory
            from infrastructure.implementation.configuration.yaml_configuration import (
                YamlConfiguration,
            )

            yaml_config = YamlConfiguration()
            hardware_model = await yaml_config.load_hardware_model()
            hw_model_dict = hardware_model.to_dict()

            logger.info(f"Loaded hardware model configuration: {hw_model_dict}")

            # Create services based on hardware model configuration
            robot_service = ServiceFactory.create_robot_service({"model": hw_model_dict["robot"]})
            mcu_service = ServiceFactory.create_mcu_service({"model": hw_model_dict["mcu"]})
            loadcell_service = ServiceFactory.create_loadcell_service(
                {"model": hw_model_dict["loadcell"]}
            )
            power_service = ServiceFactory.create_power_service({"model": hw_model_dict["power"]})
            digital_io_service = ServiceFactory.create_digital_io_service(
                {"model": hw_model_dict["digital_io"]}
            )

            self._hardware_service_facade = HardwareServiceFacade(
                robot_service=robot_service,
                mcu_service=mcu_service,
                loadcell_service=loadcell_service,
                power_service=power_service,
                digital_io_service=digital_io_service,
            )

            logger.info("Hardware service facade initialized with model-based configuration")

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

    def configuration_validator(self) -> ConfigurationValidator:
        """Get or create configuration validator"""
        if self._configuration_validator is None:
            logger.info("Initializing configuration validator...")
            self._configuration_validator = ConfigurationValidator()
            logger.info("Configuration validator initialized")
        return self._configuration_validator

    def test_result_evaluator(self) -> TestResultEvaluator:
        """Get or create test result evaluator"""
        if self._test_result_evaluator is None:
            logger.info("Initializing test result evaluator...")
            self._test_result_evaluator = TestResultEvaluator()
            logger.info("Test result evaluator initialized")
        return self._test_result_evaluator

    def repository_service(self) -> RepositoryService:
        """Get or create repository service"""
        if self._repository_service is None:
            logger.info("Initializing repository service...")
            # For now, no specific test repository implementation
            self._repository_service = RepositoryService(test_repository=None)
            logger.info("Repository service initialized")
        return self._repository_service

    def exception_handler(self) -> ExceptionHandler:
        """Get or create exception handler"""
        if self._exception_handler is None:
            logger.info("Initializing exception handler...")
            self._exception_handler = ExceptionHandler()
            logger.info("Exception handler initialized")
        return self._exception_handler

    async def eol_force_test_use_case(self) -> EOLForceTestUseCase:
        """Get or create EOL force test use case"""
        if self._eol_force_test_use_case is None:
            logger.info("Initializing EOL force test use case...")

            hardware_services = await self.hardware_service_facade()
            configuration_service = self.configuration_service()
            configuration_validator = self.configuration_validator()
            test_result_evaluator = self.test_result_evaluator()
            repository_service = self.repository_service()
            exception_handler = self.exception_handler()

            self._eol_force_test_use_case = EOLForceTestUseCase(
                hardware_services=hardware_services,
                configuration_service=configuration_service,
                configuration_validator=configuration_validator,
                test_result_evaluator=test_result_evaluator,
                repository_service=repository_service,
                exception_handler=exception_handler,
            )

            logger.info("EOL force test use case initialized")

        return self._eol_force_test_use_case

    async def robot_home_use_case(self) -> RobotHomeUseCase:
        """Get or create robot home use case with current hardware configuration"""
        # Always create a fresh instance with current configuration
        # This ensures we always use the latest hardware config
        logger.info("Creating robot home use case with current configuration...")

        hardware_services = await self.hardware_service_facade()
        configuration_service = self.configuration_service()

        # Load current hardware configuration
        hardware_config = await configuration_service.load_hardware_config()

        robot_home_use_case = RobotHomeUseCase(
            hardware_services=hardware_services,
            hardware_config=hardware_config,
        )

        logger.info("Robot home use case created")
        return robot_home_use_case

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
