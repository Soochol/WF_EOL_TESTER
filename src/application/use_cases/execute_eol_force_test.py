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
from application.interfaces.configuration_service import ConfigurationService
from application.services.exception_handler import ExceptionHandler
from domain.entities.eol_test import EOLTest
from domain.entities.dut import DUT
from domain.enums.test_status import TestStatus
from domain.enums.test_types import TestType
from domain.value_objects.identifiers import TestId
from domain.value_objects.test_configuration import TestConfiguration
from domain.exceptions.configuration_exceptions import InvalidConfigurationException
from domain.exceptions.test_exceptions import TestExecutionException


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
    """EOL Test Execution Use Case with Configuration Management"""
    
    def __init__(
        self,
        robot_service: RobotService,
        mcu_service: MCUService,
        loadcell_service: LoadCellService,
        power_service: PowerService,
        test_repository: TestRepository,
        configuration_service: ConfigurationService,
        exception_handler: ExceptionHandler
    ):
        self._robot = robot_service
        self._mcu = mcu_service
        self._loadcell = loadcell_service
        self._power = power_service
        self._repository = test_repository
        self._config_service = configuration_service
        self._exception_handler = exception_handler
        self._config: Optional[TestConfiguration] = None
    
    async def execute(self, command: ExecuteEOLTestCommand) -> EOLTestResult:
        """
        EOL 테스트 실행
        
        Args:
            command: 테스트 실행 명령
            
        Returns:
            테스트 실행 결과
        """
        logger.info(f"Starting EOL test for DUT {command.dut_id}")
        
        # Load and validate configuration first
        await self._load_configuration(command)
        
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
            
            # Evaluate results
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
        
        finally:
            # 3. Clean Up phase (always executed)
            try:
                await self._clean_up()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")
    
    async def _load_configuration(self, command: ExecuteEOLTestCommand) -> None:
        """
        Load and validate test configuration
        
        Args:
            command: Test execution command containing configuration options
            
        Raises:
            InvalidConfigurationException: If configuration is invalid
        """
        try:
            # Get profile name from command or use default
            profile_name = command.test_config.get('profile', 'default')
            
            # Load base configuration from profile
            base_config = await self._config_service.load_profile(profile_name)
            
            # Merge with runtime overrides
            if command.test_config:
                # Remove 'profile' key from overrides as it's not a config parameter
                overrides = {k: v for k, v in command.test_config.items() if k != 'profile'}
                if overrides:
                    self._config = await self._config_service.merge_configurations(base_config, overrides)
                else:
                    self._config = base_config
            else:
                self._config = base_config
            
            # Validate final configuration
            if not await self._config_service.validate_configuration(self._config):
                validation_errors = await self._config_service.get_validation_errors(self._config)
                raise InvalidConfigurationException(
                    parameter_name="merged_configuration",
                    invalid_value=str(command.test_config),
                    validation_rule="; ".join(validation_errors),
                    config_source=f"profile:{profile_name}"
                )
            
            logger.info(f"Configuration loaded: profile '{profile_name}', {self._config.get_total_measurement_points()} measurement points")
            
        except Exception as e:
            if isinstance(e, InvalidConfigurationException):
                raise
            raise TestExecutionException(
                f"Failed to load configuration: {str(e)}",
                details={"profile_name": command.test_config.get('profile', 'default')}
            )
    
    async def _connect_hardware(self, test_type: TestType) -> None:
        """Connect required hardware based on test type"""
        logger.info(f"Connecting hardware for {test_type.value}...")
        tasks = []
        hardware_names = []
        
        # Robot connection (always required)
        if not await self._robot.is_connected():
            tasks.append(self._robot.connect())
            hardware_names.append("Robot")
        
        # MCU connection (always required)
        if not await self._mcu.is_connected():
            tasks.append(self._mcu.connect())
            hardware_names.append("MCU")
        
        # Power connection (always required)
        if not await self._power.is_connected():
            tasks.append(self._power.connect())
            hardware_names.append("Power")
        
        # LoadCell connection (always required)
        if not await self._loadcell.is_connected():
            tasks.append(self._loadcell.connect())
            hardware_names.append("LoadCell")
        
        # Execute parallel connections
        if tasks:
            logger.info(f"Connecting hardware: {', '.join(hardware_names)}")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify connection results
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
        
        # Final connection status verification
        await self._verify_hardware_connections()
        logger.info("All hardware components connected successfully")
    
    async def _verify_hardware_connections(self) -> None:
        """Verify all hardware connection status"""
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
        """Initialize robot - move to home position"""
        logger.info("Initializing robot - moving to home position...")
        
        try:
            # Move robot to home position
            success = await self._robot.home_all_axes()
            if not success:
                raise RuntimeError("Failed to move robot to home position")
            
            # Verify current position
            current_pos = await self._robot.get_current_position()
            logger.info(f"Robot initialized at home position: {current_pos}")
            
        except Exception as e:
            logger.error(f"Robot initialization failed: {e}")
            raise RuntimeError(f"Robot initialization failed: {e}")
    
    async def _measure_force(self) -> float:
        """Measure force"""
        await self._loadcell.zero()
        await asyncio.sleep(self._config.loadcell_zero_delay)  # Stabilization wait
        return await self._loadcell.read_force()
    
    async def _measure_power(self) -> tuple[float, float]:
        """Measure power using current configuration"""
        voltage = self._config.voltage
        current = self._config.current
        
        await self._power.set_output(voltage, current)
        await self._power.enable_output(True)
        
        try:
            await asyncio.sleep(self._config.power_stabilization)  # Stabilization wait
            return await self._power.measure_output()
        finally:
            await self._power.enable_output(False)  # Always disable for safety
    
    
    def _evaluate_results(self, measurements: Dict[str, float], criteria: Dict[str, Any]) -> bool:
        """Evaluate measurement results"""
        if not criteria:
            return True  # Pass if no criteria
        
        for key, criterion in criteria.items():
            if key not in measurements:
                return False
            
            value = measurements[key]
            
            if isinstance(criterion, dict):
                # Range criteria
                if 'min' in criterion and value < criterion['min']:
                    return False
                if 'max' in criterion and value > criterion['max']:
                    return False
            else:
                # Direct comparison
                if abs(value - criterion) > self._config.measurement_tolerance:  # Use configured tolerance
                    return False
        
        return True
    
    async def _setup(self, command: ExecuteEOLTestCommand) -> None:
        """
        Test setup phase
        - Connect hardware
        - Initialize Robot
        - Initialize and enable Power
        - Wait for MCU boot complete signal
        - Enter test mode 1
        """
        logger.info("Starting test setup...")
        
        try:
            # Connect hardware
            await self._connect_hardware(command.test_type)
            
            # LoadCell zeroing
            await self._loadcell.zero()
            logger.info("LoadCell zeroed")

            # Robot initialization (always executed)
            await self._initialize_robot()
            
            # Power initialization and ON (always executed)
            voltage = self._config.voltage
            current = self._config.current
            await self._power.set_output(voltage, current)
            await self._power.enable_output(True)
            logger.info(f"Power enabled: {voltage}V, {current}A")
            
            # Wait for MCU boot complete signal (always executed)
            await self._wait_mcu_ready()
            
            # Enter test mode 1 (always executed)
            await self._mcu.set_test_mode(TestMode.MODE_1)
            logger.info("MCU set to test mode 1")
            
            # MCU configuration (upper temperature, fan speed)
            upper_temp = self._config.upper_temperature
            fan_speed = self._config.fan_speed

            await self._mcu.set_upper_temperature(upper_temp)
            await self._mcu.set_fan_speed(fan_speed)
            logger.info(f"MCU configured: upper_temp={upper_temp}°C, fan_speed={fan_speed}%")

            # Set LMA standby sequence
            await self._set_LMA_standby(command)

            logger.info("Test setup completed")
            
        except Exception as e:
            logger.error(f"Setup failed: {str(e)}")
            raise
    
    async def _set_LMA_standby(self, command: ExecuteEOLTestCommand = None) -> None:
        """Set LMA standby sequence"""
        # MCU start standby heating
        await self._mcu.start_standby_heating()
        logger.info("MCU standby heating started")

        # Robot to max stroke position
        max_stroke = self._config.max_stroke
        await self._robot.move_to_position(max_stroke)
        logger.info(f"Robot moved to max stroke position: {max_stroke}mm")

        # Robot to initial position
        initial_position = self._config.initial_position
        await self._robot.move_to_position(initial_position)
        logger.info(f"Robot moved to initial position: {initial_position}mm")

        # MCU start standby cooling
        await self._mcu.start_standby_cooling()
        logger.info("MCU standby cooling started")
    
    async def _wait_mcu_ready(self) -> None:
        """Wait for MCU boot complete signal"""
        logger.info("Waiting for MCU boot complete signal...")
        try:
            await self._mcu.wait_for_boot_complete()
            logger.info("MCU boot complete signal received")
        except Exception as e:
            logger.error(f"MCU boot complete wait failed: {e}")
            raise RuntimeError(f"MCU boot complete timeout: {e}")
    
    async def _main_test(self, command: ExecuteEOLTestCommand) -> Dict[str, float]:
        """
        Main test execution
        - For each temperature in list:
          - Set MCU upper temperature
          - Set MCU operating temperature
          - For each stroke position:
            - Move robot to position
            - Measure force
        """
        logger.info("Starting main test...")
        measurements = {}
        all_measurements = []
        
        # Get test parameters from configuration
        temperature_list = self._config.temperature_list
        stroke_positions = self._config.stroke_positions
        upper_temp = self._config.upper_temperature
        
        try:
            # Temperature loop
            for temp_idx, temperature in enumerate(temperature_list):
                logger.info(f"Testing at temperature {temp_idx+1}/{len(temperature_list)}: {temperature}°C")
                
                # Set upper temperature
                await self._mcu.set_upper_temperature(upper_temp)
                logger.info(f"Upper temperature set to: {upper_temp}°C")
                
                # Set operating temperature
                await self._mcu.set_temperature(temperature)
                logger.info(f"Operating temperature set to: {temperature}°C")
                await asyncio.sleep(self._config.temperature_stabilization)  # Wait for temperature stabilization
                
                # Stroke position loop
                for pos_idx, position in enumerate(stroke_positions):
                    logger.info(f"Moving to position {pos_idx+1}/{len(stroke_positions)}: {position}mm")
                    
                    # Move robot
                    await self._robot.move_to_position(position)
                    await asyncio.sleep(self._config.stabilization_delay)  # Stabilization
                    
                    # Measure force
                    await self._loadcell.zero()
                    await asyncio.sleep(self._config.loadcell_zero_delay)
                    force = await self._loadcell.read_force()
                    
                    # Store measurement
                    measurement = {
                        'temperature': temperature,
                        'position': position,
                        'force': force
                    }
                    all_measurements.append(measurement)
                    logger.info(f"Force at {temperature}°C, {position}mm: {force}N")
            
            # Store all measurements
            measurements['all_measurements'] = all_measurements
            
            # Move to standby position
            standby_position = self._config.standby_position
            await self._robot.move_to_position(standby_position)
            logger.info(f"Robot moved to standby position: {standby_position}mm")
            
            logger.info("Main test completed")
            return measurements
            
        except Exception as e:
            logger.error(f"Main test failed: {e}")
            raise
    
        # 실제 구현에서는 await self._robot.move_to_position(position) 같은 메서드 호출
    
    async def _clean_up(self) -> None:
        """
        Test cleanup phase
        - Move robot to safe position
        - Power OFF
        - Disconnect hardware
        """
        logger.info("Starting test cleanup...")
        
        # 1. Move robot to safe position and set MCU standby
        try:
            await self._set_LMA_standby()
        except Exception as e:
            logger.warning(f"Failed to set LMA standby: {e}")
        
        # 2. Power OFF
        try:
            await self._disable_power_output()
        except Exception as e:
            logger.warning(f"Failed to disable power output: {e}")
        
        # 3. Disconnect all hardware
        try:
            await self._disconnect_hardware()
        except Exception as e:
            logger.warning(f"Failed to disconnect hardware: {e}")
        
        logger.info("Test cleanup completed")
        # No exception re-raising - cleanup is best effort
    
    async def _disable_power_output(self) -> None:
        """Disable power output safely"""
        try:
            if await self._power.is_connected():
                await self._power.enable_output(False)
                logger.info("Power output disabled")
        except Exception as e:
            logger.warning(f"Failed to disable power output: {e}")
    
    async def _disconnect_hardware(self) -> None:
        """Disconnect all hardware components"""
        # Hardware disconnection (in reverse order)
        disconnect_tasks = []
        hardware_names = []
        
        # LoadCell disconnection
        try:
            if await self._loadcell.is_connected():
                disconnect_tasks.append(self._loadcell.disconnect())
                hardware_names.append("LoadCell")
        except Exception as e:
            logger.warning(f"LoadCell disconnect preparation failed: {e}")
        
        # Power disconnection
        try:
            if await self._power.is_connected():
                disconnect_tasks.append(self._power.disconnect())
                hardware_names.append("Power")
        except Exception as e:
            logger.warning(f"Power disconnect preparation failed: {e}")
        
        # MCU disconnection
        try:
            if await self._mcu.is_connected():
                disconnect_tasks.append(self._mcu.disconnect())
                hardware_names.append("MCU")
        except Exception as e:
            logger.warning(f"MCU disconnect preparation failed: {e}")
        
        # Robot disconnection
        try:
            if await self._robot.is_connected():
                disconnect_tasks.append(self._robot.disconnect())
                hardware_names.append("Robot")
        except Exception as e:
            logger.warning(f"Robot disconnect preparation failed: {e}")
        
        # Execute parallel disconnections
        if disconnect_tasks:
            logger.info(f"Disconnecting hardware: {', '.join(hardware_names)}")
            results = await asyncio.gather(*disconnect_tasks, return_exceptions=True)
            
            # Check disconnection results
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