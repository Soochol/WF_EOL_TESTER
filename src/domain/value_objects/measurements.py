"""
Measurement Value Objects

Immutable value objects representing various measurements in the EOL testing system.
"""

from typing import Union
from domain.enums.measurement_units import MeasurementUnit
from domain.exceptions.validation_exceptions import ValidationException, InvalidRangeException


class BaseMeasurement:
    """Base class for measurement value objects"""
    
    def __init__(self, value: Union[int, float], unit: MeasurementUnit):
        """
        Initialize measurement
        
        Args:
            value: Numeric measurement value
            unit: Unit of measurement
            
        Raises:
            ValidationException: If value or unit is invalid
        """
        if not isinstance(value, (int, float)):
            raise ValidationException("measurement_value", value, "Measurement value must be numeric")
        
        if not isinstance(unit, MeasurementUnit):
            raise ValidationException("measurement_unit", unit, "Unit must be MeasurementUnit enum")
        
        self._validate_value_range(value)
        self._validate_unit_compatibility(unit)
        
        self._value = float(value)
        self._unit = unit
    
    def _validate_value_range(self, value: Union[int, float]) -> None:
        """Validate value is within acceptable range - override in subclasses"""
        if not (-1e10 <= value <= 1e10):  # Basic sanity check
            raise InvalidRangeException("measurement_value", value, -1e10, 1e10)
    
    def _validate_unit_compatibility(self, unit: MeasurementUnit) -> None:
        """Validate unit is compatible with measurement type - override in subclasses"""
        pass
    
    @property
    def value(self) -> float:
        """Get measurement value"""
        return self._value
    
    @property
    def unit(self) -> MeasurementUnit:
        """Get measurement unit"""
        return self._unit
    
    def __str__(self) -> str:
        return f"{self._value:.3f} {self._unit.value}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value}, {self._unit})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (abs(self._value - other._value) < 1e-9 and 
                self._unit == other._unit)
    
    def __hash__(self) -> int:
        return hash((self.__class__.__name__, round(self._value, 9), self._unit))
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(f"Cannot compare {self.__class__.__name__} with {type(other).__name__}")
        if self._unit != other._unit:
            raise ValueError(f"Cannot compare measurements with different units: {self._unit} vs {other._unit}")
        return self._value < other._value
    
    def __le__(self, other) -> bool:
        return self < other or self == other
    
    def __gt__(self, other) -> bool:
        return not self <= other
    
    def __ge__(self, other) -> bool:
        return not self < other


class ForceValue(BaseMeasurement):
    """Force measurement value object"""
    
    def _validate_value_range(self, value: Union[int, float]) -> None:
        # Force values in EOL testing typically range from -10000N to +10000N
        if not (-10000 <= value <= 10000):
            raise InvalidRangeException("force_value", value, -10000, 10000, {
                "measurement_type": "force",
                "common_range": "±10000N for EOL testing"
            })
    
    def _validate_unit_compatibility(self, unit: MeasurementUnit) -> None:
        if not unit.is_force_unit:
            raise ValidationException("force_unit", unit, f"Unit {unit} is not a force unit")
    
    @classmethod
    def from_raw_data(cls, raw_value: float, unit: MeasurementUnit = MeasurementUnit.NEWTON) -> 'ForceValue':
        """Create ForceValue from raw controller data"""
        return cls(raw_value, unit)
    
    @classmethod
    def zero(cls, unit: MeasurementUnit = MeasurementUnit.NEWTON) -> 'ForceValue':
        """Create zero force value"""
        return cls(0.0, unit)
    
    def is_within_tolerance(self, target: 'ForceValue', tolerance_percent: float) -> bool:
        """Check if force is within tolerance of target"""
        if self._unit != target._unit:
            raise ValueError("Cannot compare forces with different units")
        
        tolerance_abs = abs(target._value * tolerance_percent / 100.0)
        return abs(self._value - target._value) <= tolerance_abs


