"""
Hardware Controller

Presentation layer controller for hardware management operations.
Coordinates between user interface and hardware services.
"""

from typing import Dict, Any, Optional, List
from loguru import logger

from ...application.interfaces.loadcell_service import LoadCellService
from ...application.interfaces.power_service import PowerService

from ...domain.value_objects.measurements import ForceValue, VoltageValue, CurrentValue
from ...domain.enums.measurement_units import MeasurementUnit
from ...domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    HardwareNotReadyException,
    UnsafeOperationException,
    ValidationException
)

from .base_controller import BaseController


class HardwareController(BaseController):
    """Controller for hardware management operations"""
    
    def __init__(
        self,
        loadcell_service: LoadCellService,
        power_service: PowerService
    ):
        """
        Initialize controller with hardware services
        
        Args:
            loadcell_service: LoadCell service interface
            power_service: Power supply service interface
        """
        super().__init__()
        self._loadcell_service = loadcell_service
        self._power_service = power_service
    
    async def get_hardware_status(self) -> Dict[str, Any]:
        """
        Get status of all hardware devices
        
        Returns:
            Hardware status information
        """
        logger.info("Hardware status requested")
        
        try:
            # Get loadcell status
            loadcell_connected = await self._loadcell_service.is_connected()
            loadcell_device = await self._loadcell_service.get_hardware_device() if loadcell_connected else None
            
            # Get power supply status  
            power_connected = await self._power_service.is_connected()
            power_device = await self._power_service.get_hardware_device() if power_connected else None
            
            hardware_status = {
                'loadcell': {
                    'connected': loadcell_connected,
                    'status': loadcell_device.status.value if loadcell_device else 'disconnected',
                    'device_type': loadcell_device.device_type if loadcell_device else None,
                    'vendor': loadcell_device.vendor if loadcell_device else None,
                    'capabilities': loadcell_device.capabilities if loadcell_device else None,
                    'error_message': loadcell_device.error_message if loadcell_device and loadcell_device.error_message else None
                },
                'power_supply': {
                    'connected': power_connected,
                    'status': power_device.status.value if power_device else 'disconnected',
                    'device_type': power_device.device_type if power_device else None,
                    'vendor': power_device.vendor if power_device else None,
                    'capabilities': power_device.capabilities if power_device else None,
                    'error_message': power_device.error_message if power_device and power_device.error_message else None
                }
            }
            
            return self._create_success_response(
                hardware_status,
                "Hardware status retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error getting hardware status: {e}")
            return self._create_error_response(
                "HARDWARE_STATUS_ERROR",
                f"Failed to get hardware status: {str(e)}",
                {"error_type": type(e).__name__}
            )
    
    async def connect_hardware(self, device_type: str) -> Dict[str, Any]:
        """
        Connect to specific hardware device
        
        Args:
            device_type: Type of device to connect ('loadcell' or 'power_supply')
            
        Returns:
            Connection result
        """
        logger.info(f"Hardware connection requested for {device_type}")
        
        try:
            if device_type.lower() == 'loadcell':
                await self._loadcell_service.connect()
                device = await self._loadcell_service.get_hardware_device()
                
                return self._create_success_response(
                    {
                        'device_type': device_type,
                        'connected': True,
                        'status': device.status.value,
                        'device_info': {
                            'vendor': device.vendor,
                            'capabilities': device.capabilities
                        }
                    },
                    f"LoadCell connected successfully"
                )
                
            elif device_type.lower() == 'power_supply':
                await self._power_service.connect()
                device = await self._power_service.get_hardware_device()
                
                return self._create_success_response(
                    {
                        'device_type': device_type,
                        'connected': True,
                        'status': device.status.value,
                        'device_info': {
                            'vendor': device.vendor,
                            'capabilities': device.capabilities
                        }
                    },
                    f"Power supply connected successfully"
                )
                
            else:
                return self._create_error_response(
                    "INVALID_DEVICE_TYPE",
                    f"Invalid device type: {device_type}",
                    {"valid_types": ["loadcell", "power_supply"]}
                )
                
        except HardwareNotReadyException as e:
            logger.error(f"Hardware connection failed: {e}")
            return self._create_error_response(
                "HARDWARE_CONNECTION_FAILED",
                str(e),
                e.context
            )
        except Exception as e:
            logger.error(f"Unexpected error connecting hardware: {e}")
            return self._create_error_response(
                "HARDWARE_CONNECTION_ERROR",
                f"Failed to connect {device_type}: {str(e)}",
                {"device_type": device_type}
            )
    
    async def disconnect_hardware(self, device_type: str) -> Dict[str, Any]:
        """
        Disconnect from specific hardware device
        
        Args:
            device_type: Type of device to disconnect ('loadcell' or 'power_supply')
            
        Returns:
            Disconnection result
        """
        logger.info(f"Hardware disconnection requested for {device_type}")
        
        try:
            if device_type.lower() == 'loadcell':
                await self._loadcell_service.disconnect()
                
                return self._create_success_response(
                    {'device_type': device_type, 'connected': False},
                    "LoadCell disconnected successfully"
                )
                
            elif device_type.lower() == 'power_supply':
                await self._power_service.disconnect()
                
                return self._create_success_response(
                    {'device_type': device_type, 'connected': False},
                    "Power supply disconnected successfully"
                )
                
            else:
                return self._create_error_response(
                    "INVALID_DEVICE_TYPE",
                    f"Invalid device type: {device_type}",
                    {"valid_types": ["loadcell", "power_supply"]}
                )
                
        except Exception as e:
            logger.error(f"Error disconnecting hardware: {e}")
            return self._create_error_response(
                "HARDWARE_DISCONNECTION_ERROR",
                f"Failed to disconnect {device_type}: {str(e)}",
                {"device_type": device_type}
            )
    
    async def read_loadcell_force(self, num_samples: int = 1) -> Dict[str, Any]:
        """
        Read force measurement from loadcell
        
        Args:
            num_samples: Number of samples to take (default: 1)
            
        Returns:
            Force measurement result
        """
        logger.info(f"Force measurement requested ({num_samples} samples)")
        
        try:
            if num_samples <= 1:
                # Single measurement
                force_value = await self._loadcell_service.read_force_value()
                
                return self._create_success_response(
                    {
                        'measurement_type': 'force',
                        'value': force_value.value,
                        'unit': force_value.unit.value,
                        'samples': 1
                    },
                    "Force measurement completed"
                )
            else:
                # Multiple measurements
                force_values = await self._loadcell_service.read_multiple_samples(num_samples)
                statistics = await self._loadcell_service.get_measurement_statistics(num_samples)
                
                return self._create_success_response(
                    {
                        'measurement_type': 'force',
                        'samples': num_samples,
                        'values': [{'value': fv.value, 'unit': fv.unit.value} for fv in force_values],
                        'statistics': {
                            'min': {'value': statistics['min'].value, 'unit': statistics['min'].unit.value},
                            'max': {'value': statistics['max'].value, 'unit': statistics['max'].unit.value},
                            'average': {'value': statistics['average'].value, 'unit': statistics['average'].unit.value},
                            'std_dev': {'value': statistics['std_dev'].value, 'unit': statistics['std_dev'].unit.value}
                        }
                    },
                    f"Force measurement completed ({num_samples} samples)"
                )
                
        except HardwareNotReadyException as e:
            logger.error(f"LoadCell not ready: {e}")
            return self._create_error_response(
                "LOADCELL_NOT_READY",
                str(e),
                e.context
            )
        except ValidationException as e:
            logger.error(f"Invalid measurement parameters: {e}")
            return self._create_error_response(
                "INVALID_PARAMETERS",
                str(e),
                e.context
            )
        except Exception as e:
            logger.error(f"Error reading force: {e}")
            return self._create_error_response(
                "FORCE_MEASUREMENT_ERROR",
                f"Failed to read force: {str(e)}",
                {"num_samples": num_samples}
            )
    
    async def zero_loadcell(self) -> Dict[str, Any]:
        """
        Perform auto-zero operation on loadcell
        
        Returns:
            Zero operation result
        """
        logger.info("LoadCell zero operation requested")
        
        try:
            await self._loadcell_service.zero_force()
            
            return self._create_success_response(
                {'operation': 'auto_zero', 'completed': True},
                "LoadCell auto-zero completed successfully"
            )
            
        except HardwareNotReadyException as e:
            logger.error(f"LoadCell not ready for zero: {e}")
            return self._create_error_response(
                "LOADCELL_NOT_READY",
                str(e),
                e.context
            )
        except Exception as e:
            logger.error(f"Error during auto-zero: {e}")
            return self._create_error_response(
                "AUTO_ZERO_ERROR",
                f"Auto-zero operation failed: {str(e)}"
            )
    
    async def set_power_output(
        self,
        voltage: float,
        current_limit: float,
        enabled: bool = True,
        channel: int = 1
    ) -> Dict[str, Any]:
        """
        Set power supply output parameters
        
        Args:
            voltage: Target voltage in volts
            current_limit: Current limit in amperes
            enabled: Enable output (default: True)
            channel: Power supply channel (default: 1)
            
        Returns:
            Power output configuration result
        """
        logger.info(f"Power output configuration requested: {voltage}V, {current_limit}A, enabled={enabled}")
        
        try:
            # Create value objects
            voltage_value = VoltageValue(voltage, MeasurementUnit.VOLT)
            current_value = CurrentValue(current_limit, MeasurementUnit.AMPERE)
            
            # Set voltage and current limit
            await self._power_service.set_voltage(channel, voltage_value)
            await self._power_service.set_current_limit(channel, current_value)
            
            # Set output state
            await self._power_service.set_output_enabled(channel, enabled)
            
            # Get actual settings for confirmation
            actual_voltage = await self._power_service.get_voltage_setting(channel)
            actual_current = await self._power_service.get_current_setting(channel)
            output_enabled = await self._power_service.is_output_enabled(channel)
            
            return self._create_success_response(
                {
                    'channel': channel,
                    'voltage': {
                        'set': voltage,
                        'actual': actual_voltage.value,
                        'unit': actual_voltage.unit.value
                    },
                    'current_limit': {
                        'set': current_limit,
                        'actual': actual_current.value,
                        'unit': actual_current.unit.value
                    },
                    'output_enabled': output_enabled
                },
                "Power output configured successfully"
            )
            
        except UnsafeOperationException as e:
            logger.error(f"Unsafe power operation: {e}")
            return self._create_error_response(
                "UNSAFE_OPERATION",
                str(e),
                e.context
            )
        except HardwareNotReadyException as e:
            logger.error(f"Power supply not ready: {e}")
            return self._create_error_response(
                "POWER_SUPPLY_NOT_READY",
                str(e),
                e.context
            )
        except Exception as e:
            logger.error(f"Error setting power output: {e}")
            return self._create_error_response(
                "POWER_OUTPUT_ERROR",
                f"Failed to set power output: {str(e)}",
                {"voltage": voltage, "current_limit": current_limit, "channel": channel}
            )
    
    async def measure_power_output(self, channel: int = 1) -> Dict[str, Any]:
        """
        Measure actual power supply output
        
        Args:
            channel: Power supply channel (default: 1)
            
        Returns:
            Power measurement result
        """
        logger.info(f"Power measurement requested for channel {channel}")
        
        try:
            measurements = await self._power_service.measure_all(channel)
            
            return self._create_success_response(
                {
                    'channel': channel,
                    'voltage': {
                        'value': measurements['voltage'].value,
                        'unit': measurements['voltage'].unit.value
                    },
                    'current': {
                        'value': measurements['current'].value,
                        'unit': measurements['current'].unit.value
                    },
                    'power': measurements.get('power', 0.0)
                },
                "Power measurement completed"
            )
            
        except HardwareNotReadyException as e:
            logger.error(f"Power supply not ready: {e}")
            return self._create_error_response(
                "POWER_SUPPLY_NOT_READY",
                str(e),
                e.context
            )
        except Exception as e:
            logger.error(f"Error measuring power: {e}")
            return self._create_error_response(
                "POWER_MEASUREMENT_ERROR",
                f"Failed to measure power: {str(e)}",
                {"channel": channel}
            )