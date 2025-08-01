"""
Hardware Configuration Value Object

Immutable configuration object containing all hardware device connection parameters.
"""

from dataclasses import dataclass, field
from typing import Any, cast, Dict, Optional, Set

from domain.exceptions.validation_exceptions import (
    ValidationException,
)

# Supported hardware models
SUPPORTED_ROBOT_MODELS: Set[str] = {"AJINEXTEK", "MOCK"}
SUPPORTED_LOADCELL_MODELS: Set[str] = {"BS205", "MOCK"}
SUPPORTED_MCU_MODELS: Set[str] = {"LMA", "MOCK"}
SUPPORTED_POWER_MODELS: Set[str] = {"ODA", "MOCK"}
SUPPORTED_DIGITAL_INPUT_MODELS: Set[str] = {
    "AJINEXTEK",
    "MOCK",
}


@dataclass(frozen=True)
class RobotConfig:
    """Robot motion configuration"""

    # Hardware model
    model: str = "AJINEXTEK"

    # Connection parameters (AJINEXTEK specific)
    irq_no: int = 7


@dataclass(frozen=True)
class LoadCellConfig:
    """LoadCell device configuration (BS205)"""

    # Hardware model
    model: str = "BS205"

    # Connection parameters
    port: str = "COM3"
    baudrate: int = 9600
    timeout: float = 1.0
    bytesize: int = 8
    stopbits: int = 1
    parity: Optional[str] = None  # None, 'even', 'odd', 'mark', 'space'
    indicator_id: int = 1

    # Mock-related parameters
    base_force: float = 10.0
    noise_level: float = 0.1
    connection_delay: float = 0.1

    # Additional operational parameters
    max_force_range: float = 1000.0
    sampling_interval_ms: int = 100
    zero_tolerance: float = 0.01


@dataclass(frozen=True)
class MCUConfig:
    """MCU device configuration (LMA)"""

    # Hardware model
    model: str = "LMA"

    # Connection parameters
    port: str = "COM4"
    baudrate: int = 115200
    timeout: float = 2.0
    bytesize: int = 8
    stopbits: int = 1
    parity: Optional[str] = None  # None, 'even', 'odd', 'mark', 'space'

    # Default temperature/fan speed parameters
    default_temperature: float = 25.0
    default_fan_speed: float = 50.0

    # Mock-related parameters
    temperature_drift_rate: float = 0.1
    response_delay: float = 0.1
    connection_delay: float = 0.1

    # Operational parameters
    max_temperature: float = 150.0
    min_temperature: float = -40.0
    max_fan_speed: float = 100.0


@dataclass(frozen=True)
class PowerConfig:
    """Power supply configuration (ODA)"""

    # Hardware model
    model: str = "ODA"

    # Connection parameters
    host: str = "192.168.1.100"
    port: int = 8080
    timeout: float = 5.0
    channel: int = 1

    # Communication parameters
    delimiter: Optional[str] = "\n"  # Command terminator (None = TCP driver handles)

    # Default voltage/current parameters
    default_voltage: float = 0.0
    default_current_limit: float = 5.0

    # Mock-related parameters
    connection_delay: float = 0.2
    response_delay: float = 0.05
    voltage_noise: float = 0.01

    # Operational parameters
    max_voltage: float = 30.0
    max_current: float = 50.0
    voltage_accuracy: float = 0.01
    current_accuracy: float = 0.001


@dataclass(frozen=True)
class DigitalInputConfig:
    """Digital Input configuration (AJINEXTEK)"""

    # Hardware model
    model: str = "AJINEXTEK"

    # Connection parameters
    board_number: int = 0  # Renamed from board_no for consistency
    board_no: int = 0  # Keep for backward compatibility
    module_position: int = 0
    signal_type: int = 2  # 0=TTL, 1=CMOS, 2=24V industrial
    input_count: int = 8

    # Operational parameters
    debounce_time: float = 0.01
    debounce_time_ms: int = 10  # Debounce time in milliseconds
    retry_count: int = 3
    auto_initialize: bool = True

    # Mock-related parameters
    total_pins: int = 32  # For mock implementation
    simulate_noise: bool = False
    noise_probability: float = 0.01
    response_delay: float = 0.005  # Response delay in seconds
    connection_delay: float = 0.1  # Connection delay in seconds


