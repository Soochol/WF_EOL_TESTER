"""
Test Configuration Value Object

Immutable configuration object containing all test parameters and settings.
This value object defines the complete test execution configuration including
hardware settings, motion parameters, timing, and validation criteria.
"""

# Standard library imports
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List

# Local application imports
from domain.exceptions.validation_exceptions import (
    ValidationException,
)
from domain.value_objects.pass_criteria import PassCriteria


@dataclass(frozen=True)
class TestConfiguration:
    """
    Test configuration value object containing all test parameters

    This immutable value object represents complete test execution configuration.
    It includes hardware settings, motion parameters, timing configurations,
    test points, and validation criteria. Two configurations with identical
    values are considered equal.

    All measurements use consistent units:
    - Distances: micrometers (μm)
    - Velocities: micrometers per second (μm/s)
    - Accelerations: micrometers per second squared (μm/s²)
    - Times: seconds (s)
    - Temperatures: degrees Celsius (°C)
    - Forces: Newtons (N)
    - Electrical: Volts (V), Amperes (A)
    """

    # ========================================================================
    # POWER SUPPLY SETTINGS
    # ========================================================================
    voltage: float = 18.0  # Operating voltage (V)
    current: float = 20.0  # Operating current (A)
    upper_current: float = 30.0  # Maximum current limit (A)

    # ========================================================================
    # MCU/TEMPERATURE CONTROLLER SETTINGS
    # ========================================================================
    upper_temperature: float = 80.0  # Maximum temperature limit (°C)
    activation_temperature: float = 52.0  # Temperature activation threshold (°C)
    standby_temperature: float = 38.0  # Standby temperature setting (°C)
    fan_speed: int = 10  # Fan speed setting (0-10)

    # ========================================================================
    # MOTION CONTROL SETTINGS
    # ========================================================================
    velocity: float = 100000.0  # Operating velocity (μm/s)
    acceleration: float = 60000.0  # Operating acceleration (μm/s²)
    deceleration: float = 60000.0  # Operating deceleration (μm/s²)

    # ========================================================================
    # POSITIONING SETTINGS
    # ========================================================================
    initial_position: float = 1000.0  # Starting position (μm)
    max_stroke: float = 220000.0  # Maximum stroke length (μm)

    # ========================================================================
    # TEST PARAMETERS
    # ========================================================================
    temperature_list: List[float] = field(
        default_factory=lambda: [
            38.0,  # Low temperature test point (°C)
            52.0,  # Medium temperature test point (°C)
            66.0,  # High temperature test point (°C)
        ]
    )
    stroke_positions: List[float] = field(
        default_factory=lambda: [
            10000.0,  # 10mm position (μm)
            60000.0,  # 60mm position (μm)
            120000.0,  # 120mm position (μm)
            180000.0,  # 180mm position (μm)
            220000.0,  # 220mm position (μm)
        ]
    )

    # ========================================================================
    # TIMING/STABILIZATION SETTINGS
    # ========================================================================
    robot_move_stabilization: float = 0.1  # Post-movement stabilization time (s)
    robot_standby_stabilization: float = 1.0  # Standby heating stabilization time (s)
    mcu_temperature_stabilization: float = 0.1  # Temperature change stabilization time (s)
    mcu_command_stabilization: float = 0.1  # MCU command stabilization time (s)
    mcu_boot_complete_stabilization: float = 2.0  # MCU boot complete stabilization time (s)
    poweron_stabilization: float = 0.5  # Power-on stabilization time (s)
    power_command_stabilization: float = 0.2  # Power command stabilization time (s)
    loadcell_zero_delay: float = 0.1  # Load cell zeroing delay (s)

    # ========================================================================
    # MEASUREMENT SETTINGS
    # ========================================================================
    measurement_tolerance: float = 0.001  # Measurement precision tolerance
    force_precision: int = 2  # Force measurement decimal places
    temperature_precision: int = 1  # Temperature measurement decimal places
    temperature_tolerance: float = 3.0  # Temperature verification tolerance (±°C)

    # ========================================================================
    # TEST EXECUTION SETTINGS
    # ========================================================================
    retry_attempts: int = 3  # Number of retry attempts on failure
    timeout_seconds: float = 60.0  # Test operation timeout (s)
    repeat_count: int = 1  # Number of times to repeat the entire test sequence

    # ========================================================================
    # PASS/FAIL CRITERIA
    # ========================================================================
    pass_criteria: PassCriteria = field(default_factory=PassCriteria)

    # ========================================================================
    # SAFETY LIMITS
    # ========================================================================
    max_voltage: float = 30.0  # Maximum allowed voltage (V)
    max_current: float = 30.0  # Maximum allowed current (A)
    max_velocity: float = 100000.0  # Maximum allowed velocity (μm/s)
    max_acceleration: float = 100000.0  # Maximum allowed acceleration (μm/s²)
    max_deceleration: float = 100000.0  # Maximum allowed deceleration (μm/s²)

    def __post_init__(self) -> None:
        """Validate configuration after initialization

        Performs comprehensive validation of all configuration parameters
        to ensure they are within valid ranges and logically consistent.

        Raises:
            ValidationException: If any parameter is invalid
        """
        self._validate_power_settings()
        self._validate_mcu_settings()
        self._validate_motion_parameters()
        self._validate_positioning_settings()
        self._validate_test_parameters()
        self._validate_timing_settings()
        self._validate_measurement_settings()
        self._validate_safety_limits()

    def _validate_power_settings(self) -> None:
        """Validate power supply configuration parameters"""
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

        if self.upper_current <= 0:
            raise ValidationException(
                "upper_current",
                self.upper_current,
                "Upper current limit must be positive",
            )

        if self.upper_current <= self.current:
            raise ValidationException(
                "upper_current",
                self.upper_current,
                f"Upper current limit must be greater than operating current ({self.current}A)",
            )

    def _validate_mcu_settings(self) -> None:
        """Validate MCU/temperature controller configuration parameters"""
        if self.upper_temperature <= 0:
            raise ValidationException(
                "upper_temperature",
                self.upper_temperature,
                "Upper temperature must be positive",
            )

        if self.activation_temperature <= 0:
            raise ValidationException(
                "activation_temperature",
                self.activation_temperature,
                "Activation temperature must be positive",
            )

        if self.standby_temperature <= 0:
            raise ValidationException(
                "standby_temperature",
                self.standby_temperature,
                "Standby temperature must be positive",
            )

        if not 0 <= self.fan_speed <= 10:
            raise ValidationException(
                "fan_speed",
                self.fan_speed,
                "Fan speed must be between 0 and 10",
            )

        # Logical temperature relationships
        if self.activation_temperature > self.upper_temperature:
            raise ValidationException(
                "activation_temperature",
                self.activation_temperature,
                f"Activation temperature must be less than or equal to upper temperature ({self.upper_temperature}°C)",
            )

        if self.standby_temperature >= self.activation_temperature:
            raise ValidationException(
                "standby_temperature",
                self.standby_temperature,
                f"Standby temperature must be less than activation temperature ({self.activation_temperature}°C)",
            )

    def _validate_positioning_settings(self) -> None:
        """Validate positioning configuration parameters"""
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

        if self.initial_position >= self.max_stroke:
            raise ValidationException(
                "initial_position",
                self.initial_position,
                f"Initial position must be less than max stroke ({self.max_stroke}μm)",
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

        # Validate stroke positions are within max_stroke
        invalid_positions = [pos for pos in self.stroke_positions if pos > self.max_stroke]
        if invalid_positions:
            raise ValidationException(
                "stroke_positions",
                invalid_positions,
                f"All stroke positions must be within max stroke ({self.max_stroke}μm)",
            )

        # Validate temperature test points are reasonable
        if any(temp < -50 or temp > 150 for temp in self.temperature_list):
            raise ValidationException(
                "temperature_list",
                self.temperature_list,
                "Temperature test points should be between -50°C and 150°C",
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

        if self.max_velocity < self.velocity:
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
        """Validate timing/stabilization configuration parameters"""
        timing_fields = [
            ("robot_move_stabilization", self.robot_move_stabilization),
            ("robot_standby_stabilization", self.robot_standby_stabilization),
            ("mcu_temperature_stabilization", self.mcu_temperature_stabilization),
            ("mcu_command_stabilization", self.mcu_command_stabilization),
            ("poweron_stabilization", self.poweron_stabilization),
            ("power_command_stabilization", self.power_command_stabilization),
            ("loadcell_zero_delay", self.loadcell_zero_delay),
            ("timeout_seconds", self.timeout_seconds),
        ]

        for field_name, value in timing_fields:
            if value <= 0:
                raise ValidationException(
                    field_name,
                    value,
                    f"{field_name} must be positive",
                )

        # Validate reasonable timing ranges
        if self.timeout_seconds > 3600:  # 1 hour
            raise ValidationException(
                "timeout_seconds",
                self.timeout_seconds,
                "Timeout should not exceed 1 hour (3600 seconds)",
            )

        if self.retry_attempts < 0:
            raise ValidationException(
                "retry_attempts",
                self.retry_attempts,
                "Retry attempts cannot be negative",
            )

        if self.retry_attempts > 10:
            raise ValidationException(
                "retry_attempts",
                self.retry_attempts,
                "Retry attempts should not exceed 10",
            )

        if self.repeat_count < 1:
            raise ValidationException(
                "repeat_count",
                self.repeat_count,
                "Repeat count must be at least 1",
            )

        if self.repeat_count > 100:
            raise ValidationException(
                "repeat_count",
                self.repeat_count,
                "Repeat count should not exceed 100 for safety and practical reasons",
            )

    def _validate_measurement_settings(self) -> None:
        """Validate measurement precision and tolerance parameters"""
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

        if self.force_precision > 10:
            raise ValidationException(
                "force_precision",
                self.force_precision,
                "Force precision should not exceed 10 decimal places",
            )

        if self.temperature_precision > 5:
            raise ValidationException(
                "temperature_precision",
                self.temperature_precision,
                "Temperature precision should not exceed 5 decimal places",
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
        """Get number of temperature test points

        Returns:
            Number of temperature points in the test sequence
        """
        return len(self.temperature_list)

    def get_position_count(self) -> int:
        """Get number of stroke position test points

        Returns:
            Number of position points in the test sequence
        """
        return len(self.stroke_positions)

    def get_total_measurement_points(self) -> int:
        """Get total number of measurement points (temperature × position)

        Returns:
            Total measurement points in the complete test matrix
        """
        return self.get_temperature_count() * self.get_position_count()

    def estimate_test_duration_seconds(self) -> float:
        """
        Estimate total test duration in seconds

        Calculates expected test duration based on:
        - Setup and cleanup time
        - Temperature stabilization time
        - Robot movement time
        - Measurement acquisition time

        Returns:
            Estimated total test duration in seconds
        """
        # Fixed overhead times
        setup_time = 30.0  # Initial hardware setup
        cleanup_time = 15.0  # Final cleanup and shutdown

        # Temperature-related timing
        temp_change_time = self.mcu_temperature_stabilization * self.get_temperature_count()
        temp_command_time = self.mcu_command_stabilization * self.get_temperature_count()

        # Movement-related timing
        position_change_time = self.robot_move_stabilization * self.get_total_measurement_points()

        # Power and setup timing
        power_setup_time = self.poweron_stabilization + self.loadcell_zero_delay

        # Measurement acquisition time (estimated 1 second per measurement)
        measurement_time = self.get_total_measurement_points() * 1.0

        single_test_duration = (
            setup_time
            + cleanup_time
            + power_setup_time
            + temp_change_time
            + temp_command_time
            + position_change_time
            + measurement_time
        )

        # For repeated tests, add setup/cleanup overhead between repetitions
        if self.repeat_count > 1:
            repetition_overhead = 10.0  # Additional time between repetitions (hardware reset, etc.)
            total_duration = single_test_duration * self.repeat_count + repetition_overhead * (
                self.repeat_count - 1
            )
        else:
            total_duration = single_test_duration

        return total_duration

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

    def get_safety_violations(self) -> List[str]:
        """Check for any safety limit violations

        Returns:
            List of safety violation messages, empty if no violations
        """
        violations = []

        if self.voltage > self.max_voltage:
            violations.append(f"Voltage {self.voltage}V exceeds safety limit {self.max_voltage}V")

        if self.current > self.max_current:
            violations.append(f"Current {self.current}A exceeds safety limit {self.max_current}A")

        if self.velocity > self.max_velocity:
            violations.append(
                f"Velocity {self.velocity}μm/s exceeds safety limit {self.max_velocity}μm/s"
            )

        if self.acceleration > self.max_acceleration:
            violations.append(
                f"Acceleration {self.acceleration}μm/s² exceeds safety limit {self.max_acceleration}μm/s²"
            )

        if self.deceleration > self.max_deceleration:
            violations.append(
                f"Deceleration {self.deceleration}μm/s² exceeds safety limit {self.max_deceleration}μm/s²"
            )

        return violations

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation"""
        return {
            # Power settings
            "voltage": self.voltage,
            "current": self.current,
            "upper_current": self.upper_current,  # Missing field added!
            # MCU settings
            "upper_temperature": self.upper_temperature,
            "activation_temperature": self.activation_temperature,  # Missing field added!
            "standby_temperature": self.standby_temperature,  # Missing field added!
            "fan_speed": self.fan_speed,
            # Positioning settings
            "max_stroke": self.max_stroke,
            "initial_position": self.initial_position,
            # Test parameters
            "pass_criteria": self.pass_criteria.to_dict(),
            "temperature_list": self.temperature_list.copy(),
            "stroke_positions": self.stroke_positions.copy(),
            # Timing settings
            "robot_move_stabilization": self.robot_move_stabilization,
            "mcu_temperature_stabilization": self.mcu_temperature_stabilization,
            "robot_standby_stabilization": (
                self.robot_standby_stabilization
            ),  # CRITICAL missing field added!
            "poweron_stabilization": self.poweron_stabilization,
            "power_command_stabilization": self.power_command_stabilization,
            "loadcell_zero_delay": self.loadcell_zero_delay,
            "mcu_command_stabilization": self.mcu_command_stabilization,
            "mcu_boot_complete_stabilization": self.mcu_boot_complete_stabilization,
            # Measurement settings
            "measurement_tolerance": self.measurement_tolerance,
            "force_precision": self.force_precision,
            "temperature_precision": self.temperature_precision,
            "temperature_tolerance": self.temperature_tolerance,
            # Test execution settings
            "retry_attempts": self.retry_attempts,
            "timeout_seconds": self.timeout_seconds,
            "repeat_count": self.repeat_count,
            # Safety limits
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

    def to_structured_dict(self) -> Dict[str, Any]:
        """Convert configuration to structured (nested) dictionary representation for better YAML readability"""
        return {
            # Hardware section
            "hardware": {
                "voltage": self.voltage,
                "current": self.current,
                "upper_current": self.upper_current,
                "upper_temperature": self.upper_temperature,
                "activation_temperature": self.activation_temperature,
                "standby_temperature": self.standby_temperature,
                "fan_speed": self.fan_speed,
                "max_stroke": self.max_stroke,
                "initial_position": self.initial_position,
            },
            # Motion control section
            "motion_control": {
                "velocity": self.velocity,
                "acceleration": self.acceleration,
                "deceleration": self.deceleration,
            },
            # Timing section
            "timing": {
                "robot_move_stabilization": self.robot_move_stabilization,
                "mcu_temperature_stabilization": self.mcu_temperature_stabilization,
                "robot_standby_stabilization": self.robot_standby_stabilization,
                "poweron_stabilization": self.poweron_stabilization,
                "power_command_stabilization": self.power_command_stabilization,
                "loadcell_zero_delay": self.loadcell_zero_delay,
                "mcu_command_stabilization": self.mcu_command_stabilization,
                "mcu_boot_complete_stabilization": self.mcu_boot_complete_stabilization,
            },
            # Test parameters section
            "test_parameters": {
                "temperature_list": self.temperature_list.copy(),
                "stroke_positions": self.stroke_positions.copy(),
            },
            # Safety section
            "safety": {
                "max_voltage": self.max_voltage,
                "max_current": self.max_current,
                "max_velocity": self.max_velocity,
                "max_acceleration": self.max_acceleration,
                "max_deceleration": self.max_deceleration,
            },
            # Execution section
            "execution": {
                "retry_attempts": self.retry_attempts,
                "timeout_seconds": self.timeout_seconds,
                "repeat_count": self.repeat_count,
            },
            # Tolerances section
            "tolerances": {
                "measurement_tolerance": self.measurement_tolerance,
                "force_precision": self.force_precision,
                "temperature_precision": self.temperature_precision,
                "temperature_tolerance": self.temperature_tolerance,
            },
            # Pass criteria (keep as nested object)
            "pass_criteria": self.pass_criteria.to_dict(),
        }

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
                    "robot_move_stabilization": timing.get("robot_move_stabilization", 0.1),
                    "mcu_temperature_stabilization": timing.get(
                        "mcu_temperature_stabilization", 0.1
                    ),
                    "robot_standby_stabilization": timing.get("robot_standby_stabilization", 1.0),
                    "poweron_stabilization": timing.get("poweron_stabilization", 0.5),
                    "power_command_stabilization": timing.get("power_command_stabilization", 0.2),
                    "loadcell_zero_delay": timing.get("loadcell_zero_delay", 0.1),
                    "mcu_command_stabilization": timing.get("mcu_command_stabilization", 0.1),
                    "mcu_boot_complete_stabilization": timing.get(
                        "mcu_boot_complete_stabilization", 2.0
                    ),
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
                    "temperature_tolerance": tolerances.get("temperature_tolerance", 3.0),
                }
            )

        # Execution section
        if "execution" in structured_data:
            execution = structured_data["execution"]
            flattened.update(
                {
                    "retry_attempts": execution.get("retry_attempts", 3),
                    "timeout_seconds": execution.get("timeout_seconds", 60.0),
                    "repeat_count": execution.get("repeat_count", 1),
                }
            )

        # Safety section
        if "safety" in structured_data:
            safety = structured_data["safety"]
            flattened.update(
                {
                    "max_voltage": safety.get("max_voltage", 30.0),
                    "max_current": safety.get("max_current", 30.0),
                    "max_velocity": safety.get("max_velocity", 60000.0),
                    "max_acceleration": safety.get("max_acceleration", 60000.0),
                    "max_deceleration": safety.get("max_deceleration", 60000.0),
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
        """Human-readable string representation"""
        duration = self.estimate_test_duration_seconds()
        points = self.get_total_measurement_points()
        mode = "SAFE" if not self.get_safety_violations() else "UNSAFE"
        repeat_info = f"{self.repeat_count}x" if self.repeat_count > 1 else ""
        return f"TestConfiguration({self.voltage}V, {self.current}A, {points} points, {repeat_info}~{duration:.0f}s, {mode})"

    def __repr__(self) -> str:
        """Debug representation"""
        return (
            f"TestConfiguration(voltage={self.voltage}, current={self.current}, "
            f"temperatures={len(self.temperature_list)}, positions={len(self.stroke_positions)}, "
            f"max_stroke={self.max_stroke}, pass_criteria={self.pass_criteria!r})"
        )
