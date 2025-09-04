"""
Persistence Container

Dedicated container for data persistence and repository services.
Manages JSON repositories, database connections, and data storage services.
"""

from dependency_injector import containers, providers

from application.services.core.repository_service import RepositoryService
from infrastructure.implementation.repositories.json_result_repository import (
    JsonResultRepository,
)


class PersistenceContainer(containers.DeclarativeContainer):
    """
    Persistence container for dependency injection.

    Provides centralized management of:
    - Repository implementations
    - Data storage services
    - Persistence-related infrastructure
    """

    # Configuration provider (shared with parent container)
    config = providers.Configuration()

    # ============================================================================
    # REPOSITORY INFRASTRUCTURE
    # ============================================================================

    json_result_repository = providers.Singleton(
        JsonResultRepository,
        data_dir=config.services.repository.results_path,
        auto_save=config.services.repository.auto_save,
    )

    # ============================================================================
    # REPOSITORY SERVICES
    # ============================================================================

    repository_service = providers.Singleton(
        RepositoryService, test_repository=json_result_repository
    )