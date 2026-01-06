# EOL Force Test Sequence (Standalone)

End-of-Line force test sequence with optional station-service-sdk integration.

## Features

- **Dual Hardware Mode**: Supports both mock (testing) and real (production) hardware
- **Complete Standalone**: Self-contained package with all drivers included
- **Full Hardware Support**: MCU, LoadCell, Power Supply, Robot, Digital I/O
- **SDK Optional**: Works with or without station-service-sdk
- **Factory Pattern**: Easy hardware configuration via `HardwareFactory`

## Supported Hardware

| Type | Mock | Real Hardware | Notes |
|------|------|---------------|-------|
| LoadCell | MockLoadCell | BS205 | Serial (RS232) |
| MCU | MockMCU | LMA | Serial (RS232) |
| Power Supply | MockPower | ODA | TCP/IP (SCPI) |
| Robot | MockRobot | Ajinextek | Windows DLL |
| Digital I/O | MockDigitalIO | Ajinextek | Windows DLL |

> **Note**: Ajinextek robot and DIO require Windows (DLL-based). On other platforms, they fall back to mock implementations.

## Installation

### Standalone (Mock Hardware)

```bash
# From sequences/eol_tester directory
pip install -e .
```

### With Real Hardware

```bash
# From sequences/eol_tester directory
pip install -e .

# Dependencies (automatically installed):
# - pyserial>=3.5
# - pyserial-asyncio>=0.6
# - loguru>=0.7.0
```

## Usage

### CLI

```bash
# Run with default parameters (standalone mock mode)
python -m eol_tester --start

# Run with parameters
python -m eol_tester --start --param voltage=18.0 --param temperature_list="38,52,66"
```

### Python API

```python
import asyncio
from eol_tester import EOLForceTestSequence, ExecutionContext

async def run_test():
    # Create execution context
    context = ExecutionContext(
        execution_id="test001",
        serial_number="DUT001",
        parameters={
            "voltage": 18.0,
            "temperature_list": "38.0,52.0,66.0",
            "stroke_positions": "170000.0",
        },
    )

    # Create and run sequence
    sequence = EOLForceTestSequence(context)
    result = await sequence._execute()

    print(f"Test passed: {result['passed']}")
    return result

asyncio.run(run_test())
```

### Hardware Factory (Recommended)

```python
from eol_tester.hardware import HardwareFactory

# Mock configuration (development/testing)
mock_config = HardwareFactory.get_default_mock_config()
hardware = HardwareFactory.create_all_hardware(mock_config)

# Real hardware configuration (production)
real_config = {
    "loadcell": {
        "type": "bs205",
        "connection": {
            "port": "COM1",
            "baudrate": 9600,
            "indicator_id": 1,
        },
    },
    "mcu": {
        "type": "lma",
        "connection": {
            "port": "COM2",
            "baudrate": 115200,
        },
    },
    "power": {
        "type": "oda",
        "connection": {
            "host": "192.168.1.10",
            "port": 5025,
        },
    },
    "robot": {
        "type": "ajinextek",  # Windows only
        "axis_count": 4,
    },
    "digital_io": {
        "type": "ajinextek",  # Windows only
        "module_no": 0,
    },
}

hardware = HardwareFactory.create_all_hardware(real_config)

# Use individual factory methods
loadcell = HardwareFactory.create_loadcell({"type": "bs205", "connection": {"port": "COM1"}})
mcu = HardwareFactory.create_mcu({"type": "lma", "connection": {"port": "COM2"}})
```

### Custom Hardware Adapter

```python
from eol_tester import (
    EOLHardwareAdapter,
    TestConfiguration,
    HardwareConfig,
)
from eol_tester.hardware import HardwareFactory
from eol_tester.services import HardwareServiceFacade

# Create hardware using factory
config = HardwareFactory.get_default_mock_config()
hardware = HardwareFactory.create_all_hardware(config)

# Create facade
facade = HardwareServiceFacade(
    robot_service=hardware["robot"],
    mcu_service=hardware["mcu"],
    loadcell_service=hardware["loadcell"],
    power_service=hardware["power"],
    digital_io_service=hardware["digital_io"],
)

# Create adapter
adapter = EOLHardwareAdapter(
    hardware_facade=facade,
    test_config=TestConfiguration(),
    hardware_config=HardwareConfig(),
)
```

