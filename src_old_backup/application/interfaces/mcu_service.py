"""
MCU Service Interface

Application layer interface for MCU (Microcontroller Unit) operations.
Defines the contract for temperature control, test mode management, and fan control.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from enum import IntEnum

from ...domain.entities.hardware_device import HardwareDevice
from ...domain.value_objects.measurements import TemperatureValue


class TestMode(IntEnum):
    """Test mode enumeration"""
    MODE_1 = 1
    MODE_2 = 2
    MODE_3 = 3


class MCUStatus(IntEnum):
    """MCU status enumeration"""
    IDLE = 0
    HEATING = 1
    COOLING = 2
    HOLDING = 3
    ERROR = 4


class MCUService(ABC):
    """
    Abstract interface for MCU service operations
    
    Provides business logic interface for MCU operations including
    temperature control, test mode management, and monitoring.
    """
    
    # Connection Management
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to MCU device
        
        Raises:
            BusinessRuleViolationException: If connection fails
            HardwareNotReadyException: If device not available
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from MCU device
        
        Raises:
            BusinessRuleViolationException: If disconnection fails
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if MCU device is connected
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_hardware_device(self) -> HardwareDevice:
        """
        Get hardware device entity
        
        Returns:
            HardwareDevice entity with current status
        """
        pass
    
    # Test Mode Management
    @abstractmethod
    async def enter_test_mode(self, mode: TestMode) -> None:
        """
        Enter specified test mode
        
        Args:
            mode: Test mode to enter
            
        Raises:
            BusinessRuleViolationException: If mode entry fails
            UnsafeOperationException: If current state doesn't allow mode change
        """
        pass
    
    @abstractmethod
    async def exit_test_mode(self) -> None:
        """
        Exit current test mode and return to idle
        
        Raises:
            BusinessRuleViolationException: If mode exit fails
        """
        pass
    
    @abstractmethod
    async def get_current_test_mode(self) -> Optional[TestMode]:
        """
        Get current test mode
        
        Returns:
            Current test mode or None if in idle mode
        """
        pass
    
    # Temperature Control
    @abstractmethod
    async def set_temperature_profile(
        self, 
        upper_temp: TemperatureValue,
        operating_temp: TemperatureValue, 
        cooling_temp: TemperatureValue
    ) -> None:
        """
        Set complete temperature profile
        
        Args:
            upper_temp: Upper temperature limit
            operating_temp: Operating temperature target
            cooling_temp: Cooling temperature target
            
        Raises:
            BusinessRuleViolationException: If temperature values are invalid
            UnsafeOperationException: If temperature limits are unsafe
        """
        pass
    
    @abstractmethod
    async def set_operating_temperature(self, temperature: TemperatureValue) -> None:
        """
        Set operating temperature target
        
        Args:
            temperature: Target operating temperature
            
        Raises:
            BusinessRuleViolationException: If temperature is invalid
            UnsafeOperationException: If temperature is outside safe range
        """
        pass
    
    @abstractmethod
    async def get_current_temperature(self) -> TemperatureValue:
        """
        Get current temperature reading
        
        Returns:
            Current temperature measurement
            
        Raises:
            BusinessRuleViolationException: If temperature reading fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def get_temperature_profile(self) -> Dict[str, TemperatureValue]:
        """
        Get current temperature profile settings
        
        Returns:
            Dictionary containing upper, operating, and cooling temperatures
        """
        pass
    
    # Fan Control
    @abstractmethod
    async def set_fan_speed(self, level: int) -> None:
        """
        Set fan speed level
        
        Args:
            level: Fan speed level (1-10)
            
        Raises:
            BusinessRuleViolationException: If fan level is invalid
            UnsafeOperationException: If fan control not allowed in current mode
        """
        pass
    
    @abstractmethod
    async def get_fan_speed(self) -> int:
        """
        Get current fan speed level
        
        Returns:
            Current fan speed level (1-10)
            
        Raises:
            BusinessRuleViolationException: If fan speed reading fails
        """
        pass
    
    # MCU Initialization and Configuration
    @abstractmethod
    async def initialize_mcu(
        self, 
        operating_temp: TemperatureValue,
        standby_temp: TemperatureValue, 
        hold_time_ms: int
    ) -> None:
        """
        Initialize MCU with operation parameters
        
        Args:
            operating_temp: Operating temperature setting
            standby_temp: Standby temperature setting
            hold_time_ms: Hold time in milliseconds
            
        Raises:
            BusinessRuleViolationException: If initialization fails
            UnsafeOperationException: If parameters are unsafe
        """
        pass
    
    # Status and Monitoring
    @abstractmethod
    async def get_mcu_status(self) -> MCUStatus:
        """
        Get current MCU operational status
        
        Returns:
            Current MCU status
        """
        pass
    
    @abstractmethod
    async def start_temperature_monitoring(
        self, 
        callback: Callable[[TemperatureValue, MCUStatus], None],
        interval_ms: int = 1000
    ) -> str:
        """
        Start temperature monitoring with callback
        
        Args:
            callback: Function to call with temperature updates
            interval_ms: Monitoring interval in milliseconds
            
        Returns:
            Monitoring session ID for later stopping
            
        Raises:
            BusinessRuleViolationException: If monitoring fails to start
        """
        pass
    
    @abstractmethod
    async def stop_temperature_monitoring(self, session_id: str) -> None:
        """
        Stop temperature monitoring session
        
        Args:
            session_id: Session ID from start_temperature_monitoring
            
        Raises:
            BusinessRuleViolationException: If session not found or stop fails
        """
        pass
    
    # Safety and Validation
    @abstractmethod
    async def validate_temperature_range(self, temperature: TemperatureValue) -> bool:
        """
        Validate if temperature is within safe operating range
        
        Args:
            temperature: Temperature to validate
            
        Returns:
            True if temperature is safe, False otherwise
        """
        pass
    
    @abstractmethod
    async def emergency_shutdown(self) -> None:
        """
        Perform emergency shutdown of MCU operations
        
        Stops all heating, sets fan to maximum, and enters safe mode.
        
        Raises:
            BusinessRuleViolationException: If shutdown fails
        """
        pass
    
    @abstractmethod
    async def reset_mcu(self) -> None:
        """
        Reset MCU to default state
        
        Returns MCU to idle mode with default temperature settings.
        
        Raises:
            BusinessRuleViolationException: If reset fails
        """
        pass
    
    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """
        Get MCU device information
        
        Returns:
            Dictionary containing device specifications and capabilities
        """
        pass
    
    @abstractmethod
    async def run_self_test(self) -> Dict[str, Any]:
        """
        Run MCU self-test diagnostics
        
        Returns:
            Dictionary containing test results and system health status
            
        Raises:
            BusinessRuleViolationException: If self-test fails
        """
        pass