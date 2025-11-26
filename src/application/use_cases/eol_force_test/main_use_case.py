"""
Main EOL Test Executor

Orchestrates EOL test execution using focused components.
Refactored from monolithic class for better maintainability while preserving exact functionality.
"""

# Standard library imports
from typing import Any, Dict, Optional, TYPE_CHECKING

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.services.core.configuration_service import ConfigurationService
from application.services.core.configuration_validator import ConfigurationValidator
from application.services.core.exception_handler import ExceptionHandler
from application.services.core.repository_service import RepositoryService
from application.services.hardware_facade import HardwareServiceFacade
from application.services.monitoring.emergency_stop_service import (
    EmergencyStopService,
)
from application.services.test.test_result_evaluator import TestResultEvaluator


if TYPE_CHECKING:
    from application.services.industrial.industrial_system_manager import IndustrialSystemManager
    from application.services.industrial.neurohub_service import NeuroHubService

# Local application imports
from domain.entities.eol_test import EOLTest
from domain.enums.test_status import TestStatus
from domain.exceptions.test_exceptions import TestExecutionException
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.eol_test_result import EOLTestResult
from domain.value_objects.identifiers import TestId
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.time_values import TestDuration

# Local folder imports
from ..common.base_use_case import BaseUseCase
from ..common.command_result_patterns import BaseUseCaseInput
from ..common.execution_context import ExecutionContext
from .configuration_loader import TestConfigurationLoader
from .constants import TestExecutionConstants
from .hardware_test_executor import HardwareTestExecutor
from .measurement_converter import MeasurementConverter
from .result_evaluator import ResultEvaluator
from .test_entity_factory import TestEntityFactory
from .test_state_manager import TestStateManager


class EOLForceTestInput(BaseUseCaseInput):
    """EOL Test Execution Input Data"""

    def __init__(self, dut_info: DUTCommandInfo, operator_id: str = "system"):
        super().__init__(operator_id)
        self.dut_info = dut_info

    def to_dict(self) -> Dict[str, Any]:
        """Convert input to dictionary representation"""
        return {
            "operator_id": self.operator_id,
            "dut_info": {
                "dut_id": self.dut_info.dut_id,
                "model_number": self.dut_info.model_number,
                "serial_number": self.dut_info.serial_number,
                "manufacturer": self.dut_info.manufacturer,
            },
        }


