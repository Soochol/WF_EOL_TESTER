"""
EOL Tester Main Entry Point

Simplified main application with direct service creation.
"""

import sys
import asyncio
from pathlib import Path
from loguru import logger

from src.infrastructure.factory import ServiceFactory
from src.ui.cli.eol_tester_cli import EOLTesterCLI
from src.application.use_cases.eol_force_test import EOLForceTestUseCase
from src.application.services.hardware_service_facade import HardwareServiceFacade
from src.application.services.repository_service import RepositoryService
from src.application.services.configuration_service import ConfigurationService
from src.application.services.exception_handler import ExceptionHandler
from src.application.services.configuration_validator import ConfigurationValidator
from src.application.services.test_result_evaluator import TestResultEvaluator
from src.infrastructure.implementation.configuration.yaml_configuration import YamlConfiguration
from src.infrastructure.implementation.repositories.json_result_repository import JsonResultRepository
from src.infrastructure.implementation.configuration.json_profile_preference import JsonProfilePreference

# 상수 정의
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




async def main() -> None:
    """메인 애플리케이션 진입점"""
    # 로깅 설정 (기본값 사용)
    setup_logging(debug=False)
    
    try:
        # 서비스 생성 (기본 설정 사용)
        logger.info("Creating EOL Tester services...")
        
        # Create hardware services with default configuration
        robot_service = ServiceFactory.create_robot_service({'type': 'mock'})
        mcu_service = ServiceFactory.create_mcu_service({'type': 'mock'})
        loadcell_service = ServiceFactory.create_loadcell_service({'type': 'mock'})
        power_service = ServiceFactory.create_power_service({'type': 'mock'})
        
        # Create repositories
        yaml_configuration = YamlConfiguration()
        profile_preference = JsonProfilePreference()
        test_result_repository = JsonResultRepository()
        
        # Create services
        configuration_service = ConfigurationService(
            configuration=yaml_configuration,
            profile_preference=profile_preference
        )
        
        test_result_service = RepositoryService(
            test_repository=test_result_repository
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
            hardware_services = hardware_services,
            configuration_service = configuration_service,
            configuration_validator = configuration_validator,
            repository_service = test_result_service,
            test_result_evaluator = test_result_evaluator,
            exception_handler = exception_handler,
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