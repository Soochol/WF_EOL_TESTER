"""
Pass Criteria Value Object

Immutable value object containing test pass/fail criteria and validation logic.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from scipy.interpolate import griddata
from domain.exceptions.validation_exceptions import ValidationException


@dataclass(frozen=True)
class PassCriteria:
    """테스트 합격 기준을 정의하는 불변 값 객체"""
    
    # Force criteria (N)
    force_limit_min: float = 0.0
    force_limit_max: float = 100.0
    
    # Temperature criteria (°C)
    temperature_limit_max: float = 80.0
    temperature_limit_min: float = -10.0
    
    # Measurement precision and tolerance
    measurement_tolerance: float = 0.001
    force_precision: int = 2
    temperature_precision: int = 1
    
    # Position criteria (mm)
    position_tolerance: float = 0.5
    
    # Timing criteria (seconds)
    max_test_duration: float = 300.0
    min_stabilization_time: float = 0.5
    
    # 2D Spec Matrix: (temperature, stroke, upper_limit, lower_limit)
    spec_points: List[Tuple[float, float, float, float]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate pass criteria after initialization"""
        self._validate_force_limits()
        self._validate_temperature_limits()
        self._validate_tolerances()
        self._validate_timing()
    
    def _validate_force_limits(self) -> None:
        """Validate force limit ranges"""
        if self.force_limit_min >= self.force_limit_max:
            raise ValidationException(
                "force_limit_min", 
                self.force_limit_min, 
                f"Force min ({self.force_limit_min}) must be less than max ({self.force_limit_max})"
            )
        
        if self.force_limit_min < 0:
            raise ValidationException(
                "force_limit_min", 
                self.force_limit_min, 
                "Force minimum cannot be negative"
            )
    
    def _validate_temperature_limits(self) -> None:
        """Validate temperature limit ranges"""
        if self.temperature_limit_min >= self.temperature_limit_max:
            raise ValidationException(
                "temperature_limit_min", 
                self.temperature_limit_min, 
                f"Temperature min ({self.temperature_limit_min}) must be less than max ({self.temperature_limit_max})"
            )
    
    def _validate_tolerances(self) -> None:
        """Validate tolerance values"""
        if self.measurement_tolerance <= 0:
            raise ValidationException(
                "measurement_tolerance", 
                self.measurement_tolerance, 
                "Measurement tolerance must be positive"
            )
        
        if self.position_tolerance <= 0:
            raise ValidationException(
                "position_tolerance", 
                self.position_tolerance, 
                "Position tolerance must be positive"
            )
    
    def _validate_timing(self) -> None:
        """Validate timing criteria"""
        if self.max_test_duration <= 0:
            raise ValidationException(
                "max_test_duration", 
                self.max_test_duration, 
                "Maximum test duration must be positive"
            )
        
        if self.min_stabilization_time < 0:
            raise ValidationException(
                "min_stabilization_time", 
                self.min_stabilization_time, 
                "Minimum stabilization time cannot be negative"
            )
    
    def is_force_within_limits(self, force: float) -> bool:
        """Check if force measurement is within acceptable limits"""
        return self.force_limit_min <= force <= self.force_limit_max
    
    def is_temperature_within_limits(self, temperature: float) -> bool:
        """Check if temperature is within acceptable limits"""
        return self.temperature_limit_min <= temperature <= self.temperature_limit_max
    
    def is_position_within_tolerance(self, expected: float, actual: float) -> bool:
        """Check if position is within tolerance of expected value"""
        return abs(expected - actual) <= self.position_tolerance
    
    def is_measurement_stable(self, measurements: list, tolerance_factor: float = 1.0) -> bool:
        """Check if measurements are stable within tolerance"""
        if len(measurements) < 2:
            return True
        
        tolerance = self.measurement_tolerance * tolerance_factor
        avg = sum(measurements) / len(measurements)
        
        return all(abs(m - avg) <= tolerance for m in measurements)
    
    def get_force_range(self) -> tuple[float, float]:
        """Get force limit range as tuple"""
        return (self.force_limit_min, self.force_limit_max)
    
    def get_temperature_range(self) -> tuple[float, float]:
        """Get temperature limit range as tuple"""
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
            return (self.force_limit_min, self.force_limit_max)
        
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
            upper_limit = griddata(points, upper_values, target_point, method='linear', fill_value=np.nan)[0]
            lower_limit = griddata(points, lower_values, target_point, method='linear', fill_value=np.nan)[0]
            
            # Handle extrapolation cases (outside spec point range)
            if np.isnan(upper_limit) or np.isnan(lower_limit):
                # Use nearest neighbor for extrapolation
                upper_limit = griddata(points, upper_values, target_point, method='nearest')[0]
                lower_limit = griddata(points, lower_values, target_point, method='nearest')[0]
            
            return (float(lower_limit), float(upper_limit))
            
        except Exception as e:
            # Fallback to global limits on interpolation failure
            return (self.force_limit_min, self.force_limit_max)
    
    def format_force(self, force: float) -> str:
        """Format force value according to precision setting"""
        return f"{force:.{self.force_precision}f}"
    
    def format_temperature(self, temperature: float) -> str:
        """Format temperature value according to precision setting"""
        return f"{temperature:.{self.temperature_precision}f}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'force_limit_min': self.force_limit_min,
            'force_limit_max': self.force_limit_max,
            'temperature_limit_max': self.temperature_limit_max,
            'temperature_limit_min': self.temperature_limit_min,
            'measurement_tolerance': self.measurement_tolerance,
            'force_precision': self.force_precision,
            'temperature_precision': self.temperature_precision,
            'position_tolerance': self.position_tolerance,
            'max_test_duration': self.max_test_duration,
            'min_stabilization_time': self.min_stabilization_time,
            'spec_points': [list(point) for point in self.spec_points]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PassCriteria':
        """Create PassCriteria from dictionary"""
        # Convert spec_points from list format back to tuples
        spec_points = []
        if 'spec_points' in data:
            spec_points = [tuple(point) for point in data['spec_points']]
        
        return cls(
            force_limit_min=data.get('force_limit_min', 0.0),
            force_limit_max=data.get('force_limit_max', 100.0),
            temperature_limit_max=data.get('temperature_limit_max', 80.0),
            temperature_limit_min=data.get('temperature_limit_min', -10.0),
            measurement_tolerance=data.get('measurement_tolerance', 0.001),
            force_precision=data.get('force_precision', 2),
            temperature_precision=data.get('temperature_precision', 1),
            position_tolerance=data.get('position_tolerance', 0.5),
            max_test_duration=data.get('max_test_duration', 300.0),
            min_stabilization_time=data.get('min_stabilization_time', 0.5),
            spec_points=spec_points
        )
    
    @classmethod
    def default(cls) -> 'PassCriteria':
        """Create default pass criteria"""
        return cls()
    
    def __str__(self) -> str:
        return f"PassCriteria(force: {self.force_limit_min}-{self.force_limit_max}N, temp: {self.temperature_limit_min}-{self.temperature_limit_max}°C)"