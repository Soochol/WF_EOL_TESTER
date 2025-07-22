"""
Mock LMA Controller

This module provides a mock implementation of the LMA controller
for testing and development purposes. It simulates all MCU operations
without requiring actual hardware.
"""

import time
import threading
from typing import Optional, Dict, Any
from random import uniform

from loguru import logger

from ....domain.enums.hardware_status import HardwareStatus
from enum import IntEnum


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


class MockUARTCommunication:
    """Mock UART communication for testing"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 2.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_connected = False
        self.boot_complete_sent = False
        
    def connect(self) -> bool:
        """Mock UART connection"""
        self.is_connected = True
        logger.debug(f"Mock UART connected to {self.port}")
        return True
        
    def disconnect(self) -> None:
        """Mock UART disconnection"""
        self.is_connected = False
        self.boot_complete_sent = False
        logger.debug("Mock UART disconnected")
        
    def wait_for_response(self, timeout: float = 1.0) -> Optional[object]:
        """Simulate boot complete signal response"""
        if not self.is_connected:
            return None
            
        # Simulate boot complete signal on first call
        if not self.boot_complete_sent:
            self.boot_complete_sent = True
            # Create a mock response object with boot complete status
            class MockResponse:
                def __init__(self):
                    from ..lma.constants import STATUS_BOOT_COMPLETE
                    self.command = STATUS_BOOT_COMPLETE
                    self.data = [STATUS_BOOT_COMPLETE]
                    
            logger.debug("Mock UART sending boot complete signal")
            return MockResponse()
            
        return None


class MockLMAController:
    """Mock LMA controller for testing"""

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 2.0):
        self.controller_type = "mcu"
        self.vendor = "lma_mock"
        self.connection_info = f'Port: {port}'
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        
        # MCU-specific attributes
        self.current_status = MCUStatus.IDLE
        self.status_callback = None
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        
        # Mock UART communication
        self.uart = MockUARTCommunication(port, baudrate, timeout)
        
        # Mock state
        self.current_temp = 25.0  # Room temperature
        self.target_temp = 25.0
        self.upper_temp_limit = 125.0
        self.operating_temp = 85.0
        self.cooling_temp = 25.0
        self.standby_temp = 40.0
        self.hold_time_ms = 1000
        
        self.fan_speed = 1
        self.test_mode = TestMode.MODE_1
        
        # Temperature simulation
        self.heating_rate = 2.0  # degrees per second
        self.cooling_rate = 1.5  # degrees per second
        self.temp_noise = 0.5    # temperature noise amplitude
        
        # Temperature simulation
        self.simulation_thread = None
        self.simulation_active = False
    
    def set_status_callback(self, callback) -> None:
        """Set status update callback"""
        self.status_callback = callback
    
    def _notify_status_change(self, status: MCUStatus, data=None) -> None:
        """Notify status change to callback"""
        self.current_status = status
        if self.status_callback:
            try:
                self.status_callback(status, data or {})
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

    def connect(self) -> bool:
        """Connect to mock LMA controller"""
        logger.info(f"Mock LMA controller connected to {self.port}")
        self.uart.connect()  # Connect mock UART
        self.status = HardwareStatus.CONNECTED
        self.current_status = MCUStatus.IDLE
        self._start_temperature_simulation()
        return True

    def disconnect(self) -> None:
        """Disconnect mock LMA controller"""
        self._stop_temperature_simulation()
        self.uart.disconnect()  # Disconnect mock UART
        logger.info("Mock LMA controller disconnected")
        self.status = HardwareStatus.DISCONNECTED

    def is_alive(self) -> bool:
        """Check if mock controller is alive"""
        return self.status == HardwareStatus.CONNECTED

    def enter_test_mode(self, mode: TestMode) -> bool:
        """Enter specified test mode"""
        from ..exceptions import LMAConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        self.test_mode = mode
        logger.info(f"Mock LMA entered test mode {mode}")
        return True

    def get_test_mode(self) -> Optional[TestMode]:
        """Get current test mode"""
        from ..exceptions import LMAConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        return self.test_mode

    def set_upper_temperature(self, temperature: float) -> None:
        """Set upper temperature limit"""
        from ..exceptions import LMAConnectionError, LMAError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        if temperature < 0 or temperature > 200:
            logger.error(f"Invalid upper temperature: {temperature}°C")
            raise LMAError(f"Invalid upper temperature: {temperature}°C (valid range: 0-200°C)")
        
        self.upper_temp_limit = temperature
        logger.info(f"Mock LMA upper temperature limit set to {temperature}°C")

    def set_operating_temperature(self, temperature: float) -> None:
        """Set operating temperature"""
        from ..exceptions import LMAConnectionError, LMAError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        if temperature < 0 or temperature > self.upper_temp_limit:
            logger.error(f"Invalid operating temperature: {temperature}°C")
            raise LMAError(f"Invalid operating temperature: {temperature}°C (max: {self.upper_temp_limit}°C)")
        
        self.operating_temp = temperature
        self.target_temp = temperature
        logger.info(f"Mock LMA operating temperature set to {temperature}°C")

    def set_cooling_temperature(self, temperature: float) -> None:
        """Set cooling temperature"""
        from ..exceptions import LMAConnectionError, LMAError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        if temperature < 0 or temperature > 100:
            logger.error(f"Invalid cooling temperature: {temperature}°C")
            raise LMAError(f"Invalid cooling temperature: {temperature}°C (valid range: 0-100°C)")
        
        self.cooling_temp = temperature
        logger.info(f"Mock LMA cooling temperature set to {temperature}°C")

    def get_temperature(self) -> float:
        """Get current temperature"""
        from ..exceptions import LMAConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        # Add noise to simulate real sensor
        noise = uniform(-self.temp_noise, self.temp_noise)
        return self.current_temp + noise

    def set_fan_speed(self, level: int) -> None:
        """Set fan speed level"""
        from ..exceptions import LMAConnectionError, LMAError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        if level < 1 or level > 10:
            logger.error(f"Invalid fan speed: {level} (valid: 1-10)")
            raise LMAError(f"Invalid fan speed: {level} (valid range: 1-10)")
        
        self.fan_speed = level
        logger.info(f"Mock LMA fan speed set to level {level}")

    def get_fan_speed(self) -> int:
        """Get current fan speed level"""
        from ..exceptions import LMAConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        return self.fan_speed

    def initialize_lma(self, operating_temp: float, standby_temp: float, 
                      hold_time_ms: int) -> None:
        """Initialize LMA with parameters"""
        from ..exceptions import LMAConnectionError, LMAError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        # Validate parameters
        if operating_temp < 0 or operating_temp > self.upper_temp_limit:
            logger.error(f"Invalid operating temperature: {operating_temp}°C")
            raise LMAError(f"Invalid operating temperature: {operating_temp}°C (max: {self.upper_temp_limit}°C)")
        
        if standby_temp < 0 or standby_temp > operating_temp:
            logger.error(f"Invalid standby temperature: {standby_temp}°C")
            raise LMAError(f"Invalid standby temperature: {standby_temp}°C (max: {operating_temp}°C)")
        
        if hold_time_ms < 0 or hold_time_ms > 60000:
            logger.error(f"Invalid hold time: {hold_time_ms}ms")
            raise LMAError(f"Invalid hold time: {hold_time_ms}ms (valid range: 0-60000ms)")
        
        self.operating_temp = operating_temp
        self.standby_temp = standby_temp
        self.hold_time_ms = hold_time_ms
        
        logger.info(f"Mock LMA initialized: op_temp={operating_temp}°C, "
                   f"standby_temp={standby_temp}°C, hold_time={hold_time_ms}ms")

    def get_mcu_status(self) -> MCUStatus:
        """Get current MCU status"""
        return self.current_status

    def notify_stroke_init_complete(self) -> None:
        """Notify MCU that robot stroke initialization is complete"""
        from ..exceptions import LMAConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            raise LMAConnectionError("Mock LMA controller not connected")
        
        logger.info("Mock LMA stroke initialization complete notification")

    def get_status(self) -> MCUStatus:
        """Get current thermal status (alias for get_mcu_status)"""
        return self.get_mcu_status()


    def _start_temperature_simulation(self) -> None:
        """Start temperature simulation thread"""
        if self.simulation_active:
            return
        
        self.simulation_active = True
        self.simulation_thread = threading.Thread(target=self._temperature_simulation_loop, daemon=True)
        self.simulation_thread.start()

    def _stop_temperature_simulation(self) -> None:
        """Stop temperature simulation thread"""
        if not self.simulation_active:
            return
        
        self.simulation_active = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)

    def _temperature_simulation_loop(self) -> None:
        """Temperature simulation loop"""
        while self.simulation_active:
            try:
                # Calculate temperature change based on target
                temp_diff = self.target_temp - self.current_temp
                
                if abs(temp_diff) > 0.5:  # Not at target temperature
                    if temp_diff > 0:  # Need to heat
                        change = min(self.heating_rate * 0.1, temp_diff)
                    else:  # Need to cool
                        change = max(-self.cooling_rate * 0.1, temp_diff)
                    
                    # Apply fan cooling effect
                    cooling_effect = (self.fan_speed / 10.0) * 0.2
                    if self.current_temp > 25.0:  # Only cool if above room temp
                        change -= cooling_effect
                    
                    self.current_temp += change
                
                time.sleep(0.1)  # Update every 100ms for smooth simulation
                
            except Exception as e:
                logger.error(f"Error in temperature simulation: {e}")
                break

    # Additional helper methods for testing
    def simulate_temperature_ramp(self, target_temp: float, ramp_rate: float = None) -> None:
        """Simulate temperature ramp for testing"""
        self.target_temp = target_temp
        if ramp_rate is not None:
            if target_temp > self.current_temp:
                self.heating_rate = ramp_rate
            else:
                self.cooling_rate = ramp_rate
        
        logger.info(f"Mock LMA temperature ramp to {target_temp}°C initiated")

    def simulate_overheat_condition(self) -> None:
        """Simulate overheat condition"""
        self.current_temp = self.upper_temp_limit + 5.0
        self.current_status = MCUStatus.ERROR
        self._notify_status_change(MCUStatus.ERROR, {'temperature': self.current_temp})
        logger.warning("Mock LMA overheat condition simulated")

    def reset_error_condition(self) -> None:
        """Reset error condition"""
        self.current_temp = min(self.current_temp, self.upper_temp_limit - 5.0)
        self.current_status = MCUStatus.IDLE
        self._notify_status_change(MCUStatus.IDLE)
        logger.info("Mock LMA error condition reset")

    def get_mock_state(self) -> Dict[str, Any]:
        """Get internal mock state for testing verification"""
        return {
            'current_temp': self.current_temp,
            'target_temp': self.target_temp,
            'operating_temp': self.operating_temp,
            'cooling_temp': self.cooling_temp,
            'standby_temp': self.standby_temp,
            'upper_temp_limit': self.upper_temp_limit,
            'fan_speed': self.fan_speed,
            'test_mode': self.test_mode,
            'status': self.current_status,
            'simulation_active': self.simulation_active
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> bool:
        """Context manager exit"""
        # Always disconnect regardless of exception
        try:
            self.disconnect()
        except Exception as e:
            logger.warning(f"Error during disconnect in context manager: {e}")
        # Return False to propagate any exceptions
        return False