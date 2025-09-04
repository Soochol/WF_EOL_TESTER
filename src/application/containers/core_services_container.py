"""
Core Services Container

Dedicated container for cross-cutting business services.
Manages exception handling, test evaluation, and other core business logic services.
"""

from dependency_injector import containers, providers

from application.services.core.exception_handler import ExceptionHandler
from application.services.test.test_result_evaluator import TestResultEvaluator


class CoreServicesContainer(containers.DeclarativeContainer):
    """
    Core services container for dependency injection.

    Provides centralized management of:
    - Exception handling services
    - Test result evaluation services
    - Other cross-cutting business concerns
    """

    # ============================================================================
    # CORE BUSINESS SERVICES
    # ============================================================================

    exception_handler = providers.Singleton(ExceptionHandler)

    test_result_evaluator = providers.Singleton(TestResultEvaluator)