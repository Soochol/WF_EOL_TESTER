"""
Hardware CLI

Command line interface for hardware management operations.
"""

import asyncio
from typing import Optional
from loguru import logger

from ..controllers.hardware_controller import HardwareController
from .base_cli import BaseCLI


class HardwareCLI(BaseCLI):
    """CLI for hardware management operations"""
    
    def __init__(self, hardware_controller: HardwareController):
        """
        Initialize CLI with controller
        
        Args:
            hardware_controller: Hardware controller
        """
        super().__init__()
        self._controller = hardware_controller
    
    async def hardware_status_interactive(self) -> None:
        """Interactive hardware status check"""
        self.print_header("Hardware Status Check")
        
        try:
            self.show_spinner("Checking hardware status...")
            result = await self._controller.get_hardware_status()
            self.hide_spinner()
            
            if result['success']:
                self._display_hardware_status(result['data'])
            else:
                self.print_error("Failed to get hardware status")
                self._display_error_result(result)
                
        except Exception as e:
            self.hide_spinner()
            self.print_error(f"Error checking hardware status: {str(e)}")
            logger.error(f"CLI error during status check: {e}")
    
    async def connect_hardware_interactive(self) -> None:
        """Interactive hardware connection"""
        self.print_header("Hardware Connection")
        
        # Show available devices
        devices = ["loadcell", "power_supply"]
        self.print_info("Available devices:")
        for i, device in enumerate(devices, 1):
            self.print_info(f"  {i}. {device}")
        
        device_choice = self.get_user_input("Select device to connect (1-2)", required=True)
        try:
            device_type = devices[int(device_choice) - 1]
        except (ValueError, IndexError):
            self.print_error("Invalid device selection")
            return
        
        try:
            self.show_spinner(f"Connecting to {device_type}...")
            result = await self._controller.connect_hardware(device_type)
            self.hide_spinner()
            
            if result['success']:
                self.print_success(f"Successfully connected to {device_type}")
                self._display_device_info(result['data'])
            else:
                self.print_error(f"Failed to connect to {device_type}")
                self._display_error_result(result)
                
        except Exception as e:
            self.hide_spinner()
            self.print_error(f"Error connecting to {device_type}: {str(e)}")
    
    async def disconnect_hardware_interactive(self) -> None:
        """Interactive hardware disconnection"""
        self.print_header("Hardware Disconnection")
        
        # Show available devices
        devices = ["loadcell", "power_supply"]
        self.print_info("Available devices:")
        for i, device in enumerate(devices, 1):
            self.print_info(f"  {i}. {device}")
        
        device_choice = self.get_user_input("Select device to disconnect (1-2)", required=True)
        try:
            device_type = devices[int(device_choice) - 1]
        except (ValueError, IndexError):
            self.print_error("Invalid device selection")
            return
        
        if not self.get_user_confirmation(f"Disconnect {device_type}?"):
            self.print_info("Disconnection cancelled")
            return
        
        try:
            self.show_spinner(f"Disconnecting from {device_type}...")
            result = await self._controller.disconnect_hardware(device_type)
            self.hide_spinner()
            
            if result['success']:
                self.print_success(f"Successfully disconnected from {device_type}")
            else:
                self.print_error(f"Failed to disconnect from {device_type}")
                self._display_error_result(result)
                
        except Exception as e:
            self.hide_spinner()
            self.print_error(f"Error disconnecting from {device_type}: {str(e)}")
    
    async def read_force_interactive(self) -> None:
        """Interactive force measurement"""
        self.print_header("Force Measurement")
        
        # Get measurement parameters
        num_samples_str = self.get_user_input("Number of samples (default: 1)")
        try:
            num_samples = int(num_samples_str) if num_samples_str else 1
        except ValueError:
            self.print_error("Invalid number of samples")
            return
        
        if num_samples < 1 or num_samples > 100:
            self.print_error("Number of samples must be between 1 and 100")
            return
        
        try:
            self.show_spinner(f"Reading force ({num_samples} samples)...")
            result = await self._controller.read_loadcell_force(num_samples)
            self.hide_spinner()
            
            if result['success']:
                self._display_force_measurement(result['data'])
            else:
                self.print_error("Force measurement failed")
                self._display_error_result(result)
                
        except Exception as e:
            self.hide_spinner()
            self.print_error(f"Error reading force: {str(e)}")
    
    async def zero_loadcell_interactive(self) -> None:
        """Interactive loadcell zero operation"""
        self.print_header("LoadCell Auto-Zero")
        
        if not self.get_user_confirmation("Perform auto-zero operation?"):
            self.print_info("Auto-zero cancelled")
            return
        
        try:
            self.show_spinner("Performing auto-zero...")
            result = await self._controller.zero_loadcell()
            self.hide_spinner()
            
            if result['success']:
                self.print_success("Auto-zero operation completed successfully")
            else:
                self.print_error("Auto-zero operation failed")
                self._display_error_result(result)
                
        except Exception as e:
            self.hide_spinner()
            self.print_error(f"Error during auto-zero: {str(e)}")
    
    async def set_power_output_interactive(self) -> None:
        """Interactive power output configuration"""
        self.print_header("Power Output Configuration")
        
        # Get power parameters
        voltage_str = self.get_user_input("Voltage (V)", required=True)
        try:
            voltage = float(voltage_str)
        except ValueError:
            self.print_error("Invalid voltage value")
            return
        
        current_str = self.get_user_input("Current limit (A)", required=True)
        try:
            current_limit = float(current_str)
        except ValueError:
            self.print_error("Invalid current limit value")
            return
        
        enable_output = self.get_user_confirmation("Enable output?", default=True)
        
        channel_str = self.get_user_input("Channel (default: 1)")
        try:
            channel = int(channel_str) if channel_str else 1
        except ValueError:
            self.print_error("Invalid channel number")
            return
        
        try:
            self.show_spinner("Configuring power output...")
            result = await self._controller.set_power_output(
                voltage=voltage,
                current_limit=current_limit,
                enabled=enable_output,
                channel=channel
            )
            self.hide_spinner()
            
            if result['success']:
                self.print_success("Power output configured successfully")
                self._display_power_configuration(result['data'])
            else:
                self.print_error("Power output configuration failed")
                self._display_error_result(result)
                
        except Exception as e:
            self.hide_spinner()
            self.print_error(f"Error configuring power output: {str(e)}")
    
    async def measure_power_interactive(self) -> None:
        """Interactive power measurement"""
        self.print_header("Power Measurement")
        
        channel_str = self.get_user_input("Channel (default: 1)")
        try:
            channel = int(channel_str) if channel_str else 1
        except ValueError:
            self.print_error("Invalid channel number")
            return
        
        try:
            self.show_spinner("Measuring power output...")
            result = await self._controller.measure_power_output(channel)
            self.hide_spinner()
            
            if result['success']:
                self._display_power_measurement(result['data'])
            else:
                self.print_error("Power measurement failed")
                self._display_error_result(result)
                
        except Exception as e:
            self.hide_spinner()
            self.print_error(f"Error measuring power: {str(e)}")
    
    def _display_hardware_status(self, status_data: dict) -> None:
        """Display hardware status in table format"""
        self.print_section_header("Hardware Status")
        
        # LoadCell status
        loadcell = status_data.get('loadcell', {})
        self.print_section_header("LoadCell")
        self.print_key_value("Connected", "Yes" if loadcell.get('connected') else "No",
                           color="green" if loadcell.get('connected') else "red")
        self.print_key_value("Status", loadcell.get('status', 'Unknown'))
        self.print_key_value("Vendor", loadcell.get('vendor', 'Unknown'))
        
        if loadcell.get('error_message'):
            self.print_key_value("Error", loadcell['error_message'], color="red")
        
        # Power Supply status
        power = status_data.get('power_supply', {})
        self.print_section_header("Power Supply")
        self.print_key_value("Connected", "Yes" if power.get('connected') else "No",
                           color="green" if power.get('connected') else "red")
        self.print_key_value("Status", power.get('status', 'Unknown'))
        self.print_key_value("Vendor", power.get('vendor', 'Unknown'))
        
        if power.get('error_message'):
            self.print_key_value("Error", power['error_message'], color="red")
    
    def _display_device_info(self, device_data: dict) -> None:
        """Display device connection information"""
        self.print_section_header("Device Information")
        self.print_key_value("Device Type", device_data.get('device_type', 'Unknown'))
        self.print_key_value("Connected", "Yes" if device_data.get('connected') else "No")
        self.print_key_value("Status", device_data.get('status', 'Unknown'))
        
        device_info = device_data.get('device_info', {})
        if device_info:
            self.print_key_value("Vendor", device_info.get('vendor', 'Unknown'))
            
            capabilities = device_info.get('capabilities', {})
            if capabilities:
                self.print_section_header("Capabilities")
                for key, value in capabilities.items():
                    self.print_key_value(key.replace('_', ' ').title(), str(value))
    
    def _display_force_measurement(self, measurement_data: dict) -> None:
        """Display force measurement results"""
        self.print_section_header("Force Measurement Results")
        
        if measurement_data.get('samples', 1) == 1:
            # Single measurement
            self.print_key_value("Force Value", f"{measurement_data['value']} {measurement_data['unit']}")
        else:
            # Multiple measurements with statistics
            self.print_key_value("Samples", str(measurement_data['samples']))
            
            statistics = measurement_data.get('statistics', {})
            if statistics:
                self.print_section_header("Statistics")
                for stat_name, stat_data in statistics.items():
                    value_str = f"{stat_data['value']} {stat_data['unit']}"
                    self.print_key_value(stat_name.replace('_', ' ').title(), value_str)
    
    def _display_power_configuration(self, config_data: dict) -> None:
        """Display power configuration results"""
        self.print_section_header("Power Configuration")
        
        self.print_key_value("Channel", str(config_data.get('channel', 'Unknown')))
        
        voltage = config_data.get('voltage', {})
        voltage_str = f"Set: {voltage.get('set')} V, Actual: {voltage.get('actual')} {voltage.get('unit', 'V')}"
        self.print_key_value("Voltage", voltage_str)
        
        current = config_data.get('current_limit', {})
        current_str = f"Set: {current.get('set')} A, Actual: {current.get('actual')} {current.get('unit', 'A')}"
        self.print_key_value("Current Limit", current_str)
        
        output_enabled = config_data.get('output_enabled', False)
        self.print_key_value("Output Enabled", "Yes" if output_enabled else "No",
                           color="green" if output_enabled else "red")
    
    def _display_power_measurement(self, measurement_data: dict) -> None:
        """Display power measurement results"""
        self.print_section_header("Power Measurement Results")
        
        self.print_key_value("Channel", str(measurement_data.get('channel', 'Unknown')))
        
        voltage = measurement_data.get('voltage', {})
        self.print_key_value("Voltage", f"{voltage.get('value')} {voltage.get('unit', 'V')}")
        
        current = measurement_data.get('current', {})
        self.print_key_value("Current", f"{current.get('value')} {current.get('unit', 'A')}")
        
        power = measurement_data.get('power', 0)
        self.print_key_value("Power", f"{power} W")
    
    def _display_error_result(self, result: dict) -> None:
        """Display error result"""
        error = result.get('error', {})
        
        self.print_section_header("Error Details")
        self.print_key_value("Error Code", error.get('code', 'UNKNOWN'))
        self.print_error(error.get('message', 'Unknown error occurred'))
        
        # Error context
        context = error.get('context', {})
        if context:
            self.print_section_header("Error Context")
            for key, value in context.items():
                self.print_key_value(key.replace('_', ' ').title(), str(value))