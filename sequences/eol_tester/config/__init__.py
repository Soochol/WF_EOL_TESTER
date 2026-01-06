"""
Configuration loader for EOL Tester sequence.
Loads hardware configuration from local config file for self-contained operation.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

# Config directory path (relative to this file)
CONFIG_DIR = Path(__file__).parent
HARDWARE_CONFIG_FILE = CONFIG_DIR / "hardware_config.yaml"


def load_hardware_config_dict() -> Dict[str, Any]:
    """
    Load hardware configuration from local YAML file.

    Returns:
        Dictionary with hardware configuration
    """
    if not HARDWARE_CONFIG_FILE.exists():
        logger.warning(f"Hardware config not found: {HARDWARE_CONFIG_FILE}, using defaults")
        return {}

    try:
        with open(HARDWARE_CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        logger.info(f"Loaded hardware config from: {HARDWARE_CONFIG_FILE}")
        return config
    except Exception as e:
        logger.error(f"Failed to load hardware config: {e}")
        return {}


def load_hardware_config() -> "HardwareConfig":
    """
    Load hardware configuration as HardwareConfig object.

    Returns:
        HardwareConfig instance with loaded values
    """
    from ..domain.value_objects import HardwareConfig

    config_dict = load_hardware_config_dict()
    if config_dict:
        return HardwareConfig.from_dict(config_dict)
    return HardwareConfig()  # Default mock config


def save_hardware_config(config: "HardwareConfig") -> bool:
    """
    Save hardware configuration to local YAML file.

    Args:
        config: HardwareConfig instance to save

    Returns:
        True if saved successfully
    """
    try:
        config_dict = config.to_dict()
        with open(HARDWARE_CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Saved hardware config to: {HARDWARE_CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to save hardware config: {e}")
        return False


def get_config_path() -> Path:
    """Return the path to the hardware config file."""
    return HARDWARE_CONFIG_FILE
