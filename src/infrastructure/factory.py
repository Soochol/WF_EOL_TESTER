"""
Hardware Service Factory

Simple factory for creating hardware services based on configuration.
Replaces the complex dependency injection system.
"""

from typing import Dict, Any
from loguru import logger

from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.mcu import MCUService
from application.interfaces.hardware.digital_input import DigitalInputService
from application.interfaces.hardware.robot import RobotService

# Hardware implementations
from infrastructure.implementation.hardware.loadcell.bs205 import BS205LoadCell
from infrastructure.implementation.hardware.power.oda import OdaPower
from infrastructure.implementation.hardware.mcu.lma import LMAMCU
from infrastructure.implementation.hardware.digital_input.ajinextek import AjinextekInput
from infrastructure.implementation.hardware.loadcell.mock import MockLoadCell
from infrastructure.implementation.hardware.power.mock import MockPower
from infrastructure.implementation.hardware.mcu.mock import MockMCU
from infrastructure.implementation.hardware.digital_input.mock import MockInput
from infrastructure.implementation.hardware.robot.mock import MockRobot

# AJINEXTEK robot service
from infrastructure.implementation.hardware.robot.ajinextek import AjinextekRobot



class ServiceFactory:
    """하드웨어 서비스 팩토리"""

    @staticmethod
    def create_loadcell_service(config: Dict[str, Any]) -> LoadCellService:
        """
        LoadCell 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            LoadCell 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get('type', 'bs205').lower()

        if hw_type == 'mock':
            # Mock 서비스 (하드코딩된 설정 사용)
            logger.info("Creating Mock LoadCell service (base: 10.0N)")
            return MockLoadCell(
                mock_values=[],
                base_force=10.0,
                noise_level=0.1
            )

        elif hw_type == 'bs205':
            # BS205 실제 하드웨어
            logger.info(f"Creating BS205 LoadCell service on {config.get('port', 'COM3')}")
            return BS205LoadCell(
                port=config.get('port', 'COM3'),
                baudrate=config.get('baudrate', 9600),
                timeout=config.get('timeout', 1.0),
                indicator_id=config.get('indicator_id', 1)
            )

        else:
            raise ValueError(f"Unsupported loadcell type: {hw_type}")

    @staticmethod
    def create_power_service(config: Dict[str, Any]) -> PowerService:
        """
        Power 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            Power 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get('type', 'oda').lower()

        if hw_type == 'mock':
            # Mock 서비스 (하드코딩된 설정 사용)
            logger.info("Creating Mock Power service (30.0V/5.0A)")
            return MockPower(
                max_voltage=30.0,
                max_current=5.0,
                voltage_accuracy=0.01,
                current_accuracy=0.001
            )

        elif hw_type == 'oda':
            # ODA 실제 하드웨어
            logger.info(f"Creating ODA Power service at {config.get('host', '192.168.1.100')}:{config.get('port', 8080)}")
            return OdaPower(
                host=config.get('host', '192.168.1.100'),
                port=config.get('port', 8080),
                timeout=config.get('timeout', 5.0),
                channel=config.get('channel', 1)
            )

        else:
            raise ValueError(f"Unsupported power supply type: {hw_type}")

    @staticmethod
    def create_mcu_service(config: Dict[str, Any]) -> MCUService:
        """
        MCU 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            MCU 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get('type', 'lma').lower()

        if hw_type == 'mock':
            # Mock 서비스 (하드코딩된 설정 사용)
            logger.info("Creating Mock MCU service (initial: 25.0°C)")
            return MockMCU(
                initial_temperature=25.0,
                temperature_drift_rate=0.1,
                response_delay=0.1
            )

        elif hw_type == 'lma':
            # LMA 실제 하드웨어
            logger.info(f"Creating LMA MCU service on {config.get('port', 'COM4')}")
            return LMAMCU(
                port=config.get('port', 'COM4'),
                baudrate=config.get('baudrate', 115200),
                timeout=config.get('timeout', 2.0)
            )

        else:
            raise ValueError(f"Unsupported MCU type: {hw_type}")

    @staticmethod
    def create_digital_input_service(config: Dict[str, Any]) -> DigitalInputService:
        """
        Digital Input 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            Digital Input 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get('type', 'ajinextek').lower()

        if hw_type == 'mock':
            # Mock 서비스 (하드코딩된 설정 사용)
            logger.info("Creating Mock Digital Input service (32 pins)")
            return MockInput(
                total_pins=32,
                simulate_noise=False,
                noise_probability=0.01,
                response_delay_ms=5.0
            )

        elif hw_type == 'ajinextek':
            # Ajinextek DIO 실제 하드웨어
            logger.info(f"Creating Ajinextek Digital Input service on board {config.get('board_no', 0)}")
            return AjinextekInput(
                board_no=config.get('board_no', 0),
                input_count=config.get('input_count', 8),
                debounce_time=config.get('debounce_time', 0.01)
            )

        else:
            raise ValueError(f"Unsupported digital input hardware type: {hw_type}")

    @staticmethod
    def create_robot_service(config: Dict[str, Any]) -> RobotService:
        """
        Robot 서비스 생성

        Args:
            config: 하드웨어 설정

        Returns:
            Robot 서비스 인스턴스

        Raises:
            ValueError: 지원되지 않는 하드웨어 타입
        """
        hw_type = config.get('type', 'ajinextek').lower()

        if hw_type == 'mock':
            # Mock 서비스 (하드코딩된 설정 사용)
            logger.info("Creating Mock Robot service (6 axes)")
            return MockRobot(
                axis_count=6,
                max_position=1000.0,
                default_velocity=100.0,
                response_delay=0.1
            )

        elif hw_type == 'ajinextek':
            # AJINEXTEK 실제 하드웨어
            logger.info(f"Creating AJINEXTEK Robot service (IRQ: {config.get('irq_no', 7)}, {config.get('axis_count', 6)} axes)")
            return AjinextekRobot(
                # Hardware model
                model=config.get('model', 'AJINEXTEK'),

                # Connection parameters
                irq_no=config.get('irq_no', 7),
                axis_count=config.get('axis_count', 6)
            )

        else:
            raise ValueError(f"Unsupported robot hardware type: {hw_type}")
