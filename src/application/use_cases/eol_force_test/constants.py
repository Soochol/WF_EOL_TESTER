"""
Constants for EOL Force Test Execution

Extracted constants used throughout EOL test execution for better maintainability.
"""


class TestExecutionConstants:
    """Constants used throughout EOL test execution"""

    # Error messages - Configuration
    TEST_CONFIG_REQUIRED_ERROR = "Test configuration is required but was not loaded. Please ensure configuration is loaded before test execution."
    HARDWARE_CONFIG_REQUIRED_ERROR = "Hardware configuration is required but was not loaded. Please ensure hardware configuration is loaded before test execution."
    TEST_EVALUATION_FAILED_PREFIX = "Test evaluation failed: "
    CONFIG_VALIDATION_FAILED_PREFIX = "Configuration validation failed: "
    TEST_CONFIG_BEFORE_EVALUATION_ERROR = "Test configuration must be loaded before evaluation can begin. Please ensure configuration loading completed successfully."

    # Error messages - Hardware
    HARDWARE_TEST_EXECUTION_ERROR_PREFIX = "Hardware test execution failed"
    HARDWARE_CONNECTION_ERROR = "Failed to establish connection with hardware devices"
    HARDWARE_CONFIGURATION_ERROR = "Failed to configure hardware with test parameters"

    # Error messages - Test Execution
    TEST_ENTITY_CREATION_ERROR = "Failed to create test entity for DUT"
    TEST_ID_GENERATION_ERROR = "Failed to generate unique test ID after maximum attempts"
    MEASUREMENT_CONVERSION_ERROR = "Failed to convert measurements for evaluation"

    # Operations for exception context
    EXECUTE_EOL_TEST_OPERATION = "execute_eol_test"
    HARDWARE_SHUTDOWN_OPERATION = "hardware_shutdown_cleanup"

    # Logging messages - Test Execution
    LOG_TEST_EXECUTION_START = "Starting EOL test execution for DUT {}"
    LOG_TEST_EXECUTION_COMPLETED = "EOL test execution completed: {}, result: {}"
    LOG_TEST_SETUP_COMPLETED = "Test setup completed for test entity {}"

    # Logging messages - Test Evaluation
    LOG_TEST_EVALUATION_START = "Starting test result evaluation and analysis"
    LOG_TEST_EVALUATION_PASSED = "Test evaluation: PASSED"
    LOG_TEST_EVALUATION_FAILED = "Test evaluation: FAILED - {}"

    # Logging messages - Hardware Operations
    LOG_HARDWARE_TEST_START = "Starting hardware test phase execution"
    LOG_HARDWARE_TEST_COMPLETED = "Hardware test phases completed, {} measurements collected"
    LOG_HARDWARE_CONNECTION_START = "Starting hardware connection initialization..."
    LOG_HARDWARE_CONNECTION_SUCCESS = "Hardware connections initialized successfully"
    LOG_HARDWARE_CONFIG_START = "Configuring hardware with test parameters..."
    LOG_HARDWARE_CONFIG_SUCCESS = "Hardware configuration completed"
    LOG_HARDWARE_CLEANUP_SUCCESS = "Hardware resources cleaned up successfully"

    # Logging messages - Configuration
    LOG_CONFIG_VALIDATION_SUCCESS = "Configuration validation passed"
    LOG_CONFIG_LOAD_SUCCESS = "Hardware configuration loaded successfully"

    # Logging messages - State Management
    LOG_TEST_STATE_SAVED = "Test entity state saved successfully for test ID: {}"
    LOG_TEST_STATE_SAVE_FAILED = "Failed to save test state: {}"
    LOG_MEASUREMENT_IDS_GENERATED = "Generated {} measurement IDs"

    # Test result status labels
    TEST_RESULT_PASSED = "PASSED"
    TEST_RESULT_FAILED = "FAILED"

    # Sequence generation constants
    MAX_TEST_ID_ATTEMPTS = 999
    INITIAL_SEQUENCE = 1
    MEASUREMENT_ID_FORMAT = "M{:010d}"

    # Timeout constants
    DEFAULT_HARDWARE_OPERATION_TIMEOUT = 30.0

    # Logging messages - Repeated Test Cycles
    LOG_REPEATED_TEST_START = "🔄 Starting repeated test execution: {} repetitions for DUT {}"
    LOG_REPEATED_TEST_COMPLETED = "📊 Repeated test completed: {}/{} cycles passed (total {:.1f}s) - DUT {}"
    LOG_CYCLE_START = "Cycle {}/{} starting"
    LOG_CYCLE_START_WITH_TIME = "Cycle {}/{} starting - estimated completion time: {}"
    LOG_CYCLE_START_WITH_REMAINING = "Cycle {}/{} starting - estimated remaining time: {:.1f}s"
    LOG_CYCLE_COMPLETED_PASS = "✅ Cycle {}/{} completed ({:.1f}s) - PASS | Progress: {}/{} passed"
    LOG_CYCLE_COMPLETED_FAIL = "❌ Cycle {}/{} completed ({:.1f}s) - FAIL | Progress: {}/{} passed"
    LOG_CYCLE_ERROR = "⚠️ Cycle {}/{} error - DUT {}: {}"
    LOG_CYCLE_DELAY = "⏳ Waiting {:.1f}s until next cycle..."

    # Enhanced Cycle Header Display Constants
    CYCLE_HEADER_SEPARATOR = "═" * 50
    CYCLE_HEADER_FORMAT = "🔄 Test Cycle {}/{}"
    CYCLE_HEADER_COLOR_START = "\033[44;97;1m"  # Blue background, white text, bold
    CYCLE_HEADER_COLOR_END = "\033[0m"  # Reset color
