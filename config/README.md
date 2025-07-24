# EOL Tester Configuration

This directory contains YAML configuration files for different test profiles.

## Profile Structure

Each YAML profile contains the following sections:

### metadata
- `profile_name`: Unique identifier for the profile
- `description`: Human-readable description
- `version`: Configuration version
- `created_by`: Creator information
- `created_time`: Creation timestamp

### hardware
- `voltage`: Operating voltage (V)
- `current`: Current limit (A)
- `upper_temperature`: Upper temperature limit (°C)
- `fan_speed`: Fan speed percentage (0-100%)
- `max_stroke`: Maximum stroke position (mm)
- `initial_position`: Initial robot position (mm)

### test_parameters
- `temperature_list`: List of temperature test points (°C)
- `stroke_positions`: List of stroke position test points (mm)
- `standby_position`: Standby position (mm)

### timing
- `stabilization_delay`: General stabilization wait (seconds)
- `temperature_stabilization`: Temperature change stabilization (seconds)
- `power_stabilization`: Power output stabilization (seconds)
- `loadcell_zero_delay`: LoadCell zeroing delay (seconds)

### tolerances
- `measurement_tolerance`: General measurement tolerance
- `force_precision`: Force measurement decimal places
- `temperature_precision`: Temperature measurement decimal places

### execution
- `retry_attempts`: Number of retry attempts for failed operations
- `timeout_seconds`: Overall test timeout (seconds)

### safety
- `max_temperature`: Absolute maximum temperature (°C)
- `max_force`: Absolute maximum force (N)
- `max_voltage`: Absolute maximum voltage (V)
- `max_current`: Absolute maximum current (A)

## Available Profiles

### default.yaml
Standard configuration for normal EOL testing operations.
- **Use case**: Normal production testing
- **Test points**: 6 temperatures × 7 positions = 42 measurements
- **Duration**: ~3-5 minutes

### quick_test.yaml
Fast configuration with minimal test points for development.
- **Use case**: Development and quick validation
- **Test points**: 3 temperatures × 4 positions = 12 measurements
- **Duration**: ~1-2 minutes

### comprehensive.yaml
Extended configuration with many test points for thorough validation.
- **Use case**: Qualification testing and detailed analysis
- **Test points**: 9 temperatures × 13 positions = 117 measurements
- **Duration**: ~10-15 minutes

### high_voltage.yaml
Configuration for testing with higher voltage requirements.
- **Use case**: High voltage device testing
- **Test points**: 6 temperatures × 7 positions = 42 measurements
- **Duration**: ~3-5 minutes

### safety_test.yaml
Conservative configuration with enhanced safety margins.
- **Use case**: Safety validation and conservative testing
- **Test points**: 4 temperatures × 5 positions = 20 measurements
- **Duration**: ~2-3 minutes

## Usage

Profiles can be loaded by name in the test configuration:

```python
# Load specific profile
config = await config_service.load_profile("default")

# Load with runtime overrides
command = ExecuteEOLTestCommand(
    dut_id="DUT-001",
    dut_model="Model-X",
    dut_serial="SN-12345",
    test_type=TestType.FORCE,
    operator_id="OP-001",
    test_config={
        "profile": "quick_test",
        "voltage": 15.0  # Override default voltage
    }
)
```

## Creating Custom Profiles

1. Copy an existing profile as a starting point
2. Modify the parameters as needed
3. Update the metadata section
4. Save with a descriptive filename
5. Test the configuration before production use

## Safety Notes

- Always respect the safety limits defined in each profile
- The safety section defines absolute maximums that should never be exceeded
- Test new profiles thoroughly in a safe environment
- Keep backups of working configurations

## Backup and Recovery

The configuration service automatically creates backups in the `backups/` subdirectory when profiles are modified or deleted.