class VoltageValue(BaseMeasurement):
    """Voltage measurement value object"""
    
    def _validate_value_range(self, value: Union[int, float]) -> None:
        # Voltage values in EOL testing typically range from -1000V to +1000V
        if not (-1000 <= value <= 1000):
            raise InvalidRangeException("voltage_value", value, -1000, 1000, {
                "measurement_type": "voltage",
                "common_range": "±1000V for EOL testing"
            })
    
    def _validate_unit_compatibility(self, unit: MeasurementUnit) -> None:
        if unit not in (MeasurementUnit.VOLT, MeasurementUnit.MILLIVOLT):
            raise ValidationException("voltage_unit", unit, f"Unit {unit} is not a voltage unit")
    
    @classmethod
    def from_raw_data(cls, raw_value: float, unit: MeasurementUnit = MeasurementUnit.VOLT) -> 'VoltageValue':
        """Create VoltageValue from raw controller data"""
        return cls(raw_value, unit)
    
    def to_volts(self) -> float:
        """Convert to volts regardless of current unit"""
        if self._unit == MeasurementUnit.VOLT:
            return self._value
        elif self._unit == MeasurementUnit.MILLIVOLT:
            return self._value / 1000.0
        else:
            raise ValueError(f"Cannot convert {self._unit} to volts")


class CurrentValue(BaseMeasurement):
    """Current measurement value object"""
    
    def _validate_value_range(self, value: Union[int, float]) -> None:
        # Current values in EOL testing typically range from -100A to +100A
        if not (-100 <= value <= 100):
            raise InvalidRangeException("current_value", value, -100, 100, {
                "measurement_type": "current",
                "common_range": "±100A for EOL testing"
            })
    
    def _validate_unit_compatibility(self, unit: MeasurementUnit) -> None:
        if unit not in (MeasurementUnit.AMPERE, MeasurementUnit.MILLIAMPERE, MeasurementUnit.MICROAMPERE):
            raise ValidationException("current_unit", unit, f"Unit {unit} is not a current unit")
    
    @classmethod
    def from_raw_data(cls, raw_value: float, unit: MeasurementUnit = MeasurementUnit.AMPERE) -> 'CurrentValue':
        """Create CurrentValue from raw controller data"""
        return cls(raw_value, unit)
    
    def to_amperes(self) -> float:
        """Convert to amperes regardless of current unit"""
        if self._unit == MeasurementUnit.AMPERE:
            return self._value
        elif self._unit == MeasurementUnit.MILLIAMPERE:
            return self._value / 1000.0
        elif self._unit == MeasurementUnit.MICROAMPERE:
            return self._value / 1000000.0
        else:
            raise ValueError(f"Cannot convert {self._unit} to amperes")


class TemperatureValue(BaseMeasurement):
    """Temperature measurement value object"""
    
    def _validate_value_range(self, value: Union[int, float]) -> None:
        # Temperature values for MCU control typically range from -40°C to +200°C
        if not (-40 <= value <= 200):
            raise InvalidRangeException("temperature_value", value, -40, 200, {
                "measurement_type": "temperature",
                "common_range": "-40°C to +200°C for MCU operations"
            })
    
    def _validate_unit_compatibility(self, unit: MeasurementUnit) -> None:
        if unit not in (MeasurementUnit.CELSIUS, MeasurementUnit.FAHRENHEIT, MeasurementUnit.KELVIN):
            raise ValidationException("temperature_unit", unit, f"Unit {unit} is not a temperature unit")
    
    @classmethod
    def from_raw_data(cls, raw_value: float, unit: MeasurementUnit = MeasurementUnit.CELSIUS) -> 'TemperatureValue':
        """Create TemperatureValue from raw controller data"""
        return cls(raw_value, unit)
    
    def to_celsius(self) -> float:
        """Convert to Celsius regardless of current unit"""
        if self._unit == MeasurementUnit.CELSIUS:
            return self._value
        elif self._unit == MeasurementUnit.FAHRENHEIT:
            return (self._value - 32) * 5.0 / 9.0
        elif self._unit == MeasurementUnit.KELVIN:
            return self._value - 273.15
        else:
            raise ValueError(f"Cannot convert {self._unit} to celsius")
    
    def to_fahrenheit(self) -> float:
        """Convert to Fahrenheit regardless of current unit"""
        celsius = self.to_celsius()
        return celsius * 9.0 / 5.0 + 32
    
    def to_kelvin(self) -> float:
        """Convert to Kelvin regardless of current unit"""
        celsius = self.to_celsius()
        return celsius + 273.15


