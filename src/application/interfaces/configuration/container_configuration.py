"""
Container Configuration Interface

Interface for configuration loading specifically for dependency injection containers.
"""

from typing import Any, Dict, Protocol


class ContainerConfigurationLoader(Protocol):
    """Configuration loader interface for dependency injection containers"""

    def load_all_configurations(self) -> Dict[str, Any]:
        """
        Load all configuration files and return combined configuration dictionary.
        
        Returns:
            Dictionary containing all loaded configurations for container initialization
        """
        ...

    def ensure_configurations_exist(self) -> None:
        """
        Ensure configuration files exist, create from defaults if missing.
        
        Raises:
            Exception: If configuration files cannot be created or accessed
        """
        ...