"""
Measurement Value Objects

Immutable value objects representing various measurements in the EOL testing system.
Provides type-safe measurement handling with proper validation, unit conversion,
and structured access to test measurement data collections.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from domain.enums.measurement_units import MeasurementUnit
from domain.exceptions.validation_exceptions import ValidationException


class BaseMeasurement:
    """
    Base class for measurement value objects
    
    Provides common functionality for all measurement types including
    validation, unit handling, and standardized representation.
    All measurement classes inherit from this base to ensure consistency.
    """

    def __init__(self, value: Union[int, float], unit: MeasurementUnit) -> None:
        """Initialize measurement with validation
        
        Args:
            value: Numeric measurement value
            unit: Measurement unit from MeasurementUnit enum
            
        Raises:
            ValidationException: If value is not numeric or unit is invalid
        """
        self._validate_value(value)
        self._validate_unit(unit)
        
        self._value = float(value)
        self._unit = unit
    
    def _validate_value(self, value: Union[int, float]) -> None:
        """Validate measurement value"""
        if not isinstance(value, (int, float)):
            raise ValidationException(
                "measurement_value",
                value,
                "Measurement value must be numeric",
            )
        
        if not (-1e6 <= value <= 1e6):  # Reasonable range check
            raise ValidationException(
                "measurement_value",
                value,
                "Measurement value outside reasonable range (-1M to 1M)",
            )
    
    def _validate_unit(self, unit: MeasurementUnit) -> None:
        """Validate measurement unit"""
        if not isinstance(unit, MeasurementUnit):
            raise ValidationException(
                "measurement_unit",
                unit,
                "Unit must be MeasurementUnit enum",
            )

    @property
    def value(self) -> float:
        """Get measurement value
        
        Returns:
            Numeric measurement value
        """
        return self._value

    @property
    def unit(self) -> MeasurementUnit:
        """Get measurement unit
        
        Returns:
            MeasurementUnit enum value
        """
        return self._unit

    def __str__(self) -> str:
        """Human-readable string representation"""
        return f"{self._value:.3f} {self._unit.value}"

    def __repr__(self) -> str:
        """Debug representation"""
        return f"{self.__class__.__name__}({self._value}, {self._unit})"

    def __eq__(self, other: object) -> bool:
        """Check equality with tolerance for floating point comparison"""
        if not isinstance(other, self.__class__):
            return False
        return abs(self._value - other._value) < 1e-9 and self._unit == other._unit
    
    def __hash__(self) -> int:
        """Make measurement hashable for use in sets and as dict keys"""
        return hash((round(self._value, 9), self._unit))

    def __format__(self, format_spec: str) -> str:
        """Format the measurement value according to the format specification
        
        Args:
            format_spec: Python format specification string
            
        Returns:
            Formatted value string
        """
        if format_spec:
            return format(self._value, format_spec)
        return str(self._value)
    
    def is_valid(self) -> bool:
        """Check if measurement is valid
        
        Returns:
            True if measurement value and unit are valid
        """
        try:
            self._validate_value(self._value)
            self._validate_unit(self._unit)
            return True
        except ValidationException:
            return False


class ForceValue(BaseMeasurement):
    """Force measurement value object
    
    Specialized measurement class for force values with validation
    specific to force measurements and convenient factory methods.
    """
    
    def _validate_value(self, value: Union[int, float]) -> None:
        """Validate force-specific value constraints"""
        super()._validate_value(value)
        
        # Force-specific validations
        if value < 0:
            raise ValidationException(
                "force_value",
                value,
                "Force value cannot be negative",
            )
    
    @classmethod
    def from_raw_data(
        cls,
        raw_value: float,
        unit: MeasurementUnit = MeasurementUnit.KILOGRAM_FORCE,
    ) -> "ForceValue":
        """Create ForceValue from raw controller data
        
        Args:
            raw_value: Raw force measurement from hardware
            unit: Unit of the raw measurement
            
        Returns:
            Validated ForceValue instance
        """
        return cls(raw_value, unit)
    
    @classmethod
    def from_newtons(cls, newtons: float) -> "ForceValue":
        """Create ForceValue from Newtons
        
        Args:
            newtons: Force value in Newtons
            
        Returns:
            ForceValue instance with NEWTON unit
        """
        return cls(newtons, MeasurementUnit.NEWTON)


class VoltageValue(BaseMeasurement):
    """Voltage measurement value object
    
    Specialized measurement class for electrical voltage values.
    """
    
    @classmethod
    def from_volts(cls, volts: float) -> "VoltageValue":
        """Create VoltageValue from volts
        
        Args:
            volts: Voltage value in volts
            
        Returns:
            VoltageValue instance
        """
        return cls(volts, MeasurementUnit.VOLT)


class CurrentValue(BaseMeasurement):
    """Current measurement value object
    
    Specialized measurement class for electrical current values.
    """
    
    @classmethod
    def from_amperes(cls, amperes: float) -> "CurrentValue":
        """Create CurrentValue from amperes
        
        Args:
            amperes: Current value in amperes
            
        Returns:
            CurrentValue instance
        """
        return cls(amperes, MeasurementUnit.AMPERE)


class ResistanceValue(BaseMeasurement):
    """Resistance measurement value object
    
    Specialized measurement class for electrical resistance values.
    """
    
    @classmethod
    def from_ohms(cls, ohms: float) -> "ResistanceValue":
        """Create ResistanceValue from ohms
        
        Args:
            ohms: Resistance value in ohms
            
        Returns:
            ResistanceValue instance
        """
        return cls(ohms, MeasurementUnit.OHM)


# ========================================================================
# TEST MEASUREMENT COLLECTIONS
# ========================================================================


@dataclass(frozen=True)
class MeasurementReading:
    """
    Individual measurement reading combining force value with timestamp

    Represents a single measurement reading in a test sequence.
    Uses ForceValue for proper validation and unit handling.
    Immutable to ensure measurement integrity.
    """

    force_value: ForceValue
    timestamp: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Validate measurement reading after initialization"""
        if not isinstance(self.force_value, ForceValue):
            raise ValidationException(
                "force_value",
                self.force_value,
                "force_value must be a ForceValue instance",
            )

    @classmethod
    def from_raw_force(
        cls,
        force: float,
        timestamp: Optional[datetime] = None,
        unit: MeasurementUnit = MeasurementUnit.KILOGRAM_FORCE,
    ) -> "MeasurementReading":
        """Create measurement reading from raw force value
        
        Args:
            force: Raw force measurement value
            timestamp: Optional timestamp of measurement
            unit: Unit of the force measurement
            
        Returns:
            MeasurementReading instance with validated force value
        """
        force_value = ForceValue.from_raw_data(force, unit)
        return cls(force_value=force_value, timestamp=timestamp)
    
    @classmethod
    def create_now(cls, force: float, unit: MeasurementUnit = MeasurementUnit.KILOGRAM_FORCE) -> "MeasurementReading":
        """Create measurement reading with current timestamp
        
        Args:
            force: Force measurement value
            unit: Unit of the force measurement
            
        Returns:
            MeasurementReading with current timestamp
        """
        return cls.from_raw_force(force, datetime.now(), unit)

    @property
    def force(self) -> float:
        """Get force value in configured unit
        
        Returns:
            Force measurement value as float
        """
        return self.force_value.value
    
    @property
    def unit(self) -> MeasurementUnit:
        """Get force measurement unit
        
        Returns:
            MeasurementUnit enum value
        """
        return self.force_value.unit
    
    def is_timestamped(self) -> bool:
        """Check if reading has timestamp
        
        Returns:
            True if timestamp is available
        """
        return self.timestamp is not None

    def __str__(self) -> str:
        """Human-readable string representation"""
        timestamp_str = f" at {self.timestamp.strftime('%H:%M:%S')}" if self.timestamp else ""
        return f"MeasurementReading(force={self.force:.2f}{self.force_value.unit.value}{timestamp_str})"

    def __repr__(self) -> str:
        """Debug representation"""
        return f"MeasurementReading(force_value={self.force_value!r}, timestamp={self.timestamp!r})"


