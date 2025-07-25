"""
EOL Tester Main Entry Point

Simplified main application with direct service creation.
"""

import sys
import asyncio
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from infrastructure.hardware.factory import ServiceFactory
from ui.cli.eol_tester_cli import EOLTesterCLI
from application.use_cases.eol_force_test import EOLForceTestUseCase
from application.services.hardware_service_facade import HardwareServiceFacade
from application.services.repository_service import RepositoryService
from application.services.exception_handler import ExceptionHandler
from application.services.configuration_validator import ConfigurationValidator
from application.services.test_result_evaluator import TestResultEvaluator
from infrastructure.repositories.yaml_configuration_repository import YamlConfigurationRepository
from infrastructure.repositories.json_test_repository import JsonTestRepository
from infrastructure.repositories.json_profile_preference_repository import JsonProfilePreferenceRepository

# 상수 정의
DEFAULT_CONFIG_FILE = "config.json"
DEFAULT_LOG_ROTATION = "10 MB"
DEFAULT_LOG_RETENTION = "7 days"
LOGS_DIRECTORY = "logs"
EOL_TESTER_LOG_FILE = "eol_tester.log"


def setup_logging(debug: bool = False) -> None:
    """
    로깅 설정
    
    Args:
        debug: 디버그 모드 여부
    """
    # 기본 로거 제거
    logger.remove()
    
    # 콘솔 로깅
    log_level = "DEBUG" if debug else "INFO"
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>"
    )
    
    # 파일 로깅
    logs_dir = Path(LOGS_DIRECTORY)
    logs_dir.mkdir(exist_ok=True)
    
    logger.add(
        logs_dir / EOL_TESTER_LOG_FILE,
        rotation=DEFAULT_LOG_ROTATION,
        retention=DEFAULT_LOG_RETENTION,
        compression="zip",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}"
    )


def load_config(config_file: str) -> Dict[str, Any]:
    """
    설정 파일 로드
    
    Args:
        config_file: 설정 파일 경로
        
    Returns:
        설정 딕셔너리
    """
    config_path = Path(config_file)
    
    if not config_path.exists():
        logger.info(f"Config file {config_file} not found, using default config")
        return ServiceFactory.get_default_config()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_file}")
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        sys.exit(1)


def save_config(config: Dict[str, Any], config_file: str) -> None:
    """
    설정 파일 저장
    
    Args:
        config: 설정 딕셔너리
        config_file: 저장할 파일 경로
    """
    config_path = Path(config_file)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Configuration saved to {config_file}")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        sys.exit(1)


def create_argument_parser() -> argparse.ArgumentParser:
    """명령행 인수 파서 생성"""
    parser = argparse.ArgumentParser(
        description="EOL Tester Application - Simplified Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                              # Run with default mock hardware
  python main.py --config config.json        # Run with custom configuration
  python main.py --debug                     # Enable debug logging
  python main.py --generate-config default   # Generate default config file
  python main.py --generate-config production # Generate production config file
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_FILE,
        help=f"Configuration file path (default: {DEFAULT_CONFIG_FILE})"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--generate-config",
        choices=["default", "production"],
        help="Generate configuration file and exit"
    )
    
    parser.add_argument(
        "--config-output",
        type=str,
        help="Output path for generated configuration (default: based on type)"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration file and exit"
    )
    
    return parser


async def main() -> None:
    """메인 애플리케이션 진입점"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 로깅 설정
    setup_logging(args.debug)
    
    try:
        # 설정 파일 생성 요청
        if args.generate_config:
            if args.generate_config == "default":
                config = ServiceFactory.get_default_config()
                output_file = args.config_output or "config_default.json"
            else:  # production
                config = ServiceFactory.get_production_config()
                output_file = args.config_output or "config_production.json"
            
            save_config(config, output_file)
            return
        
        # 설정 로드
        config = load_config(args.config)
        
        # 설정 검증 요청
        if args.validate_config:
            if ServiceFactory.validate_config(config):
                print("Configuration is valid")
                return
            else:
                print("Configuration validation failed")
                sys.exit(1)
        
        # 설정 검증
        if not ServiceFactory.validate_config(config):
            logger.error("Invalid configuration")
            sys.exit(1)
        
        # 서비스 생성
        logger.info("Creating EOL Tester services...")
        
        robot_service = ServiceFactory.create_robot_service(
            config['hardware']['robot']
        )
        
        mcu_service = ServiceFactory.create_mcu_service(
            config['hardware']['mcu']
        )
        
        loadcell_service = ServiceFactory.create_loadcell_service(
            config['hardware']['loadcell']
        )
        
        power_service = ServiceFactory.create_power_service(
            config['hardware']['power_supply']
        )
        
        test_repository = ServiceFactory.create_test_repository(
            config.get('repository', {})
        )
        
        # Create repositories
        configuration_repository = YamlConfigurationRepository()
        profile_preference_repository = JsonProfilePreferenceRepository()
        
        # Create repository service
        repository_service = RepositoryService(
            test_repository=test_repository,
            configuration_repository=configuration_repository,
            profile_preference_repository=profile_preference_repository
        )
        
        # Create individual business services
        exception_handler = ExceptionHandler()
        configuration_validator = ConfigurationValidator()
        test_result_evaluator = TestResultEvaluator()
        
        # Create hardware services facade
        hardware_services = HardwareServiceFacade(
            robot_service=robot_service,
            mcu_service=mcu_service,
            loadcell_service=loadcell_service,
            power_service=power_service
        )
        
        # Use Case 생성
        use_case = EOLForceTestUseCase(
            hardware_services=hardware_services,
            repository_service=repository_service,
            exception_handler=exception_handler,
            configuration_validator=configuration_validator,
            test_result_evaluator=test_result_evaluator
        )
        
        # CLI 생성 및 실행
        cli = EOLTesterCLI(use_case)
        logger.info("Starting EOL Tester application")
        
        await cli.run_interactive()
        
        logger.info("EOL Tester application finished")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Python 3.7+ 호환성을 위해 asyncio.run 사용
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nExiting...")
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)