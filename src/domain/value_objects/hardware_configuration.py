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
class DigitalPin:
    """Configuration for a single digital I/O pin with contact type and edge detection"""

    pin_number: int  # Hardware pin number
    contact_type: str  # "A" (Normally Open) or "B" (Normally Closed)
    edge_type: str  # "rising", "falling", "both"
    name: str  # Human-readable name for logging/identification

    def __post_init__(self) -> None:
        """Validate pin configuration after initialization"""
        if self.pin_number < 0:
            raise ValidationException(
                "pin_number", self.pin_number, "Pin number cannot be negative"
            )

        if self.contact_type not in ["A", "B"]:
            raise ValidationException(
                "contact_type",
                self.contact_type,
                "Contact type must be 'A' (Normally Open) or 'B' (Normally Closed)",
            )

        if self.edge_type not in ["rising", "falling", "both"]:
            raise ValidationException(
                "edge_type", self.edge_type, "Edge type must be 'rising', 'falling', or 'both'"
            )

        if not self.name or not self.name.strip():
            raise ValidationException("name", self.name, "Pin name cannot be empty")


@dataclass(frozen=True)
class RobotConfig:
    """Robot controller configuration (AJINEXTEK)

    Configures connection parameters for the AJINEXTEK robot controller.
    Motion parameters are configured separately in TestConfiguration.
    """

    # Hardware connection parameters
    irq_no: int = 7  # Hardware interrupt number for AJINEXTEK controller
    axis_id: int = 0  # Robot axis identifier (typically 0 for single-axis systems)


@dataclass(frozen=True)
class LoadCellConfig:
    """Load Cell / Force Sensor configuration (BS205)

    Configures serial communication parameters and device settings
    for the BS205 load cell indicator.
    """

    # Serial communication parameters
    port: str = "COM8"  # Serial port (Windows: COMx, Linux: /dev/ttyUSBx)
    baudrate: int = 9600  # Communication speed (9600 bps for BS205)
    timeout: float = 1.0  # Read timeout in seconds

    # Serial protocol settings
    bytesize: int = 8  # Data bits (8-bit data)
    stopbits: int = 1  # Stop bits (1 stop bit)
    parity: Optional[str] = "even"  # Parity checking (even parity for BS205)

    # Device configuration
    indicator_id: int = 0  # Load cell indicator ID


@dataclass(frozen=True)
class MCUConfig:
    """MCU / Temperature Controller configuration (LMA)

    Configures serial communication parameters for the LMA
    temperature controller MCU.
    """

    # Serial communication parameters
    port: str = "COM10"  # Serial port (Windows: COMx, Linux: /dev/ttyUSBx)
    baudrate: int = 115200  # Communication speed (115200 bps for LMA)
    timeout: float = 60.0  # Read timeout in seconds (longer for complex operations)

    # Serial protocol settings
    bytesize: int = 8  # Data bits (8-bit data)
    stopbits: int = 1  # Stop bits (1 stop bit)
    parity: Optional[str] = None  # Parity checking (no parity for LMA)


@dataclass(frozen=True)
class PowerConfig:
    """Power Supply System configuration (ODA)

    Configures network connection parameters and device settings
    for the ODA power supply system.
    """

    # Network connection parameters
    host: str = "192.168.11.1"  # IP address of the power supply
    port: int = 5000  # TCP port for communication
    timeout: float = 5.0  # Connection timeout in seconds

    # Device configuration
    channel: int = 1  # Power supply channel to use

    # Communication protocol settings
    delimiter: Optional[str] = "\n"  # Command terminator (None = TCP driver handles)


