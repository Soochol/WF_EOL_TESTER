"""
Hardware Model Value Object

Defines hardware model specifications for different hardware types.
This is separate from hardware configuration and focuses on model selection.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class HardwareModel:
    """
    Hardware model specification value object

    This immutable value object represents which hardware models to use
    for each hardware type. It's used to determine the appropriate
    service implementation without detailed configuration parameters.
    """

    # Hardware model specifications
    robot: str = "mock"  # "mock", "AJINEXTEK", etc.
    mcu: str = "mock"    # "mock", "LMA", etc.
    loadcell: str = "mock"  # "mock", "BS205", etc.
    power: str = "mock"     # "mock", "ODA", etc.
    digital_io: str = "mock"  # "mock", "AJINEXTEK", etc.

    def to_dict(self) -> Dict[str, Any]:
        """Convert hardware model to dictionary representation"""
        return {
            "robot": self.robot,
            "mcu": self.mcu,
            "loadcell": self.loadcell,
            "power": self.power,
            "digital_io": self.digital_io,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HardwareModel":
        """
        Create hardware model from dictionary

        Args:
            data: Dictionary containing hardware model specifications

        Returns:
            HardwareModel instance
        """
        return cls(
            robot=data.get("robot", "mock"),
            mcu=data.get("mcu", "mock"),
            loadcell=data.get("loadcell", "mock"),
            power=data.get("power", "mock"),
            digital_io=data.get("digital_io", "mock"),
        )

    def is_mock_mode(self) -> bool:
        """Check if all hardware is set to mock mode"""
        return all([
            self.robot == "mock",
            self.mcu == "mock",
            self.loadcell == "mock",
            self.power == "mock",
            self.digital_io == "mock"
        ])

    def is_real_hardware(self) -> bool:
        """Check if any real hardware is configured"""
        return not self.is_mock_mode()

    def __str__(self) -> str:
        """String representation"""
        return f"HardwareModel(robot={self.robot}, mcu={self.mcu}, loadcell={self.loadcell}, power={self.power}, digital_io={self.digital_io})"

    def __repr__(self) -> str:
        """Debug representation"""
        return self.__str__()