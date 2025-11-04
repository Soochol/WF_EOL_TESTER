# Power Analyzer Test Suite

Comprehensive integration tests for Power Analyzer implementations following Clean Architecture and TDD principles.

## Test Coverage

### ✅ Passing Tests: 46/46 (100%)

All core functionality tests pass successfully:

- **PowerAnalyzerConfig Validation**: 20 tests
- **Mock Power Analyzer Integration**: 26 tests

### Test Suites

#### 1. PowerAnalyzerConfig Validation Tests (`test_power_analyzer_config.py`)
Tests for configuration value object with 20 test cases covering:

- **Default Configuration**: Verifies default values (mock mode, standard ports, auto-range)
- **WT1800E Configuration**: Tests production hardware configuration
- **Immutability**: Ensures frozen dataclass behavior (cannot modify after creation)
- **Mock Detection**: Validates hardware type detection logic
- **Element Range**: Tests measurement channel/element configuration
- **Voltage/Current Ranges**: Validates various range options (15V-1000V, 500mA-30A)
- **Auto-range Toggle**: Tests automatic range adjustment enable/disable
- **Filter Configurations**: Tests line and frequency filter settings
- **Timeout Values**: Validates various timeout configurations (1s-120s)
- **Network Configuration**: Tests host/port combinations
- **HardwareConfig Integration**: Tests integration with main hardware configuration
- **Serialization**: Tests to_dict()/from_dict() round-trip conversion
- **Edge Cases**: Boundary conditions, equality comparison, hash consistency

#### 2. Mock Power Analyzer Integration Tests (`test_mock_power_analyzer.py`)
Comprehensive tests for mock hardware implementation with 26 test cases:

**Connection Management** (4 tests):
- Successful connection/disconnection
- Multiple connect/disconnect cycles
- Double connection handling

**Measurements** (7 tests):
- Data structure validation (voltage, current, power)
- Realistic value ranges (24V ±0.5V, 2.5A ±0.2A)
- Non-negative value constraints
- Error handling when disconnected
- Controllable base values via `set_base_values()`
- Adjustable noise levels via `set_noise_levels()`

**Device Identity** (2 tests):
- SCPI *IDN? format compliance
- Error handling when disconnected

**Configuration** (4 tests):
- Auto-range configuration
- Manual range configuration
- Filter configuration (line/frequency)
- Error handling when disconnected

**Integration Measurement** (7 tests):
- Setup integration mode
- Start/stop integration sequence
- Reset integration data
- Get integration time (start/end timestamps)
- Get integration data structure (active_energy_wh, apparent_energy_vah, reactive_energy_varh)
- Realistic energy value ranges (~60Wh active, ~65VAh apparent)
- Complete workflow test (setup → reset → start → query → stop)

**Stress Tests** (2 tests):
- 100 rapid consecutive measurements
- Mixed concurrent operations

#### 3. WT1800E Error Handling Tests (`test_wt1800e_error_handling.py`)
Advanced error handling tests for production hardware (requires mock framework refinement):

**Planned Coverage**:
- Error queue checking mechanism
- TCP connection failures
- Measurement errors (timeouts, invalid responses)
- Configuration errors
- Integration measurement errors
- Error recovery mechanisms
- Edge cases and boundary conditions

**Status**: Test framework created, requires async mock refinement for full compatibility.

## Running Tests

### Run All Passing Tests
```bash
# Using UV (recommended)
uv run pytest tests/test_power_analyzer_config.py tests/test_mock_power_analyzer.py -v

# Using pytest directly
pytest tests/test_power_analyzer_config.py tests/test_mock_power_analyzer.py -v
```

### Run Specific Test Suites
```bash
# Configuration tests only
uv run pytest tests/test_power_analyzer_config.py -v

# Mock hardware tests only
uv run pytest tests/test_mock_power_analyzer.py -v

# Specific test class
uv run pytest tests/test_mock_power_analyzer.py::TestMockPowerAnalyzerIntegration -v

# Specific test method
uv run pytest tests/test_mock_power_analyzer.py::TestMockPowerAnalyzerIntegration::test_full_integration_workflow -v
```

### Generate Coverage Report
```bash
# HTML coverage report
pytest tests/test_power_analyzer_config.py tests/test_mock_power_analyzer.py --cov=src --cov-report=html

# Terminal coverage report
pytest tests/test_power_analyzer_config.py tests/test_mock_power_analyzer.py --cov=src --cov-report=term-missing
```

## Test Fixtures

### Configuration Fixtures (`conftest.py`)
- `default_power_analyzer_config`: Default mock configuration
- `wt1800e_config`: Production WT1800E configuration
- `mock_power_analyzer`: Connected mock analyzer instance (async)
- `mock_power_analyzer_disconnected`: Disconnected mock analyzer for connection tests

## Test Organization

```
tests/
├── __init__.py                          # Test package initialization
├── conftest.py                          # Shared pytest fixtures
├── test_power_analyzer_config.py        # Configuration validation tests (20 tests ✅)
├── test_mock_power_analyzer.py          # Mock hardware integration tests (26 tests ✅)
├── test_wt1800e_error_handling.py       # WT1800E error handling tests (in progress)
└── README.md                            # This file
```

## Design Philosophy

These tests follow the project's Clean Architecture principles:

1. **Interface Testing**: Tests validate the PowerAnalyzerService interface contract
2. **Implementation Testing**: Tests verify mock implementation behavior
3. **Value Object Testing**: Tests ensure immutable configuration objects
4. **Async Support**: All tests use pytest-asyncio for async hardware operations
5. **Isolation**: Each test is independent with proper setup/teardown
6. **Realistic Scenarios**: Tests simulate actual hardware usage patterns

## Key Features Tested

### PowerAnalyzerConfig
- ✅ Immutable frozen dataclass
- ✅ Comprehensive validation
- ✅ Serialization (JSON-compatible)
- ✅ HardwareConfig integration

### Mock Power Analyzer
- ✅ Full PowerAnalyzerService interface implementation
- ✅ Realistic measurement simulation with noise
- ✅ Integration measurement support (energy calculation)
- ✅ Configurable base values for predictable testing
- ✅ Connection state management
- ✅ Error handling (disconnected state)

### Integration Measurement
- ✅ Setup with mode and timer configuration
- ✅ Start/stop/reset operations
- ✅ Time tracking (start/end timestamps)
- ✅ Energy data retrieval (active, apparent, reactive)
- ✅ Realistic simulation values

## Next Steps

1. **WT1800E Test Refinement**: Complete async mock framework for WT1800E error tests
2. **Integration Tests**: Add end-to-end tests with PowerMonitor service
3. **Performance Tests**: Add benchmarks for measurement throughput
4. **Coverage Expansion**: Achieve >90% code coverage for power analyzer module

## References

- WT1800E Programming Guide (section 4.4: Integration Measurement)
- Project CLAUDE.md for architecture guidelines
- Clean Architecture principles
- pytest-asyncio documentation
