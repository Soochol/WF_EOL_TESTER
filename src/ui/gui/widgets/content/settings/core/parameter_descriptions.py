"""
Parameter descriptions for Settings UI.

Contains detailed descriptions for all configuration parameters
to provide user-friendly explanations in the Settings panel.
"""

from typing import Dict


class ParameterDescriptions:
    """Central repository for parameter descriptions"""

    # Hardware Configuration Descriptions
    HARDWARE_DESCRIPTIONS: Dict[str, str] = {
        "hardware.voltage": "Operating voltage for the power supply (V). Typical range: 18-40V.",
        "hardware.current": "Operating current for the power supply (A). Typical range: 15-25A.",
        "hardware.upper_current": "Maximum current limit for safety protection (A).",
        "hardware.upper_temperature": "Maximum temperature limit for MCU controller (°C).",
        "hardware.activation_temperature": "Temperature threshold for device activation (°C).",
        "hardware.standby_temperature": "Standby mode temperature setpoint (°C).",
        "hardware.fan_speed": "Cooling fan speed (0-10). 0 = off, 10 = maximum speed.",
        "hardware.operating_position": "Maximum stroke length for robot movement (μm).",
        "hardware.initial_position": "Starting position for robot homing (μm).",
    }

    # Motion Control Descriptions
    MOTION_DESCRIPTIONS: Dict[str, str] = {
        "motion_control.velocity": "Robot movement velocity (μm/s). Higher = faster movement.",
        "motion_control.acceleration": "Robot acceleration rate (μm/s²). Higher = faster speed changes.",
        "motion_control.deceleration": "Robot deceleration rate (μm/s²). Higher = faster stops.",
    }

    # Timing Descriptions
    TIMING_DESCRIPTIONS: Dict[str, str] = {
        "timing.robot_move_stabilization": "Delay after robot movement to allow mechanical stabilization (seconds).",
        "timing.mcu_temperature_stabilization": "Delay after temperature change for thermal stabilization (seconds).",
        "timing.robot_standby_stabilization": "Delay for standby heating stabilization (seconds).",
        "timing.poweron_stabilization": "Delay after power on for system stabilization (seconds).",
        "timing.power_command_stabilization": "Delay after power command execution (seconds).",
        "timing.loadcell_zero_delay": "Delay for load cell zeroing operation (seconds).",
        "timing.mcu_command_stabilization": "Delay after MCU command execution (seconds).",
        "timing.mcu_boot_complete_stabilization": "Delay for MCU boot completion (seconds).",
    }

    # Test Parameters Descriptions
    TEST_DESCRIPTIONS: Dict[str, str] = {
        "test_parameters.temperature_list": "List of temperature test points (°C) for force measurement.",
        "test_parameters.stroke_positions": "List of stroke positions (μm) for force measurement.",
    }

    # Safety Descriptions
    SAFETY_DESCRIPTIONS: Dict[str, str] = {
        "safety.max_voltage": "Maximum allowed voltage for safety protection (V).",
        "safety.max_current": "Maximum allowed current for safety protection (A).",
        "safety.max_velocity": "Maximum allowed robot velocity for safety (μm/s).",
        "safety.max_acceleration": "Maximum allowed acceleration for safety (μm/s²).",
        "safety.max_deceleration": "Maximum allowed deceleration for safety (μm/s²).",
        "safety.max_stroke": "Maximum allowed stroke length for safety (μm).",
    }

    # Execution Descriptions
    EXECUTION_DESCRIPTIONS: Dict[str, str] = {
        "execution.retry_attempts": "Number of retry attempts on test failure (0-10).",
        "execution.timeout_seconds": "Maximum allowed test duration before timeout (seconds).",
        "execution.repeat_count": "Number of times to repeat the entire test sequence (1-100).",
    }

    # Tolerances Descriptions
    TOLERANCE_DESCRIPTIONS: Dict[str, str] = {
        "tolerances.measurement_tolerance": "General measurement precision tolerance for stability checks.",
        "tolerances.force_precision": "Number of decimal places for force value display (0-10).",
        "tolerances.temperature_precision": "Number of decimal places for temperature value display (0-5).",
        "tolerances.temperature_tolerance": "Allowed temperature deviation from target (±°C).",
    }

    # Pass Criteria Descriptions
    PASS_CRITERIA_DESCRIPTIONS: Dict[str, str] = {
        "pass_criteria.force_limit_min": "Minimum acceptable force measurement (kgf). Used when spec_points is empty.",
        "pass_criteria.force_limit_max": "Maximum acceptable force measurement (kgf). Used when spec_points is empty.",
        "pass_criteria.temperature_limit_min": "Minimum acceptable temperature (°C).",
        "pass_criteria.temperature_limit_max": "Maximum acceptable temperature (°C).",
        "pass_criteria.spec_points": "⚠️ Force validation specification points. Empty ([]) = ALL PASS (validation disabled). Format: [temperature(°C), stroke(μm), upper_limit(kgf), lower_limit(kgf)]",
        "pass_criteria.position_tolerance": "Allowed position deviation from target (±mm).",
        "pass_criteria.max_test_duration": "Maximum allowed test duration (seconds).",
        "pass_criteria.min_stabilization_time": "Minimum required stabilization time (seconds).",
        "pass_criteria.measurement_tolerance": "General measurement precision tolerance.",
        "pass_criteria.force_precision": "Force value decimal places (0-10).",
        "pass_criteria.temperature_precision": "Temperature value decimal places (0-5).",
        "pass_criteria.enable_pass_fail_judgment": "Enable or disable pass/fail criteria enforcement. When disabled, all tests are marked as PASS regardless of measurement values.",
    }

    # Hardware Device Descriptions
    HARDWARE_DEVICE_DESCRIPTIONS: Dict[str, str] = {
        # Robot Configuration
        "robot.model": "Robot controller model. Options: 'mock' (simulation) or 'ajinextek' (real hardware).",
        "robot.connection.library_path": "Path to Ajinextek AXL library files for robot control.",
        "robot.axis_id": "Robot axis identifier (0-7) for multi-axis motion control systems.",
        "robot.irq_no": "Hardware interrupt request (IRQ) number for real-time robot control (typically 7-15).",
        "robot.timeout": "Maximum time (seconds) to wait for robot operation completion before timeout error.",
        "robot.polling_interval": "Robot status polling interval in milliseconds (e.g., 250ms = 4Hz update rate).",

        # Loadcell Configuration
        "loadcell.model": "Load cell amplifier model. Options: 'mock' (simulation) or 'bs205' (real hardware).",
        "loadcell.connection.port": "Serial port for BS205 load cell (e.g., COM1, COM2, /dev/ttyUSB0).",
        "loadcell.connection.baudrate": "Serial communication baud rate (bps). Common: 9600, 115200.",
        "loadcell.port": "Serial port for load cell communication (Windows: COM1-COM256, Linux: /dev/ttyUSB*).",
        "loadcell.baudrate": "Serial baud rate (bits per second). Standard: 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200.",
        "loadcell.timeout": "Serial communication timeout in seconds. Increase if experiencing timeout errors.",
        "loadcell.bytesize": "Number of data bits per byte. Options: 5, 6, 7, 8 (8 is standard).",
        "loadcell.stopbits": "Number of stop bits. Options: 1, 1.5, 2 (1 is standard).",
        "loadcell.parity": "Parity checking mode. Options: 'none', 'even', 'odd', 'mark', 'space' (even/none most common).",
        "loadcell.indicator_id": "Load cell indicator device ID for multi-device systems (0-255).",

        # MCU Configuration
        "mcu.model": "Microcontroller model. Options: 'mock' (simulation) or 'lma' (real hardware).",
        "mcu.connection.port": "Serial port for LMA microcontroller communication.",
        "mcu.connection.baudrate": "Serial baud rate for MCU (typically 115200 for high-speed data transfer).",
        "mcu.port": "Serial port for MCU communication (Windows: COM1-COM256, Linux: /dev/ttyUSB*).",
        "mcu.baudrate": "MCU serial baud rate (bps). Typical: 9600, 115200. Higher = faster but less reliable over long distances.",
        "mcu.timeout": "MCU communication timeout in seconds (recommend 5-10s for reliable operation).",
        "mcu.bytesize": "Serial data bits (8 is standard for modern MCUs).",
        "mcu.stopbits": "Serial stop bits (1 is standard).",
        "mcu.parity": "Serial parity checking. Options: null (none), 'even', 'odd'. Typically null for MCU communication.",

        # Power Supply Configuration
        "power.model": "Power supply model. Options: 'mock' (simulation) or 'oda' (real hardware).",
        "power.connection.host": "IP address of ODA power supply for Ethernet/TCP connection (e.g., 192.168.1.10).",
        "power.connection.port": "TCP/IP port number for power supply communication (default: 5000).",
        "power.host": "Power supply IP address for network communication.",
        "power.port": "TCP port number for power supply remote control (typically 5000-8000).",
        "power.timeout": "Network communication timeout in seconds (recommend 5-10s).",
        "power.channel": "Power supply output channel number (1-4, depending on model capacity).",
        "power.delimiter": "Command delimiter character for power supply protocol (usually newline or carriage return).",

        # Power Analyzer Configuration (Hardware-level defaults)
        "power_analyzer.model": "Power analyzer model. Options: 'mock' (simulation) or 'wt1800e' (Yokogawa WT1800E).",
        "power_analyzer.host": "Power analyzer IP address for network communication (e.g., 192.168.1.100).",
        "power_analyzer.port": "TCP port number for power analyzer communication (default WT1800E: 10001).",
        "power_analyzer.timeout": "Network communication timeout in seconds (recommend 5-10s).",
        "power_analyzer.element": "Default measurement element/channel number (1-6 for WT1800E). Can be overridden by test config.",
        "power_analyzer.voltage_range": "Default voltage measurement range (e.g., '15V', '30V', '60V', '150V', '300V', '600V', '1000V'). null = auto-range.",
        "power_analyzer.current_range": "Default current measurement range (e.g., '1A', '2A', '5A', '10A', '20A', '50A'). null = auto-range.",
        "power_analyzer.auto_range": "Enable automatic range adjustment for optimal accuracy. Recommended for most use cases.",
        "power_analyzer.line_filter": "Default line filter frequency for noise reduction (e.g., '500HZ', '1KHZ', '10KHZ', '100KHZ'). null = device default.",
        "power_analyzer.frequency_filter": "Default frequency filter for signal processing (e.g., '0.5HZ', '1HZ', '10HZ', '100HZ', '1KHZ'). null = device default.",

        # Digital I/O Configuration
        "digital_io.model": "Digital I/O board model. Options: 'mock' (simulation) or 'ajinextek' (real hardware).",
        "digital_io.connection.board_id": "Digital I/O board ID for multi-board systems (0-3).",
    }

    # Digital I/O Pin Descriptions
    DIGITAL_IO_PIN_DESCRIPTIONS: Dict[str, str] = {
        # Emergency Stop Button
        "digital_io.emergency_stop_button.pin_number": "GPIO pin number for emergency stop button (physical safety input).",
        "digital_io.emergency_stop_button.contact_type": "Contact type: 'A' (normally open/NO) or 'B' (normally closed/NC). NC is safer for emergency stops.",
        "digital_io.emergency_stop_button.edge_type": "Trigger edge detection: 'rising', 'falling', or 'both'. Determines when button press is detected.",
        "digital_io.emergency_stop_button.name": "Descriptive name for this input signal (used in logs and UI).",

        # Operator Start Buttons
        "digital_io.operator_start_button_left.pin_number": "GPIO pin for left operator start button (two-hand safety start).",
        "digital_io.operator_start_button_left.contact_type": "Contact type: 'A' (NO) or 'B' (NC). Typically 'B' for safety.",
        "digital_io.operator_start_button_left.edge_type": "Trigger edge: 'rising', 'falling', or 'both'.",
        "digital_io.operator_start_button_left.name": "Signal name for left start button.",

        "digital_io.operator_start_button_right.pin_number": "GPIO pin for right operator start button (two-hand safety start).",
        "digital_io.operator_start_button_right.contact_type": "Contact type: 'A' (NO) or 'B' (NC). Typically 'B' for safety.",
        "digital_io.operator_start_button_right.edge_type": "Trigger edge: 'rising', 'falling', or 'both'.",
        "digital_io.operator_start_button_right.name": "Signal name for right start button.",

        # Safety Sensors
        "digital_io.safety_door_closed_sensor.pin_number": "GPIO pin for safety door closed sensor (interlock safety).",
        "digital_io.safety_door_closed_sensor.contact_type": "Contact type: 'A' (NO) or 'B' (NC). NC is safer - opens when door opens.",
        "digital_io.safety_door_closed_sensor.edge_type": "Trigger edge detection type.",
        "digital_io.safety_door_closed_sensor.name": "Signal name for door sensor.",

        "digital_io.dut_clamp_safety_sensor.pin_number": "GPIO pin for DUT clamping safety sensor (ensures DUT is secured).",
        "digital_io.dut_clamp_safety_sensor.contact_type": "Contact type: 'A' (NO - closed when clamped) or 'B' (NC).",
        "digital_io.dut_clamp_safety_sensor.edge_type": "Trigger edge detection type.",
        "digital_io.dut_clamp_safety_sensor.name": "Signal name for clamp sensor.",

        "digital_io.dut_chain_safety_sensor.pin_number": "GPIO pin for DUT chain safety sensor (detects chain/fixture position).",
        "digital_io.dut_chain_safety_sensor.contact_type": "Contact type: 'A' (NO) or 'B' (NC).",
        "digital_io.dut_chain_safety_sensor.edge_type": "Trigger edge detection type.",
        "digital_io.dut_chain_safety_sensor.name": "Signal name for chain sensor.",

        # Output Signals
        "digital_io.servo1_brake_release": "GPIO output pin for servo motor brake release signal (active = brake released).",
        "digital_io.tower_lamp_red": "GPIO output pin for red tower lamp (indicates error, alarm, or emergency stop state).",
        "digital_io.tower_lamp_yellow": "GPIO output pin for yellow tower lamp (indicates warning or test running state).",
        "digital_io.tower_lamp_green": "GPIO output pin for green tower lamp (indicates ready, idle, or test passed state).",
        "digital_io.beep": "GPIO output pin for audible beeper/buzzer (alerts, warnings, test completion).",
    }

    # Application Configuration Descriptions
    APPLICATION_DESCRIPTIONS: Dict[str, str] = {
        "application.name": "Application name displayed in GUI window title and reports.",
        "application.version": "Application version number (semantic versioning: MAJOR.MINOR.PATCH).",
        "application.environment": "Runtime environment mode. Options: 'development', 'testing', 'production'.",
        "services.repository.results_path": "Directory path where JSON test result files are saved.",
        "services.repository.raw_data_path": "Directory path where raw measurement data files (CSV, binary) are stored.",
        "services.repository.summary_path": "Directory path where test summary CSV files are saved.",
        "services.repository.summary_filename": "Filename for the test summary CSV file (e.g., test_summary.csv).",
        "services.repository.auto_save": "Enable automatic saving of test results immediately after each test completes.",
        "services.configuration.application_path": "Full path to the application configuration YAML file.",
        "services.configuration.hardware_path": "Full path to the hardware configuration YAML file.",
        "services.configuration.profile_preference_path": "Full path to the profile preferences YAML file.",
        "services.configuration.test_profiles_dir": "Directory path containing test profile YAML files.",
        "services.configuration.heating_cooling_path": "Full path to the heating/cooling test configuration YAML file.",
        "services.configuration.type": "Configuration service implementation type (yaml, json, etc.).",
        "services.repository.type": "Data repository implementation type (csv, sqlite, etc.).",
        "logging.level": "Log verbosity level. Options: DEBUG (most verbose), INFO, WARNING, ERROR, CRITICAL (least verbose).",
        "logging.console_output": "Enable/disable console log output (true/false).",
        "logging.file_output": "Enable/disable file log output (true/false).",
        "logging.rotation": "Log file rotation size threshold (e.g., '10 MB', '100 MB').",
        "gui.require_serial_number_popup": "Show serial number input dialog before starting each test.",
        "gui.scaling_factor": "UI scaling factor for high-DPI displays (0.5-2.0). 1.0 = 100% scaling.",
    }

    # Heating/Cooling Test Descriptions
    HEATING_COOLING_DESCRIPTIONS: Dict[str, str] = {
        "repeat_count": "Number of heating/cooling test cycles to perform (1-100). More cycles = better statistical data.",
        "heating_wait_time": "Minimum total time (seconds) for heating phase. If actual heating < this value, additional wait is added. If actual heating >= this value, no additional wait.",
        "cooling_wait_time": "Minimum total time (seconds) for cooling phase. If actual cooling < this value, additional wait is added. If actual cooling >= this value, no additional wait.",
        "stabilization_wait_time": "Wait time (seconds) for temperature stabilization after setpoint change.",
        "power_monitoring_interval": "Power measurement sampling interval in seconds (e.g., 0.5s = 2Hz). Lower = more data points.",
        "power_monitoring_enabled": "Enable real-time power consumption monitoring and logging during test.",
        "activation_temperature": "Target activation temperature (°C) for heating phase in heating/cooling test.",
        "standby_temperature": "Target standby temperature (°C) for cooling phase in heating/cooling test.",
        "voltage": "Operating voltage (V) for heating/cooling test power supply.",
        "current": "Operating current (A) for heating/cooling test power supply.",
        "fan_speed": "Cooling fan speed level (0-10). 0 = off, 10 = maximum cooling. Affects cooling rate.",
        "upper_temperature": "Maximum allowed temperature limit (°C) for safety during heating/cooling test.",
        "poweron_stabilization": "Power-on stabilization delay (seconds) before starting test operations.",
        "mcu_boot_complete_stabilization": "MCU boot completion delay (seconds). Wait for MCU firmware initialization.",
        "mcu_command_stabilization": "Delay (seconds) after sending MCU command before reading response.",
        "mcu_temperature_stabilization": "Delay (seconds) after temperature setpoint change for thermal equilibrium.",
        "calculate_statistics": "Calculate and display power consumption statistics (min, max, average, total energy).",
        "show_detailed_results": "Show detailed cycle-by-cycle test results in report (includes per-cycle timing and power data).",
        # Power Analyzer Measurement Parameters (Test-specific overrides)
        "power_analyzer_voltage_range": "Power analyzer voltage measurement range (e.g., '15V', '30V', '60V', '150V', '300V', '600V', '1000V'). Leave null to use hardware config default.",
        "power_analyzer_current_range": "Power analyzer current measurement range (e.g., '1A', '2A', '5A', '10A', '20A', '50A'). Leave null to use hardware config default.",
        "power_analyzer_auto_range": "Enable automatic range adjustment for optimal measurement accuracy. Recommended unless specific fixed range needed.",
        "power_analyzer_line_filter": "Line filter frequency for noise reduction (e.g., '500HZ', '1KHZ', '10KHZ', '100KHZ'). Leave null to use hardware config default.",
        "power_analyzer_frequency_filter": "Frequency filter for signal processing (e.g., '0.5HZ', '1HZ', '10HZ', '100HZ', '1KHZ'). Leave null to use hardware config default.",
        "power_analyzer_element": "Power analyzer measurement element/channel number (1-6). Leave null to use hardware config default element.",
    }

    # DUT (Device Under Test) Descriptions
    DUT_DESCRIPTIONS: Dict[str, str] = {
        "default.dut_id": "Default Device Under Test identifier code (unique tracking ID).",
        "default.model_number": "Default DUT model number or part number for test records.",
        "default.serial_number": "Default DUT serial number. Can be overridden by user input or barcode scanner.",
    }

    # Profile Management Descriptions
    PROFILE_DESCRIPTIONS: Dict[str, str] = {
        "active_profile": "Currently active test profile name (e.g., 'default', 'production', 'debug').",
        "available_profiles": "List of available test profile names that can be loaded.",
        "profile_paths": "Search directory paths for locating test profile YAML files.",
        "validation.strict_mode": "Enable strict validation of profile parameters. If true, invalid profiles will be rejected.",
        "validation.fallback_profile": "Fallback profile name to load if active profile fails validation or is not found.",
    }

    # Metadata Field Descriptions
    METADATA_DESCRIPTIONS: Dict[str, str] = {
        "metadata.created_at": "Timestamp when this configuration was created (ISO 8601 format: YYYY-MM-DDTHH:MM:SS).",
        "metadata.created_by": "Service or user that created this configuration file (e.g., 'YamlConfiguration', 'Admin').",
        "metadata.note": "Additional notes or comments about this configuration (single-line).",
        "metadata.profile_name": "Name of this test profile (used for identification and selection).",
        "metadata.version": "Configuration file version number (semantic versioning recommended).",
        "metadata.description": "Detailed description of this configuration's purpose and usage.",
        "metadata.notes": "Multi-line notes and usage instructions for this configuration.",
        "metadata.updated_by": "Service or user that last updated this configuration file.",
    }

    # Combine all descriptions
    ALL_DESCRIPTIONS: Dict[str, str] = {
        **HARDWARE_DESCRIPTIONS,
        **MOTION_DESCRIPTIONS,
        **TIMING_DESCRIPTIONS,
        **TEST_DESCRIPTIONS,
        **SAFETY_DESCRIPTIONS,
        **EXECUTION_DESCRIPTIONS,
        **TOLERANCE_DESCRIPTIONS,
        **PASS_CRITERIA_DESCRIPTIONS,
        **HARDWARE_DEVICE_DESCRIPTIONS,
        **DIGITAL_IO_PIN_DESCRIPTIONS,
        **APPLICATION_DESCRIPTIONS,
        **HEATING_COOLING_DESCRIPTIONS,
        **DUT_DESCRIPTIONS,
        **PROFILE_DESCRIPTIONS,
        **METADATA_DESCRIPTIONS,
    }

    @classmethod
    def get_description(cls, key: str) -> str:
        """
        Get description for a parameter key

        Args:
            key: Full parameter key (e.g., "hardware.voltage")

        Returns:
            Description string, or empty string if not found
        """
        # Try exact match first
        if key in cls.ALL_DESCRIPTIONS:
            return cls.ALL_DESCRIPTIONS[key]

        # Try partial match (for nested keys)
        # e.g., "hardware.robot.model" -> look for "robot.model"
        parts = key.split(".")
        for i in range(len(parts)):
            partial_key = ".".join(parts[i:])
            if partial_key in cls.ALL_DESCRIPTIONS:
                return cls.ALL_DESCRIPTIONS[partial_key]

        # No description found
        return ""

    @classmethod
    def has_description(cls, key: str) -> bool:
        """Check if description exists for a key"""
        return bool(cls.get_description(key))