## Package Structure

```
eol_tester/
├── __init__.py              # Package exports
├── sequence.py              # Main SequenceBase implementation
├── hardware_adapter.py      # Hardware adapter for SDK
├── manifest.yaml            # SDK manifest configuration
├── pyproject.toml           # Package configuration
├── domain/
│   ├── __init__.py
│   ├── exceptions.py        # Custom exceptions
│   ├── enums.py             # Enums (RobotState, etc.)
│   └── value_objects.py     # Data classes (TestConfiguration, etc.)
├── interfaces/
│   └── __init__.py          # Hardware service interfaces
├── driver/
│   ├── __init__.py
│   ├── serial/              # Serial communication driver
│   │   ├── __init__.py
│   │   ├── serial.py        # SerialConnection, SerialManager
│   │   ├── constants.py     # Serial constants
│   │   └── exceptions.py    # Serial exceptions
│   ├── tcp/                 # TCP communication driver
│   │   ├── __init__.py
│   │   ├── communication.py # TCPCommunication class
│   │   ├── constants.py     # TCP constants
│   │   └── exceptions.py    # TCP exceptions
│   └── ajinextek/           # Ajinextek AXL driver (Windows)
│       ├── __init__.py
│       ├── axl_wrapper.py   # AXL DLL wrapper
│       ├── constants.py     # AXL constants
│       ├── error_codes.py   # AXL error codes
│       └── exceptions.py    # AXL exceptions
├── hardware/
│   ├── __init__.py
│   ├── factory.py           # HardwareFactory for real/mock selection
│   ├── mock/                # Mock hardware implementations
│   │   └── __init__.py      # MockLoadCell, MockMCU, etc.
│   └── real/                # Real hardware implementations
│       ├── __init__.py
│       ├── bs205_loadcell.py    # BS205 LoadCell (Serial)
│       ├── lma_mcu.py           # LMA MCU (Serial)
│       ├── oda_power.py         # ODA Power Supply (TCP)
│       ├── ajinextek_robot.py   # Ajinextek Robot (Windows DLL)
│       └── ajinextek_dio.py     # Ajinextek DIO (Windows DLL)
└── services/
    ├── __init__.py
    └── hardware_facade.py   # Hardware service coordinator
```

## Hardware Control Methods

### MCU
- `read_temperature()` - Read current temperature
- `set_temperature(temp)` - Set operating temperature
- `verify_temperature(temp)` - Verify temperature within tolerance

### LoadCell
- `read_force()` - Read current force
- `read_peak_force()` - Read peak force

### Robot
- `move_robot_to_position(pos)` - Move to position (um)
- `get_robot_position()` - Get current position
- `reset_robot_homing_state()` - Reset homing state

### Power Supply
- `set_voltage(v)` / `get_voltage()` - Voltage control
- `set_current(a)` / `get_current()` - Current control
- `enable_power_output()` / `disable_power_output()` - Output control
- `get_all_power_measurements()` - Get V/I/P readings

### Digital I/O
- `read_digital_input(ch)` / `read_all_digital_inputs()` - Input reading
- `write_digital_output(ch, level)` - Output writing
- `reset_all_digital_outputs()` - Reset all outputs

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| voltage | float | 18.0 | Operating voltage (V) |
| current | float | 20.0 | Operating current (A) |
| temperature_list | string | "38.0,52.0,66.0" | Test temperatures (C) |
| stroke_positions | string | "170000.0" | Test positions (um) |
| velocity | float | 100000.0 | Robot velocity (um/s) |
| acceleration | float | 85000.0 | Robot acceleration (um/s2) |
| repeat_count | int | 1 | Number of test repetitions |
| stop_on_failure | bool | true | Stop on first failure |

## License

Part of WF_EOL_TESTER project.
