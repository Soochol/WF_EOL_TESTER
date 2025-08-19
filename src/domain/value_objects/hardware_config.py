"""
Unified Hardware Configuration Value Object

Consolidated configuration object containing both hardware model selection
and detailed connection parameters for all hardware devices.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set, cast

from domain.exceptions.validation_exceptions import (
    ValidationException,
)

# Supported hardware models
SUPPORTED_ROBOT_MODELS: Set[str] = {"ajinextek", "mock"}
SUPPORTED_LOADCELL_MODELS: Set[str] = {"bs205", "mock"}
SUPPORTED_MCU_MODELS: Set[str] = {"lma", "mock"}
SUPPORTED_POWER_MODELS: Set[str] = {"oda", "mock"}
SUPPORTED_DIGITAL_INPUT_MODELS: Set[str] = {
    "ajinextek",
    "mock",
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
    """Robot controller configuration with model selection and connection parameters"""

    # Hardware model selection
    model: str = "mock"  # "mock", "AJINEXTEK"

    # Hardware connection parameters
    irq_no: int = 7  # Hardware interrupt number for AJINEXTEK controller
    axis_id: int = 0  # Robot axis identifier (typically 0 for single-axis systems)

    # Optional additional parameters for compatibility with existing YAML
    timeout: float = 30.0  # Timeout for robot operations
    polling_interval: int = 250  # Polling interval in ms for motion

    def __post_init__(self) -> None:
        """Validate robot configuration after initialization"""
        if self.model not in SUPPORTED_ROBOT_MODELS:
            raise ValidationException(
                "robot.model",
                self.model,
                f"Unsupported robot model. Supported: {', '.join(sorted(SUPPORTED_ROBOT_MODELS))}",
            )

        if self.axis_id < 0:
            raise ValidationException(
                "robot.axis_id",
                self.axis_id,
                "Axis ID cannot be negative",
            )

        if self.irq_no < 0:
            raise ValidationException(
                "robot.irq_no",
                self.irq_no,
                "IRQ number cannot be negative",
            )


@dataclass(frozen=True)
class LoadCellConfig:
    """Load Cell / Force Sensor configuration with model selection and connection parameters"""

    # Hardware model selection
    model: str = "mock"  # "mock", "BS205"

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

    def __post_init__(self) -> None:
        """Validate loadcell configuration after initialization"""
        if self.model not in SUPPORTED_LOADCELL_MODELS:
            raise ValidationException(
                "loadcell.model",
                self.model,
                f"Unsupported loadcell model. Supported: {', '.join(sorted(SUPPORTED_LOADCELL_MODELS))}",
            )

        if not self.port:
            raise ValidationException(
                "loadcell.port",
                self.port,
                "LoadCell port cannot be empty",
            )

        if self.baudrate <= 0:
            raise ValidationException(
                "loadcell.baudrate",
                self.baudrate,
                "LoadCell baudrate must be positive",
            )

        if self.timeout <= 0:
            raise ValidationException(
                "loadcell.timeout",
                self.timeout,
                "LoadCell timeout must be positive",
            )

        if self.indicator_id < 0:
            raise ValidationException(
                "loadcell.indicator_id",
                self.indicator_id,
                "LoadCell indicator ID cannot be negative",
            )

        # Validate LoadCell serial parameters
        self._validate_serial_params()

    def _validate_serial_params(self) -> None:
        """Validate serial communication parameters"""
        if self.bytesize not in [5, 6, 7, 8]:
            raise ValidationException(
                "loadcell.bytesize",
                self.bytesize,
                "Bytesize must be 5, 6, 7, or 8",
            )

        if self.stopbits not in [1, 2]:
            raise ValidationException(
                "loadcell.stopbits",
                self.stopbits,
                "Stopbits must be 1 or 2",
            )

        if self.parity is not None and self.parity.lower() not in [
            "none",
            "even",
            "odd",
            "mark",
            "space",
        ]:
            raise ValidationException(
                "loadcell.parity",
                self.parity,
                "Parity must be None, 'none', 'even', 'odd', 'mark', or 'space'",
            )


@dataclass(frozen=True)
class MCUConfig:
    """MCU / Temperature Controller configuration with model selection and connection parameters"""

    # Hardware model selection
    model: str = "mock"  # "mock", "LMA"

    # Serial communication parameters
    port: str = "COM10"  # Serial port (Windows: COMx, Linux: /dev/ttyUSBx)
    baudrate: int = 115200  # Communication speed (115200 bps for LMA)
    timeout: float = 10.0  # Read timeout in seconds (longer for complex operations)

    # Serial protocol settings
    bytesize: int = 8  # Data bits (8-bit data)
    stopbits: int = 1  # Stop bits (1 stop bit)
    parity: Optional[str] = None  # Parity checking (no parity for LMA)

    def __post_init__(self) -> None:
        """Validate MCU configuration after initialization"""
        if self.model not in SUPPORTED_MCU_MODELS:
            raise ValidationException(
                "mcu.model",
                self.model,
                f"Unsupported MCU model. Supported: {', '.join(sorted(SUPPORTED_MCU_MODELS))}",
            )

        if not self.port:
            raise ValidationException(
                "mcu.port",
                self.port,
                "MCU port cannot be empty",
            )

        if self.baudrate <= 0:
            raise ValidationException(
                "mcu.baudrate",
                self.baudrate,
                "MCU baudrate must be positive",
            )

        if self.timeout <= 0:
            raise ValidationException(
                "mcu.timeout",
                self.timeout,
                "MCU timeout must be positive",
            )

        # Validate MCU serial parameters
        self._validate_serial_params()

    def _validate_serial_params(self) -> None:
        """Validate serial communication parameters"""
        if self.bytesize not in [5, 6, 7, 8]:
            raise ValidationException(
                "mcu.bytesize",
                self.bytesize,
                "Bytesize must be 5, 6, 7, or 8",
            )

        if self.stopbits not in [1, 2]:
            raise ValidationException(
                "mcu.stopbits",
                self.stopbits,
                "Stopbits must be 1 or 2",
            )

        if self.parity is not None and self.parity.lower() not in [
            "none",
            "even",
            "odd",
            "mark",
            "space",
        ]:
            raise ValidationException(
                "mcu.parity",
                self.parity,
                "Parity must be None, 'none', 'even', 'odd', 'mark', or 'space'",
            )


@dataclass(frozen=True)
class PowerConfig:
    """Power Supply System configuration with model selection and connection parameters"""

    # Hardware model selection
    model: str = "mock"  # "mock", "ODA"

    # Network connection parameters
    host: str = "192.168.11.1"  # IP address of the power supply
    port: int = 5000  # TCP port for communication
    timeout: float = 5.0  # Connection timeout in seconds

    # Device configuration
    channel: int = 1  # Power supply channel to use

    # Communication protocol settings
    delimiter: Optional[str] = "\n"  # Command terminator (None = TCP driver handles)

    def __post_init__(self) -> None:
        """Validate power configuration after initialization"""
        if self.model not in SUPPORTED_POWER_MODELS:
            raise ValidationException(
                "power.model",
                self.model,
                f"Unsupported power model. Supported: {', '.join(sorted(SUPPORTED_POWER_MODELS))}",
            )

        if not self.host:
            raise ValidationException(
                "power.host",
                self.host,
                "Power host cannot be empty",
            )

        if not 1 <= self.port <= 65535:
            raise ValidationException(
                "power.port",
                self.port,
                "Power port must be between 1 and 65535",
            )

        if self.timeout <= 0:
            raise ValidationException(
                "power.timeout",
                self.timeout,
                "Power timeout must be positive",
            )

        if self.channel <= 0:
            raise ValidationException(
                "power.channel",
                self.channel,
                "Power channel must be positive",
            )


@dataclass(frozen=True)
class DigitalIOConfig:
    """Digital I/O Interface configuration with model selection and pin assignments"""

    # Hardware model selection
    model: str = "mock"  # "mock", "AJINEXTEK"

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

    def __post_init__(self) -> None:
        """Validate digital I/O configuration after initialization"""
        if self.model not in SUPPORTED_DIGITAL_INPUT_MODELS:
            raise ValidationException(
                "digital_io.model",
                self.model,
                f"Unsupported digital I/O model. Supported: {', '.join(sorted(SUPPORTED_DIGITAL_INPUT_MODELS))}",
            )

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
            model=data.get("model", defaults.model),
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
class HardwareConfig:
    """
    Unified hardware configuration value object containing both model selection
    and detailed connection parameters for all hardware devices

    This immutable value object represents the complete hardware system configuration,
    including both which hardware models to use (mock vs real) and all device-specific
    connection and communication parameters.
    """

    robot: RobotConfig = field(default_factory=RobotConfig)
    loadcell: LoadCellConfig = field(default_factory=LoadCellConfig)
    mcu: MCUConfig = field(default_factory=MCUConfig)
    power: PowerConfig = field(default_factory=PowerConfig)
    digital_io: DigitalIOConfig = field(default_factory=DigitalIOConfig)

    def __post_init__(self) -> None:
        """Validate configuration after initialization"""
        # Individual component validation is handled by their __post_init__ methods

    def is_mock_mode(self) -> bool:
        """Check if all hardware components are set to mock mode

        Returns:
            True if all components use mock implementations
        """
        return all(
            [
                self.robot.model == "mock",
                self.loadcell.model == "mock",
                self.mcu.model == "mock",
                self.power.model == "mock",
                self.digital_io.model == "mock",
            ]
        )

    def is_real_hardware(self) -> bool:
        """Check if any real hardware components are configured

        Returns:
            True if at least one component uses real hardware implementation
        """
        return not self.is_mock_mode()

    def get_real_hardware_components(self) -> Dict[str, str]:
        """Get list of components using real hardware implementations

        Returns:
            Dictionary of component names and their real hardware models
        """
        real_components = {}
        components = {
            "robot": self.robot.model,
            "loadcell": self.loadcell.model,
            "mcu": self.mcu.model,
            "power": self.power.model,
            "digital_io": self.digital_io.model,
        }

        for component, model in components.items():
            if model != "mock":
                real_components[component] = model

        return real_components

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

    def with_overrides(self, **overrides: Any) -> "HardwareConfig":
        """
        Create new configuration with specific field overrides

        Args:
            **overrides: Field values to override

        Returns:
            New HardwareConfig instance with overridden values

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
                # Special handling for DigitalIOConfig which has a custom from_dict method
                if config_name == "digital_io":
                    current_values[config_name] = DigitalIOConfig.from_dict(overrides[config_name])
                else:
                    current_values[config_name] = config_class(**overrides[config_name])

        # Create new instance with properly typed config objects
        return HardwareConfig(
            robot=cast(RobotConfig, current_values.get("robot", self.robot)),
            loadcell=cast(LoadCellConfig, current_values.get("loadcell", self.loadcell)),
            mcu=cast(MCUConfig, current_values.get("mcu", self.mcu)),
            power=cast(PowerConfig, current_values.get("power", self.power)),
            digital_io=cast(DigitalIOConfig, current_values.get("digital_io", self.digital_io)),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation"""
        return {
            "robot": {
                "model": self.robot.model,
                "axis_id": self.robot.axis_id,
                "irq_no": self.robot.irq_no,
                "timeout": self.robot.timeout,
                "polling_interval": self.robot.polling_interval,
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
            },
            "mcu": {
                "model": self.mcu.model,
                "port": self.mcu.port,
                "baudrate": self.mcu.baudrate,
                "timeout": self.mcu.timeout,
                "bytesize": self.mcu.bytesize,
                "stopbits": self.mcu.stopbits,
                "parity": self.mcu.parity,
            },
            "power": {
                "model": self.power.model,
                "host": self.power.host,
                "port": self.power.port,
                "timeout": self.power.timeout,
                "channel": self.power.channel,
                "delimiter": self.power.delimiter,
            },
            "digital_io": {
                "model": self.digital_io.model,
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
        return {"hardware": self.to_dict()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HardwareConfig":
        """
        Create configuration from dictionary

        Args:
            data: Dictionary containing configuration values

        Returns:
            HardwareConfig instance

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
            robot=cast(RobotConfig, data_copy.get("robot", RobotConfig())),
            loadcell=cast(LoadCellConfig, data_copy.get("loadcell", LoadCellConfig())),
            mcu=cast(MCUConfig, data_copy.get("mcu", MCUConfig())),
            power=cast(PowerConfig, data_copy.get("power", PowerConfig())),
            digital_io=cast(DigitalIOConfig, data_copy.get("digital_io", DigitalIOConfig())),
        )

    @classmethod
    def from_structured_dict(cls, data: Dict[str, Any]) -> "HardwareConfig":
        """
        Create hardware config from structured dictionary (with hardware key)

        Args:
            data: Structured dictionary containing hardware section

        Returns:
            HardwareConfig instance

        Raises:
            ValidationException: If structure is invalid or models are unsupported
        """
        if "hardware" not in data:
            raise ValidationException(
                "hardware",
                "missing",
                "Missing 'hardware' section in structured data",
            )

        return cls.from_dict(data["hardware"])

    def __str__(self) -> str:
        """Human-readable string representation"""
        mode = "Mock Mode" if self.is_mock_mode() else "Mixed/Real Hardware"
        return f"HardwareConfig({mode}: robot={self.robot.model}, mcu={self.mcu.model}, loadcell={self.loadcell.model}, power={self.power.model}, digital_io={self.digital_io.model})"

    def __repr__(self) -> str:
        """Debug representation"""
        return (
            f"HardwareConfig(robot={self.robot}, loadcell={self.loadcell}, "
            f"mcu={self.mcu}, power={self.power}, digital_io={self.digital_io})"
        )
