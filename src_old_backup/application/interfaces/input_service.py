"""
Input Service Interface

Application layer interface for digital input and trigger management operations.
Defines the contract for button press detection, trigger monitoring, and event handling.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Optional, Tuple
from enum import Enum

from ...domain.entities.hardware_device import HardwareDevice


class InputTriggerType(Enum):
    """Input trigger types"""
    BUTTON_PRESS = "button_press"
    DIGITAL_HIGH = "digital_high"
    DIGITAL_LOW = "digital_low"
    DIGITAL_CHANGE = "digital_change"


class InputService(ABC):
    """
    Abstract interface for input service operations
    
    Provides business logic interface for digital input management including
    trigger detection, button press handling, and event monitoring.
    """
    
    # Connection Management
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to input device
        
        Raises:
            BusinessRuleViolationException: If connection fails
            HardwareNotReadyException: If device not available
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from input device
        
        Raises:
            BusinessRuleViolationException: If disconnection fails
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if input device is connected
        
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
    
    # Input Reading
    @abstractmethod
    async def read_input(self, module: int, pin: int) -> bool:
        """
        Read digital input state
        
        Args:
            module: Module number
            pin: Pin number
            
        Returns:
            True if input is high/active, False otherwise
            
        Raises:
            BusinessRuleViolationException: If reading fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def read_all_inputs(self, module: int) -> Dict[int, bool]:
        """
        Read all input states for a module
        
        Args:
            module: Module number
            
        Returns:
            Dictionary mapping pin numbers to their states
            
        Raises:
            BusinessRuleViolationException: If reading fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def read_multiple_modules(self, modules: List[int]) -> Dict[int, Dict[int, bool]]:
        """
        Read input states for multiple modules
        
        Args:
            modules: List of module numbers
            
        Returns:
            Dictionary mapping module numbers to pin state dictionaries
            
        Raises:
            BusinessRuleViolationException: If reading fails
        """
        pass
    
    # Trigger Management
    @abstractmethod
    async def setup_trigger(
        self, 
        module: int, 
        pin: int, 
        trigger_type: InputTriggerType,
        callback: Callable[[int, int, bool], None],
        debounce_ms: int = 50
    ) -> str:
        """
        Setup input trigger monitoring
        
        Args:
            module: Module number
            pin: Pin number
            trigger_type: Type of trigger to monitor
            callback: Callback function to execute on trigger
            debounce_ms: Debounce time in milliseconds
            
        Returns:
            Trigger ID for later removal
            
        Raises:
            BusinessRuleViolationException: If setup fails
            UnsafeOperationException: If parameters are invalid
        """
        pass
    
    @abstractmethod
    async def setup_multiple_triggers(
        self, 
        trigger_configs: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Setup multiple triggers at once
        
        Args:
            trigger_configs: List of trigger configuration dictionaries
            
        Returns:
            Dictionary mapping configuration names to trigger IDs
            
        Raises:
            BusinessRuleViolationException: If any setup fails
        """
        pass
    
    @abstractmethod
    async def remove_trigger(self, trigger_id: str) -> None:
        """
        Remove input trigger monitoring
        
        Args:
            trigger_id: ID of trigger to remove
            
        Raises:
            BusinessRuleViolationException: If removal fails or trigger not found
        """
        pass
    
    @abstractmethod
    async def remove_all_triggers(self) -> None:
        """
        Remove all active triggers
        
        Raises:
            BusinessRuleViolationException: If removal fails
        """
        pass
    
    @abstractmethod
    async def get_active_triggers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about active triggers
        
        Returns:
            Dictionary mapping trigger IDs to trigger information
        """
        pass
    
    # Monitoring Control
    @abstractmethod
    async def start_monitoring(self) -> None:
        """
        Start input monitoring loop
        
        Raises:
            BusinessRuleViolationException: If monitoring fails to start
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def stop_monitoring(self) -> None:
        """
        Stop input monitoring loop
        
        Raises:
            BusinessRuleViolationException: If monitoring fails to stop
        """
        pass
    
    @abstractmethod
    async def is_monitoring_active(self) -> bool:
        """
        Check if input monitoring is active
        
        Returns:
            True if monitoring is active, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_monitoring_statistics(self) -> Dict[str, Any]:
        """
        Get monitoring performance statistics
        
        Returns:
            Dictionary containing monitoring metrics and statistics
        """
        pass
    
    # Module and Device Information
    @abstractmethod
    async def get_module_info(self, module: int) -> Dict[str, Any]:
        """
        Get information about a specific module
        
        Args:
            module: Module number
            
        Returns:
            Dictionary containing module information and capabilities
            
        Raises:
            BusinessRuleViolationException: If module is invalid
        """
        pass
    
    @abstractmethod
    async def get_available_modules(self) -> List[int]:
        """
        Get list of available module numbers
        
        Returns:
            List of available module numbers
            
        Raises:
            BusinessRuleViolationException: If module detection fails
        """
        pass
    
    @abstractmethod
    async def get_pin_configuration(self, module: int, pin: int) -> Dict[str, Any]:
        """
        Get configuration information for a specific pin
        
        Args:
            module: Module number
            pin: Pin number
            
        Returns:
            Dictionary containing pin configuration and capabilities
            
        Raises:
            BusinessRuleViolationException: If module/pin is invalid
        """
        pass
    
    # Event History and Logging
    @abstractmethod
    async def get_event_history(
        self, 
        module: Optional[int] = None, 
        pin: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get history of input events
        
        Args:
            module: Optional module filter
            pin: Optional pin filter
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries with timestamps and details
        """
        pass
    
    @abstractmethod
    async def clear_event_history(self) -> None:
        """
        Clear stored event history
        
        Raises:
            BusinessRuleViolationException: If clear operation fails
        """
        pass
    
    @abstractmethod
    async def enable_event_logging(self, enabled: bool) -> None:
        """
        Enable or disable event logging
        
        Args:
            enabled: Whether to enable event logging
        """
        pass
    
    # Button Press Utilities
    @abstractmethod
    async def wait_for_button_press(
        self, 
        module: int, 
        pin: int,
        timeout_ms: int = 30000,
        debounce_ms: int = 50
    ) -> bool:
        """
        Wait for button press on specific pin
        
        Args:
            module: Module number
            pin: Pin number
            timeout_ms: Maximum wait time in milliseconds
            debounce_ms: Debounce time in milliseconds
            
        Returns:
            True if button was pressed within timeout, False otherwise
            
        Raises:
            BusinessRuleViolationException: If wait operation fails
        """
        pass
    
    @abstractmethod
    async def wait_for_any_button_press(
        self, 
        module_pins: List[Tuple[int, int]],
        timeout_ms: int = 30000,
        debounce_ms: int = 50
    ) -> Optional[Tuple[int, int]]:
        """
        Wait for button press on any of the specified pins
        
        Args:
            module_pins: List of (module, pin) tuples to monitor
            timeout_ms: Maximum wait time in milliseconds
            debounce_ms: Debounce time in milliseconds
            
        Returns:
            (module, pin) tuple of pressed button, or None if timeout
            
        Raises:
            BusinessRuleViolationException: If wait operation fails
        """
        pass
    
    # Safety and Validation
    @abstractmethod
    async def validate_module_pin(self, module: int, pin: int) -> bool:
        """
        Validate if module and pin combination is valid
        
        Args:
            module: Module number
            pin: Pin number
            
        Returns:
            True if module/pin is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_debounce_time(self, debounce_ms: int) -> bool:
        """
        Validate if debounce time is within acceptable range
        
        Args:
            debounce_ms: Debounce time in milliseconds
            
        Returns:
            True if debounce time is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """
        Get input device information and capabilities
        
        Returns:
            Dictionary containing device specifications and capabilities
        """
        pass
    
    @abstractmethod
    async def run_self_test(self) -> Dict[str, Any]:
        """
        Run input device self-test diagnostics
        
        Returns:
            Dictionary containing test results and system health status
            
        Raises:
            BusinessRuleViolationException: If self-test fails
        """
        pass