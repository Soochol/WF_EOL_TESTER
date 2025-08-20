"""
Test execution API routes

Provides REST endpoints for test execution and management.
"""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from loguru import logger
from dependency_injector.wiring import Provide, inject

from application.use_cases.eol_force_test import EOLForceTestCommand, EOLForceTestUseCase
from application.use_cases.robot_home import RobotHomeCommand, RobotHomeUseCase
from domain.entities.dut import DUT
from domain.value_objects.dut_command_info import DUTCommandInfo
from application.containers import ApplicationContainer
from ui.api.models.test_models import (
    RobotHomeRequest,
    RobotHomeResponse,
    TestCancellationRequest,
    TestExecutionRequest,
    TestExecutionResponse,
    TestProgressResponse,
)

router = APIRouter()

# Global test execution state
active_tests: Dict[str, Dict] = {}
cancelled_tests: set = set()


@router.post("/eol-force-test", response_model=TestExecutionResponse)
@inject
async def start_eol_force_test(
    request: TestExecutionRequest,
    background_tasks: BackgroundTasks,
    eol_test_use_case: EOLForceTestUseCase = Provide[ApplicationContainer.eol_force_test_use_case],
):
    """Start EOL force test execution"""
    try:

        # Create DUT entity
        from domain.value_objects.identifiers import DUTId

        # Generate DUT ID from serial number or create unique one
        dut_id = DUTId(
            request.dut_serial_number or f"DUT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )

        dut = DUT(
            dut_id=dut_id,
            model_number=request.dut_part_number or "Unknown",
            serial_number=request.dut_serial_number or "Unknown",
        )

        # Create command info
        command_info = DUTCommandInfo(
            dut_id=str(dut.dut_id),
            model_number=dut.model_number,
            serial_number=dut.serial_number,
            manufacturer=dut.manufacturer,
        )

        # Create test command
        test_command = EOLForceTestCommand(
            dut_info=command_info,
            operator_id=request.operator_id,
        )

        # Generate unique test ID
        import uuid

        test_id = str(uuid.uuid4())

        # Create test execution response with initial state
        test_response = TestExecutionResponse(
            test_id=test_id,
            status="starting",
            dut_serial_number=request.dut_serial_number,
            dut_part_number=request.dut_part_number,
            start_time=None,
            end_time=None,
            duration_seconds=None,
            result=None,
            measurements=None,
            error_message=None,
            progress_percentage=0.0,
        )

        # Store test info for tracking
        active_tests[test_response.test_id] = {
            "command": test_command,
            "status": "starting",
            "progress": 0.0,
            "use_case": eol_test_use_case,
        }

        # Start test execution in background
        background_tasks.add_task(
            execute_test_background, test_response.test_id, test_command, eol_test_use_case
        )

        logger.info(f"EOL force test started - ID: {test_response.test_id}")
        return test_response

    except Exception as e:
        logger.error(f"Failed to start EOL force test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start test: {str(e)}",
        ) from e


async def execute_test_background(test_id: str, command: EOLForceTestCommand, use_case):
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
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Test not found: {test_id}"
        )

    test_info = active_tests[test_id]
    command = test_info["command"]

    response = TestExecutionResponse(
        test_id=test_id,
        status=test_info["status"],
        dut_serial_number=command.dut_info.serial_number,
        dut_part_number=command.dut_info.model_number,
        start_time=None,
        end_time=None,
        duration_seconds=None,
        result=None,
        measurements=None,
        error_message=None,
        progress_percentage=test_info.get("progress", 0.0),
    )

    # Add additional info if available
    if "result" in test_info:
        result = test_info["result"]
        response.result = result.test_result.value
        response.start_time = result.start_time.isoformat()
        response.end_time = result.end_time.isoformat() if result.end_time else None
        response.duration_seconds = result.execution_duration.seconds

        if hasattr(result, "measurements") and result.measurements:
            response.measurements = result.measurements.to_dict()

    if "error" in test_info:
        response.error_message = test_info["error"]

    return response


@router.get("/eol-force-test/{test_id}/progress", response_model=TestProgressResponse)
async def get_test_progress(test_id: str):
    """Get detailed test progress"""
    if test_id not in active_tests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Test not found: {test_id}"
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
        current_step="Executing test measurements",
        measurements_completed=completed,
        total_measurements=estimated_total,
    )


@router.post("/eol-force-test/{test_id}/cancel")
async def cancel_test(test_id: str, request: TestCancellationRequest):
    """Cancel running test"""
    if test_id not in active_tests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Test not found: {test_id}"
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
        "emergency_stop": request.emergency_stop,
    }


@router.post("/robot-home", response_model=RobotHomeResponse)
@inject
async def execute_robot_home(
    request: RobotHomeRequest, 
    robot_home_use_case: RobotHomeUseCase = Provide[ApplicationContainer.robot_home_use_case]
):
    """Execute robot homing operation"""
    try:

        # Create command
        command = RobotHomeCommand(operator_id=request.operator_id)

        # Execute robot homing
        result = await robot_home_use_case.execute(command)

        response = RobotHomeResponse(
            operation_id=str(result.operation_id),
            status=result.test_status.value,
            duration_seconds=result.execution_duration.seconds,
            success=result.is_success,
            error_message=result.error_message if hasattr(result, "error_message") else None,
        )

        if result.error_message:
            response.error_message = result.error_message

        logger.info(f"Robot home operation completed - ID: {response.operation_id}")
        return response

    except Exception as e:
        logger.error(f"Robot home operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Robot home operation failed: {str(e)}",
        ) from e


@router.get("/active")
async def get_active_tests():
    """Get list of active tests"""
    active_test_list = []

    for test_id, test_info in active_tests.items():
        command = test_info["command"]
        active_test_list.append(
            {
                "test_id": test_id,
                "status": test_info["status"],
                "progress": test_info.get("progress", 0.0),
                "dut_serial_number": command.dut_info.serial_number,
                "dut_part_number": command.dut_info.model_number,
                "operator_id": command.operator_id,
            }
        )

    return {"active_tests": active_test_list, "total_count": len(active_test_list)}


@router.delete("/cleanup")
async def cleanup_completed_tests():
    """Clean up completed test records"""
    completed_statuses = {"completed", "failed", "cancelled", "emergency_stopped"}

    tests_to_remove = [
        test_id
        for test_id, test_info in active_tests.items()
        if test_info["status"] in completed_statuses
    ]

    for test_id in tests_to_remove:
        del active_tests[test_id]
        cancelled_tests.discard(test_id)

    logger.info(f"Cleaned up {len(tests_to_remove)} completed test records")
    return {
        "message": f"Cleaned up {len(tests_to_remove)} completed test records",
        "removed_tests": tests_to_remove,
    }
