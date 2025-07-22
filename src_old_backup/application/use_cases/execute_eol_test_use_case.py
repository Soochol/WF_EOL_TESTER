"""
Execute EOL Test Use Case

Main use case for executing End-of-Line tests with full hardware coordination.
"""

import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger

from ..commands.execute_eol_test_command import ExecuteEOLTestCommand
from ..results.eol_test_result import EOLTestResult
from ..interfaces.test_repository import TestRepository
from ..interfaces.measurement_repository import MeasurementRepository
from ..interfaces.loadcell_service import LoadCellService
from ..interfaces.power_service import PowerService

from ...domain.entities.eol_test import EOLTest
from ...domain.entities.dut import DUT
from ...domain.entities.measurement import Measurement
from ...domain.entities.test_result import TestResult
from ...domain.value_objects.identifiers import TestId, MeasurementId
from ...domain.value_objects.time_values import Timestamp
from ...domain.enums.test_status import TestStatus
from ...domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException, 
    HardwareNotReadyException,
    UnsafeOperationException
)


class ExecuteEOLTestUseCase:
    """Use case for executing EOL tests"""
    
    def __init__(
        self,
        test_repository: TestRepository,
        measurement_repository: MeasurementRepository,
        loadcell_service: LoadCellService,
        power_service: PowerService
    ):
        """
        Initialize use case with required dependencies
        
        Args:
            test_repository: Repository for test persistence
            measurement_repository: Repository for measurement persistence  
            loadcell_service: Service for loadcell operations
            power_service: Service for power supply operations
        """
        self._test_repository = test_repository
        self._measurement_repository = measurement_repository
        self._loadcell_service = loadcell_service
        self._power_service = power_service
    
    async def execute(self, command: ExecuteEOLTestCommand) -> EOLTestResult:
        """
        Execute EOL test based on command
        
        Args:
            command: Test execution command
            
        Returns:
            Test execution result
            
        Raises:
            BusinessRuleViolationException: If test execution fails
        """
        logger.info(f"Starting EOL test execution for DUT {command.dut_id}")
        
        try:
            # Create and save test entity
            eol_test = await self._create_test_entity(command)
            eol_test = await self._test_repository.save(eol_test)
            
            # Setup hardware based on test requirements
            await self._setup_required_hardware(eol_test)
            
            # Execute test steps
            measurement_ids = await self._execute_test_steps(eol_test)
            
            # Create test result and complete test
            test_result = await self._create_test_result(eol_test, measurement_ids)
            eol_test.complete_test(test_result)
            
            # Save final test state
            await self._test_repository.update(eol_test)
            
            logger.info(f"EOL test {eol_test.test_id} completed successfully")
            
            return self._create_use_case_result(eol_test, measurement_ids)
            
        except BusinessRuleViolationException:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during EOL test execution: {e}")
            
            # Try to fail the test if it was created
            try:
                if 'eol_test' in locals():
                    eol_test.fail_test(f"Unexpected error: {str(e)}")
                    await self._test_repository.update(eol_test)
            except Exception:
                pass  # Don't fail on cleanup failure
            
            raise BusinessRuleViolationException(
                "TEST_EXECUTION_ERROR",
                f"EOL test execution failed: {str(e)}",
                {"dut_id": str(command.dut_id), "test_type": command.test_type.value}
            )
    
    async def _create_test_entity(self, command: ExecuteEOLTestCommand) -> EOLTest:
        """Create EOL test entity from command"""
        # Create DUT entity
        dut = DUT(
            dut_id=command.dut_id,
            model_number=command.dut_model_number,
            serial_number=command.dut_serial_number,
            manufacturer=command.dut_manufacturer
        )
        
        # Create test entity
        test_id = TestId.generate()
        eol_test = EOLTest(
            test_id=test_id,
            dut=dut,
            test_type=command.test_type,
            operator_id=command.operator_id,
            test_configuration=command.test_configuration,
            pass_criteria=command.pass_criteria
        )
        
        if command.operator_notes:
            eol_test.set_operator_notes(command.operator_notes)
        
        return eol_test
    
    async def _setup_required_hardware(self, eol_test: EOLTest) -> None:
        """Setup and connect required hardware for test"""
        required_hardware = []
        
        # Determine required hardware based on test type
        if eol_test.test_type.requires_force_measurement:
            required_hardware.append("loadcell")
        
        if eol_test.test_type.requires_electrical_measurement:
            required_hardware.append("power_supply")
        
        eol_test.set_required_hardware(required_hardware)
        
        # Connect hardware services
        hardware_tasks = []
        
        if "loadcell" in required_hardware:
            hardware_tasks.append(self._setup_loadcell_hardware(eol_test))
        
        if "power_supply" in required_hardware:
            hardware_tasks.append(self._setup_power_supply_hardware(eol_test))
        
        # Execute hardware setup in parallel
        if hardware_tasks:
            await asyncio.gather(*hardware_tasks)
        
        # Verify all hardware is ready
        if not eol_test.are_all_hardware_connected():
            missing = eol_test.get_missing_hardware()
            raise HardwareNotReadyException(
                "multiple", 
                f"disconnected: {missing}",
                "execute_test",
                {"missing_hardware": missing, "test_id": str(eol_test.test_id)}
            )
    
    async def _setup_loadcell_hardware(self, eol_test: EOLTest) -> None:
        """Setup loadcell hardware"""
        try:
            if not await self._loadcell_service.is_connected():
                await self._loadcell_service.connect()
            
            # Perform auto-zero for accurate measurements
            await self._loadcell_service.zero_force()
            
            eol_test.set_hardware_connection_status("loadcell", True)
            logger.info("Loadcell hardware setup completed")
            
        except Exception as e:
            logger.error(f"Loadcell setup failed: {e}")
            eol_test.set_hardware_connection_status("loadcell", False)
            raise HardwareNotReadyException(
                "loadcell",
                "setup_failed",
                "connect",
                {"error": str(e)}
            )
    
    async def _setup_power_supply_hardware(self, eol_test: EOLTest) -> None:
        """Setup power supply hardware"""
        try:
            if not await self._power_service.is_connected():
                await self._power_service.connect()
            
            # Ensure output is disabled initially for safety
            await self._power_service.set_output_enabled(1, False)
            
            eol_test.set_hardware_connection_status("power_supply", True)
            logger.info("Power supply hardware setup completed")
            
        except Exception as e:
            logger.error(f"Power supply setup failed: {e}")
            eol_test.set_hardware_connection_status("power_supply", False)
            raise HardwareNotReadyException(
                "power_supply",
                "setup_failed", 
                "connect",
                {"error": str(e)}
            )
    
    async def _execute_test_steps(self, eol_test: EOLTest) -> List[MeasurementId]:
        """Execute test steps and collect measurements"""
        measurement_ids = []
        
        # Determine test steps based on test type
        total_steps = self._calculate_total_steps(eol_test.test_type)
        eol_test.start_test(total_steps)
        await self._test_repository.update(eol_test)
        
        eol_test.begin_execution()
        await self._test_repository.update(eol_test)
        
        try:
            # Execute force measurements if required
            if eol_test.test_type.requires_force_measurement:
                force_measurements = await self._execute_force_measurements(eol_test)
                measurement_ids.extend(force_measurements)
            
            # Execute electrical measurements if required
            if eol_test.test_type.requires_electrical_measurement:
                electrical_measurements = await self._execute_electrical_measurements(eol_test)
                measurement_ids.extend(electrical_measurements)
            
            # Execute comprehensive test if required
            if eol_test.test_type.is_comprehensive:
                comprehensive_measurements = await self._execute_comprehensive_test(eol_test)
                measurement_ids.extend(comprehensive_measurements)
            
            return measurement_ids
            
        except Exception as e:
            logger.error(f"Test step execution failed: {e}")
            eol_test.fail_test(f"Test execution failed: {str(e)}")
            await self._test_repository.update(eol_test)
            raise
    
    def _calculate_total_steps(self, test_type) -> int:
        """Calculate total number of test steps"""
        step_count = 0
        
        if test_type.requires_force_measurement:
            step_count += 2  # Zero + measurement
        
        if test_type.requires_electrical_measurement:
            step_count += 3  # Setup + voltage + current
        
        if test_type.is_comprehensive:
            step_count += 2  # Additional validation + reporting
        
        return max(step_count, 1)  # At least 1 step
    
    async def _execute_force_measurements(self, eol_test: EOLTest) -> List[MeasurementId]:
        """Execute force measurement steps"""
        measurement_ids = []
        
        eol_test.advance_step("Force measurement preparation")
        await self._test_repository.update(eol_test)
        
        # Get test configuration for force measurement
        num_samples = eol_test.get_configuration_parameter("force_samples", 3)
        sample_interval = eol_test.get_configuration_parameter("force_interval_ms", 100)
        
        # Take force measurements
        force_values = await self._loadcell_service.read_multiple_samples(
            num_samples, sample_interval
        )
        
        # Create measurement entities
        for i, force_value in enumerate(force_values):
            measurement_id = MeasurementId.generate()
            measurement = Measurement.create_force_measurement(
                measurement_id=measurement_id,
                test_id=eol_test.test_id,
                force_value=force_value,
                sequence_number=i + 1
            )
            
            await self._measurement_repository.save(measurement)
            eol_test.add_measurement_id(measurement_id)
            measurement_ids.append(measurement_id)
        
        eol_test.advance_step("Force measurements completed")
        await self._test_repository.update(eol_test)
        
        return measurement_ids
    
    async def _execute_electrical_measurements(self, eol_test: EOLTest) -> List[MeasurementId]:
        """Execute electrical measurement steps"""
        measurement_ids = []
        
        eol_test.advance_step("Electrical measurement preparation")
        await self._test_repository.update(eol_test)
        
        # Configure power supply from test parameters
        target_voltage = eol_test.get_configuration_parameter("target_voltage", 12.0)
        current_limit = eol_test.get_configuration_parameter("current_limit", 1.0)
        
        # Set voltage and current limit
        from ...domain.value_objects.measurements import VoltageValue, CurrentValue
        from ...domain.enums.measurement_units import MeasurementUnit
        
        voltage_value = VoltageValue(target_voltage, MeasurementUnit.VOLT)
        current_value = CurrentValue(current_limit, MeasurementUnit.AMPERE)
        
        await self._power_service.set_voltage(1, voltage_value)
        await self._power_service.set_current_limit(1, current_value)
        
        # Enable output (with safety check)
        await self._power_service.set_output_enabled(1, True)
        
        try:
            # Allow settling time
            await asyncio.sleep(0.5)
            
            # Take electrical measurements
            measurements = await self._power_service.measure_all(1)
            
            # Create measurement entities for voltage and current
            for measurement_type, value in measurements.items():
                if measurement_type in ('voltage', 'current'):
                    measurement_id = MeasurementId.generate()
                    
                    if measurement_type == 'voltage':
                        measurement_value = VoltageValue.from_raw_data(value)
                    else:
                        measurement_value = CurrentValue.from_raw_data(value)
                    
                    measurement = Measurement(
                        measurement_id=measurement_id,
                        test_id=eol_test.test_id,
                        measurement_type=measurement_type,
                        measurement_value=measurement_value,
                        hardware_device_type="power_supply"
                    )
                    
                    await self._measurement_repository.save(measurement)
                    eol_test.add_measurement_id(measurement_id)
                    measurement_ids.append(measurement_id)
        
        finally:
            # Always disable output for safety
            await self._power_service.set_output_enabled(1, False)
        
        eol_test.advance_step("Electrical measurements completed")
        await self._test_repository.update(eol_test)
        
        return measurement_ids
    
    async def _execute_comprehensive_test(self, eol_test: EOLTest) -> List[MeasurementId]:
        """Execute comprehensive test validation"""
        measurement_ids = []
        
        eol_test.advance_step("Comprehensive test validation")
        await self._test_repository.update(eol_test)
        
        # Perform additional validation steps for comprehensive tests
        # This could include cross-verification of measurements,
        # repeatability tests, etc.
        
        eol_test.advance_step("Comprehensive test completed")
        await self._test_repository.update(eol_test)
        
        return measurement_ids
    
    async def _create_test_result(self, eol_test: EOLTest, measurement_ids: List[MeasurementId]) -> TestResult:
        """Create test result entity"""
        # Get all measurements for evaluation
        measurements = []
        for measurement_id in measurement_ids:
            measurement = await self._measurement_repository.find_by_id(measurement_id)
            if measurement:
                measurements.append(measurement)
        
        # Evaluate test results against pass criteria
        actual_results = self._calculate_actual_results(measurements)
        test_passed = self._evaluate_pass_criteria(eol_test, actual_results)
        
        # Create test result
        test_result = TestResult(
            test_id=eol_test.test_id,
            test_status=TestStatus.COMPLETED if test_passed else TestStatus.FAILED,
            start_time=eol_test.start_time,
            end_time=Timestamp.now(),
            measurement_ids=measurement_ids,
            pass_criteria=eol_test.pass_criteria,
            actual_results=actual_results
        )
        
        return test_result
    
    def _calculate_actual_results(self, measurements: List[Measurement]) -> Dict[str, Any]:
        """Calculate actual test results from measurements"""
        results = {}
        
        # Group measurements by type
        measurements_by_type = {}
        for measurement in measurements:
            measurement_type = measurement.measurement_type
            if measurement_type not in measurements_by_type:
                measurements_by_type[measurement_type] = []
            measurements_by_type[measurement_type].append(measurement)
        
        # Calculate statistics for each measurement type
        for measurement_type, type_measurements in measurements_by_type.items():
            values = [m.get_numeric_value() for m in type_measurements]
            
            if values:
                results[f"{measurement_type}_count"] = len(values)
                results[f"{measurement_type}_average"] = sum(values) / len(values)
                results[f"{measurement_type}_min"] = min(values)
                results[f"{measurement_type}_max"] = max(values)
                
                if len(values) > 1:
                    import statistics
                    results[f"{measurement_type}_std_dev"] = statistics.stdev(values)
        
        return results
    
    def _evaluate_pass_criteria(self, eol_test: EOLTest, actual_results: Dict[str, Any]) -> bool:
        """Evaluate if test passes based on criteria and results"""
        pass_criteria = eol_test.pass_criteria
        
        if not pass_criteria:
            return True  # No criteria means auto-pass
        
        for criterion_name, criterion_value in pass_criteria.items():
            actual_value = actual_results.get(criterion_name)
            
            if actual_value is None:
                return False  # Missing required result
            
            if not self._evaluate_single_criterion(criterion_value, actual_value):
                return False
        
        return True
    
    def _evaluate_single_criterion(self, criterion: Any, actual: Any) -> bool:
        """Evaluate single pass criterion"""
        if isinstance(criterion, dict):
            # Range criterion
            if "min" in criterion and actual < criterion["min"]:
                return False
            if "max" in criterion and actual > criterion["max"]:
                return False
            return True
        else:
            # Direct comparison
            return abs(actual - criterion) < 1e-9 if isinstance(criterion, (int, float)) else actual == criterion
    
    def _create_use_case_result(self, eol_test: EOLTest, measurement_ids: List[MeasurementId]) -> EOLTestResult:
        """Create use case result from domain entities"""
        return EOLTestResult(
            test_id=eol_test.test_id,
            test_type=eol_test.test_type,
            test_status=eol_test.status,
            execution_duration=eol_test.get_duration(),
            is_passed=eol_test.is_passed(),
            measurement_ids=measurement_ids,
            test_summary=eol_test.test_result.actual_results if eol_test.test_result else {},
            error_message=eol_test.error_message,
            operator_notes=eol_test.operator_notes
        )