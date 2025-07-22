"""
ODA Power Adapter

Concrete implementation of PowerAdapter for ODA power supply controller.
Provides business logic abstraction over OdaPowerSupply.
"""

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

from ....controllers.power_controller.oda.oda_power_supply import OdaPowerSupply
from ...interfaces.power_adapter import PowerAdapter


class OdaAdapter(PowerAdapter):
    """
    ODA Power Supply adapter implementation
    
    Provides business logic abstraction over OdaPowerSupply with
    domain object conversion, safety validation, and business rule enforcement.
    """
    
    def __init__(self, controller: OdaPowerSupply):
        """
        Initialize ODA adapter
        
        Args:
            controller: OdaPowerSupply instance to wrap
        """
        super().__init__("oda")
        self._controller = controller
        self._hardware_device = self._create_hardware_device_from_controller()
    
    def _create_hardware_device_from_controller(self) -> HardwareDevice:
        """Create hardware device entity from controller information"""
        return self._create_hardware_device(
            connection_info=self._controller.connection_info,
            device_id=f"oda_power_supply_{id(self._controller)}",
            capabilities={
                "max_voltage": 60.0,  # V (typical for ODA supplies)
                "max_current": 10.0,  # A
                "channels": 1,
                "ovp_protection": True,
                "ocp_protection": True,
                "remote_control": True,
                "output_control": True,
                "protection_clearing": True,
                "measurement_accuracy": 0.1  # %
            }
        )
    
    def _validate_channel(self, channel: int) -> None:
        """Validate channel number (ODA is single channel)"""
        if channel != 1:
            raise BusinessRuleViolationException(
                "INVALID_CHANNEL",
                f"Invalid channel {channel}. ODA power supply only supports channel 1",
                {"channel": channel, "max_channels": 1}
            )
    
    async def connect(self) -> None:
        """Connect to ODA power supply with business logic validation"""
        try:
            # Attempt connection
            self._controller.connect()
            
            # Update hardware device status
            self._hardware_device.set_status(HardwareStatus.CONNECTED)
            self._log_operation("connect", True)
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("connect", False, str(e))
            raise BusinessRuleViolationException(
                "ODA_CONNECTION_FAILED",
                f"Failed to connect to ODA power supply: {str(e)}",
                {"controller_type": "ODA", "connection_info": self._controller.connection_info}
            )
    
    async def disconnect(self) -> None:
        """Disconnect from ODA power supply with safety measures"""
        try:
            # Safety: Ensure output is disabled before disconnecting
            if self._controller.status.is_connected:
                try:
                    await self.set_output_enabled(1, False)
                except Exception:
                    logger.warning("Failed to disable output before disconnect - continuing anyway")
            
            self._controller.disconnect()
            self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
            self._log_operation("disconnect", True)
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("disconnect", False, str(e))
            raise BusinessRuleViolationException(
                "ODA_DISCONNECTION_FAILED",
                f"Failed to disconnect from ODA power supply: {str(e)}",
                {"controller_type": "ODA"}
            )
    
    async def is_connected(self) -> bool:
        """Check connection status with state synchronization"""
        try:
            is_connected = self._controller.is_alive()
            
            # Synchronize hardware device status
            if is_connected:
                if self._hardware_device.status != HardwareStatus.CONNECTED:
                    self._hardware_device.set_status(HardwareStatus.CONNECTED)
            else:
                if self._hardware_device.status == HardwareStatus.CONNECTED:
                    self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
            
            return is_connected
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("connection_check", False, str(e))
            return False
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device with updated status"""
        # Update status from controller
        await self.is_connected()
        return self._hardware_device
    
    async def set_voltage(self, channel: int, voltage: VoltageValue) -> None:
        """Set target voltage with safety validation"""
        self._validate_channel(channel)
        self._validate_connection("set_voltage")
        
        # Safety check: Validate voltage range
        max_voltage = self._hardware_device.get_capability("max_voltage", 60.0)
        voltage_value = voltage.to_volts()  # Convert to volts
        
        if voltage_value < 0 or voltage_value > max_voltage:
            raise UnsafeOperationException(
                "set_voltage",
                f"Voltage {voltage_value}V is outside safe range [0, {max_voltage}V]",
                {"requested_voltage": voltage_value, "max_voltage": max_voltage}
            )
        
        try:
            self._controller.set_voltage(channel, voltage_value)
            self._log_operation("set_voltage", True)
            
        except Exception as e:
            self._log_operation("set_voltage", False, str(e))
            raise BusinessRuleViolationException(
                "SET_VOLTAGE_FAILED",
                f"Failed to set voltage: {str(e)}",
                {"channel": channel, "voltage": str(voltage)}
            )
    
    async def get_voltage_setting(self, channel: int) -> VoltageValue:
        """Get voltage setting as domain object"""
        self._validate_channel(channel)
        self._validate_connection("get_voltage_setting")
        
        try:
            voltage_setting = self._controller.get_voltage_setting(channel)
            return VoltageValue.from_raw_data(voltage_setting, MeasurementUnit.VOLT)
            
        except Exception as e:
            self._log_operation("get_voltage_setting", False, str(e))
            raise BusinessRuleViolationException(
                "GET_VOLTAGE_SETTING_FAILED",
                f"Failed to get voltage setting: {str(e)}",
                {"channel": channel}
            )
    
    async def get_voltage_actual(self, channel: int) -> VoltageValue:
        """Get actual output voltage as domain object"""
        self._validate_channel(channel)
        self._validate_connection("get_voltage_actual")
        
        try:
            actual_voltage = self._controller.get_voltage_actual(channel)
            return VoltageValue.from_raw_data(actual_voltage, MeasurementUnit.VOLT)
            
        except Exception as e:
            self._log_operation("get_voltage_actual", False, str(e))
            raise BusinessRuleViolationException(
                "GET_VOLTAGE_ACTUAL_FAILED",
                f"Failed to get actual voltage: {str(e)}",
                {"channel": channel}
            )
    
    async def set_current_limit(self, channel: int, current: CurrentValue) -> None:
        """Set current limit with safety validation"""
        self._validate_channel(channel)
        self._validate_connection("set_current_limit")
        
        # Safety check: Validate current range
        max_current = self._hardware_device.get_capability("max_current", 10.0)
        current_value = current.to_amperes()  # Convert to amperes
        
        if current_value < 0 or current_value > max_current:
            raise UnsafeOperationException(
                "set_current_limit",
                f"Current {current_value}A is outside safe range [0, {max_current}A]",
                {"requested_current": current_value, "max_current": max_current}
            )
        
        try:
            self._controller.set_current(channel, current_value)
            self._log_operation("set_current_limit", True)
            
        except Exception as e:
            self._log_operation("set_current_limit", False, str(e))
            raise BusinessRuleViolationException(
                "SET_CURRENT_LIMIT_FAILED",
                f"Failed to set current limit: {str(e)}",
                {"channel": channel, "current": str(current)}
            )
    
    async def get_current_setting(self, channel: int) -> CurrentValue:
        """Get current limit setting as domain object"""
        self._validate_channel(channel)
        self._validate_connection("get_current_setting")
        
        try:
            current_setting = self._controller.get_current_setting(channel)
            return CurrentValue.from_raw_data(current_setting, MeasurementUnit.AMPERE)
            
        except Exception as e:
            self._log_operation("get_current_setting", False, str(e))
            raise BusinessRuleViolationException(
                "GET_CURRENT_SETTING_FAILED",
                f"Failed to get current setting: {str(e)}",
                {"channel": channel}
            )
    
    async def get_current_actual(self, channel: int) -> CurrentValue:
        """Get actual output current as domain object"""
        self._validate_channel(channel)
        self._validate_connection("get_current_actual")
        
        try:
            actual_current = self._controller.get_current_actual(channel)
            return CurrentValue.from_raw_data(actual_current, MeasurementUnit.AMPERE)
            
        except Exception as e:
            self._log_operation("get_current_actual", False, str(e))
            raise BusinessRuleViolationException(
                "GET_CURRENT_ACTUAL_FAILED",
                f"Failed to get actual current: {str(e)}",
                {"channel": channel}
            )
    
    async def set_output_enabled(self, channel: int, enabled: bool) -> None:
        """Enable or disable output with safety logging"""
        self._validate_channel(channel)
        self._validate_connection("set_output_enabled")
        
        try:
            self._controller.set_output_state(channel, enabled)
            action = "enabled" if enabled else "disabled"
            logger.info(f"ODA power supply output {action} on channel {channel}")
            self._log_operation(f"set_output_{action}", True)
            
        except Exception as e:
            self._log_operation("set_output_enabled", False, str(e))
            raise BusinessRuleViolationException(
                "SET_OUTPUT_STATE_FAILED",
                f"Failed to set output state: {str(e)}",
                {"channel": channel, "enabled": enabled}
            )
    
    async def is_output_enabled(self, channel: int) -> bool:
        """Check if output is enabled"""
        self._validate_channel(channel)
        self._validate_connection("is_output_enabled")
        
        try:
            return self._controller.get_output_state(channel)
            
        except Exception as e:
            self._log_operation("is_output_enabled", False, str(e))
            raise BusinessRuleViolationException(
                "GET_OUTPUT_STATE_FAILED",
                f"Failed to get output state: {str(e)}",
                {"channel": channel}
            )
    
    async def measure_all(self, channel: int) -> Dict[str, Any]:
        """Measure all parameters with domain object conversion"""
        self._validate_channel(channel)
        self._validate_connection("measure_all")
        
        try:
            measurements = self._controller.measure_all(channel)
            
            # Convert to domain objects
            return {
                'voltage': VoltageValue.from_raw_data(measurements['voltage'], MeasurementUnit.VOLT),
                'current': CurrentValue.from_raw_data(measurements['current'], MeasurementUnit.AMPERE),
                'power': measurements.get('power', 0.0)  # Power as raw value for now
            }
            
        except Exception as e:
            self._log_operation("measure_all", False, str(e))
            raise BusinessRuleViolationException(
                "MEASURE_ALL_FAILED",
                f"Failed to measure all parameters: {str(e)}",
                {"channel": channel}
            )
    
    async def set_protection_limits(
        self, 
        channel: int, 
        ovp_voltage: Optional[VoltageValue] = None,
        ocp_current: Optional[CurrentValue] = None
    ) -> None:
        """Set protection limits with business rule validation"""
        self._validate_channel(channel)
        self._validate_connection("set_protection_limits")
        
        try:
            if ovp_voltage is not None:
                voltage_value = ovp_voltage.to_volts()
                # Business rule: OVP should be higher than max operating voltage
                max_voltage = self._hardware_device.get_capability("max_voltage", 60.0)
                if voltage_value > max_voltage * 1.1:  # Allow 10% margin
                    logger.warning(f"OVP voltage {voltage_value}V is very high compared to max voltage {max_voltage}V")
                
                self._controller.set_ovp(channel, voltage_value)
                logger.info(f"Set OVP to {ovp_voltage} on channel {channel}")
            
            if ocp_current is not None:
                current_value = ocp_current.to_amperes()
                # Business rule: OCP should be higher than max operating current
                max_current = self._hardware_device.get_capability("max_current", 10.0)
                if current_value > max_current * 1.1:  # Allow 10% margin
                    logger.warning(f"OCP current {current_value}A is very high compared to max current {max_current}A")
                
                self._controller.set_ocp(channel, current_value)
                logger.info(f"Set OCP to {ocp_current} on channel {channel}")
            
            self._log_operation("set_protection_limits", True)
                
        except Exception as e:
            self._log_operation("set_protection_limits", False, str(e))
            raise BusinessRuleViolationException(
                "SET_PROTECTION_LIMITS_FAILED",
                f"Failed to set protection limits: {str(e)}",
                {"channel": channel, "ovp": str(ovp_voltage), "ocp": str(ocp_current)}
            )
    
    async def get_protection_status(self, channel: int) -> Dict[str, bool]:
        """Get protection status"""
        self._validate_channel(channel)
        self._validate_connection("get_protection_status")
        
        try:
            return self._controller.get_protection_status(channel)
            
        except Exception as e:
            self._log_operation("get_protection_status", False, str(e))
            raise BusinessRuleViolationException(
                "GET_PROTECTION_STATUS_FAILED",
                f"Failed to get protection status: {str(e)}",
                {"channel": channel}
            )
    
    async def clear_protection(self, channel: int) -> None:
        """Clear protection faults"""
        self._validate_channel(channel)
        self._validate_connection("clear_protection")
        
        try:
            self._controller.clear_protection(channel)
            logger.info(f"Cleared protection faults on channel {channel}")
            self._log_operation("clear_protection", True)
            
        except Exception as e:
            self._log_operation("clear_protection", False, str(e))
            raise BusinessRuleViolationException(
                "CLEAR_PROTECTION_FAILED",
                f"Failed to clear protection faults: {str(e)}",
                {"channel": channel}
            )
    
    async def reset_device(self) -> None:
        """Reset device with safety measures"""
        self._validate_connection("reset_device")
        
        try:
            # Safety: Disable output before reset
            await self.set_output_enabled(1, False)
            
            self._controller.reset()
            logger.info("ODA power supply reset completed")
            self._log_operation("reset_device", True)
            
        except Exception as e:
            self._log_operation("reset_device", False, str(e))
            raise BusinessRuleViolationException(
                "RESET_DEVICE_FAILED",
                f"Failed to reset device: {str(e)}",
                {"controller_type": "ODA"}
            )
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information"""
        self._validate_connection("get_device_info")
        
        try:
            device_info = self._controller.get_device_info()
            
            return {
                'model': 'ODA',
                'vendor': 'oda',
                'adapter_type': 'oda_adapter',
                'connection_info': self._controller.connection_info,
                'identity': device_info.get('identity', 'Unknown'),
                'serial_number': device_info.get('serial_number', 'Unknown'),
                'firmware_version': device_info.get('version', 'Unknown'),
                'capabilities': self._hardware_device.capabilities,
                'hardware_device': self._hardware_device.to_dict() if hasattr(self._hardware_device, 'to_dict') else {}
            }
            
        except Exception as e:
            self._log_operation("get_device_info", False, str(e))
            raise BusinessRuleViolationException(
                "GET_DEVICE_INFO_FAILED",
                f"Failed to get device info: {str(e)}",
                {"controller_type": "ODA"}
            )