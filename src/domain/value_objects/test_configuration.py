"""
Test Configuration Value Object

Immutable configuration object containing all test parameters and settings.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from domain.exceptions.validation_exceptions import ValidationException


@dataclass(frozen=True)
class TestConfiguration:
    """
    Test configuration value object containing all test parameters
    
    This is an immutable value object that represents test configuration settings.
    Two configurations with same values are considered identical.
    """
    
    # Hardware default settings
    voltage: float = 18.0
    current: float = 20.0
    upper_temperature: float = 80.0
    fan_speed: int = 10
    standby_position: float = 10.0
    max_stroke: float = 240.0
    initial_position: float = 10.0
    
    # Test parameters
    temperature_list: List[float] = field(default_factory=lambda: [38.0, 40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 54.0, 56.0, 58.0, 60.0])
    stroke_positions: List[float] = field(default_factory=lambda: [10.0, 60.0, 100.0, 140.0, 180.0, 220.0, 240.0])
    
    # Timing settings (in seconds)
    stabilization_delay: float = 0.5
    temperature_stabilization: float = 1.0
    power_stabilization: float = 0.5
    loadcell_zero_delay: float = 0.1
    
    # Measurement tolerances and precision
    measurement_tolerance: float = 0.001
    force_precision: int = 2
    temperature_precision: int = 1
    
    # Test execution settings
    retry_attempts: int = 3
    timeout_seconds: float = 60.0
    
    # Safety limits
    max_temperature: float = 80.0
    max_force: float = 1000.0
    max_voltage: float = 30.0
    max_current: float = 30.0
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization"""
        self._validate_hardware_settings()
        self._validate_test_parameters()
        self._validate_safety_limits()
        self._validate_timing_settings()
    
    def _validate_hardware_settings(self) -> None:
        """Validate hardware configuration parameters"""
        if self.voltage <= 0:
            raise ValidationException("voltage", self.voltage, "Voltage must be positive")
        
        if self.current <= 0:
            raise ValidationException("current", self.current, "Current must be positive")
        
        if self.upper_temperature <= 0:
            raise ValidationException("upper_temperature", self.upper_temperature, "Upper temperature must be positive")
        
        if not (0 <= self.fan_speed <= 100):
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
        if self.max_temperature <= self.upper_temperature:
            raise ValidationException("max_temperature", self.max_temperature, 
                                    f"Max temperature must be greater than upper temperature ({self.upper_temperature})")
        
        if self.max_force <= 0:
            raise ValidationException("max_force", self.max_force, "Max force must be positive")
        
        if self.max_voltage <= self.voltage:
            raise ValidationException("max_voltage", self.max_voltage, 
                                    f"Max voltage must be greater than operating voltage ({self.voltage})")
        
        if self.max_current <= self.current:
            raise ValidationException("max_current", self.max_current, 
                                    f"Max current must be greater than operating current ({self.current})")
    
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
            'max_temperature': self.max_temperature,
            'max_force': self.max_force,
            'max_voltage': self.max_voltage,
            'max_current': self.max_current
        }
        
        # Apply overrides
        current_values.update(overrides)
        
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
            'max_temperature': self.max_temperature,
            'max_force': self.max_force,
            'max_voltage': self.max_voltage,
            'max_current': self.max_current
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
        return cls(**data)
    
    def __str__(self) -> str:
        duration = self.estimate_test_duration_seconds()
        points = self.get_total_measurement_points()
        return f"TestConfiguration({self.voltage}V, {self.current}A, {points} points, ~{duration:.0f}s)"
    
    def __repr__(self) -> str:
        return (f"TestConfiguration(voltage={self.voltage}, current={self.current}, "
                f"temperatures={len(self.temperature_list)}, positions={len(self.stroke_positions)})")