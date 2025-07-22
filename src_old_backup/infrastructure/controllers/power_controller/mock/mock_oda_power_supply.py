"""
Mock ODA Power Supply Controller

This module provides a mock implementation of the ODA power supply controller
for testing and development purposes. It simulates all power supply operations
without requiring actual hardware.
"""

from typing import Optional, Dict, Any
from random import uniform

from loguru import logger

from ....domain.enums.hardware_status import HardwareStatus
from ..exceptions import ODAError, ODAConnectionError, ODAOperationError


class MockOdaPowerSupply:
    """Mock ODA power supply controller for testing"""

    def __init__(self, host: str, port: int = 5025, timeout: float = 2.0):
        self.controller_type = "power"
        self.vendor = "oda_mock"
        self.connection_info = f"{host}:{port}"
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        
        # Power supply specific attributes
        self.interface = 'ethernet'
        self.address = f"{host}:{port}"
        self.channels = {}
        self.host = host
        self.port = port
        self.timeout = timeout
        
        # Initialize mock channels (assume 3 channels for ODA power supply)
        self.max_channels = 3
        for ch in range(1, self.max_channels + 1):
            self.channels[ch] = {
                'output_enabled': False,
                'voltage_setting': 0.0,
                'current_setting': 0.0,
                'voltage_actual': 0.0,
                'current_actual': 0.0,
                'ovp_setting': 30.0,  # Default OVP
                'ocp_setting': 3.0,   # Default OCP
                'protection_status': {
                    'ovp': False,
                    'ocp': False,
                    'otp': False
                }
            }
        
        # Device state
        self.device_identity = "Mock ODA Power Supply, Version 1.0"
        self.noise_amplitude = 0.01  # Simulate measurement noise

    def connect(self) -> bool:
        """Connect to mock power supply"""
        try:
            # Simulate connection logic
            logger.info(f"Mock ODA power supply connected to {self.host}:{self.port}")
            self.status = HardwareStatus.CONNECTED
            return True
        except Exception as e:
            logger.error(f"Mock power supply connection failed ({type(e).__name__}): {e}")
            self.status = HardwareStatus.DISCONNECTED
            raise ODAConnectionError(f"Mock power supply connection failed: {e}", command="CONNECT")

    def disconnect(self) -> None:
        """Disconnect mock power supply"""
        logger.info("Mock ODA power supply disconnected")
        self.status = HardwareStatus.DISCONNECTED

    def is_alive(self) -> bool:
        """Check if mock power supply is alive"""
        return self.status == HardwareStatus.CONNECTED

    def get_identity(self) -> str:
        """Get device identification"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Mock ODA power supply not connected", command="GET_IDENTITY")
        return self.device_identity

    def reset(self) -> None:
        """Reset device to default state"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Mock ODA power supply not connected", command="RESET")
        
        for ch in range(1, self.max_channels + 1):
            self.channels[ch]['output_enabled'] = False
            self.channels[ch]['voltage_setting'] = 0.0
            self.channels[ch]['current_setting'] = 0.0
            self.channels[ch]['voltage_actual'] = 0.0
            self.channels[ch]['current_actual'] = 0.0
            self.channels[ch]['protection_status'] = {
                'ovp': False,
                'ocp': False,
                'otp': False
            }
        
        logger.info("Mock ODA power supply reset to default state")

    def set_output_state(self, channel: int, state: bool) -> None:
        """Enable/disable channel output"""
        self._check_channel(channel)
        
        self.channels[channel]['output_enabled'] = state
        
        # When output is disabled, set actual values to 0
        if not state:
            self.channels[channel]['voltage_actual'] = 0.0
            self.channels[channel]['current_actual'] = 0.0
        else:
            # When enabled, set actual values to settings
            self.channels[channel]['voltage_actual'] = self.channels[channel]['voltage_setting']
            self.channels[channel]['current_actual'] = min(0.1, self.channels[channel]['current_setting'])  # Simulate light load
        
        logger.info(f"Mock ODA channel {channel} output {'enabled' if state else 'disabled'}")

    def get_output_state(self, channel: int) -> bool:
        """Get channel output state"""
        self._check_channel(channel)
        
        return self.channels[channel]['output_enabled']

    def set_voltage(self, channel: int, voltage: float) -> None:
        """Set target voltage"""
        self._check_channel(channel)
        
        try:
            # Validate voltage range (0-30V for typical power supply)
            if voltage < 0 or voltage > 30:
                raise ODAOperationError(f"Invalid voltage: {voltage}V (valid range: 0-30V)", command="SET_VOLTAGE")
        except ODAError:
            # Re-raise ODA errors to maintain consistency with real controller
            raise
        except Exception as e:
            logger.error(f"Mock set voltage failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Mock set voltage failed: {e}", command="SET_VOLTAGE")
        
        self.channels[channel]['voltage_setting'] = voltage
        
        # Update actual voltage if output is enabled
        if self.channels[channel]['output_enabled']:
            self.channels[channel]['voltage_actual'] = voltage
        
        logger.info(f"Mock ODA channel {channel} voltage set to {voltage}V")

    def get_voltage_setting(self, channel: int) -> float:
        """Get voltage setting"""
        self._check_channel(channel)
        
        return self.channels[channel]['voltage_setting']

    def get_voltage_actual(self, channel: int) -> float:
        """Get actual output voltage"""
        self._check_channel(channel)
        
        # Add some noise to simulate real measurement
        voltage = self.channels[channel]['voltage_actual']
        if voltage > 0:
            noise = uniform(-self.noise_amplitude, self.noise_amplitude)
            voltage += noise
        
        return voltage

    def set_current(self, channel: int, current: float) -> None:
        """Set current limit"""
        self._check_channel(channel)
        
        try:
            # Validate current range (0-3A for typical power supply)
            if current < 0 or current > 3:
                raise ODAOperationError(f"Invalid current: {current}A (valid range: 0-3A)", command="SET_CURRENT")
        except ODAError:
            # Re-raise ODA errors to maintain consistency with real controller
            raise
        except Exception as e:
            logger.error(f"Mock set current failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Mock set current failed: {e}", command="SET_CURRENT")
        
        self.channels[channel]['current_setting'] = current
        
        logger.info(f"Mock ODA channel {channel} current limit set to {current}A")

    def get_current_setting(self, channel: int) -> float:
        """Get current setting"""
        self._check_channel(channel)
        
        return self.channels[channel]['current_setting']

    def get_current_actual(self, channel: int) -> float:
        """Get actual output current"""
        self._check_channel(channel)
        
        # Add some noise to simulate real measurement
        current = self.channels[channel]['current_actual']
        if current > 0:
            noise = uniform(-self.noise_amplitude * 0.1, self.noise_amplitude * 0.1)
            current += noise
        
        return current

    def set_ovp(self, channel: int, voltage: float) -> None:
        """Set over-voltage protection"""
        self._check_channel(channel)
        
        if voltage < 0 or voltage > 33:  # Slightly above max output
            logger.error(f"Invalid OVP voltage: {voltage}V")
            raise ODAOperationError(f"Invalid OVP voltage: {voltage}V (valid range: 0-33V)", command="SET_OVP")
        
        self.channels[channel]['ovp_setting'] = voltage
        logger.info(f"Mock ODA channel {channel} OVP set to {voltage}V")

    def set_ocp(self, channel: int, current: float) -> None:
        """Set over-current protection"""
        self._check_channel(channel)
        
        if current < 0 or current > 3.3:  # Slightly above max output
            logger.error(f"Invalid OCP current: {current}A")
            raise ODAOperationError(f"Invalid OCP current: {current}A (valid range: 0-3.3A)", command="SET_OCP")
        
        self.channels[channel]['ocp_setting'] = current
        logger.info(f"Mock ODA channel {channel} OCP set to {current}A")

    def get_protection_status(self, channel: int) -> Dict[str, bool]:
        """Get protection status (OVP, OCP, OTP, etc.)"""
        self._check_channel(channel)
        
        # Check for protection conditions
        status = self.channels[channel]['protection_status'].copy()
        
        # Simulate OVP if voltage exceeds setting
        if self.channels[channel]['voltage_actual'] > self.channels[channel]['ovp_setting']:
            status['ovp'] = True
        
        # Simulate OCP if current exceeds setting
        if self.channels[channel]['current_actual'] > self.channels[channel]['ocp_setting']:
            status['ocp'] = True
        
        return status

    def clear_protection(self, channel: int) -> None:
        """Clear protection faults"""
        self._check_channel(channel)
        
        self.channels[channel]['protection_status'] = {
            'ovp': False,
            'ocp': False,
            'otp': False
        }
        
        logger.info(f"Mock ODA channel {channel} protection cleared")

    def measure_all(self, channel: int) -> Dict[str, float]:
        """Measure voltage, current, power"""
        self._check_channel(channel)
        
        voltage = self.get_voltage_actual(channel)
        current = self.get_current_actual(channel)
        
        power = voltage * current
        
        return {
            'voltage': voltage,
            'current': current,
            'power': power
        }

    def _check_channel(self, channel: int) -> None:
        """Check if channel number is valid"""
        if self.status != HardwareStatus.CONNECTED:
            logger.error("Mock ODA power supply not initialized")
            raise ODAConnectionError("Mock ODA power supply not connected", command="CHECK_CHANNEL")
        
        if channel not in self.channels:
            logger.error(f"Invalid channel: {channel} (valid: {list(self.channels.keys())})")
            raise ODAError(f"Invalid channel: {channel} (valid: {list(self.channels.keys())})", command="CHECK_CHANNEL")

    # Additional helper methods for testing
    def simulate_load(self, channel: int, current: float) -> None:
        """Simulate load current for testing"""
        self._check_channel(channel)
        
        # Limit current to the setting
        limited_current = min(current, self.channels[channel]['current_setting'])
        self.channels[channel]['current_actual'] = limited_current
        
        logger.debug(f"Mock ODA channel {channel} load simulated: {limited_current}A")

    def simulate_protection_fault(self, channel: int, fault_type: str) -> None:
        """Simulate protection fault for testing"""
        self._check_channel(channel)
        
        valid_faults = ['ovp', 'ocp', 'otp']
        if fault_type not in valid_faults:
            logger.error(f"Invalid fault type: {fault_type}")
            raise ODAOperationError(f"Invalid fault type: {fault_type} (valid: {valid_faults})", command="SIMULATE_FAULT")
        
        self.channels[channel]['protection_status'][fault_type] = True
        
        # Disable output when fault occurs
        self.channels[channel]['output_enabled'] = False
        self.channels[channel]['voltage_actual'] = 0.0
        self.channels[channel]['current_actual'] = 0.0
        
        logger.warning(f"Mock ODA channel {channel} {fault_type.upper()} fault simulated")

    def get_mock_state(self) -> Dict[str, Any]:
        """Get internal mock state for testing verification"""
        return {
            'channels': self.channels,
            'device_identity': self.device_identity,
            'noise_amplitude': self.noise_amplitude
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