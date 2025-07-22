"""
Input Adapter Interface

Defines the contract for input device adapters (DIO, buttons, triggers).
Provides business logic abstraction over input controllers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional, List
from enum import Enum

from ....domain.entities.hardware_device import HardwareDevice
from ..base import HardwareAdapterBase


class InputTriggerType(Enum):
    """Input trigger types"""
    BUTTON_PRESS = "button_press"
    DIGITAL_HIGH = "digital_high"
    DIGITAL_LOW = "digital_low"
    DIGITAL_CHANGE = "digital_change"


class InputAdapter(HardwareAdapterBase):
    """
    Abstract interface for input device adapters
    
    Provides business logic layer for input devices like DIO modules.
    Handles input event detection and trigger management.
    """
    
    def __init__(self, vendor: str, device_subtype: str = "dio"):
        """
        Initialize input adapter
        
        Args:
            vendor: Input device vendor name
            device_subtype: Specific type of input device (dio, button, etc.)
        """
        super().__init__(f"input_{device_subtype}", vendor)
        self._device_subtype = device_subtype
        self._trigger_callbacks: Dict[str, Callable] = {}
    
    @property
    def device_subtype(self) -> str:
        """Get device subtype"""
        return self._device_subtype
    
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
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def remove_trigger(self, trigger_id: str) -> None:
        """
        Remove input trigger monitoring
        
        Args:
            trigger_id: ID of trigger to remove
            
        Raises:
            BusinessRuleViolationException: If removal fails
        """
        pass
    
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
    async def get_module_info(self, module: int) -> Dict[str, Any]:
        """
        Get information about a specific module
        
        Args:
            module: Module number
            
        Returns:
            Module information including pin count, capabilities
            
        Raises:
            BusinessRuleViolationException: If info retrieval fails
            HardwareNotReadyException: If device not ready
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
            HardwareNotReadyException: If device not ready
        """
        pass
    
    def get_active_triggers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about active triggers
        
        Returns:
            Dictionary mapping trigger IDs to trigger information
        """
        return {
            trigger_id: {
                "callback": callback.__name__ if hasattr(callback, '__name__') else str(callback),
                "registered_at": "unknown"  # Could be enhanced with timestamp tracking
            }
            for trigger_id, callback in self._trigger_callbacks.items()
        }