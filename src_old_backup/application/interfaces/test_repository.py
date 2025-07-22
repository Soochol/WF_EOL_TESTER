"""
Test Repository Interface

Defines the contract for test data persistence.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...domain.entities.eol_test import EOLTest
from ...domain.entities.test_result import TestResult
from ...domain.value_objects.identifiers import TestId, DUTId, OperatorId
from ...domain.enums.test_status import TestStatus
from ...domain.enums.test_types import TestType
from ...domain.value_objects.time_values import Timestamp


class TestRepository(ABC):
    """Interface for test data repository"""
    
    @abstractmethod
    async def save(self, test: EOLTest) -> EOLTest:
        """
        Save EOL test to repository
        
        Args:
            test: EOL test entity to save
            
        Returns:
            Saved test entity
            
        Raises:
            BusinessRuleViolationException: If save operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, test_id: TestId) -> Optional[EOLTest]:
        """
        Find test by ID
        
        Args:
            test_id: Test identifier
            
        Returns:
            EOL test if found, None otherwise
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_by_dut_id(self, dut_id: DUTId) -> List[EOLTest]:
        """
        Find all tests for a specific DUT
        
        Args:
            dut_id: DUT identifier
            
        Returns:
            List of tests for the DUT
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_by_operator(self, operator_id: OperatorId) -> List[EOLTest]:
        """
        Find all tests performed by specific operator
        
        Args:
            operator_id: Operator identifier
            
        Returns:
            List of tests performed by operator
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_by_status(self, status: TestStatus) -> List[EOLTest]:
        """
        Find all tests with specific status
        
        Args:
            status: Test status to filter by
            
        Returns:
            List of tests with matching status
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_by_test_type(self, test_type: TestType) -> List[EOLTest]:
        """
        Find all tests of specific type
        
        Args:
            test_type: Test type to filter by
            
        Returns:
            List of tests with matching type
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_by_date_range(
        self, 
        start_date: Timestamp, 
        end_date: Timestamp
    ) -> List[EOLTest]:
        """
        Find tests within date range
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            List of tests within date range
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_active_tests(self) -> List[EOLTest]:
        """
        Find all currently active tests
        
        Returns:
            List of tests that are currently running or preparing
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def update(self, test: EOLTest) -> EOLTest:
        """
        Update existing test in repository
        
        Args:
            test: Updated test entity
            
        Returns:
            Updated test entity
            
        Raises:
            BusinessRuleViolationException: If update operation fails
        """
        pass
    
    @abstractmethod
    async def delete(self, test_id: TestId) -> bool:
        """
        Delete test from repository
        
        Args:
            test_id: Test identifier
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            BusinessRuleViolationException: If delete operation fails
        """
        pass
    
    @abstractmethod
    async def count_by_status(self, status: TestStatus) -> int:
        """
        Count tests with specific status
        
        Args:
            status: Test status to count
            
        Returns:
            Number of tests with matching status
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def get_test_statistics(
        self, 
        start_date: Optional[Timestamp] = None,
        end_date: Optional[Timestamp] = None
    ) -> Dict[str, Any]:
        """
        Get test statistics for specified period
        
        Args:
            start_date: Start of period (optional)
            end_date: End of period (optional)
            
        Returns:
            Dictionary with statistics including:
                - total_tests: Total number of tests
                - passed_tests: Number of passed tests
                - failed_tests: Number of failed tests
                - pass_rate: Percentage of passed tests
                - average_duration: Average test duration
                - tests_by_type: Breakdown by test type
                
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass