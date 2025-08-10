"""
Pydantic models for configuration management API endpoints
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConfigurationResponse(BaseModel):
    """Response model for configuration data"""
    profile_name: str = Field(..., description="Configuration profile name")
    test_configuration: Dict[str, Any] = Field(..., description="Test configuration parameters")
    hardware_configuration: Dict[str, Any] = Field(..., description="Hardware configuration parameters")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Configuration metadata")


class ConfigurationUpdateRequest(BaseModel):
    """Request model for configuration updates"""
    profile_name: str = Field(..., description="Profile name to update")
    test_configuration: Optional[Dict[str, Any]] = Field(None, description="Test configuration updates")
    hardware_configuration: Optional[Dict[str, Any]] = Field(None, description="Hardware configuration updates")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Configuration metadata")
    create_backup: bool = Field(True, description="Whether to create backup before update")


class ProfileListResponse(BaseModel):
    """Response model for available configuration profiles"""
    profiles: List[str] = Field(..., description="List of available profile names")
    current_profile: str = Field(..., description="Currently active profile")
    total_count: int = Field(..., description="Total number of profiles")


class ProfileUsageResponse(BaseModel):
    """Response model for profile usage information"""
    current_profile: str
    last_used_profile: Optional[str] = None
    usage_history: List[str] = Field(default_factory=list)
    available_profiles: List[str] = Field(default_factory=list)
    history_count: int = 0
    unique_profiles_used: int = 0
    repository_available: bool = False


class ConfigurationValidationResponse(BaseModel):
    """Response model for configuration validation"""
    is_valid: bool
    profile_name: str
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    validated_at: str = Field(..., description="Validation timestamp")


class ConfigurationBackupRequest(BaseModel):
    """Request model for configuration backup"""
    profile_names: Optional[List[str]] = Field(None, description="Specific profiles to backup")
    include_hardware_config: bool = Field(True, description="Include hardware configuration")
    backup_name: Optional[str] = Field(None, description="Custom backup name")


class ConfigurationRestoreRequest(BaseModel):
    """Request model for configuration restore"""
    backup_name: str = Field(..., description="Backup to restore from")
    restore_profiles: Optional[List[str]] = Field(None, description="Specific profiles to restore")
    overwrite_existing: bool = Field(False, description="Overwrite existing profiles")


class ConfigurationBackupResponse(BaseModel):
    """Response model for backup operations"""
    backup_name: str
    backup_path: str
    profiles_backed_up: List[str]
    backup_size_bytes: int
    created_at: str
    success: bool
    error_message: Optional[str] = None


class BackupListResponse(BaseModel):
    """Response model for available backups"""
    backups: List[Dict[str, Any]] = Field(..., description="List of available backups")
    total_count: int


class DUTDefaultsResponse(BaseModel):
    """Response model for DUT default values"""
    serial_number: str
    part_number: str
    defaults: Dict[str, str]
    profile_name: str
    loaded_at: str


# Configuration Editor Models

class TestProfileConfiguration(BaseModel):
    """Model for Test Profile configuration data"""
    hardware: Dict[str, Any] = Field(..., description="Hardware settings")
    motion_control: Dict[str, Any] = Field(..., description="Motion control parameters")
    test_parameters: Dict[str, Any] = Field(..., description="Test parameters")
    timing: Dict[str, Any] = Field(..., description="Timing settings")
    tolerances: Dict[str, Any] = Field(..., description="Tolerance settings")
    execution: Dict[str, Any] = Field(..., description="Execution settings")
    safety: Dict[str, Any] = Field(..., description="Safety limits")
    pass_criteria: Dict[str, Any] = Field(..., description="Pass criteria")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Profile metadata")


class DUTDefaultsConfiguration(BaseModel):
    """Model for DUT Defaults configuration data"""
    active_profile: str = Field(..., description="Active profile name")
    default: Dict[str, str] = Field(..., description="Default DUT values")
    metadata: Optional[Dict[str, Any]] = Field(None, description="DUT defaults metadata")


class HardwareConfigurationModel(BaseModel):
    """Model for Hardware configuration data"""
    hardware_config: Dict[str, Any] = Field(..., description="Hardware configuration sections")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Hardware config metadata")


class HardwareModelConfiguration(BaseModel):
    """Model for Hardware Model configuration data"""
    hardware_model: Dict[str, str] = Field(..., description="Hardware model selections")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Hardware model metadata")


class ConfigurationUpdateResponse(BaseModel):
    """Response model for configuration updates"""
    success: bool
    message: str
    profile_name: str
    config_type: str
    backup_created: bool = False
    backup_path: Optional[str] = None
    updated_at: str
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)


class ConfigurationValidationRequest(BaseModel):
    """Request model for configuration validation"""
    configuration: Dict[str, Any] = Field(..., description="Configuration to validate")
    config_type: str = Field(..., description="Type of configuration (test_profile, dut_defaults, etc.)")
    strict_validation: bool = Field(False, description="Enable strict validation mode")


class ConfigurationHistoryResponse(BaseModel):
    """Response model for configuration change history"""
    profile_name: str
    config_type: str
    history: List[Dict[str, Any]] = Field(..., description="List of configuration changes")
    total_changes: int
