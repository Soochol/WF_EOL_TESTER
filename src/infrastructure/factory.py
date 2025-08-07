"""
Hardware Service Factory

Simple factory for creating hardware services based on configuration.
Replaces the complex dependency injection system.
"""

from typing import TYPE_CHECKING, Dict, Optional, Union

from loguru import logger

from application.services.hardware_service_facade import HardwareServiceFacade
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
from infrastructure.implementation.hardware.robot.mock.mock_robot import (
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
            from infrastructure.implementation.configuration.yaml_configuration import YamlConfiguration
            import asyncio
            
            config = YamlConfiguration()
            
            # Try to load hardware config synchronously
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're in an async context, log warning and use defaults
                    logger.warning("Cannot load YAML config in running event loop, using defaults")
                    return None
                else:
                    hw_config = loop.run_until_complete(config.load_hardware_config())
            except RuntimeError:
                # No event loop running, create one
                hw_config = asyncio.run(config.load_hardware_config())
            
            # Convert HardwareConfiguration object to dictionary format
            configs = {
                'robot': {
                    'model': 'ajinextek',
                    'axis_id': hw_config.robot.axis_id,
                    'irq_no': hw_config.robot.irq_no,
                },
                'loadcell': {
                    'model': 'bs205',
                    'port': hw_config.loadcell.port,
                    'baudrate': hw_config.loadcell.baudrate,
                    'timeout': hw_config.loadcell.timeout,
                    'bytesize': hw_config.loadcell.bytesize,
                    'stopbits': hw_config.loadcell.stopbits,
                    'parity': hw_config.loadcell.parity,
                    'indicator_id': hw_config.loadcell.indicator_id,
                },
                'mcu': {
                    'model': 'lma',
                    'port': hw_config.mcu.port,
                    'baudrate': hw_config.mcu.baudrate,
                    'timeout': hw_config.mcu.timeout,
                    'bytesize': hw_config.mcu.bytesize,
                    'stopbits': hw_config.mcu.stopbits,
                    'parity': hw_config.mcu.parity,
                },
                'power': {
                    'model': 'oda',
                    'host': hw_config.power.host,
                    'port': hw_config.power.port,
                    'timeout': hw_config.power.timeout,
                    'channel': hw_config.power.channel,
                },
                'digital_io': {
                    'model': 'ajinextek',
                    'operator_start_button_left': hw_config.digital_io.operator_start_button_left,
                    'operator_start_button_right': hw_config.digital_io.operator_start_button_right,
                    'tower_lamp_red': hw_config.digital_io.tower_lamp_red,
                    'tower_lamp_yellow': hw_config.digital_io.tower_lamp_yellow,
                    'tower_lamp_green': hw_config.digital_io.tower_lamp_green,
                    'beep': hw_config.digital_io.beep,
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


def create_hardware_service_facade(
    config_path: Optional[str] = None, use_mock: bool = False
) -> "HardwareServiceFacade":
    """
    Create a complete hardware service facade with all hardware services

    Args:
        config_path: Optional path to configuration file (currently unused but kept for compatibility)
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
            hardware_configs.get('robot') if hardware_configs else ({"model": "mock"} if use_mock else None)
        )
        mcu_service = ServiceFactory.create_mcu_service(
            hardware_configs.get('mcu') if hardware_configs else ({"model": "mock"} if use_mock else None)
        )
        loadcell_service = ServiceFactory.create_loadcell_service(
            hardware_configs.get('loadcell') if hardware_configs else ({"model": "mock"} if use_mock else None)
        )
        power_service = ServiceFactory.create_power_service(
            hardware_configs.get('power') if hardware_configs else ({"model": "mock"} if use_mock else None)
        )
        digital_io_service = ServiceFactory.create_digital_io_service(
            hardware_configs.get('digital_io') if hardware_configs else ({"model": "mock"} if use_mock else None)
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

    @staticmethod
    def create_hardware_services_typed(use_mock: bool = False):
        """
        IDE 개발용: 구체 타입을 반환하는 팩토리 메서드
        
        Returns:
            실제 구현체 타입의 tuple (IDE 네비게이션용)
        """
        try:
            hardware_configs = ServiceFactory.load_hardware_configurations() if not use_mock else None
            
            robot_service = ServiceFactory.create_robot_service(
                hardware_configs.get('robot') if hardware_configs else ({"model": "mock"} if use_mock else None)
            )
            mcu_service = ServiceFactory.create_mcu_service(
                hardware_configs.get('mcu') if hardware_configs else ({"model": "mock"} if use_mock else None)
            )
            loadcell_service = ServiceFactory.create_loadcell_service(
                hardware_configs.get('loadcell') if hardware_configs else ({"model": "mock"} if use_mock else None)
            )
            power_service = ServiceFactory.create_power_service(
                hardware_configs.get('power') if hardware_configs else ({"model": "mock"} if use_mock else None)
            )
            digital_io_service = ServiceFactory.create_digital_io_service(
                hardware_configs.get('digital_io') if hardware_configs else ({"model": "mock"} if use_mock else None)
            )

            return robot_service, mcu_service, loadcell_service, power_service, digital_io_service
            
        except Exception as e:
            logger.error("Failed to create typed hardware services: %s", e)
            raise
