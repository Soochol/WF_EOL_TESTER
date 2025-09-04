"""
Use Case Container

Dedicated container for application use cases and business logic.
Manages all use case implementations and their dependencies.
"""

from dependency_injector import containers, providers

from application.use_cases.eol_force_test import EOLForceTestUseCase
from application.use_cases.heating_cooling_time_test import (
    HeatingCoolingTimeTestUseCase,
)
from application.use_cases.robot_operations import RobotHomeUseCase
from application.use_cases.system_tests import SimpleMCUTestUseCase


class UseCaseContainer(containers.DeclarativeContainer):
    """
    Use case container for dependency injection.

    Provides centralized management of:
    - All application use cases
    - Business logic implementations
    - Use case dependencies and wiring
    """

    # External dependencies (injected from parent container)
    hardware_service_facade = providers.Dependency()
    configuration_service = providers.Dependency()
    configuration_validator = providers.Dependency()
    test_result_evaluator = providers.Dependency()
    repository_service = providers.Dependency()
    exception_handler = providers.Dependency()

    # ============================================================================
    # USE CASES
    # ============================================================================

    # Complex Use Case (with full dependency set)
    eol_force_test_use_case: providers.Factory[EOLForceTestUseCase] = providers.Factory(
        EOLForceTestUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
        configuration_validator=configuration_validator,
        test_result_evaluator=test_result_evaluator,
        repository_service=repository_service,
        exception_handler=exception_handler,
    )

    # Standard Use Cases (with minimal dependencies)
    robot_home_use_case: providers.Factory[RobotHomeUseCase] = providers.Factory(
        RobotHomeUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
    )

    heating_cooling_time_test_use_case: providers.Factory[HeatingCoolingTimeTestUseCase] = (
        providers.Factory(
            HeatingCoolingTimeTestUseCase,
            hardware_services=hardware_service_facade,
            configuration_service=configuration_service,
        )
    )

    simple_mcu_test_use_case: providers.Factory[SimpleMCUTestUseCase] = providers.Factory(
        SimpleMCUTestUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
    )