"""
Test execution API routes

Provides REST endpoints for test execution and management.
"""

import asyncio
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from loguru import logger

from application.use_cases.eol_force_test import EOLForceTestCommand
from application.use_cases.robot_home import RobotHomeCommand
from domain.entities.dut import DUT
from domain.value_objects.dut_command_info import DUTCommandInfo
from ui.api.dependencies import DIContainer, get_container
from ui.api.models.test_models import (
    RobotHomeRequest,
    RobotHomeResponse,
    TestCancellationRequest,
    TestExecutionRequest,
    TestExecutionResponse,
    TestProgressResponse,
    TestResultsResponse,
)

router = APIRouter()

# Global test execution state
active_tests: Dict[str, Dict] = {}
cancelled_tests: set = set()


@router.post("/eol-force-test", response_model=TestExecutionResponse)
async def start_eol_force_test(
    request: TestExecutionRequest,
    background_tasks: BackgroundTasks,
    container: DIContainer = Depends(get_container)
):
    """Start EOL force test execution"""
    try:
        # Get use case and services
        eol_test_use_case = container.eol_force_test_use_case()
        config_service = container.configuration_service()
        
        # Determine profile to use
        profile_name = request.profile_name or await config_service.get_active_profile_name()
        
        # Create DUT entity
        dut = DUT(
            serial_number=request.dut_serial_number,
            part_number=request.dut_part_number
        )
        
        # Create command info
        command_info = DUTCommandInfo(
            operator_id=request.operator_id,
            dut=dut
        )
        
        # Create test command
        test_command = EOLForceTestCommand(
            dut_command_info=command_info,
            profile_name=profile_name,
            operator_id=request.operator_id
        )
        
        # Create test execution response with initial state
        test_response = TestExecutionResponse(
            test_id=str(test_command.execution_id),
            status="starting",
            dut_serial_number=request.dut_serial_number,
            dut_part_number=request.dut_part_number,
            progress_percentage=0.0
        )
        
        # Store test info for tracking
        active_tests[test_response.test_id] = {
            "command": test_command,
            "status": "starting",
            "progress": 0.0,
            "use_case": eol_test_use_case
        }
        
        # Start test execution in background
        background_tasks.add_task(
            execute_test_background,
            test_response.test_id,
            test_command,
            eol_test_use_case
        )
        
        logger.info(f"EOL force test started - ID: {test_response.test_id}")
        return test_response
        
    except Exception as e:
        logger.error(f"Failed to start EOL force test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start test: {str(e)}"
        )


async def execute_test_background(
    test_id: str,
    command: EOLForceTestCommand,
    use_case
):
    """Execute test in background task"""
    try:
        # Update status
        if test_id in active_tests:
            active_tests[test_id]["status"] = "running"
            active_tests[test_id]["progress"] = 5.0
        
        # Check if test was cancelled before starting
        if test_id in cancelled_tests:
            logger.info(f"Test {test_id} was cancelled before execution")
            if test_id in active_tests:
                active_tests[test_id]["status"] = "cancelled"
            return
        
        logger.info(f"Executing EOL force test in background - ID: {test_id}")
        
        # Execute the test
        result = await use_case.execute(command)
        
        # Update final status
        if test_id in active_tests:
            active_tests[test_id]["status"] = "completed"
            active_tests[test_id]["progress"] = 100.0
            active_tests[test_id]["result"] = result
        
        logger.info(f"EOL force test completed - ID: {test_id}, Result: {result.test_result}")
        
    except Exception as e:
        logger.error(f"EOL force test execution failed - ID: {test_id}: {e}")
        if test_id in active_tests:
            active_tests[test_id]["status"] = "failed"
            active_tests[test_id]["error"] = str(e)


@router.get("/eol-force-test/{test_id}/status", response_model=TestExecutionResponse)
async def get_test_status(test_id: str):
    """Get test execution status"""
    if test_id not in active_tests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test not found: {test_id}"
        )
    
    test_info = active_tests[test_id]
    command = test_info["command"]
    
    response = TestExecutionResponse(
        test_id=test_id,
        status=test_info["status"],
        dut_serial_number=command.dut_command_info.dut.serial_number,
        dut_part_number=command.dut_command_info.dut.part_number,
        progress_percentage=test_info.get("progress", 0.0)
    )
    
    # Add additional info if available
    if "result" in test_info:
        result = test_info["result"]
        response.result = result.test_result.value
        response.start_time = result.start_time.isoformat()
        response.end_time = result.end_time.isoformat() if result.end_time else None
        response.duration_seconds = result.execution_duration.seconds
        
        if hasattr(result, 'measurements') and result.measurements:
            response.measurements = result.measurements.to_dict()
    
    if "error" in test_info:
        response.error_message = test_info["error"]
    
    return response


