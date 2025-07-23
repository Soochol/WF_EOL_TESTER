"""
Execute EOL Test Use Case

Simplified use case for executing End-of-Line tests.
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger

from application.interfaces.loadcell_service import LoadCellService
from application.interfaces.power_service import PowerService
from application.interfaces.robot_service import RobotService
from application.interfaces.mcu_service import MCUService
from application.interfaces.test_repository import TestRepository
from domain.entities.eol_test import EOLTest
from domain.entities.dut import DUT
from domain.enums.test_status import TestStatus
from domain.enums.test_types import TestType
from domain.value_objects.identifiers import TestId


class ExecuteEOLTestCommand:
    """EOL 테스트 실행 명령"""
    
    def __init__(
        self,
        dut_id: str,
        dut_model: str,
        dut_serial: str,
        test_type: TestType,
        operator_id: str,
        test_config: Optional[Dict[str, Any]] = None,
        pass_criteria: Optional[Dict[str, Any]] = None
    ):
        self.dut_id = dut_id
        self.dut_model = dut_model
        self.dut_serial = dut_serial
        self.test_type = test_type
        self.operator_id = operator_id
        self.test_config = test_config or {}
        self.pass_criteria = pass_criteria or {}


class EOLTestResult:
    """EOL 테스트 결과"""
    
    def __init__(
        self,
        test_id: TestId,
        status: TestStatus,
        passed: bool,
        measurements: Dict[str, float],
        duration: float,
        error_message: Optional[str] = None
    ):
        self.test_id = test_id
        self.status = status
        self.passed = passed
        self.measurements = measurements
        self.duration = duration
        self.error_message = error_message


class ExecuteEOLTestUseCase:
    """EOL 테스트 실행 Use Case"""
    
    def __init__(
        self,
        robot_service: RobotService,
        mcu_service: MCUService,
        loadcell_service: LoadCellService,
        power_service: PowerService,
        test_repository: TestRepository
    ):
        self._robot = robot_service
        self._mcu = mcu_service
        self._loadcell = loadcell_service
        self._power = power_service
        self._repository = test_repository
    
    async def execute(self, command: ExecuteEOLTestCommand) -> EOLTestResult:
        """
        EOL 테스트 실행
        
        Args:
            command: 테스트 실행 명령
            
        Returns:
            테스트 실행 결과
        """
        logger.info(f"Starting EOL test for DUT {command.dut_id}")
        
        # 테스트 엔티티 생성
        dut = DUT(
            dut_id=command.dut_id,
            model_number=command.dut_model,
            serial_number=command.dut_serial,
            manufacturer="Unknown"
        )
        
        test = EOLTest(
            test_id=TestId.generate(),
            dut=dut,
            test_type=command.test_type,
            operator_id=command.operator_id
        )
        
        # 테스트 저장
        await self._repository.save(test)
        
        measurements = {}
        start_time = asyncio.get_event_loop().time()
        
        try:
            test.start_test()
            
            # 하드웨어 연결
            await self._connect_hardware(command.test_type)
            
            # Robot 초기화 (홈 위치로 이동)
            await self._initialize_robot()
            
            # 측정 실행
            if self._requires_force_measurement(command.test_type):
                force = await self._measure_force()
                measurements['force'] = force
            
            if self._requires_power_measurement(command.test_type):
                voltage, current = await self._measure_power(command.test_config)
                measurements['voltage'] = voltage
                measurements['current'] = current
            
            # 결과 평가
            passed = self._evaluate_results(measurements, command.pass_criteria)
            
            # 테스트 완료
            if passed:
                test.complete_test()
            else:
                test.fail_test("Measurements outside acceptable range")
            
            await self._repository.update(test)
            
            duration = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"EOL test completed: {test.test_id}, passed: {passed}")
            
            return EOLTestResult(
                test_id=test.test_id,
                status=test.status,
                passed=passed,
                measurements=measurements,
                duration=duration
            )
            
        except Exception as e:
            test.fail_test(str(e))
            await self._repository.update(test)
            
            duration = asyncio.get_event_loop().time() - start_time
            
            logger.error(f"EOL test failed: {e}")
            
            return EOLTestResult(
                test_id=test.test_id,
                status=TestStatus.FAILED,
                passed=False,
                measurements=measurements,
                duration=duration,
                error_message=str(e)
            )
    
    async def _connect_hardware(self, test_type: TestType) -> None:
        """모든 필수 하드웨어 연결"""
        logger.info("Connecting all hardware components...")
        tasks = []
        hardware_names = []
        
        # Robot 연결 (모든 테스트에 필수)
        if not await self._robot.is_connected():
            tasks.append(self._robot.connect())
            hardware_names.append("Robot")
        
        # MCU 연결 (모든 테스트에 필수)
        if not await self._mcu.is_connected():
            tasks.append(self._mcu.connect())
            hardware_names.append("MCU")
        
        # Power 연결 (모든 테스트에 필수)
        if not await self._power.is_connected():
            tasks.append(self._power.connect())
            hardware_names.append("Power")
        
        # LoadCell 연결 (모든 테스트에 필수)
        if not await self._loadcell.is_connected():
            tasks.append(self._loadcell.connect())
            hardware_names.append("LoadCell")
        
        # 병렬로 연결 시도
        if tasks:
            logger.info(f"Connecting hardware: {', '.join(hardware_names)}")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 연결 결과 검증
            failed_hardware = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_hardware.append(f"{hardware_names[i]}: {str(result)}")
                elif not result:
                    failed_hardware.append(f"{hardware_names[i]}: Connection returned False")
            
            if failed_hardware:
                error_msg = f"Failed to connect hardware: {'; '.join(failed_hardware)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        
        # 연결 상태 최종 검증
        await self._verify_hardware_connections()
        logger.info("All hardware components connected successfully")
    
    async def _verify_hardware_connections(self) -> None:
        """하드웨어 연결 상태 검증"""
        connection_checks = [
            ("Robot", self._robot.is_connected()),
            ("MCU", self._mcu.is_connected()),
            ("Power", self._power.is_connected()),
            ("LoadCell", self._loadcell.is_connected())
        ]
        
        results = await asyncio.gather(*[check[1] for check in connection_checks])
        
        disconnected = []
        for i, (name, _) in enumerate(connection_checks):
            if not results[i]:
                disconnected.append(name)
        
        if disconnected:
            error_msg = f"Hardware connection verification failed: {', '.join(disconnected)} not connected"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    async def _initialize_robot(self) -> None:
        """Robot 초기화 - 홈 위치로 이동"""
        logger.info("Initializing robot - moving to home position...")
        
        try:
            # Robot 홈 위치로 이동
            success = await self._robot.home_all_axes()
            if not success:
                raise RuntimeError("Failed to move robot to home position")
            
            # 현재 위치 확인
            current_pos = await self._robot.get_current_position()
            logger.info(f"Robot initialized at home position: {current_pos}")
            
        except Exception as e:
            logger.error(f"Robot initialization failed: {e}")
            raise RuntimeError(f"Robot initialization failed: {e}")
    
    async def _measure_force(self) -> float:
        """힘 측정"""
        await self._loadcell.zero()
        await asyncio.sleep(0.1)  # 안정화 대기
        return await self._loadcell.read_force()
    
    async def _measure_power(self, config: Dict[str, Any]) -> tuple[float, float]:
        """전력 측정"""
        voltage = config.get('target_voltage', 12.0)
        current = config.get('current_limit', 1.0)
        
        await self._power.set_output(voltage, current)
        await self._power.enable_output(True)
        
        try:
            await asyncio.sleep(0.5)  # 안정화 대기
            return await self._power.measure_output()
        finally:
            await self._power.enable_output(False)  # 안전을 위해 항상 비활성화
    
    def _requires_force_measurement(self, test_type: TestType) -> bool:
        """힘 측정이 필요한지 확인"""
        return test_type in [TestType.FORCE_ONLY, TestType.COMPREHENSIVE]
    
    def _requires_power_measurement(self, test_type: TestType) -> bool:
        """전력 측정이 필요한지 확인"""
        return test_type in [TestType.ELECTRICAL_ONLY, TestType.COMPREHENSIVE]
    
    def _evaluate_results(self, measurements: Dict[str, float], criteria: Dict[str, Any]) -> bool:
        """측정 결과 평가"""
        if not criteria:
            return True  # 기준이 없으면 통과
        
        for key, criterion in criteria.items():
            if key not in measurements:
                return False
            
            value = measurements[key]
            
            if isinstance(criterion, dict):
                # 범위 기준
                if 'min' in criterion and value < criterion['min']:
                    return False
                if 'max' in criterion and value > criterion['max']:
                    return False
            else:
                # 직접 비교
                if abs(value - criterion) > 0.001:  # 허용 오차
                    return False
        
        return True