@dataclass(frozen=True)
class DigitalIOConfig:
    """Digital I/O Interface configuration (AJINEXTEK)

    Configures digital input and output pin assignments for the
    AJINEXTEK digital I/O interface board using structured DigitalPin objects.
    """

    # ========================================================================
    # DIGITAL INPUT PINS (Structured with contact type and edge detection)
    # ========================================================================

    # Safety System Inputs
    emergency_stop_button: DigitalPin = field(
        default=DigitalPin(3, "A", "rising", "emergency_stop")
    )  # Emergency stop button (A-contact, rising edge = pressed)

    safety_door_closed_sensor: DigitalPin = field(
        default=DigitalPin(10, "B", "rising", "door_sensor")
    )  # Safety door closed verification sensor (A-contact, rising = closed)

    dut_clamp_safety_sensor: DigitalPin = field(
        default=DigitalPin(14, "A", "rising", "clamp_sensor")
    )  # DUT clamping safety verification sensor (A-contact, rising = clamped)

    dut_chain_safety_sensor: DigitalPin = field(
        default=DigitalPin(15, "A", "rising", "chain_sensor")
    )  # DUT chain safety verification sensor (A-contact, rising = chained)

    # Operator Control Inputs (B-contact/Normally Closed)
    operator_start_button_left: DigitalPin = field(
        default=DigitalPin(8, "B", "falling", "left_button")
    )  # Left operator start button (B-contact, falling edge = pressed)

    operator_start_button_right: DigitalPin = field(
        default=DigitalPin(9, "B", "falling", "right_button")
    )  # Right operator start button (B-contact, falling edge = pressed)

    # ========================================================================
    # DIGITAL OUTPUT PINS (Simple pin numbers - outputs don't need edge detection)
    # ========================================================================

    # Motion Control Outputs
    servo1_brake_release: int = 0  # Servo brake release control

    # Status Indicator Outputs
    tower_lamp_red: int = 4  # Red warning/error light
    tower_lamp_yellow: int = 5  # Yellow caution/processing light
    tower_lamp_green: int = 6  # Green ready/success light
    beep: int = 7  # Audio signal output

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DigitalIOConfig":
        """
        Create DigitalIOConfig from dictionary
        
        Args:
            data: Dictionary containing digital I/O configuration
            
        Returns:
            DigitalIOConfig instance
        """
        # Helper function to create DigitalPin from dict or use default
        def create_digital_pin(pin_data: Any, default_pin: DigitalPin) -> DigitalPin:
            if isinstance(pin_data, dict):
                return DigitalPin(
                    pin_number=pin_data.get("pin_number", default_pin.pin_number),
                    contact_type=pin_data.get("contact_type", default_pin.contact_type),
                    edge_type=pin_data.get("edge_type", default_pin.edge_type),
                    name=pin_data.get("name", default_pin.name),
                )
            return default_pin

        # Create default instance to get default values
        defaults = cls()

        return cls(
            emergency_stop_button=create_digital_pin(
                data.get("emergency_stop_button"), defaults.emergency_stop_button
            ),
            safety_door_closed_sensor=create_digital_pin(
                data.get("safety_door_closed_sensor"), defaults.safety_door_closed_sensor
            ),
            dut_clamp_safety_sensor=create_digital_pin(
                data.get("dut_clamp_safety_sensor"), defaults.dut_clamp_safety_sensor
            ),
            dut_chain_safety_sensor=create_digital_pin(
                data.get("dut_chain_safety_sensor"), defaults.dut_chain_safety_sensor
            ),
            operator_start_button_left=create_digital_pin(
                data.get("operator_start_button_left"), defaults.operator_start_button_left
            ),
            operator_start_button_right=create_digital_pin(
                data.get("operator_start_button_right"), defaults.operator_start_button_right
            ),
            servo1_brake_release=data.get("servo1_brake_release", defaults.servo1_brake_release),
            tower_lamp_red=data.get("tower_lamp_red", defaults.tower_lamp_red),
            tower_lamp_yellow=data.get("tower_lamp_yellow", defaults.tower_lamp_yellow),
            tower_lamp_green=data.get("tower_lamp_green", defaults.tower_lamp_green),
            beep=data.get("beep", defaults.beep),
        )


