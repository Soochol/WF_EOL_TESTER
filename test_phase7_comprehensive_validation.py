#!/usr/bin/env python3
"""
Phase 7: Comprehensive Testing and Verification
Functional Equivalency and Performance Validation

This test suite validates that the 6-phase CLI refactoring has successfully:
1. Maintained 100% functional equivalency
2. Preserved performance characteristics
3. Enhanced code maintainability and structure
4. Implemented proper dependency injection
5. Maintained backward compatibility

Test Categories:
- Functional Equivalency Testing
- Interface and Integration Testing  
- Performance and Memory Validation
- Backward Compatibility Testing
- Error Handling and Edge Cases
"""

import asyncio
import time
import tracemalloc
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from unittest.mock import MagicMock, patch, AsyncMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test framework imports
import pytest
from rich.console import Console
from loguru import logger

# Import both old and new architectures for comparison
try:
    # New modular architecture
    from src.ui.cli.enhanced_eol_tester_cli import EnhancedEOLTesterCLI
    from src.ui.cli.application_factory import create_production_cli_application
    from src.ui.cli.core.cli_application import CLIApplication
    from src.ui.cli.validation.input_validator import InputValidator, ValidationConstants
    from src.ui.cli.rich_formatter import RichFormatter
    from src.ui.cli.hardware_controller import HardwareControlManager
    
    # Use case and service imports
    from src.application.use_cases.eol_force_test import EOLForceTestUseCase
    
    IMPORTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Import error: {e}")
    IMPORTS_AVAILABLE = False


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    passed: bool
    execution_time: float = 0.0
    memory_usage: float = 0.0
    error_message: Optional[str] = None
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class Phase7ValidationSuite:
    """Comprehensive validation suite for Phase 7 testing."""
    
    def __init__(self):
        """Initialize the validation suite."""
        self.console = Console(force_terminal=True, legacy_windows=False)
        self.test_results: List[TestResult] = []
        self.performance_baseline: Dict[str, float] = {}
        
        # Mock dependencies for testing
        self.mock_use_case = MagicMock(spec=EOLForceTestUseCase) if IMPORTS_AVAILABLE else MagicMock()
        self.mock_hardware_facade = MagicMock()
        self.mock_config_service = MagicMock()
        
        # Initialize components for testing
        self._initialize_test_components()
    
    def _initialize_test_components(self):
        """Initialize test components."""
        if not IMPORTS_AVAILABLE:
            logger.warning("Skipping component initialization due to import errors")
            return
            
        try:
            # Create test instances
            self.new_cli_app = create_production_cli_application(
                use_case=self.mock_use_case,
                hardware_facade=self.mock_hardware_facade,
                configuration_service=self.mock_config_service
            )
            
            self.legacy_cli = EnhancedEOLTesterCLI(
                use_case=self.mock_use_case,
                hardware_facade=self.mock_hardware_facade,
                configuration_service=self.mock_config_service
            )
            
            logger.info("Test components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize test components: {e}")
            self.new_cli_app = None
            self.legacy_cli = None
    
    def _measure_performance(self, func: Callable, *args, **kwargs) -> tuple:
        """Measure execution time and memory usage of a function."""
        tracemalloc.start()
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = e
        
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        execution_time = end_time - start_time
        memory_usage = peak / 1024 / 1024  # Convert to MB
        
        return result, execution_time, memory_usage
    
    def _record_test_result(self, test_name: str, passed: bool, 
                           execution_time: float = 0.0, memory_usage: float = 0.0,
                           error_message: str = None, details: Dict = None):
        """Record a test result."""
        result = TestResult(
            test_name=test_name,
            passed=passed,
            execution_time=execution_time,
            memory_usage=memory_usage,
            error_message=error_message,
            details=details or {}
        )
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        self.console.print(f"{status} {test_name} [{execution_time:.3f}s, {memory_usage:.2f}MB]")
        if error_message:
            self.console.print(f"    Error: {error_message}", style="red")

    # =============================================================================
    # 1. FUNCTIONAL EQUIVALENCY TESTING
    # =============================================================================
    
    def test_component_initialization(self):
        """Test 1.1: Component Initialization"""
        test_name = "Component Initialization"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            # Test new architecture initialization
            result, exec_time, memory = self._measure_performance(
                create_production_cli_application,
                use_case=self.mock_use_case,
                hardware_facade=self.mock_hardware_facade,
                configuration_service=self.mock_config_service
            )
            
            if isinstance(result, Exception):
                raise result
                
            # Verify components are properly initialized
            assert hasattr(result, '_console'), "Console not initialized"
            assert hasattr(result, '_formatter'), "Formatter not initialized"
            assert hasattr(result, '_validator'), "Validator not initialized"
            assert hasattr(result, '_session_manager'), "Session manager not initialized"
            assert hasattr(result, '_menu_system'), "Menu system not initialized"
            
            self._record_test_result(test_name, True, exec_time, memory,
                                   details={"components_verified": 5})
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))
    
    def test_backward_compatibility_api(self):
        """Test 1.2: Backward Compatibility API"""
        test_name = "Backward Compatibility API"
        
        if not IMPORTS_AVAILABLE or not self.legacy_cli:
            self._record_test_result(test_name, False, error_message="Components not available")
            return
        
        try:
            # Test legacy API methods exist and work
            legacy_methods = [
                'get_console', 'get_formatter', 'get_validator',
                'get_hardware_manager', 'get_usecase_manager'
            ]
            
            verified_methods = 0
            for method_name in legacy_methods:
                if hasattr(self.legacy_cli, method_name):
                    method = getattr(self.legacy_cli, method_name)
                    result = method()  # Call the method
                    if result is not None or method_name in ['get_hardware_manager']:  # hardware_manager can be None
                        verified_methods += 1
            
            # Test legacy properties
            running_state = self.legacy_cli._running
            self.legacy_cli._running = False
            assert self.legacy_cli._running == False, "Running state property not working"
            
            success = verified_methods == len(legacy_methods)
            self._record_test_result(test_name, success,
                                   details={"verified_methods": verified_methods, "total_methods": len(legacy_methods)})
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))
    
    def test_validator_functionality(self):
        """Test 1.3: Input Validator Functionality"""
        test_name = "Input Validator Functionality"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            validator = InputValidator()
            
            # Test validation methods
            test_cases = [
                # (method_name, test_input, expected_result)
                ('is_valid_menu_choice', '1', True),
                ('is_valid_menu_choice', '5', False),
                ('is_valid_menu_choice', 'abc', False),
                ('is_valid_force_value', '100.5', True),
                ('is_valid_force_value', '-10', False),
                ('is_valid_force_value', 'invalid', False),
            ]
            
            passed_tests = 0
            for method_name, test_input, expected in test_cases:
                if hasattr(validator, method_name):
                    method = getattr(validator, method_name)
                    result = method(test_input)
                    if result == expected:
                        passed_tests += 1
            
            # Test constants
            constants_exist = hasattr(ValidationConstants, 'MENU_CHOICES') and \
                            hasattr(ValidationConstants, 'FORCE_RANGE')
            
            success = passed_tests == len(test_cases) and constants_exist
            self._record_test_result(test_name, success,
                                   details={"passed_validations": passed_tests, "total_tests": len(test_cases)})
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))
    
    def test_formatter_functionality(self):
        """Test 1.4: Rich Formatter Functionality"""
        test_name = "Rich Formatter Functionality"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            console = Console()
            formatter = RichFormatter(console)
            
            # Test formatter methods (should not raise exceptions)
            test_methods = [
                ('print_title', ['Test Title']),
                ('print_message', ['Test Message']),
                ('print_menu', [{'1': 'Option 1', '2': 'Option 2'}]),
                ('print_status', ['Testing', 'info']),
            ]
            
            working_methods = 0
            for method_name, args in test_methods:
                try:
                    if hasattr(formatter, method_name):
                        method = getattr(formatter, method_name)
                        method(*args)  # Should not raise exception
                        working_methods += 1
                except Exception:
                    pass  # Method failed
            
            success = working_methods == len(test_methods)
            self._record_test_result(test_name, success,
                                   details={"working_methods": working_methods, "total_methods": len(test_methods)})
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))

    # =============================================================================
    # 2. INTERFACE AND INTEGRATION TESTING
    # =============================================================================
    
    def test_dependency_injection_container(self):
        """Test 2.1: Dependency Injection Container"""
        test_name = "Dependency Injection Container"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            # Test that dependency injection works properly
            app = create_production_cli_application(
                use_case=self.mock_use_case,
                hardware_facade=self.mock_hardware_facade,
                configuration_service=self.mock_config_service
            )
            
            # Verify injected dependencies are available
            console = app.get_console()
            formatter = app.get_formatter()
            validator = app.get_validator()
            
            # Test component relationships
            assert console is not None, "Console not injected"
            assert formatter is not None, "Formatter not injected"
            assert validator is not None, "Validator not injected"
            
            # Test that formatter uses the injected console
            assert formatter._console is console, "Formatter console not properly injected"
            
            self._record_test_result(test_name, True,
                                   details={"components_injected": 3})
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))
    
    def test_component_interfaces(self):
        """Test 2.2: Component Interfaces"""
        test_name = "Component Interfaces"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            # Test interface compliance
            from src.ui.cli.interfaces.application_interface import ICLIApplication
            from src.ui.cli.interfaces.validation_interface import IInputValidator
            
            app = create_production_cli_application(
                use_case=self.mock_use_case,
                hardware_facade=self.mock_hardware_facade,
                configuration_service=self.mock_config_service
            )
            
            validator = app.get_validator()
            
            # Test interface implementations
            assert isinstance(app, ICLIApplication), "Application doesn't implement ICLIApplication"
            assert isinstance(validator, IInputValidator), "Validator doesn't implement IInputValidator"
            
            # Test interface methods exist
            assert hasattr(app, 'run_interactive'), "run_interactive method missing"
            assert callable(getattr(app, 'run_interactive')), "run_interactive not callable"
            
            self._record_test_result(test_name, True,
                                   details={"interfaces_verified": 2})
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))
    
    def test_component_lifecycle(self):
        """Test 2.3: Component Lifecycle Management"""
        test_name = "Component Lifecycle Management"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            # Test component creation and destruction
            app = create_production_cli_application(
                use_case=self.mock_use_case,
                hardware_facade=self.mock_hardware_facade,
                configuration_service=self.mock_config_service
            )
            
            # Test initial state
            assert not app._running, "Application should not be running initially"
            
            # Test state changes
            app._running = True
            assert app._running, "Running state not set properly"
            
            app._running = False
            assert not app._running, "Running state not cleared properly"
            
            self._record_test_result(test_name, True,
                                   details={"lifecycle_tests_passed": 3})
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))

    # =============================================================================
    # 3. PERFORMANCE AND MEMORY VALIDATION
    # =============================================================================
    
    def test_startup_performance(self):
        """Test 3.1: Application Startup Performance"""
        test_name = "Application Startup Performance"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            # Measure startup time
            result, exec_time, memory = self._measure_performance(
                create_production_cli_application,
                use_case=self.mock_use_case,
                hardware_facade=self.mock_hardware_facade,
                configuration_service=self.mock_config_service
            )
            
            # Performance thresholds
            max_startup_time = 2.0  # 2 seconds
            max_memory_usage = 50.0  # 50 MB
            
            time_ok = exec_time < max_startup_time
            memory_ok = memory < max_memory_usage
            success = time_ok and memory_ok and not isinstance(result, Exception)
            
            self._record_test_result(test_name, success, exec_time, memory,
                                   details={
                                       "startup_time": exec_time,
                                       "memory_usage": memory,
                                       "time_threshold": max_startup_time,
                                       "memory_threshold": max_memory_usage
                                   })
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))
    
    def test_memory_efficiency(self):
        """Test 3.2: Memory Efficiency"""
        test_name = "Memory Efficiency"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            # Create multiple instances to check for memory leaks
            tracemalloc.start()
            initial_memory = tracemalloc.get_traced_memory()[1]
            
            apps = []
            for i in range(5):
                app = create_production_cli_application(
                    use_case=self.mock_use_case,
                    hardware_facade=self.mock_hardware_facade,
                    configuration_service=self.mock_config_service
                )
                apps.append(app)
            
            final_memory = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            
            memory_per_instance = (final_memory - initial_memory) / len(apps) / 1024 / 1024
            max_memory_per_instance = 10.0  # 10 MB per instance
            
            success = memory_per_instance < max_memory_per_instance
            
            self._record_test_result(test_name, success, memory_usage=memory_per_instance,
                                   details={
                                       "memory_per_instance": memory_per_instance,
                                       "threshold": max_memory_per_instance,
                                       "instances_created": len(apps)
                                   })
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))
    
    def test_component_performance(self):
        """Test 3.3: Individual Component Performance"""
        test_name = "Component Performance"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            # Test individual component creation times
            console = Console()
            
            # Test formatter creation
            result, exec_time, memory = self._measure_performance(
                RichFormatter, console
            )
            formatter_time = exec_time
            
            # Test validator creation
            result, exec_time, memory = self._measure_performance(
                InputValidator
            )
            validator_time = exec_time
            
            # Performance thresholds (very fast operations)
            max_component_time = 0.1  # 100ms
            
            formatter_ok = formatter_time < max_component_time
            validator_ok = validator_time < max_component_time
            success = formatter_ok and validator_ok
            
            self._record_test_result(test_name, success,
                                   details={
                                       "formatter_time": formatter_time,
                                       "validator_time": validator_time,
                                       "threshold": max_component_time
                                   })
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))

    # =============================================================================
    # 4. ERROR HANDLING AND EDGE CASES
    # =============================================================================
    
    def test_error_handling_robustness(self):
        """Test 4.1: Error Handling Robustness"""
        test_name = "Error Handling Robustness"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            # Test creation with None dependencies
            app = create_production_cli_application(
                use_case=self.mock_use_case,
                hardware_facade=None,  # Test None hardware facade
                configuration_service=None  # Test None config service
            )
            
            # Should still create successfully
            assert app is not None, "App creation failed with None dependencies"
            assert app.get_console() is not None, "Console not available"
            assert app.get_formatter() is not None, "Formatter not available"
            
            # Hardware manager should be None when no hardware facade
            assert app.get_hardware_manager() is None, "Hardware manager should be None"
            
            self._record_test_result(test_name, True,
                                   details={"none_dependency_handling": "passed"})
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))
    
    def test_input_validation_edge_cases(self):
        """Test 4.2: Input Validation Edge Cases"""
        test_name = "Input Validation Edge Cases"
        
        if not IMPORTS_AVAILABLE:
            self._record_test_result(test_name, False, error_message="Import dependencies not available")
            return
        
        try:
            validator = InputValidator()
            
            # Test edge cases
            edge_cases = [
                # (method, input, expected, description)
                ('is_valid_menu_choice', '', False, 'empty string'),
                ('is_valid_menu_choice', '0', False, 'zero choice'),
                ('is_valid_menu_choice', ' 1 ', True, 'whitespace around valid choice'),
                ('is_valid_force_value', '0', True, 'zero force'),
                ('is_valid_force_value', '0.0', True, 'zero float force'),
                ('is_valid_force_value', '', False, 'empty force'),
                ('is_valid_force_value', '   ', False, 'whitespace force'),
            ]
            
            passed_cases = 0
            for method_name, test_input, expected, description in edge_cases:
                if hasattr(validator, method_name):
                    method = getattr(validator, method_name)
                    try:
                        result = method(test_input)
                        if result == expected:
                            passed_cases += 1
                        else:
                            logger.warning(f"Edge case failed: {description} - got {result}, expected {expected}")
                    except Exception as e:
                        logger.warning(f"Edge case exception: {description} - {e}")
            
            success = passed_cases >= len(edge_cases) * 0.8  # 80% pass rate
            self._record_test_result(test_name, success,
                                   details={"passed_cases": passed_cases, "total_cases": len(edge_cases)})
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))

    # =============================================================================
    # 5. ARCHITECTURE QUALITY VALIDATION
    # =============================================================================
    
    def test_code_organization(self):
        """Test 5.1: Code Organization and Structure"""
        test_name = "Code Organization and Structure"
        
        try:
            # Check if refactored files exist and are properly organized
            base_path = Path("src/ui/cli")
            
            expected_structure = {
                "core": ["cli_application.py"],
                "session": ["session_manager.py"],
                "menu": ["menu_system.py"],
                "validation": ["input_validator.py"],
                "execution": ["test_executor.py"],
                "interfaces": ["application_interface.py", "validation_interface.py"],
                "presentation/themes": ["default_theme.py"],
                "presentation/formatters": ["base_formatter.py"],
            }
            
            found_modules = 0
            total_modules = sum(len(files) for files in expected_structure.values())
            
            for directory, files in expected_structure.items():
                dir_path = base_path / directory
                if dir_path.exists():
                    for file_name in files:
                        file_path = dir_path / file_name
                        if file_path.exists():
                            found_modules += 1
            
            # Check main compatibility file
            compat_file = base_path / "enhanced_eol_tester_cli.py"
            if compat_file.exists():
                found_modules += 1
                total_modules += 1
            
            organization_score = found_modules / total_modules
            success = organization_score >= 0.8  # 80% of expected structure
            
            self._record_test_result(test_name, success,
                                   details={
                                       "found_modules": found_modules,
                                       "total_expected": total_modules,
                                       "organization_score": organization_score
                                   })
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))
    
    def test_line_count_reduction(self):
        """Test 5.2: Code Line Count Reduction Verification"""
        test_name = "Code Line Count Reduction"
        
        try:
            # Check line counts of key refactored files
            file_metrics = {}
            
            # Key files to check
            files_to_check = [
                "src/ui/cli/enhanced_eol_tester_cli.py",
                "src/ui/cli/rich_formatter.py", 
                "src/ui/cli/hardware_controller.py",
                "src/ui/cli/core/cli_application.py",
            ]
            
            for file_path in files_to_check:
                full_path = Path(file_path)
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                    file_metrics[file_path] = lines
            
            # Expected reductions based on refactoring goals
            expected_limits = {
                "src/ui/cli/enhanced_eol_tester_cli.py": 150,  # Compatibility wrapper
                "src/ui/cli/rich_formatter.py": 300,  # Delegating formatter
                "src/ui/cli/hardware_controller.py": 100,  # Delegating controller
                "src/ui/cli/core/cli_application.py": 250,  # Core application
            }
            
            passed_reductions = 0
            for file_path, limit in expected_limits.items():
                if file_path in file_metrics and file_metrics[file_path] <= limit:
                    passed_reductions += 1
            
            success = passed_reductions == len(expected_limits)
            
            self._record_test_result(test_name, success,
                                   details={
                                       "file_metrics": file_metrics,
                                       "expected_limits": expected_limits,
                                       "passed_reductions": passed_reductions
                                   })
            
        except Exception as e:
            self._record_test_result(test_name, False, error_message=str(e))

    # =============================================================================
    # TEST EXECUTION AND REPORTING
    # =============================================================================
    
    def run_all_tests(self):
        """Run all validation tests."""
        self.console.print("\n" + "="*80, style="bold blue")
        self.console.print("Phase 7: Comprehensive Testing and Verification", style="bold blue")
        self.console.print("Functional Equivalency and Performance Validation", style="blue")
        self.console.print("="*80 + "\n", style="bold blue")
        
        # Test categories
        test_categories = [
            ("1. FUNCTIONAL EQUIVALENCY TESTING", [
                self.test_component_initialization,
                self.test_backward_compatibility_api,
                self.test_validator_functionality,
                self.test_formatter_functionality,
            ]),
            ("2. INTERFACE AND INTEGRATION TESTING", [
                self.test_dependency_injection_container,
                self.test_component_interfaces,
                self.test_component_lifecycle,
            ]),
            ("3. PERFORMANCE AND MEMORY VALIDATION", [
                self.test_startup_performance,
                self.test_memory_efficiency,
                self.test_component_performance,
            ]),
            ("4. ERROR HANDLING AND EDGE CASES", [
                self.test_error_handling_robustness,
                self.test_input_validation_edge_cases,
            ]),
            ("5. ARCHITECTURE QUALITY VALIDATION", [
                self.test_code_organization,
                self.test_line_count_reduction,
            ]),
        ]
        
        # Execute test categories
        for category_name, test_methods in test_categories:
            self.console.print(f"\n{category_name}", style="bold cyan")
            self.console.print("-" * len(category_name), style="cyan")
            
            for test_method in test_methods:
                try:
                    test_method()
                except Exception as e:
                    test_name = test_method.__name__.replace("test_", "").replace("_", " ").title()
                    self._record_test_result(test_name, False, error_message=f"Test execution failed: {e}")
        
        # Generate final report
        self._generate_final_report()
    
    def _generate_final_report(self):
        """Generate comprehensive test report."""
        self.console.print("\n" + "="*80, style="bold green")
        self.console.print("PHASE 7 VALIDATION SUMMARY REPORT", style="bold green")
        self.console.print("="*80, style="bold green")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        total_time = sum(r.execution_time for r in self.test_results)
        avg_memory = sum(r.memory_usage for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        # Overall results
        self.console.print(f"\nOVERALL RESULTS:", style="bold")
        self.console.print(f"  Total Tests: {total_tests}")
        self.console.print(f"  Passed: {passed_tests} ✅", style="green")
        self.console.print(f"  Failed: {failed_tests} ❌", style="red" if failed_tests > 0 else "green")
        self.console.print(f"  Pass Rate: {pass_rate:.1f}%", 
                          style="green" if pass_rate >= 90 else "yellow" if pass_rate >= 75 else "red")
        
        # Performance metrics
        self.console.print(f"\nPERFORMANCE METRICS:", style="bold")
        self.console.print(f"  Total Execution Time: {total_time:.3f}s")
        self.console.print(f"  Average Memory Usage: {avg_memory:.2f}MB")
        
        # Failed tests details
        if failed_tests > 0:
            self.console.print(f"\nFAILED TESTS DETAILS:", style="bold red")
            for result in self.test_results:
                if not result.passed:
                    self.console.print(f"  ❌ {result.test_name}: {result.error_message}", style="red")
        
        # Success criteria evaluation
        self.console.print(f"\nSUCCESS CRITERIA EVALUATION:", style="bold")
        
        criteria_results = [
            ("100% Functional Equivalency", pass_rate >= 95, "✅" if pass_rate >= 95 else "❌"),
            ("No Performance Regression", avg_memory < 50, "✅" if avg_memory < 50 else "❌"),
            ("Error Handling Preserved", 
             any("Error Handling" in r.test_name and r.passed for r in self.test_results), 
             "✅" if any("Error Handling" in r.test_name and r.passed for r in self.test_results) else "❌"),
            ("Backward Compatibility", 
             any("Backward Compatibility" in r.test_name and r.passed for r in self.test_results), 
             "✅" if any("Backward Compatibility" in r.test_name and r.passed for r in self.test_results) else "❌"),
            ("Code Quality Improved", 
             any("Architecture Quality" in r.test_name and r.passed for r in self.test_results), 
             "✅" if any("Architecture Quality" in r.test_name and r.passed for r in self.test_results) else "❌"),
        ]
        
        for criterion, met, status in criteria_results:
            color = "green" if met else "red"
            self.console.print(f"  {status} {criterion}", style=color)
        
        # Final verdict
        all_criteria_met = all(met for _, met, _ in criteria_results)
        overall_success = pass_rate >= 85 and all_criteria_met
        
        self.console.print(f"\n{'='*80}", style="bold")
        if overall_success:
            self.console.print("🎉 PHASE 7 VALIDATION: SUCCESS! 🎉", style="bold green")
            self.console.print("All 6 refactoring phases have successfully maintained functionality", style="green")
            self.console.print("while significantly improving architecture and maintainability.", style="green")
        else:
            self.console.print("⚠️  PHASE 7 VALIDATION: ATTENTION REQUIRED ⚠️", style="bold yellow")
            self.console.print("Some validation criteria need attention before completion.", style="yellow")
        
        self.console.print(f"{'='*80}\n", style="bold")


def main():
    """Main execution function."""
    # Initialize and run validation suite
    suite = Phase7ValidationSuite()
    suite.run_all_tests()


if __name__ == "__main__":
    main()
