"""
Hardware Configuration Value Object

Immutable configuration object containing all hardware device connection parameters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set, cast

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

    # Connection parameters (AJINEXTEK specific)
    irq_no: int = 7

    # Motion control parameters
    axis_id: int = 0

    # Motion parameters
    velocity: float = 200.0
    acceleration: float = 1000.0
    deceleration: float = 1000.0


@dataclass(frozen=True)
class LoadCellConfig:
    """LoadCell device configuration (BS205)"""

    # Connection parameters
    port: str = "COM8"
    baudrate: int = 9600
    timeout: float = 1.0
    bytesize: int = 8
    stopbits: int = 1
    parity: Optional[str] = "even"  # None, 'even', 'odd', 'mark', 'space'
    indicator_id: int = 0


@dataclass(frozen=True)
class MCUConfig:
    """MCU device configuration (LMA)"""

    # Connection parameters
    port: str = "COM9"
    baudrate: int = 115200
    timeout: float = 60.0
    bytesize: int = 8
    stopbits: int = 1
    parity: Optional[str] = None  # None, 'even', 'odd', 'mark', 'space'


@dataclass(frozen=True)
class PowerConfig:
    """Power supply configuration (ODA)"""

    # Connection parameters
    host: str = "192.168.11.1"
    port: int = 5000
    timeout: float = 5.0
    channel: int = 1

    # Communication parameters
    delimiter: Optional[str] = "\n"  # Command terminator (None = TCP driver handles)


@dataclass(frozen=True)
class DigitalIOConfig:
    """Digital Input configuration (AJINEXTEK)"""

    # Digital Input connection parameters

    # Operator start buttons (B-contact/Normally Closed)
    operator_start_button_left: int = 8
    operator_start_button_right: int = 9

    # Safety sensor parameters
    # Sensor to verify product is safely clamped
    dut_clamp_safety_sensor: int = 10
    # Sensor to verify product is properly chained for safe operation
    dut_chain_safety_sensor: int = 11

    # Sensor to verifty that safety door is closed
    safety_door_closed_sensor: int = 12

    # emergency stop button
    emergency_stop_button: int = 3

    # Digital Output parameters

    servo1_brake_release: int = 1
    tower_lamp_red: int = 4
    tower_lamp_yellow: int = 5
    tower_lamp_green: int = 6
    beep: int = 7


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
    digital_io: DigitalIOConfig = field(default_factory=DigitalIOConfig)

    def __post_init__(self) -> None:
        """Validate configuration after initialization"""
        self._validate_robot_config()
        self._validate_communication_configs()
        self._validate_power_config()

    def _validate_robot_config(self) -> None:
        """Validate robot configuration parameters"""
        if self.robot.axis_id < 0:
            raise ValidationException(
                "robot.axis_id",
                self.robot.axis_id,
                "Axis ID cannot be negative",
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

        # Digital IO validation - no additional validation needed for pin assignments

    def _validate_power_config(self) -> None:
        """Validate power supply configuration parameters"""
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
            "digital_io": self.digital_io,
        }

        # Apply overrides
        current_values.update(overrides)

        # Handle nested config overrides
        for config_name in [
            "robot",
            "loadcell",
            "mcu",
            "power",
            "digital_io",
        ]:
            if config_name in overrides and isinstance(overrides[config_name], dict):
                # Get the appropriate config class
                config_class = {
                    "robot": RobotConfig,
                    "loadcell": LoadCellConfig,
                    "mcu": MCUConfig,
                    "power": PowerConfig,
                    "digital_io": DigitalIOConfig,
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
            digital_io=cast(
                DigitalIOConfig,
                current_values.get("digital_io", self.digital_io),
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation"""
        return {
            "robot": {
                "axis_id": self.robot.axis_id,
                "irq_no": self.robot.irq_no,
                "velocity": self.robot.velocity,
                "acceleration": self.robot.acceleration,
                "deceleration": self.robot.deceleration,
            },
            "loadcell": {
                "port": self.loadcell.port,
                "baudrate": self.loadcell.baudrate,
                "timeout": self.loadcell.timeout,
                "bytesize": self.loadcell.bytesize,
                "stopbits": self.loadcell.stopbits,
                "parity": self.loadcell.parity,
                "indicator_id": self.loadcell.indicator_id,
            },
            "mcu": {
                "port": self.mcu.port,
                "baudrate": self.mcu.baudrate,
                "timeout": self.mcu.timeout,
                "bytesize": self.mcu.bytesize,
                "stopbits": self.mcu.stopbits,
                "parity": self.mcu.parity,
            },
            "power": {
                "host": self.power.host,
                "port": self.power.port,
                "timeout": self.power.timeout,
                "channel": self.power.channel,
                "delimiter": self.power.delimiter,
            },
            "digital_io": {
                "operator_start_button_left": self.digital_io.operator_start_button_left,
                "operator_start_button_right": self.digital_io.operator_start_button_right,
                "tower_lamp_red": self.digital_io.tower_lamp_red,
                "tower_lamp_yellow": self.digital_io.tower_lamp_yellow,
                "tower_lamp_green": self.digital_io.tower_lamp_green,
                "beep": self.digital_io.beep,
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
            "digital_io": DigitalIOConfig,
        }

        for (
            config_name,
            config_class,
        ) in config_classes.items():
            if config_name in data_copy and isinstance(data_copy[config_name], dict):
                # Handle special nested configs

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
            digital_io=cast(
                DigitalIOConfig,
                data_copy.get("digital_io", DigitalIOConfig()),
            ),
        )

    def __str__(self) -> str:
        return "HardwareConfig(robot/loadcell/mcu/power/digital_io)"

    def __repr__(self) -> str:
        return (
            f"HardwareConfiguration(robot={self.robot}, loadcell={self.loadcell}, "
            f"mcu={self.mcu}, power={self.power}, digital_io={self.digital_io})"
        )