@dataclass(frozen=True)
class PositionMeasurements:
    """
    Measurements at different positions for a given temperature

    Contains measurement readings for multiple positions at a specific temperature.
    Provides convenient access methods and position-based operations.
    Immutable collection ensuring measurement data integrity.
    """

    _readings: Dict[float, MeasurementReading]

    def __post_init__(self) -> None:
        """Validate position measurements on creation
        
        Raises:
            ValidationException: If readings are empty or contain invalid data
        """
        if not self._readings:
            raise ValidationException(
                "position_readings",
                self._readings,
                "Position measurements cannot be empty",
            )
        
        # Validate all readings are MeasurementReading instances
        for position, reading in self._readings.items():
            if not isinstance(reading, MeasurementReading):
                raise ValidationException(
                    f"position_reading[{position}]",
                    reading,
                    "All readings must be MeasurementReading instances",
                )
            
            if position < 0:
                raise ValidationException(
                    f"position[{position}]",
                    position,
                    "Position values cannot be negative",
                )

    def get_reading(self, position: float) -> Optional[MeasurementReading]:
        """Get measurement reading at specific position
        
        Args:
            position: Position value to look up
            
        Returns:
            MeasurementReading if position exists, None otherwise
        """
        return self._readings.get(position)

    def get_force(self, position: float) -> Optional[float]:
        """Get force value at specific position
        
        Args:
            position: Position value to look up
            
        Returns:
            Force value if position exists, None otherwise
        """
        reading = self.get_reading(position)
        return reading.force if reading else None

    def get_force_value(self, position: float) -> Optional[ForceValue]:
        """Get ForceValue object at specific position
        
        Args:
            position: Position value to look up
            
        Returns:
            ForceValue instance if position exists, None otherwise
        """
        reading = self.get_reading(position)
        return reading.force_value if reading else None

    def get_positions(self) -> List[float]:
        """Get all measured positions sorted in ascending order
        
        Returns:
            List of position values in ascending order
        """
        return sorted(self._readings.keys())

    def get_position_count(self) -> int:
        """Get number of positions measured
        
        Returns:
            Number of position measurements
        """
        return len(self._readings)

    def has_position(self, position: float) -> bool:
        """Check if position was measured
        
        Args:
            position: Position value to check
            
        Returns:
            True if position has measurement data
        """
        return position in self._readings
    
    def get_force_range(self) -> Tuple[float, float]:
        """Get minimum and maximum force values across all positions
        
        Returns:
            Tuple of (min_force, max_force)
            
        Raises:
            ValueError: If no measurements available
        """
        if not self._readings:
            raise ValueError("No measurements available")
            
        forces = [reading.force for reading in self._readings.values()]
        return (min(forces), max(forces))
    
    def get_average_force(self) -> float:
        """Get average force across all positions
        
        Returns:
            Average force value
            
        Raises:
            ValueError: If no measurements available
        """
        if not self._readings:
            raise ValueError("No measurements available")
            
        forces = [reading.force for reading in self._readings.values()]
        return sum(forces) / len(forces)

    def to_dict(self) -> Dict[float, Dict[str, float]]:
        """Convert to dictionary format for serialization
        
        Returns:
            Dictionary mapping positions to force values
        """
        return {position: {"force": reading.force} for position, reading in self._readings.items()}

    @classmethod
    def from_dict(cls, data: Dict[float, Dict[str, float]]) -> "PositionMeasurements":
        """Create from dictionary format
        
        Args:
            data: Dictionary mapping positions to force data
            
        Returns:
            PositionMeasurements instance
            
        Raises:
            ValidationException: If data format is invalid
        """
        if not data:
            raise ValidationException(
                "position_data",
                data,
                "Position data cannot be empty",
            )
            
        readings = {}
        for position, force_data in data.items():
            if "force" not in force_data:
                raise ValidationException(
                    f"position_data[{position}]",
                    force_data,
                    "Missing 'force' key in position data",
                )
            readings[position] = MeasurementReading.from_raw_force(force_data["force"])
        return cls(_readings=readings)

    def __str__(self) -> str:
        """Human-readable string representation"""
        count = len(self._readings)
        force_range = self.get_force_range() if count > 0 else (0, 0)
        return f"PositionMeasurements({count} positions, force range: {force_range[0]:.2f}-{force_range[1]:.2f})"

    def __repr__(self) -> str:
        """Debug representation"""
        return f"PositionMeasurements(_readings={dict(self._readings)})"
    
    def __len__(self) -> int:
        """Return number of position measurements"""
        return len(self._readings)
    
    def __contains__(self, position: float) -> bool:
        """Check if position is in measurements"""
        return position in self._readings
    
    def __iter__(self) -> Iterator[Tuple[float, MeasurementReading]]:
        """Allow iteration over position-reading pairs"""
        for position in self.get_positions():
            yield position, self._readings[position]