@dataclass(frozen=True)
class HardwareConfiguration:
    """
    Hardware configuration value object containing all device connection parameters

    This is an immutable value object that represents hardware device configurations.
    Each hardware device has its own configuration section with connection parameters.
    """

    robot: RobotConfig = field(default_factory=RobotConfig)
    loadcell: LoadCellConfig = field(default_factory=LoadCellConfig)
    mcu: MCUConfig = field(default_factory=MCUConfig)
    power: PowerConfig = field(default_factory=PowerConfig)
    digital_input: DigitalInputConfig = field(default_factory=DigitalInputConfig)

    def __post_init__(self) -> None:
        """Validate configuration after initialization"""
        self._validate_robot_config()
        self._validate_communication_configs()
        self._validate_power_config()

    def _validate_robot_config(self) -> None:
        """Validate robot configuration parameters"""
        # Validate model
        if self.robot.model not in SUPPORTED_ROBOT_MODELS:
            raise ValidationException(
                "robot.model",
                self.robot.model,
                f"Unsupported robot model. Supported models: {', '.join(SUPPORTED_ROBOT_MODELS)}",
            )

        if self.robot.irq_no < 0:
            raise ValidationException(
                "robot.irq_no",
                self.robot.irq_no,
                "IRQ number cannot be negative",
            )

    def _validate_communication_configs(self) -> None:
        """Validate communication configuration parameters"""
        # LoadCell validation
        if self.loadcell.model not in SUPPORTED_LOADCELL_MODELS:
            raise ValidationException(
                "loadcell.model",
                self.loadcell.model,
                f"Unsupported loadcell model. Supported models: {', '.join(SUPPORTED_LOADCELL_MODELS)}",
            )

        if not self.loadcell.port:
            raise ValidationException(
                "loadcell.port",
                self.loadcell.port,
                "LoadCell port cannot be empty",
            )

        if self.loadcell.baudrate <= 0:
            raise ValidationException(
                "loadcell.baudrate",
                self.loadcell.baudrate,
                "LoadCell baudrate must be positive",
            )

        if self.loadcell.timeout <= 0:
            raise ValidationException(
                "loadcell.timeout",
                self.loadcell.timeout,
                "LoadCell timeout must be positive",
            )

        if self.loadcell.indicator_id < 0:
            raise ValidationException(
                "loadcell.indicator_id",
                self.loadcell.indicator_id,
                "LoadCell indicator ID cannot be negative",
            )

        # Validate mock-related parameters
        if self.loadcell.base_force < 0:
            raise ValidationException(
                "loadcell.base_force",
                self.loadcell.base_force,
                "LoadCell base force cannot be negative",
            )

        if self.loadcell.noise_level < 0:
            raise ValidationException(
                "loadcell.noise_level",
                self.loadcell.noise_level,
                "LoadCell noise level cannot be negative",
            )

        if self.loadcell.connection_delay < 0:
            raise ValidationException(
                "loadcell.connection_delay",
                self.loadcell.connection_delay,
                "LoadCell connection delay cannot be negative",
            )

        if self.loadcell.max_force_range <= 0:
            raise ValidationException(
                "loadcell.max_force_range",
                self.loadcell.max_force_range,
                "LoadCell max force range must be positive",
            )

        if self.loadcell.sampling_interval_ms <= 0:
            raise ValidationException(
                "loadcell.sampling_interval_ms",
                self.loadcell.sampling_interval_ms,
                "LoadCell sampling interval must be positive",
            )

        if self.loadcell.zero_tolerance < 0:
            raise ValidationException(
                "loadcell.zero_tolerance",
                self.loadcell.zero_tolerance,
                "LoadCell zero tolerance cannot be negative",
            )

        # Validate LoadCell serial parameters
        if self.loadcell.bytesize not in [5, 6, 7, 8]:
            raise ValidationException(
                "loadcell.bytesize",
                self.loadcell.bytesize,
                "LoadCell bytesize must be 5, 6, 7, or 8",
            )

        if self.loadcell.stopbits not in [1, 2]:
            raise ValidationException(
                "loadcell.stopbits",
                self.loadcell.stopbits,
                "LoadCell stopbits must be 1 or 2",
            )

        if self.loadcell.parity is not None and self.loadcell.parity.lower() not in [
            "none",
            "even",
            "odd",
            "mark",
            "space",
        ]:
            raise ValidationException(
                "loadcell.parity",
                self.loadcell.parity,
                "LoadCell parity must be None, 'none', 'even', 'odd', 'mark', or 'space'",
            )

        # MCU validation
        if self.mcu.model not in SUPPORTED_MCU_MODELS:
            raise ValidationException(
                "mcu.model",
                self.mcu.model,
                f"Unsupported MCU model. Supported models: {', '.join(SUPPORTED_MCU_MODELS)}",
            )

        if not self.mcu.port:
            raise ValidationException(
                "mcu.port",
                self.mcu.port,
                "MCU port cannot be empty",
            )

        if self.mcu.baudrate <= 0:
            raise ValidationException(
                "mcu.baudrate",
                self.mcu.baudrate,
                "MCU baudrate must be positive",
            )

        if self.mcu.timeout <= 0:
            raise ValidationException(
                "mcu.timeout",
                self.mcu.timeout,
                "MCU timeout must be positive",
            )

        # Validate default parameters
        if not (
            self.mcu.min_temperature <= self.mcu.default_temperature <= self.mcu.max_temperature
        ):
            raise ValidationException(
                "mcu.default_temperature",
                self.mcu.default_temperature,
                f"MCU default temperature must be between {self.mcu.min_temperature}°C and {self.mcu.max_temperature}°C",
            )

        if not (0.0 <= self.mcu.default_fan_speed <= self.mcu.max_fan_speed):
            raise ValidationException(
                "mcu.default_fan_speed",
                self.mcu.default_fan_speed,
                f"MCU default fan speed must be between 0% and {self.mcu.max_fan_speed}%",
            )

        # Validate mock-related parameters
        if self.mcu.temperature_drift_rate < 0:
            raise ValidationException(
                "mcu.temperature_drift_rate",
                self.mcu.temperature_drift_rate,
                "MCU temperature drift rate cannot be negative",
            )

        if self.mcu.response_delay < 0:
            raise ValidationException(
                "mcu.response_delay",
                self.mcu.response_delay,
                "MCU response delay cannot be negative",
            )

        if self.mcu.connection_delay < 0:
            raise ValidationException(
                "mcu.connection_delay",
                self.mcu.connection_delay,
                "MCU connection delay cannot be negative",
            )

        # Validate operational parameters
        if self.mcu.max_temperature <= self.mcu.min_temperature:
            raise ValidationException(
                "mcu.max_temperature",
                self.mcu.max_temperature,
                f"MCU max temperature must be greater than min temperature ({self.mcu.min_temperature}°C)",
            )

        if self.mcu.max_fan_speed <= 0:
            raise ValidationException(
                "mcu.max_fan_speed",
                self.mcu.max_fan_speed,
                "MCU max fan speed must be positive",
            )

        # Validate MCU serial parameters
        if self.mcu.bytesize not in [5, 6, 7, 8]:
            raise ValidationException(
                "mcu.bytesize",
                self.mcu.bytesize,
                "MCU bytesize must be 5, 6, 7, or 8",
            )

        if self.mcu.stopbits not in [1, 2]:
            raise ValidationException(
                "mcu.stopbits",
                self.mcu.stopbits,
                "MCU stopbits must be 1 or 2",
            )

        if self.mcu.parity is not None and self.mcu.parity.lower() not in [
            "none",
            "even",
            "odd",
            "mark",
            "space",
        ]:
            raise ValidationException(
                "mcu.parity",
                self.mcu.parity,
                "MCU parity must be None, 'none', 'even', 'odd', 'mark', or 'space'",
            )

        # Digital Input validation
        if self.digital_input.model not in SUPPORTED_DIGITAL_INPUT_MODELS:
            raise ValidationException(
                "digital_input.model",
                self.digital_input.model,
                f"Unsupported digital input model. Supported models: {', '.join(SUPPORTED_DIGITAL_INPUT_MODELS)}",
            )

        # Connection parameters validation
        if self.digital_input.board_number < 0:
            raise ValidationException(
                "digital_input.board_number",
                self.digital_input.board_number,
                "Board number cannot be negative",
            )

        if self.digital_input.board_no < 0:
            raise ValidationException(
                "digital_input.board_no",
                self.digital_input.board_no,
                "Board number cannot be negative",
            )

        if self.digital_input.module_position < 0:
            raise ValidationException(
                "digital_input.module_position",
                self.digital_input.module_position,
                "Module position cannot be negative",
            )

        if self.digital_input.signal_type not in [0, 1, 2]:
            raise ValidationException(
                "digital_input.signal_type",
                self.digital_input.signal_type,
                "Signal type must be 0 (TTL), 1 (CMOS), or 2 (24V)",
            )

        if self.digital_input.input_count <= 0:
            raise ValidationException(
                "digital_input.input_count",
                self.digital_input.input_count,
                "Input count must be positive",
            )

        # Operational parameters validation
        if self.digital_input.debounce_time < 0:
            raise ValidationException(
                "digital_input.debounce_time",
                self.digital_input.debounce_time,
                "Debounce time cannot be negative",
            )

        if self.digital_input.debounce_time_ms < 0:
            raise ValidationException(
                "digital_input.debounce_time_ms",
                self.digital_input.debounce_time_ms,
                "Debounce time (ms) cannot be negative",
            )

        if self.digital_input.retry_count < 0:
            raise ValidationException(
                "digital_input.retry_count",
                self.digital_input.retry_count,
                "Retry count cannot be negative",
            )

        # Mock-related parameters validation
        if self.digital_input.total_pins <= 0:
            raise ValidationException(
                "digital_input.total_pins",
                self.digital_input.total_pins,
                "Total pins must be positive",
            )

        if not (0.0 <= self.digital_input.noise_probability <= 1.0):
            raise ValidationException(
                "digital_input.noise_probability",
                self.digital_input.noise_probability,
                "Noise probability must be between 0.0 and 1.0",
            )

        if self.digital_input.response_delay < 0:
            raise ValidationException(
                "digital_input.response_delay",
                self.digital_input.response_delay,
                "Response delay cannot be negative",
            )

        if self.digital_input.connection_delay < 0:
            raise ValidationException(
                "digital_input.connection_delay",
                self.digital_input.connection_delay,
                "Connection delay cannot be negative",
            )

    def _validate_power_config(self) -> None:
        """Validate power supply configuration parameters"""
        # Validate model
        if self.power.model not in SUPPORTED_POWER_MODELS:
            raise ValidationException(
                "power.model",
                self.power.model,
                f"Unsupported power supply model. Supported models: {', '.join(SUPPORTED_POWER_MODELS)}",
            )

        if not self.power.host:
            raise ValidationException(
                "power.host",
                self.power.host,
                "Power host cannot be empty",
            )

        if not 1 <= self.power.port <= 65535:
            raise ValidationException(
                "power.port",
                self.power.port,
                "Power port must be between 1 and 65535",
            )

        if self.power.timeout <= 0:
            raise ValidationException(
                "power.timeout",
                self.power.timeout,
                "Power timeout must be positive",
            )

        if self.power.channel <= 0:
            raise ValidationException(
                "power.channel",
                self.power.channel,
                "Power channel must be positive",
            )

        # Validate default parameters
        if self.power.default_voltage < 0:
            raise ValidationException(
                "power.default_voltage",
                self.power.default_voltage,
                "Power default voltage cannot be negative",
            )

        if self.power.default_current_limit <= 0:
            raise ValidationException(
                "power.default_current_limit",
                self.power.default_current_limit,
                "Power default current limit must be positive",
            )

        # Validate mock-related parameters
        if self.power.connection_delay < 0:
            raise ValidationException(
                "power.connection_delay",
                self.power.connection_delay,
                "Power connection delay cannot be negative",
            )

        if self.power.response_delay < 0:
            raise ValidationException(
                "power.response_delay",
                self.power.response_delay,
                "Power response delay cannot be negative",
            )

        if self.power.voltage_noise < 0:
            raise ValidationException(
                "power.voltage_noise",
                self.power.voltage_noise,
                "Power voltage noise cannot be negative",
            )

        # Validate operational parameters
        if self.power.max_voltage <= 0:
            raise ValidationException(
                "power.max_voltage",
                self.power.max_voltage,
                "Power max voltage must be positive",
            )

        if self.power.max_current <= 0:
            raise ValidationException(
                "power.max_current",
                self.power.max_current,
                "Power max current must be positive",
            )

        if self.power.voltage_accuracy < 0:
            raise ValidationException(
                "power.voltage_accuracy",
                self.power.voltage_accuracy,
                "Power voltage accuracy cannot be negative",
            )

        if self.power.current_accuracy < 0:
            raise ValidationException(
                "power.current_accuracy",
                self.power.current_accuracy,
                "Power current accuracy cannot be negative",
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

    def with_overrides(self, **overrides: Any) -> "HardwareConfiguration":
        """
        Create new configuration with specific field overrides

        Args:
            **overrides: Field values to override

        Returns:
            New HardwareConfiguration instance with overridden values

        Raises:
            ValidationException: If overridden values are invalid
        """
        # Get current values as dict
        current_values = {
            "robot": self.robot,
            "loadcell": self.loadcell,
            "mcu": self.mcu,
            "power": self.power,
            "digital_input": self.digital_input,
        }

        # Apply overrides
        current_values.update(overrides)

        # Handle nested config overrides
        for config_name in [
            "robot",
            "loadcell",
            "mcu",
            "power",
            "digital_input",
        ]:
            if config_name in overrides and isinstance(overrides[config_name], dict):
                # Get the appropriate config class
                config_class = {
                    "robot": RobotConfig,
                    "loadcell": LoadCellConfig,
                    "mcu": MCUConfig,
                    "power": PowerConfig,
                    "digital_input": DigitalInputConfig,
                }[config_name]

                # Create new config instance from dict
                current_values[config_name] = config_class(**overrides[config_name])

        # Create new instance with properly typed config objects
        return HardwareConfiguration(
            robot=cast(
                RobotConfig,
                current_values.get("robot", self.robot),
            ),
            loadcell=cast(
                LoadCellConfig,
                current_values.get("loadcell", self.loadcell),
            ),
            mcu=cast(
                MCUConfig,
                current_values.get("mcu", self.mcu),
            ),
            power=cast(
                PowerConfig,
                current_values.get("power", self.power),
            ),
            digital_input=cast(
                DigitalInputConfig,
                current_values.get("digital_input", self.digital_input),
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation"""
        return {
            "robot": {
                "model": self.robot.model,
                "irq_no": self.robot.irq_no,
            },
            "loadcell": {
                "model": self.loadcell.model,
                "port": self.loadcell.port,
                "baudrate": self.loadcell.baudrate,
                "timeout": self.loadcell.timeout,
                "bytesize": self.loadcell.bytesize,
                "stopbits": self.loadcell.stopbits,
                "parity": self.loadcell.parity,
                "indicator_id": self.loadcell.indicator_id,
                "base_force": self.loadcell.base_force,
                "noise_level": self.loadcell.noise_level,
                "connection_delay": self.loadcell.connection_delay,
                "max_force_range": self.loadcell.max_force_range,
                "sampling_interval_ms": self.loadcell.sampling_interval_ms,
                "zero_tolerance": self.loadcell.zero_tolerance,
            },
            "mcu": {
                "model": self.mcu.model,
                "port": self.mcu.port,
                "baudrate": self.mcu.baudrate,
                "timeout": self.mcu.timeout,
                "bytesize": self.mcu.bytesize,
                "stopbits": self.mcu.stopbits,
                "parity": self.mcu.parity,
                "default_temperature": self.mcu.default_temperature,
                "default_fan_speed": self.mcu.default_fan_speed,
                "temperature_drift_rate": self.mcu.temperature_drift_rate,
                "response_delay": self.mcu.response_delay,
                "connection_delay": self.mcu.connection_delay,
                "max_temperature": self.mcu.max_temperature,
                "min_temperature": self.mcu.min_temperature,
                "max_fan_speed": self.mcu.max_fan_speed,
            },
            "power": {
                "model": self.power.model,
                "host": self.power.host,
                "port": self.power.port,
                "timeout": self.power.timeout,
                "channel": self.power.channel,
                "delimiter": self.power.delimiter,
                "default_voltage": self.power.default_voltage,
                "default_current_limit": self.power.default_current_limit,
                "connection_delay": self.power.connection_delay,
                "response_delay": self.power.response_delay,
                "voltage_noise": self.power.voltage_noise,
                "max_voltage": self.power.max_voltage,
                "max_current": self.power.max_current,
                "voltage_accuracy": self.power.voltage_accuracy,
                "current_accuracy": self.power.current_accuracy,
            },
            "digital_input": {
                "model": self.digital_input.model,
                "board_number": self.digital_input.board_number,
                "board_no": self.digital_input.board_no,
                "module_position": self.digital_input.module_position,
                "signal_type": self.digital_input.signal_type,
                "input_count": self.digital_input.input_count,
                "debounce_time": self.digital_input.debounce_time,
                "debounce_time_ms": self.digital_input.debounce_time_ms,
                "retry_count": self.digital_input.retry_count,
                "auto_initialize": self.digital_input.auto_initialize,
                "total_pins": self.digital_input.total_pins,
                "simulate_noise": self.digital_input.simulate_noise,
                "noise_probability": self.digital_input.noise_probability,
                "response_delay": self.digital_input.response_delay,
                "connection_delay": self.digital_input.connection_delay,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HardwareConfiguration":
        """
        Create configuration from dictionary

        Args:
            data: Dictionary containing configuration values

        Returns:
            HardwareConfiguration instance

        Raises:
            ValidationException: If dictionary contains invalid values
        """
        # Create a copy to avoid modifying original data
        data_copy = data.copy()

        # Handle nested config dictionaries
        config_classes = {
            "robot": RobotConfig,
            "loadcell": LoadCellConfig,
            "mcu": MCUConfig,
            "power": PowerConfig,
            "digital_input": DigitalInputConfig,
        }

        for (
            config_name,
            config_class,
        ) in config_classes.items():
            if config_name in data_copy and isinstance(data_copy[config_name], dict):
                data_copy[config_name] = config_class(**data_copy[config_name])

        # Create instance with properly typed config objects
        return cls(
            robot=cast(
                RobotConfig,
                data_copy.get("robot", RobotConfig()),
            ),
            loadcell=cast(
                LoadCellConfig,
                data_copy.get("loadcell", LoadCellConfig()),
            ),
            mcu=cast(MCUConfig, data_copy.get("mcu", MCUConfig())),
            power=cast(
                PowerConfig,
                data_copy.get("power", PowerConfig()),
            ),
            digital_input=cast(
                DigitalInputConfig,
                data_copy.get("digital_input", DigitalInputConfig()),
            ),
        )

    def __str__(self) -> str:
        return f"HardwareConfig({self.robot.model}/{self.loadcell.model}/{self.mcu.model}/{self.power.model}/{self.digital_input.model})"

    def __repr__(self) -> str:
        return (
            f"HardwareConfiguration(robot={self.robot}, loadcell={self.loadcell}, "
            f"mcu={self.mcu}, power={self.power}, digital_input={self.digital_input})"
        )
