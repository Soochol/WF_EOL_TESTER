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
from application.interfaces.mcu_service import MCUService, TestMode
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
            
            # 1. Setup 단계
            await self._setup(command)
            
            # 2. Main Test 단계
            measurements = await self._main_test(command)
            
            # 3. Clean Up 단계 (성공 시)
            await self._clean_up()
            
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
            # Clean Up 단계 (실패 시)
            try:
                await self._clean_up()
            except Exception as cleanup_error:
                logger.error(f"Cleanup after failure also failed: {cleanup_error}")
            
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
        """테스트 타입에 따라 필요한 하드웨어 연결"""
        logger.info(f"Connecting hardware for {test_type.value}...")
        tasks = []
        hardware_names = []
        
        # Robot 연결 (항상 필요)
        if not await self._robot.is_connected():
            tasks.append(self._robot.connect())
            hardware_names.append("Robot")
        
        # MCU 연결 (항상 필요)
        if not await self._mcu.is_connected():
            tasks.append(self._mcu.connect())
            hardware_names.append("MCU")
        
        # Power 연결 (항상 필요)
        if not await self._power.is_connected():
            tasks.append(self._power.connect())
            hardware_names.append("Power")
        
        # LoadCell 연결 (항상 필요)
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
        """모든 하드웨어 연결 상태 검증"""
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
    
    async def _setup(self, command: ExecuteEOLTestCommand) -> None:
        """
        테스트 준비 단계
        - 하드웨어 연결
        - Robot 초기화
        - Power 초기화 및 ON
        - MCU 부팅 완료 신호 대기
        - 테스트모드 1 진입
        """
        logger.info("Starting test setup...")
        
        # 1. 하드웨어 연결
        await self._connect_hardware(command.test_type)
        
        # 2. Robot 초기화 (항상 실행)
        await self._initialize_robot()
        
        # 3. Power 초기화 및 ON (항상 실행)
        voltage = command.test_config.get('target_voltage', 18.0)
        current = command.test_config.get('current_limit', 20.0)
        await self._power.set_output(voltage, current)
        await self._power.enable_output(True)
        logger.info(f"Power enabled: {voltage}V, {current}A")
        
        # 4. MCU 부팅 완료 신호 대기 (항상 실행)
        await self._wait_mcu_ready()
        
        # 5. 테스트모드 1 진입 (항상 실행)
        await self._mcu.set_test_mode(TestMode.MODE_1)
        logger.info("DUT set to test mode 1")
        
        logger.info("Test setup completed")
    
    async def _wait_mcu_ready(self) -> None:
        """MCU 부팅 완료 신호 대기"""
        logger.info("Waiting for MCU boot complete signal...")
        try:
            await self._mcu.wait_for_boot_complete()
            logger.info("MCU boot complete signal received")
        except Exception as e:
            logger.error(f"MCU boot complete wait failed: {e}")
            raise RuntimeError(f"MCU boot complete timeout: {e}")
    
    async def _main_test(self, command: ExecuteEOLTestCommand) -> Dict[str, float]:
        """
        메인 테스트 실행
        - 상한온도 설정
        - Force up (테스트 동작 온도) 설정
        - Robot 스트로크 이동
        - LoadCell 측정
        - (Robot 스트로크 이동 - LoadCell 측정 반복)
        - Force up (동작 온도 설정)
        - 스트로크 대기 위치 이동
        - Force down (대기온도 설정)
        """
        logger.info("Starting main test...")
        measurements = {}
        
        try:
            # 1. 상한온도 설정 (예: 85도)
            upper_temp = command.test_config.get('upper_temperature', 85.0)
            logger.info(f"Setting upper temperature: {upper_temp}°C")
            # TODO: MCU에 상한온도 설정 메서드 필요
            
            # 2. Force up (테스트 동작 온도) 설정
            test_temp = command.test_config.get('test_temperature', 25.0)
            logger.info(f"Setting test temperature: {test_temp}°C")
            # TODO: MCU에 동작온도 설정 메서드 필요
            
            # 3. Robot 스트로크 이동 및 LoadCell 측정 반복
            stroke_positions = command.test_config.get('stroke_positions', [0.0, 10.0, 20.0])
            force_measurements = []
            
            for i, position in enumerate(stroke_positions):
                logger.info(f"Moving robot to stroke position {i+1}: {position}mm")
                
                # Robot을 지정된 위치로 이동 (항상 실행)
                await self._move_robot_to_position(position)
                await asyncio.sleep(0.5)  # 안정화 대기
                
                # LoadCell 측정 (항상 실행)
                force = await self._measure_force()
                force_measurements.append(force)
                logger.info(f"Force measurement at position {position}mm: {force}N")
                
                # 잠시 대기
                await asyncio.sleep(0.2)
            
            # 측정값 평균 계산
            if force_measurements:
                measurements['force'] = sum(force_measurements) / len(force_measurements)
                measurements['force_max'] = max(force_measurements)
                measurements['force_min'] = min(force_measurements)
            
            # 4. 전력 측정 (항상 실행)
            voltage, current = await self._measure_power(command.test_config)
            measurements['voltage'] = voltage
            measurements['current'] = current
            
            # 5. 스트로크 대기 위치로 이동 (항상 실행)
            standby_position = command.test_config.get('standby_position', 0.0)
            logger.info(f"Moving robot to standby position: {standby_position}mm")
            await self._move_robot_to_position(standby_position)
            
            # 6. Force down (대기온도) 설정
            standby_temp = command.test_config.get('standby_temperature', 20.0)
            logger.info(f"Setting standby temperature: {standby_temp}°C")
            # TODO: MCU에 대기온도 설정 메서드 필요
            
            logger.info("Main test completed")
            return measurements
            
        except Exception as e:
            logger.error(f"Main test failed: {e}")
            raise
    
    async def _move_robot_to_position(self, position: float) -> None:
        """Robot을 지정된 위치로 이동"""
        logger.debug(f"Moving robot to position: {position}mm")
        # TODO: Robot 서비스에 위치 이동 메서드 구현 필요
        # 임시로 현재 위치 가져오기만 수행
        current_pos = await self._robot.get_current_position()
        logger.debug(f"Current robot position: {current_pos}")
        # 실제 구현에서는 await self._robot.move_to_position(position) 같은 메서드 호출
    
    async def _clean_up(self) -> None:
        """
        테스트 정리 단계
        - Power OFF
        - 하드웨어 연결 해제
        """
        logger.info("Starting test cleanup...")
        
        try:
            # 1. Power OFF
            try:
                if await self._power.is_connected():
                    await self._power.enable_output(False)
                    logger.info("Power output disabled")
            except Exception as e:
                logger.warning(f"Failed to disable power output: {e}")
            
            # 2. 하드웨어 연결 해제 (역순으로)
            disconnect_tasks = []
            hardware_names = []
            
            # LoadCell 연결 해제
            try:
                if await self._loadcell.is_connected():
                    disconnect_tasks.append(self._loadcell.disconnect())
                    hardware_names.append("LoadCell")
            except Exception as e:
                logger.warning(f"LoadCell disconnect preparation failed: {e}")
            
            # Power 연결 해제
            try:
                if await self._power.is_connected():
                    disconnect_tasks.append(self._power.disconnect())
                    hardware_names.append("Power")
            except Exception as e:
                logger.warning(f"Power disconnect preparation failed: {e}")
            
            # MCU 연결 해제
            try:
                if await self._mcu.is_connected():
                    disconnect_tasks.append(self._mcu.disconnect())
                    hardware_names.append("MCU")
            except Exception as e:
                logger.warning(f"MCU disconnect preparation failed: {e}")
            
            # Robot 연결 해제
            try:
                if await self._robot.is_connected():
                    disconnect_tasks.append(self._robot.disconnect())
                    hardware_names.append("Robot")
            except Exception as e:
                logger.warning(f"Robot disconnect preparation failed: {e}")
            
            # 병렬로 연결 해제 시도
            if disconnect_tasks:
                logger.info(f"Disconnecting hardware: {', '.join(hardware_names)}")
                results = await asyncio.gather(*disconnect_tasks, return_exceptions=True)
                
                # 연결 해제 결과 확인
                failed_disconnects = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        failed_disconnects.append(f"{hardware_names[i]}: {str(result)}")
                    elif not result:
                        failed_disconnects.append(f"{hardware_names[i]}: Disconnect returned False")
                
                if failed_disconnects:
                    logger.warning(f"Some hardware disconnections failed: {'; '.join(failed_disconnects)}")
                else:
                    logger.info("All hardware disconnected successfully")
            
            logger.info("Test cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            # 정리 실패해도 예외를 다시 발생시키지 않음 (이미 테스트는 완료된 상태)