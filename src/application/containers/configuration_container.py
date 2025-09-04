"""
Configuration Container

Dedicated container for configuration-related services and dependencies.
Manages YAML configuration loading, validation, and configuration services.
"""

from dependency_injector import containers, providers

from application.services.core.configuration_service import ConfigurationService
from application.services.core.configuration_validator import ConfigurationValidator
from infrastructure.implementation.configuration.yaml_configuration import (
    YamlConfiguration,
)


class ConfigurationContainer(containers.DeclarativeContainer):
    """
    Configuration container for dependency injection.

    Provides centralized management of:
    - Configuration loading (YAML)
    - Configuration validation
    - Configuration services
    """

    # Configuration provider (shared with parent container)
    config = providers.Configuration()

    # ============================================================================
    # CONFIGURATION INFRASTRUCTURE
    # ============================================================================

    yaml_configuration = providers.Singleton(YamlConfiguration)

    # ============================================================================
    # CONFIGURATION SERVICES
    # ============================================================================

    configuration_service = providers.Singleton(
        ConfigurationService,
        configuration=yaml_configuration,
    )

    configuration_validator = providers.Singleton(ConfigurationValidator)