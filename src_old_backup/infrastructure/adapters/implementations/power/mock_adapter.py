"""
Mock Power Adapter

Mock implementation of PowerAdapter for testing and development.
Provides simulated power supply behavior without hardware dependencies.
"""

import asyncio
import random
from typing import Dict, Any, Optional
from loguru import logger

from ....domain.value_objects.measurements import VoltageValue, CurrentValue
from ....domain.entities.hardware_device import HardwareDevice
from ....domain.enums.hardware_status import HardwareStatus
from ....domain.enums.measurement_units import MeasurementUnit
from ....domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    HardwareNotReadyException,
    UnsafeOperationException
)

from ...interfaces.power_adapter import PowerAdapter


class MockPowerAdapter(PowerAdapter):
    """
    Mock Power Supply adapter implementation
    
    Provides simulated power supply behavior for testing and development
    without requiring actual hardware.
    """
    
    def __init__(self, device_id: str = "mock_power_001"):
        """
        Initialize mock power adapter
        
        Args:
            device_id: Mock device identifier
        """
        super().__init__("mock")
        self._device_id = device_id
        self._is_connected = False
        self._output_enabled = False
        self._voltage_setting = 0.0
        self._current_setting = 1.0
        self._ovp_setting = 65.0  # Slightly above max voltage
        self._ocp_setting = 11.0  # Slightly above max current
        self._protection_status = {"ovp": False, "ocp": False, "otp": False}
        self._hardware_device = self._create_mock_hardware_device()
    
    def _create_mock_hardware_device(self) -> HardwareDevice:
        """Create mock hardware device entity"""
        return self._create_hardware_device(
            connection_info="mock://power_supply",
            device_id=self._device_id,
            capabilities={
                "max_voltage": 30.0,  # V (lower than ODA for testing)
                "max_current": 5.0,   # A (lower than ODA for testing)
                "channels": 1,
                "ovp_protection": True,
                "ocp_protection": True,
                "otp_protection": True,
                "remote_control": True,
                "output_control": True,
                "protection_clearing": True,
                "measurement_accuracy": 0.05,  # % (better accuracy for testing)
                "simulation_mode": True
            }
        )
    
    def _validate_channel(self, channel: int) -> None:
        """Validate channel number (Mock supports only channel 1)"""
        if channel != 1:
            raise BusinessRuleViolationException(
                "INVALID_CHANNEL",
                f"Invalid channel {channel}. Mock power supply only supports channel 1",
                {"channel": channel, "max_channels": 1}
            )
    
    async def connect(self) -> None:
        """Simulate connection to mock device"""
        try:
            # Simulate connection delay
            await asyncio.sleep(0.1)
            
            # Simulate occasional connection failures for testing
            if random.random() < 0.03:  # 3% failure rate
                raise BusinessRuleViolationException(
                    "MOCK_CONNECTION_FAILED",
                    "Simulated connection failure for testing",
                    {"device_id": self._device_id}
                )
            
            self._is_connected = True
            self._hardware_device.set_status(HardwareStatus.CONNECTED)
            self._log_operation("connect", True)
            
        except BusinessRuleViolationException:
            raise
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("connect", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_CONNECTION_FAILED",
                f"Failed to connect to mock power supply: {str(e)}",
                {"device_id": self._device_id}
            )
    
    async def disconnect(self) -> None:
        """Simulate disconnection with safety measures"""
        try:
            # Safety: Disable output before disconnect
            if self._output_enabled:
                await self.set_output_enabled(1, False)
            
            await asyncio.sleep(0.05)
            self._is_connected = False
            self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
            self._log_operation("disconnect", True)
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("disconnect", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_DISCONNECTION_FAILED",
                f"Failed to disconnect from mock power supply: {str(e)}",
                {"device_id": self._device_id}
            )
    
    async def is_connected(self) -> bool:
        """Check mock connection status"""
        return self._is_connected
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device with current status"""
        if self._is_connected:
            if self._hardware_device.status != HardwareStatus.CONNECTED:
                self._hardware_device.set_status(HardwareStatus.CONNECTED)
        else:
            if self._hardware_device.status == HardwareStatus.CONNECTED:
                self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
        
        return self._hardware_device
    
    async def set_voltage(self, channel: int, voltage: VoltageValue) -> None:
        """Simulate voltage setting with safety validation"""
        self._validate_channel(channel)
        self._validate_connection("set_voltage")
        
        max_voltage = self._hardware_device.get_capability("max_voltage", 30.0)
        voltage_value = voltage.to_volts()
        
        if voltage_value < 0 or voltage_value > max_voltage:
            raise UnsafeOperationException(
                "set_voltage",
                f"Voltage {voltage_value}V is outside safe range [0, {max_voltage}V]",
                {"requested_voltage": voltage_value, "max_voltage": max_voltage}
            )
        
        try:
            await asyncio.sleep(0.05)  # Simulate setting delay
            self._voltage_setting = voltage_value
            self._log_operation("set_voltage", True)
            
        except Exception as e:
            self._log_operation("set_voltage", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_SET_VOLTAGE_FAILED",
                f"Failed to simulate voltage setting: {str(e)}",
                {"channel": channel, "voltage": str(voltage)}
            )
    
    async def get_voltage_setting(self, channel: int) -> VoltageValue:
        """Get simulated voltage setting"""
        self._validate_channel(channel)
        self._validate_connection("get_voltage_setting")
        
        return VoltageValue(self._voltage_setting, MeasurementUnit.VOLT)
    
    async def get_voltage_actual(self, channel: int) -> VoltageValue:
        """Get simulated actual voltage with realistic behavior"""
        self._validate_channel(channel)
        self._validate_connection("get_voltage_actual")
        
        if not self._output_enabled:
            actual_voltage = 0.0
        else:
            # Simulate slight difference from setting with noise
            noise = random.gauss(0, 0.01)  # 10mV noise
            actual_voltage = self._voltage_setting + noise
        
        return VoltageValue(actual_voltage, MeasurementUnit.VOLT)
    
    async def set_current_limit(self, channel: int, current: CurrentValue) -> None:
        """Simulate current limit setting with safety validation"""
        self._validate_channel(channel)
        self._validate_connection("set_current_limit")
        
        max_current = self._hardware_device.get_capability("max_current", 5.0)
        current_value = current.to_amperes()
        
        if current_value < 0 or current_value > max_current:
            raise UnsafeOperationException(
                "set_current_limit",
                f"Current {current_value}A is outside safe range [0, {max_current}A]",
                {"requested_current": current_value, "max_current": max_current}
            )
        
        try:
            await asyncio.sleep(0.05)
            self._current_setting = current_value
            self._log_operation("set_current_limit", True)
            
        except Exception as e:
            self._log_operation("set_current_limit", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_SET_CURRENT_FAILED",
                f"Failed to simulate current setting: {str(e)}",
                {"channel": channel, "current": str(current)}
            )
    
    async def get_current_setting(self, channel: int) -> CurrentValue:
        """Get simulated current limit setting"""
        self._validate_channel(channel)
        self._validate_connection("get_current_setting")
        
        return CurrentValue(self._current_setting, MeasurementUnit.AMPERE)
    
    async def get_current_actual(self, channel: int) -> CurrentValue:
        """Get simulated actual current"""
        self._validate_channel(channel)
        self._validate_connection("get_current_actual")
        
        if not self._output_enabled:
            actual_current = 0.0
        else:
            # Simulate load-dependent current
            load_factor = random.uniform(0.1, 0.8)  # Simulate varying load
            actual_current = self._current_setting * load_factor
        
        return CurrentValue(actual_current, MeasurementUnit.AMPERE)
    
    async def set_output_enabled(self, channel: int, enabled: bool) -> None:
        """Simulate output control"""
        self._validate_channel(channel)
        self._validate_connection("set_output_enabled")
        
        try:
            await asyncio.sleep(0.1)  # Simulate output switching delay
            self._output_enabled = enabled
            action = "enabled" if enabled else "disabled"
            self._log_operation(f"set_output_{action}", True)
            
        except Exception as e:
            self._log_operation("set_output_enabled", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_SET_OUTPUT_FAILED",
                f"Failed to simulate output control: {str(e)}",
                {"channel": channel, "enabled": enabled}
            )
    
    async def is_output_enabled(self, channel: int) -> bool:
        """Get output enable status"""
        self._validate_channel(channel)
        self._validate_connection("is_output_enabled")
        
        return self._output_enabled
    
    async def measure_all(self, channel: int) -> Dict[str, Any]:
        """Simulate comprehensive measurements"""
        self._validate_channel(channel)
        self._validate_connection("measure_all")
        
        try:
            voltage = await self.get_voltage_actual(channel)
            current = await self.get_current_actual(channel)
            power = voltage.value * current.value  # Calculate power
            
            return {
                'voltage': voltage,
                'current': current,
                'power': power
            }
            
        except Exception as e:
            self._log_operation("measure_all", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_MEASURE_ALL_FAILED",
                f"Failed to simulate measurements: {str(e)}",
                {"channel": channel}
            )
    
    async def set_protection_limits(
        self, 
        channel: int, 
        ovp_voltage: Optional[VoltageValue] = None,
        ocp_current: Optional[CurrentValue] = None
    ) -> None:
        """Simulate protection limit setting"""
        self._validate_channel(channel)
        self._validate_connection("set_protection_limits")
        
        try:
            if ovp_voltage is not None:
                self._ovp_setting = ovp_voltage.to_volts()
                logger.info(f"Mock: Set OVP to {ovp_voltage} on channel {channel}")
            
            if ocp_current is not None:
                self._ocp_setting = ocp_current.to_amperes()
                logger.info(f"Mock: Set OCP to {ocp_current} on channel {channel}")
            
            self._log_operation("set_protection_limits", True)
            
        except Exception as e:
            self._log_operation("set_protection_limits", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_SET_PROTECTION_FAILED",
                f"Failed to simulate protection setting: {str(e)}",
                {"channel": channel, "ovp": str(ovp_voltage), "ocp": str(ocp_current)}
            )
    
    async def get_protection_status(self, channel: int) -> Dict[str, bool]:
        """Get simulated protection status"""
        self._validate_channel(channel)
        self._validate_connection("get_protection_status")
        
        # Simulate occasional protection triggers for testing
        if random.random() < 0.01:  # 1% chance
            protection_type = random.choice(["ovp", "ocp", "otp"])
            self._protection_status[protection_type] = True
        
        return self._protection_status.copy()
    
    async def clear_protection(self, channel: int) -> None:
        """Simulate protection clearing"""
        self._validate_channel(channel)
        self._validate_connection("clear_protection")
        
        try:
            await asyncio.sleep(0.1)
            self._protection_status = {"ovp": False, "ocp": False, "otp": False}
            self._log_operation("clear_protection", True)
            
        except Exception as e:
            self._log_operation("clear_protection", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_CLEAR_PROTECTION_FAILED",
                f"Failed to simulate protection clearing: {str(e)}",
                {"channel": channel}
            )
    
    async def reset_device(self) -> None:
        """Simulate device reset"""
        self._validate_connection("reset_device")
        
        try:
            # Safety: Disable output before reset
            await self.set_output_enabled(1, False)
            
            await asyncio.sleep(0.5)  # Simulate reset delay
            
            # Reset to default values
            self._voltage_setting = 0.0
            self._current_setting = 1.0
            self._protection_status = {"ovp": False, "ocp": False, "otp": False}
            
            self._log_operation("reset_device", True)
            
        except Exception as e:
            self._log_operation("reset_device", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_RESET_FAILED",
                f"Failed to simulate device reset: {str(e)}",
                {"device_id": self._device_id}
            )
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get mock device information"""
        self._validate_connection("get_device_info")
        
        return {
            'model': 'MockPowerSupply',
            'vendor': 'mock',
            'adapter_type': 'mock_adapter',
            'device_id': self._device_id,
            'connection_info': 'mock://power_supply',
            'identity': f'Mock Power Supply {self._device_id}',
            'serial_number': f'MOCK-{self._device_id[-3:]}',
            'firmware_version': 'Mock v1.0.0',
            'capabilities': self._hardware_device.capabilities,
            'simulation_mode': True,
            'current_settings': {
                'voltage': self._voltage_setting,
                'current_limit': self._current_setting,
                'output_enabled': self._output_enabled,
                'ovp_setting': self._ovp_setting,
                'ocp_setting': self._ocp_setting
            }
        }
    
    # Mock-specific methods for testing
    def set_simulated_protection(self, protection_type: str, active: bool) -> None:
        """Set protection status for testing scenarios"""
        if protection_type in self._protection_status:
            self._protection_status[protection_type] = active
    
    def get_current_settings(self) -> Dict[str, float]:
        """Get current settings for testing verification"""
        return {
            'voltage': self._voltage_setting,
            'current_limit': self._current_setting,
            'ovp': self._ovp_setting,
            'ocp': self._ocp_setting
        }