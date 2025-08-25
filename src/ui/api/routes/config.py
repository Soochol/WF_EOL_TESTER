"""
Configuration management API routes

Provides REST endpoints for configuration and profile management.
"""

from datetime import datetime
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, Request, status
from loguru import logger

from application.containers.application_container import ApplicationContainer
from application.services.configuration_service import ConfigurationService
from ui.api.models.config_models import (
    ConfigurationResponse,
    ConfigurationUpdateRequest,
    ConfigurationUpdateResponse,
    ConfigurationValidationRequest,
    ConfigurationValidationResponse,
    DUTDefaultsConfiguration,
    DUTDefaultsResponse,
    HardwareConfigurationModel,
    HardwareModelConfiguration,
    ProfileListResponse,
    ProfileUsageResponse,
)

router = APIRouter()


@router.get("/profiles", response_model=ProfileListResponse)
async def list_profiles(request: Request):
    """List all available configuration profiles"""
    try:
        config_service = request.app.state.container.configuration_service()

        available_profiles = await config_service.list_available_profiles()
        current_profile = await config_service.get_active_profile_name()

        return ProfileListResponse(
            profiles=available_profiles,
            current_profile=current_profile,
            total_count=len(available_profiles),
        )

    except Exception as e:
        logger.error(f"Failed to list profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list profiles: {str(e)}",
        ) from e


@router.get("/current")
async def get_current_configuration(request: Request):
    """Get current active test configuration with motion parameters"""
    try:
        config_service = request.app.state.container.configuration_service()
        # Get current active profile name
        profile_name = await config_service.get_active_profile_name()
        # Load current test configuration
        test_config = await config_service.load_test_config(profile_name)
        # Return motion parameters for UI
        return {
            "profile_name": profile_name,
            "velocity": test_config.velocity,
            "acceleration": test_config.acceleration,
            "deceleration": test_config.deceleration,
            "max_velocity": test_config.max_velocity,
            "max_acceleration": test_config.max_acceleration,
            "max_deceleration": test_config.max_deceleration,
        }
    except Exception as e:
        logger.error(f"Failed to get current configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current configuration: {str(e)}",
        ) from e


