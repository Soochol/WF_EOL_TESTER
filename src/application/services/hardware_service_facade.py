"""
Hardware Service Facade (Refactored)

Lightweight coordinator that orchestrates hardware services following single responsibility principle.
Previously 786 lines, now significantly reduced by delegating to specialized services.
"""

from typing import TYPE_CHECKING, Dict, Optional, cast

from loguru import logger

from application.interfaces.hardware.digital_io import DigitalIOService
from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.mcu import MCUService
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.robot import RobotService
from domain.value_objects.hardware_config import HardwareConfig
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.test_configuration import TestConfiguration

# Hardware service components
from .hardware.hardware_connection_manager import HardwareConnectionManager
from .hardware.hardware_initialization_service import HardwareInitializationService
from .hardware.hardware_test_executor import HardwareTestExecutor
from .hardware.hardware_verification_service import HardwareVerificationService

# IDE 개발용 타입 힌트 - 런타임에는 영향 없음
if TYPE_CHECKING:
    from infrastructure.implementation.hardware.digital_io.ajinextek.ajinextek_dio import (
        AjinextekDIO,
    )
    from infrastructure.implementation.hardware.loadcell.bs205.bs205_loadcell import (
        BS205LoadCell,
    )
    from infrastructure.implementation.hardware.mcu.lma.lma_mcu import (
        LMAMCU,
    )
    from infrastructure.implementation.hardware.power.oda.oda_power import (
        OdaPower,
    )
    from infrastructure.implementation.hardware.robot.ajinextek.ajinextek_robot import (
        AjinextekRobot,
    )


class HardwareServiceFacade:
    """
    Lightweight coordinator for hardware services

    This refactored facade delegates operations to specialized services while maintaining
    the same public interface for backward compatibility.

    Services coordinated:
    - HardwareConnectionManager: Connection lifecycle
    - HardwareInitializationService: Hardware setup and configuration
    - HardwareTestExecutor: Test execution sequences
    - HardwareVerificationService: Hardware validation operations
    """

    def __init__(
        self,
        robot_service: RobotService,
        mcu_service: MCUService,
        loadcell_service: LoadCellService,
        power_service: PowerService,
        digital_io_service: DigitalIOService,
    ):
        # Store services for property access (backward compatibility)
        if TYPE_CHECKING:
            self._robot = cast("AjinextekRobot", robot_service)
            self._mcu = cast("LMAMCU", mcu_service)
            self._loadcell = cast("BS205LoadCell", loadcell_service)
            self._power = cast("OdaPower", power_service)
            self._digital_io = cast("AjinextekDIO", digital_io_service)
        else:
            self._robot = robot_service
            self._mcu = mcu_service
            self._loadcell = loadcell_service
            self._power = power_service
            self._digital_io = digital_io_service

        # Initialize specialized hardware services
        self._connection_manager = HardwareConnectionManager(
            robot_service, mcu_service, loadcell_service, power_service, digital_io_service
        )

        self._initialization_service = HardwareInitializationService(
            robot_service, power_service, digital_io_service, loadcell_service
        )

        self._verification_service = HardwareVerificationService(mcu_service)

        self._test_executor = HardwareTestExecutor(
            robot_service, mcu_service, loadcell_service, power_service, digital_io_service
        )

        # Set verification service in test executor to avoid circular dependency
        self._test_executor.set_verification_service(self._verification_service)

    # ============================================================================
    # Service Property Accessors (Backward Compatibility)
    # ============================================================================

    @property
    def robot_service(self) -> RobotService:
        """Get robot service instance"""
        return self._robot

    @property
    def mcu_service(self) -> MCUService:
        """Get MCU service instance"""
        return self._mcu

    @property
    def loadcell_service(self) -> LoadCellService:
        """Get loadcell service instance"""
        return self._loadcell

    @property
    def power_service(self) -> PowerService:
        """Get power service instance"""
        return self._power

    @property
    def digital_io_service(self) -> DigitalIOService:
        """Get digital I/O service instance"""
        return self._digital_io

    # ============================================================================
    # Connection Management (Delegated to HardwareConnectionManager)
    # ============================================================================

    async def connect_all_hardware(self, hardware_config: HardwareConfig) -> None:
        """Connect all required hardware"""
        logger.debug("HardwareServiceFacade: Delegating connection to HardwareConnectionManager")
        await self._connection_manager.connect_all_hardware(hardware_config)

    async def get_hardware_status(self) -> Dict[str, bool]:
        """Get connection status of all hardware"""
        logger.debug("HardwareServiceFacade: Delegating status check to HardwareConnectionManager")
        return await self._connection_manager.get_hardware_status()

    async def shutdown_hardware(self, hardware_config: Optional[HardwareConfig] = None) -> None:
        """Safely shutdown all hardware"""
        logger.debug("HardwareServiceFacade: Delegating shutdown to HardwareConnectionManager")
        await self._connection_manager.shutdown_hardware(hardware_config)

    # ============================================================================
    # Hardware Initialization (Delegated to HardwareInitializationService)
    # ============================================================================

    async def initialize_hardware(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> None:
        """Initialize all hardware with configuration settings"""
        logger.debug(
            "HardwareServiceFacade: Delegating initialization to HardwareInitializationService"
        )
        await self._initialization_service.initialize_hardware(test_config, hardware_config)

    # ============================================================================
    # Test Execution (Delegated to HardwareTestExecutor)
    # ============================================================================

    async def setup_test(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> None:
        """Setup hardware for test execution"""
        logger.debug("HardwareServiceFacade: Delegating test setup to HardwareTestExecutor")
        await self._test_executor.setup_test(test_config, hardware_config)

    async def set_lma_standby(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> None:
        """Set LMA standby sequence - coordinate MCU and Robot for LMA standby state"""
        logger.debug("HardwareServiceFacade: Delegating LMA standby to HardwareTestExecutor")
        await self._test_executor.set_lma_standby(test_config, hardware_config)

    async def perform_force_test_sequence(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> TestMeasurements:
        """Perform complete force test measurement sequence with temperature and position matrix"""
        logger.debug("HardwareServiceFacade: Delegating test execution to HardwareTestExecutor")
        return await self._test_executor.perform_force_test_sequence(test_config, hardware_config)

    async def teardown_test(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> None:
        """Teardown test and return hardware to safe state"""
        logger.debug("HardwareServiceFacade: Delegating test teardown to HardwareTestExecutor")
        await self._test_executor.teardown_test(test_config, hardware_config)

    # ============================================================================
    # Hardware Verification (Delegated to HardwareVerificationService)
    # ============================================================================

    async def verify_mcu_temperature(
        self, expected_temp: float, test_config: TestConfiguration
    ) -> None:
        """Verify MCU temperature is within acceptable range of expected value"""
        logger.debug(
            "HardwareServiceFacade: Delegating temperature verification to HardwareVerificationService"
        )
        await self._verification_service.verify_mcu_temperature(expected_temp, test_config)

    # ============================================================================
    # Additional Utility Methods
    # ============================================================================

    def is_robot_homed(self) -> bool:
        """Check if robot has been homed"""
        return self._initialization_service.is_robot_homed()

    def reset_robot_homing_state(self) -> None:
        """Reset robot homing state"""
        self._initialization_service.reset_homing_state()
