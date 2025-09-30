"""
YAML Container Configuration Implementation

Provides YAML file-based configuration loading specifically for dependency injection containers.
"""

# Standard library imports
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml

# Third-party imports
from loguru import logger

# Local application imports
from domain.value_objects.application_config import (
    CONFIG_APPLICATION_PATH,
    CONFIG_HARDWARE_PATH,
    CONFIG_PROFILE_PATH,
    CONFIG_TEST_PROFILES_DIR,
    ApplicationConfig,
)
from domain.value_objects.hardware_config import HardwareConfig


class YamlContainerConfigurationLoader:
    """YAML-based configuration loader for dependency injection containers"""

    def __init__(
        self,
        application_config_path: Path = CONFIG_APPLICATION_PATH,
        hardware_config_path: Path = CONFIG_HARDWARE_PATH,
        profile_config_path: Path = CONFIG_PROFILE_PATH,
        test_profiles_dir: Path = CONFIG_TEST_PROFILES_DIR,
    ):
        self.application_config_path = application_config_path
        self.hardware_config_path = hardware_config_path
        self.profile_config_path = profile_config_path
        self.test_profiles_dir = test_profiles_dir

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
            "services:",
            "logging:",
            "metadata:",
            "hardware:",
            "digital_io:",
            "power:",
            "loadcell:",
            "mcu:",
            "robot:",
        ]

        # Add blank line before each major section (except if it's at the start of file)
        formatted_content = yaml_content
        for keyword in section_keywords:
            # Match the keyword at the start of a line, not preceded by a blank line
            pattern = f"(?<!\\n\\n)^({re.escape(keyword)})"
            replacement = "\\n\\1"
            formatted_content = re.sub(pattern, replacement, formatted_content, flags=re.MULTILINE)

        return formatted_content

    def load_all_configurations(self) -> Dict[str, Any]:
        """
        Load all configuration files and return combined configuration dictionary.
        This method provides compatibility with ApplicationContainer initialization.

        Returns:
            Dictionary containing all loaded configurations
        """
        try:
            # Ensure config files exist
            self._ensure_config_files_exist()

            # Load application configuration
            app_config = self._load_application_config_dict()

            # Load hardware configuration
            hardware_config = self._load_hardware_config_dict()

            # Combine configurations
            combined_config = app_config.copy()
            combined_config["hardware"] = hardware_config

            # Load and merge active test profile (overrides hardware settings)
            test_profile_config = self._load_active_test_profile()
            if test_profile_config:
                self._merge_test_profile_into_config(combined_config, test_profile_config)

            logger.info("All configurations loaded successfully")
            return combined_config

        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
            logger.info("Using fallback default configurations")
            return self._get_fallback_configuration()

    def ensure_configurations_exist(self) -> None:
        """Public method to ensure configuration files exist."""
        try:
            self._ensure_config_files_exist()
            logger.info("Configuration files ensured successfully")

        except Exception as e:
            logger.error(f"Failed to ensure configuration files exist: {e}")
            logger.info("Application will continue with in-memory defaults")

    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================

    def _load_application_config_dict(self) -> Dict[str, Any]:
        """Load application configuration from file and return as dictionary."""
        try:
            config_data = self._load_yaml_file(self.application_config_path)
            logger.info(f"Application configuration loaded from: {self.application_config_path}")
            return config_data

        except Exception as e:
            logger.error(f"Failed to load application config: {e}")
            logger.info("Using default application configuration")
            return ApplicationConfig().to_dict()

    def _load_hardware_config_dict(self) -> Dict[str, Any]:
        """Load hardware configuration from file and return as dictionary."""
        try:
            config_data = self._load_yaml_file(self.hardware_config_path)
            logger.info(f"Hardware configuration loaded from: {self.hardware_config_path}")
            return config_data

        except Exception as e:
            logger.error(f"Failed to load hardware config: {e}")
            logger.info("Using default hardware configuration")
            return HardwareConfig().to_dict()

    def _load_active_test_profile(self) -> Dict[str, Any]:
        """
        Load active test profile from profile.yaml and test_profiles directory.

        Returns:
            Dictionary containing test profile configuration, or empty dict if not found
        """
        try:
            # Load profile.yaml to get active profile name
            profile_config_file = Path(self.profile_config_path)
            if not profile_config_file.exists():
                logger.debug(f"Profile config not found: {self.profile_config_path}")
                return {}

            with open(profile_config_file, "r", encoding="utf-8") as f:
                profile_data = yaml.safe_load(f)

            active_profile = profile_data.get("active_profile", "default")

            # Load test profile file
            test_profile_path = Path(self.test_profiles_dir) / f"{active_profile}.yaml"
            if not test_profile_path.exists():
                logger.warning(f"Active test profile not found: {test_profile_path}")
                return {}

            with open(test_profile_path, "r", encoding="utf-8") as f:
                test_profile_config = yaml.safe_load(f)

            logger.info(f"Active test profile '{active_profile}' loaded from: {test_profile_path}")
            return test_profile_config

        except Exception as e:
            logger.warning(f"Failed to load active test profile: {e}")
            return {}

    def _merge_test_profile_into_config(
        self, combined_config: Dict[str, Any], test_profile_config: Dict[str, Any]
    ) -> None:
        """
        Merge test profile configuration into combined config.
        Test profile settings override hardware config settings.

        Args:
            combined_config: Combined configuration to merge into (modified in-place)
            test_profile_config: Test profile configuration to merge
        """
        try:
            # Merge hardware settings from test profile (voltage, current, etc.)
            if "hardware" in test_profile_config:
                if "hardware" not in combined_config:
                    combined_config["hardware"] = {}

                # Override hardware settings with test profile values
                for key, value in test_profile_config["hardware"].items():
                    combined_config["hardware"][key] = value
                    logger.debug(f"Override hardware.{key} = {value} from test profile")

            # Merge other test profile sections (motion_control, timing, etc.)
            for section in [
                "motion_control",
                "timing",
                "test_parameters",
                "safety",
                "execution",
                "tolerances",
                "pass_criteria",
            ]:
                if section in test_profile_config:
                    combined_config[section] = test_profile_config[section]
                    logger.debug(f"Added {section} from test profile")

            logger.info("Test profile settings merged into configuration")

        except Exception as e:
            logger.error(f"Failed to merge test profile: {e}")

    def _ensure_config_files_exist(self) -> None:
        """Ensure configuration files exist, create from domain defaults if missing."""
        try:
            self._ensure_config_from_defaults(self.application_config_path, "application")
            self._ensure_config_from_defaults(self.hardware_config_path, "hardware")
            logger.debug("Configuration files existence verified")

        except Exception as e:
            logger.error(f"Failed to ensure configuration files exist: {e}")
            raise

    def _ensure_config_from_defaults(self, target_path: Path | str, config_type: str) -> None:
        """
        Create configuration file from domain defaults if it doesn't exist.

        Args:
            target_path: Path where config file should be created (Path object or string)
            config_type: Type of config ("application" or "hardware")
        """
        target_file = Path(target_path)

        if target_file.exists():
            logger.debug(f"Configuration file already exists: {target_path}")
            return

        try:
            # Create target directory
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Get default configuration from domain value objects
            if config_type == "application":
                default_config = ApplicationConfig()
                config_data = default_config.to_dict()
            elif config_type == "hardware":
                default_config = HardwareConfig()
                config_data = default_config.to_dict()
            else:
                raise ValueError(f"Unknown config type: {config_type}")

            # Add metadata
            config_data["metadata"] = {
                "created_at": datetime.now().isoformat(),
                "note": f"Auto-generated default {config_type} configuration",
                "created_by": "YamlContainerConfigurationLoader (auto-generated)",
            }

            # Write to target file with formatting
            yaml_content = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
            formatted_content = self._format_yaml_with_spacing(yaml_content)

            with open(target_file, "w", encoding="utf-8") as f:
                f.write(formatted_content)

            logger.info(f"Created {config_type} configuration from defaults: {target_path}")

        except Exception as e:
            logger.error(f"Failed to create config from defaults: {e}")
            raise

    def _load_yaml_file(self, file_path: Path | str) -> Dict[str, Any]:
        """
        Load YAML configuration file.

        Args:
            file_path: Path to YAML file (Path object or string)

        Returns:
            Dictionary containing loaded configuration
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if config_data is None:
                logger.warning(f"Empty YAML file: {file_path}")
                return {}

            return config_data

        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}")
            raise

    def _get_fallback_configuration(self) -> Dict[str, Any]:
        """Get fallback configuration using in-memory defaults."""
        app_config = ApplicationConfig()
        hardware_config = HardwareConfig()

        combined_config = app_config.to_dict()
        combined_config["hardware"] = hardware_config.to_dict()

        logger.info("Fallback default configuration created")
        return combined_config
