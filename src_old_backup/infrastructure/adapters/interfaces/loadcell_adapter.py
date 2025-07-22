"""
LoadCell Adapter Interface

Defines the contract for loadcell hardware adapters.
Provides business logic abstraction over loadcell controllers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from ....domain.value_objects.measurements import ForceValue
from ....domain.entities.hardware_device import HardwareDevice
from ..base import HardwareAdapterBase


class LoadCellAdapter(HardwareAdapterBase):
    """
    Abstract interface for loadcell adapters
    
    Provides business logic layer between LoadCellService and hardware controllers.
    Handles domain object conversion and business rule enforcement.
    """
    
    def __init__(self, vendor: str):
        """
        Initialize loadcell adapter
        
        Args:
            vendor: LoadCell vendor name
        """
        super().__init__("loadcell", vendor)
    
    @abstractmethod
    async def read_force_value(self) -> ForceValue:
        """
        Read current force measurement
        
        Returns:
            ForceValue domain object with proper units and validation
            
        Raises:
            BusinessRuleViolationException: If reading fails or value invalid
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def read_multiple_samples(self, num_samples: int, interval_ms: float = 100) -> List[ForceValue]:
        """
        Read multiple force samples
        
        Args:
            num_samples: Number of samples to collect
            interval_ms: Interval between samples in milliseconds
            
        Returns:
            List of ForceValue domain objects
            
        Raises:
            BusinessRuleViolationException: If parameters invalid or reading fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def get_raw_data(self) -> str:
        """
        Get raw data string from loadcell
        
        Returns:
            Raw data string for debugging/analysis
            
        Raises:
            BusinessRuleViolationException: If reading fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def zero_force(self) -> None:
        """
        Perform auto-zero operation
        
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def set_hold_enabled(self, enabled: bool) -> None:
        """
        Enable or disable hold function
        
        Args:
            enabled: True to enable hold, False to disable
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def is_hold_enabled(self) -> bool:
        """
        Check if hold function is enabled
        
        Returns:
            True if hold enabled, False otherwise
            
        Raises:
            BusinessRuleViolationException: If status check fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def get_measurement_statistics(self, num_samples: int) -> Dict[str, ForceValue]:
        """
        Get statistical measurements
        
        Args:
            num_samples: Number of samples for statistics
            
        Returns:
            Dictionary with 'min', 'max', 'average', 'std_dev' ForceValue objects
            
        Raises:
            BusinessRuleViolationException: If insufficient samples or calculation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def execute_force_test(self, test_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute comprehensive force test
        
        Args:
            test_parameters: Test configuration parameters
            
        Returns:
            Test results with enhanced domain information
            
        Raises:
            BusinessRuleViolationException: If test execution fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def calibrate(self, reference_force: ForceValue) -> None:
        """
        Perform calibration with known reference force
        
        Args:
            reference_force: Known reference force for calibration
            
        Raises:
            BusinessRuleViolationException: If calibration fails or not supported
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """
        Get comprehensive device information
        
        Returns:
            Device information including model, capabilities, status
            
        Raises:
            BusinessRuleViolationException: If info retrieval fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def get_measurement_range(self) -> Dict[str, ForceValue]:
        """
        Get measurement range capabilities
        
        Returns:
            Dictionary with 'min_force' and 'max_force' ForceValue objects
        """
        pass
    
    @abstractmethod
    async def validate_force_range(self, force: ForceValue) -> bool:
        """
        Validate if force value is within device measurement range
        
        Args:
            force: Force value to validate
            
        Returns:
            True if within range, False otherwise
            
        Raises:
            HardwareNotReadyException: If device not ready
        """
        pass