@router.get("/eol-force-test/{test_id}/progress", response_model=TestProgressResponse)
async def get_test_progress(test_id: str):
    """Get detailed test progress"""
    if test_id not in active_tests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test not found: {test_id}"
        )
    
    test_info = active_tests[test_id]
    
    # Get estimated measurements based on test configuration
    # This would need to be enhanced based on actual test config
    estimated_total = 84  # 12 temps * 7 positions as default
    completed = int((test_info.get("progress", 0.0) / 100.0) * estimated_total)
    
    return TestProgressResponse(
        test_id=test_id,
        status=test_info["status"],
        progress_percentage=test_info.get("progress", 0.0),
        current_step=f"Executing test measurements",
        measurements_completed=completed,
        total_measurements=estimated_total
    )


@router.post("/eol-force-test/{test_id}/cancel")
async def cancel_test(
    test_id: str,
    request: TestCancellationRequest
):
    """Cancel running test"""
    if test_id not in active_tests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test not found: {test_id}"
        )
    
    # Mark test as cancelled
    cancelled_tests.add(test_id)
    
    if test_id in active_tests:
        active_tests[test_id]["status"] = "cancelling"
        
        # If emergency stop, we should also stop hardware
        if request.emergency_stop:
            # This would trigger emergency stop procedures
            logger.warning(f"Emergency stop requested for test {test_id}")
            active_tests[test_id]["status"] = "emergency_stopped"
    
    logger.info(f"Test cancellation requested - ID: {test_id}, Reason: {request.reason}")
    return {
        "message": f"Test {test_id} cancellation requested",
        "emergency_stop": request.emergency_stop
    }


@router.post("/robot-home", response_model=RobotHomeResponse)
async def execute_robot_home(
    request: RobotHomeRequest,
    container: DIContainer = Depends(get_container)
):
    """Execute robot homing operation"""
    try:
        robot_home_use_case = container.robot_home_use_case()
        
        # Create command
        command = RobotHomeCommand(operator_id=request.operator_id)
        
        # Execute robot homing
        result = await robot_home_use_case.execute(command)
        
        response = RobotHomeResponse(
            operation_id=str(result.operation_id),
            status=result.test_status.value,
            duration_seconds=result.execution_duration.seconds,
            success=result.is_success
        )
        
        if result.error_message:
            response.error_message = result.error_message
        
        logger.info(f"Robot home operation completed - ID: {response.operation_id}")
        return response
        
    except Exception as e:
        logger.error(f"Robot home operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Robot home operation failed: {str(e)}"
        )


@router.get("/active")
async def get_active_tests():
    """Get list of active tests"""
    active_test_list = []
    
    for test_id, test_info in active_tests.items():
        command = test_info["command"]
        active_test_list.append({
            "test_id": test_id,
            "status": test_info["status"],
            "progress": test_info.get("progress", 0.0),
            "dut_serial_number": command.dut_command_info.dut.serial_number,
            "dut_part_number": command.dut_command_info.dut.part_number,
            "operator_id": command.operator_id
        })
    
    return {
        "active_tests": active_test_list,
        "total_count": len(active_test_list)
    }


@router.delete("/cleanup")
async def cleanup_completed_tests():
    """Clean up completed test records"""
    completed_statuses = {"completed", "failed", "cancelled", "emergency_stopped"}
    
    tests_to_remove = [
        test_id for test_id, test_info in active_tests.items()
        if test_info["status"] in completed_statuses
    ]
    
    for test_id in tests_to_remove:
        del active_tests[test_id]
        cancelled_tests.discard(test_id)
    
    logger.info(f"Cleaned up {len(tests_to_remove)} completed test records")
    return {
        "message": f"Cleaned up {len(tests_to_remove)} completed test records",
        "removed_tests": tests_to_remove
    }