@dataclass(frozen=True)
class TestMeasurements:
    """
    Complete test measurements across all temperatures and positions

    Contains the complete measurement matrix for an EOL test.
    Provides high-level operations for accessing and analyzing measurement data.
    """

    _measurements: Dict[float, PositionMeasurements]

    def __post_init__(self) -> None:
        """Validate test measurements on creation
        
        Raises:
            ValidationException: If measurements are empty or contain invalid data
        """
        if not self._measurements:
            raise ValidationException(
                "test_measurements",
                self._measurements,
                "Test measurements cannot be empty",
            )
        
        # Validate all measurements are PositionMeasurements instances
        for temperature, pos_measurements in self._measurements.items():
            if not isinstance(pos_measurements, PositionMeasurements):
                raise ValidationException(
                    f"temperature_measurement[{temperature}]",
                    pos_measurements,
                    "All temperature measurements must be PositionMeasurements instances",
                )
            
            if temperature < -100 or temperature > 200:
                raise ValidationException(
                    f"temperature[{temperature}]",
                    temperature,
                    "Temperature should be between -100°C and 200°C",
                )

    def get_temperature_measurements(self, temperature: float) -> Optional[PositionMeasurements]:
        """Get all measurements for a specific temperature"""
        return self._measurements.get(temperature)

    def get_force(self, temperature: float, position: float) -> Optional[float]:
        """Get force value at specific temperature and position"""
        temp_measurements = self.get_temperature_measurements(temperature)
        return temp_measurements.get_force(position) if temp_measurements else None

    def get_force_value(self, temperature: float, position: float) -> Optional[ForceValue]:
        """Get ForceValue object at specific temperature and position"""
        temp_measurements = self.get_temperature_measurements(temperature)
        return temp_measurements.get_force_value(position) if temp_measurements else None

    def get_reading(self, temperature: float, position: float) -> Optional[MeasurementReading]:
        """Get measurement reading at specific temperature and position"""
        temp_measurements = self.get_temperature_measurements(temperature)
        return temp_measurements.get_reading(position) if temp_measurements else None

    def get_temperatures(self) -> List[float]:
        """Get all measured temperatures sorted in ascending order"""
        return sorted(self._measurements.keys())

    def get_temperature_count(self) -> int:
        """Get number of temperatures measured"""
        return len(self._measurements)

    def get_positions_for_temperature(self, temperature: float) -> List[float]:
        """Get all positions measured at specific temperature"""
        temp_measurements = self.get_temperature_measurements(temperature)
        return temp_measurements.get_positions() if temp_measurements else []

    def get_total_measurement_count(self) -> int:
        """Get total number of individual measurements across all temperatures and positions"""
        return sum(
            pos_measurements.get_position_count()
            for pos_measurements in self._measurements.values()
        )

    def get_measurement_matrix(self) -> Dict[Tuple[float, float], float]:
        """
        Get flattened temperature-position-force mapping

        Returns:
            Dictionary with (temperature, position) tuple keys and force values
        """
        result = {}
        for temp, pos_measurements in self._measurements.items():
            for pos in pos_measurements.get_positions():
                force = pos_measurements.get_force(pos)
                if force is not None:
                    result[(temp, pos)] = force
        return result
    
    def get_temperature_range(self) -> Tuple[float, float]:
        """Get minimum and maximum temperatures measured
        
        Returns:
            Tuple of (min_temperature, max_temperature)
        """
        temps = self.get_temperatures()
        return (min(temps), max(temps))
    
    def get_position_range(self) -> Tuple[float, float]:
        """Get minimum and maximum positions across all temperatures
        
        Returns:
            Tuple of (min_position, max_position)
        """
        all_positions = set()
        for pos_measurements in self._measurements.values():
            all_positions.update(pos_measurements.get_positions())
        positions = list(all_positions)
        return (min(positions), max(positions))
    
    def get_force_range(self) -> Tuple[float, float]:
        """Get minimum and maximum force values across all measurements
        
        Returns:
            Tuple of (min_force, max_force)
        """
        all_forces = []
        for pos_measurements in self._measurements.values():
            for _, reading in pos_measurements:
                all_forces.append(reading.force)
        return (min(all_forces), max(all_forces))
    
    def is_complete_matrix(self, expected_temperatures: List[float], expected_positions: List[float]) -> bool:
        """Check if measurement matrix is complete for expected test points
        
        Args:
            expected_temperatures: List of expected temperature points
            expected_positions: List of expected position points
            
        Returns:
            True if all expected combinations have measurements
        """
        for temp in expected_temperatures:
            if temp not in self._measurements:
                return False
            pos_measurements = self._measurements[temp]
            for pos in expected_positions:
                if not pos_measurements.has_position(pos):
                    return False
        return True

    def to_legacy_dict(self) -> Dict[float, Dict[float, Dict[str, float]]]:
        """
        Convert to legacy nested dict format for backward compatibility

        Returns:
            Dictionary in format: {temperature: {position: {"force": value}}}
        """
        result = {}
        for temp, pos_measurements in self._measurements.items():
            result[temp] = pos_measurements.to_dict()
        return result

    @classmethod
    def from_legacy_dict(cls, data: Dict[float, Dict[float, Dict[str, float]]]) -> "TestMeasurements":
        """
        Create TestMeasurements from legacy nested dict format

        Args:
            data: Dictionary in format: {temperature: {position: {"force": value}}}

        Returns:
            TestMeasurements instance
            
        Raises:
            ValidationException: If data format is invalid
        """
        if not data:
            raise ValidationException(
                "test_data",
                data,
                "Test measurement data cannot be empty",
            )
            
        measurements = {}
        for temp, positions_data in data.items():
            measurements[temp] = PositionMeasurements.from_dict(positions_data)
        return cls(_measurements=measurements)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for serialization
        
        Returns:
            Dictionary with measurements and metadata
        """
        temp_range = self.get_temperature_range()
        pos_range = self.get_position_range()
        force_range = self.get_force_range()
        
        return {
            "measurements": self.to_legacy_dict(),
            "metadata": {
                "temperature_count": self.get_temperature_count(),
                "total_measurement_count": self.get_total_measurement_count(),
                "temperature_range": temp_range,
                "position_range": pos_range,
                "force_range": force_range,
            },
        }

    def __str__(self) -> str:
        """Human-readable string representation"""
        temp_count = self.get_temperature_count()
        total_count = self.get_total_measurement_count()
        temp_range = self.get_temperature_range()
        force_range = self.get_force_range()
        return (
            f"TestMeasurements({temp_count} temps [{temp_range[0]:.1f}-{temp_range[1]:.1f}°C], "
            f"{total_count} measurements, force [{force_range[0]:.2f}-{force_range[1]:.2f}])"
        )

    def __repr__(self) -> str:
        """Debug representation"""
        return f"TestMeasurements(_measurements={dict(self._measurements)})"

    def __iter__(self) -> Iterator[Tuple[float, PositionMeasurements]]:
        """Allow iteration over temperature-measurements pairs"""
        for temp in self.get_temperatures():
            yield temp, self._measurements[temp]

    def __len__(self) -> int:
        """Return number of temperatures measured"""
        return len(self._measurements)

    def __contains__(self, temperature: float) -> bool:
        """Check if temperature was measured"""
        return temperature in self._measurements
