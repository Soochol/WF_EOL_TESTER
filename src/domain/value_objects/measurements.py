"""
Measurement Value Objects

Immutable value objects representing various measurements in the EOL testing system.
Includes individual measurement values and complete test measurement collections.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)

from domain.enums.measurement_units import MeasurementUnit
from domain.exceptions.validation_exceptions import (
    ValidationException,
)


class BaseMeasurement:
    """Base class for measurement value objects"""

    def __init__(
        self,
        value: Union[int, float],
        unit: MeasurementUnit,
    ):
        """Initialize measurement with basic validation"""
        if not isinstance(value, (int, float)):
            raise ValidationException(
                "measurement_value",
                value,
                "Measurement value must be numeric",
            )

        if not isinstance(unit, MeasurementUnit):
            raise ValidationException(
                "measurement_unit",
                unit,
                "Unit must be MeasurementUnit enum",
            )

        self._value = float(value)
        self._unit = unit

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
        return (
            abs(self._value - other._value) < 1e-9
            and self._unit == other._unit
        )


class ForceValue(BaseMeasurement):
    """Force measurement value object"""

    @classmethod
    def from_raw_data(
        cls,
        raw_value: float,
        unit: MeasurementUnit = MeasurementUnit.NEWTON,
    ) -> "ForceValue":
        """Create ForceValue from raw controller data"""
        return cls(raw_value, unit)


class VoltageValue(BaseMeasurement):
    """Voltage measurement value object"""


class CurrentValue(BaseMeasurement):
    """Current measurement value object"""


class ResistanceValue(BaseMeasurement):
    """Resistance measurement value object"""


# === Test Measurement Collections ===


@dataclass(frozen=True)
class MeasurementReading:
    """
    Individual measurement reading combining force value with timestamp

    Represents a single measurement reading in a test sequence.
    Uses ForceValue for proper validation and unit handling.
    """

    force_value: ForceValue
    timestamp: Optional[datetime] = None

    @classmethod
    def from_raw_force(
        cls,
        force: float,
        timestamp: Optional[datetime] = None,
    ) -> "MeasurementReading":
        """Create measurement reading from raw force value"""
        force_value = ForceValue.from_raw_data(force)
        return cls(
            force_value=force_value, timestamp=timestamp
        )

    @property
    def force(self) -> float:
        """Get force value in Newtons"""
        return self.force_value.value

    def __str__(self) -> str:
        return (
            f"MeasurementReading(force={self.force:.2f}N)"
        )

    def __repr__(self) -> str:
        return f"MeasurementReading(force_value={self.force_value}, timestamp={self.timestamp})"


@dataclass(frozen=True)
class PositionMeasurements:
    """
    Measurements at different positions for a given temperature

    Contains measurement readings for multiple positions at a specific temperature.
    Provides convenient access methods and position-based operations.
    """

    _readings: Dict[float, MeasurementReading]

    def __post_init__(self):
        """Validate position measurements on creation"""
        if not self._readings:
            raise ValueError(
                "Position measurements cannot be empty"
            )

    def get_reading(
        self, position: float
    ) -> Optional[MeasurementReading]:
        """Get measurement reading at specific position"""
        return self._readings.get(position)

    def get_force(self, position: float) -> Optional[float]:
        """Get force value at specific position"""
        reading = self.get_reading(position)
        return reading.force if reading else None

    def get_force_value(
        self, position: float
    ) -> Optional[ForceValue]:
        """Get ForceValue object at specific position"""
        reading = self.get_reading(position)
        return reading.force_value if reading else None

    def get_positions(self) -> List[float]:
        """Get all measured positions sorted in ascending order"""
        return sorted(self._readings.keys())

    def get_position_count(self) -> int:
        """Get number of positions measured"""
        return len(self._readings)

    def has_position(self, position: float) -> bool:
        """Check if position was measured"""
        return position in self._readings

    def to_dict(self) -> Dict[float, Dict[str, float]]:
        """Convert to dictionary format for serialization"""
        return {
            position: {"force": reading.force}
            for position, reading in self._readings.items()
        }

    @classmethod
    def from_dict(
        cls, data: Dict[float, Dict[str, float]]
    ) -> "PositionMeasurements":
        """Create from dictionary format"""
        readings = {}
        for position, force_data in data.items():
            readings[position] = (
                MeasurementReading.from_raw_force(
                    force_data["force"]
                )
            )
        return cls(_readings=readings)

    def __str__(self) -> str:
        return f"PositionMeasurements({len(self._readings)} positions)"

    def __repr__(self) -> str:
        return f"PositionMeasurements(_readings={dict(self._readings)})"


@dataclass(frozen=True)
class TestMeasurements:
    """
    Complete test measurements across all temperatures and positions

    Contains the complete measurement matrix for an EOL test.
    Provides high-level operations for accessing and analyzing measurement data.
    """

    _measurements: Dict[float, PositionMeasurements]

    def __post_init__(self):
        """Validate test measurements on creation"""
        if not self._measurements:
            raise ValueError(
                "Test measurements cannot be empty"
            )

    def get_temperature_measurements(
        self, temperature: float
    ) -> Optional[PositionMeasurements]:
        """Get all measurements for a specific temperature"""
        return self._measurements.get(temperature)

    def get_force(
        self, temperature: float, position: float
    ) -> Optional[float]:
        """Get force value at specific temperature and position"""
        temp_measurements = (
            self.get_temperature_measurements(temperature)
        )
        return (
            temp_measurements.get_force(position)
            if temp_measurements
            else None
        )

    def get_force_value(
        self, temperature: float, position: float
    ) -> Optional[ForceValue]:
        """Get ForceValue object at specific temperature and position"""
        temp_measurements = (
            self.get_temperature_measurements(temperature)
        )
        return (
            temp_measurements.get_force_value(position)
            if temp_measurements
            else None
        )

    def get_reading(
        self, temperature: float, position: float
    ) -> Optional[MeasurementReading]:
        """Get measurement reading at specific temperature and position"""
        temp_measurements = (
            self.get_temperature_measurements(temperature)
        )
        return (
            temp_measurements.get_reading(position)
            if temp_measurements
            else None
        )

    def get_temperatures(self) -> List[float]:
        """Get all measured temperatures sorted in ascending order"""
        return sorted(self._measurements.keys())

    def get_temperature_count(self) -> int:
        """Get number of temperatures measured"""
        return len(self._measurements)

    def get_positions_for_temperature(
        self, temperature: float
    ) -> List[float]:
        """Get all positions measured at specific temperature"""
        temp_measurements = (
            self.get_temperature_measurements(temperature)
        )
        return (
            temp_measurements.get_positions()
            if temp_measurements
            else []
        )

    def get_total_measurement_count(self) -> int:
        """Get total number of individual measurements across all temperatures and positions"""
        return sum(
            pos_measurements.get_position_count()
            for pos_measurements in self._measurements.values()
        )

    def get_measurement_matrix(
        self,
    ) -> Dict[Tuple[float, float], float]:
        """
        Get flattened temperature-position-force mapping

        Returns:
            Dictionary with (temperature, position) tuple keys and force values
        """
        result = {}
        for (
            temp,
            pos_measurements,
        ) in self._measurements.items():
            for pos in pos_measurements.get_positions():
                force = pos_measurements.get_force(pos)
                if force is not None:
                    result[(temp, pos)] = force
        return result

    def to_legacy_dict(
        self,
    ) -> Dict[float, Dict[float, Dict[str, float]]]:
        """
        Convert to legacy nested dict format for backward compatibility

        Returns:
            Dictionary in format: {temperature: {position: {"force": value}}}
        """
        result = {}
        for (
            temp,
            pos_measurements,
        ) in self._measurements.items():
            result[temp] = pos_measurements.to_dict()
        return result

    @classmethod
    def from_legacy_dict(
        cls,
        data: Dict[float, Dict[float, Dict[str, float]]],
    ) -> "TestMeasurements":
        """
        Create TestMeasurements from legacy nested dict format

        Args:
            data: Dictionary in format: {temperature: {position: {"force": value}}}

        Returns:
            TestMeasurements instance
        """
        measurements = {}
        for temp, positions_data in data.items():
            measurements[temp] = (
                PositionMeasurements.from_dict(
                    positions_data
                )
            )
        return cls(_measurements=measurements)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for serialization"""
        return {
            "measurements": self.to_legacy_dict(),
            "temperature_count": self.get_temperature_count(),
            "total_measurement_count": self.get_total_measurement_count(),
        }

    def __str__(self) -> str:
        temp_count = self.get_temperature_count()
        total_count = self.get_total_measurement_count()
        return f"TestMeasurements({temp_count} temperatures, {total_count} total measurements)"

    def __repr__(self) -> str:
        return f"TestMeasurements(_measurements={dict(self._measurements)})"

    def __iter__(
        self,
    ) -> Iterator[Tuple[float, PositionMeasurements]]:
        """Allow iteration over temperature-measurements pairs"""
        for temp in self.get_temperatures():
            yield temp, self._measurements[temp]

    def __len__(self) -> int:
        """Return number of temperatures measured"""
        return len(self._measurements)

    def __contains__(self, temperature: float) -> bool:
        """Check if temperature was measured"""
        return temperature in self._measurements
