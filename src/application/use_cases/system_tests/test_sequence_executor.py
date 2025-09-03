"""
Test Sequence Executor for Simple MCU Test

Executes predefined MCU command sequences and records timing and success metrics.
Handles individual test step execution with error handling and timing.
"""

import time
from typing import Any, Dict, List
from loguru import logger

from application.services.hardware_facade import HardwareServiceFacade
from domain.enums.mcu_enums import TestMode


class TestSequenceExecutor:
    """
    Test sequence executor for simple MCU test
    
    Manages execution of predefined MCU command sequences with timing
    and error handling for each step.
    """

    def __init__(self, hardware_services: HardwareServiceFacade):
        """
        Initialize test sequence executor
        
        Args:
            hardware_services: Hardware service facade
        """
        self._hardware_services = hardware_services

    def get_test_sequence(self) -> List[Dict[str, Any]]:
        """
        Get the predefined test sequence for MCU communication
        
        Returns:
            List of test step dictionaries with commands and descriptions
        """
        mcu_service = self._hardware_services.mcu_service
        
        return [
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

    async def execute_test_sequence(self) -> List[Dict[str, Any]]:
        """
        Execute the complete test sequence
        
        Returns:
            List of test step results with timing and success metrics
        """
        test_sequence = self.get_test_sequence()
        test_results = []

        logger.info(f"Starting MCU command sequence - {len(test_sequence)} steps")
        
        for i, test_step in enumerate(test_sequence, 1):
            result = await self._execute_single_step(test_step, i, len(test_sequence))
            test_results.append(result)
            
            # Log progress
            if i < len(test_sequence):
                logger.info(f"Moving to next command... (step {i}/{len(test_sequence)})")
            else:
                logger.info(f"Last command completed (step {i}/{len(test_sequence)})")
        
        # Log summary
        successful_steps = len([r for r in test_results if r["success"]])
        total_steps = len(test_results)
        logger.info(f"Test sequence completed - Success: {successful_steps}/{total_steps}")
        
        return test_results

    async def _execute_single_step(
        self, 
        test_step: Dict[str, Any], 
        step_number: int, 
        total_steps: int
    ) -> Dict[str, Any]:
        """
        Execute a single test step with timing and error handling
        
        Args:
            test_step: Test step dictionary containing command and metadata
            step_number: Current step number (1-indexed)
            total_steps: Total number of steps
            
        Returns:
            Dictionary containing step execution results
        """
        step_start_time = time.time()
        logger.info(f"[{step_number}/{total_steps}] {test_step['description']}")

        try:
            await test_step["command"]()
            step_duration = (time.time() - step_start_time) * 1000

            result = {
                "step": step_number,
                "name": test_step["name"],
                "description": test_step["description"],
                "success": True,
                "response_time_ms": step_duration,
                "error": None,
            }
            
            logger.info(f"✅ Step {step_number} completed successfully ({step_duration:.1f}ms)")
            return result

        except Exception as step_error:
            step_duration = (time.time() - step_start_time) * 1000

            result = {
                "step": step_number,
                "name": test_step["name"],
                "description": test_step["description"],
                "success": False,
                "response_time_ms": step_duration,
                "error": str(step_error),
            }
            
            logger.error(f"❌ Step {step_number} failed: {step_error}")
            return result
