"""
Simple MCU Communication Test Use Case

A straightforward use case that performs direct MCU communication testing
similar to simple_serial_test.py but integrated into the UseCase framework.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from loguru import logger

from application.services.configuration_service import ConfigurationService
from application.services.hardware_service_facade import HardwareServiceFacade
from domain.enums.mcu_enums import TestMode
from domain.enums.test_status import TestStatus
from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration


class SimpleMCUTestCommand:
    """Simple MCU Test Command"""

    def __init__(self, operator_id: str = "cli_user"):
        self.operator_id = operator_id


class SimpleMCUTestResult:
    """Simple MCU Test Result"""

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        test_id: TestId,
        test_status: TestStatus,
        execution_duration: TestDuration,
        is_passed: bool,
        test_results: List[Dict[str, Any]],
        error_message: Optional[str] = None,
    ):
        self.test_id = test_id
        self.test_status = test_status
        self.execution_duration = execution_duration
        self.is_passed = is_passed
        self.test_results = test_results
        self.error_message = error_message

    @property
    def measurement_count(self) -> int:
        """Number of successful measurements"""
        return len([r for r in self.test_results if r.get("success", False)])

    def format_duration(self) -> str:
        """Format duration as string"""
        return f"{self.execution_duration.seconds:.3f}s"


class SimpleMCUTestUseCase:
    """
    Simple MCU Communication Test Use Case

    Performs direct MCU communication testing with the same sequence
    as simple_serial_test.py but integrated into the UseCase framework.
    """

    def __init__(
        self, hardware_services: HardwareServiceFacade, configuration_service: ConfigurationService
    ):
        """Initialize Simple MCU Test Use Case"""
        self._hardware_services = hardware_services
        self._configuration_service = configuration_service
        self._is_running = False

    def is_running(self) -> bool:
        """Check if test is currently running"""
        return self._is_running

    async def execute(self, command: SimpleMCUTestCommand) -> SimpleMCUTestResult:
        """
        Execute Simple MCU Communication Test

        Args:
            command: Test command with operator information

        Returns:
            SimpleMCUTestResult with test outcomes and timing information
        """
        test_id = TestId.generate()
        start_time = asyncio.get_event_loop().time()
        self._is_running = True
        test_results = []

        logger.info(f"Starting Simple MCU Test - ID: {test_id}")
        logger.info(f"Test parameters - Operator: {command.operator_id}")

        try:
            # Load hardware configuration
            logger.info("Loading hardware configuration...")
            hardware_config = await self._configuration_service.load_hardware_config()

            # Get MCU service using public property
            mcu_service = self._hardware_services.mcu_service
            if not mcu_service:
                raise RuntimeError("MCU service not available")

            # Connect to MCU using configuration values
            logger.info(
                f"Connecting to MCU - Port: {hardware_config.mcu.port}, Baudrate: {hardware_config.mcu.baudrate}"
            )
            await mcu_service.connect()

            # Wait for boot complete
            logger.info("Waiting for MCU boot complete...")
            await mcu_service.wait_boot_complete()

            # Add 2 second delay after boot complete (using default stabilization time)
            logger.info("Boot complete confirmed, waiting 2 seconds for stabilization...")
            await asyncio.sleep(2.0)

            # Define test sequence (same as simple_serial_test.py)
            test_sequence = [
                {
                    "name": "set_test_mode",
                    "description": "CMD_ENTER_TEST_MODE (모드 1)",
                    "command": lambda: mcu_service.set_test_mode(TestMode.MODE_1),
                },
                {
                    "name": "set_upper_temperature",
                    "description": "CMD_SET_UPPER_TEMP (52°C)",
                    "command": lambda: mcu_service.set_upper_temperature(52.0),
                },
                {
                    "name": "set_fan_speed",
                    "description": "CMD_SET_FAN_SPEED (레벨 10)",
                    "command": lambda: mcu_service.set_fan_speed(10),
                },
                {
                    "name": "start_standby_heating",
                    "description": "CMD_LMA_INIT (동작:52°C, 대기:35°C)",
                    "command": lambda: mcu_service.start_standby_heating(52.0, 35.0, 10000),
                },
                {
                    "name": "start_standby_cooling",
                    "description": "CMD_STROKE_INIT_COMPLETE",
                    "command": mcu_service.start_standby_cooling,
                },
            ]

            # Execute test sequence
            for i, test_step in enumerate(test_sequence, 1):
                step_start_time = time.time()
                logger.info(f"[{i}/{len(test_sequence)}] {test_step['description']}")

                try:
                    await test_step["command"]()
                    step_duration = (time.time() - step_start_time) * 1000

                    result = {
                        "step": i,
                        "name": test_step["name"],
                        "description": test_step["description"],
                        "success": True,
                        "response_time_ms": step_duration,
                        "error": None,
                    }
                    test_results.append(result)
                    logger.info(f"✅ Step {i} completed successfully ({step_duration:.1f}ms)")

                except Exception as step_error:
                    step_duration = (time.time() - step_start_time) * 1000

                    result = {
                        "step": i,
                        "name": test_step["name"],
                        "description": test_step["description"],
                        "success": False,
                        "response_time_ms": step_duration,
                        "error": str(step_error),
                    }
                    test_results.append(result)
                    logger.error(f"❌ Step {i} failed: {step_error}")

                # No delay between commands for maximum speed
                if i < len(test_sequence):  # Don't delay after the last command
                    logger.info(f"Moving to next command... (step {i}/{len(test_sequence)})")
                else:
                    logger.info(f"Last command completed (step {i}/{len(test_sequence)})")

            # Disconnect from MCU
            await mcu_service.disconnect()

            # Calculate results
            successful_steps = len([r for r in test_results if r["success"]])
            total_steps = len(test_results)
            is_passed = successful_steps == total_steps

            end_time = asyncio.get_event_loop().time()
            execution_duration = TestDuration.from_seconds(end_time - start_time)

            logger.info(f"Simple MCU Test completed - Success: {successful_steps}/{total_steps}")

            return SimpleMCUTestResult(
                test_id=test_id,
                test_status=TestStatus.COMPLETED if is_passed else TestStatus.FAILED,
                execution_duration=execution_duration,
                is_passed=is_passed,
                test_results=test_results,
                error_message=None,
            )

        except Exception as e:
            # Handle test failure
            end_time = asyncio.get_event_loop().time()
            execution_duration = TestDuration.from_seconds(end_time - start_time)

            logger.error(f"Simple MCU Test failed: {e}")

            # Try to disconnect on error
            try:
                mcu_service = self._hardware_services.mcu_service
                if mcu_service:
                    await mcu_service.disconnect()
            except Exception as disconnect_error:
                logger.warning(f"Failed to disconnect MCU after error: {disconnect_error}")

            return SimpleMCUTestResult(
                test_id=test_id,
                test_status=TestStatus.ERROR,
                execution_duration=execution_duration,
                is_passed=False,
                test_results=test_results,
                error_message=str(e),
            )

        finally:
            self._is_running = False
