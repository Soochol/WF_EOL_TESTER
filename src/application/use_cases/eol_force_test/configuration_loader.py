"""
Test Configuration Loader

Handles loading and validation of all configurations required for EOL test execution.
Extracted from EOLForceTestUseCase for better separation of concerns.
"""

from typing import Optional

from loguru import logger

from application.services.core.configuration_service import ConfigurationService
from application.services.core.configuration_validator import ConfigurationValidator
from domain.exceptions import MultiConfigurationValidationError
from domain.exceptions.test_exceptions import TestExecutionException
from domain.value_objects.hardware_config import HardwareConfig
from domain.value_objects.test_configuration import TestConfiguration

from .constants import TestExecutionConstants


class TestConfigurationLoader:
    """Handles configuration loading and validation for EOL tests"""

    def __init__(
        self,
        configuration_service: ConfigurationService,
        configuration_validator: ConfigurationValidator,
    ):
        self._configuration_service = configuration_service
        self._configuration_validator = configuration_validator

        # Configuration state
        self._profile_name: Optional[str] = None
        self._test_config: Optional[TestConfiguration] = None
        self._hardware_config: Optional[HardwareConfig] = None

    @property
    def profile_name(self) -> Optional[str]:
        """Get loaded profile name"""
        return self._profile_name

    @property
    def test_config(self) -> Optional[TestConfiguration]:
        """Get loaded test configuration"""
        return self._test_config

    @property
    def hardware_config(self) -> Optional[HardwareConfig]:
        """Get loaded hardware configuration"""
        return self._hardware_config

    async def load_and_validate_configurations(self) -> None:
        """
        Load and validate all configurations for test execution

        This method handles the complete configuration loading workflow:
        1. Load active profile name
        2. Load test configuration
        3. Load hardware configuration
        4. Validate configurations
        5. Mark profile as used

        Raises:
            TestExecutionException: If configuration loading or validation fails
        """
        # Load profile name
        self._profile_name = await self._configuration_service.get_active_profile_name()

        # Load test configuration
        self._test_config = await self._configuration_service.load_test_config(self._profile_name)

        # Load hardware configuration
        self._hardware_config = await self._configuration_service.load_hardware_config()
        logger.info(TestExecutionConstants.LOG_CONFIG_LOAD_SUCCESS)

        # Validate configuration
        try:
            await self._configuration_validator.validate_test_configuration(self._test_config)
            logger.info(TestExecutionConstants.LOG_CONFIG_VALIDATION_SUCCESS)
        except MultiConfigurationValidationError as e:
            logger.error("Configuration validation failed: {}", e.message)
            raise TestExecutionException(
                f"Configuration validation failed: {e.get_context('total_errors')} errors found"
            ) from e

        # Mark profile as used (non-critical operation - don't fail test on error)
        try:
            # Profile usage tracking removed - no longer needed
            logger.debug("Profile '{}' loaded successfully", self._profile_name)
        except Exception as pref_error:
            # Profile usage tracking failure should not interrupt test execution
            logger.warning(
                "Failed to mark profile '{}' as used: {}", self._profile_name, pref_error
            )
