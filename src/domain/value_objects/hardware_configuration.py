"""
Hardware Configuration Value Object

Immutable configuration object containing all hardware device connection parameters.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Set

from domain.exceptions.validation_exceptions import ValidationException

# Supported hardware models
SUPPORTED_ROBOT_MODELS: Set[str] = {"AJINEXTEK", "MOCK"}
SUPPORTED_LOADCELL_MODELS: Set[str] = {"BS205", "MOCK"}
SUPPORTED_MCU_MODELS: Set[str] = {"LMA", "MOCK"}
SUPPORTED_POWER_MODELS: Set[str] = {"ODA", "MOCK"}
SUPPORTED_DIGITAL_INPUT_MODELS: Set[str] = {"AJINEXTEK", "MOCK"}


@dataclass(frozen=True)
class RobotConfig:
    """Robot motion configuration"""

    # Hardware model
    model: str = "AJINEXTEK"

    # Connection parameters (AJINEXTEK specific)
    irq_no: int = 7
    axis_count: int = 6


@dataclass(frozen=True)
class LoadCellConfig:
    """LoadCell device configuration (BS205)"""

    # Hardware model
    model: str = "BS205"

    port: str = "COM3"
    baudrate: int = 9600
    timeout: float = 1.0
    indicator_id: int = 1


@dataclass(frozen=True)
class MCUConfig:
    """MCU device configuration (LMA)"""

    # Hardware model
    model: str = "LMA"

    port: str = "COM4"
    baudrate: int = 115200
    timeout: float = 2.0


@dataclass(frozen=True)
class PowerConfig:
    """Power supply configuration (ODA)"""

    # Hardware model
    model: str = "ODA"

    host: str = "192.168.1.100"
    port: int = 8080
    timeout: float = 5.0
    channel: int = 1


@dataclass(frozen=True)
class DigitalInputConfig:
    """Digital Input configuration (AJINEXTEK)"""

    # Hardware model
    model: str = "AJINEXTEK"

    board_no: int = 0
    input_count: int = 8
    debounce_time: float = 0.01


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
                "robot.model", self.robot.model, f"Unsupported robot model. Supported models: {', '.join(SUPPORTED_ROBOT_MODELS)}"
            )

        if self.robot.irq_no < 0:
            raise ValidationException("robot.irq_no", self.robot.irq_no, "IRQ number cannot be negative")

        if self.robot.axis_count <= 0:
            raise ValidationException("robot.axis_count", self.robot.axis_count, "Axis count must be positive")

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
            raise ValidationException("loadcell.port", self.loadcell.port, "LoadCell port cannot be empty")

        if self.loadcell.baudrate <= 0:
            raise ValidationException("loadcell.baudrate", self.loadcell.baudrate, "LoadCell baudrate must be positive")

        if self.loadcell.timeout <= 0:
            raise ValidationException("loadcell.timeout", self.loadcell.timeout, "LoadCell timeout must be positive")

        if self.loadcell.indicator_id < 0:
            raise ValidationException(
                "loadcell.indicator_id", self.loadcell.indicator_id, "LoadCell indicator ID cannot be negative"
            )

        # MCU validation
        if self.mcu.model not in SUPPORTED_MCU_MODELS:
            raise ValidationException(
                "mcu.model", self.mcu.model, f"Unsupported MCU model. Supported models: {', '.join(SUPPORTED_MCU_MODELS)}"
            )

        if not self.mcu.port:
            raise ValidationException("mcu.port", self.mcu.port, "MCU port cannot be empty")

        if self.mcu.baudrate <= 0:
            raise ValidationException("mcu.baudrate", self.mcu.baudrate, "MCU baudrate must be positive")

        if self.mcu.timeout <= 0:
            raise ValidationException("mcu.timeout", self.mcu.timeout, "MCU timeout must be positive")

        # Digital Input validation
        if self.digital_input.model not in SUPPORTED_DIGITAL_INPUT_MODELS:
            raise ValidationException(
                "digital_input.model",
                self.digital_input.model,
                f"Unsupported digital input model. Supported models: {', '.join(SUPPORTED_DIGITAL_INPUT_MODELS)}",
            )

        if self.digital_input.board_no < 0:
            raise ValidationException("digital_input.board_no", self.digital_input.board_no, "Board number cannot be negative")

        if self.digital_input.input_count <= 0:
            raise ValidationException("digital_input.input_count", self.digital_input.input_count, "Input count must be positive")

        if self.digital_input.debounce_time < 0:
            raise ValidationException(
                "digital_input.debounce_time", self.digital_input.debounce_time, "Debounce time cannot be negative"
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
            raise ValidationException("power.host", self.power.host, "Power host cannot be empty")

        if not (1 <= self.power.port <= 65535):
            raise ValidationException("power.port", self.power.port, "Power port must be between 1 and 65535")

        if self.power.timeout <= 0:
            raise ValidationException("power.timeout", self.power.timeout, "Power timeout must be positive")

        if self.power.channel <= 0:
            raise ValidationException("power.channel", self.power.channel, "Power channel must be positive")

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

    def with_overrides(self, **overrides) -> "HardwareConfiguration":
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
        for config_name in ["robot", "loadcell", "mcu", "power", "digital_input"]:
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

        # Create new instance
        return HardwareConfiguration(**current_values)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation"""
        return {
            "robot": {"model": self.robot.model, "irq_no": self.robot.irq_no, "axis_count": self.robot.axis_count},
            "loadcell": {
                "model": self.loadcell.model,
                "port": self.loadcell.port,
                "baudrate": self.loadcell.baudrate,
                "timeout": self.loadcell.timeout,
                "indicator_id": self.loadcell.indicator_id,
            },
            "mcu": {"model": self.mcu.model, "port": self.mcu.port, "baudrate": self.mcu.baudrate, "timeout": self.mcu.timeout},
            "power": {
                "model": self.power.model,
                "host": self.power.host,
                "port": self.power.port,
                "timeout": self.power.timeout,
                "channel": self.power.channel,
            },
            "digital_input": {
                "model": self.digital_input.model,
                "board_no": self.digital_input.board_no,
                "input_count": self.digital_input.input_count,
                "debounce_time": self.digital_input.debounce_time,
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

        for config_name, config_class in config_classes.items():
            if config_name in data_copy and isinstance(data_copy[config_name], dict):
                data_copy[config_name] = config_class(**data_copy[config_name])

        return cls(**data_copy)

    def __str__(self) -> str:
        return f"HardwareConfiguration(robot={self.robot.model}:{self.robot.axis}, loadcell={self.loadcell.model}:{self.loadcell.port}, mcu={self.mcu.model}:{self.mcu.port}, power={self.power.model}, input={self.digital_input.model})"

    def __repr__(self) -> str:
        return (
            f"HardwareConfiguration(robot={self.robot}, loadcell={self.loadcell}, "
            f"mcu={self.mcu}, power={self.power}, digital_input={self.digital_input})"
        )
