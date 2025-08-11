"""
Test Configuration Value Object

Immutable configuration object containing all test parameters and settings.
"""

from dataclasses import dataclass, field, replace
from typing import Any, Dict, List

from src.domain.exceptions.validation_exceptions import (
    ValidationException,
)
from src.domain.value_objects.pass_criteria import PassCriteria


@dataclass(frozen=True)
class TestConfiguration:
    """
    Test configuration value object containing all test parameters

    This is an immutable value object that represents test configuration settings.
    Two configurations with same values are considered identical.
    """

    # Power settings
    voltage: float = 18.0
    current: float = 20.0
    upper_current: float = 30.0

    # MCU settings
    upper_temperature: float = 80.0
    activation_temperature: float = 60.0
    standby_temperature: float = 40.0
    fan_speed: int = 10

    # Motion control settings (μm/s, μm/s²)
    velocity: float = 60000.0  # μm/s
    acceleration: float = 60000.0  # μm/s²
    deceleration: float = 60000.0  # μm/s²

    # Positioning settings (μm)
    initial_position: float = 10000.0  # μm (10mm)
    max_stroke: float = 240000.0  # μm (240mm)

    # Test parameters
    temperature_list: List[float] = field(
        default_factory=lambda: [
            38.0,
            40.0,
            42.0,
            44.0,
            46.0,
            48.0,
            50.0,
            52.0,
            54.0,
            56.0,
            58.0,
            60.0,
        ]
    )
    stroke_positions: List[float] = field(
        default_factory=lambda: [
            10000.0,  # 10mm in μm
            60000.0,  # 60mm in μm
            100000.0,  # 100mm in μm
            140000.0,  # 140mm in μm
            180000.0,  # 180mm in μm
            220000.0,  # 220mm in μm
            240000.0,  # 240mm in μm
        ]
    )

    # Timing settings (in seconds)
    stabilization_delay: float = 0.1  # Time to stabilize after hardware power on
    temperature_stabilization: float = 0.1  # Time to stabilize after temperature change
    standby_stabilization: float = 1.0  # Time to stabilize after lma stanby heating
    power_stabilization: float = 0.5  # Time to stabilize after power on
    loadcell_zero_delay: float = 0.1  # Time to zero loadcell after power on

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
    max_velocity: float = 100000.0  # μm/s
    max_acceleration: float = 100000.0  # μm/s²
    max_deceleration: float = 100000.0  # μm/s²

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
            raise ValidationException(
                "voltage",
                self.voltage,
                "Voltage must be positive",
            )

        if self.current <= 0:
            raise ValidationException(
                "current",
                self.current,
                "Current must be positive",
            )

        if self.upper_temperature <= 0:
            raise ValidationException(
                "upper_temperature",
                self.upper_temperature,
                "Upper temperature must be positive",
            )

        if not 0 <= self.fan_speed <= 10:
            raise ValidationException(
                "fan_speed",
                self.fan_speed,
                "Fan speed must be between 0 and 100",
            )

        if self.max_stroke <= 0:
            raise ValidationException(
                "max_stroke",
                self.max_stroke,
                "Max stroke must be positive",
            )

        if self.initial_position < 0:
            raise ValidationException(
                "initial_position",
                self.initial_position,
                "Initial position cannot be negative",
            )

    def _validate_test_parameters(self) -> None:
        """Validate test execution parameters"""
        if not self.temperature_list:
            raise ValidationException(
                "temperature_list",
                self.temperature_list,
                "Temperature list cannot be empty",
            )

        if not self.stroke_positions:
            raise ValidationException(
                "stroke_positions",
                self.stroke_positions,
                "Stroke positions list cannot be empty",
            )

        if any(temp <= 0 for temp in self.temperature_list):
            raise ValidationException(
                "temperature_list",
                self.temperature_list,
                "All temperatures must be positive",
            )

        if any(pos < 0 for pos in self.stroke_positions):
            raise ValidationException(
                "stroke_positions",
                self.stroke_positions,
                "All stroke positions must be non-negative",
            )

    def _validate_safety_limits(self) -> None:
        """Validate safety limit parameters"""
        if self.max_voltage <= self.voltage:
            raise ValidationException(
                "max_voltage",
                self.max_voltage,
                f"Max voltage must be greater than operating voltage ({self.voltage})",
            )

        if self.max_current <= self.current:
            raise ValidationException(
                "max_current",
                self.max_current,
                f"Max current must be greater than operating current ({self.current})",
            )

    def _validate_motion_parameters(self) -> None:
        """Validate motion control parameters"""

        if self.velocity <= 0:
            raise ValidationException(
                "velocity",
                self.velocity,
                "Velocity must be positive",
            )

        if self.acceleration <= 0:
            raise ValidationException(
                "acceleration",
                self.acceleration,
                "Acceleration must be positive",
            )

        if self.deceleration <= 0:
            raise ValidationException(
                "deceleration",
                self.deceleration,
                "Deceleration must be positive",
            )

        if self.max_velocity <= self.velocity:
            raise ValidationException(
                "max_velocity",
                self.max_velocity,
                f"Max velocity must be greater than operating velocity ({self.velocity})",
            )

        if self.max_acceleration <= self.acceleration:
            raise ValidationException(
                "max_acceleration",
                self.max_acceleration,
                f"Max acceleration must be greater than operating acceleration ({self.acceleration})",
            )

        if self.max_deceleration <= self.deceleration:
            raise ValidationException(
                "max_deceleration",
                self.max_deceleration,
                f"Max deceleration must be greater than operating deceleration ({self.deceleration})",
            )

    def _validate_timing_settings(self) -> None:
        """Validate timing configuration parameters"""
        timing_fields = [
            (
                "stabilization_delay",
                self.stabilization_delay,
            ),
            (
                "temperature_stabilization",
                self.temperature_stabilization,
            ),
            (
                "power_stabilization",
                self.power_stabilization,
            ),
            (
                "loadcell_zero_delay",
                self.loadcell_zero_delay,
            ),
            ("timeout_seconds", self.timeout_seconds),
        ]

        for field_name, value in timing_fields:
            if value <= 0:
                raise ValidationException(
                    field_name,
                    value,
                    f"{field_name} must be positive",
                )

        if self.retry_attempts < 0:
            raise ValidationException(
                "retry_attempts",
                self.retry_attempts,
                "Retry attempts cannot be negative",
            )

        if self.measurement_tolerance <= 0:
            raise ValidationException(
                "measurement_tolerance",
                self.measurement_tolerance,
                "Measurement tolerance must be positive",
            )

        if self.force_precision < 0:
            raise ValidationException(
                "force_precision",
                self.force_precision,
                "Force precision cannot be negative",
            )

        if self.temperature_precision < 0:
            raise ValidationException(
                "temperature_precision",
                self.temperature_precision,
                "Temperature precision cannot be negative",
            )

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

        return (
            setup_time + temp_change_time + position_change_time + measurement_time + cleanup_time
        )

    def with_overrides(self, **overrides) -> "TestConfiguration":
        """
        Create new configuration with specific field overrides

        Args:
            **overrides: Field values to override

        Returns:
            New TestConfiguration instance with overridden values

        Raises:
            ValidationException: If overridden values are invalid
        """
        # Handle pass_criteria override specially
        processed_overrides = overrides.copy()
        if "pass_criteria" in processed_overrides and not isinstance(
            processed_overrides["pass_criteria"],
            PassCriteria,
        ):
            processed_overrides["pass_criteria"] = PassCriteria.from_dict(
                processed_overrides["pass_criteria"]
            )

        # Create new instance using dataclasses.replace
        return replace(self, **processed_overrides)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation"""
        return {
            "voltage": self.voltage,
            "current": self.current,
            "upper_temperature": self.upper_temperature,
            "fan_speed": self.fan_speed,
            "max_stroke": self.max_stroke,
            "initial_position": self.initial_position,
            "pass_criteria": self.pass_criteria.to_dict(),
            "temperature_list": self.temperature_list.copy(),
            "stroke_positions": self.stroke_positions.copy(),
            "stabilization_delay": self.stabilization_delay,
            "temperature_stabilization": self.temperature_stabilization,
            "power_stabilization": self.power_stabilization,
            "loadcell_zero_delay": self.loadcell_zero_delay,
            "measurement_tolerance": self.measurement_tolerance,
            "force_precision": self.force_precision,
            "temperature_precision": self.temperature_precision,
            "retry_attempts": self.retry_attempts,
            "timeout_seconds": self.timeout_seconds,
            "max_voltage": self.max_voltage,
            "max_current": self.max_current,
            "velocity": self.velocity,
            "acceleration": self.acceleration,
            "deceleration": self.deceleration,
            "max_velocity": self.max_velocity,
            "max_acceleration": self.max_acceleration,
            "max_deceleration": self.max_deceleration,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestConfiguration":
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
        if "pass_criteria" in data_copy and isinstance(data_copy["pass_criteria"], dict):
            data_copy["pass_criteria"] = PassCriteria.from_dict(data_copy["pass_criteria"])

        return cls(**data_copy)

    @classmethod
    def from_structured_dict(cls, structured_data: Dict[str, Any]) -> "TestConfiguration":
        """
        Create configuration from structured (nested) dictionary format

        This method handles the conversion from hierarchical configuration files
        (YAML/JSON with sections like hardware, timing, etc.) to flat TestConfiguration format.

        Args:
            structured_data: Nested dictionary with configuration sections

        Returns:
            TestConfiguration instance

        Raises:
            ValidationException: If dictionary contains invalid values
        """
        flattened = {}

        # Hardware section
        if "hardware" in structured_data:
            hardware = structured_data["hardware"]
            flattened.update(
                {
                    "voltage": hardware.get("voltage", 18.0),
                    "current": hardware.get("current", 20.0),
                    "upper_current": hardware.get("upper_current", 30.0),
                    "upper_temperature": hardware.get("upper_temperature", 80.0),
                    "activation_temperature": hardware.get("activation_temperature", 60.0),
                    "standby_temperature": hardware.get("standby_temperature", 40.0),
                    "fan_speed": hardware.get("fan_speed", 10),
                    "max_stroke": hardware.get("max_stroke", 240000.0),
                    "initial_position": hardware.get("initial_position", 10000.0),
                }
            )

        # Motion control section
        if "motion_control" in structured_data:
            motion = structured_data["motion_control"]
            flattened.update(
                {
                    "velocity": motion.get("velocity", 60000.0),
                    "acceleration": motion.get("acceleration", 60000.0),
                    "deceleration": motion.get("deceleration", 60000.0),
                }
            )

        # Test parameters section
        if "test_parameters" in structured_data:
            test_params = structured_data["test_parameters"]
            flattened.update(
                {
                    "temperature_list": test_params.get(
                        "temperature_list",
                        [
                            38.0,
                            40.0,
                            42.0,
                            44.0,
                            46.0,
                            48.0,
                            50.0,
                            52.0,
                            54.0,
                            56.0,
                            58.0,
                            60.0,
                        ],
                    ),
                    "stroke_positions": test_params.get(
                        "stroke_positions",
                        [
                            10000.0,
                            60000.0,
                            100000.0,
                            140000.0,
                            180000.0,
                            220000.0,
                            240000.0,
                        ],
                    ),
                }
            )

        # Timing section
        if "timing" in structured_data:
            timing = structured_data["timing"]
            flattened.update(
                {
                    "stabilization_delay": timing.get("stabilization_delay", 0.1),
                    "temperature_stabilization": timing.get("temperature_stabilization", 0.1),
                    "standby_stabilization": timing.get("standby_stabilization", 1.0),
                    "power_stabilization": timing.get("power_stabilization", 0.5),
                    "loadcell_zero_delay": timing.get("loadcell_zero_delay", 0.1),
                }
            )

        # Tolerances section
        if "tolerances" in structured_data:
            tolerances = structured_data["tolerances"]
            flattened.update(
                {
                    "measurement_tolerance": tolerances.get("measurement_tolerance", 0.001),
                    "force_precision": tolerances.get("force_precision", 2),
                    "temperature_precision": tolerances.get("temperature_precision", 1),
                }
            )

        # Execution section
        if "execution" in structured_data:
            execution = structured_data["execution"]
            flattened.update(
                {
                    "retry_attempts": execution.get("retry_attempts", 3),
                    "timeout_seconds": execution.get("timeout_seconds", 60.0),
                }
            )

        # Safety section
        if "safety" in structured_data:
            safety = structured_data["safety"]
            flattened.update(
                {
                    "max_voltage": safety.get("max_voltage", 30.0),
                    "max_current": safety.get("max_current", 30.0),
                    "max_velocity": safety.get("max_velocity", 100000.0),
                    "max_acceleration": safety.get("max_acceleration", 100000.0),
                    "max_deceleration": safety.get("max_deceleration", 100000.0),
                }
            )

        # Pass criteria section
        if "pass_criteria" in structured_data:
            pass_criteria = structured_data["pass_criteria"]

            # Convert spec_points from list format to tuple format
            spec_points = pass_criteria.get("spec_points", [])
            if spec_points:
                # Convert each spec point from list to tuple
                spec_points_tuples = [
                    (tuple(point) if isinstance(point, list) else point) for point in spec_points
                ]
            else:
                spec_points_tuples = []

            # Create pass_criteria dictionary for PassCriteria.from_dict()
            pass_criteria_dict = {
                "force_limit_min": pass_criteria.get("force_limit_min", 0.0),
                "force_limit_max": pass_criteria.get("force_limit_max", 100.0),
                "temperature_limit_min": pass_criteria.get("temperature_limit_min", -10.0),
                "temperature_limit_max": pass_criteria.get("temperature_limit_max", 80.0),
                "spec_points": spec_points_tuples,
                "measurement_tolerance": pass_criteria.get("measurement_tolerance", 0.001),
                "force_precision": pass_criteria.get("force_precision", 2),
                "temperature_precision": pass_criteria.get("temperature_precision", 1),
                "max_test_duration": pass_criteria.get("max_test_duration", 300.0),
                "min_stabilization_time": pass_criteria.get("min_stabilization_time", 0.5),
            }

            flattened["pass_criteria"] = pass_criteria_dict

        # Handle direct top-level parameters (backward compatibility)
        for key, value in structured_data.items():
            if key not in [
                "hardware",
                "motion_control",
                "test_parameters",
                "timing",
                "tolerances",
                "execution",
                "safety",
                "pass_criteria",
                "hardware_config",
                "metadata",
            ]:
                flattened[key] = value

        # Use regular from_dict to create the instance
        return cls.from_dict(flattened)

    def __str__(self) -> str:
        duration = self.estimate_test_duration_seconds()
        points = self.get_total_measurement_points()
        return f"TestConfiguration({self.voltage}V, {self.current}A, {points} points, ~{duration:.0f}s)"

    def __repr__(self) -> str:
        return (
            f"TestConfiguration(voltage={self.voltage}, current={self.current}, "
            f"temperatures={len(self.temperature_list)}, positions={len(self.stroke_positions)})"
        )
