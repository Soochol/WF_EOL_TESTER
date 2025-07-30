"""
Hardware Service Factory

Simple factory for creating hardware services based on configuration.
Replaces the complex dependency injection system.
"""

from typing import Any, Dict, Optional

from application.interfaces.hardware.digital_input import (
    DigitalInputService,
)
from application.interfaces.hardware.loadcell import (
    LoadCellService,
)
from application.interfaces.hardware.mcu import MCUService
from application.interfaces.hardware.power import (
    PowerService,
)
from application.interfaces.hardware.robot import (
    RobotService,
)
from application.services.hardware_service_facade import HardwareServiceFacade

# Hardware implementations
from infrastructure.implementation.hardware.digital_input.ajinextek.ajinextek_input import (
    AjinextekInput,
)
from infrastructure.implementation.hardware.digital_input.mock.mock_input import (
    MockInput,
)
from infrastructure.implementation.hardware.loadcell.bs205.bs205_loadcell import (
    BS205LoadCell,
)
from infrastructure.implementation.hardware.loadcell.mock.mock_loadcell import (
    MockLoadCell,
)
from infrastructure.implementation.hardware.mcu.lma.lma_mcu import (
    LMAMCU,
)
from infrastructure.implementation.hardware.mcu.mock.mock_mcu import (
    MockMCU,
)
from infrastructure.implementation.hardware.power.mock.mock_power import (
    MockPower,
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

# Conditional logging import
logger: Any
try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class ServiceFactory:
    """하드웨어 서비스 팩토리"""

    @staticmethod
    def create_loadcell_service(
        config: Dict[str, Any],
    ) -> LoadCellService:
        """
        LoadCell 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            LoadCell 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get("model", config.get("type", "bs205")).lower()

        if hw_type == "mock":
            # Mock 서비스 (config Dict 전달)
            logger.info("Creating Mock LoadCell service with config")
            return MockLoadCell(config=config)

        if hw_type == "bs205":
            # BS205 실제 하드웨어 (config Dict 전달)
            logger.info("Creating BS205 LoadCell service with config")
            return BS205LoadCell(config=config)

        raise ValueError(f"Unsupported loadcell type: {hw_type}")

    @staticmethod
    def create_power_service(
        config: Dict[str, Any],
    ) -> PowerService:
        """
        Power 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            Power 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get("model", config.get("type", "oda")).lower()

        if hw_type == "mock":
            # Mock 서비스 (config Dict 전달)
            logger.info("Creating Mock Power service with config")
            return MockPower(config=config)

        if hw_type == "oda":
            # ODA 실제 하드웨어 (config Dict 전달)
            logger.info("Creating ODA Power service with config")
            return OdaPower(config=config)

        raise ValueError(f"Unsupported power supply type: {hw_type}")

    @staticmethod
    def create_mcu_service(
        config: Dict[str, Any],
    ) -> MCUService:
        """
        MCU 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            MCU 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get("model", config.get("type", "lma")).lower()

        if hw_type == "mock":
            # Mock 서비스
            config_filtered = {k: v for k, v in config.items() if k != 'model'}
            logger.info(f"Creating Mock MCU service with config: {config_filtered}")
            return MockMCU(config=config)

        if hw_type == "lma":
            # LMA 실제 하드웨어
            logger.info(
                "Creating LMA MCU service with config: %s",
                {k: v for k, v in config.items() if k != "model"},
            )
            return LMAMCU(config=config)

        raise ValueError(f"Unsupported MCU type: {hw_type}")

    @staticmethod
    def create_digital_input_service(
        config: Dict[str, Any],
    ) -> DigitalInputService:
        """
        Digital Input 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            Digital Input 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get("model", config.get("type", "ajinextek")).lower()

        if hw_type == "mock":
            # Mock 서비스
            logger.info("Creating Mock Digital Input service with config")
            return MockInput(config=config)

        if hw_type == "ajinextek":
            # Ajinextek DIO 실제 하드웨어
            logger.info("Creating Ajinextek Digital Input service with config")
            return AjinextekInput(config=config)

        raise ValueError(f"Unsupported digital input hardware type: {hw_type}")

    @staticmethod
    def create_robot_service(
        config: Dict[str, Any],
    ) -> RobotService:
        """
        Robot 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            Robot 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get("model", config.get("type", "ajinextek")).lower()

        if hw_type == "mock":
            # Mock 서비스 (config Dict 전달)
            logger.info("Creating Mock Robot service with config")
            return MockRobot(config=config)

        if hw_type == "ajinextek":
            # AJINEXTEK 실제 하드웨어
            logger.info(
                "Creating AJINEXTEK Robot service (IRQ: %s)",
                config.get("irq_no", 7),
            )
            return AjinextekRobot(config=config)

        raise ValueError(f"Unsupported robot hardware type: {hw_type}")


def create_hardware_service_facade(
    config_path: Optional[str] = None, use_mock: bool = False
) -> HardwareServiceFacade:
    """
    Create a complete hardware service facade with all hardware services

    Args:
        config_path: Path to hardware configuration file (optional)
        use_mock: Force use of mock hardware services

    Returns:
        HardwareServiceFacade instance with all services configured
    """
    logger.info("Creating hardware service facade (mock: %s)", use_mock)

    # Default hardware configurations
    default_configs: Dict[str, Dict[str, Any]] = {
        "robot": {
            "model": "mock" if use_mock else "ajinextek",
            "irq_no": 7,
            "max_velocity": 100.0,
            "max_acceleration": 1000.0,
        },
        "mcu": {
            "model": "mock" if use_mock else "lma",
            "port": "COM4",
            "baudrate": 115200,
            "timeout": 2.0,
            "default_temperature": 25.0,
            "default_fan_speed": 50.0,
        },
        "loadcell": {
            "model": "mock" if use_mock else "bs205",
            "port": "COM3",
            "baudrate": 9600,
            "timeout": 1.0,
        },
        "power": {
            "model": "mock" if use_mock else "oda",
            "host": "192.168.1.100",
            "port": 8080,
            "timeout": 5.0,
            "default_voltage": 0.0,
            "default_current_limit": 5.0,
        },
        "digital_input": {
            "model": "mock" if use_mock else "ajinextek",
            "device_number": 0,
            "module_position": 0,
        },
    }

    # If config_path is provided, you could load from file here
    # For now, using default configurations
    configs: Dict[str, Dict[str, Any]] = default_configs

    try:
        # Create all hardware services
        robot_service = ServiceFactory.create_robot_service(configs["robot"])
        mcu_service = ServiceFactory.create_mcu_service(configs["mcu"])
        loadcell_service = ServiceFactory.create_loadcell_service(configs["loadcell"])
        power_service = ServiceFactory.create_power_service(configs["power"])
        digital_input_service = ServiceFactory.create_digital_input_service(
            configs["digital_input"]
        )

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
