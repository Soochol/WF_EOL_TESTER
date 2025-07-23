"""
Measurement Entity

Represents a single measurement taken during EOL testing.
"""

from typing import Dict, Any, Optional, Union
from domain.value_objects.identifiers import MeasurementId, TestId
from domain.value_objects.measurements import BaseMeasurement, ForceValue, VoltageValue, CurrentValue, ResistanceValue
from domain.value_objects.time_values import Timestamp
from domain.enums.measurement_units import MeasurementUnit
from domain.exceptions.validation_exceptions import ValidationException


class Measurement:
    """Single measurement entity"""
    
    def __init__(
        self,
        measurement_id: MeasurementId,
        test_id: TestId,
        measurement_type: str,
        measurement_value: BaseMeasurement,
        hardware_device_type: str,
        timestamp: Optional[Timestamp] = None,
        sequence_number: Optional[int] = None,
        raw_data: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize measurement
        
        Args:
            measurement_id: Unique identifier for this measurement
            test_id: ID of the test this measurement belongs to
            measurement_type: Type of measurement (e.g., 'force', 'voltage', 'current')
            measurement_value: The measured value with units
            hardware_device_type: Type of device that took the measurement
            timestamp: When measurement was taken (defaults to now)
            sequence_number: Sequence number within the test
            raw_data: Raw data string from hardware
            metadata: Additional measurement metadata
            
        Raises:
            ValidationException: If required fields are invalid
        """
        self._validate_required_fields(
            measurement_id, test_id, measurement_type, 
            measurement_value, hardware_device_type
        )
        
        self._measurement_id = measurement_id
        self._test_id = test_id
        self._measurement_type = measurement_type.lower().strip()
        self._measurement_value = measurement_value
        self._hardware_device_type = hardware_device_type.lower().strip()
        self._timestamp = timestamp or Timestamp.now()
        self._sequence_number = sequence_number
        self._raw_data = raw_data
        self._metadata = metadata or {}
        
        # Validate measurement type matches measurement value
        self._validate_measurement_type_consistency()
    
    def _validate_required_fields(
        self, 
        measurement_id: MeasurementId, 
        test_id: TestId, 
        measurement_type: str,
        measurement_value: BaseMeasurement, 
        hardware_device_type: str
    ) -> None:
        """Validate required fields"""
        if not isinstance(measurement_id, MeasurementId):
            raise ValidationException("measurement_id", measurement_id, "Measurement ID must be MeasurementId instance")
        
        if not isinstance(test_id, TestId):
            raise ValidationException("test_id", test_id, "Test ID must be TestId instance")
        
        if not measurement_type or not measurement_type.strip():
            raise ValidationException("measurement_type", measurement_type, "Measurement type is required")
        
        if not isinstance(measurement_value, BaseMeasurement):
            raise ValidationException("measurement_value", measurement_value, "Measurement value must be BaseMeasurement instance")
        
        if not hardware_device_type or not hardware_device_type.strip():
            raise ValidationException("hardware_device_type", hardware_device_type, "Hardware device type is required")
        
        # Validate measurement type
        valid_measurement_types = {'force', 'voltage', 'current', 'resistance', 'temperature', 'frequency', 'time'}
        if measurement_type.lower().strip() not in valid_measurement_types:
            raise ValidationException(
                "measurement_type", 
                measurement_type, 
                f"Measurement type must be one of: {', '.join(valid_measurement_types)}"
            )
    
    def _validate_measurement_type_consistency(self) -> None:
        """Validate that measurement type matches measurement value type"""
        type_mapping = {
            'force': ForceValue,
            'voltage': VoltageValue,
            'current': CurrentValue,
            'resistance': ResistanceValue
        }
        
        expected_type = type_mapping.get(self._measurement_type)
        if expected_type and not isinstance(self._measurement_value, expected_type):
            raise ValidationException(
                "measurement_consistency",
                type(self._measurement_value).__name__,
                f"Measurement type '{self._measurement_type}' requires {expected_type.__name__} value"
            )
    
    @property
    def measurement_id(self) -> MeasurementId:
        """Get measurement identifier"""
        return self._measurement_id
    
    @property
    def test_id(self) -> TestId:
        """Get test identifier"""
        return self._test_id
    
    @property
    def measurement_type(self) -> str:
        """Get measurement type"""
        return self._measurement_type
    
    @property
    def measurement_value(self) -> BaseMeasurement:
        """Get measurement value"""
        return self._measurement_value
    
    @property
    def hardware_device_type(self) -> str:
        """Get hardware device type"""
        return self._hardware_device_type
    
    @property
    def timestamp(self) -> Timestamp:
        """Get measurement timestamp"""
        return self._timestamp
    
    @property
    def sequence_number(self) -> Optional[int]:
        """Get sequence number"""
        return self._sequence_number
    
    @property
    def raw_data(self) -> Optional[str]:
        """Get raw data"""
        return self._raw_data
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get measurement metadata"""
        return self._metadata.copy()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get specific metadata value"""
        return self._metadata.get(key, default)
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update measurement metadata"""
        if not isinstance(metadata, dict):
            raise ValidationException("metadata", metadata, "Metadata must be a dictionary")
        
        self._metadata.update(metadata)
    
    def get_numeric_value(self) -> float:
        """Get numeric value regardless of units"""
        return self._measurement_value.value
    
    def get_unit(self) -> MeasurementUnit:
        """Get measurement unit"""
        return self._measurement_value.unit
    
    def is_within_range(self, min_value: float, max_value: float) -> bool:
        """Check if measurement is within specified range"""
        value = self.get_numeric_value()
        return min_value <= value <= max_value
    
    def is_within_tolerance(self, target_value: float, tolerance_percent: float) -> bool:
        """Check if measurement is within tolerance of target"""
        value = self.get_numeric_value()
        tolerance_abs = abs(target_value * tolerance_percent / 100.0)
        return abs(value - target_value) <= tolerance_abs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert measurement to dictionary representation"""
        return {
            'measurement_id': str(self._measurement_id),
            'test_id': str(self._test_id),
            'measurement_type': self._measurement_type,
            'measurement_value': self._measurement_value.value,
            'measurement_unit': self._measurement_value.unit.value,
            'hardware_device_type': self._hardware_device_type,
            'timestamp': self._timestamp.to_iso(),
            'sequence_number': self._sequence_number,
            'raw_data': self._raw_data,
            'metadata': self._metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Measurement':
        """Create measurement from dictionary representation"""
        # Reconstruct measurement value based on type
        measurement_type = data['measurement_type']
        value = data['measurement_value']
        unit = MeasurementUnit(data['measurement_unit'])
        
        # Create appropriate measurement value object
        measurement_value = cls._create_measurement_value(measurement_type, value, unit)
        
        return cls(
            measurement_id=MeasurementId(data['measurement_id']),
            test_id=TestId(data['test_id']),
            measurement_type=measurement_type,
            measurement_value=measurement_value,
            hardware_device_type=data['hardware_device_type'],
            timestamp=Timestamp.from_iso(data['timestamp']),
            sequence_number=data.get('sequence_number'),
            raw_data=data.get('raw_data'),
            metadata=data.get('metadata', {})
        )
    
    @classmethod
    def _create_measurement_value(cls, measurement_type: str, value: float, unit: MeasurementUnit) -> BaseMeasurement:
        """Create appropriate measurement value object based on type"""
        type_mapping = {
            'force': ForceValue,
            'voltage': VoltageValue,
            'current': CurrentValue,
            'resistance': ResistanceValue
        }
        
        value_class = type_mapping.get(measurement_type.lower())
        if value_class:
            return value_class(value, unit)
        else:
            # Fallback to BaseMeasurement for unknown types
            return BaseMeasurement(value, unit)
    
    @classmethod
    def create_force_measurement(
        cls,
        measurement_id: MeasurementId,
        test_id: TestId,
        force_value: ForceValue,
        hardware_device_type: str = "loadcell",
        **kwargs
    ) -> 'Measurement':
        """Create force measurement"""
        return cls(
            measurement_id=measurement_id,
            test_id=test_id,
            measurement_type="force",
            measurement_value=force_value,
            hardware_device_type=hardware_device_type,
            **kwargs
        )
    
    @classmethod
    def create_voltage_measurement(
        cls,
        measurement_id: MeasurementId,
        test_id: TestId,
        voltage_value: VoltageValue,
        hardware_device_type: str = "power_supply",
        **kwargs
    ) -> 'Measurement':
        """Create voltage measurement"""
        return cls(
            measurement_id=measurement_id,
            test_id=test_id,
            measurement_type="voltage",
            measurement_value=voltage_value,
            hardware_device_type=hardware_device_type,
            **kwargs
        )
    
    def __str__(self) -> str:
        return f"{self._measurement_type.title()}: {self._measurement_value} @ {self._timestamp}"
    
    def __repr__(self) -> str:
        return f"Measurement(id={self._measurement_id}, type={self._measurement_type}, value={self._measurement_value})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Measurement):
            return False
        return self._measurement_id == other._measurement_id
    
    def __hash__(self) -> int:
        return hash(self._measurement_id)