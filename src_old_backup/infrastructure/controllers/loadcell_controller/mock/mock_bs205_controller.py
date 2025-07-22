"""
Mock BS205 Loadcell Controller

This module provides a mock implementation of the BS205 loadcell controller
for testing and development purposes. It simulates all loadcell operations
without requiring actual hardware.
"""

import time
import threading
from typing import Optional, Dict, Any
from random import uniform

from loguru import logger

from ....domain.enums.hardware_status import HardwareStatus
from enum import IntEnum


class LoadcellStatus(IntEnum):
    """Loadcell status enumeration"""
    IDLE = 0
    MEASURING = 1
    HOLD = 2
    ZERO_SETTING = 3
    ERROR = 4


class MockBS205Controller:
    """Mock BS205 loadcell controller for testing"""

    def __init__(self, port: str, indicator_id: int = 1, baudrate: int = 9600, timeout: float = 2.0):
        self.controller_type = "loadcell"
        self.vendor = "bs205_mock"
        self.connection_info = f'Port: {port}'
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        
        # Loadcell-specific attributes
        self.indicator_id = indicator_id
        self.current_status = LoadcellStatus.IDLE
        self.status_callback = None
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        
        # Mock state
        self.current_value = 0.0
        self.hold_enabled = False
        self.held_value = 0.0
        self.zero_offset = 0.0
        self.base_value = 0.0
        self.noise_amplitude = 0.1  # Simulate measurement noise
        
        # Monitoring
        self.monitoring_thread = None
        self.monitoring_active = False
        self.monitoring_interval = 1.0

    def stop_monitoring(self) -> None:
        """Stop monitoring (wrapper for _stop_monitoring_impl)"""
        self._stop_monitoring_impl()

    def start_monitoring(self) -> bool:
        """Start monitoring (wrapper for _start_monitoring_impl)"""
        return self._start_monitoring_impl()
    
    def set_status_callback(self, callback) -> None:
        """Set status update callback"""
        self.status_callback = callback
    
    def _notify_status_change(self, status: LoadcellStatus, data=None) -> None:
        """Notify status change to callback"""
        self.current_status = status
        if self.status_callback:
            try:
                self.status_callback(status, data or {})
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def validate_indicator_id(self, indicator_id: int) -> bool:
        """Validate indicator ID range"""
        return 1 <= indicator_id <= 255

    def connect(self) -> bool:
        """Connect to mock loadcell controller"""
        logger.info(f"Mock BS205 controller connected to {self.port}")
        self.status = HardwareStatus.CONNECTED
        self.current_status = LoadcellStatus.IDLE
        return True

    def disconnect(self) -> None:
        """Disconnect mock loadcell controller"""
        self.stop_monitoring()
        logger.info("Mock BS205 controller disconnected")
        self.status = HardwareStatus.DISCONNECTED

    def is_alive(self) -> bool:
        """Check if mock controller is alive"""
        return self.status == HardwareStatus.CONNECTED

    def read_value(self) -> Optional[float]:
        """Read current loadcell value"""
        from ..exceptions import BS205ConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            raise BS205ConnectionError("Mock BS205 controller not connected")
        
        # Simulate dynamic value with noise
        noise = uniform(-self.noise_amplitude, self.noise_amplitude)
        raw_value = self.base_value + noise
        
        # Apply zero offset
        adjusted_value = raw_value - self.zero_offset
        
        # If hold is enabled, return held value
        if self.hold_enabled:
            return self.held_value
        
        # Update current value
        self.current_value = adjusted_value
        return self.current_value

    def read_raw_data(self) -> Optional[str]:
        """Read raw data string from loadcell"""
        from ..exceptions import BS205ConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            raise BS205ConnectionError("Mock BS205 controller not connected")
        
        value = self.read_value()
        
        # Simulate BS205 protocol format
        return f"ID:{self.indicator_id:02d},ST:00,+{value:08.3f}kg\r\n"

    def auto_zero(self) -> bool:
        """Perform auto zero operation"""
        from ..exceptions import BS205ConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            raise BS205ConnectionError("Mock BS205 controller not connected")
        
        logger.info("Mock BS205 performing auto zero")
        self.current_status = LoadcellStatus.ZERO_SETTING
        self._notify_status_change(LoadcellStatus.ZERO_SETTING)
        
        # Simulate zero setting time
        time.sleep(0.5)
        
        # Set current reading as zero offset
        self.zero_offset = self.base_value
        
        self.current_status = LoadcellStatus.IDLE
        self._notify_status_change(LoadcellStatus.IDLE)
        
        logger.info("Mock BS205 auto zero completed")
        return True

    def set_hold(self, enable: bool) -> bool:
        """Enable or disable hold function"""
        if self.status != HardwareStatus.CONNECTED:
            return False
        
        self.hold_enabled = enable
        
        if enable:
            # Capture current value when enabling hold
            self.held_value = self.current_value
            self.current_status = LoadcellStatus.HOLD
            logger.info(f"Mock BS205 hold enabled, value: {self.held_value:.3f}")
        else:
            self.current_status = LoadcellStatus.IDLE
            logger.info("Mock BS205 hold disabled")
        
        self._notify_status_change(self.current_status)
        return True

    def is_hold_enabled(self) -> Optional[bool]:
        """Check if hold function is enabled"""
        if self.status != HardwareStatus.CONNECTED:
            return None
        
        return self.hold_enabled

    def set_indicator_id(self, indicator_id: int) -> bool:
        """Set indicator ID"""
        if not self.validate_indicator_id(indicator_id):
            return False
        
        self.indicator_id = indicator_id
        logger.info(f"Mock BS205 indicator ID set to {indicator_id}")
        return True

    def get_indicator_id(self) -> int:
        """Get current indicator ID"""
        return self.indicator_id

    def get_loadcell_status(self) -> LoadcellStatus:
        """Get current loadcell status"""
        return self.current_status

    def _start_monitoring_impl(self) -> bool:
        """Start monitoring implementation"""
        if self.monitoring_active:
            return True
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Mock BS205 monitoring started")
        return True

    def _stop_monitoring_impl(self) -> None:
        """Stop monitoring implementation"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        
        logger.info("Mock BS205 monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Monitoring loop implementation"""
        while self.monitoring_active:
            try:
                # Read current value to trigger updates
                value = self.read_value()
                
                # Simulate status changes based on conditions
                if self.hold_enabled:
                    status = LoadcellStatus.HOLD
                elif abs(value or 0) > 1000:  # Simulate overload condition
                    status = LoadcellStatus.ERROR
                else:
                    status = LoadcellStatus.MEASURING if self.monitoring_active else LoadcellStatus.IDLE
                
                if status != self.current_status:
                    self._notify_status_change(status, {'value': value})
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in mock BS205 monitoring: {e}")
                break

    # Additional helper methods for testing
    def simulate_load_change(self, new_value: float) -> None:
        """Simulate load change for testing purposes"""
        self.base_value = new_value
        logger.debug(f"Mock BS205 base value changed to {new_value}")

    def simulate_noise_level(self, amplitude: float) -> None:
        """Set noise amplitude for testing"""
        self.noise_amplitude = amplitude
        logger.debug(f"Mock BS205 noise amplitude set to {amplitude}")

    def simulate_error_condition(self) -> None:
        """Simulate error condition"""
        self.current_status = LoadcellStatus.ERROR
        self._notify_status_change(LoadcellStatus.ERROR)
        logger.warning("Mock BS205 error condition simulated")

    def reset_error_condition(self) -> None:
        """Reset error condition"""
        self.current_status = LoadcellStatus.IDLE
        self._notify_status_change(LoadcellStatus.IDLE)
        logger.info("Mock BS205 error condition reset")

    def get_mock_state(self) -> Dict[str, Any]:
        """Get internal mock state for testing verification"""
        return {
            'current_value': self.current_value,
            'base_value': self.base_value,
            'zero_offset': self.zero_offset,
            'hold_enabled': self.hold_enabled,
            'held_value': self.held_value,
            'monitoring_active': self.monitoring_active,
            'status': self.current_status
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