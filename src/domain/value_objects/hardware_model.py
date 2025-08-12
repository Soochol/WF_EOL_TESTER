"""
Hardware Model Value Object

Defines hardware model specifications for different hardware types.
This immutable value object specifies which hardware implementations to use
for each component (mock vs real hardware models).
"""

from dataclasses import dataclass
from typing import Any, Dict, Set

from domain.exceptions.validation_exceptions import ValidationException

# Supported hardware models
SUPPORTED_ROBOT_MODELS: Set[str] = {"AJINEXTEK", "mock"}
SUPPORTED_LOADCELL_MODELS: Set[str] = {"BS205", "mock"}
SUPPORTED_MCU_MODELS: Set[str] = {"LMA", "mock"}
SUPPORTED_POWER_MODELS: Set[str] = {"ODA", "mock"}
SUPPORTED_DIGITAL_IO_MODELS: Set[str] = {"AJINEXTEK", "mock"}


@dataclass(frozen=True)
class HardwareModel:
    """
    Hardware model specification value object

    This immutable value object represents which hardware models to use
    for each hardware component. It determines the appropriate service
    implementation (mock vs real hardware) without detailed configuration.
    
    Each field specifies the model type for the corresponding hardware component:
    - "mock": Use mock/simulation implementation for development/testing
    - Hardware-specific model: Use real hardware implementation (e.g., "AJINEXTEK", "LMA")
    """

    # Hardware model specifications
    robot: str = "mock"       # Robot controller model: "mock", "AJINEXTEK"
    mcu: str = "mock"         # MCU/Temperature controller model: "mock", "LMA"
    loadcell: str = "mock"    # Load cell model: "mock", "BS205"
    power: str = "mock"       # Power supply model: "mock", "ODA"
    digital_io: str = "mock"  # Digital I/O interface model: "mock", "AJINEXTEK"
    
    def __post_init__(self) -> None:
        """Validate hardware model specifications after initialization"""
        self._validate_models()
    
    def _validate_models(self) -> None:
        """Validate that all specified models are supported"""
        model_validations = [
            ("robot", self.robot, SUPPORTED_ROBOT_MODELS),
            ("mcu", self.mcu, SUPPORTED_MCU_MODELS),
            ("loadcell", self.loadcell, SUPPORTED_LOADCELL_MODELS),
            ("power", self.power, SUPPORTED_POWER_MODELS),
            ("digital_io", self.digital_io, SUPPORTED_DIGITAL_IO_MODELS),
        ]
        
        for component, model, supported_models in model_validations:
            if model not in supported_models:
                raise ValidationException(
                    f"hardware_model.{component}",
                    model,
                    f"Unsupported {component} model. Supported: {', '.join(sorted(supported_models))}",
                )

    def to_dict(self) -> Dict[str, str]:
        """Convert hardware model to dictionary representation
        
        Returns:
            Dictionary with hardware component models
        """
        return {
            "robot": self.robot,
            "mcu": self.mcu,
            "loadcell": self.loadcell,
            "power": self.power,
            "digital_io": self.digital_io,
        }

    def to_structured_dict(self) -> Dict[str, Any]:
        """Convert hardware model to structured dictionary for better YAML readability
        
        Returns:
            Nested dictionary structure suitable for YAML configuration files
        """
        return {
            "hardware_model": self.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HardwareModel":
        """
        Create hardware model from dictionary

        Args:
            data: Dictionary containing hardware model specifications

        Returns:
            HardwareModel instance with validated models
            
        Raises:
            ValidationException: If any specified models are unsupported
        """
        return cls(
            robot=data.get("robot", "mock"),
            mcu=data.get("mcu", "mock"),
            loadcell=data.get("loadcell", "mock"),
            power=data.get("power", "mock"),
            digital_io=data.get("digital_io", "mock"),
        )
    
    @classmethod
    def from_structured_dict(cls, data: Dict[str, Any]) -> "HardwareModel":
        """
        Create hardware model from structured dictionary (with hardware_model key)
        
        Args:
            data: Structured dictionary containing hardware_model section
            
        Returns:
            HardwareModel instance
            
        Raises:
            ValidationException: If structure is invalid or models are unsupported
        """
        if "hardware_model" not in data:
            raise ValidationException(
                "hardware_model",
                "missing",
                "Missing 'hardware_model' section in structured data",
            )
            
        return cls.from_dict(data["hardware_model"])

    def is_mock_mode(self) -> bool:
        """Check if all hardware components are set to mock mode
        
        Returns:
            True if all components use mock implementations
        """
        return all([
            self.robot == "mock",
            self.mcu == "mock",
            self.loadcell == "mock",
            self.power == "mock",
            self.digital_io == "mock"
        ])

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
            "robot": self.robot,
            "mcu": self.mcu,
            "loadcell": self.loadcell,
            "power": self.power,
            "digital_io": self.digital_io,
        }
        
        for component, model in components.items():
            if model != "mock":
                real_components[component] = model
                
        return real_components
    
    def is_valid(self) -> bool:
        """Check if hardware model configuration is valid
        
        Returns:
            True if all validation rules pass, False otherwise
        """
        try:
            self._validate_models()
            return True
        except ValidationException:
            return False

    def __str__(self) -> str:
        """Human-readable string representation"""
        mode = "Mock Mode" if self.is_mock_mode() else "Mixed/Real Hardware"
        return f"HardwareModel({mode}: robot={self.robot}, mcu={self.mcu}, loadcell={self.loadcell}, power={self.power}, digital_io={self.digital_io})"

    def __repr__(self) -> str:
        """Debug representation"""
        return f"HardwareModel(robot={self.robot!r}, mcu={self.mcu!r}, loadcell={self.loadcell!r}, power={self.power!r}, digital_io={self.digital_io!r})"