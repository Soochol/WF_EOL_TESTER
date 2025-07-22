"""
Hardware Device Entity

Represents a hardware device (controller) used in the EOL testing system.
"""

from typing import Dict, Any, Optional
from ..enums.hardware_status import HardwareStatus
from ..value_objects.time_values import Timestamp
from ..exceptions.validation_exceptions import ValidationException
from ..exceptions.business_rule_exceptions import BusinessRuleViolationException


class HardwareDevice:
    """Hardware device entity representing test equipment"""
    
    def __init__(
        self,
        device_type: str,
        vendor: str,
        connection_info: str,
        device_id: Optional[str] = None,
        model: Optional[str] = None,
        firmware_version: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize hardware device
        
        Args:
            device_type: Type of device (e.g., 'loadcell', 'power_supply', 'dio')
            vendor: Device vendor/manufacturer
            connection_info: Connection details (port, IP, etc.)
            device_id: Unique device identifier
            model: Device model number
            firmware_version: Firmware version
            capabilities: Device capabilities and specifications
            
        Raises:
            ValidationException: If required fields are invalid
        """
        self._validate_required_fields(device_type, vendor, connection_info)
        
        self._device_type = device_type.lower().strip()
        self._vendor = vendor.strip()
        self._connection_info = connection_info.strip()
        self._device_id = device_id.strip() if device_id else None
        self._model = model.strip() if model else None
        self._firmware_version = firmware_version.strip() if firmware_version else None
        self._capabilities = capabilities or {}
        
        # Device state
        self._status = HardwareStatus.DISCONNECTED
        self._last_status_change = Timestamp.now()
        self._error_message: Optional[str] = None
        self._connection_count = 0
        self._last_activity: Optional[Timestamp] = None
        
        self._created_at = Timestamp.now()
    
    def _validate_required_fields(self, device_type: str, vendor: str, connection_info: str) -> None:
        """Validate required fields"""
        if not device_type or not device_type.strip():
            raise ValidationException("device_type", device_type, "Device type is required")
        
        if not vendor or not vendor.strip():
            raise ValidationException("vendor", vendor, "Vendor is required")
        
        if not connection_info or not connection_info.strip():
            raise ValidationException("connection_info", connection_info, "Connection info is required")
        
        # Validate device type
        valid_device_types = {
            'loadcell', 'power_supply', 'dio', 'mcu', 'robot', 
            'multimeter', 'oscilloscope', 'function_generator'
        }
        if device_type.lower().strip() not in valid_device_types:
            raise ValidationException(
                "device_type", 
                device_type, 
                f"Device type must be one of: {', '.join(valid_device_types)}"
            )
    
    @property
    def device_type(self) -> str:
        """Get device type"""
        return self._device_type
    
    @property
    def vendor(self) -> str:
        """Get vendor"""
        return self._vendor
    
    @property
    def connection_info(self) -> str:
        """Get connection info"""
        return self._connection_info
    
    @property
    def device_id(self) -> Optional[str]:
        """Get device ID"""
        return self._device_id
    
    @property
    def model(self) -> Optional[str]:
        """Get model"""
        return self._model
    
    @property
    def firmware_version(self) -> Optional[str]:
        """Get firmware version"""
        return self._firmware_version
    
    @property
    def capabilities(self) -> Dict[str, Any]:
        """Get device capabilities"""
        return self._capabilities.copy()
    
    @property
    def status(self) -> HardwareStatus:
        """Get current status"""
        return self._status
    
    @property
    def last_status_change(self) -> Timestamp:
        """Get timestamp of last status change"""
        return self._last_status_change
    
    @property
    def error_message(self) -> Optional[str]:
        """Get current error message"""
        return self._error_message
    
    @property
    def connection_count(self) -> int:
        """Get total connection count"""
        return self._connection_count
    
    @property
    def last_activity(self) -> Optional[Timestamp]:
        """Get timestamp of last activity"""
        return self._last_activity
    
    @property
    def created_at(self) -> Timestamp:
        """Get creation timestamp"""
        return self._created_at
    
    def set_status(self, status: HardwareStatus, error_message: Optional[str] = None) -> None:
        """
        Update device status
        
        Args:
            status: New status
            error_message: Error message if status is ERROR
            
        Raises:
            ValidationException: If status transition is invalid
        """
        if not isinstance(status, HardwareStatus):
            raise ValidationException("status", status, "Status must be HardwareStatus enum")
        
        # Validate status transitions
        if not self._is_valid_status_transition(self._status, status):
            raise BusinessRuleViolationException(
                "STATUS_TRANSITION",
                f"Invalid status transition from {self._status} to {status}",
                {
                    'current_status': self._status.value,
                    'requested_status': status.value,
                    'device_type': self._device_type
                }
            )
        
        old_status = self._status
        self._status = status
        self._last_status_change = Timestamp.now()
        
        if status == HardwareStatus.ERROR:
            self._error_message = error_message
        elif status == HardwareStatus.CONNECTED:
            self._error_message = None
            self._connection_count += 1
        
        self._record_activity()
    
    def _is_valid_status_transition(self, from_status: HardwareStatus, to_status: HardwareStatus) -> bool:
        """Check if status transition is valid"""
        # All transitions are allowed from DISCONNECTED
        if from_status == HardwareStatus.DISCONNECTED:
            return True
        
        # Can always go to ERROR or DISCONNECTED
        if to_status in (HardwareStatus.ERROR, HardwareStatus.DISCONNECTED):
            return True
        
        # Specific transitions
        valid_transitions = {
            HardwareStatus.CONNECTING: {HardwareStatus.CONNECTED, HardwareStatus.ERROR, HardwareStatus.DISCONNECTED},
            HardwareStatus.CONNECTED: {HardwareStatus.DISCONNECTED, HardwareStatus.ERROR},
            HardwareStatus.ERROR: {HardwareStatus.DISCONNECTED, HardwareStatus.CONNECTING},
            HardwareStatus.UNKNOWN: {HardwareStatus.DISCONNECTED, HardwareStatus.CONNECTING}
        }
        
        return to_status in valid_transitions.get(from_status, set())
    
    def _record_activity(self) -> None:
        """Record activity timestamp"""
        self._last_activity = Timestamp.now()
    
    def clear_error(self) -> None:
        """Clear error status and message"""
        if self._status == HardwareStatus.ERROR:
            self._status = HardwareStatus.DISCONNECTED
            self._error_message = None
            self._last_status_change = Timestamp.now()
    
    def get_capability(self, key: str, default: Any = None) -> Any:
        """Get specific capability value"""
        return self._capabilities.get(key, default)
    
    def update_capabilities(self, capabilities: Dict[str, Any]) -> None:
        """Update device capabilities"""
        if not isinstance(capabilities, dict):
            raise ValidationException("capabilities", capabilities, "Capabilities must be a dictionary")
        
        self._capabilities.update(capabilities)
        self._record_activity()
    
    def is_operational(self) -> bool:
        """Check if device is operational (can perform operations)"""
        return self._status.is_operational
    
    def requires_attention(self) -> bool:
        """Check if device requires attention"""
        return self._status.requires_attention
    
    def get_full_identifier(self) -> str:
        """Get full device identifier string"""
        parts = [self._vendor, self._device_type]
        if self._model:
            parts.append(self._model)
        if self._device_id:
            parts.append(f"ID:{self._device_id}")
        return "_".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert hardware device to dictionary representation"""
        return {
            'device_type': self._device_type,
            'vendor': self._vendor,
            'connection_info': self._connection_info,
            'device_id': self._device_id,
            'model': self._model,
            'firmware_version': self._firmware_version,
            'capabilities': self._capabilities,
            'status': self._status.value,
            'last_status_change': self._last_status_change.to_iso(),
            'error_message': self._error_message,
            'connection_count': self._connection_count,
            'last_activity': self._last_activity.to_iso() if self._last_activity else None,
            'created_at': self._created_at.to_iso()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HardwareDevice':
        """Create hardware device from dictionary representation"""
        device = cls(
            device_type=data['device_type'],
            vendor=data['vendor'],
            connection_info=data['connection_info'],
            device_id=data.get('device_id'),
            model=data.get('model'),
            firmware_version=data.get('firmware_version'),
            capabilities=data.get('capabilities', {})
        )
        
        # Restore state
        device._status = HardwareStatus(data['status'])
        device._last_status_change = Timestamp.from_iso(data['last_status_change'])
        device._error_message = data.get('error_message')
        device._connection_count = data.get('connection_count', 0)
        
        if data.get('last_activity'):
            device._last_activity = Timestamp.from_iso(data['last_activity'])
        
        return device
    
    def __str__(self) -> str:
        status_info = f"({self._status.value})"
        if self._error_message:
            status_info = f"({self._status.value}: {self._error_message})"
        
        return f"{self._vendor} {self._device_type} {status_info}"
    
    def __repr__(self) -> str:
        return f"HardwareDevice(type={self._device_type}, vendor={self._vendor}, status={self._status.value})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, HardwareDevice):
            return False
        return (self._device_type == other._device_type and 
                self._vendor == other._vendor and 
                self._connection_info == other._connection_info)
    
    def __hash__(self) -> int:
        return hash((self._device_type, self._vendor, self._connection_info))