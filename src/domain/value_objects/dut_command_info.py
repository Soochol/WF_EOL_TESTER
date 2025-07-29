"""
DUT Command Information

Value object for DUT information in command objects.
Represents basic DUT data needed for command execution.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from domain.exceptions.validation_exceptions import ValidationException


@dataclass(frozen=True)
class DUTCommandInfo:
    """DUT information for command objects"""

    dut_id: str
    model_number: str
    serial_number: str
    manufacturer: str = "Unknown"

    def __post_init__(self):
        """Validate DUT command info after initialization"""
        self._validate_fields()

    def _validate_fields(self) -> None:
        """Validate required fields"""
        if not self.dut_id or not self.dut_id.strip():
            raise ValidationException("dut_id", self.dut_id, "DUT ID is required")

        if not self.model_number or not self.model_number.strip():
            raise ValidationException("model_number", self.model_number, "Model number is required")

        if not self.serial_number or not self.serial_number.strip():
            raise ValidationException(
                "serial_number", self.serial_number, "Serial number is required"
            )

        if not self.manufacturer or not self.manufacturer.strip():
            raise ValidationException("manufacturer", self.manufacturer, "Manufacturer is required")

        # Length validations
        if len(self.dut_id.strip()) > 50:
            raise ValidationException("dut_id", self.dut_id, "DUT ID too long (max 50 characters)")

        if len(self.model_number.strip()) > 100:
            raise ValidationException(
                "model_number", self.model_number, "Model number too long (max 100 characters)"
            )

        if len(self.serial_number.strip()) > 50:
            raise ValidationException(
                "serial_number", self.serial_number, "Serial number too long (max 50 characters)"
            )

        if len(self.manufacturer.strip()) > 100:
            raise ValidationException(
                "manufacturer", self.manufacturer, "Manufacturer name too long (max 100 characters)"
            )

    def get_full_identifier(self) -> str:
        """Get full device identifier string"""
        return f"{self.manufacturer}_{self.model_number}_{self.serial_number}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "dut_id": self.dut_id,
            "model_number": self.model_number,
            "serial_number": self.serial_number,
            "manufacturer": self.manufacturer,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DUTCommandInfo":
        """Create DUTCommandInfo from dictionary"""
        return cls(
            dut_id=data["dut_id"],
            model_number=data["model_number"],
            serial_number=data["serial_number"],
            manufacturer=data.get("manufacturer", "Unknown"),
        )

    def __str__(self) -> str:
        return f"{self.manufacturer} {self.model_number} (SN: {self.serial_number})"
