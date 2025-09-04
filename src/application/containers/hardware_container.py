"""
Hardware Container

Dedicated container for hardware-related services and dependencies.
Manages hardware factory, hardware service facade, and all hardware integrations.
"""

from dependency_injector import containers, providers

from application.services.hardware_facade import HardwareServiceFacade
from infrastructure.factories.hardware_factory import HardwareFactory


class HardwareContainer(containers.DeclarativeContainer):
    """
    Hardware container for dependency injection.

    Provides centralized management of:
    - Hardware factory and services
    - Hardware service facade
    - Hardware-related infrastructure
    """

    # Configuration provider (shared with parent container)
    config = providers.Configuration()

    # ============================================================================
    # HARDWARE LAYER
    # ============================================================================

    hardware_factory = providers.Container(HardwareFactory, config=config.hardware)

    # ============================================================================
    # HARDWARE SERVICES
    # ============================================================================

    hardware_service_facade = providers.Singleton(
        HardwareServiceFacade,
        robot_service=hardware_factory.robot_service,
        mcu_service=hardware_factory.mcu_service,
        loadcell_service=hardware_factory.loadcell_service,
        power_service=hardware_factory.power_service,
        digital_io_service=hardware_factory.digital_io_service,
    )