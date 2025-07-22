"""
BS205 LoadCell Adapter

Concrete implementation of LoadCellAdapter for BS205 loadcell controller.
Provides business logic abstraction over BS205Controller.
"""

import asyncio
import statistics
from typing import Dict, Any, List
from loguru import logger

from ....domain.value_objects.measurements import ForceValue
from ....domain.entities.hardware_device import HardwareDevice
from ....domain.enums.hardware_status import HardwareStatus
from ....domain.enums.measurement_units import MeasurementUnit
from ....domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    HardwareNotReadyException,
    UnsafeOperationException
)

from ....controllers.loadcell_controller.bs205.bs205_controller import BS205Controller
from ...interfaces.loadcell_adapter import LoadCellAdapter


class BS205Adapter(LoadCellAdapter):
    """
    BS205 LoadCell adapter implementation
    
    Provides business logic abstraction over BS205Controller with
    domain object conversion and business rule enforcement.
    """
    
    def __init__(self, controller: BS205Controller):
        """
        Initialize BS205 adapter
        
        Args:
            controller: BS205Controller instance to wrap
        """
        super().__init__("bs205")
        self._controller = controller
        self._hardware_device = self._create_hardware_device_from_controller()
    
    def _create_hardware_device_from_controller(self) -> HardwareDevice:
        """Create hardware device entity from controller information"""
        return self._create_hardware_device(
            connection_info=self._controller.connection_info,
            device_id=str(self._controller.indicator_id),
            capabilities={
                "max_force": 10000.0,  # N (typical for BS205)
                "min_force": -10000.0,  # N
                "resolution": 0.1,  # N
                "sample_rate": 10,  # Hz
                "calibration_supported": False,
                "hold_function": True,
                "auto_zero": True
            }
        )
    
    async def connect(self) -> None:
        """Connect to BS205 controller with business logic validation"""
        try:
            # Attempt connection
            success = self._controller.connect()
            if not success:
                raise BusinessRuleViolationException(
                    "BS205_CONNECTION_FAILED",
                    "Failed to establish connection to BS205 controller",
                    {"connection_info": self._controller.connection_info}
                )
            
            # Update hardware device status
            self._hardware_device.set_status(HardwareStatus.CONNECTED)
            self._log_operation("connect", True)
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("connect", False, str(e))
            raise BusinessRuleViolationException(
                "BS205_CONNECTION_FAILED",
                f"Failed to connect to BS205 controller: {str(e)}",
                {"controller_type": "BS205", "connection_info": self._controller.connection_info}
            )
    
    async def disconnect(self) -> None:
        """Disconnect from BS205 controller with cleanup"""
        try:
            self._controller.disconnect()
            self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
            self._log_operation("disconnect", True)
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("disconnect", False, str(e))
            raise BusinessRuleViolationException(
                "BS205_DISCONNECTION_FAILED",
                f"Failed to disconnect from BS205 controller: {str(e)}",
                {"controller_type": "BS205"}
            )
    
    async def is_connected(self) -> bool:
        """Check connection status with state synchronization"""
        try:
            is_connected = self._controller.is_connected
            
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
    
    async def read_force_value(self) -> ForceValue:
        """Read force value with business logic validation"""
        self._validate_connection("read_force_value")
        
        try:
            # Read raw value from controller
            raw_value = self._controller.read_value()
            if raw_value is None:
                raise BusinessRuleViolationException(
                    "BS205_READ_FAILED",
                    "Failed to read value from BS205 controller",
                    {"controller_type": "BS205"}
                )
            
            # Convert to domain object with validation
            force_value = ForceValue.from_raw_data(raw_value, MeasurementUnit.NEWTON)
            
            # Business rule: Validate range
            if not await self.validate_force_range(force_value):
                logger.warning(f"Force value {force_value} outside expected range")
            
            self._log_operation("read_force_value", True)
            return force_value
            
        except BusinessRuleViolationException:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            self._log_operation("read_force_value", False, str(e))
            raise BusinessRuleViolationException(
                "FORCE_READING_FAILED",
                f"Failed to read force value: {str(e)}",
                {"controller_type": "BS205", "indicator_id": self._controller.indicator_id}
            )
    
    async def read_multiple_samples(self, num_samples: int, interval_ms: float = 100) -> List[ForceValue]:
        """Read multiple samples with business rule validation"""
        self._validate_connection("read_multiple_samples")
        
        # Business rule validation
        if num_samples < 1:
            raise BusinessRuleViolationException(
                "INVALID_SAMPLE_COUNT",
                f"Number of samples must be at least 1, got {num_samples}",
                {"num_samples": num_samples}
            )
        
        if interval_ms < 10:
            raise BusinessRuleViolationException(
                "INVALID_SAMPLE_INTERVAL",
                f"Sample interval must be at least 10ms, got {interval_ms}ms",
                {"interval_ms": interval_ms}
            )
        
        try:
            force_values = []
            interval_seconds = interval_ms / 1000.0
            
            for i in range(num_samples):
                # Read single sample
                force_value = await self.read_force_value()
                force_values.append(force_value)
                
                # Wait for interval (except for last sample)
                if i < num_samples - 1:
                    await asyncio.sleep(interval_seconds)
            
            self._log_operation("read_multiple_samples", True)
            return force_values
            
        except BusinessRuleViolationException:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            self._log_operation("read_multiple_samples", False, str(e))
            raise BusinessRuleViolationException(
                "MULTIPLE_SAMPLES_FAILED",
                f"Failed to read multiple samples: {str(e)}",
                {"num_samples": num_samples, "interval_ms": interval_ms}
            )
    
    async def get_raw_data(self) -> str:
        """Get raw data with error handling"""
        self._validate_connection("get_raw_data")
        
        try:
            raw_data = self._controller.read_raw_data()
            if raw_data is None:
                raise BusinessRuleViolationException(
                    "BS205_RAW_DATA_FAILED",
                    "Failed to read raw data from BS205 controller",
                    {"controller_type": "BS205"}
                )
            
            self._log_operation("get_raw_data", True)
            return raw_data
            
        except Exception as e:
            self._log_operation("get_raw_data", False, str(e))
            raise BusinessRuleViolationException(
                "RAW_DATA_READING_FAILED",
                f"Failed to read raw data: {str(e)}",
                {"controller_type": "BS205"}
            )
    
    async def zero_force(self) -> None:
        """Perform auto-zero with business logic"""
        self._validate_connection("zero_force")
        
        try:
            success = self._controller.auto_zero()
            if not success:
                raise BusinessRuleViolationException(
                    "BS205_AUTO_ZERO_FAILED",
                    "Auto-zero operation failed",
                    {"controller_type": "BS205"}
                )
            
            self._log_operation("zero_force", True)
            
        except Exception as e:
            self._log_operation("zero_force", False, str(e))
            raise BusinessRuleViolationException(
                "AUTO_ZERO_FAILED",
                f"Failed to perform auto-zero: {str(e)}",
                {"controller_type": "BS205"}
            )
    
    async def set_hold_enabled(self, enabled: bool) -> None:
        """Set hold function with validation"""
        self._validate_connection("set_hold_enabled")
        
        try:
            success = self._controller.set_hold(enabled)
            if not success:
                raise BusinessRuleViolationException(
                    "BS205_HOLD_SET_FAILED",
                    f"Failed to set hold function to {enabled}",
                    {"controller_type": "BS205", "enabled": enabled}
                )
            
            action = "enabled" if enabled else "disabled"
            self._log_operation(f"set_hold_{action}", True)
            
        except Exception as e:
            self._log_operation("set_hold_enabled", False, str(e))
            raise BusinessRuleViolationException(
                "HOLD_OPERATION_FAILED",
                f"Failed to set hold function: {str(e)}",
                {"enabled": enabled, "controller_type": "BS205"}
            )
    
    async def is_hold_enabled(self) -> bool:
        """Check hold status with error handling"""
        self._validate_connection("is_hold_enabled")
        
        try:
            hold_status = self._controller.is_hold_enabled()
            return hold_status if hold_status is not None else False
            
        except Exception as e:
            self._log_operation("is_hold_enabled", False, str(e))
            raise BusinessRuleViolationException(
                "HOLD_STATUS_CHECK_FAILED",
                f"Failed to check hold status: {str(e)}",
                {"controller_type": "BS205"}
            )
    
    async def get_measurement_statistics(self, num_samples: int) -> Dict[str, ForceValue]:
        """Get statistical measurements with business logic"""
        if num_samples < 2:
            raise BusinessRuleViolationException(
                "INSUFFICIENT_SAMPLES",
                f"At least 2 samples required for statistics, got {num_samples}",
                {"num_samples": num_samples}
            )
        
        # Take multiple samples
        force_values = await self.read_multiple_samples(num_samples)
        
        # Extract numeric values for calculations
        numeric_values = [fv.value for fv in force_values]
        
        # Calculate statistics
        min_value = min(numeric_values)
        max_value = max(numeric_values)
        avg_value = sum(numeric_values) / len(numeric_values)
        std_dev_value = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0
        
        # Convert back to ForceValue objects
        return {
            'min': ForceValue(min_value, MeasurementUnit.NEWTON),
            'max': ForceValue(max_value, MeasurementUnit.NEWTON),
            'average': ForceValue(avg_value, MeasurementUnit.NEWTON),
            'std_dev': ForceValue(std_dev_value, MeasurementUnit.NEWTON)
        }
    
    async def execute_force_test(self, test_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute force test with enhanced domain information"""
        self._validate_connection("execute_force_test")
        
        try:
            # Use controller's execute_test method
            result = self._controller.execute_test(test_parameters)
            
            # Enhance result with domain information
            enhanced_result = result.copy() if result else {}
            enhanced_result.update({
                'hardware_type': 'loadcell',
                'controller_type': 'BS205',
                'adapter_type': 'bs205_adapter',
                'indicator_id': self._controller.indicator_id,
                'device_capabilities': self._hardware_device.capabilities
            })
            
            self._log_operation("execute_force_test", True)
            return enhanced_result
            
        except Exception as e:
            self._log_operation("execute_force_test", False, str(e))
            raise BusinessRuleViolationException(
                "FORCE_TEST_EXECUTION_FAILED",
                f"Failed to execute force test: {str(e)}",
                {"test_parameters": test_parameters}
            )
    
    async def calibrate(self, reference_force: ForceValue) -> None:
        """Handle calibration request (not supported by BS205)"""
        # BS205 controller doesn't support direct calibration
        self._log_operation("calibrate", False, "Not supported by BS205")
        raise BusinessRuleViolationException(
            "CALIBRATION_NOT_SUPPORTED",
            "Calibration is not supported by BS205 controller",
            {"reference_force": str(reference_force), "controller_type": "BS205"}
        )
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information"""
        self._validate_connection("get_device_info")
        
        try:
            # Get information from controller
            port_info = self._controller.get_port_info()
            
            return {
                'model': 'BS205',
                'vendor': 'bs205',
                'adapter_type': 'bs205_adapter',
                'indicator_id': self._controller.indicator_id,
                'connection_info': self._controller.connection_info,
                'communication_stats': port_info,
                'capabilities': self._hardware_device.capabilities,
                'last_calibration': None,  # Not supported by BS205
                'firmware_version': 'Unknown',  # Not available via BS205 protocol
                'hardware_device': self._hardware_device.to_dict() if hasattr(self._hardware_device, 'to_dict') else {}
            }
            
        except Exception as e:
            self._log_operation("get_device_info", False, str(e))
            raise BusinessRuleViolationException(
                "DEVICE_INFO_FAILED",
                f"Failed to get device info: {str(e)}",
                {"controller_type": "BS205"}
            )
    
    async def get_measurement_range(self) -> Dict[str, ForceValue]:
        """Get measurement range from capabilities"""
        capabilities = self._hardware_device.capabilities
        
        return {
            'min_force': ForceValue(capabilities.get('min_force', -10000.0), MeasurementUnit.NEWTON),
            'max_force': ForceValue(capabilities.get('max_force', 10000.0), MeasurementUnit.NEWTON)
        }
    
    async def validate_force_range(self, force: ForceValue) -> bool:
        """Validate force value against measurement range"""
        self._validate_connection("validate_force_range")
        
        measurement_range = await self.get_measurement_range()
        min_force = measurement_range['min_force']
        max_force = measurement_range['max_force']
        
        # Convert to same units for comparison
        if force.unit != MeasurementUnit.NEWTON:
            logger.warning(f"Force unit {force.unit} may not be directly comparable to range in Newtons")
        
        return min_force.value <= force.value <= max_force.value