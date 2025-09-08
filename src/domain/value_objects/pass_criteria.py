"""
Pass Criteria Value Object

Immutable value object containing test pass/fail criteria and validation logic.
Defines acceptable ranges for measurements and provides interpolation capabilities
for 2D specification matrices based on temperature and stroke position.
"""

# Standard library imports
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

# Third-party imports
import numpy as np
from scipy.interpolate import griddata

# Local application imports
from domain.exceptions.validation_exceptions import ValidationException


@dataclass(frozen=True)
class PassCriteria:
    """
    Test pass/fail criteria value object

    Immutable value object that defines acceptable measurement ranges and validation
    criteria for test results. Supports both global limits and 2D specification
    matrices with interpolation capabilities.

    The spec_points field defines a 2D specification matrix where each point
    contains (temperature, stroke_position, upper_limit, lower_limit) tuples.
    Force limits at arbitrary points are calculated using 2D linear interpolation.
    """

    # ========================================================================
    # FORCE MEASUREMENT CRITERIA
    # ========================================================================
    force_limit_min: float = 0.0  # Minimum acceptable force (N)
    force_limit_max: float = 100.0  # Maximum acceptable force (N)

    # ========================================================================
    # TEMPERATURE CRITERIA
    # ========================================================================
    temperature_limit_min: float = -10.0  # Minimum acceptable temperature (°C)
    temperature_limit_max: float = 80.0  # Maximum acceptable temperature (°C)

    # ========================================================================
    # MEASUREMENT PRECISION AND TOLERANCE
    # ========================================================================
    measurement_tolerance: float = 0.001  # General measurement precision tolerance
    force_precision: int = 2  # Force value decimal places
    temperature_precision: int = 1  # Temperature value decimal places

    # ========================================================================
    # POSITION CRITERIA
    # ========================================================================
    position_tolerance: float = 0.5  # Position accuracy tolerance (mm)

    # ========================================================================
    # TIMING CRITERIA
    # ========================================================================
    max_test_duration: float = 300.0  # Maximum allowed test duration (s)
    min_stabilization_time: float = 0.5  # Minimum stabilization time (s)

    # ========================================================================
    # 2D SPECIFICATION MATRIX
    # ========================================================================
    # Each tuple: (temperature°C, stroke_mm, upper_limit_N, lower_limit_N)
    spec_points: List[Tuple[float, float, float, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate pass criteria after initialization

        Performs comprehensive validation of all criteria parameters
        to ensure they are within valid ranges and logically consistent.

        Raises:
            ValidationException: If any parameter is invalid
        """
        self._validate_force_limits()
        self._validate_temperature_limits()
        self._validate_measurement_settings()
        self._validate_position_criteria()
        self._validate_timing_criteria()
        self._validate_spec_points()

    def _validate_force_limits(self) -> None:
        """Validate force limit ranges"""
        if self.force_limit_min >= self.force_limit_max:
            raise ValidationException(
                "force_limit_min",
                self.force_limit_min,
                f"Force min ({self.force_limit_min}) must be less than max ({self.force_limit_max})",
            )

        if self.force_limit_min < 0:
            raise ValidationException(
                "force_limit_min",
                self.force_limit_min,
                "Force minimum cannot be negative",
            )

    def _validate_temperature_limits(self) -> None:
        """Validate temperature limit ranges"""
        if self.temperature_limit_min >= self.temperature_limit_max:
            raise ValidationException(
                "temperature_limit_min",
                self.temperature_limit_min,
                f"Temperature min ({self.temperature_limit_min}) must be less than max ({self.temperature_limit_max})",
            )

    def _validate_measurement_settings(self) -> None:
        """Validate measurement precision and tolerance settings"""
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

    def _validate_position_criteria(self) -> None:
        """Validate position tolerance settings"""
        if self.position_tolerance <= 0:
            raise ValidationException(
                "position_tolerance",
                self.position_tolerance,
                "Position tolerance must be positive",
            )

        if self.position_tolerance > 100:  # 100mm seems excessive
            raise ValidationException(
                "position_tolerance",
                self.position_tolerance,
                "Position tolerance should not exceed 100mm",
            )

    def _validate_timing_criteria(self) -> None:
        """Validate timing-related criteria"""
        if self.max_test_duration <= 0:
            raise ValidationException(
                "max_test_duration",
                self.max_test_duration,
                "Maximum test duration must be positive",
            )

        if self.max_test_duration > 3600:  # 1 hour
            raise ValidationException(
                "max_test_duration",
                self.max_test_duration,
                "Maximum test duration should not exceed 1 hour (3600 seconds)",
            )

        if self.min_stabilization_time < 0:
            raise ValidationException(
                "min_stabilization_time",
                self.min_stabilization_time,
                "Minimum stabilization time cannot be negative",
            )

        if self.min_stabilization_time > 60:  # 1 minute
            raise ValidationException(
                "min_stabilization_time",
                self.min_stabilization_time,
                "Minimum stabilization time should not exceed 60 seconds",
            )

    def _validate_spec_points(self) -> None:
        """Validate 2D specification matrix points"""
        if not self.spec_points:
            return  # Empty spec points is allowed (uses global limits)

        for i, point in enumerate(self.spec_points):
            if len(point) != 4:
                raise ValidationException(
                    f"spec_points[{i}]",
                    point,
                    "Each spec point must have 4 values: (temperature, stroke, upper_limit, lower_limit)",
                )

            temp, stroke, upper_limit, lower_limit = point

            # Validate temperature range
            if temp < -100 or temp > 200:
                raise ValidationException(
                    f"spec_points[{i}].temperature",
                    temp,
                    "Temperature should be between -100°C and 200°C",
                )

            # Validate stroke position
            if stroke < 0:
                raise ValidationException(
                    f"spec_points[{i}].stroke",
                    stroke,
                    "Stroke position cannot be negative",
                )

            # Validate force limits relationship
            if lower_limit >= upper_limit:
                raise ValidationException(
                    f"spec_points[{i}].limits",
                    (lower_limit, upper_limit),
                    f"Lower limit ({lower_limit}) must be less than upper limit ({upper_limit})",
                )

            # Validate force limits are reasonable
            if lower_limit < 0:
                raise ValidationException(
                    f"spec_points[{i}].lower_limit",
                    lower_limit,
                    "Force lower limit cannot be negative",
                )

    def is_force_within_limits(
        self, force: float, temperature: Optional[float] = None, stroke: Optional[float] = None
    ) -> bool:
        """Check if force measurement is within acceptable limits

        Args:
            force: Force measurement value (N)
            temperature: Temperature at measurement point (°C), used for 2D interpolation
            stroke: Stroke position at measurement point (mm), used for 2D interpolation

        Returns:
            True if force is within acceptable limits
        """
        if temperature is not None and stroke is not None and self.spec_points:
            # Use 2D interpolated limits
            lower_limit, upper_limit = self.get_force_limits_at_point(temperature, stroke)
            return lower_limit <= force <= upper_limit
        else:
            # Use global limits
            return self.force_limit_min <= force <= self.force_limit_max

    def is_temperature_within_limits(self, temperature: float) -> bool:
        """Check if temperature is within acceptable limits

        Args:
            temperature: Temperature measurement value (°C)

        Returns:
            True if temperature is within acceptable limits
        """
        return self.temperature_limit_min <= temperature <= self.temperature_limit_max

    def is_position_within_tolerance(self, expected: float, actual: float) -> bool:
        """Check if position is within tolerance of expected value

        Args:
            expected: Expected position value (mm)
            actual: Actual measured position value (mm)

        Returns:
            True if actual position is within tolerance of expected
        """
        return abs(expected - actual) <= self.position_tolerance

    def is_measurement_stable(
        self, measurements: List[float], tolerance_factor: float = 1.0
    ) -> bool:
        """Check if measurements are stable within tolerance

        Args:
            measurements: List of measurement values
            tolerance_factor: Multiplier for measurement tolerance (default 1.0)

        Returns:
            True if all measurements are within tolerance of the average
        """
        if len(measurements) < 2:
            return True

        tolerance = self.measurement_tolerance * tolerance_factor
        avg = sum(measurements) / len(measurements)

        return all(abs(m - avg) <= tolerance for m in measurements)

    def get_force_range(self) -> Tuple[float, float]:
        """Get global force limit range as tuple

        Returns:
            Tuple of (min_force, max_force) in Newtons
        """
        return (self.force_limit_min, self.force_limit_max)

    def get_temperature_range(self) -> Tuple[float, float]:
        """Get temperature limit range as tuple

        Returns:
            Tuple of (min_temperature, max_temperature) in degrees Celsius
        """
        return (self.temperature_limit_min, self.temperature_limit_max)

    def get_force_limits_at_point(self, temperature: float, stroke: float) -> Tuple[float, float]:
        """
        Get force limits at specific temperature and stroke using 2D linear interpolation

        Args:
            temperature: Temperature value (°C)
            stroke: Stroke position value (mm)

        Returns:
            Tuple of (lower_limit, upper_limit) for force at the given point

        Raises:
            ValueError: If spec_points is empty or interpolation fails
        """
        if not self.spec_points:
            # Fallback to global limits if no spec points defined
            return (
                self.force_limit_min,
                self.force_limit_max,
            )

        if len(self.spec_points) == 1:
            # Single point - return its limits
            _, _, upper_limit, lower_limit = self.spec_points[0]
            return (lower_limit, upper_limit)

        try:
            # Extract coordinates and values from spec points
            points = np.array([(temp, stroke_pos) for temp, stroke_pos, _, _ in self.spec_points])
            upper_values = np.array([upper for _, _, upper, _ in self.spec_points])
            lower_values = np.array([lower for _, _, _, lower in self.spec_points])

            # Target point for interpolation
            target_point = np.array([[temperature, stroke]])

            # Perform 2D linear interpolation
            upper_limit = griddata(
                points,
                upper_values,
                target_point,
                method="linear",
                fill_value=np.nan,
            )[0]
            lower_limit = griddata(
                points,
                lower_values,
                target_point,
                method="linear",
                fill_value=np.nan,
            )[0]

            # Handle extrapolation cases (outside spec point range)
            if np.isnan(upper_limit) or np.isnan(lower_limit):
                # Use nearest neighbor for extrapolation
                upper_limit = griddata(
                    points,
                    upper_values,
                    target_point,
                    method="nearest",
                )[0]
                lower_limit = griddata(
                    points,
                    lower_values,
                    target_point,
                    method="nearest",
                )[0]

            return (float(lower_limit), float(upper_limit))

        except Exception:
            # Fallback to global limits on interpolation failure
            return (
                self.force_limit_min,
                self.force_limit_max,
            )

    def format_force(self, force: float) -> str:
        """Format force value according to precision setting

        Args:
            force: Force value to format (N)

        Returns:
            Formatted force string with appropriate decimal places
        """
        return f"{force:.{self.force_precision}f}"

    def format_temperature(self, temperature: float) -> str:
        """Format temperature value according to precision setting

        Args:
            temperature: Temperature value to format (°C)

        Returns:
            Formatted temperature string with appropriate decimal places
        """
        return f"{temperature:.{self.temperature_precision}f}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation

        Returns:
            Dictionary containing all pass criteria parameters
        """
        return {
            "force_limit_min": self.force_limit_min,
            "force_limit_max": self.force_limit_max,
            "temperature_limit_min": self.temperature_limit_min,
            "temperature_limit_max": self.temperature_limit_max,
            "measurement_tolerance": self.measurement_tolerance,
            "force_precision": self.force_precision,
            "temperature_precision": self.temperature_precision,
            "position_tolerance": self.position_tolerance,
            "max_test_duration": self.max_test_duration,
            "min_stabilization_time": self.min_stabilization_time,
            "spec_points": [list(point) for point in self.spec_points],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PassCriteria":
        """Create PassCriteria from dictionary

        Args:
            data: Dictionary containing pass criteria parameters

        Returns:
            PassCriteria instance with validated parameters

        Raises:
            ValidationException: If any parameters are invalid
        """
        # Convert spec_points from list format back to tuples
        spec_points = []
        if "spec_points" in data and data["spec_points"]:
            spec_points = [tuple(point) for point in data["spec_points"]]

        return cls(
            force_limit_min=data.get("force_limit_min", 0.0),
            force_limit_max=data.get("force_limit_max", 100.0),
            temperature_limit_min=data.get("temperature_limit_min", -10.0),
            temperature_limit_max=data.get("temperature_limit_max", 80.0),
            measurement_tolerance=data.get("measurement_tolerance", 0.001),
            force_precision=data.get("force_precision", 2),
            temperature_precision=data.get("temperature_precision", 1),
            position_tolerance=data.get("position_tolerance", 0.5),
            max_test_duration=data.get("max_test_duration", 300.0),
            min_stabilization_time=data.get("min_stabilization_time", 0.5),
            spec_points=spec_points,
        )

    @classmethod
    def default(cls) -> "PassCriteria":
        """Create default pass criteria with conservative settings

        Returns:
            PassCriteria instance with default values suitable for most tests
        """
        return cls()

    def is_valid(self) -> bool:
        """Check if pass criteria configuration is valid

        Returns:
            True if all validation rules pass, False otherwise
        """
        try:
            self.__post_init__()
            return True
        except ValidationException:
            return False

    def get_spec_point_count(self) -> int:
        """Get number of specification points in 2D matrix

        Returns:
            Number of spec points defined
        """
        return len(self.spec_points)

    def has_2d_specification(self) -> bool:
        """Check if 2D specification matrix is defined

        Returns:
            True if spec points are available for interpolation
        """
        return len(self.spec_points) > 0

    def get_measurement_summary(self) -> Dict[str, Union[str, int, float]]:
        """Get summary of measurement criteria

        Returns:
            Dictionary with formatted measurement criteria information
        """
        return {
            "force_range": f"{self.force_limit_min}-{self.force_limit_max}N",
            "temperature_range": f"{self.temperature_limit_min}-{self.temperature_limit_max}°C",
            "position_tolerance": f"±{self.position_tolerance}mm",
            "measurement_tolerance": self.measurement_tolerance,
            "max_test_duration": f"{self.max_test_duration}s",
            "spec_points_count": len(self.spec_points),
            "has_2d_spec": self.has_2d_specification(),
        }

    def __str__(self) -> str:
        """Human-readable string representation"""
        spec_info = f", {len(self.spec_points)} 2D points" if self.spec_points else ""
        return (
            f"PassCriteria(force: {self.force_limit_min}-{self.force_limit_max}N, "
            f"temp: {self.temperature_limit_min}-{self.temperature_limit_max}°C{spec_info})"
        )

    def __repr__(self) -> str:
        """Debug representation"""
        return (
            f"PassCriteria(force_limits=({self.force_limit_min}, {self.force_limit_max}), "
            f"temp_limits=({self.temperature_limit_min}, {self.temperature_limit_max}), "
            f"tolerance={self.measurement_tolerance}, spec_points={len(self.spec_points)})"
        )
