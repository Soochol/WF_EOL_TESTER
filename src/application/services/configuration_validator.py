"""
Configuration Validator Service

Business service for validating test and hardware configurations.
"""

from typing import List, Dict, Any, Tuple
from loguru import logger

from domain.value_objects.test_configuration import TestConfiguration
from domain.value_objects.hardware_configuration import HardwareConfiguration
from domain.exceptions.validation_exceptions import ValidationException


class ConfigurationValidator:
    """
    Service responsible for validating configurations

    This service encapsulates all configuration validation logic
    to ensure consistency and reliability across the system.
    """

    def __init__(self):
        """Initialize the configuration validator"""
        pass

    async def validate_test_configuration(self, config: TestConfiguration) -> Tuple[bool, List[str]]:
        """
        Validate test configuration

        Args:
            config: TestConfiguration to validate

        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        errors = []

        try:
            # Use the built-in validation
            config.__post_init__()
            logger.debug("Test configuration validation passed")
            return True, []

        except ValidationException as e:
            error_msg = f"Test configuration validation failed: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            return False, errors

        except Exception as e:
            error_msg = f"Unexpected error during test configuration validation: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            return False, errors

    async def validate_hardware_configuration(self, config: HardwareConfiguration) -> Tuple[bool, List[str]]:
        """
        Validate hardware configuration

        Args:
            config: HardwareConfiguration to validate

        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        errors = []

        try:
            # Use the built-in validation
            config.__post_init__()
            logger.debug("Hardware configuration validation passed")
            return True, []

        except ValidationException as e:
            error_msg = f"Hardware configuration validation failed: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            return False, errors

        except Exception as e:
            error_msg = f"Unexpected error during hardware configuration validation: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            return False, errors

    async def validate_all_configurations(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate both test and hardware configurations

        Args:
            test_config: TestConfiguration to validate
            hardware_config: HardwareConfiguration to validate

        Returns:
            Tuple of (all_valid: bool, errors_by_type: Dict[str, List[str]])
        """
        logger.info("Starting comprehensive configuration validation")

        # Validate test configuration
        test_valid, test_errors = await self.validate_test_configuration(test_config)

        # Validate hardware configuration
        hardware_valid, hardware_errors = await self.validate_hardware_configuration(hardware_config)

        # Check cross-configuration compatibility
        compatibility_valid, compatibility_errors = await self.validate_configuration_compatibility(
            test_config, hardware_config
        )

        all_valid = test_valid and hardware_valid and compatibility_valid

        errors_by_type = {
            'test_configuration': test_errors,
            'hardware_configuration': hardware_errors,
            'compatibility': compatibility_errors
        }

        if all_valid:
            logger.info("✅ All configuration validations passed")
        else:
            total_errors = sum(len(errs) for errs in errors_by_type.values())
            logger.warning(f"❌ Configuration validation failed with {total_errors} errors")

        return all_valid, errors_by_type

    async def validate_configuration_compatibility(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration
    ) -> Tuple[bool, List[str]]:
        """
        Validate compatibility between test and hardware configurations

        Args:
            test_config: TestConfiguration to check
            hardware_config: HardwareConfiguration to check

        Returns:
            Tuple of (is_compatible: bool, errors: List[str])
        """
        errors = []

        try:
            # Check robot stroke compatibility
            max_test_stroke = max(test_config.stroke_positions) if test_config.stroke_positions else 0
            if max_test_stroke > test_config.max_stroke:
                errors.append(f"Test stroke positions exceed max_stroke limit: {max_test_stroke} > {test_config.max_stroke}")

            # Check robot axis compatibility (must be 0 or 1)
            if hardware_config.robot.axis not in [0, 1]:
                errors.append(f"Invalid robot axis configuration: {hardware_config.robot.axis} (must be 0 or 1)")

            # Check temperature compatibility
            max_test_temp = max(test_config.temperature_list) if test_config.temperature_list else 0
            if max_test_temp > test_config.upper_temperature:
                errors.append(f"Test temperatures exceed upper_temperature limit: {max_test_temp} > {test_config.upper_temperature}")

            # Check safety limits compatibility
            if test_config.upper_temperature >= test_config.max_temperature:
                errors.append(f"Upper temperature {test_config.upper_temperature} should be less than max temperature {test_config.max_temperature}")

            # Check robot velocity compatibility
            if hardware_config.robot.velocity > hardware_config.robot.max_velocity:
                errors.append(f"Robot velocity {hardware_config.robot.velocity} exceeds max velocity {hardware_config.robot.max_velocity}")

            # Check robot acceleration compatibility
            if hardware_config.robot.acceleration > hardware_config.robot.max_acceleration:
                errors.append(f"Robot acceleration {hardware_config.robot.acceleration} exceeds max acceleration {hardware_config.robot.max_acceleration}")

            if len(errors) == 0:
                logger.debug("Configuration compatibility validation passed")
                return True, []
            else:
                logger.warning(f"Configuration compatibility validation failed with {len(errors)} errors")
                return False, errors

        except Exception as e:
            error_msg = f"Unexpected error during compatibility validation: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            return False, errors

    async def get_configuration_summary(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration
    ) -> Dict[str, Any]:
        """
        Generate a summary of configuration settings for logging/debugging

        Args:
            test_config: TestConfiguration to summarize
            hardware_config: HardwareConfiguration to summarize

        Returns:
            Dictionary containing configuration summary
        """
        try:
            summary = {
                'test_configuration': {
                    'measurement_points': test_config.get_total_measurement_points(),
                    'estimated_duration_seconds': test_config.estimate_test_duration_seconds(),
                    'temperature_count': test_config.get_temperature_count(),
                    'position_count': test_config.get_position_count(),
                    'temperature_range': [min(test_config.temperature_list), max(test_config.temperature_list)] if test_config.temperature_list else [0, 0],
                    'stroke_range': [min(test_config.stroke_positions), max(test_config.stroke_positions)] if test_config.stroke_positions else [0, 0],
                    'safety_limits': {
                        'max_temperature': test_config.max_temperature,
                        'max_force': test_config.max_force,
                        'max_voltage': test_config.max_voltage,
                        'max_current': test_config.max_current
                    }
                },
                'hardware_configuration': {
                    'robot': {
                        'axis': hardware_config.robot.axis,
                        'velocity': hardware_config.robot.velocity,
                        'max_velocity': hardware_config.robot.max_velocity,
                        'position_tolerance': hardware_config.robot.position_tolerance
                    },
                    'loadcell': {
                        'port': hardware_config.loadcell.port,
                        'baudrate': hardware_config.loadcell.baudrate
                    },
                    'mcu': {
                        'port': hardware_config.mcu.port,
                        'baudrate': hardware_config.mcu.baudrate
                    },
                    'power': {
                        'host': hardware_config.power.host,
                        'port': hardware_config.power.port
                    }
                }
            }

            logger.debug("Configuration summary generated successfully")
            return summary

        except Exception as e:
            error_msg = f"Failed to generate configuration summary: {e}"
            logger.error(error_msg)
            return {'error': error_msg}
