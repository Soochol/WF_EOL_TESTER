"""
Heating/Cooling Time Test Configuration Value Object

Configuration parameters for heating/cooling time test including
wait times, power monitoring settings, and test execution parameters.
"""

from dataclasses import dataclass


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