@router.get("/profiles/usage", response_model=ProfileUsageResponse)
@inject
async def get_profile_usage(
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Get profile usage information"""
    try:
        profile_info = await config_service.get_profile_info()

        return ProfileUsageResponse(**profile_info)

    except Exception as e:
        logger.error(f"Failed to get profile usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile usage: {str(e)}",
        ) from e


@router.get("/profiles/{profile_name}", response_model=ConfigurationResponse)
@inject
async def get_profile_configuration(
    profile_name: str,
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Get configuration for a specific profile"""
    try:

        # Load test configuration
        test_config = await config_service.load_test_config(profile_name)

        # Load hardware configuration
        hardware_config = await config_service.load_hardware_config()

        # Mark profile as used
        # Profile usage tracking removed - no longer needed

        return ConfigurationResponse(
            profile_name=profile_name,
            test_configuration=test_config.to_dict(),
            hardware_configuration=hardware_config.to_dict(),
            metadata={
                "loaded_at": datetime.now().isoformat(),
                "test_duration_estimate_seconds": test_config.estimate_test_duration_seconds(),
                "total_measurements": test_config.get_total_measurement_points(),
            },
        )

    except Exception as e:
        logger.error(f"Failed to get profile configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration: {str(e)}",
        ) from e


@router.get("/profiles/{profile_name}/validate", response_model=ConfigurationValidationResponse)
@inject
async def validate_profile_configuration(
    profile_name: str,
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Validate a configuration profile"""
    try:

        validation_errors = []
        validation_warnings = []
        is_valid = True

        try:
            # Load and validate test configuration
            test_config = await config_service.load_test_config(profile_name)

            # The TestConfiguration.__post_init__ will validate the configuration
            if not test_config.is_valid():
                is_valid = False
                validation_errors.append("Test configuration validation failed")

        except Exception as test_error:
            is_valid = False
            validation_errors.append(f"Test configuration error: {str(test_error)}")

        try:
            # Load and validate hardware configuration
            hardware_config = await config_service.load_hardware_config()

            if not hardware_config.is_valid():
                is_valid = False
                validation_errors.append("Hardware configuration validation failed")

        except Exception as hw_error:
            is_valid = False
            validation_errors.append(f"Hardware configuration error: {str(hw_error)}")

        # Add some additional validation warnings
        if is_valid:
            test_config = await config_service.load_test_config(profile_name)

            # Check for potentially long test durations
            estimated_duration = test_config.estimate_test_duration_seconds()
            if estimated_duration > 1800:  # 30 minutes
                validation_warnings.append(
                    f"Test duration estimated at {estimated_duration/60:.1f} minutes - consider reducing measurement points"
                )

            # Check temperature range
            if test_config.temperature_list:
                temp_range = max(test_config.temperature_list) - min(test_config.temperature_list)
                if temp_range > 30:
                    validation_warnings.append(
                        f"Large temperature range ({temp_range}°C) may require longer stabilization times"
                    )

        return ConfigurationValidationResponse(
            is_valid=is_valid,
            profile_name=profile_name,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings,
            validated_at=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to validate profile configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate configuration: {str(e)}",
        ) from e


@router.get("/hardware", response_model=dict)
@inject
async def get_hardware_configuration(
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Get hardware configuration"""
    try:
        hardware_config = await config_service.load_hardware_config()

        return {
            "hardware_configuration": hardware_config.to_dict(),
            "metadata": {"loaded_at": datetime.now().isoformat()},
        }

    except Exception as e:
        logger.error(f"Failed to get hardware configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hardware configuration: {str(e)}",
        ) from e


@router.get("/dut-defaults", response_model=DUTDefaultsResponse)
@inject
async def get_dut_defaults(
    profile_name: Optional[str] = None,
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Get DUT default values"""
    try:

        # Use provided profile or get active profile
        if not profile_name:
            profile_name = await config_service.get_active_profile_name()

        # Load DUT defaults
        dut_defaults = await config_service.load_dut_defaults(profile_name)

        return DUTDefaultsResponse(
            serial_number=dut_defaults.get("serial_number", "WF-EOL-001"),
            part_number=dut_defaults.get("part_number", "WF-PART-001"),
            defaults=dut_defaults,
            profile_name=profile_name,
            loaded_at=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to get DUT defaults: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get DUT defaults: {str(e)}",
        ) from e


@router.post("/profiles/clear-preferences")
@inject
async def clear_profile_preferences(
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Clear all profile preferences"""
    try:
        await config_service.clear_profile_preferences()

        logger.info("Profile preferences cleared")
        return {
            "message": "Profile preferences cleared successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to clear profile preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear preferences: {str(e)}",
        ) from e


@router.put("/profiles/{profile_name}")
@inject
async def update_profile_configuration(
    profile_name: str,
    request: ConfigurationUpdateRequest,
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Update test profile configuration"""
    try:

        # Validate configuration data if provided
        validation_errors = []
        validation_warnings = []
        backup_created = False
        backup_path = None

        if request.test_configuration:
            try:
                # Create backup if requested
                if request.create_backup:
                    import shutil
                    from pathlib import Path

                    source_file = Path(f"configuration/test_profiles/{profile_name}.yaml")
                    if source_file.exists():
                        backup_path = f"configuration/test_profiles/backup_{profile_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                        shutil.copy2(source_file, backup_path)
                        backup_created = True
                        logger.info(f"Created backup: {backup_path}")

                # Save the updated configuration
                await config_service.save_test_profile(profile_name, request.test_configuration)

                return ConfigurationUpdateResponse(
                    success=True,
                    message=f"Test profile '{profile_name}' updated successfully",
                    profile_name=profile_name,
                    config_type="test_profile",
                    backup_created=backup_created,
                    backup_path=backup_path,
                    updated_at=datetime.now().isoformat(),
                    validation_errors=validation_errors,
                    validation_warnings=validation_warnings,
                )

            except Exception as save_error:
                validation_errors.append(f"Failed to save configuration: {str(save_error)}")
                return ConfigurationUpdateResponse(
                    success=False,
                    message=f"Failed to update profile '{profile_name}': {str(save_error)}",
                    profile_name=profile_name,
                    config_type="test_profile",
                    backup_created=backup_created,
                    backup_path=backup_path,
                    updated_at=datetime.now().isoformat(),
                    validation_errors=validation_errors,
                    validation_warnings=validation_warnings,
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No test configuration data provided",
            )

    except Exception as e:
        logger.error(f"Failed to update profile configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update configuration: {str(e)}",
        ) from e


@router.post("/backup")
async def backup_configurations():
    """Backup all configurations (placeholder)"""
    # This would require implementation of configuration backup
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Configuration backup not yet implemented",
    )


@router.post("/restore")
async def restore_configurations():
    """Restore configurations from backup (placeholder)"""
    # This would require implementation of configuration restore
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Configuration restore not yet implemented",
    )


# Hardware Configuration Endpoints


@router.get("/hardware-config", response_model=HardwareConfigurationModel)
@inject
async def get_hardware_config(
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Get hardware configuration"""
    try:
        hardware_config = await config_service.load_hardware_config()

        return HardwareConfigurationModel(
            hardware_config=hardware_config.to_dict(),
            metadata={"loaded_at": datetime.now().isoformat()},
        )

    except Exception as e:
        logger.error(f"Failed to get hardware configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hardware configuration: {str(e)}",
        ) from e


@router.put("/hardware-config")
@inject
async def update_hardware_config(
    config: HardwareConfigurationModel,
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Update hardware configuration"""
    try:

        # Save the updated configuration
        await config_service.save_hardware_config(config.hardware_config)

        return ConfigurationUpdateResponse(
            success=True,
            message="Hardware configuration updated successfully",
            profile_name="hardware_configuration",
            config_type="hardware_config",
            backup_created=True,  # Automatic backup is created
            updated_at=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to update hardware configuration: {e}")
        return ConfigurationUpdateResponse(
            success=False,
            message=f"Failed to update hardware configuration: {str(e)}",
            profile_name="hardware_configuration",
            config_type="hardware_config",
            updated_at=datetime.now().isoformat(),
            validation_errors=[str(e)],
        )


# Hardware Model Endpoints


@router.get("/hardware-model", response_model=HardwareModelConfiguration)
@inject
async def get_hardware_model(
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Get hardware model configuration"""
    try:
        # Load hardware model from the YAML configuration
        hardware_model = await config_service.load_hardware_config()

        return HardwareModelConfiguration(
            hardware_model=hardware_model.to_dict(),
            metadata={"loaded_at": datetime.now().isoformat()},
        )

    except Exception as e:
        logger.error(f"Failed to get hardware model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hardware model: {str(e)}",
        ) from e


@router.put("/hardware-model")
@inject
async def update_hardware_model(
    config: HardwareModelConfiguration,
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Update hardware model configuration"""
    try:

        # Save the updated configuration
        await config_service.save_hardware_config(config.hardware_model)

        return ConfigurationUpdateResponse(
            success=True,
            message="Hardware model configuration updated successfully",
            profile_name="hardware_model",
            config_type="hardware_model",
            backup_created=True,  # Automatic backup is created
            updated_at=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to update hardware model: {e}")
        return ConfigurationUpdateResponse(
            success=False,
            message=f"Failed to update hardware model: {str(e)}",
            profile_name="hardware_model",
            config_type="hardware_model",
            updated_at=datetime.now().isoformat(),
            validation_errors=[str(e)],
        )


# DUT Defaults Endpoints


@router.get("/dut-defaults-config", response_model=DUTDefaultsConfiguration)
async def get_dut_defaults_config():
    """Get DUT defaults configuration"""
    try:
        # Load the full DUT defaults file structure
        from pathlib import Path

        import yaml

        dut_defaults_path = Path("configuration") / "dut_defaults.yaml"
        if dut_defaults_path.exists():
            with open(dut_defaults_path, "r", encoding="utf-8") as file:
                dut_config = yaml.safe_load(file)

            return DUTDefaultsConfiguration(
                active_profile=dut_config.get("active_profile", "default"),
                default=dut_config.get("default", {}),
                metadata=dut_config.get("metadata", {"loaded_at": datetime.now().isoformat()}),
            )
        else:
            # Return default structure
            return DUTDefaultsConfiguration(
                active_profile="default",
                default={
                    "dut_id": "DEFAULT001",
                    "model": "Default Model",
                    "operator_id": "DEFAULT_OP",
                    "manufacturer": "Default Manufacturer",
                },
                metadata={
                    "loaded_at": datetime.now().isoformat(),
                    "note": "Default configuration - file not found",
                },
            )

    except Exception as e:
        logger.error(f"Failed to get DUT defaults configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get DUT defaults configuration: {str(e)}",
        ) from e


@router.put("/dut-defaults-config")
@inject
async def update_dut_defaults_config(
    config: DUTDefaultsConfiguration,
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Update DUT defaults configuration"""
    try:

        # Prepare data for saving
        dut_data = {"active_profile": config.active_profile, "default": config.default}

        # Save the updated configuration
        await config_service.save_dut_defaults_configuration(dut_data)

        return ConfigurationUpdateResponse(
            success=True,
            message="DUT defaults configuration updated successfully",
            profile_name="dut_defaults",
            config_type="dut_defaults",
            backup_created=True,  # Automatic backup is created
            updated_at=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to update DUT defaults configuration: {e}")
        return ConfigurationUpdateResponse(
            success=False,
            message=f"Failed to update DUT defaults configuration: {str(e)}",
            profile_name="dut_defaults",
            config_type="dut_defaults",
            updated_at=datetime.now().isoformat(),
            validation_errors=[str(e)],
        )


# Configuration Validation Endpoint


@router.post("/validate")
async def validate_configuration(request: ConfigurationValidationRequest):
    """Validate a configuration"""
    try:
        validation_errors = []
        validation_warnings = []
        is_valid = True

        # Validate based on configuration type
        if request.config_type == "test_profile":
            try:
                from domain.value_objects.test_configuration import TestConfiguration

                test_config = TestConfiguration.from_structured_dict(request.configuration)

                # Basic validation - TestConfiguration will validate itself
                if not test_config.is_valid():
                    is_valid = False
                    validation_errors.append("Test configuration validation failed")

            except Exception as e:
                is_valid = False
                validation_errors.append(f"Test configuration error: {str(e)}")

        elif request.config_type == "hardware_config":
            try:
                from domain.value_objects.hardware_config import HardwareConfig

                hardware_config = HardwareConfig.from_dict(request.configuration)

                if not hardware_config.is_valid():
                    is_valid = False
                    validation_errors.append("Hardware configuration validation failed")

            except Exception as e:
                is_valid = False
                validation_errors.append(f"Hardware configuration error: {str(e)}")

        elif request.config_type == "hardware_model":
            try:
                from domain.value_objects.hardware_config import HardwareConfig

                # Validate that hardware config can be created from configuration
                HardwareConfig.from_dict(request.configuration)
                # Hardware model doesn't have complex validation currently

            except Exception as e:
                is_valid = False
                validation_errors.append(f"Hardware model error: {str(e)}")

        elif request.config_type == "dut_defaults":
            # Basic DUT defaults validation
            required_fields = ["dut_id", "model", "operator_id", "manufacturer"]
            default_section = request.configuration.get("default", {})

            for field in required_fields:
                if field not in default_section or not default_section[field]:
                    validation_warnings.append(f"Missing or empty required field: {field}")

        else:
            validation_errors.append(f"Unknown configuration type: {request.config_type}")
            is_valid = False

        return ConfigurationValidationResponse(
            is_valid=is_valid,
            profile_name=request.config_type,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings,
            validated_at=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to validate configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate configuration: {str(e)}",
        ) from e
