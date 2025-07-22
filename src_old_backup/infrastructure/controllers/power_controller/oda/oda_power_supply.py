"""
ODA Power Supply Controller

This module provides high-level control for ODA power supplies using SCPI commands.
"""

from typing import Optional, Dict, Any, List

from loguru import logger

from ....domain.enums.hardware_status import HardwareStatus
from ..exceptions import ODAError, ODAConnectionError, ODAOperationError, ODACommunicationError
from .....driver.tcp import TCPCommunication, DEFAULT_PORT
from .constants import COMMANDS
from .error_codes import get_error_message, analyze_error, is_trip_error


class OdaPowerSupply:
    """ODA Power Supply controller using SCPI over TCP/IP"""

    def __init__(self, host: str, port: int = DEFAULT_PORT, timeout: float = 2.0):
        """
        Initialize ODA Power Supply

        Args:
            host: IP address of power supply
            port: TCP port (default: 5025)
            timeout: Communication timeout
        """
        self.controller_type = "power"
        self.vendor = "oda"
        self.connection_info = f"{host}:{port}"
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        
        # Power supply specific attributes
        self.interface = 'ethernet'
        self.address = f"{host}:{port}"
        self.channels = {}
        self.host = host
        self.port = port
        self.timeout = timeout
        self.comm = TCPCommunication(host, port, timeout)

        # ODA is single channel
        self.channels = {1: {'max_voltage': 0.0, 'max_current': 0.0, 'max_power': 0.0}}
        self._device_info = {}

    def set_error(self, message: str) -> None:
        """Set error message and status"""
        self._error_message = message
        self.status = HardwareStatus.ERROR

    def connect(self) -> None:
        """Connect to power supply (exception-first design)"""
        try:
            self.comm.connect()
            self.status = HardwareStatus.CONNECTED
            # Get device information
            self._get_device_info()
            logger.info(f"Connected to ODA power supply at {self.connection_info}")
        except ODAError:
            # Re-raise ODA specific errors to preserve error context and debugging info
            self.status = HardwareStatus.DISCONNECTED
            raise
        except Exception as e:
            logger.error(f"Power supply connection failed ({type(e).__name__}): {e}")
            self.status = HardwareStatus.DISCONNECTED
            raise ODAConnectionError(f"Power supply connection failed: {e}", command="CONNECT")

    def disconnect(self) -> None:
        """Disconnect from power supply"""
        try:
            self.comm.disconnect()
            self.status = HardwareStatus.DISCONNECTED
            logger.info("Disconnected from power supply")
        except Exception as e:
            # Note: Disconnect errors could be suppressed, but we re-raise for debugging
            logger.error(f"Failed to disconnect from power supply: {e}")
            self.set_error(f"Disconnect failed: {e}")
            raise ODAConnectionError(f"Power supply disconnect failed: {e}", command="DISCONNECT")

    def _get_device_info(self) -> None:
        """Get device identification and capabilities"""
        try:
            # Get device identity
            identity = self.comm.query(COMMANDS['IDENTITY'])
            if identity:
                self._device_info['identity'] = identity

            # Get serial number
            serial = self.comm.query(COMMANDS['SERIAL_NUMBER'])
            if serial:
                self._device_info['serial_number'] = serial

            # Get version
            version = self.comm.query(COMMANDS['VERSION'])
            if version:
                self._device_info['version'] = version

            logger.info(f"Device Info: {self._device_info}")

        except Exception as e:
            logger.error(f"Failed to get device info: {e}")

    def is_alive(self) -> bool:
        """Check if power supply connection is alive and responsive"""
        if self.status != HardwareStatus.CONNECTED:
            return False

        try:
            # Try to get device identity to verify connection
            identity = self.comm.query(COMMANDS['IDENTITY'])
            return identity is not None
        except Exception:
            return False

    def get_identity(self) -> str:
        """Get device identification"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="IDENTITY")

        try:
            response = self.comm.query(COMMANDS['IDENTITY'])
            if not response:
                raise ODACommunicationError("No identity response received", command="IDENTITY")
            return response
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Get identity failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get identity failed: {e}", command="IDENTITY")

    def reset(self) -> None:
        """Reset device to default state"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="RESET")

        try:
            self.comm.send_command(COMMANDS['RESET'])
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Power supply reset failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Reset failed: {e}", command="RESET")

    def clear_errors(self) -> None:
        """Clear error queue"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="CLEAR")

        try:
            self.comm.send_command(COMMANDS['CLEAR'])
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Power supply clear errors failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Clear errors failed: {e}", command="CLEAR")

    def get_error(self) -> tuple:
        """
        Get error from error queue

        Returns:
            tuple: (error_code, error_message)
        """
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="ERROR")

        try:
            response = self.comm.query(COMMANDS['ERROR'])
            if not response:
                raise ODACommunicationError("No error response received", command="ERROR")
            
            # Parse response like "+0,\"No error\""
            parts = response.split(',', 1)
            error_code = int(parts[0])
            error_msg = parts[1].strip('\"') if len(parts) > 1 else get_error_message(error_code)
            return (error_code, error_msg)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Failed to parse error response: {response}")
            raise ODAOperationError(f"Failed to parse error response: {response}", command="ERROR")
        except Exception as e:
            logger.error(f"Get error failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get error failed: {e}", command="ERROR")

    def get_temperature(self) -> float:
        """Get internal temperature"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="TEMPERATURE")

        try:
            response = self.comm.query(COMMANDS['TEMPERATURE'])
            if not response:
                raise ODACommunicationError("No temperature response received", command="TEMPERATURE")
            return float(response)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Invalid temperature response: {response}")
            raise ODAOperationError(f"Invalid temperature response: {response}", command="TEMPERATURE")
        except Exception as e:
            logger.error(f"Get temperature failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get temperature failed: {e}", command="TEMPERATURE")

    def beep(self) -> None:
        """Make device beep"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="BEEP")
        
        try:
            self.comm.send_command(COMMANDS['BEEP'])
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Beep operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Beep operation failed: {e}", command="BEEP")

    # Output Control Implementation
    def set_output_state(self, channel: int, state: bool) -> None:
        """Enable/disable output (ODA is single channel)"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="SET_OUTPUT")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="SET_OUTPUT")

        try:
            command = COMMANDS['OUTPUT_ON'] if state else COMMANDS['OUTPUT_OFF']
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Set output state failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Set output state failed: {e}", command="SET_OUTPUT")

    def get_output_state(self, channel: int) -> bool:
        """Get output state"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="OUTPUT_STATE")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="OUTPUT_STATE")

        try:
            response = self.comm.query(COMMANDS['OUTPUT_STATE'])
            if not response:
                raise ODACommunicationError("No output state response received", command="OUTPUT_STATE")
            return response.strip() == '1'
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Get output state failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get output state failed: {e}", command="OUTPUT_STATE")

    # Voltage Control Implementation
    def set_voltage(self, channel: int, voltage: float) -> None:
        """Set target voltage"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="SET_VOLTAGE")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="SET_VOLTAGE")

        try:
            command = COMMANDS['SET_VOLTAGE'].format(value=voltage)
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Set voltage failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Set voltage failed: {e}", command="SET_VOLTAGE")

    def get_voltage_setting(self, channel: int) -> float:
        """Get voltage setting"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="GET_VOLTAGE")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="GET_VOLTAGE")

        try:
            response = self.comm.query(COMMANDS['GET_VOLTAGE'])
            if not response:
                raise ODACommunicationError("No voltage response received", command="GET_VOLTAGE")
            return float(response)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Invalid voltage response: {response}")
            raise ODAOperationError(f"Invalid voltage response: {response}", command="GET_VOLTAGE")
        except Exception as e:
            logger.error(f"Get voltage setting failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get voltage setting failed: {e}", command="GET_VOLTAGE")

    def get_voltage_actual(self, channel: int) -> float:
        """Get actual output voltage"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="MEASURE_VOLTAGE")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="MEASURE_VOLTAGE")

        try:
            response = self.comm.query(COMMANDS['MEASURE_VOLTAGE'])
            if not response:
                raise ODACommunicationError("No voltage measurement response received", command="MEASURE_VOLTAGE")
            return float(response)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Invalid voltage measurement: {response}")
            raise ODAOperationError(f"Invalid voltage measurement: {response}", command="MEASURE_VOLTAGE")
        except Exception as e:
            logger.error(f"Get voltage actual failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get voltage actual failed: {e}", command="MEASURE_VOLTAGE")

    def voltage_up(self) -> None:
        """Increase voltage by step"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="VOLTAGE_UP")
        
        try:
            self.comm.send_command(COMMANDS['VOLTAGE_UP'])
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Voltage up operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Voltage up operation failed: {e}", command="VOLTAGE_UP")

    def voltage_down(self) -> None:
        """Decrease voltage by step"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="VOLTAGE_DOWN")
        
        try:
            self.comm.send_command(COMMANDS['VOLTAGE_DOWN'])
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Voltage down operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Voltage down operation failed: {e}", command="VOLTAGE_DOWN")

    def set_voltage_step(self, step: float) -> None:
        """Set voltage step size"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="VOLTAGE_STEP")
        
        try:
            command = COMMANDS['VOLTAGE_STEP'].format(value=step)
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Set voltage step operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Set voltage step operation failed: {e}", command="VOLTAGE_STEP")

    def get_voltage_step(self) -> float:
        """Get voltage step size"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="GET_VOLTAGE_STEP")

        try:
            response = self.comm.query(COMMANDS['GET_VOLTAGE_STEP'])
            if not response:
                raise ODACommunicationError("No voltage step response received", command="GET_VOLTAGE_STEP")
            return float(response)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Invalid voltage step response: {response}")
            raise ODAOperationError(f"Invalid voltage step response: {response}", command="GET_VOLTAGE_STEP")
        except Exception as e:
            logger.error(f"Get voltage step failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get voltage step failed: {e}", command="GET_VOLTAGE_STEP")

    # Current Control Implementation
    def set_current(self, channel: int, current: float) -> None:
        """Set current limit"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="SET_CURRENT")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="SET_CURRENT")

        try:
            command = COMMANDS['SET_CURRENT'].format(value=current)
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Set current failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Set current failed: {e}", command="SET_CURRENT")

    def get_current_setting(self, channel: int) -> float:
        """Get current setting"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="GET_CURRENT")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="GET_CURRENT")

        try:
            response = self.comm.query(COMMANDS['GET_CURRENT'])
            if not response:
                raise ODACommunicationError("No current response received", command="GET_CURRENT")
            return float(response)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Invalid current response: {response}")
            raise ODAOperationError(f"Invalid current response: {response}", command="GET_CURRENT")
        except Exception as e:
            logger.error(f"Get current setting failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get current setting failed: {e}", command="GET_CURRENT")

    def get_current_actual(self, channel: int) -> float:
        """Get actual output current"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="MEASURE_CURRENT")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="MEASURE_CURRENT")

        try:
            response = self.comm.query(COMMANDS['MEASURE_CURRENT'])
            if not response:
                raise ODACommunicationError("No current measurement response received", command="MEASURE_CURRENT")
            return float(response)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Invalid current measurement: {response}")
            raise ODAOperationError(f"Invalid current measurement: {response}", command="MEASURE_CURRENT")
        except Exception as e:
            logger.error(f"Get current actual failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get current actual failed: {e}", command="MEASURE_CURRENT")

    def current_up(self) -> None:
        """Increase current by step"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="CURRENT_UP")
        
        try:
            self.comm.send_command(COMMANDS['CURRENT_UP'])
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Current up operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Current up operation failed: {e}", command="CURRENT_UP")

    def current_down(self) -> None:
        """Decrease current by step"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="CURRENT_DOWN")
        
        try:
            self.comm.send_command(COMMANDS['CURRENT_DOWN'])
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Current down operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Current down operation failed: {e}", command="CURRENT_DOWN")

    def set_current_step(self, step: float) -> None:
        """Set current step size"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="CURRENT_STEP")
        
        try:
            command = COMMANDS['CURRENT_STEP'].format(value=step)
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Set current step operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Set current step operation failed: {e}", command="CURRENT_STEP")

    def get_current_step(self) -> float:
        """Get current step size"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="GET_CURRENT_STEP")

        try:
            response = self.comm.query(COMMANDS['GET_CURRENT_STEP'])
            if not response:
                raise ODACommunicationError("No current step response received", command="GET_CURRENT_STEP")
            return float(response)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Invalid current step response: {response}")
            raise ODAOperationError(f"Invalid current step response: {response}", command="GET_CURRENT_STEP")
        except Exception as e:
            logger.error(f"Get current step failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get current step failed: {e}", command="GET_CURRENT_STEP")

    # Combined Commands
    def apply_settings(self, voltage: float, current: float) -> None:
        """Apply voltage and current settings simultaneously"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="APPLY")
        
        try:
            command = COMMANDS['APPLY'].format(voltage=voltage, current=current)
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Apply settings operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Apply settings operation failed: {e}", command="APPLY")

    def get_apply_settings(self) -> Dict[str, float]:
        """Get current apply settings"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="APPLY_QUERY")

        try:
            response = self.comm.query(COMMANDS['APPLY_QUERY'])
            if not response:
                raise ODACommunicationError("No apply settings response received", command="APPLY_QUERY")
            
            # Parse response like "12.5,2.0"
            values = response.split(',')
            return {
                'voltage': float(values[0]),
                'current': float(values[1])
            }
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except (ValueError, IndexError):
            logger.error(f"Invalid apply response: {response}")
            raise ODAOperationError(f"Invalid apply response: {response}", command="APPLY_QUERY")
        except Exception as e:
            logger.error(f"Get apply settings failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get apply settings failed: {e}", command="APPLY_QUERY")

    # Protection Implementation
    def set_ovp(self, channel: int, voltage: float) -> None:
        """Set over-voltage protection"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="SET_OVP")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="SET_OVP")
        
        try:
            command = COMMANDS['SET_OVP'].format(value=voltage)
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Set OVP operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Set OVP operation failed: {e}", command="SET_OVP")

    def get_ovp(self, channel: int) -> float:
        """Get over-voltage protection setting"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="GET_OVP")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="GET_OVP")

        try:
            response = self.comm.query(COMMANDS['GET_OVP'])
            if not response:
                raise ODACommunicationError("No OVP response received", command="GET_OVP")
            return float(response)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Invalid OVP response: {response}")
            raise ODAOperationError(f"Invalid OVP response: {response}", command="GET_OVP")
        except Exception as e:
            logger.error(f"Get OVP failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get OVP failed: {e}", command="GET_OVP")

    def set_ocp(self, channel: int, current: float) -> None:
        """Set over-current protection"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="SET_OCP")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="SET_OCP")
        
        try:
            command = COMMANDS['SET_OCP'].format(value=current)
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Set OCP operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Set OCP operation failed: {e}", command="SET_OCP")

    def get_ocp(self, channel: int) -> float:
        """Get over-current protection setting"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="GET_OCP")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="GET_OCP")

        try:
            response = self.comm.query(COMMANDS['GET_OCP'])
            if not response:
                raise ODACommunicationError("No OCP response received", command="GET_OCP")
            return float(response)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except ValueError:
            logger.error(f"Invalid OCP response: {response}")
            raise ODAOperationError(f"Invalid OCP response: {response}", command="GET_OCP")
        except Exception as e:
            logger.error(f"Get OCP failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get OCP failed: {e}", command="GET_OCP")

    def get_protection_status(self, channel: int) -> Dict[str, bool]:
        """Get protection status"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="PROTECTION_STATUS")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="PROTECTION_STATUS")

        try:
            ovp_trip = self.comm.query(COMMANDS['OVP_TRIP_STATUS'])
            ocp_trip = self.comm.query(COMMANDS['OCP_TRIP_STATUS'])

            status = {}
            if ovp_trip is not None:
                status['ovp_trip'] = ovp_trip.strip() == '1'
            if ocp_trip is not None:
                status['ocp_trip'] = ocp_trip.strip() == '1'

            if not status:
                raise ODACommunicationError("No protection status response received", command="PROTECTION_STATUS")
            return status
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Get protection status failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get protection status failed: {e}", command="PROTECTION_STATUS")

    def clear_protection(self, channel: int) -> None:
        """Clear protection faults"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="CLEAR_PROTECTION")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="CLEAR_PROTECTION")
        
        try:
            # Clear both OVP and OCP
            self.comm.send_command(COMMANDS['CLEAR_OVP'])
            self.comm.send_command(COMMANDS['CLEAR_OCP'])
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Clear protection operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Clear protection operation failed: {e}", command="CLEAR_PROTECTION")

    # Measurement Implementation
    def measure_all(self, channel: int) -> Dict[str, float]:
        """Measure voltage, current, power"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="MEASURE_ALL")
        if channel != 1:
            raise ODAOperationError("Invalid channel: ODA is single channel device", command="MEASURE_ALL")

        try:
            response = self.comm.query(COMMANDS['MEASURE_ALL'])
            if not response:
                raise ODACommunicationError("No measurement response received", command="MEASURE_ALL")
            
            # Parse response like "12.5,2.0,25.0"
            values = response.split(',')
            return {
                'voltage': float(values[0]),
                'current': float(values[1]),
                'power': float(values[2]) if len(values) > 2 else 0.0
            }
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except (ValueError, IndexError):
            logger.error(f"Invalid measurement response: {response}")
            raise ODAOperationError(f"Invalid measurement response: {response}", command="MEASURE_ALL")
        except Exception as e:
            logger.error(f"Measure all failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Measure all failed: {e}", command="MEASURE_ALL")

    # Memory Operations
    def save_settings(self, slot: int) -> None:
        """Save current settings to memory slot (1-8, 10)"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="SAVE_SETTINGS")
        if slot not in [1, 2, 3, 4, 5, 6, 7, 8, 10]:
            raise ODAOperationError(f"Invalid memory slot: {slot}. Valid slots: 1-8, 10", command="SAVE_SETTINGS")
        
        try:
            command = COMMANDS['SAVE_SETTINGS'].format(slot=slot)
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Save settings operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Save settings operation failed: {e}", command="SAVE_SETTINGS")

    def recall_settings(self, slot: int) -> None:
        """Recall settings from memory slot (1-8, 10)"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="RECALL_SETTINGS")
        if slot not in [1, 2, 3, 4, 5, 6, 7, 8, 10]:
            raise ODAOperationError(f"Invalid memory slot: {slot}. Valid slots: 1-8, 10", command="RECALL_SETTINGS")
        
        try:
            command = COMMANDS['RECALL_SETTINGS'].format(slot=slot)
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Recall settings operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Recall settings operation failed: {e}", command="RECALL_SETTINGS")

    # Key Lock
    def set_key_lock(self, locked: bool) -> None:
        """Enable/disable front panel key lock"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="SET_KEY_LOCK")
        
        try:
            command = COMMANDS['KEY_LOCK_ON'] if locked else COMMANDS['KEY_LOCK_OFF']
            self.comm.send_command(command)
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Set key lock operation failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Set key lock operation failed: {e}", command="SET_KEY_LOCK")

    def get_key_lock_state(self) -> bool:
        """Get key lock state"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="KEY_LOCK_STATE")

        try:
            response = self.comm.query(COMMANDS['KEY_LOCK_STATE'])
            if not response:
                raise ODACommunicationError("No key lock state response received", command="KEY_LOCK_STATE")
            return response.strip() == '1'
        except ODAError:
            # Re-raise ODA specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Get key lock state failed ({type(e).__name__}): {e}")
            raise ODAOperationError(f"Get key lock state failed: {e}", command="KEY_LOCK_STATE")

    # Utility methods
    def get_device_info(self) -> Dict[str, Any]:
        """Get cached device information"""
        return self._device_info.copy()

    def check_errors(self) -> List[tuple]:
        """Check all errors in error queue"""
        errors = []
        if self.status != HardwareStatus.CONNECTED:
            return errors

        # Read errors until queue is empty
        for _ in range(10):  # Prevent infinite loop
            error = self.get_error()
            if error and error[0] != 0:  # 0 = No error
                errors.append(error)
            else:
                break

        return errors

    def analyze_errors(self) -> List[Dict]:
        """Get comprehensive error analysis"""
        errors = self.check_errors()
        analyses = []

        for error_code, error_msg in errors:
            analysis = analyze_error(error_code)
            analysis['original_message'] = error_msg
            analyses.append(analysis)

        return analyses

    def clear_all_errors(self) -> None:
        """Clear all errors from queue"""
        if self.status != HardwareStatus.CONNECTED:
            raise ODAConnectionError("Device not connected", command="CLEAR_ALL")

        # Read all errors to clear queue
        self.check_errors()

        # Send clear command
        self.clear_errors()

    def has_trip_errors(self) -> bool:
        """Check if there are any protection trip errors"""
        errors = self.check_errors()
        for error_code, _ in errors:
            if is_trip_error(error_code):
                return True
        return False

    def is_output_on(self, channel: int = 1) -> bool:
        """Check if output is enabled"""
        try:
            return self.get_output_state(channel)
        except ODAError:
            # Re-raise ODA specific errors
            raise
        except Exception as e:
            logger.error(f"Failed to check output state: {e}")
            raise ODAOperationError(f"Failed to check output state: {e}", command="OUTPUT_STATE")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """Context manager exit"""
        self.disconnect()
        # Return False to propagate any exceptions
        return False
