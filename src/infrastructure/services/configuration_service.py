"""
Configuration Service

Service for managing hardware configuration loading, saving, and validation.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger

from .hardware_configuration import (
    HardwareConfiguration,
    RobotConfig, 
    LoadCellConfig, 
    MCUConfig, 
    PowerConfig, 
    DigitalInputConfig
)
from domain.exceptions.validation_exceptions import ValidationException


class ConfigurationService:
    """Service for managing hardware configuration operations"""
    
    def load_hardware_config(self, file_path: str) -> HardwareConfiguration:
        """
        Load hardware configuration from file (supports JSON and YAML)
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            HardwareConfiguration object
            
        Raises:
            ValidationException: If configuration is invalid
            json.JSONDecodeError: If JSON is malformed
            yaml.YAMLError: If YAML is malformed
        """
        config_path = Path(file_path)
        
        if not config_path.exists():
            logger.info(f"Config file {file_path} not found, using default config")
            return self.get_default_hardware_config()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                # Determine file format by extension
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config_dict = yaml.safe_load(f)
                    logger.info(f"YAML configuration loaded from {file_path}")
                else:
                    config_dict = json.load(f)
                    logger.info(f"JSON configuration loaded from {file_path}")
            
            # Handle case where config_dict is None (empty file)
            if config_dict is None:
                logger.warning(f"Config file {file_path} is empty, using default config")
                return self.get_default_hardware_config()
            
            # Extract hardware section and convert to HardwareConfiguration
            hardware_dict = config_dict.get('hardware', config_dict)  # Support both nested and direct format
            return self._dict_to_hardware_config(hardware_dict)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            logger.error(f"Invalid format in config file: {e}")
            logger.info("Using default configuration due to file format error")
            return self.get_default_hardware_config()
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            logger.info("Using default configuration due to loading error")
            return self.get_default_hardware_config()
    
    def save_hardware_config(self, config: HardwareConfiguration, file_path: str) -> None:
        """
        Save hardware configuration to file (supports JSON and YAML)
        
        Args:
            config: HardwareConfiguration object to save
            file_path: Path where to save the configuration
            
        Raises:
            OSError: If file cannot be written
        """
        config_path = Path(file_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Convert to full configuration format
            full_config = {
                'hardware': config.to_dict(),
                'repository': {
                    'type': 'json',
                    'data_dir': 'data/tests',
                    'auto_save': True
                },
                'application': {
                    'test_timeout': 300,
                    'measurement_precision': 3,
                    'auto_connect': True
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                # Determine file format by extension
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(full_config, f, default_flow_style=False, allow_unicode=True, indent=2)
                    logger.info(f"YAML configuration saved to {file_path}")
                else:
                    json.dump(full_config, f, indent=2, ensure_ascii=False)
                    logger.info(f"JSON configuration saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise
    
    def get_default_hardware_config(self) -> HardwareConfiguration:
        """
        Get default hardware configuration
        
        Returns:
            Default HardwareConfiguration for mock hardware
        """
        robot_config = RobotConfig(
            model="MOCK",
            axis=0,
            velocity=100.0,
            acceleration=100.0,
            deceleration=100.0,
            max_velocity=500.0,
            axis_count=6,
            irq_no=7
        )
        
        loadcell_config = LoadCellConfig(
            model="MOCK",
            port="MOCK",
            baudrate=9600,
            timeout=1.0,
            indicator_id=1
        )
        
        mcu_config = MCUConfig(
            model="MOCK",
            port="MOCK",
            baudrate=115200,
            timeout=2.0
        )
        
        power_config = PowerConfig(
            model="MOCK",
            host="localhost",
            port=8080,
            timeout=5.0,
            channel=1
        )
        
        digital_input_config = DigitalInputConfig(
            model="MOCK",
            board_no=0,
            input_count=32,
            debounce_time=0.01
        )
        
        return HardwareConfiguration(
            robot=robot_config,
            loadcell=loadcell_config,
            mcu=mcu_config,
            power=power_config,
            digital_input=digital_input_config
        )
    
    def get_production_hardware_config(self) -> HardwareConfiguration:
        """
        Get production hardware configuration
        
        Returns:
            Production HardwareConfiguration for real hardware
        """
        robot_config = RobotConfig(
            model="AJINEXTEK",
            axis=0,
            velocity=100.0,
            acceleration=100.0,
            deceleration=100.0,
            max_velocity=500.0,
            axis_count=6,
            irq_no=7
        )
        
        loadcell_config = LoadCellConfig(
            model="BS205",
            port="COM1",
            baudrate=9600,
            timeout=1.0,
            indicator_id=1
        )
        
        mcu_config = MCUConfig(
            model="LMA",
            port="COM2",
            baudrate=9600,
            timeout=5.0
        )
        
        power_config = PowerConfig(
            model="ODA",
            host="192.168.1.10",
            port=8080,
            timeout=5.0,
            channel=1
        )
        
        digital_input_config = DigitalInputConfig(
            model="AJINEXTEK",
            board_no=0,
            input_count=8,
            debounce_time=0.01
        )
        
        return HardwareConfiguration(
            robot=robot_config,
            loadcell=loadcell_config,
            mcu=mcu_config,
            power=power_config,
            digital_input=digital_input_config
        )
    
    def validate_hardware_config(self, config: HardwareConfiguration) -> bool:
        """
        Validate hardware configuration
        
        Args:
            config: HardwareConfiguration to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # The dataclass __post_init__ method handles validation
            return config.is_valid()
        except ValidationException as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            return False
    
    def _dict_to_hardware_config(self, hardware_dict: Dict[str, Any]) -> HardwareConfiguration:
        """
        Convert dictionary to HardwareConfiguration
        
        Args:
            hardware_dict: Dictionary containing hardware configuration
            
        Returns:
            HardwareConfiguration object
        """
        # Create individual config objects from dictionary
        robot_data = hardware_dict.get('robot', {})
        robot_config = RobotConfig(**robot_data) if robot_data else RobotConfig()
        
        loadcell_data = hardware_dict.get('loadcell', {})
        loadcell_config = LoadCellConfig(**loadcell_data) if loadcell_data else LoadCellConfig()
        
        mcu_data = hardware_dict.get('mcu', {})
        mcu_config = MCUConfig(**mcu_data) if mcu_data else MCUConfig()
        
        power_data = hardware_dict.get('power', {})
        power_config = PowerConfig(**power_data) if power_data else PowerConfig()
        
        digital_input_data = hardware_dict.get('digital_input', {})
        digital_input_config = DigitalInputConfig(**digital_input_data) if digital_input_data else DigitalInputConfig()
        
        return HardwareConfiguration(
            robot=robot_config,
            loadcell=loadcell_config,
            mcu=mcu_config,
            power=power_config,
            digital_input=digital_input_config
        )
    
    def hardware_config_to_factory_dict(self, config: HardwareConfiguration) -> Dict[str, Any]:
        """
        Convert HardwareConfiguration to ServiceFactory compatible dictionary
        
        Args:
            config: HardwareConfiguration object
            
        Returns:
            Dictionary compatible with ServiceFactory methods
        """
        config_dict = config.to_dict()
        
        # Convert to factory format - only real hardware needs connection info
        return {
            'hardware': {
                'loadcell': {
                    'type': config.loadcell.model.lower(),
                    'connection': {
                        'port': config_dict['loadcell']['port'],
                        'baudrate': config_dict['loadcell']['baudrate'],
                        'timeout': config_dict['loadcell']['timeout'],
                        'indicator_id': config_dict['loadcell']['indicator_id']
                    }
                },
                'power_supply': {
                    'type': config.power.model.lower(),
                    'connection': {
                        'host': config_dict['power']['host'],
                        'port': config_dict['power']['port'],
                        'timeout': config_dict['power']['timeout'],
                        'channel': config_dict['power']['channel']
                    }
                },
                'mcu': {
                    'type': config.mcu.model.lower(),
                    'connection': {
                        'port': config_dict['mcu']['port'],
                        'baudrate': config_dict['mcu']['baudrate'],
                        'timeout': config_dict['mcu']['timeout']
                    }
                },
                'digital_input': {
                    'type': config.digital_input.model.lower(),
                    'connection': {
                        'board_number': config_dict['digital_input']['board_no'],
                        'input_count': config_dict['digital_input']['input_count'],
                        'module_position': 0,
                        'signal_type': 2,
                        'debounce_time_ms': int(config_dict['digital_input']['debounce_time'] * 1000),
                        'retry_count': 3,
                        'auto_initialize': True
                    }
                },
                'robot': {
                    'type': config.robot.model.lower(),
                    'connection': {
                        'irq_no': config_dict['robot']['irq_no'],
                        'axis_count': config_dict['robot']['axis_count'],
                        'axis': config_dict['robot']['axis'],
                        'default_velocity': config_dict['robot']['velocity'],
                        'default_acceleration': config_dict['robot']['acceleration'],
                        'default_deceleration': config_dict['robot']['deceleration'],
                        'max_velocity': config_dict['robot']['max_velocity'],
                        'max_acceleration': config_dict['robot']['max_acceleration'],
                        'max_deceleration': config_dict['robot']['max_deceleration'],
                        'position_tolerance': config_dict['robot']['position_tolerance'],
                        'homing_velocity': config_dict['robot']['homing_velocity'],
                        'homing_acceleration': config_dict['robot']['homing_acceleration'],
                        'homing_deceleration': config_dict['robot']['homing_deceleration']
                    }
                }
            },
            'repository': {
                'type': 'json',
                'data_dir': 'data/tests',
                'auto_save': True
            },
            'application': {
                'test_timeout': 300,
                'measurement_precision': 3,
                'auto_connect': True
            }
        }