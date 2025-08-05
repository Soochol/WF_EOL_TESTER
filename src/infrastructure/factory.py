"""
Hardware Service Factory

Simple factory for creating hardware services based on configuration.
Replaces the complex dependency injection system.
"""

from typing import TYPE_CHECKING, Dict, Optional, Union

from loguru import logger

from application.services.hardware_service_facade import HardwareServiceFacade
from infrastructure.implementation.hardware.digital_input.ajinextek.ajinextek_dio import (
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
from infrastructure.implementation.hardware.robot.mock.mock_robot import (
    MockRobot,
)

# Type checking imports for better IDE support
if TYPE_CHECKING:
    from infrastructure.implementation.hardware.digital_input.mock.mock_dio import (
        MockDIO,
    )
    from infrastructure.implementation.hardware.loadcell.mock.mock_loadcell import (
        MockLoadCell,
    )
    from infrastructure.implementation.hardware.mcu.mock.mock_mcu import MockMCU
    from infrastructure.implementation.hardware.power.mock.mock_power import MockPower


class ServiceFactory:
    """하드웨어 서비스 팩토리"""

    @staticmethod
    def create_loadcell_service(
        config: Optional[Dict] = None,
    ) -> Union["BS205LoadCell", "MockLoadCell"]:
        """
        LoadCell 서비스 생성 (설정 기반)

        Args:
            config: LoadCell 설정 딕셔너리 (model 키로 구분)

        Returns:
            LoadCell 서비스 인스턴스
        """
        if config and config.get("model", "").lower() == "mock":
            from infrastructure.implementation.hardware.loadcell.mock.mock_loadcell import (
                MockLoadCell,
            )

            logger.info("Creating Mock LoadCell service")
            return MockLoadCell()

        # BS205 실제 하드웨어 (기본 설정)
        logger.info("Creating BS205 LoadCell service")
        return BS205LoadCell()

    @staticmethod
    def create_power_service(config: Optional[Dict] = None) -> Union["OdaPower", "MockPower"]:
        """
        Power 서비스 생성 (설정 기반)

        Args:
            config: Power 설정 딕셔너리 (model 키로 구분)

        Returns:
            Power 서비스 인스턴스
        """
        if config and config.get("model", "").lower() == "mock":
            from infrastructure.implementation.hardware.power.mock.mock_power import (
                MockPower,
            )

            logger.info("Creating Mock Power service")
            return MockPower()

        # ODA 실제 하드웨어 (기본 설정)
        logger.info("Creating ODA Power service")
        return OdaPower()

    @staticmethod
    def create_mcu_service(config: Optional[Dict] = None) -> Union["LMAMCU", "MockMCU"]:
        """
        MCU 서비스 생성 (설정 기반)

        Args:
            config: MCU 설정 딕셔너리 (model 키로 구분)

        Returns:
            MCU 서비스 인스턴스
        """
        if config and config.get("model", "").lower() == "mock":
            from infrastructure.implementation.hardware.mcu.mock.mock_mcu import MockMCU

            logger.info("Creating Mock MCU service")
            return MockMCU()

        # LMA 실제 하드웨어 (기본 설정)
        logger.info("Creating LMA MCU service")
        return LMAMCU()

    @staticmethod
    def create_digital_input_service(
        config: Optional[Dict] = None,
    ) -> Union["AjinextekDIO", "MockDIO"]:
        """
        Digital Input 서비스 생성 (설정 기반)

        Args:
            config: Digital Input 설정 딕셔너리 (model 키로 구분)

        Returns:
            Digital Input 서비스 인스턴스
        """
        if config and config.get("model", "").lower() == "mock":
            from infrastructure.implementation.hardware.digital_input.mock.mock_dio import (
                MockDIO,
            )

            logger.info("Creating Mock Digital Input service")
            # MockDIO requires config, so pass a default config if none provided
            mock_config = config if config else {"model": "mock"}
            return MockDIO(mock_config)

        # Ajinextek DIO 실제 하드웨어 (기본 설정)
        logger.info("Creating Ajinextek Digital Input service")
        return AjinextekDIO()

    @staticmethod
    def create_robot_service(config: Optional[Dict] = None) -> Union["AjinextekRobot", "MockRobot"]:
        """
        Robot 서비스 생성 (설정 기반)

        Args:
            config: Robot 설정 딕셔너리 (model 키로 구분)

        Returns:
            Robot 서비스 인스턴스
        """
        if config and config.get("model", "").lower() == "mock":
            logger.info("Creating Mock Robot service")
            return MockRobot()

        # AJINEXTEK 실제 하드웨어 (기본 설정)
        logger.info("Creating AJINEXTEK Robot service")
        return AjinextekRobot()


def create_hardware_service_facade() -> "HardwareServiceFacade":
    """
    Create a complete hardware service facade with all hardware services

    Returns:
        HardwareServiceFacade instance with all services configured
    """
    logger.info("Creating hardware service facade")

    try:
        # Create all hardware services
        robot_service = ServiceFactory.create_robot_service()
        mcu_service = ServiceFactory.create_mcu_service()
        loadcell_service = ServiceFactory.create_loadcell_service()
        power_service = ServiceFactory.create_power_service()
        digital_input_service = ServiceFactory.create_digital_input_service()

        # Create and return facade
        facade = HardwareServiceFacade(
            robot_service=robot_service,
            mcu_service=mcu_service,
            loadcell_service=loadcell_service,
            power_service=power_service,
            digital_input_service=digital_input_service,
        )

        logger.info("Hardware service facade created successfully")
        return facade

    except Exception as e:
        logger.error("Failed to create hardware service facade: %s", e)
        raise
