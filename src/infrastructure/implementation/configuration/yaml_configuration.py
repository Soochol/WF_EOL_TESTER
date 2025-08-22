"""
Configuration Implementation

Provides YAML file-based configuration loading/saving and profile preference management.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from loguru import logger

from domain.value_objects.hardware_config import HardwareConfig
from domain.value_objects.test_configuration import TestConfiguration


class YamlConfiguration:
    """Simple YAML-based configuration implementation"""

    def __init__(self, config_dir: str = "configuration"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

    def _format_yaml_with_spacing(self, yaml_content: str) -> str:
        """
        Add blank lines before major sections for better readability
        
        Args:
            yaml_content: Raw YAML content string
            
        Returns:
            Formatted YAML content with spacing
        """
        # Define major section keywords that should have blank lines before them
        section_keywords = [
            'services:',
            'logging:', 
            'metadata:',
            'hardware:',
            'motion_control:',
            'timing:',
            'test_parameters:',
            'tolerances:',
            'execution:',
            'safety:',
            'pass_criteria:',
            'digital_io:',
            'available_profiles:',
            'validation:',
            'profile_paths:',
            'power:',
            'loadcell:',
            'mcu:',
            'robot:'
        ]
        
        # Add blank line before each major section (except if it's at the start of file)
        formatted_content = yaml_content
        for keyword in section_keywords:
            # Match the keyword at the start of a line, not preceded by a blank line
            pattern = f'(?<!\\n\\n)^({re.escape(keyword)})'
            replacement = '\\n\\1'
            formatted_content = re.sub(pattern, replacement, formatted_content, flags=re.MULTILINE)
        
        return formatted_content

    async def load_profile(self, profile_name: str) -> TestConfiguration:
        """Load test configuration profile"""
        # Use test_profiles subdirectory for better organization
        profiles_dir = self.config_dir / "test_profiles"
        profile_path = profiles_dir / f"{profile_name}.yaml"

        if not profile_path.exists():
            # Create default test configuration when profile is missing
            from datetime import datetime

            # Create test_profiles directory if it doesn't exist
            profiles_dir.mkdir(exist_ok=True)

            # Create default TestConfiguration with all default values
            default_test_config = TestConfiguration()

            # Convert to structured dictionary format for better readability
            config_data = default_test_config.to_structured_dict()

            # Add metadata
            config_data["metadata"] = {
                "profile_name": profile_name,
                "created_at": datetime.now().isoformat(),
                "note": f"Auto-generated default test profile '{profile_name}'",
                "created_by": "YamlConfiguration (auto-generated)",
            }

            # Save the default profile for future use with formatting
            yaml_content = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
            formatted_content = self._format_yaml_with_spacing(yaml_content)
            
            with open(profile_path, "w", encoding="utf-8") as f:
                f.write(formatted_content)
            
            logger.info(f"Created default test profile: {profile_path}")
            
            # Update profile configuration to include this new profile
            self._update_profile_config_with_new_profile(profile_name)

            return default_test_config

        with open(profile_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return TestConfiguration.from_structured_dict(data)

    async def load_hardware_config(self) -> HardwareConfig:
        """Load unified hardware configuration from application.yaml"""
        app_config_path = self.config_dir / "application.yaml"

        if not app_config_path.exists():
            logger.info("No application.yaml found, creating default hardware configuration")
            return HardwareConfig()  # Default constructor creates all mock hardware

        # Load from application.yaml
        try:
            with open(app_config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Extract hardware section from application.yaml
            hardware_data = data.get("hardware", {})

            if not hardware_data:
                logger.warning("No hardware section found in application.yaml, using defaults")
                return HardwareConfig()

            return HardwareConfig.from_dict(hardware_data)

        except Exception as e:
            logger.error(f"Failed to load hardware configuration from {app_config_path}: {e}")
            logger.info("Using default hardware configuration")
            return HardwareConfig()

    async def list_available_profiles(self) -> List[str]:
        """List available configuration profiles"""
        profiles = []

        # Look in test_profiles subdirectory
        profiles_dir = self.config_dir / "test_profiles"
        if profiles_dir.exists():
            for yaml_file in profiles_dir.glob("*.yaml"):
                profiles.append(yaml_file.stem)

        return sorted(profiles)

    async def load_dut_defaults(self, profile_name: Optional[str] = None) -> Dict[str, str]:
        """Load DUT default values"""
        dut_path = self.config_dir / "dut_defaults.yaml"

        if not dut_path.exists():
            # Create default DUT configuration when file is missing
            from datetime import datetime

            default_config = {
                "active_profile": "default",
                "default": {
                    "dut_id": "DEFAULT001",
                    "model": "Default Model",
                    "operator_id": "DEFAULT_OP",
                    "manufacturer": "Default Manufacturer",
                    "serial_number": "SN001",
                    "part_number": "PN001",
                },
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "note": "Auto-generated default configuration",
                    "created_by": "YamlConfiguration (auto-generated)",
                },
            }

            # Save the default configuration for future use with formatting
            yaml_content = yaml.dump(default_config, default_flow_style=False, sort_keys=False)
            formatted_content = self._format_yaml_with_spacing(yaml_content)
            
            with open(dut_path, "w", encoding="utf-8") as f:
                f.write(formatted_content)

            # Return the appropriate profile
            if profile_name and profile_name in default_config:
                return default_config[profile_name]
            return default_config.get("default", default_config)

        with open(dut_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # If profile_name is specified, try to get profile-specific defaults
        if profile_name and profile_name in data:
            return data[profile_name]

        # Otherwise return the default section or the whole data
        return data.get("default", data)

    async def save_profile(self, profile_name: str, test_config: TestConfiguration) -> None:
        """Save test configuration profile"""
        # Use test_profiles subdirectory for consistency
        profiles_dir = self.config_dir / "test_profiles"
        profiles_dir.mkdir(exist_ok=True)
        profile_path = profiles_dir / f"{profile_name}.yaml"

        # Convert TestConfiguration to structured dictionary for better readability
        config_data = test_config.to_structured_dict()

        # Save with formatting
        yaml_content = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
        formatted_content = self._format_yaml_with_spacing(yaml_content)
        
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)

        logger.info(f"Saved test profile: {profile_path}")

    async def save_hardware_config(self, hardware_config: HardwareConfig) -> None:
        """Save unified hardware configuration to application.yaml"""
        app_config_path = self.config_dir / "application.yaml"

        # Load existing application.yaml
        if app_config_path.exists():
            with open(app_config_path, "r", encoding="utf-8") as f:
                app_data = yaml.safe_load(f) or {}
        else:
            app_data = {}

        # Update hardware section with unified configuration
        app_data["hardware"] = hardware_config.to_dict()

        # Save updated application.yaml with formatting
        yaml_content = yaml.dump(app_data, default_flow_style=False, sort_keys=False)
        formatted_content = self._format_yaml_with_spacing(yaml_content)
        
        with open(app_config_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)

        logger.info(f"Saved hardware configuration to: {app_config_path}")

    async def save_dut_defaults(
        self, dut_defaults_data: Dict[str, Any], profile_name: str = "default"
    ) -> None:
        """Save DUT defaults configuration"""
        dut_path = self.config_dir / "dut_defaults.yaml"

        # Load existing data if file exists
        existing_data = {}
        if dut_path.exists():
            with open(dut_path, "r", encoding="utf-8") as f:
                existing_data = yaml.safe_load(f) or {}

        # Update with new data for the specified profile
        existing_data[profile_name] = dut_defaults_data

        # Save with formatting
        yaml_content = yaml.dump(existing_data, default_flow_style=False, sort_keys=False)
        formatted_content = self._format_yaml_with_spacing(yaml_content)
        
        with open(dut_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)

        logger.info(f"Saved DUT defaults for profile '{profile_name}': {dut_path}")

    # ============================================================================
    # PROFILE PREFERENCE METHODS (YAML-based)
    # ============================================================================

    def _ensure_profile_config(self) -> None:
        """Ensure profile configuration file exists with default settings"""
        profile_config_path = self.config_dir / "profile.yaml"
        
        if not profile_config_path.exists():
            logger.info("Creating default profile configuration file")
            
            # Check available profiles in test_profiles directory
            profiles_dir = self.config_dir / "test_profiles"
            available_profiles = []
            
            if profiles_dir.exists():
                available_profiles = [f.stem for f in profiles_dir.glob("*.yaml")]
            
            # If no profiles exist, ensure "default" is in the list
            if not available_profiles:
                available_profiles = ["default"]
            
            # Create default profile configuration
            profile_config = {
                "active_profile": "default",
                "available_profiles": available_profiles,
                "profile_paths": ["test_profiles"],
                "validation": {
                    "strict_mode": True,
                    "fallback_profile": "default"
                },
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_by": "YamlConfiguration (auto-generated)",
                    "description": "Profile management configuration for EOL test system"
                }
            }
            
            # Save profile configuration with formatting
            yaml_content = yaml.dump(profile_config, default_flow_style=False, sort_keys=False)
            formatted_content = self._format_yaml_with_spacing(yaml_content)
            
            with open(profile_config_path, "w", encoding="utf-8") as f:
                f.write(formatted_content)
            
            logger.info(f"Created profile configuration: {profile_config_path}")

    def _update_profile_config_with_new_profile(self, profile_name: str) -> None:
        """Update profile configuration when a new profile is created"""
        profile_config_path = self.config_dir / "profile.yaml"
        
        try:
            # Ensure profile config exists
            self._ensure_profile_config()
            
            # Load current config
            with open(profile_config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
            
            # Update available profiles list
            available_profiles = config_data.get("available_profiles", [])
            if profile_name not in available_profiles:
                available_profiles.append(profile_name)
                config_data["available_profiles"] = sorted(available_profiles)
                
                # Update metadata
                config_data["metadata"]["last_updated"] = datetime.now().isoformat()
                config_data["metadata"]["updated_by"] = "YamlConfiguration (profile added)"
                
                # Save updated config with formatting
                yaml_content = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
                formatted_content = self._format_yaml_with_spacing(yaml_content)
                
                with open(profile_config_path, "w", encoding="utf-8") as f:
                    f.write(formatted_content)
                
                logger.debug(f"Added profile '{profile_name}' to profile configuration")
                
        except Exception as e:
            logger.warning(f"Failed to update profile configuration with new profile '{profile_name}': {e}")

    async def load_last_used_profile(self) -> Optional[str]:
        """Load the last used profile name from profile configuration and preferences"""
        # Ensure profile configuration file exists
        self._ensure_profile_config()
        
        # First try to load from profile_preferences.yaml (last used)
        preference_path = self.config_dir / "profile_preferences.yaml"
        try:
            if preference_path.exists():
                with open(preference_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                last_used = data.get("last_used_profile")
                if last_used:
                    return last_used
        except Exception as e:
            logger.warning(f"Failed to load from profile preferences: {e}")
        
        # Fallback to active_profile from profile.yaml
        profile_config_path = self.config_dir / "profile.yaml"
        try:
            if profile_config_path.exists():
                with open(profile_config_path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
                active_profile = config_data.get("active_profile", "default")
                logger.debug(f"Using active profile from profile.yaml: {active_profile}")
                return active_profile
        except Exception as e:
            logger.warning(f"Failed to load from profile config: {e}")
        
        # Ultimate fallback
        return "default"

    async def save_last_used_profile(self, profile_name: str) -> None:
        """Save the last used profile name to YAML preference file"""
        preference_path = self.config_dir / "profile_preferences.yaml"

        try:
            # Load existing preferences
            data = {}
            if preference_path.exists():
                with open(preference_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

            # Update last used profile and timestamp
            data["last_used_profile"] = profile_name
            data["last_used_timestamp"] = datetime.now().isoformat()

            # Save preferences
            with open(preference_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            logger.debug(f"Saved last used profile: {profile_name}")

        except Exception as e:
            logger.warning(f"Failed to save last used profile: {e}")

    async def clear_preferences(self) -> None:
        """Clear all profile preferences"""
        preference_path = self.config_dir / "profile_preferences.yaml"

        try:
            if preference_path.exists():
                preference_path.unlink()
            logger.info("Profile preferences cleared")
        except Exception as e:
            logger.warning(f"Failed to clear preferences: {e}")
