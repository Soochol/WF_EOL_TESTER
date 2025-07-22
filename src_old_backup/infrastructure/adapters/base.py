"""
Base Adapter Classes

Common functionality and interfaces for all hardware adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger

from ...domain.entities.hardware_device import HardwareDevice
from ...domain.enums.hardware_status import HardwareStatus
from ...domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    HardwareNotReadyException
)


class HardwareAdapterBase(ABC):
    """
    Abstract base class for all hardware adapters
    
    Provides common functionality for hardware abstraction and
    domain object conversion.
    """
    
    def __init__(self, device_type: str, vendor: str):
        """
        Initialize hardware adapter base
        
        Args:
            device_type: Type of hardware device
            vendor: Hardware vendor name
        """
        self._device_type = device_type
        self._vendor = vendor
        self._hardware_device: Optional[HardwareDevice] = None
    
    @property
    def device_type(self) -> str:
        """Get device type"""
        return self._device_type
    
    @property
    def vendor(self) -> str:
        """Get vendor name"""
        return self._vendor
    
    @property
    def hardware_device(self) -> HardwareDevice:
        """
        Get hardware device entity
        
        Returns:
            HardwareDevice entity
            
        Raises:
            BusinessRuleViolationException: If device not initialized
        """
        if self._hardware_device is None:
            raise BusinessRuleViolationException(
                "HARDWARE_DEVICE_NOT_INITIALIZED",
                f"Hardware device for {self._device_type} not initialized",
                {"device_type": self._device_type, "vendor": self._vendor}
            )
        return self._hardware_device
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to hardware device
        
        Raises:
            BusinessRuleViolationException: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from hardware device
        
        Raises:
            BusinessRuleViolationException: If disconnection fails
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if hardware device is connected
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_hardware_device(self) -> HardwareDevice:
        """
        Get hardware device entity with current status
        
        Returns:
            Updated HardwareDevice entity
        """
        pass
    
    def _validate_connection(self, operation: str) -> None:
        """
        Validate that device is connected before operation
        
        Args:
            operation: Name of operation being performed
            
        Raises:
            HardwareNotReadyException: If device not connected
        """
        if self._hardware_device is None:
            raise HardwareNotReadyException(
                self._device_type,
                "not_initialized",
                operation,
                {"vendor": self._vendor}
            )
        
        if self._hardware_device.status != HardwareStatus.CONNECTED:
            raise HardwareNotReadyException(
                self._device_type,
                "disconnected",
                operation,
                {"vendor": self._vendor, "status": self._hardware_device.status}
            )
    
    def _create_hardware_device(
        self, 
        connection_info: str, 
        device_id: str, 
        capabilities: Dict[str, Any]
    ) -> HardwareDevice:
        """
        Create hardware device entity
        
        Args:
            connection_info: Connection information
            device_id: Device identifier
            capabilities: Device capabilities
            
        Returns:
            HardwareDevice entity
        """
        return HardwareDevice(
            device_type=self._device_type,
            vendor=self._vendor,
            connection_info=connection_info,
            device_id=device_id,
            capabilities=capabilities
        )
    
    def _log_operation(self, operation: str, success: bool = True, error: Optional[str] = None) -> None:
        """
        Log adapter operations for debugging
        
        Args:
            operation: Operation name
            success: Whether operation succeeded
            error: Error message if failed
        """
        if success:
            logger.debug(f"{self._device_type} adapter: {operation} successful")
        else:
            logger.error(f"{self._device_type} adapter: {operation} failed - {error}")