"""
Test Configuration Value Object

Immutable configuration object containing all test parameters and settings.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from domain.exceptions.validation_exceptions import ValidationException
from domain.value_objects.pass_criteria import PassCriteria


@dataclass(frozen=True)
class TestConfiguration:
    """
    Test configuration value object containing all test parameters

    This is an immutable value object that represents test configuration settings.
    Two configurations with same values are considered identical.
    """

    # Hardware power settings
    voltage: float = 18.0
    current: float = 20.0
    upper_temperature: float = 80.0
    fan_speed: int = 10

    # Motion control settings
    axis: int = 0
    velocity: float = 100.0
    acceleration: float = 100.0
    deceleration: float = 100.0

    # Positioning settings
    standby_position: float = 10.0
    max_stroke: float = 240.0
    initial_position: float = 10.0
    position_tolerance: float = 0.1
    homing_velocity: float = 10.0
    homing_acceleration: float = 100.0
    homing_deceleration: float = 100.0

    # Test parameters
    temperature_list: List[float] = field(default_factory=lambda: [38.0, 40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 54.0, 56.0, 58.0, 60.0])
    stroke_positions: List[float] = field(default_factory=lambda: [10.0, 60.0, 100.0, 140.0, 180.0, 220.0, 240.0])

    # Timing settings (in seconds)
    stabilization_delay: float = 0.1
    temperature_stabilization: float = 0.1
    power_stabilization: float = 0.5
    loadcell_zero_delay: float = 0.1

    # Measurement settings
    measurement_tolerance: float = 0.001
    force_precision: int = 2
    temperature_precision: int = 1

    # Test execution settings
    retry_attempts: int = 3
    timeout_seconds: float = 60.0

    # Pass/Fail criteria configuration
    pass_criteria: PassCriteria = field(default_factory=PassCriteria)

    # Safety limits
    max_voltage: float = 30.0
    max_current: float = 30.0
    max_velocity: float = 500.0
    max_acceleration: float = 1000.0
    max_deceleration: float = 1000.0

    def __post_init__(self) -> None:
        """Validate configuration after initialization"""
        self._validate_hardware_settings()
        self._validate_test_parameters()
        self._validate_safety_limits()
        self._validate_motion_parameters()
        self._validate_timing_settings()

    def _validate_hardware_settings(self) -> None:
        """Validate hardware configuration parameters"""
        if self.voltage <= 0:
            raise ValidationException("voltage", self.voltage, "Voltage must be positive")

        if self.current <= 0:
            raise ValidationException("current", self.current, "Current must be positive")

        if self.upper_temperature <= 0:
            raise ValidationException("upper_temperature", self.upper_temperature, "Upper temperature must be positive")

        if not (0 <= self.fan_speed <= 10):
            raise ValidationException("fan_speed", self.fan_speed, "Fan speed must be between 0 and 100")

        if self.max_stroke <= 0:
            raise ValidationException("max_stroke", self.max_stroke, "Max stroke must be positive")

        if self.initial_position < 0:
            raise ValidationException("initial_position", self.initial_position, "Initial position cannot be negative")

    def _validate_test_parameters(self) -> None:
        """Validate test execution parameters"""
        if not self.temperature_list:
            raise ValidationException("temperature_list", self.temperature_list, "Temperature list cannot be empty")

        if not self.stroke_positions:
            raise ValidationException("stroke_positions", self.stroke_positions, "Stroke positions list cannot be empty")

        if any(temp <= 0 for temp in self.temperature_list):
            raise ValidationException("temperature_list", self.temperature_list, "All temperatures must be positive")

        if any(pos < 0 for pos in self.stroke_positions):
            raise ValidationException("stroke_positions", self.stroke_positions, "All stroke positions must be non-negative")

        if self.standby_position < 0:
            raise ValidationException("standby_position", self.standby_position, "Standby position cannot be negative")

    def _validate_safety_limits(self) -> None:
        """Validate safety limit parameters"""
        if self.max_voltage <= self.voltage:
            raise ValidationException("max_voltage", self.max_voltage,
                                    f"Max voltage must be greater than operating voltage ({self.voltage})")

        if self.max_current <= self.current:
            raise ValidationException("max_current", self.max_current,
                                    f"Max current must be greater than operating current ({self.current})")

    def _validate_motion_parameters(self) -> None:
        """Validate motion control parameters"""
        if self.axis < 0:
            raise ValidationException("axis", self.axis, "Axis number cannot be negative")

        if self.velocity <= 0:
            raise ValidationException("velocity", self.velocity, "Velocity must be positive")

        if self.acceleration <= 0:
            raise ValidationException("acceleration", self.acceleration, "Acceleration must be positive")

        if self.deceleration <= 0:
            raise ValidationException("deceleration", self.deceleration, "Deceleration must be positive")

        if self.max_velocity <= self.velocity:
            raise ValidationException("max_velocity", self.max_velocity,
                                    f"Max velocity must be greater than operating velocity ({self.velocity})")

        if self.max_acceleration <= self.acceleration:
            raise ValidationException("max_acceleration", self.max_acceleration,
                                    f"Max acceleration must be greater than operating acceleration ({self.acceleration})")

        if self.max_deceleration <= self.deceleration:
            raise ValidationException("max_deceleration", self.max_deceleration,
                                    f"Max deceleration must be greater than operating deceleration ({self.deceleration})")

        if self.position_tolerance <= 0:
            raise ValidationException("position_tolerance", self.position_tolerance, "Position tolerance must be positive")

        if self.homing_velocity <= 0:
            raise ValidationException("homing_velocity", self.homing_velocity, "Homing velocity must be positive")

        if self.homing_acceleration <= 0:
            raise ValidationException("homing_acceleration", self.homing_acceleration, "Homing acceleration must be positive")

        if self.homing_deceleration <= 0:
            raise ValidationException("homing_deceleration", self.homing_deceleration, "Homing deceleration must be positive")

    def _validate_timing_settings(self) -> None:
        """Validate timing configuration parameters"""
        timing_fields = [
            ("stabilization_delay", self.stabilization_delay),
            ("temperature_stabilization", self.temperature_stabilization),
            ("power_stabilization", self.power_stabilization),
            ("loadcell_zero_delay", self.loadcell_zero_delay),
            ("timeout_seconds", self.timeout_seconds)
        ]

        for field_name, value in timing_fields:
            if value <= 0:
                raise ValidationException(field_name, value, f"{field_name} must be positive")

        if self.retry_attempts < 0:
            raise ValidationException("retry_attempts", self.retry_attempts, "Retry attempts cannot be negative")

        if self.measurement_tolerance <= 0:
            raise ValidationException("measurement_tolerance", self.measurement_tolerance, "Measurement tolerance must be positive")

        if self.force_precision < 0:
            raise ValidationException("force_precision", self.force_precision, "Force precision cannot be negative")

        if self.temperature_precision < 0:
            raise ValidationException("temperature_precision", self.temperature_precision, "Temperature precision cannot be negative")

    def is_valid(self) -> bool:
        """
        Check if configuration is valid

        Returns:
            True if all validation rules pass, False otherwise
        """
        try:
            self.__post_init__()
            return True
        except ValidationException:
            return False

    def get_temperature_count(self) -> int:
        """Get number of temperature test points"""
        return len(self.temperature_list)

    def get_position_count(self) -> int:
        """Get number of stroke position test points"""
        return len(self.stroke_positions)

    def get_total_measurement_points(self) -> int:
        """Get total number of measurement points (temperature × position)"""
        return self.get_temperature_count() * self.get_position_count()

    def estimate_test_duration_seconds(self) -> float:
        """
        Estimate total test duration in seconds

        Returns:
            Estimated duration based on stabilization times and measurement points
        """
        setup_time = 30.0  # Estimated setup time
        cleanup_time = 15.0  # Estimated cleanup time

        # Time per temperature change
        temp_change_time = self.temperature_stabilization * self.get_temperature_count()

        # Time per position change
        position_change_time = self.stabilization_delay * self.get_total_measurement_points()

        # Measurement time (estimated 1 second per measurement)
        measurement_time = self.get_total_measurement_points() * 1.0

        return setup_time + temp_change_time + position_change_time + measurement_time + cleanup_time

    def with_overrides(self, **overrides) -> 'TestConfiguration':
        """
        Create new configuration with specific field overrides

        Args:
            **overrides: Field values to override

        Returns:
            New TestConfiguration instance with overridden values

        Raises:
            ValidationException: If overridden values are invalid
        """
        # Get current values as dict
        current_values = {
            'voltage': self.voltage,
            'current': self.current,
            'upper_temperature': self.upper_temperature,
            'fan_speed': self.fan_speed,
            'max_stroke': self.max_stroke,
            'initial_position': self.initial_position,
            'pass_criteria': self.pass_criteria,
            'temperature_list': self.temperature_list.copy(),
            'stroke_positions': self.stroke_positions.copy(),
            'standby_position': self.standby_position,
            'stabilization_delay': self.stabilization_delay,
            'temperature_stabilization': self.temperature_stabilization,
            'power_stabilization': self.power_stabilization,
            'loadcell_zero_delay': self.loadcell_zero_delay,
            'measurement_tolerance': self.measurement_tolerance,
            'force_precision': self.force_precision,
            'temperature_precision': self.temperature_precision,
            'retry_attempts': self.retry_attempts,
            'timeout_seconds': self.timeout_seconds,
            'max_voltage': self.max_voltage,
            'max_current': self.max_current,
            'axis': self.axis,
            'velocity': self.velocity,
            'acceleration': self.acceleration,
            'deceleration': self.deceleration,
            'max_velocity': self.max_velocity,
            'max_acceleration': self.max_acceleration,
            'max_deceleration': self.max_deceleration,
            'position_tolerance': self.position_tolerance,
            'homing_velocity': self.homing_velocity,
            'homing_acceleration': self.homing_acceleration,
            'homing_deceleration': self.homing_deceleration
        }

        # Apply overrides
        current_values.update(overrides)

        # Handle pass_criteria override specially
        if 'pass_criteria' in overrides and not isinstance(overrides['pass_criteria'], PassCriteria):
            current_values['pass_criteria'] = PassCriteria.from_dict(overrides['pass_criteria'])

        # Create new instance
        return TestConfiguration(**current_values)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation"""
        return {
            'voltage': self.voltage,
            'current': self.current,
            'upper_temperature': self.upper_temperature,
            'fan_speed': self.fan_speed,
            'max_stroke': self.max_stroke,
            'initial_position': self.initial_position,
            'pass_criteria': self.pass_criteria.to_dict(),
            'temperature_list': self.temperature_list.copy(),
            'stroke_positions': self.stroke_positions.copy(),
            'standby_position': self.standby_position,
            'stabilization_delay': self.stabilization_delay,
            'temperature_stabilization': self.temperature_stabilization,
            'power_stabilization': self.power_stabilization,
            'loadcell_zero_delay': self.loadcell_zero_delay,
            'measurement_tolerance': self.measurement_tolerance,
            'force_precision': self.force_precision,
            'temperature_precision': self.temperature_precision,
            'retry_attempts': self.retry_attempts,
            'timeout_seconds': self.timeout_seconds,
            'max_voltage': self.max_voltage,
            'max_current': self.max_current,
            'axis': self.axis,
            'velocity': self.velocity,
            'acceleration': self.acceleration,
            'deceleration': self.deceleration,
            'max_velocity': self.max_velocity,
            'max_acceleration': self.max_acceleration,
            'max_deceleration': self.max_deceleration,
            'position_tolerance': self.position_tolerance,
            'homing_velocity': self.homing_velocity,
            'homing_acceleration': self.homing_acceleration,
            'homing_deceleration': self.homing_deceleration
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestConfiguration':
        """
        Create configuration from dictionary

        Args:
            data: Dictionary containing configuration values

        Returns:
            TestConfiguration instance

        Raises:
            ValidationException: If dictionary contains invalid values
        """
        # Create a copy if we need to modify nested objects
        data_copy = data.copy()

        # Handle pass_criteria field specially
        if 'pass_criteria' in data_copy and isinstance(data_copy['pass_criteria'], dict):
            data_copy['pass_criteria'] = PassCriteria.from_dict(data_copy['pass_criteria'])

        return cls(**data_copy)

    def __str__(self) -> str:
        duration = self.estimate_test_duration_seconds()
        points = self.get_total_measurement_points()
        return f"TestConfiguration({self.voltage}V, {self.current}A, {points} points, ~{duration:.0f}s)"

    def __repr__(self) -> str:
        return (f"TestConfiguration(voltage={self.voltage}, current={self.current}, "
                f"temperatures={len(self.temperature_list)}, positions={len(self.stroke_positions)})")
