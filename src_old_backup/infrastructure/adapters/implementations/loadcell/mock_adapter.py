"""
Mock LoadCell Adapter

Mock implementation of LoadCellAdapter for testing and development.
Provides simulated loadcell behavior without hardware dependencies.
"""

import asyncio
import statistics
import random
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

from ...interfaces.loadcell_adapter import LoadCellAdapter


class MockLoadCellAdapter(LoadCellAdapter):
    """
    Mock LoadCell adapter implementation
    
    Provides simulated loadcell behavior for testing and development
    without requiring actual hardware.
    """
    
    def __init__(self, device_id: str = "mock_loadcell_001"):
        """
        Initialize mock adapter
        
        Args:
            device_id: Mock device identifier
        """
        super().__init__("mock")
        self._device_id = device_id
        self._is_connected = False
        self._is_hold_enabled = False
        self._simulated_force = 0.0
        self._force_noise_level = 0.1  # N
        self._hardware_device = self._create_mock_hardware_device()
    
    def _create_mock_hardware_device(self) -> HardwareDevice:
        """Create mock hardware device entity"""
        return self._create_hardware_device(
            connection_info="mock://loadcell",
            device_id=self._device_id,
            capabilities={
                "max_force": 5000.0,  # N (lower than BS205 for testing)
                "min_force": -5000.0,  # N
                "resolution": 0.01,  # N (better resolution for testing)
                "sample_rate": 100,  # Hz (faster for testing)
                "calibration_supported": True,  # Mock supports calibration
                "hold_function": True,
                "auto_zero": True,
                "simulation_mode": True
            }
        )
    
    async def connect(self) -> None:
        """Simulate connection to mock device"""
        try:
            # Simulate connection delay
            await asyncio.sleep(0.1)
            
            # Simulate occasional connection failures for testing
            if random.random() < 0.05:  # 5% failure rate
                raise BusinessRuleViolationException(
                    "MOCK_CONNECTION_FAILED",
                    "Simulated connection failure for testing",
                    {"device_id": self._device_id}
                )
            
            self._is_connected = True
            self._hardware_device.set_status(HardwareStatus.CONNECTED)
            self._log_operation("connect", True)
            
        except BusinessRuleViolationException:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("connect", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_CONNECTION_FAILED",
                f"Failed to connect to mock device: {str(e)}",
                {"device_id": self._device_id}
            )
    
    async def disconnect(self) -> None:
        """Simulate disconnection from mock device"""
        try:
            # Simulate disconnection delay
            await asyncio.sleep(0.05)
            
            self._is_connected = False
            self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
            self._log_operation("disconnect", True)
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("disconnect", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_DISCONNECTION_FAILED",
                f"Failed to disconnect from mock device: {str(e)}",
                {"device_id": self._device_id}
            )
    
    async def is_connected(self) -> bool:
        """Check mock connection status"""
        return self._is_connected
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device with current status"""
        # Update status based on connection
        if self._is_connected:
            if self._hardware_device.status != HardwareStatus.CONNECTED:
                self._hardware_device.set_status(HardwareStatus.CONNECTED)
        else:
            if self._hardware_device.status == HardwareStatus.CONNECTED:
                self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
        
        return self._hardware_device
    
    async def read_force_value(self) -> ForceValue:
        """Simulate force value reading with realistic behavior"""
        self._validate_connection("read_force_value")
        
        try:
            # Simulate reading delay
            await asyncio.sleep(0.01)
            
            # Generate simulated force with noise
            noise = random.gauss(0, self._force_noise_level)
            simulated_value = self._simulated_force + noise
            
            # Apply hold function
            if self._is_hold_enabled:
                # Hold the last "stable" reading
                pass  # Keep current simulated_value
            else:
                # Update simulated force with some drift
                drift = random.gauss(0, 0.01)
                self._simulated_force += drift
            
            # Convert to domain object
            force_value = ForceValue(simulated_value, MeasurementUnit.NEWTON)
            
            # Validate range
            if not await self.validate_force_range(force_value):
                logger.warning(f"Simulated force value {force_value} outside expected range")
            
            self._log_operation("read_force_value", True)
            return force_value
            
        except Exception as e:
            self._log_operation("read_force_value", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_FORCE_READING_FAILED",
                f"Failed to simulate force reading: {str(e)}",
                {"device_id": self._device_id}
            )
    
    async def read_multiple_samples(self, num_samples: int, interval_ms: float = 100) -> List[ForceValue]:
        """Simulate multiple sample reading"""
        self._validate_connection("read_multiple_samples")
        
        # Business rule validation
        if num_samples < 1:
            raise BusinessRuleViolationException(
                "INVALID_SAMPLE_COUNT",
                f"Number of samples must be at least 1, got {num_samples}",
                {"num_samples": num_samples}
            )
        
        if interval_ms < 1:  # More lenient for mock
            raise BusinessRuleViolationException(
                "INVALID_SAMPLE_INTERVAL",
                f"Sample interval must be at least 1ms, got {interval_ms}ms",
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
                "MOCK_MULTIPLE_SAMPLES_FAILED",
                f"Failed to simulate multiple samples: {str(e)}",
                {"num_samples": num_samples, "interval_ms": interval_ms}
            )
    
    async def get_raw_data(self) -> str:
        """Simulate raw data output"""
        self._validate_connection("get_raw_data")
        
        try:
            # Simulate raw data format similar to BS205
            current_force = await self.read_force_value()
            raw_data = f"MOCK,{current_force.value:.3f},N,{self._device_id}"
            
            self._log_operation("get_raw_data", True)
            return raw_data
            
        except Exception as e:
            self._log_operation("get_raw_data", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_RAW_DATA_FAILED",
                f"Failed to simulate raw data: {str(e)}",
                {"device_id": self._device_id}
            )
    
    async def zero_force(self) -> None:
        """Simulate auto-zero operation"""
        self._validate_connection("zero_force")
        
        try:
            # Simulate zero operation delay
            await asyncio.sleep(0.2)
            
            # Reset simulated force to zero
            self._simulated_force = 0.0
            
            self._log_operation("zero_force", True)
            
        except Exception as e:
            self._log_operation("zero_force", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_AUTO_ZERO_FAILED",
                f"Failed to simulate auto-zero: {str(e)}",
                {"device_id": self._device_id}
            )
    
    async def set_hold_enabled(self, enabled: bool) -> None:
        """Simulate hold function control"""
        self._validate_connection("set_hold_enabled")
        
        try:
            self._is_hold_enabled = enabled
            action = "enabled" if enabled else "disabled"
            self._log_operation(f"set_hold_{action}", True)
            
        except Exception as e:
            self._log_operation("set_hold_enabled", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_HOLD_OPERATION_FAILED",
                f"Failed to simulate hold function: {str(e)}",
                {"enabled": enabled, "device_id": self._device_id}
            )
    
    async def is_hold_enabled(self) -> bool:
        """Get hold function status"""
        self._validate_connection("is_hold_enabled")
        return self._is_hold_enabled
    
    async def get_measurement_statistics(self, num_samples: int) -> Dict[str, ForceValue]:
        """Calculate statistics from simulated samples"""
        if num_samples < 2:
            raise BusinessRuleViolationException(
                "INSUFFICIENT_SAMPLES",
                f"At least 2 samples required for statistics, got {num_samples}",
                {"num_samples": num_samples}
            )
        
        # Take multiple samples
        force_values = await self.read_multiple_samples(num_samples, interval_ms=10)
        
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
        """Simulate force test execution"""
        self._validate_connection("execute_force_test")
        
        try:
            # Simulate test execution delay
            await asyncio.sleep(0.5)
            
            # Simulate test results
            target_force = test_parameters.get('target_force', 100.0)
            tolerance = test_parameters.get('tolerance', 5.0)
            
            # Simulate measurement near target
            actual_force = target_force + random.gauss(0, tolerance / 3)
            test_passed = abs(actual_force - target_force) <= tolerance
            
            result = {
                'test_passed': test_passed,
                'target_force': target_force,
                'actual_force': actual_force,
                'tolerance': tolerance,
                'deviation': abs(actual_force - target_force),
                'timestamp': asyncio.get_event_loop().time(),
                'hardware_type': 'loadcell',
                'controller_type': 'Mock',
                'adapter_type': 'mock_adapter',
                'device_id': self._device_id,
                'device_capabilities': self._hardware_device.capabilities,
                'simulation_mode': True
            }
            
            self._log_operation("execute_force_test", True)
            return result
            
        except Exception as e:
            self._log_operation("execute_force_test", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_FORCE_TEST_FAILED",
                f"Failed to simulate force test: {str(e)}",
                {"test_parameters": test_parameters}
            )
    
    async def calibrate(self, reference_force: ForceValue) -> None:
        """Simulate calibration operation"""
        self._validate_connection("calibrate")
        
        try:
            # Simulate calibration delay
            await asyncio.sleep(1.0)
            
            # Update simulated offset based on reference
            current_reading = await self.read_force_value()
            calibration_offset = reference_force.value - current_reading.value
            self._simulated_force += calibration_offset
            
            self._log_operation("calibrate", True)
            
        except Exception as e:
            self._log_operation("calibrate", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_CALIBRATION_FAILED",
                f"Failed to simulate calibration: {str(e)}",
                {"reference_force": str(reference_force), "device_id": self._device_id}
            )
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get mock device information"""
        self._validate_connection("get_device_info")
        
        return {
            'model': 'MockLoadCell',
            'vendor': 'mock',
            'adapter_type': 'mock_adapter',
            'device_id': self._device_id,
            'connection_info': 'mock://loadcell',
            'communication_stats': {
                'total_commands': random.randint(100, 1000),
                'failed_commands': random.randint(0, 10),
                'last_command_time': asyncio.get_event_loop().time()
            },
            'capabilities': self._hardware_device.capabilities,
            'last_calibration': asyncio.get_event_loop().time(),
            'firmware_version': 'Mock v1.0.0',
            'simulation_mode': True,
            'noise_level': self._force_noise_level,
            'current_force_offset': self._simulated_force
        }
    
    async def get_measurement_range(self) -> Dict[str, ForceValue]:
        """Get measurement range from capabilities"""
        capabilities = self._hardware_device.capabilities
        
        return {
            'min_force': ForceValue(capabilities.get('min_force', -5000.0), MeasurementUnit.NEWTON),
            'max_force': ForceValue(capabilities.get('max_force', 5000.0), MeasurementUnit.NEWTON)
        }
    
    async def validate_force_range(self, force: ForceValue) -> bool:
        """Validate force value against measurement range"""
        if not self._is_connected:
            # Allow validation even when disconnected for testing
            pass
        
        measurement_range = await self.get_measurement_range()
        min_force = measurement_range['min_force']
        max_force = measurement_range['max_force']
        
        return min_force.value <= force.value <= max_force.value
    
    # Mock-specific methods for testing
    def set_simulated_force(self, force: float) -> None:
        """Set simulated force for testing scenarios"""
        self._simulated_force = force
    
    def set_noise_level(self, noise_level: float) -> None:
        """Set noise level for testing scenarios"""
        self._force_noise_level = noise_level