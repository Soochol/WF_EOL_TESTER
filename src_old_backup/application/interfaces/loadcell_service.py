"""
LoadCell Service Interface

Defines the contract for loadcell measurement services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ...domain.value_objects.measurements import ForceValue
from ...domain.entities.hardware_device import HardwareDevice
from ...domain.enums.hardware_status import HardwareStatus


class LoadCellService(ABC):
    """Interface for loadcell measurement services"""
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to loadcell controller
        
        Raises:
            BusinessRuleViolationException: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from loadcell controller
        
        Raises:
            BusinessRuleViolationException: If disconnection fails
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if loadcell is connected
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_hardware_device(self) -> HardwareDevice:
        """
        Get hardware device entity representing the loadcell
        
        Returns:
            HardwareDevice entity with current status and information
        """
        pass
    
    @abstractmethod
    async def read_force_value(self) -> ForceValue:
        """
        Read current force measurement
        
        Returns:
            Force value with appropriate units
            
        Raises:
            BusinessRuleViolationException: If measurement fails or device not ready
        """
        pass
    
    @abstractmethod
    async def read_multiple_samples(self, num_samples: int, interval_ms: float = 100) -> list[ForceValue]:
        """
        Read multiple force samples
        
        Args:
            num_samples: Number of samples to take
            interval_ms: Interval between samples in milliseconds
            
        Returns:
            List of force measurements
            
        Raises:
            BusinessRuleViolationException: If measurement fails or parameters invalid
        """
        pass
    
    @abstractmethod
    async def get_raw_data(self) -> str:
        """
        Get raw data string from loadcell controller
        
        Returns:
            Raw measurement data as received from hardware
            
        Raises:
            BusinessRuleViolationException: If read fails or device not ready
        """
        pass
    
    @abstractmethod
    async def zero_force(self) -> None:
        """
        Perform auto-zero operation to set current reading as zero reference
        
        Raises:
            BusinessRuleViolationException: If zero operation fails or device not ready
        """
        pass
    
    @abstractmethod
    async def set_hold_enabled(self, enabled: bool) -> None:
        """
        Enable or disable hold function
        
        Args:
            enabled: True to enable hold, False to disable
            
        Raises:
            BusinessRuleViolationException: If operation fails or device not ready
        """
        pass
    
    @abstractmethod
    async def is_hold_enabled(self) -> bool:
        """
        Check if hold function is enabled
        
        Returns:
            True if hold enabled, False otherwise
            
        Raises:
            BusinessRuleViolationException: If device not connected
        """
        pass
    
    @abstractmethod
    async def get_measurement_statistics(self, num_samples: int) -> Dict[str, ForceValue]:
        """
        Get statistical measurements (min, max, average, std dev)
        
        Args:
            num_samples: Number of samples for statistics calculation
            
        Returns:
            Dictionary with 'min', 'max', 'average', 'std_dev' force values
            
        Raises:
            BusinessRuleViolationException: If measurement fails
        """
        pass
    
    @abstractmethod
    async def execute_force_test(self, test_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute comprehensive force test with specified parameters
        
        Args:
            test_parameters: Test configuration including:
                - test_type: Type of force test ('single_reading', 'multi_sample', 'zero_test')
                - num_samples: Number of samples (for multi_sample tests)
                - sample_interval: Interval between samples in milliseconds
                - target_force: Target force for comparison tests
                - tolerance_percent: Acceptable tolerance percentage
                
        Returns:
            Test results dictionary including:
                - test_type: Type of test performed
                - force_readings: List of force measurements
                - statistics: Statistical analysis if applicable
                - test_passed: Boolean pass/fail result
                - execution_time: Test duration
                
        Raises:
            BusinessRuleViolationException: If test execution fails
        """
        pass
    
    @abstractmethod
    async def calibrate(self, reference_force: ForceValue) -> None:
        """
        Perform calibration with known reference force
        
        Args:
            reference_force: Known reference force for calibration
            
        Raises:
            BusinessRuleViolationException: If calibration fails
        """
        pass
    
    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """
        Get loadcell device information
        
        Returns:
            Dictionary with device information including:
                - model: Device model
                - indicator_id: Indicator ID
                - communication_stats: Connection statistics
                - last_calibration: Last calibration timestamp if available
                
        Raises:
            BusinessRuleViolationException: If not connected
        """
        pass
    
    @abstractmethod
    async def get_measurement_range(self) -> Dict[str, ForceValue]:
        """
        Get measurement range capabilities
        
        Returns:
            Dictionary with 'min_force' and 'max_force' values
            
        Raises:
            BusinessRuleViolationException: If not connected
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
            BusinessRuleViolationException: If device not connected
        """
        pass