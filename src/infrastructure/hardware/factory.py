"""
Hardware Service Factory

Simple factory for creating hardware services based on configuration.
Replaces the complex dependency injection system.
"""

from typing import Dict, Any, Optional
from loguru import logger

from application.interfaces.loadcell import LoadCellService
from application.interfaces.power import PowerService
from application.interfaces.mcu import MCUService
from application.interfaces.digital_input import DigitalInputService
from application.interfaces.robot import RobotService
from application.interfaces.test_repository import TestRepository

# Hardware implementations
from infrastructure.hardware.loadcell.bs205 import BS205LoadCellAdapter
from infrastructure.hardware.power.oda import OdaPowerAdapter
from infrastructure.hardware.mcu.lma import LMAMCUAdapter
from infrastructure.hardware.digital_input.ajinextek import AjinextekInputAdapter
from infrastructure.hardware.loadcell.mock import MockLoadCellAdapter
from infrastructure.hardware.power.mock import MockPowerAdapter
from infrastructure.hardware.mcu.mock import MockMCUAdapter
from infrastructure.hardware.digital_input.mock import MockInputAdapter
from infrastructure.hardware.robot import MockRobotAdapter

# Try to import AJINEXTEK robot service
try:
    from infrastructure.hardware.robot import AjinextekRobotAdapter
    _AJINEXTEK_ROBOT_AVAILABLE = True
except ImportError:
    _AJINEXTEK_ROBOT_AVAILABLE = False

