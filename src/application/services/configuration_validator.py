"""
Configuration Validator Service

Business service for validating test and hardware configurations.
Uses Exception First principles for error handling.
"""

from typing import Any, Dict

from loguru import logger

from domain.exceptions import (
    ConfigurationValidationError,
    MultiConfigurationValidationError,
    create_multi_validation_error,
    create_validation_error,
)
from domain.exceptions.validation_exceptions import ValidationException
from domain.value_objects.test_configuration import TestConfiguration


class ConfigurationValidator:
    """
    Service responsible for validating configurations

    This service encapsulates all configuration validation logic
    to ensure consistency and reliability across the system.
    """

    def __init__(self):
        """Initialize the configuration validator"""
        pass

    async def validate_test_configuration(self, config: TestConfiguration) -> None:
        """
        Validate test configuration

        Args:
            config: TestConfiguration to validate

        Raises:
            ConfigurationValidationError: If validation fails
        """
        errors = []

        try:
            # Use the built-in validation
            config.__post_init__()
            logger.debug("Test configuration validation passed")

        except ValidationException as e:
            error_msg = f"Test configuration validation failed: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error during test configuration validation: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

        if errors:
            raise create_validation_error(errors, "test_configuration")

    async def validate_all_configurations(self, test_config: TestConfiguration) -> None:
        """
        Validate test configuration

        Args:
            test_config: TestConfiguration to validate

        Raises:
            MultiConfigurationValidationError: If any validation fails
        """
        logger.info("Starting comprehensive configuration validation")

        errors_by_type = {}

        # Validate test configuration
        try:
            await self.validate_test_configuration(test_config)
        except ConfigurationValidationError as e:
            errors_by_type["test_configuration"] = e.errors

        # Hardware configuration validation removed - no longer needed
        # Cross-configuration compatibility validation removed - no longer needed

        if errors_by_type:
            total_errors = sum(len(errors) for errors in errors_by_type.values())
            logger.warning(f"❌ Configuration validation failed with {total_errors} errors")
            raise create_multi_validation_error(errors_by_type)
        else:
            logger.info("✅ All configuration validations passed")

    async def validate_configuration_compatibility(self, test_config: TestConfiguration) -> None:
        """
        Validate test configuration compatibility and internal consistency

        Args:
            test_config: TestConfiguration to check

        Raises:
            ConfigurationValidationError: If compatibility validation fails
        """
        errors = []

        try:
            # Check robot stroke compatibility
            max_test_stroke = max(test_config.stroke_positions) if test_config.stroke_positions else 0
            if max_test_stroke > test_config.max_stroke:
                errors.append(f"Test stroke positions exceed max_stroke limit: {max_test_stroke} > {test_config.max_stroke}")

            # Check temperature compatibility
            max_test_temp = max(test_config.temperature_list) if test_config.temperature_list else 0
            if max_test_temp > test_config.upper_temperature:
                errors.append(
                    f"Test temperatures exceed upper_temperature limit: {max_test_temp} > {test_config.upper_temperature}"
                )

            # Check safety limits compatibility - removed max_temperature check as it's no longer in TestConfiguration

            if errors:
                logger.warning(f"Configuration compatibility validation failed with {len(errors)} errors")
                raise create_validation_error(errors, "compatibility")
            else:
                logger.debug("Configuration compatibility validation passed")

        except ConfigurationValidationError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during compatibility validation: {e}"
            logger.error(error_msg)
            raise create_validation_error([error_msg], "compatibility")

    async def get_configuration_summary(self, test_config: TestConfiguration) -> Dict[str, Any]:
        """
        Generate a summary of test configuration settings for logging/debugging

        Args:
            test_config: TestConfiguration to summarize

        Returns:
            Dictionary containing configuration summary
        """
        try:
            summary = {
                "test_configuration": {
                    "measurement_points": test_config.get_total_measurement_points(),
                    "estimated_duration_seconds": test_config.estimate_test_duration_seconds(),
                    "temperature_count": test_config.get_temperature_count(),
                    "position_count": test_config.get_position_count(),
                    "temperature_range": (
                        [min(test_config.temperature_list), max(test_config.temperature_list)]
                        if test_config.temperature_list
                        else [0, 0]
                    ),
                    "stroke_range": (
                        [min(test_config.stroke_positions), max(test_config.stroke_positions)]
                        if test_config.stroke_positions
                        else [0, 0]
                    ),
                    "safety_limits": {
                        "max_temperature": test_config.max_temperature,
                        "max_force": test_config.max_force,
                        "max_voltage": test_config.max_voltage,
                        "max_current": test_config.max_current,
                    },
                }
            }

            logger.debug("Configuration summary generated successfully")
            return summary

        except Exception as e:
            error_msg = f"Failed to generate configuration summary: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
