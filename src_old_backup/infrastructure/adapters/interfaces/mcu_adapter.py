"""
MCU Adapter Interface

Defines the contract for MCU device adapters.
Provides business logic abstraction over MCU controllers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable

from ....domain.entities.hardware_device import HardwareDevice
from ....domain.value_objects.measurements import TemperatureValue
from ....application.interfaces.mcu_service import TestMode, MCUStatus
from ..base import HardwareAdapterBase


class MCUAdapter(HardwareAdapterBase):
    """
    Abstract interface for MCU device adapters
    
    Provides business logic layer for MCU operations including
    temperature control, test mode management, and safety enforcement.
    """
    
    def __init__(self, vendor: str, device_subtype: str = "mcu"):
        """
        Initialize MCU adapter
        
        Args:
            vendor: MCU device vendor name
            device_subtype: Specific type of MCU device
        """
        super().__init__(f"mcu_{device_subtype}", vendor)
        self._device_subtype = device_subtype
        self._monitoring_sessions: Dict[str, Dict[str, Any]] = {}
        self._current_mode: Optional[TestMode] = None
        self._safety_limits: Dict[str, TemperatureValue] = {}
    
    @property
    def device_subtype(self) -> str:
        """Get device subtype"""
        return self._device_subtype
    
    @property
    def current_test_mode(self) -> Optional[TestMode]:
        """Get current test mode"""
        return self._current_mode
    
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
        Set complete temperature profile with safety validation
        
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
        Set operating temperature target with safety checks
        
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
        Set fan speed level with validation
        
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
        Initialize MCU with operation parameters and safety validation
        
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
        Get MCU device information and capabilities
        
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
    
    # Helper methods for safety enforcement
    def _validate_fan_speed_range(self, level: int) -> None:
        """Validate fan speed is within acceptable range"""
        from ....domain.exceptions.business_rule_exceptions import BusinessRuleViolationException
        
        if not (1 <= level <= 10):
            raise BusinessRuleViolationException(
                "INVALID_FAN_SPEED",
                f"Fan speed level must be between 1-10, got {level}",
                {"level": level, "valid_range": "1-10"}
            )
    
    def _validate_hold_time(self, hold_time_ms: int) -> None:
        """Validate hold time is within acceptable range"""
        from ....domain.exceptions.business_rule_exceptions import BusinessRuleViolationException
        
        if not (100 <= hold_time_ms <= 60000):  # 100ms to 60s
            raise BusinessRuleViolationException(
                "INVALID_HOLD_TIME",
                f"Hold time must be between 100-60000ms, got {hold_time_ms}ms",
                {"hold_time_ms": hold_time_ms, "valid_range": "100-60000ms"}
            )
    
    def _validate_monitoring_interval(self, interval_ms: int) -> None:
        """Validate monitoring interval is reasonable"""
        from ....domain.exceptions.business_rule_exceptions import BusinessRuleViolationException
        
        if not (100 <= interval_ms <= 10000):  # 100ms to 10s
            raise BusinessRuleViolationException(
                "INVALID_MONITORING_INTERVAL",
                f"Monitoring interval must be between 100-10000ms, got {interval_ms}ms",
                {"interval_ms": interval_ms, "valid_range": "100-10000ms"}
            )
    
    def _validate_temperature_safety(
        self, 
        operating_temp: TemperatureValue, 
        upper_temp: TemperatureValue,
        cooling_temp: TemperatureValue
    ) -> None:
        """Validate temperature profile safety"""
        from ....domain.exceptions.business_rule_exceptions import UnsafeOperationException
        
        # Convert all to Celsius for comparison
        op_celsius = operating_temp.to_celsius()
        upper_celsius = upper_temp.to_celsius()
        cool_celsius = cooling_temp.to_celsius()
        
        if op_celsius >= upper_celsius:
            raise UnsafeOperationException(
                "UNSAFE_TEMPERATURE_PROFILE",
                f"Operating temperature ({op_celsius}°C) must be below upper limit ({upper_celsius}°C)",
                {"operating_temp": op_celsius, "upper_temp": upper_celsius}
            )
        
        if cool_celsius >= op_celsius:
            raise UnsafeOperationException(
                "UNSAFE_TEMPERATURE_PROFILE", 
                f"Cooling temperature ({cool_celsius}°C) must be below operating temperature ({op_celsius}°C)",
                {"cooling_temp": cool_celsius, "operating_temp": op_celsius}
            )
        
        # Safety limits for MCU operations
        if upper_celsius > 150:  # Conservative upper limit
            raise UnsafeOperationException(
                "TEMPERATURE_TOO_HIGH",
                f"Upper temperature ({upper_celsius}°C) exceeds safety limit (150°C)",
                {"upper_temp": upper_celsius, "safety_limit": 150}
            )
    
    def get_monitoring_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about active monitoring sessions
        
        Returns:
            Dictionary of active monitoring sessions
        """
        return {
            session_id: {
                "callback": session["callback"].__name__ if hasattr(session["callback"], '__name__') else str(session["callback"]),
                "interval_ms": session.get("interval_ms", "unknown"),
                "started_at": session.get("started_at", "unknown")
            }
            for session_id, session in self._monitoring_sessions.items()
        }