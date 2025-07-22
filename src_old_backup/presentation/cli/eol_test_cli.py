"""
EOL Test CLI

Command line interface for EOL test operations.
"""

import asyncio
import json
from typing import Optional
from loguru import logger

from ..controllers.eol_test_controller import EOLTestController
from .base_cli import BaseCLI


class EOLTestCLI(BaseCLI):
    """CLI for EOL test operations"""
    
    def __init__(self, eol_test_controller: EOLTestController):
        """
        Initialize CLI with controller
        
        Args:
            eol_test_controller: EOL test controller
        """
        super().__init__()
        self._controller = eol_test_controller
    
    async def execute_test_interactive(self) -> None:
        """Interactive test execution"""
        self.print_header("EOL Test Execution")
        
        try:
            # Collect test parameters interactively
            dut_id = self.get_user_input("Enter DUT ID", required=True)
            
            # Show available test types
            test_types = ["FORCE_ONLY", "ELECTRICAL_ONLY", "COMPREHENSIVE"]
            self.print_info("Available test types:")
            for i, test_type in enumerate(test_types, 1):
                self.print_info(f"  {i}. {test_type}")
            
            test_type_choice = self.get_user_input("Select test type (1-3)", required=True)
            try:
                test_type = test_types[int(test_type_choice) - 1]
            except (ValueError, IndexError):
                self.print_error("Invalid test type selection")
                return
            
            operator_id = self.get_user_input("Enter operator ID", required=True)
            
            # Optional parameters
            dut_model = self.get_user_input("Enter DUT model number (optional)")
            dut_serial = self.get_user_input("Enter DUT serial number (optional)")
            dut_manufacturer = self.get_user_input("Enter DUT manufacturer (optional)")
            operator_notes = self.get_user_input("Enter operator notes (optional)")
            
            # Test configuration
            config_input = self.get_user_input("Enter test configuration JSON (optional)")
            test_configuration = None
            if config_input:
                try:
                    test_configuration = json.loads(config_input)
                except json.JSONDecodeError:
                    self.print_warning("Invalid JSON format for test configuration, using default")
            
            # Pass criteria
            criteria_input = self.get_user_input("Enter pass criteria JSON (optional)")
            pass_criteria = None
            if criteria_input:
                try:
                    pass_criteria = json.loads(criteria_input)
                except json.JSONDecodeError:
                    self.print_warning("Invalid JSON format for pass criteria, using default")
            
            # Execute test
            self.print_info("Starting test execution...")
            self.show_spinner()
            
            result = await self._controller.execute_test(
                dut_id=dut_id,
                test_type=test_type,
                operator_id=operator_id,
                dut_model_number=dut_model if dut_model else None,
                dut_serial_number=dut_serial if dut_serial else None,
                dut_manufacturer=dut_manufacturer if dut_manufacturer else None,
                test_configuration=test_configuration,
                pass_criteria=pass_criteria,
                operator_notes=operator_notes if operator_notes else None
            )
            
            self.hide_spinner()
            
            # Display result
            if result['success']:
                self.print_success("Test execution completed!")
                self._display_test_result(result)
            else:
                self.print_error("Test execution failed!")
                self._display_error_result(result)
                
        except KeyboardInterrupt:
            self.hide_spinner()
            self.print_warning("Test execution cancelled by user")
        except Exception as e:
            self.hide_spinner()
            self.print_error(f"Unexpected error: {str(e)}")
            logger.error(f"CLI error during test execution: {e}")
    
    async def execute_test_command(
        self,
        dut_id: str,
        test_type: str,
        operator_id: str,
        dut_model: Optional[str] = None,
        dut_serial: Optional[str] = None,
        dut_manufacturer: Optional[str] = None,
        config_file: Optional[str] = None,
        criteria_file: Optional[str] = None,
        notes: Optional[str] = None,
        output_format: str = "table"
    ) -> None:
        """
        Execute test from command line arguments
        
        Args:
            dut_id: DUT identifier
            test_type: Type of test
            operator_id: Operator identifier
            dut_model: DUT model number (optional)
            dut_serial: DUT serial number (optional)
            dut_manufacturer: DUT manufacturer (optional)
            config_file: Test configuration file path (optional)
            criteria_file: Pass criteria file path (optional)
            notes: Operator notes (optional)
            output_format: Output format ('table', 'json', 'yaml')
        """
        try:
            # Load configuration from file if provided
            test_configuration = None
            if config_file:
                test_configuration = self._load_json_file(config_file)
            
            # Load pass criteria from file if provided
            pass_criteria = None
            if criteria_file:
                pass_criteria = self._load_json_file(criteria_file)
            
            # Execute test
            result = await self._controller.execute_test(
                dut_id=dut_id,
                test_type=test_type,
                operator_id=operator_id,
                dut_model_number=dut_model,
                dut_serial_number=dut_serial,
                dut_manufacturer=dut_manufacturer,
                test_configuration=test_configuration,
                pass_criteria=pass_criteria,
                operator_notes=notes
            )
            
            # Output result in requested format
            if output_format.lower() == 'json':
                self.print_json(result)
            elif output_format.lower() == 'yaml':
                self.print_yaml(result)
            else:
                if result['success']:
                    self._display_test_result(result)
                else:
                    self._display_error_result(result)
                    
        except Exception as e:
            self.print_error(f"Test execution failed: {str(e)}")
            logger.error(f"CLI command error: {e}")
    
    async def get_test_status_command(self, test_id: str, output_format: str = "table") -> None:
        """
        Get test status from command line
        
        Args:
            test_id: Test identifier
            output_format: Output format ('table', 'json', 'yaml')
        """
        try:
            result = await self._controller.get_test_status(test_id)
            
            if output_format.lower() == 'json':
                self.print_json(result)
            elif output_format.lower() == 'yaml':
                self.print_yaml(result)
            else:
                if result['success']:
                    self.print_success(f"Test Status for {test_id}")
                    self.print_key_value("Status", result.get('status', 'Unknown'))
                else:
                    self._display_error_result(result)
                    
        except Exception as e:
            self.print_error(f"Failed to get test status: {str(e)}")
    
    def _display_test_result(self, result: dict) -> None:
        """Display test execution result in table format"""
        self.print_section_header("Test Execution Result")
        
        # Basic test information
        self.print_key_value("Test ID", result.get('test_id', 'N/A'))
        self.print_key_value("Test Type", result.get('test_type', 'N/A'))
        self.print_key_value("Status", result.get('status', 'N/A'))
        
        # Test outcome
        passed = result.get('passed', False)
        if passed:
            self.print_key_value("Result", "PASSED", color="green")
        else:
            self.print_key_value("Result", "FAILED", color="red")
        
        # Execution details
        duration = result.get('execution_duration_ms', 0)
        self.print_key_value("Duration", f"{duration:.1f} ms")
        self.print_key_value("Measurements", str(result.get('measurement_count', 0)))
        
        # Test summary
        summary = result.get('test_summary', {})
        if summary:
            self.print_section_header("Test Summary")
            for key, value in summary.items():
                self.print_key_value(key.replace('_', ' ').title(), str(value))
        
        # Error message if any
        error_msg = result.get('error_message')
        if error_msg:
            self.print_section_header("Error Information")
            self.print_error(error_msg)
        
        # Operator notes
        notes = result.get('operator_notes')
        if notes:
            self.print_section_header("Operator Notes")
            self.print_info(notes)
        
        # Measurement IDs
        measurement_ids = result.get('measurement_ids', [])
        if measurement_ids:
            self.print_section_header("Measurement IDs")
            for i, mid in enumerate(measurement_ids, 1):
                self.print_info(f"  {i}. {mid}")
    
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
        
        # Suggestions
        suggestions = error.get('suggestions', [])
        if suggestions:
            self.print_section_header("Suggestions")
            for suggestion in suggestions:
                self.print_info(f"• {suggestion}")
    
    def _load_json_file(self, file_path: str) -> dict:
        """Load JSON configuration from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.print_error(f"Configuration file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            self.print_error(f"Invalid JSON in file {file_path}: {str(e)}")
            raise
        except Exception as e:
            self.print_error(f"Error loading file {file_path}: {str(e)}")
            raise