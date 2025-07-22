"""
Hardware API

HTTP API endpoints for hardware management operations.
"""

from typing import Dict, Any, Optional, Tuple
from loguru import logger

from ..controllers.hardware_controller import HardwareController
from .base_api import BaseAPI


class HardwareAPI(BaseAPI):
    """HTTP API for hardware management operations"""
    
    def __init__(self, hardware_controller: HardwareController):
        """
        Initialize API with controller
        
        Args:
            hardware_controller: Hardware controller
        """
        super().__init__()
        self._controller = hardware_controller
    
    async def get_hardware_status(self) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        GET /api/v1/hardware/status
        Get status of all hardware devices
        
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("GET", "/api/v1/hardware/status")
        
        try:
            # Get status through controller
            result = await self._controller.get_hardware_status()
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, "get hardware status")
    
    async def connect_hardware(self, device_type: str) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        POST /api/v1/hardware/{device_type}/connect
        Connect to specific hardware device
        
        Args:
            device_type: Type of device to connect ('loadcell' or 'power_supply')
            
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("POST", f"/api/v1/hardware/{device_type}/connect")
        
        try:
            # Validate device type
            if not device_type or device_type.lower() not in ['loadcell', 'power_supply']:
                return self.create_validation_error_response(
                    {'device_type': 'Device type must be "loadcell" or "power_supply"'}
                )
            
            # Connect through controller
            result = await self._controller.connect_hardware(device_type.lower())
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, f"connect {device_type}")
    
    async def disconnect_hardware(self, device_type: str) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        POST /api/v1/hardware/{device_type}/disconnect
        Disconnect from specific hardware device
        
        Args:
            device_type: Type of device to disconnect ('loadcell' or 'power_supply')
            
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("POST", f"/api/v1/hardware/{device_type}/disconnect")
        
        try:
            # Validate device type
            if not device_type or device_type.lower() not in ['loadcell', 'power_supply']:
                return self.create_validation_error_response(
                    {'device_type': 'Device type must be "loadcell" or "power_supply"'}
                )
            
            # Disconnect through controller
            result = await self._controller.disconnect_hardware(device_type.lower())
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, f"disconnect {device_type}")
    
    async def read_loadcell_force(self, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        POST /api/v1/hardware/loadcell/measure
        Read force measurement from loadcell
        
        Args:
            request_data: Request payload containing measurement parameters
            
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("POST", "/api/v1/hardware/loadcell/measure", request_data)
        
        try:
            # Validate and extract parameters
            validation_errors = self._validate_force_measurement_request(request_data)
            if validation_errors:
                return self.create_validation_error_response(validation_errors)
            
            num_samples = request_data.get('num_samples', 1)
            
            # Read force through controller
            result = await self._controller.read_loadcell_force(num_samples)
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, "loadcell force measurement")
    
    async def zero_loadcell(self) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        POST /api/v1/hardware/loadcell/zero
        Perform auto-zero operation on loadcell
        
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("POST", "/api/v1/hardware/loadcell/zero")
        
        try:
            # Zero loadcell through controller
            result = await self._controller.zero_loadcell()
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, "loadcell auto-zero")
    
    async def set_power_output(self, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        POST /api/v1/hardware/power_supply/configure
        Set power supply output parameters
        
        Args:
            request_data: Request payload containing power configuration
            
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("POST", "/api/v1/hardware/power_supply/configure", request_data)
        
        try:
            # Validate and extract parameters
            validation_errors = self._validate_power_configuration_request(request_data)
            if validation_errors:
                return self.create_validation_error_response(validation_errors)
            
            voltage = request_data['voltage']
            current_limit = request_data['current_limit']
            enabled = request_data.get('enabled', True)
            channel = request_data.get('channel', 1)
            
            # Configure power through controller
            result = await self._controller.set_power_output(
                voltage=voltage,
                current_limit=current_limit,
                enabled=enabled,
                channel=channel
            )
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, "power output configuration")
    
    async def measure_power_output(self, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        POST /api/v1/hardware/power_supply/measure
        Measure actual power supply output
        
        Args:
            request_data: Request payload containing measurement parameters
            
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("POST", "/api/v1/hardware/power_supply/measure", request_data)
        
        try:
            # Validate and extract parameters
            channel = request_data.get('channel', 1)
            
            if not isinstance(channel, int) or channel < 1:
                return self.create_validation_error_response(
                    {'channel': 'Channel must be a positive integer'}
                )
            
            # Measure power through controller
            result = await self._controller.measure_power_output(channel)
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, "power measurement")
    
    def _validate_force_measurement_request(self, request_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate force measurement request data
        
        Args:
            request_data: Request payload
            
        Returns:
            Dictionary of field validation errors (empty if valid)
        """
        errors = {}
        
        num_samples = request_data.get('num_samples', 1)
        
        if not isinstance(num_samples, int):
            errors['num_samples'] = 'Number of samples must be an integer'
        elif num_samples < 1:
            errors['num_samples'] = 'Number of samples must be at least 1'
        elif num_samples > 1000:
            errors['num_samples'] = 'Number of samples must be 1000 or less'
        
        return errors
    
    def _validate_power_configuration_request(self, request_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate power configuration request data
        
        Args:
            request_data: Request payload
            
        Returns:
            Dictionary of field validation errors (empty if valid)
        """
        errors = {}
        
        # Required fields
        if 'voltage' not in request_data:
            errors['voltage'] = 'Voltage is required'
        else:
            voltage = request_data['voltage']
            if not isinstance(voltage, (int, float)):
                errors['voltage'] = 'Voltage must be a number'
            elif voltage < 0:
                errors['voltage'] = 'Voltage must be non-negative'
            elif voltage > 100:  # Safety limit
                errors['voltage'] = 'Voltage must be 100V or less'
        
        if 'current_limit' not in request_data:
            errors['current_limit'] = 'Current limit is required'
        else:
            current_limit = request_data['current_limit']
            if not isinstance(current_limit, (int, float)):
                errors['current_limit'] = 'Current limit must be a number'
            elif current_limit < 0:
                errors['current_limit'] = 'Current limit must be non-negative'
            elif current_limit > 50:  # Safety limit
                errors['current_limit'] = 'Current limit must be 50A or less'
        
        # Optional fields
        enabled = request_data.get('enabled', True)
        if not isinstance(enabled, bool):
            errors['enabled'] = 'Enabled must be a boolean'
        
        channel = request_data.get('channel', 1)
        if not isinstance(channel, int) or channel < 1:
            errors['channel'] = 'Channel must be a positive integer'
        
        return errors