@dataclass(frozen=True)
class HardwareConfiguration:
    """
    Hardware configuration value object containing all device connection parameters

    This immutable value object represents the complete hardware system configuration,
    including connection parameters for all devices: robot controller, load cell,
    MCU temperature controller, power supply, and digital I/O interface.

    Each hardware device has its own configuration section with device-specific
    connection and communication parameters.
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
        self._validate_loadcell_config()
        self._validate_mcu_config()
        # Digital IO validation - pin assignments are validated implicitly by dataclass

    def _validate_loadcell_config(self) -> None:
        """Validate LoadCell configuration parameters"""
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
        self._validate_serial_params(
            "loadcell", self.loadcell.bytesize, self.loadcell.stopbits, self.loadcell.parity
        )

    def _validate_mcu_config(self) -> None:
        """Validate MCU configuration parameters"""
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
        self._validate_serial_params("mcu", self.mcu.bytesize, self.mcu.stopbits, self.mcu.parity)

    def _validate_serial_params(
        self, device_name: str, bytesize: int, stopbits: int, parity: Optional[str]
    ) -> None:
        """Validate serial communication parameters"""
        if bytesize not in [5, 6, 7, 8]:
            raise ValidationException(
                f"{device_name}.bytesize",
                bytesize,
                "Bytesize must be 5, 6, 7, or 8",
            )

        if stopbits not in [1, 2]:
            raise ValidationException(
                f"{device_name}.stopbits",
                stopbits,
                "Stopbits must be 1 or 2",
            )

        if parity is not None and parity.lower() not in [
            "none",
            "even",
            "odd",
            "mark",
            "space",
        ]:
            raise ValidationException(
                f"{device_name}.parity",
                parity,
                "Parity must be None, 'none', 'even', 'odd', 'mark', or 'space'",
            )

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
        config_classes = {
            "robot": RobotConfig,
            "loadcell": LoadCellConfig,
            "mcu": MCUConfig,
            "power": PowerConfig,
            "digital_io": DigitalIOConfig,
        }

        for config_name, config_class in config_classes.items():
            if config_name in overrides and isinstance(overrides[config_name], dict):
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
                # Input pins with structured configuration
                "emergency_stop_button": {
                    "pin_number": self.digital_io.emergency_stop_button.pin_number,
                    "contact_type": self.digital_io.emergency_stop_button.contact_type,
                    "edge_type": self.digital_io.emergency_stop_button.edge_type,
                    "name": self.digital_io.emergency_stop_button.name,
                },
                "operator_start_button_left": {
                    "pin_number": self.digital_io.operator_start_button_left.pin_number,
                    "contact_type": self.digital_io.operator_start_button_left.contact_type,
                    "edge_type": self.digital_io.operator_start_button_left.edge_type,
                    "name": self.digital_io.operator_start_button_left.name,
                },
                "operator_start_button_right": {
                    "pin_number": self.digital_io.operator_start_button_right.pin_number,
                    "contact_type": self.digital_io.operator_start_button_right.contact_type,
                    "edge_type": self.digital_io.operator_start_button_right.edge_type,
                    "name": self.digital_io.operator_start_button_right.name,
                },
                "safety_door_closed_sensor": {
                    "pin_number": self.digital_io.safety_door_closed_sensor.pin_number,
                    "contact_type": self.digital_io.safety_door_closed_sensor.contact_type,
                    "edge_type": self.digital_io.safety_door_closed_sensor.edge_type,
                    "name": self.digital_io.safety_door_closed_sensor.name,
                },
                "dut_clamp_safety_sensor": {
                    "pin_number": self.digital_io.dut_clamp_safety_sensor.pin_number,
                    "contact_type": self.digital_io.dut_clamp_safety_sensor.contact_type,
                    "edge_type": self.digital_io.dut_clamp_safety_sensor.edge_type,
                    "name": self.digital_io.dut_clamp_safety_sensor.name,
                },
                "dut_chain_safety_sensor": {
                    "pin_number": self.digital_io.dut_chain_safety_sensor.pin_number,
                    "contact_type": self.digital_io.dut_chain_safety_sensor.contact_type,
                    "edge_type": self.digital_io.dut_chain_safety_sensor.edge_type,
                    "name": self.digital_io.dut_chain_safety_sensor.name,
                },
                # Output pins (simple pin numbers)
                "servo1_brake_release": self.digital_io.servo1_brake_release,
                "tower_lamp_red": self.digital_io.tower_lamp_red,
                "tower_lamp_yellow": self.digital_io.tower_lamp_yellow,
                "tower_lamp_green": self.digital_io.tower_lamp_green,
                "beep": self.digital_io.beep,
            },
        }

    def to_structured_dict(self) -> Dict[str, Any]:
        """Convert configuration to structured dictionary representation for better YAML readability"""
        return {"hardware_config": self.to_dict()}

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

        for config_name, config_class in config_classes.items():
            if config_name in data_copy and isinstance(data_copy[config_name], dict):
                # Special handling for DigitalIOConfig which has a custom from_dict method
                if config_name == "digital_io":
                    data_copy[config_name] = DigitalIOConfig.from_dict(data_copy[config_name])
                else:
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
