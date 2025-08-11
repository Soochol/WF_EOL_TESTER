"""
Simple YAML Configuration Implementation

Replacement for the deleted yaml_configuration module.
Provides basic YAML file-based configuration loading and saving.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from loguru import logger

from domain.value_objects.hardware_configuration import HardwareConfiguration
from domain.value_objects.test_configuration import TestConfiguration
from domain.value_objects.hardware_model import HardwareModel


class YamlConfiguration:
    """Simple YAML-based configuration implementation"""
    
    def __init__(self, config_dir: str = "configuration"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    async def load_profile(self, profile_name: str) -> TestConfiguration:
        """Load test configuration profile"""
        profile_path = self.config_dir / f"{profile_name}.yaml"
        
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_path}")
        
        with open(profile_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        return TestConfiguration.from_structured_dict(data)
    
    async def load_hardware_config(self) -> HardwareConfiguration:
        """Load hardware configuration"""
        config_path = self.config_dir / "hardware_configuration.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Hardware config not found: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Extract hardware_config section if present
        hw_config_data = data.get("hardware_config", data)
        return HardwareConfiguration.from_dict(hw_config_data)
    
    async def list_available_profiles(self) -> List[str]:
        """List available configuration profiles"""
        profiles = []
        
        for yaml_file in self.config_dir.glob("*.yaml"):
            # Skip special configuration files
            if yaml_file.name not in ["hardware_configuration.yaml", "hardware_model.yaml", "dut_defaults.yaml"]:
                profiles.append(yaml_file.stem)
        
        return sorted(profiles)
    
    async def load_hardware_model(self) -> HardwareModel:
        """Load hardware model configuration"""
        model_path = self.config_dir / "hardware_model.yaml"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Hardware model not found: {model_path}")
        
        with open(model_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Extract hardware_model section if present
        model_data = data.get("hardware_model", data)
        return HardwareModel.from_dict(model_data)
    
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
                    "part_number": "PN001"
                },
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "note": "Auto-generated default configuration",
                    "created_by": "YamlConfiguration (auto-generated)"
                }
            }
            
            # Save the default configuration for future use
            with open(dut_path, "w", encoding="utf-8") as f:
                yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
            
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
        profile_path = self.config_dir / f"{profile_name}.yaml"
        
        # Convert TestConfiguration to dictionary
        config_data = test_config.to_dict()
        
        with open(profile_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Saved test profile: {profile_path}")
    
    async def save_hardware_config(self, hardware_config: HardwareConfiguration) -> None:
        """Save hardware configuration"""
        config_path = self.config_dir / "hardware_configuration.yaml"
        
        # Convert to dictionary and wrap in hardware_config section
        config_data = {
            "hardware_config": hardware_config.to_dict()
        }
        
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Saved hardware configuration: {config_path}")
    
    async def save_hardware_model(self, hardware_model: HardwareModel) -> None:
        """Save hardware model configuration"""
        model_path = self.config_dir / "hardware_model.yaml"
        
        # Convert to dictionary and wrap in hardware_model section
        model_data = {
            "hardware_model": hardware_model.to_dict()
        }
        
        with open(model_path, "w", encoding="utf-8") as f:
            yaml.dump(model_data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Saved hardware model: {model_path}")
    
    async def save_dut_defaults(self, dut_defaults_data: Dict[str, Any], profile_name: str = "default") -> None:
        """Save DUT defaults configuration"""
        dut_path = self.config_dir / "dut_defaults.yaml"
        
        # Load existing data if file exists
        existing_data = {}
        if dut_path.exists():
            with open(dut_path, "r", encoding="utf-8") as f:
                existing_data = yaml.safe_load(f) or {}
        
        # Update with new data for the specified profile
        existing_data[profile_name] = dut_defaults_data
        
        with open(dut_path, "w", encoding="utf-8") as f:
            yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Saved DUT defaults for profile '{profile_name}': {dut_path}")