class PositionValue(BaseMeasurement):
    """Position measurement value object for robot control"""
    
    def _validate_value_range(self, value: Union[int, float]) -> None:
        # Position values for robot control typically range from -10000mm to +10000mm
        if not (-10000 <= value <= 10000):
            raise InvalidRangeException("position_value", value, -10000, 10000, {
                "measurement_type": "position",
                "common_range": "±10000mm for robot control"
            })
    
    def _validate_unit_compatibility(self, unit: MeasurementUnit) -> None:
        if unit not in (MeasurementUnit.MILLIMETER, MeasurementUnit.MICROMETER, MeasurementUnit.METER):
            raise ValidationException("position_unit", unit, f"Unit {unit} is not a position unit")
    
    @classmethod
    def from_raw_data(cls, raw_value: float, unit: MeasurementUnit = MeasurementUnit.MILLIMETER) -> 'PositionValue':
        """Create PositionValue from raw controller data"""
        return cls(raw_value, unit)
    
    def to_millimeters(self) -> float:
        """Convert to millimeters regardless of current unit"""
        if self._unit == MeasurementUnit.MILLIMETER:
            return self._value
        elif self._unit == MeasurementUnit.MICROMETER:
            return self._value / 1000.0
        elif self._unit == MeasurementUnit.METER:
            return self._value * 1000.0
        else:
            raise ValueError(f"Cannot convert {self._unit} to millimeters")
    
    def to_meters(self) -> float:
        """Convert to meters regardless of current unit"""
        mm = self.to_millimeters()
        return mm / 1000.0


class VelocityValue(BaseMeasurement):
    """Velocity measurement value object for robot control"""
    
    def _validate_value_range(self, value: Union[int, float]) -> None:
        # Velocity values for robot control typically range from 0 to 10000mm/s
        if not (0 <= value <= 10000):
            raise InvalidRangeException("velocity_value", value, 0, 10000, {
                "measurement_type": "velocity",
                "common_range": "0 to 10000mm/s for robot control"
            })
    
    def _validate_unit_compatibility(self, unit: MeasurementUnit) -> None:
        if unit not in (MeasurementUnit.MM_PER_SEC, MeasurementUnit.M_PER_SEC):
            raise ValidationException("velocity_unit", unit, f"Unit {unit} is not a velocity unit")
    
    @classmethod
    def from_raw_data(cls, raw_value: float, unit: MeasurementUnit = MeasurementUnit.MM_PER_SEC) -> 'VelocityValue':
        """Create VelocityValue from raw controller data"""
        return cls(raw_value, unit)
    
    def to_mm_per_sec(self) -> float:
        """Convert to mm/s regardless of current unit"""
        if self._unit == MeasurementUnit.MM_PER_SEC:
            return self._value
        elif self._unit == MeasurementUnit.M_PER_SEC:
            return self._value * 1000.0
        else:
            raise ValueError(f"Cannot convert {self._unit} to mm/s")
    
    def to_m_per_sec(self) -> float:
        """Convert to m/s regardless of current unit"""
        mm_per_sec = self.to_mm_per_sec()
        return mm_per_sec / 1000.0


class ResistanceValue(BaseMeasurement):
    """Resistance measurement value object"""
    
    def _validate_value_range(self, value: Union[int, float]) -> None:
        # Resistance values must be positive and within reasonable range
        if value < 0:
            raise InvalidRangeException("resistance_value", value, 0, float('inf'), {
                "measurement_type": "resistance",
                "note": "Resistance cannot be negative"
            })
        
        if not (0 <= value <= 1e12):  # Up to 1TΩ
            raise InvalidRangeException("resistance_value", value, 0, 1e12, {
                "measurement_type": "resistance",
                "common_range": "0 to 1TΩ for EOL testing"
            })
    
    def _validate_unit_compatibility(self, unit: MeasurementUnit) -> None:
        if unit not in (MeasurementUnit.OHM, MeasurementUnit.KILOOHM, MeasurementUnit.MEGAOHM):
            raise ValidationException("resistance_unit", unit, f"Unit {unit} is not a resistance unit")
    
    @classmethod
    def from_raw_data(cls, raw_value: float, unit: MeasurementUnit = MeasurementUnit.OHM) -> 'ResistanceValue':
        """Create ResistanceValue from raw controller data"""
        return cls(raw_value, unit)
    
    def to_ohms(self) -> float:
        """Convert to ohms regardless of current unit"""
        if self._unit == MeasurementUnit.OHM:
            return self._value
        elif self._unit == MeasurementUnit.KILOOHM:
            return self._value * 1000.0
        elif self._unit == MeasurementUnit.MEGAOHM:
            return self._value * 1000000.0
        else:
            raise ValueError(f"Cannot convert {self._unit} to ohms")