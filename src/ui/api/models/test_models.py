"""
Pydantic models for test execution API endpoints
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TestExecutionRequest(BaseModel):
    """Request model for test execution"""
    profile_name: Optional[str] = Field(None, description="Configuration profile to use")
    dut_serial_number: str = Field(..., description="DUT serial number")
    dut_part_number: str = Field(..., description="DUT part number")
    operator_id: str = Field("system", description="Operator ID")
    test_parameters: Optional[Dict] = Field(None, description="Override test parameters")


class TestExecutionResponse(BaseModel):
    """Response model for test execution"""
    test_id: str = Field(..., description="Unique test execution ID")
    status: str = Field(..., description="Test status: 'running', 'completed', 'failed', 'cancelled'")
    dut_serial_number: str
    dut_part_number: str
    start_time: Optional[str] = Field(None, description="Test start timestamp")
    end_time: Optional[str] = Field(None, description="Test end timestamp")
    duration_seconds: Optional[float] = Field(None, description="Test duration in seconds")
    result: Optional[str] = Field(None, description="Test result: 'PASS', 'FAIL'")
    measurements: Optional[Dict] = Field(None, description="Test measurement data")
    error_message: Optional[str] = Field(None, description="Error message if test failed")
    progress_percentage: Optional[float] = Field(None, description="Test progress percentage")


class RobotHomeRequest(BaseModel):
    """Request model for robot homing"""
    operator_id: str = Field("system", description="Operator ID")


class RobotHomeResponse(BaseModel):
    """Response model for robot homing"""
    operation_id: str = Field(..., description="Unique operation ID")
    status: str = Field(..., description="Operation status")
    duration_seconds: float = Field(..., description="Operation duration")
    success: bool = Field(..., description="Whether operation succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class TestProgressResponse(BaseModel):
    """Response model for test progress updates"""
    test_id: str
    status: str
    progress_percentage: float
    current_step: str
    measurements_completed: int
    total_measurements: int
    estimated_remaining_seconds: Optional[float] = None


class TestResultsResponse(BaseModel):
    """Response model for detailed test results"""
    test_id: str
    dut_serial_number: str
    dut_part_number: str
    test_result: str  # PASS/FAIL
    start_time: str
    end_time: str
    duration_seconds: float
    measurements: Dict[str, Dict[str, Dict[str, float]]]  # temp -> position -> measurement
    pass_criteria_evaluation: Dict
    operator_id: str
    configuration_used: Dict
    error_details: Optional[Dict] = None


class TestListResponse(BaseModel):
    """Response model for test history list"""
    tests: List[TestResultsResponse]
    total_count: int
    page: int
    page_size: int


class TestCancellationRequest(BaseModel):
    """Request model for test cancellation"""
    reason: Optional[str] = Field(None, description="Reason for cancellation")
    emergency_stop: bool = Field(False, description="Whether this is an emergency stop")