# Repository implementations
from infrastructure.repositories.json_test_repository import JsonTestRepository


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
            # Mock 서비스
            mock_values = config.get('mock_values', [])
            base_force = config.get('base_force', 10.0)
            noise_level = config.get('noise_level', 0.1)
            
            logger.info(f"Creating Mock LoadCell service (base: {base_force}N)")
            return MockLoadCellAdapter(
                mock_values=mock_values,
                base_force=base_force,
                noise_level=noise_level
            )
            
        elif hw_type == 'bs205':
            # BS205 실제 하드웨어
            connection = config.get('connection', {})
            port = connection.get('port', 'COM3')
            baudrate = connection.get('baudrate', 9600)
            timeout = connection.get('timeout', 1.0)
            indicator_id = connection.get('indicator_id', 1)
            
            logger.info(f"Creating BS205 LoadCell service on {port}")
            return BS205LoadCellAdapter(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                indicator_id=indicator_id
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
            # Mock 서비스
            max_voltage = config.get('max_voltage', 30.0)
            max_current = config.get('max_current', 5.0)
            voltage_accuracy = config.get('voltage_accuracy', 0.01)
            current_accuracy = config.get('current_accuracy', 0.001)
            
            logger.info(f"Creating Mock Power service ({max_voltage}V/{max_current}A)")
            return MockPowerAdapter(
                max_voltage=max_voltage,
                max_current=max_current,
                voltage_accuracy=voltage_accuracy,
                current_accuracy=current_accuracy
            )
            
        elif hw_type == 'oda':
            # ODA 실제 하드웨어
            connection = config.get('connection', {})
            host = connection.get('host', '192.168.1.100')
            port = connection.get('port', 8080)
            timeout = connection.get('timeout', 5.0)
            channel = connection.get('channel', 1)
            
            logger.info(f"Creating ODA Power service at {host}:{port}")
            return OdaPowerAdapter(
                host=host,
                port=port,
                timeout=timeout,
                channel=channel
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
            # Mock 서비스
            initial_temperature = config.get('initial_temperature', 25.0)
            temperature_drift_rate = config.get('temperature_drift_rate', 0.1)
            response_delay = config.get('response_delay', 0.1)
            
            logger.info(f"Creating Mock MCU service (initial: {initial_temperature}°C)")
            return MockMCUAdapter(
                initial_temperature=initial_temperature,
                temperature_drift_rate=temperature_drift_rate,
                response_delay=response_delay
            )
            
        elif hw_type == 'lma':
            # LMA 실제 하드웨어
            connection = config.get('connection', {})
            port = connection.get('port', 'COM3')
            baudrate = connection.get('baudrate', 9600)
            timeout = connection.get('timeout', 5.0)
            
            logger.info(f"Creating LMA MCU service on {port}")
            return LMAMCUAdapter(
                port=port,
                baudrate=baudrate,
                timeout=timeout
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
            # Mock 서비스
            total_pins = config.get('total_pins', 32)
            simulate_noise = config.get('simulate_noise', False)
            noise_probability = config.get('noise_probability', 0.01)
            response_delay_ms = config.get('response_delay_ms', 5.0)
            
            logger.info(f"Creating Mock Digital Input service ({total_pins} pins)")
            return MockInputAdapter(
                total_pins=total_pins,
                simulate_noise=simulate_noise,
                noise_probability=noise_probability,
                response_delay_ms=response_delay_ms
            )
            
        elif hw_type == 'ajinextek':
            # Ajinextek DIO 실제 하드웨어
            connection = config.get('connection', {})
            board_number = connection.get('board_number', 0)
            module_position = connection.get('module_position', 0)
            signal_type = connection.get('signal_type', 2)  # 24V industrial
            debounce_time_ms = connection.get('debounce_time_ms', 10)
            retry_count = connection.get('retry_count', 3)
            auto_initialize = connection.get('auto_initialize', True)
            
            logger.info(f"Creating Ajinextek Digital Input service on board {board_number}")
            return AjinextekInputAdapter(
                board_number=board_number,
                module_position=module_position,
                signal_type=signal_type,
                debounce_time_ms=debounce_time_ms,
                retry_count=retry_count,
                auto_initialize=auto_initialize
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
            # Mock 서비스
            axis_count = config.get('axis_count', 6)
            max_position = config.get('max_position', 1000.0)
            default_velocity = config.get('default_velocity', 100.0)
            response_delay = config.get('response_delay', 0.1)
            
            logger.info(f"Creating Mock Robot service ({axis_count} axes)")
            return MockRobotAdapter(
                axis_count=axis_count,
                max_position=max_position,
                default_velocity=default_velocity,
                response_delay=response_delay
            )
            
        elif hw_type == 'ajinextek':
            if not _AJINEXTEK_ROBOT_AVAILABLE:
                logger.warning("AJINEXTEK robot service not available, falling back to Mock")
                return ServiceFactory.create_robot_service({'type': 'mock', **config})
            
            # AJINEXTEK 실제 하드웨어
            connection = config.get('connection', {})
            irq_no = connection.get('irq_no', 7)
            axis_count = connection.get('axis_count', 6)
            default_velocity = connection.get('default_velocity', 100.0)
            default_acceleration = connection.get('default_acceleration', 100.0)
            
            logger.info(f"Creating AJINEXTEK Robot service (IRQ: {irq_no}, {axis_count} axes)")
            return AjinextekRobotAdapter(
                irq_no=irq_no,
                axis_count=axis_count,
                default_velocity=default_velocity,
                default_acceleration=default_acceleration
            )
        
        else:
            raise ValueError(f"Unsupported robot hardware type: {hw_type}")
    
    @staticmethod
    def create_test_repository(config: Optional[Dict[str, Any]] = None) -> TestRepository:
        """
        Test Repository 생성
        
        Args:
            config: 저장소 설정
            
        Returns:
            Test Repository 인스턴스
        """
        if config is None:
            config = {}
        
        repo_type = config.get('type', 'json').lower()
        
        if repo_type == 'json':
            # JSON 파일 기반 저장소
            data_dir = config.get('data_dir', 'data/tests')
            auto_save = config.get('auto_save', True)
            
            logger.info(f"Creating JSON Test repository in {data_dir}")
            return JsonTestRepository(
                data_dir=data_dir,
                auto_save=auto_save
            )
        
        else:
            raise ValueError(f"Unsupported repository type: {repo_type}")
    
    @staticmethod
    def create_application(config: Dict[str, Any]) -> 'EOLTesterApplication':
        """
        전체 애플리케이션 생성
        
        Args:
            config: 애플리케이션 설정
            
        Returns:
            EOL 테스터 애플리케이션 인스턴스
        """
        hardware_config = config.get('hardware', {})
        repository_config = config.get('repository', {})
        
        # 서비스 생성
        loadcell = ServiceFactory.create_loadcell_service(
            hardware_config.get('loadcell', {})
        )
        
        power = ServiceFactory.create_power_service(
            hardware_config.get('power_supply', {})
        )
        
        repository = ServiceFactory.create_test_repository(repository_config)
        
        # 애플리케이션 구성
        from application.use_cases.eol_force_test import EOLForceTestUseCase
        from ui.cli.eol_tester_cli import EOLTesterCLI
        
        use_case = EOLForceTestUseCase(
            loadcell_service=loadcell,
            power_service=power,
            test_repository=repository
        )
        
        cli = EOLTesterCLI(use_case)
        
        logger.info("EOL Tester application created successfully")
        return cli
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        설정 유효성 검증
        
        Args:
            config: 검증할 설정
            
        Returns:
            유효성 여부
        """
        try:
            hardware = config.get('hardware', {})
            
            # LoadCell 설정 검증
            loadcell_config = hardware.get('loadcell', {})
            loadcell_type = loadcell_config.get('type', 'bs205')
            
            if loadcell_type == 'bs205':
                connection = loadcell_config.get('connection', {})
                if not connection.get('port'):
                    raise ValueError("BS205 requires port configuration")
            
            # Power 설정 검증
            power_config = hardware.get('power_supply', {})
            power_type = power_config.get('type', 'oda')
            
            if power_type == 'oda':
                connection = power_config.get('connection', {})
                if not connection.get('host'):
                    raise ValueError("ODA requires host configuration")
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """
        기본 설정 반환
        
        Returns:
            기본 설정 딕셔너리
        """
        return {
            'hardware': {
                'loadcell': {
                    'type': 'mock',
                    'base_force': 10.0,
                    'noise_level': 0.1
                },
                'power_supply': {
                    'type': 'mock',
                    'max_voltage': 30.0,
                    'max_current': 5.0
                },
                'mcu': {
                    'type': 'mock',
                    'initial_temperature': 25.0,
                    'temperature_drift_rate': 0.1,
                    'response_delay': 0.1
                },
                'digital_input': {
                    'type': 'mock',
                    'total_pins': 32,
                    'simulate_noise': False,
                    'noise_probability': 0.01,
                    'response_delay_ms': 5.0
                },
                'robot': {
                    'type': 'mock',
                    'axis_count': 6,
                    'max_position': 1000.0,
                    'default_velocity': 100.0,
                    'response_delay': 0.1
                }
            },
            'repository': {
                'type': 'json',
                'data_dir': 'data/tests',
                'auto_save': True
            },
            'application': {
                'test_timeout': 300,
                'measurement_precision': 3,
                'auto_connect': True
            }
        }
    
    @staticmethod
    def get_production_config() -> Dict[str, Any]:
        """
        프로덕션 설정 반환
        
        Returns:
            프로덕션 설정 딕셔너리
        """
        return {
            'hardware': {
                'loadcell': {
                    'type': 'bs205',
                    'connection': {
                        'port': 'COM1',
                        'baudrate': 9600,
                        'timeout': 1.0,
                        'indicator_id': 1
                    }
                },
                'power_supply': {
                    'type': 'oda',
                    'connection': {
                        'host': '192.168.1.10',
                        'port': 8080,
                        'timeout': 5.0,
                        'channel': 1
                    }
                },
                'mcu': {
                    'type': 'lma',
                    'connection': {
                        'port': 'COM2',
                        'baudrate': 9600,
                        'timeout': 5.0
                    }
                },
                'digital_input': {
                    'type': 'ajinextek',
                    'connection': {
                        'board_number': 0,
                        'module_position': 0,
                        'signal_type': 2,
                        'debounce_time_ms': 10,
                        'retry_count': 3,
                        'auto_initialize': True
                    }
                },
                'robot': {
                    'type': 'ajinextek',
                    'connection': {
                        'irq_no': 7,
                        'axis_count': 6,
                        'default_velocity': 100.0,
                        'default_acceleration': 100.0
                    }
                }
            },
            'repository': {
                'type': 'json',
                'data_dir': 'data/production',
                'auto_save': True
            },
            'application': {
                'test_timeout': 300,
                'measurement_precision': 3,
                'auto_connect': False  # 프로덕션에서는 수동 연결
            }
        }