class EOLForceTestUseCase(BaseUseCase):
    """
    EOL Test Execution Use Case with Component-Based Architecture

    Orchestrates the complete End-of-Line testing process using focused components
    for better maintainability while preserving exact functionality and execution order.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        hardware_services: HardwareServiceFacade,
        configuration_service: ConfigurationService,
        configuration_validator: ConfigurationValidator,
        test_result_evaluator: TestResultEvaluator,
        repository_service: RepositoryService,
        exception_handler: ExceptionHandler,
        emergency_stop_service: Optional[EmergencyStopService] = None,
        industrial_system_manager: Optional["IndustrialSystemManager"] = None,
        neurohub_service: Optional["NeuroHubService"] = None,
        db_logger_service: Optional[Any] = None,
    ):
        # Initialize BaseUseCase
        super().__init__("EOL Force Test", emergency_stop_service)

        # Core service dependencies (unchanged)
        self._hardware_services = hardware_services
        self._exception_handler = exception_handler
        self._industrial_system_manager = industrial_system_manager
        self._neurohub_service = neurohub_service
        self._db_logger_service = db_logger_service

        # Inject repository service into hardware facade for cycle-by-cycle saving
        if hasattr(hardware_services, "_repository_service"):
            hardware_services._repository_service = repository_service

        # Initialize focused components
        self._config_loader = TestConfigurationLoader(
            configuration_service, configuration_validator
        )
        self._test_factory = TestEntityFactory(repository_service)
        self._hardware_executor = HardwareTestExecutor(hardware_services)
        self._measurement_converter = MeasurementConverter()
        self._state_manager = TestStateManager(repository_service)
        self._result_evaluator = ResultEvaluator(
            test_result_evaluator, self._measurement_converter, self._state_manager
        )

        # Emergency stop and interruption handling
        self._keyboard_interrupt_raised = False

    async def _execute_implementation(
        self, input_data: BaseUseCaseInput, context: ExecutionContext
    ) -> EOLTestResult:
        """
        Execute EOL test implementation (BaseUseCase abstract method)

        Args:
            input_data: Base input (will be cast to EOLForceTestInput)
            context: Execution context with timing and identification info

        Returns:
            EOLTestResult containing test outcome and execution details
        """
        # Cast to specific input type
        if not isinstance(input_data, EOLForceTestInput):
            raise ValueError(f"Expected EOLForceTestInput, got {type(input_data)}")

        eol_input = input_data

        # Execute single test - repeat_count is now handled within the force test sequence
        return await self.execute_single(eol_input)

    async def execute(self, input_data: EOLForceTestInput) -> EOLTestResult:
        """
        Execute EOL test (public interface)

        This method delegates to BaseUseCase.execute for consistent behavior.
        """
        result = await super().execute(input_data)
        # Result is guaranteed to be EOLTestResult since _execute_implementation returns one
        return result  # type: ignore

    def _create_failure_result(
        self,
        input_data: BaseUseCaseInput,
        context: ExecutionContext,
        execution_duration: TestDuration,
        error_message: str,
    ) -> EOLTestResult:
        """
        Create failure result for BaseUseCase compatibility

        Args:
            command: Original command that failed
            context: Execution context
            execution_duration: How long execution took before failing
            error_message: Error description

        Returns:
            EOLTestResult indicating failure
        """
        return EOLTestResult.create_error(
            test_id=context.test_id, error_message=error_message, duration=execution_duration
        )

    async def execute_single(
        self, command: EOLForceTestInput, session_timestamp: Optional[str] = None
    ) -> EOLTestResult:
        """
        Execute EOL test using component-based architecture

        Args:
            command: Test execution command containing DUT info and operator ID
            session_timestamp: Optional session timestamp for CSV file grouping

        Returns:
            EOLTestResult containing test outcome, measurements, and execution details

        Raises:
            TestExecutionException: If configuration validation fails or critical test errors occur
            ConfigurationNotFoundError: If specified profile cannot be found
            RepositoryAccessError: If test data cannot be saved
            HardwareConnectionException: If hardware connection fails

        Note:
            This method follows Exception First principles - all operations either succeed
            or raise descriptive exceptions. Test failures are captured in the result
            object rather than raised as exceptions.
        """
        logger.info(TestExecutionConstants.LOG_TEST_EXECUTION_START, command.dut_info.dut_id)

        # Reset KeyboardInterrupt flag for each execution
        self._keyboard_interrupt_raised = False

        # Track if 착공 (START) was sent - 완공 (COMPLETE) must be sent if this is True
        neurohub_start_sent = False
        neurohub_complete_sent = False  # 완공 전송 여부 추적

        # Execute test with proper error handling (BaseUseCase handles _is_running)
        start_time = asyncio.get_event_loop().time()
        measurements: Optional[TestMeasurements] = None
        test_entity = None

        # Verify GUI State Manager connection for real-time updates
        gui_state_manager_connected = (
            hasattr(self._hardware_services, "_gui_state_manager")
            and self._hardware_services._gui_state_manager is not None
        )
        logger.info(
            f"🔌 EOL UseCase: GUI State Manager connection status: {gui_state_manager_connected}"
        )
        if gui_state_manager_connected:
            logger.info(
                f"🔗 EOL UseCase: GUI State Manager ID = {id(self._hardware_services._gui_state_manager)}"
            )
        else:
            logger.warning(
                "⚠️ EOL UseCase: GUI State Manager not connected - cycle results will not be displayed in real-time"
            )

        # DEBUG: Check Industrial System Manager status
        logger.info(
            f"🏭 DEBUG: Industrial System Manager status: {self._industrial_system_manager is not None}"
        )
        if self._industrial_system_manager:
            logger.info(
                f"🏭 DEBUG: Industrial System Manager ID: {id(self._industrial_system_manager)}"
            )
            logger.info(
                f"🏭 DEBUG: Industrial System Manager type: {type(self._industrial_system_manager)}"
            )
        else:
            logger.error("🏭 DEBUG: Industrial System Manager is None - Tower Lamp will not work!")

        # Phase 0: Initialize Industrial System Manager BEFORE try block
        # This ensures tower lamp error indication works even if config loading fails
        if self._industrial_system_manager:
            try:
                logger.info("🏭 EOL UseCase: Initializing Industrial System Manager...")
                await self._industrial_system_manager.initialize_system()
                logger.info("🏭 EOL UseCase: Industrial System Manager ready")
            except Exception as init_error:
                logger.error(
                    f"⚠️ EOL UseCase: Failed to initialize Industrial Manager: {init_error}"
                )
                logger.warning("⚠️ EOL UseCase: Continuing without Tower Lamp (degraded mode)")

        try:
            # Phase 1: Initialize test setup
            await self._config_loader.load_and_validate_configurations()

            test_entity = await self._test_factory.create_test_entity(
                command.dut_info,
                command.operator_id,
                self._config_loader.test_config,
                session_timestamp,
            )

            # NeuroHub: Send START (착공) message
            # 반환값으로 실제 착공 전송 여부 확인 (enabled 상태에서만 True)
            neurohub_start_sent = await self._send_neurohub_start(command.dut_info.serial_number)

            # Phase 2: Execute test
            test_entity.prepare_test()

            # Validate configurations are loaded (will raise exception if None)
            assert self._config_loader.test_config is not None
            assert self._config_loader.hardware_config is not None

            self._hardware_executor.validate_configurations_loaded(
                self._config_loader.test_config, self._config_loader.hardware_config
            )

            # Start test execution (transition from PREPARING to RUNNING)
            test_entity.start_execution()

            # Update industrial status indication
            if self._industrial_system_manager:
                # Import here to avoid circular imports
                # Local application imports
                from application.services.industrial.tower_lamp_service import SystemStatus

                await self._industrial_system_manager.set_system_status(SystemStatus.SYSTEM_RUNNING)

            # Phase 3: Execute hardware test phases
            measurements, individual_cycle_results = (
                await self._hardware_executor.execute_hardware_test_phases(
                    self._config_loader.test_config,
                    self._config_loader.hardware_config,
                    command.dut_info,
                )
            )

            # Phase 4: Evaluate results and create success result
            is_test_passed = await self._result_evaluator.evaluate_measurements_and_update_test(
                test_entity, measurements, self._config_loader.test_config
            )
            await self._state_manager.save_test_state(test_entity)

            # Save to database if db_logger_service is available
            await self._log_test_to_database(test_entity, measurements)

            execution_duration = self._calculate_execution_duration(start_time)
            result_status = (
                TestExecutionConstants.TEST_RESULT_PASSED
                if is_test_passed
                else TestExecutionConstants.TEST_RESULT_FAILED
            )
            logger.info(
                TestExecutionConstants.LOG_TEST_EXECUTION_COMPLETED,
                test_entity.test_id,
                result_status,
            )

            # Update industrial status indication based on test result
            if self._industrial_system_manager:
                await self._industrial_system_manager.handle_test_completion(
                    test_success=is_test_passed, test_error=False
                )

            # NeuroHub: Send COMPLETE (완공) message
            await self._send_neurohub_complete(
                serial_number=command.dut_info.serial_number,
                result="PASS" if is_test_passed else "FAIL",
                measurements=measurements,
            )
            neurohub_complete_sent = True

            return self._create_success_result(
                test_entity,
                measurements,
                execution_duration,
                is_test_passed,
                individual_cycle_results,
            )

        except KeyboardInterrupt:
            # Handle KeyboardInterrupt with emergency stop priority
            # Set flag to prevent normal cleanup in finally block
            self._keyboard_interrupt_raised = True
            # Reset robot homing state to force homing on next test after interrupt
            self._hardware_services.reset_robot_homing_state()
            logger.info("Robot homing state reset due to keyboard interrupt")
            # Don't perform normal cleanup - let emergency stop handle hardware safety
            # Re-raise to allow emergency stop service to execute
            raise
        except asyncio.CancelledError:
            # Handle CancelledError (from asyncio.sleep interruptions) as KeyboardInterrupt
            # Set flag to prevent normal cleanup in finally block
            self._keyboard_interrupt_raised = True
            # Reset robot homing state to force homing on next test after cancellation
            self._hardware_services.reset_robot_homing_state()
            logger.info("Robot homing state reset due to test cancellation")
            # Convert CancelledError back to KeyboardInterrupt for emergency stop service
            raise KeyboardInterrupt("Test cancelled by user interrupt") from None
        except Exception as e:
            # Phase 5: Handle test failure with proper error context
            return await self._handle_test_failure(
                e, test_entity, command, measurements, start_time
            )

        finally:
            # NeuroHub: 착공이 시작되었으면 반드시 완공을 보내야 함
            # (KeyboardInterrupt, CancelledError 포함 모든 경우)
            if neurohub_start_sent and not neurohub_complete_sent:
                try:
                    logger.info("🔗 NeuroHub: Sending COMPLETE (완공) in finally block (interrupted/error)")
                    await self._send_neurohub_complete(
                        serial_number=command.dut_info.serial_number,
                        result="FAIL",
                        measurements=measurements,
                    )
                except Exception as neurohub_error:
                    logger.warning(f"🔗 NeuroHub: Failed to send COMPLETE in finally: {neurohub_error}")

            # Phase 6: Cleanup hardware resources (only if not interrupted)
            # Skip cleanup entirely if KeyboardInterrupt was raised - let Emergency Stop handle hardware safety
            if self._keyboard_interrupt_raised:
                # Skip cleanup - Emergency Stop Service will handle hardware safety
                pass
            else:
                # Normal cleanup for successful/failed tests (not interrupted)
                try:
                    await self._cleanup_hardware_resources(test_entity)
                except KeyboardInterrupt:
                    # If KeyboardInterrupt occurs during cleanup, prioritize emergency stop
                    self._keyboard_interrupt_raised = True
                    raise
                except Exception as cleanup_error:
                    # If standard cleanup fails, ensure power is still turned off for safety
                    logger.warning(
                        "Standard cleanup failed: {}, attempting emergency power off", cleanup_error
                    )
                    await self._emergency_power_off()

    def _calculate_execution_duration(self, start_time: float) -> TestDuration:
        """
        Calculate test execution duration

        Args:
            start_time: Test start time from event loop

        Returns:
            TestDuration: Calculated execution duration
        """
        end_time = asyncio.get_event_loop().time()
        duration_seconds = end_time - start_time
        return TestDuration.from_seconds(duration_seconds)

    def _create_success_result(
        self,
        test_entity: EOLTest,
        measurements: TestMeasurements,
        execution_duration: TestDuration,
        is_test_passed: bool,
        individual_cycle_results: list,
    ) -> EOLTestResult:
        """
        Create successful test result object

        Args:
            test_entity: Completed test entity
            measurements: Test measurements
            execution_duration: Total execution time
            is_test_passed: Whether test passed or failed
            individual_cycle_results: Results for each repeat cycle

        Returns:
            EOLTestResult: Success result with all test data
        """
        return EOLTestResult(
            test_id=test_entity.test_id,
            test_status=(TestStatus.COMPLETED if is_test_passed else TestStatus.FAILED),
            execution_duration=execution_duration,
            is_passed=is_test_passed,
            measurement_ids=self._state_manager.generate_measurement_ids(measurements),
            test_summary=measurements,
            error_message=None,
            individual_cycle_results=individual_cycle_results,
        )

    async def _handle_test_failure(  # pylint: disable=too-many-arguments
        self,
        error: Exception,
        test_entity: Optional[EOLTest],
        command: EOLForceTestInput,  # pylint: disable=unused-argument
        measurements: Optional[TestMeasurements],
        start_time: float,
    ) -> EOLTestResult:
        """
        Handle test failure and create appropriate result

        Args:
            error: Exception that caused the failure
            test_entity: Test entity (may be incomplete)
            command: Original command for fallback data
            measurements: Measurements collected before failure (if any)
            start_time: Test start time for duration calculation

        Returns:
            EOLTestResult: Failure result with error details
        """
        execution_duration = self._calculate_execution_duration(start_time)
        error_context = await self._exception_handler.handle_exception(
            error,
            TestExecutionConstants.EXECUTE_EOL_TEST_OPERATION,
        )

        logger.error("EOL test execution failed: {}", error_context.get("user_message", str(error)))

        # Reset robot homing state to force homing on next test
        # This ensures robot position is verified after errors
        self._hardware_services.reset_robot_homing_state()
        logger.info("Robot homing state reset - next test will perform homing")

        # Update industrial status indication for error (with safety net)
        if self._industrial_system_manager:
            try:
                await self._industrial_system_manager.handle_test_completion(
                    test_success=False, test_error=True
                )
            except Exception as lamp_error:
                logger.warning(f"⚠️ Failed to indicate error on Tower Lamp: {lamp_error}")

        # NeuroHub: 완공은 finally 블록에서 처리됨
        # (착공 여부 체크와 중복 방지를 위해 finally에서 일괄 처리)

        # Try to save error state if test entity exists
        if test_entity is not None:
            try:
                test_entity.error_test(error_context.get("user_message", str(error)))
                await self._state_manager.save_test_state(test_entity)
            except Exception as save_error:
                logger.warning("Failed to save test entity error state: {}", save_error)

        # Create failure result with available data
        return EOLTestResult(
            test_id=(test_entity.test_id if test_entity else TestId.generate()),
            test_status=TestStatus.ERROR,
            execution_duration=execution_duration,
            is_passed=False,
            measurement_ids=(
                self._state_manager.generate_measurement_ids(measurements) if measurements else []
            ),
            test_summary=measurements or {},
            error_message=error_context.get("user_message", str(error)),
        )

    async def _cleanup_hardware_resources(self, test_entity: Optional[EOLTest]) -> None:
        """
        Clean up hardware resources and connections

        Args:
            test_entity: Test entity for logging context (optional)

        Note:
            Cleanup failures are logged but never raise exceptions

        IMPORTANT: Hardware connections are NOT shutdown here to preserve tower lamp state.
        Tower lamp blinking/status must continue after test completion.
        Hardware shutdown only happens on program exit.
        """
        try:
            # Only perform teardown if test configuration is available
            if self._config_loader.test_config and self._config_loader.hardware_config:
                await self._hardware_services.teardown_test(
                    self._config_loader.test_config, self._config_loader.hardware_config
                )
            # DO NOT call shutdown_hardware() here!
            # Reason: Tower lamp needs Digital I/O to stay connected for blinking to work.
            # TEST_PASS/FAIL states use blinking, which requires active Digital I/O connection.
            # Hardware shutdown will be handled by main window on program exit.
            logger.debug(TestExecutionConstants.LOG_HARDWARE_CLEANUP_SUCCESS)
        except Exception as cleanup_error:
            # Hardware cleanup errors should never fail the test
            test_context = f" for test entity {test_entity.test_id}" if test_entity else ""
            logger.warning("Hardware cleanup failed{}: {}", test_context, cleanup_error)

    async def _emergency_power_off(self) -> None:
        """
        Emergency power off when standard cleanup fails

        Attempts to disable power output regardless of configuration state
        for safety purposes. This is a last resort when normal teardown fails.
        """
        try:
            # Direct power service access for emergency shutdown
            power_service = self._hardware_services.power_service
            if power_service and await power_service.is_connected():
                await power_service.disable_output()
                logger.info("Emergency power off completed successfully")
            else:
                logger.warning("Power service not available for emergency power off")
        except Exception as emergency_error:
            # Even emergency power off failed - log critical error but don't raise
            logger.critical("Emergency power off failed: {}", emergency_error)

    async def _log_test_to_database(
        self, test_entity: "EOLTest", measurements: TestMeasurements
    ) -> None:
        """
        Log test result and measurements to database

        Args:
            test_entity: Test entity with results
            measurements: Test measurements data

        Note:
            Database logging failures are logged but never raise exceptions
            to avoid breaking the main test flow
        """
        if not self._db_logger_service:
            return

        try:
            # Log test result
            await self._db_logger_service.log_test_result(test_entity)

            # Log raw measurements
            # Standard library imports
            from datetime import datetime

            serial_number = test_entity.dut.serial_number or "UNKNOWN"
            test_id_str = str(test_entity.test_id)

            # TestMeasurements is iterable over (temperature, PositionMeasurements) pairs
            cycle_idx = 0
            for temp, position_measurements in measurements:
                # PositionMeasurements is iterable over (position, MeasurementReading) pairs
                for pos, reading in position_measurements:
                    try:
                        # Extract values from MeasurementReading
                        temperature_val = float(temp) if temp is not None else None
                        position_val = float(pos) if pos is not None else None
                        force_val = (
                            float(reading.force_value.value)
                            if reading.force_value is not None
                            else None
                        )

                        # Log to database
                        await self._db_logger_service.log_raw_measurement(
                            test_id=test_id_str,
                            serial_number=serial_number,
                            cycle_number=cycle_idx + 1,
                            temperature=temperature_val,
                            position=position_val,
                            force=force_val,
                            timestamp=datetime.now(),
                        )
                        cycle_idx += 1
                    except Exception as meas_error:
                        logger.debug(
                            f"Failed to log measurement (T={temp}, P={pos}) to database: {meas_error}"
                        )

            logger.debug(f"Test {test_id_str} logged to database successfully")

        except Exception as e:
            logger.warning(f"Failed to log test to database: {e}")
            # Don't raise - database logging is optional

    # ============================================================================
    # NEUROHUB MES INTEGRATION (착공/완공)
    # ============================================================================

    async def _send_neurohub_start(self, serial_number: str) -> bool:
        """
        Send START (착공) message to NeuroHub MES

        Args:
            serial_number: WIP serial number

        Returns:
            bool: True if START was actually sent (enabled and successful),
                  False if disabled or failed

        Note:
            NeuroHub communication failures are logged but never raise exceptions
            to avoid blocking test execution.
        """
        if not self._neurohub_service:
            return False  # 서비스 없음 - 착공 안 보냄

        try:
            # Check if service is enabled
            if not await self._neurohub_service.is_enabled():
                logger.debug("🔗 NeuroHub: Service disabled, skipping START")
                return False  # disabled - 착공 안 보냄

            logger.info(f"🔗 NeuroHub: Sending START (착공) for {serial_number}")
            success = await self._neurohub_service.send_start(serial_number)
            if success:
                logger.info(f"🔗 NeuroHub: START acknowledged for {serial_number}")
                return True  # 착공 실제로 전송됨
            else:
                logger.warning(f"🔗 NeuroHub: START failed for {serial_number}")
                return True  # 시도했으나 실패 - 완공도 시도해야 함
        except Exception as e:
            logger.warning(f"🔗 NeuroHub: Error sending START: {e}")
            return True  # 시도했으나 에러 - 완공도 시도해야 함

    async def _send_neurohub_complete(
        self,
        serial_number: str,
        result: str,
        measurements: Optional[TestMeasurements] = None,
    ) -> None:
        """
        Send COMPLETE (완공) message to NeuroHub MES

        Args:
            serial_number: WIP serial number
            result: Test result ("PASS" or "FAIL")
            measurements: Test measurements data

        Note:
            NeuroHub communication failures are logged but never raise exceptions
            to avoid blocking test completion.
        """
        if not self._neurohub_service:
            return

        try:
            # Convert measurements to NeuroHub format
            neurohub_measurements = self._convert_measurements_for_neurohub(measurements)
            defects = self._extract_defects_for_neurohub(measurements, result)

            logger.info(f"🔗 NeuroHub: Sending COMPLETE (완공) [{result}] for {serial_number}")
            success = await self._neurohub_service.send_complete(
                serial_number=serial_number,
                result=result,
                measurements=neurohub_measurements,
                defects=defects if result == "FAIL" else None,
            )
            if success:
                logger.info(f"🔗 NeuroHub: COMPLETE acknowledged for {serial_number}")
            else:
                logger.warning(f"🔗 NeuroHub: COMPLETE failed for {serial_number}")
        except Exception as e:
            logger.warning(f"🔗 NeuroHub: Error sending COMPLETE: {e}")
            # Don't raise - NeuroHub communication is optional

    def _convert_measurements_for_neurohub(
        self, measurements: Optional[TestMeasurements]
    ) -> list:
        """
        Convert TestMeasurements to NeuroHub measurement format

        Args:
            measurements: Test measurements data

        Returns:
            List of measurement dictionaries in NeuroHub format
        """
        if not measurements:
            return []

        neurohub_measurements = []
        try:
            # TestMeasurements is iterable over (temperature, PositionMeasurements) pairs
            for temp, position_measurements in measurements:
                # PositionMeasurements is iterable over (position, MeasurementReading) pairs
                for pos, reading in position_measurements:
                    try:
                        force_val = (
                            float(reading.force_value.value)
                            if reading.force_value is not None
                            else None
                        )
                        # Determine pass/fail for this measurement
                        meas_result = "PASS"
                        if reading.force_value and hasattr(reading.force_value, "is_valid"):
                            meas_result = "PASS" if reading.force_value.is_valid else "FAIL"

                        neurohub_measurements.append({
                            "code": f"FORCE_T{temp}_P{pos}",
                            "name": f"Force at T={temp}°C, P={pos}mm",
                            "value": force_val,
                            "unit": reading.force_value.unit.value if reading.force_value else "kgf",
                            "result": meas_result,
                        })
                    except Exception:
                        continue
        except Exception as e:
            logger.debug(f"Error converting measurements for NeuroHub: {e}")

        return neurohub_measurements

    def _extract_defects_for_neurohub(
        self, measurements: Optional[TestMeasurements], result: str
    ) -> list:
        """
        Extract defect information for NeuroHub FAIL results

        Args:
            measurements: Test measurements data
            result: Test result ("PASS" or "FAIL")

        Returns:
            List of defect dictionaries in NeuroHub format
        """
        if result != "FAIL" or not measurements:
            return []

        defects = []
        try:
            # Find failed measurements
            for temp, position_measurements in measurements:
                for pos, reading in position_measurements:
                    try:
                        if reading.force_value and hasattr(reading.force_value, "is_valid"):
                            if not reading.force_value.is_valid:
                                force_val = float(reading.force_value.value)
                                unit_str = reading.force_value.unit.value if reading.force_value else "kgf"
                                defects.append({
                                    "code": f"FORCE_T{temp}_P{pos}",
                                    "reason": f"Force out of spec: {force_val}{unit_str}",
                                })
                    except Exception:
                        continue
        except Exception as e:
            logger.debug(f"Error extracting defects for NeuroHub: {e}")

        return defects
