"""
Heating/Cooling Time Test Configuration Value Object

Configuration parameters for heating/cooling time test including
wait times, power monitoring settings, and test execution parameters.
"""

# Future imports
from __future__ import annotations

# Standard library imports
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class HeatingCoolingConfiguration:
    """
    Heating/Cooling Time Test Configuration

    Immutable configuration object for heating/cooling test parameters.
    Contains default values for all test settings including wait times,
    power monitoring intervals, and measurement parameters.

    All time values are in seconds unless otherwise specified.
    """

    # ========================================================================
    # TEST EXECUTION PARAMETERS
    # ========================================================================
    repeat_count: int = 1  # Number of heating/cooling cycles to perform

    # ========================================================================
    # WAIT TIME PARAMETERS
    # ========================================================================
    heating_wait_time: float = 2.0  # Wait time after heating completes (seconds)
    cooling_wait_time: float = 2.0  # Wait time after cooling completes (seconds)
    stabilization_wait_time: float = 1.0  # Wait time for temperature stabilization (seconds)

    # ========================================================================
    # POWER MONITORING PARAMETERS
    # ========================================================================
    power_monitoring_interval: float = 0.5  # Power measurement interval (seconds)
    power_monitoring_enabled: bool = True  # Enable/disable power monitoring

    # ========================================================================
    # TEMPERATURE PARAMETERS (from existing TestConfiguration)
    # ========================================================================
    activation_temperature: float = 52.0  # Temperature activation threshold (°C)
    standby_temperature: float = 38.0  # Standby temperature setting (°C)

    # ========================================================================
    # POWER SUPPLY PARAMETERS (from existing TestConfiguration)
    # ========================================================================
    voltage: float = 38.0  # Operating voltage (V) - Updated from 18V to 38V based on logs
    current: float = 25.0  # Operating current (A) - Updated from 20A to 25A based on logs

    # ========================================================================
    # MCU PARAMETERS
    # ========================================================================
    fan_speed: int = 10  # Fan speed level (1-10)
    upper_temperature: float = 80.0  # Maximum temperature limit (°C)

    # ========================================================================
    # ROBOT INTEGRATION PARAMETERS
    # ========================================================================
    enable_robot: bool = True  # Enable robot integration
    enable_force_measurement: bool = True  # Enable force measurement during test

    # Robot motion parameters
    velocity: float = 100000.0  # Robot velocity (μm/s)
    acceleration: float = 85000.0  # Robot acceleration (μm/s²)
    deceleration: float = 85000.0  # Robot deceleration (μm/s²)

    # Robot positions (μm)
    initial_position: float = 1000.0  # Initial/safe position
    measurement_positions: List[float] = field(
        default_factory=lambda: [100000.0, 130000.0, 170000.0]
    )  # Force measurement positions

    # Robot timing (seconds)
    robot_move_stabilization: float = 0.1  # Post-movement stabilization time
    force_measurement_delay: float = 0.05  # Pre-measurement delay

    # ========================================================================
    # STABILIZATION TIME PARAMETERS
    # ========================================================================
    poweron_stabilization: float = 0.5  # Power-on stabilization time (s)
    mcu_boot_complete_stabilization: float = 2.0  # MCU boot complete stabilization time (s)
    mcu_command_stabilization: float = 0.1  # MCU command stabilization time (s)
    mcu_temperature_stabilization: float = 0.1  # MCU temperature stabilization time (s)

    # ========================================================================
    # STATISTICS PARAMETERS
    # ========================================================================
    calculate_statistics: bool = True  # Calculate power consumption statistics
    show_detailed_results: bool = True  # Show detailed cycle-by-cycle results

    # ========================================================================
    # POWER ANALYZER MEASUREMENT PARAMETERS (Optional, Test-specific)
    # ========================================================================
    # If power analyzer is configured, these test-specific settings will override
    # hardware config defaults. Leave as None to use hardware config values.
    power_analyzer_voltage_range: Optional[str] = (
        None  # e.g., "15V", "30V", "60V", "150V", "300V", "600V", "1000V"
    )
    power_analyzer_current_range: Optional[str] = (
        None  # e.g., "1A", "2A", "5A", "10A", "20A", "50A"
    )
    power_analyzer_auto_range: Optional[bool] = None  # None = use hardware config default
    power_analyzer_line_filter: Optional[str] = None  # e.g., "500HZ", "1KHZ", "10KHZ", "100KHZ"
    power_analyzer_frequency_filter: Optional[str] = (
        None  # e.g., "0.5HZ", "1HZ", "10HZ", "100HZ", "1KHZ"
    )
    power_analyzer_element: Optional[int] = (
        None  # Measurement element/channel (1-6), None = use hardware config
    )

    def __post_init__(self):
        """Validate configuration parameters"""
        if self.repeat_count < 1:
            raise ValueError("repeat_count must be at least 1")

        if self.heating_wait_time < 0:
            raise ValueError("heating_wait_time must be non-negative")

        if self.cooling_wait_time < 0:
            raise ValueError("cooling_wait_time must be non-negative")

        if self.power_monitoring_interval <= 0:
            raise ValueError("power_monitoring_interval must be positive")

        if self.activation_temperature <= self.standby_temperature:
            raise ValueError("activation_temperature must be higher than standby_temperature")

        if self.voltage <= 0:
            raise ValueError("voltage must be positive")

        if self.current <= 0:
            raise ValueError("current must be positive")

        if not (1 <= self.fan_speed <= 10):
            raise ValueError("fan_speed must be between 1 and 10")

        if self.poweron_stabilization < 0:
            raise ValueError("poweron_stabilization must be non-negative")

        if self.mcu_boot_complete_stabilization < 0:
            raise ValueError("mcu_boot_complete_stabilization must be non-negative")

        if self.mcu_command_stabilization < 0:
            raise ValueError("mcu_command_stabilization must be non-negative")

        if self.mcu_temperature_stabilization < 0:
            raise ValueError("mcu_temperature_stabilization must be non-negative")

        # Validate power analyzer parameters (if specified)
        if self.power_analyzer_element is not None:
            if not (1 <= self.power_analyzer_element <= 6):
                raise ValueError("power_analyzer_element must be between 1 and 6")

        # Validate robot parameters (if robot enabled)
        if self.enable_robot:
            if self.velocity <= 0:
                raise ValueError("velocity must be positive")

            if self.acceleration <= 0:
                raise ValueError("acceleration must be positive")

            if self.deceleration <= 0:
                raise ValueError("deceleration must be positive")

            if self.initial_position < 0:
                raise ValueError("initial_position must be non-negative")

            if not self.measurement_positions:
                raise ValueError("measurement_positions cannot be empty when robot is enabled")

            for pos in self.measurement_positions:
                if pos < 0:
                    raise ValueError("all measurement_positions must be non-negative")

            if self.robot_move_stabilization < 0:
                raise ValueError("robot_move_stabilization must be non-negative")

            if self.force_measurement_delay < 0:
                raise ValueError("force_measurement_delay must be non-negative")

    @property
    def total_cycle_time_estimate(self) -> float:
        """
        Estimate total cycle time including heating, cooling, and wait times

        Returns:
            Estimated total cycle time in seconds
        """
        # Rough estimates based on typical heating/cooling times
        estimated_heating_time = 3.0  # ~3 seconds based on logs
        estimated_cooling_time = 12.0  # ~12 seconds based on logs

        single_cycle_time = (
            estimated_heating_time
            + self.heating_wait_time
            + estimated_cooling_time
            + self.cooling_wait_time
            + self.stabilization_wait_time
        )

        return single_cycle_time * self.repeat_count

    @property
    def expected_sample_count(self) -> int:
        """
        Calculate expected number of power measurement samples

        Returns:
            Expected number of samples based on cycle time and interval
        """
        return int(self.total_cycle_time_estimate / self.power_monitoring_interval)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization"""
        return {
            # TEST EXECUTION PARAMETERS
            "repeat_count": self.repeat_count,
            # WAIT TIME PARAMETERS
            "heating_wait_time": self.heating_wait_time,
            "cooling_wait_time": self.cooling_wait_time,
            "stabilization_wait_time": self.stabilization_wait_time,
            # POWER MONITORING PARAMETERS
            "power_monitoring_interval": self.power_monitoring_interval,
            "power_monitoring_enabled": self.power_monitoring_enabled,
            # TEMPERATURE PARAMETERS
            "activation_temperature": self.activation_temperature,
            "standby_temperature": self.standby_temperature,
            # POWER SUPPLY PARAMETERS
            "voltage": self.voltage,
            "current": self.current,
            # MCU PARAMETERS
            "fan_speed": self.fan_speed,
            "upper_temperature": self.upper_temperature,
            # ROBOT INTEGRATION PARAMETERS
            "enable_robot": self.enable_robot,
            "enable_force_measurement": self.enable_force_measurement,
            "velocity": self.velocity,
            "acceleration": self.acceleration,
            "deceleration": self.deceleration,
            "initial_position": self.initial_position,
            "measurement_positions": self.measurement_positions,
            "robot_move_stabilization": self.robot_move_stabilization,
            "force_measurement_delay": self.force_measurement_delay,
            # STABILIZATION TIME PARAMETERS
            "poweron_stabilization": self.poweron_stabilization,
            "mcu_boot_complete_stabilization": self.mcu_boot_complete_stabilization,
            "mcu_command_stabilization": self.mcu_command_stabilization,
            "mcu_temperature_stabilization": self.mcu_temperature_stabilization,
            # STATISTICS PARAMETERS
            "calculate_statistics": self.calculate_statistics,
            "show_detailed_results": self.show_detailed_results,
            # POWER ANALYZER MEASUREMENT PARAMETERS
            "power_analyzer_voltage_range": self.power_analyzer_voltage_range,
            "power_analyzer_current_range": self.power_analyzer_current_range,
            "power_analyzer_auto_range": self.power_analyzer_auto_range,
            "power_analyzer_line_filter": self.power_analyzer_line_filter,
            "power_analyzer_frequency_filter": self.power_analyzer_frequency_filter,
            "power_analyzer_element": self.power_analyzer_element,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HeatingCoolingConfiguration:
        """Create HeatingCoolingConfiguration from dictionary with automatic defaults"""
        return cls(
            # TEST EXECUTION PARAMETERS
            repeat_count=data.get("repeat_count", 1),
            # WAIT TIME PARAMETERS
            heating_wait_time=data.get("heating_wait_time", 2.0),
            cooling_wait_time=data.get("cooling_wait_time", 2.0),
            stabilization_wait_time=data.get("stabilization_wait_time", 1.0),
            # POWER MONITORING PARAMETERS
            power_monitoring_interval=data.get("power_monitoring_interval", 0.5),
            power_monitoring_enabled=data.get("power_monitoring_enabled", True),
            # TEMPERATURE PARAMETERS
            activation_temperature=data.get("activation_temperature", 52.0),
            standby_temperature=data.get("standby_temperature", 38.0),
            # POWER SUPPLY PARAMETERS
            voltage=data.get("voltage", 38.0),
            current=data.get("current", 25.0),
            # MCU PARAMETERS
            fan_speed=data.get("fan_speed", 10),
            upper_temperature=data.get("upper_temperature", 80.0),
            # ROBOT INTEGRATION PARAMETERS
            enable_robot=data.get("enable_robot", True),
            enable_force_measurement=data.get("enable_force_measurement", True),
            velocity=data.get("velocity", 100000.0),
            acceleration=data.get("acceleration", 85000.0),
            deceleration=data.get("deceleration", 85000.0),
            initial_position=data.get("initial_position", 1000.0),
            measurement_positions=data.get("measurement_positions", [100000.0, 130000.0, 170000.0]),
            robot_move_stabilization=data.get("robot_move_stabilization", 0.1),
            force_measurement_delay=data.get("force_measurement_delay", 0.05),
            # STABILIZATION TIME PARAMETERS
            poweron_stabilization=data.get("poweron_stabilization", 0.5),
            mcu_boot_complete_stabilization=data.get("mcu_boot_complete_stabilization", 2.0),
            mcu_command_stabilization=data.get("mcu_command_stabilization", 0.1),
            mcu_temperature_stabilization=data.get("mcu_temperature_stabilization", 0.1),
            # STATISTICS PARAMETERS
            calculate_statistics=data.get("calculate_statistics", True),
            show_detailed_results=data.get("show_detailed_results", True),
            # POWER ANALYZER MEASUREMENT PARAMETERS
            power_analyzer_voltage_range=data.get("power_analyzer_voltage_range"),
            power_analyzer_current_range=data.get("power_analyzer_current_range"),
            power_analyzer_auto_range=data.get("power_analyzer_auto_range"),
            power_analyzer_line_filter=data.get("power_analyzer_line_filter"),
            power_analyzer_frequency_filter=data.get("power_analyzer_frequency_filter"),
            power_analyzer_element=data.get("power_analyzer_element"),
        )
