"""
Hardware Service Factory

Simple factory for creating hardware services based on configuration.
Replaces the complex dependency injection system.
"""

from typing import TYPE_CHECKING, Dict, Optional, Union

from loguru import logger

from src.application.services.hardware_service_facade import HardwareServiceFacade
from src.infrastructure.implementation.hardware.digital_io.ajinextek.ajinextek_dio import (
    AjinextekDIO,
)
from src.infrastructure.implementation.hardware.loadcell.bs205.bs205_loadcell import (
    BS205LoadCell,
)
from src.infrastructure.implementation.hardware.mcu.lma.lma_mcu import (
    LMAMCU,
)
from src.infrastructure.implementation.hardware.power.oda.oda_power import (
    OdaPower,
)
from src.infrastructure.implementation.hardware.robot.ajinextek.ajinextek_robot import (
    AjinextekRobot,
)
from src.infrastructure.implementation.hardware.robot.mock.mock_robot import (
    MockRobot,
)

# Type checking imports for better IDE support
if TYPE_CHECKING:
    from infrastructure.implementation.hardware.digital_io.mock.mock_dio import (
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
    def load_hardware_configurations() -> Optional[Dict]:
        """Load hardware configurations from YAML file

        Returns:
            Dictionary containing hardware configurations or None if loading fails
        """
        try:
            from pathlib import Path

            import yaml

            # Try to directly load hardware configuration file
            config_path = Path("configuration/hardware_configuration.yaml")

            if not config_path.exists():
                logger.warning(f"Hardware configuration file not found: {config_path}")
                return None

            with open(config_path, "r", encoding="utf-8") as f:
                yaml_content = yaml.safe_load(f)

            # Extract hardware_config section
            hw_config_data = yaml_content.get("hardware_config", {})
            if not hw_config_data:
                logger.warning("No 'hardware_config' section found in YAML file")
                return None

            # Convert YAML dictionary to standardized format with model information
            robot_data = hw_config_data.get("robot", {})
            loadcell_data = hw_config_data.get("loadcell", {})
            mcu_data = hw_config_data.get("mcu", {})
            power_data = hw_config_data.get("power", {})
            digital_io_data = hw_config_data.get("digital_io", {})

            configs = {
                "robot": {
                    "model": "ajinextek",
                    "axis_id": robot_data.get("axis_id", 0),
                    "irq_no": robot_data.get("irq_no", 7),
                    **robot_data,  # Include any additional robot configuration
                },
                "loadcell": {
                    "model": "bs205",
                    "port": loadcell_data.get("port", "COM1"),
                    "baudrate": loadcell_data.get("baudrate", 9600),
                    "timeout": loadcell_data.get("timeout", 1.0),
                    "bytesize": loadcell_data.get("bytesize", 8),
                    "stopbits": loadcell_data.get("stopbits", 1),
                    "parity": loadcell_data.get("parity", "N"),
                    "indicator_id": loadcell_data.get("indicator_id", 1),
                    **loadcell_data,  # Include any additional loadcell configuration
                },
                "mcu": {
                    "model": "lma",
                    "port": mcu_data.get("port", "COM2"),
                    "baudrate": mcu_data.get("baudrate", 115200),
                    "timeout": mcu_data.get("timeout", 1.0),
                    "bytesize": mcu_data.get("bytesize", 8),
                    "stopbits": mcu_data.get("stopbits", 1),
                    "parity": mcu_data.get("parity", "N"),
                    **mcu_data,  # Include any additional MCU configuration
                },
                "power": {
                    "model": "oda",
                    "host": power_data.get("host", "localhost"),
                    "port": power_data.get("port", 8080),
                    "timeout": power_data.get("timeout", 5.0),
                    "channel": power_data.get("channel", 1),
                    **power_data,  # Include any additional power configuration
                },
                "digital_io": {
                    "model": "ajinextek",
                    "operator_start_button_left": digital_io_data.get(
                        "operator_start_button_left", 0
                    ),
                    "operator_start_button_right": digital_io_data.get(
                        "operator_start_button_right", 1
                    ),
                    "tower_lamp_red": digital_io_data.get("tower_lamp_red", 2),
                    "tower_lamp_yellow": digital_io_data.get("tower_lamp_yellow", 3),
                    "tower_lamp_green": digital_io_data.get("tower_lamp_green", 4),
                    "beep": digital_io_data.get("beep", 5),
                    **digital_io_data,  # Include any additional digital I/O configuration
                },
            }

            logger.info("Hardware configurations loaded from YAML file successfully")
            return configs

        except Exception as e:
            logger.warning(f"Failed to load hardware configuration from YAML: {e}")
            logger.info("Using default hardware configurations")
            return None

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

        # BS205 실제 하드웨어
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

        # ODA 실제 하드웨어
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

        # LMA 실제 하드웨어
        logger.info("Creating LMA MCU service")
        return LMAMCU()

    @staticmethod
    def create_digital_io_service(
        config: Optional[Dict] = None,
    ) -> Union["AjinextekDIO", "MockDIO"]:
        """
        Digital I/O 서비스 생성 (설정 기반)

        Args:
            config: Digital I/O 설정 딕셔너리 (model 키로 구분)

        Returns:
            Digital I/O 서비스 인스턴스
        """
        if config and config.get("model", "").lower() == "mock":
            from infrastructure.implementation.hardware.digital_io.mock.mock_dio import (
                MockDIO,
            )

            logger.info("Creating Mock Digital I/O service")
            # MockInput requires config, so pass a default config if none provided
            mock_config = config if config else {"model": "mock"}
            return MockDIO(mock_config)

        # Ajinextek DIO 실제 하드웨어
        logger.info("Creating Ajinextek Digital I/O service")
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

        # AJINEXTEK 실제 하드웨어
        logger.info("Creating AJINEXTEK Robot service")
        return AjinextekRobot()

    @staticmethod
    def create_hardware_services_typed(use_mock: bool = False):
        """
        IDE 개발용: 구체 타입을 반환하는 팩토리 메서드

        Returns:
            실제 구현체 타입의 tuple (IDE 네비게이션용)
        """
        try:
            hardware_configs = (
                ServiceFactory.load_hardware_configurations() if not use_mock else None
            )

            robot_service = ServiceFactory.create_robot_service(
                hardware_configs.get("robot")
                if hardware_configs
                else ({"model": "mock"} if use_mock else None)
            )
            mcu_service = ServiceFactory.create_mcu_service(
                hardware_configs.get("mcu")
                if hardware_configs
                else ({"model": "mock"} if use_mock else None)
            )
            loadcell_service = ServiceFactory.create_loadcell_service(
                hardware_configs.get("loadcell")
                if hardware_configs
                else ({"model": "mock"} if use_mock else None)
            )
            power_service = ServiceFactory.create_power_service(
                hardware_configs.get("power")
                if hardware_configs
                else ({"model": "mock"} if use_mock else None)
            )
            digital_io_service = ServiceFactory.create_digital_io_service(
                hardware_configs.get("digital_io")
                if hardware_configs
                else ({"model": "mock"} if use_mock else None)
            )

            return robot_service, mcu_service, loadcell_service, power_service, digital_io_service

        except Exception as e:
            logger.error("Failed to create typed hardware services: %s", e)
            raise


def create_hardware_service_facade(
    _config_path: Optional[str] = None, use_mock: bool = False
) -> "HardwareServiceFacade":
    """
    Create a complete hardware service facade with all hardware services

    Args:
        _config_path: Optional path to configuration file (currently unused but kept for compatibility)
        use_mock: If True, create mock hardware services instead of real ones

    Returns:
        HardwareServiceFacade instance with all services configured
    """
    logger.info("Creating hardware service facade (use_mock=%s)", use_mock)

    try:
        # Load hardware configuration from YAML file if not using mock
        hardware_configs = ServiceFactory.load_hardware_configurations() if not use_mock else None
        # Create all hardware services with proper configuration
        robot_service = ServiceFactory.create_robot_service(
            hardware_configs.get("robot")
            if hardware_configs
            else ({"model": "mock"} if use_mock else None)
        )
        mcu_service = ServiceFactory.create_mcu_service(
            hardware_configs.get("mcu")
            if hardware_configs
            else ({"model": "mock"} if use_mock else None)
        )
        loadcell_service = ServiceFactory.create_loadcell_service(
            hardware_configs.get("loadcell")
            if hardware_configs
            else ({"model": "mock"} if use_mock else None)
        )
        power_service = ServiceFactory.create_power_service(
            hardware_configs.get("power")
            if hardware_configs
            else ({"model": "mock"} if use_mock else None)
        )
        digital_io_service = ServiceFactory.create_digital_io_service(
            hardware_configs.get("digital_io")
            if hardware_configs
            else ({"model": "mock"} if use_mock else None)
        )

        # Create and return facade
        facade = HardwareServiceFacade(
            robot_service=robot_service,
            mcu_service=mcu_service,
            loadcell_service=loadcell_service,
            power_service=power_service,
            digital_io_service=digital_io_service,
        )

        logger.info("Hardware service facade created successfully")
        return facade

    except Exception as e:
        logger.error("Failed to create hardware service facade: %s", e)
        raise
