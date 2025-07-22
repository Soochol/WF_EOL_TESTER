"""
BS205 Loadcell Controller Implementation

Simple, clean implementation focused on hardware control with delegated protocol handling.
"""

import time
from typing import Optional, Dict, Any
from enum import IntEnum

from loguru import logger

from .....domain.enums.hardware_status import HardwareStatus
from .constants import *
from .models import LoadcellResponse
from .protocol import BS205Protocol
from ..exceptions import BS205Error, BS205ConnectionError, BS205CommunicationError, BS205OperationError, BS205ValidationError
from .....driver.serial import SerialManager
# Serial exceptions are handled by the protocol layer
from .error_codes import validate_indicator_id


class LoadcellStatus(IntEnum):
    """Loadcell status enumeration"""
    IDLE = 0
    MEASURING = 1
    HOLD = 2
    ZERO_SETTING = 3
    ERROR = 4


class BS205Controller:
    """
    BS205 loadcell controller implementation
    
    Simple hardware controller for BS205 loadcell devices with delegated protocol handling.
    """

    def __init__(self, port: str, indicator_id: int = 1, baudrate: int = DEFAULT_BAUDRATE,
                 timeout: float = DEFAULT_TIMEOUT, parity: str = PARITY_NONE):
        """
        Initialize BS205 loadcell controller

        Args:
            port: Serial port (e.g., 'COM3', '/dev/ttyUSB0')
            indicator_id: Indicator ID for communication (1-255)
            baudrate: Baud rate (default: 9600)
            timeout: Communication timeout in seconds
            parity: Parity setting ('N', 'E', 'O')
        """
        # Controller base attributes
        self.controller_type = "loadcell"
        self.vendor = "bs205"
        self.connection_info = port
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        
        # Loadcell-specific attributes
        self.indicator_id = indicator_id
        self.current_status = LoadcellStatus.IDLE
        self.status_callback = None

        # Convert parity to serial driver format
        parity_map = {'N': 'N', 'E': 'E', 'O': 'O'}
        serial_parity = parity_map.get(parity, 'N')
        
        # Serial communication setup
        self.serial_manager = SerialManager()
        self.port = port
        self.baudrate = baudrate
        self.parity = serial_parity
        self.timeout = timeout
        
        # Protocol handler
        self.protocol = BS205Protocol(self.serial_manager)
        
        # Status tracking
        self.hold_enabled = False
        self.last_response: Optional[LoadcellResponse] = None
    
    def set_status_callback(self, callback) -> None:
        """Set status update callback"""
        self.status_callback = callback
    
    def _notify_status_change(self, status: LoadcellStatus, data=None) -> None:
        """Notify status change to callback"""
        self.current_status = status
        if self.status_callback:
            try:
                self.status_callback(status, data or {})
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

    def connect(self) -> None:
        """Connect to loadcell controller (exception-first design)"""
        try:
            self.serial_manager.connect(self.port, baudrate=self.baudrate, timeout=self.timeout, parity=self.parity)
            logger.info(f"Connected to loadcell controller at {self.connection_info} "
                      f"(ID: {self.indicator_id})")
            self.status = HardwareStatus.CONNECTED
            self.current_status = LoadcellStatus.IDLE

        except BS205Error:
            # Re-raise BS205 specific errors to preserve error context and debugging info
            self.status = HardwareStatus.DISCONNECTED
            raise
        except Exception as e:
            logger.error(f"Connection error ({type(e).__name__}): {e}")
            self.status = HardwareStatus.DISCONNECTED
            raise BS205ConnectionError(f"Connection error: {e}", port=self.connection_info)

    def disconnect(self) -> None:
        """Disconnect from loadcell controller"""
        try:
            self.serial_manager.disconnect()
            logger.info("Disconnected from loadcell controller")
        except Exception as e:
            # Disconnect errors are logged but not re-raised (best-effort cleanup)
            logger.error(f"Failed to disconnect from loadcell controller: {e}")
        finally:
            self.status = HardwareStatus.DISCONNECTED

    def is_alive(self) -> bool:
        """Check if connection is alive"""
        return self.is_connected() and self.serial_manager.is_connected()

    def is_connected(self) -> bool:
        """Check if hardware is connected (consistent with mock)"""
        return self.status == HardwareStatus.CONNECTED

    def read_value(self) -> float:
        """Read current loadcell value immediately (exception-first design)"""
        if not self.is_connected():
            raise BS205ConnectionError("Not connected to loadcell controller", port=self.connection_info)

        try:
            logger.debug(f"Reading value from loadcell (ID: {self.indicator_id}, timeout: {self.timeout}s)")
            response = self.protocol.read_value(self.indicator_id, self.timeout)
            
            if response and response.is_valid:
                self.last_response = response
                logger.debug(f"Successfully read value: {response.value} (ID: {response.indicator_id}, sign: {response.sign})")
                return response.value
            else:
                error_msg = f"Invalid response from loadcell (ID: {self.indicator_id})"
                if response:
                    error_msg += f" - received response but invalid: {response.raw_data}"
                else:
                    error_msg += " - no response received"
                logger.error(error_msg)
                raise BS205CommunicationError(error_msg, indicator_id=self.indicator_id)

        except BS205Error:
            # Re-raise BS205 specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Unexpected error during value read (ID: {self.indicator_id}): {type(e).__name__}: {e}")
            raise BS205OperationError(f"Read value error: {e}", indicator_id=self.indicator_id)

    def read_raw_data(self) -> str:
        """Read raw data string from loadcell (exception-first design)"""
        if not self.is_connected():
            raise BS205ConnectionError("Not connected to loadcell controller", port=self.connection_info)

        try:
            logger.debug(f"Reading raw data from loadcell (ID: {self.indicator_id})")
            response = self.protocol.read_value(self.indicator_id, self.timeout)
            
            if response and response.is_valid:
                self.last_response = response
                logger.debug(f"Successfully read raw data: '{response.raw_data}' (ID: {response.indicator_id})")
                return response.raw_data
            else:
                error_msg = f"Invalid raw data response from loadcell (ID: {self.indicator_id})"
                if response:
                    error_msg += f" - received: '{response.raw_data}'"
                else:
                    error_msg += " - no response received"
                logger.error(error_msg)
                raise BS205CommunicationError(error_msg, indicator_id=self.indicator_id)

        except BS205Error:
            # Re-raise BS205 specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Unexpected error during raw data read (ID: {self.indicator_id}): {type(e).__name__}: {e}")
            raise BS205OperationError(f"Read raw data error: {e}", indicator_id=self.indicator_id)

    def auto_zero(self) -> None:
        """Perform auto zero operation (exception-first design)"""
        if not self.is_connected():
            raise BS205ConnectionError("Cannot perform auto zero: not connected", port=self.connection_info)

        try:
            logger.info(f"Starting auto zero operation (ID: {self.indicator_id})")
            self._notify_status_change(LoadcellStatus.ZERO_SETTING)

            self.protocol.send_control_command(self.indicator_id, CMD_AUTO_ZERO)
            logger.info(f"Auto zero command sent successfully (ID: {self.indicator_id})")
            
            # Wait for operation to complete
            time.sleep(0.5)
            self._notify_status_change(LoadcellStatus.IDLE)
            logger.info(f"Auto zero operation completed (ID: {self.indicator_id})")

        except BS205Error:
            # Re-raise BS205 specific errors
            logger.error(f"BS205-specific error during auto zero (ID: {self.indicator_id})")
            self._notify_status_change(LoadcellStatus.ERROR)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during auto zero (ID: {self.indicator_id}): {type(e).__name__}: {e}")
            self._notify_status_change(LoadcellStatus.ERROR)
            raise BS205OperationError(f"Auto zero error: {e}", indicator_id=self.indicator_id)

    def set_hold(self, enable: bool) -> None:
        """Enable or disable hold function (exception-first design)"""
        if not self.is_connected():
            raise BS205ConnectionError("Cannot set hold: not connected", port=self.connection_info)

        try:
            action = "enable" if enable else "disable"
            logger.debug(f"Setting hold {action} (ID: {self.indicator_id})")
            
            command = CMD_HOLD_ON if enable else CMD_HOLD_OFF
            self.protocol.send_control_command(self.indicator_id, command)
            self.hold_enabled = enable
            logger.info(f"Hold {action}d successfully (ID: {self.indicator_id})")

            # Update status based on hold state
            status = LoadcellStatus.HOLD if enable else LoadcellStatus.IDLE
            self._notify_status_change(status)

        except BS205Error:
            # Re-raise BS205 specific errors to preserve error context and debugging info
            logger.error(f"BS205-specific error during hold {action} (ID: {self.indicator_id})")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during hold {action} (ID: {self.indicator_id}): {type(e).__name__}: {e}")
            raise BS205OperationError(f"Set hold error: {e}", indicator_id=self.indicator_id)

    def is_hold_enabled(self) -> Optional[bool]:
        """Check if hold function is enabled"""
        return self.hold_enabled

    def set_indicator_id(self, indicator_id: int) -> None:
        """Set indicator ID with validation (exception-first design)"""
        if not self.is_connected():
            raise BS205ConnectionError("Cannot set indicator ID: not connected", port=self.connection_info)

        try:
            # Validate ID range first
            logger.debug(f"Validating indicator ID {indicator_id}")
            validate_indicator_id(indicator_id)

            # Update ID
            old_id = self.indicator_id
            self.indicator_id = indicator_id
            logger.info(f"Indicator ID successfully changed from {old_id} to {indicator_id}")

        except BS205Error:
            # Re-raise BS205 specific errors to preserve error context and debugging info
            logger.error(f"BS205-specific error while setting indicator ID to {indicator_id}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error setting indicator ID to {indicator_id}: {type(e).__name__}: {e}")
            raise BS205ValidationError(f"Set indicator ID error: {e}",
                                     indicator_id=indicator_id, command="SET_INDICATOR_ID")

    def get_indicator_id(self) -> int:
        """Get current indicator ID"""
        return self.indicator_id

    def get_loadcell_status(self) -> LoadcellStatus:
        """Get current loadcell status"""
        return self.current_status

    def get_last_response(self) -> Optional[LoadcellResponse]:
        """Get last received response"""
        return self.last_response

    def flush_buffers(self) -> None:
        """Flush communication buffers"""
        self.serial_manager.flush_buffers()

    def get_port_info(self) -> Dict[str, Any]:
        """Get serial port information"""
        return self.serial_manager.get_stats()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, _exc_type: Optional[type], _exc_val: Optional[Exception], _exc_tb: Optional[Any]) -> bool:
        """Context manager exit"""
        # Always disconnect regardless of exception
        self.disconnect()
        # Return False to propagate any exceptions
        return False


# Convenience functions for common operations
def create_controller(port: str, indicator_id: int = 1, **kwargs) -> BS205Controller:
    """
    Create and configure BS205 loadcell controller

    Args:
        port: Serial port
        indicator_id: Indicator ID
        **kwargs: Additional configuration options

    Returns:
        BS205Controller: Configured controller instance
    """
    return BS205Controller(port, indicator_id, **kwargs)


