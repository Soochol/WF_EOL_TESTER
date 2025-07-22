"""
Measurement Repository Interface

Defines the contract for measurement data persistence.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...domain.entities.measurement import Measurement
from ...domain.value_objects.identifiers import MeasurementId, TestId
from ...domain.value_objects.time_values import Timestamp


class MeasurementRepository(ABC):
    """Interface for measurement data repository"""
    
    @abstractmethod
    async def save(self, measurement: Measurement) -> Measurement:
        """
        Save measurement to repository
        
        Args:
            measurement: Measurement entity to save
            
        Returns:
            Saved measurement entity
            
        Raises:
            BusinessRuleViolationException: If save operation fails
        """
        pass
    
    @abstractmethod
    async def save_batch(self, measurements: List[Measurement]) -> List[Measurement]:
        """
        Save multiple measurements in batch operation
        
        Args:
            measurements: List of measurement entities to save
            
        Returns:
            List of saved measurement entities
            
        Raises:
            BusinessRuleViolationException: If batch save operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, measurement_id: MeasurementId) -> Optional[Measurement]:
        """
        Find measurement by ID
        
        Args:
            measurement_id: Measurement identifier
            
        Returns:
            Measurement if found, None otherwise
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_by_test_id(self, test_id: TestId) -> List[Measurement]:
        """
        Find all measurements for a specific test
        
        Args:
            test_id: Test identifier
            
        Returns:
            List of measurements for the test, ordered by sequence/timestamp
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_by_test_id_and_type(
        self, 
        test_id: TestId, 
        measurement_type: str
    ) -> List[Measurement]:
        """
        Find measurements by test ID and measurement type
        
        Args:
            test_id: Test identifier
            measurement_type: Type of measurement ('force', 'voltage', etc.)
            
        Returns:
            List of measurements of specified type for the test
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_by_hardware_type(self, hardware_type: str) -> List[Measurement]:
        """
        Find measurements by hardware device type
        
        Args:
            hardware_type: Hardware device type ('loadcell', 'power_supply', etc.)
            
        Returns:
            List of measurements from specified hardware type
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def find_by_date_range(
        self, 
        start_date: Timestamp, 
        end_date: Timestamp,
        measurement_type: Optional[str] = None
    ) -> List[Measurement]:
        """
        Find measurements within date range
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            measurement_type: Optional filter by measurement type
            
        Returns:
            List of measurements within date range
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def get_latest_measurement(
        self, 
        test_id: TestId, 
        measurement_type: Optional[str] = None
    ) -> Optional[Measurement]:
        """
        Get latest measurement for a test
        
        Args:
            test_id: Test identifier
            measurement_type: Optional filter by measurement type
            
        Returns:
            Latest measurement if found, None otherwise
            
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass
    
    @abstractmethod
    async def delete_by_test_id(self, test_id: TestId) -> int:
        """
        Delete all measurements for a test
        
        Args:
            test_id: Test identifier
            
        Returns:
            Number of measurements deleted
            
        Raises:
            BusinessRuleViolationException: If delete operation fails
        """
        pass
    
    @abstractmethod
    async def get_measurement_statistics(
        self,
        test_id: Optional[TestId] = None,
        measurement_type: Optional[str] = None,
        start_date: Optional[Timestamp] = None,
        end_date: Optional[Timestamp] = None
    ) -> Dict[str, Any]:
        """
        Get measurement statistics
        
        Args:
            test_id: Optional filter by test ID
            measurement_type: Optional filter by measurement type
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with statistics including:
                - count: Total number of measurements
                - min_value: Minimum measured value
                - max_value: Maximum measured value
                - average_value: Average measured value
                - std_deviation: Standard deviation
                - measurements_by_type: Breakdown by measurement type
                - measurements_by_hardware: Breakdown by hardware type
                
        Raises:
            BusinessRuleViolationException: If repository access fails
        """
        pass