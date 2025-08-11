"""
Device Under Test (DUT) Entity

Represents a device being tested in the EOL testing system.
"""

from typing import Any, Dict, Optional

from domain.exceptions.validation_exceptions import (
    ValidationException,
)
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.identifiers import DUTId
from domain.value_objects.time_values import Timestamp


class DUT:
    """Device Under Test entity"""

    def __init__(
        self,
        dut_id: DUTId,
        model_number: str,
        serial_number: str,
        manufacturer: str = "Unknown",
        firmware_version: Optional[str] = None,
        hardware_revision: Optional[str] = None,
        manufacturing_date: Optional[Timestamp] = None,
        specifications: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize DUT entity

        Args:
            dut_id: Unique identifier for this DUT
            model_number: Model/part number
            serial_number: Serial number
            manufacturer: Manufacturer name
            firmware_version: Firmware version if applicable
            hardware_revision: Hardware revision if applicable
            manufacturing_date: When device was manufactured
            specifications: Device specifications and limits

        Raises:
            ValidationException: If required fields are invalid
        """
        self._validate_required_fields(
            dut_id,
            model_number,
            serial_number,
            manufacturer,
        )

        self._dut_id = dut_id
        self._model_number = model_number.strip()
        self._serial_number = serial_number.strip()
        self._manufacturer = manufacturer.strip()
        self._firmware_version = firmware_version.strip() if firmware_version else None
        self._hardware_revision = hardware_revision.strip() if hardware_revision else None
        self._manufacturing_date = manufacturing_date
        self._specifications = specifications or {}
        self._created_at = Timestamp.now()

    def _validate_required_fields(
        self,
        dut_id: DUTId,
        model_number: str,
        serial_number: str,
        manufacturer: str,
    ) -> None:
        """Validate required fields"""
        if not isinstance(dut_id, DUTId):
            raise ValidationException(
                "dut_id",
                dut_id,
                "DUT ID must be DUTId instance",
            )

        if not model_number or not model_number.strip():
            raise ValidationException(
                "model_number",
                model_number,
                "Model number is required",
            )

        if not serial_number or not serial_number.strip():
            raise ValidationException(
                "serial_number",
                serial_number,
                "Serial number is required",
            )

        if not manufacturer or not manufacturer.strip():
            raise ValidationException(
                "manufacturer",
                manufacturer,
                "Manufacturer is required",
            )

        # Model number validation
        if len(model_number.strip()) > 100:
            raise ValidationException(
                "model_number",
                model_number,
                "Model number too long (max 100 characters)",
            )

        # Serial number validation
        if len(serial_number.strip()) > 50:
            raise ValidationException(
                "serial_number",
                serial_number,
                "Serial number too long (max 50 characters)",
            )

    @property
    def dut_id(self) -> DUTId:
        """Get DUT identifier"""
        return self._dut_id

    @property
    def model_number(self) -> str:
        """Get model number"""
        return self._model_number

    @property
    def serial_number(self) -> str:
        """Get serial number"""
        return self._serial_number

    @property
    def manufacturer(self) -> str:
        """Get manufacturer"""
        return self._manufacturer

    @property
    def firmware_version(self) -> Optional[str]:
        """Get firmware version"""
        return self._firmware_version

    @property
    def hardware_revision(self) -> Optional[str]:
        """Get hardware revision"""
        return self._hardware_revision

    @property
    def manufacturing_date(self) -> Optional[Timestamp]:
        """Get manufacturing date"""
        return self._manufacturing_date

    @property
    def specifications(self) -> Dict[str, Any]:
        """Get device specifications"""
        return self._specifications.copy()

    @property
    def created_at(self) -> Timestamp:
        """Get creation timestamp"""
        return self._created_at

    def get_specification(self, key: str, default: Any = None) -> Any:
        """Get specific specification value"""
        return self._specifications.get(key, default)

    def update_specifications(self, specifications: Dict[str, Any]) -> None:
        """Update device specifications"""
        if not isinstance(specifications, dict):
            raise ValidationException(
                "specifications",
                specifications,
                "Specifications must be a dictionary",
            )

        self._specifications.update(specifications)

    def get_full_identifier(self) -> str:
        """Get full device identifier string"""
        return f"{self._manufacturer}_{self._model_number}_{self._serial_number}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert DUT to dictionary representation"""
        return {
            "dut_id": str(self._dut_id),
            "model_number": self._model_number,
            "serial_number": self._serial_number,
            "manufacturer": self._manufacturer,
            "firmware_version": self._firmware_version,
            "hardware_revision": self._hardware_revision,
            "manufacturing_date": (
                self._manufacturing_date.to_iso() if self._manufacturing_date else None
            ),
            "specifications": self._specifications,
            "created_at": self._created_at.to_iso(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DUT":
        """Create DUT from dictionary representation"""
        manufacturing_date = None
        if data.get("manufacturing_date"):
            manufacturing_date = Timestamp.from_iso(data["manufacturing_date"])

        return cls(
            dut_id=DUTId(data["dut_id"]),
            model_number=data["model_number"],
            serial_number=data["serial_number"],
            manufacturer=data["manufacturer"],
            firmware_version=data.get("firmware_version"),
            hardware_revision=data.get("hardware_revision"),
            manufacturing_date=manufacturing_date,
            specifications=data.get("specifications", {}),
        )

    @classmethod
    def from_command_info(cls, command_info: DUTCommandInfo) -> "DUT":
        """Create DUT from DUTCommandInfo

        Args:
            command_info: DUTCommandInfo instance

        Returns:
            DUT entity with data from command info
        """
        return cls(
            dut_id=DUTId(command_info.dut_id),
            model_number=command_info.model_number,
            serial_number=command_info.serial_number,
            manufacturer=command_info.manufacturer,
        )

    def __str__(self) -> str:
        return f"{self._manufacturer} {self._model_number} (SN: {self._serial_number})"

    def __repr__(self) -> str:
        return f"DUT(id={self._dut_id}, model={self._model_number}, sn={self._serial_number})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DUT):
            return False
        return self._dut_id == other._dut_id

    def __hash__(self) -> int:
        return hash(self._dut_id)
