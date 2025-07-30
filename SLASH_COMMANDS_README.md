# Slash Command System for EOL Tester

This document describes the comprehensive slash command system implemented for hardware control in the EOL Tester CLI.

## Overview

The slash command system provides a powerful, command-line interface for controlling individual hardware components in the EOL testing system. It supports commands for robot, MCU, loadcell, and power supply hardware with Rich-formatted output and comprehensive error handling.

## Features

- **Command parsing and validation**: Robust parsing with argument support
- **Individual hardware control**: Standardized interfaces for all hardware types
- **Rich-formatted output**: Professional terminal output using Rich library
- **Error handling**: User-friendly error messages and graceful failure handling
- **Help system**: Comprehensive help with examples and usage information
- **Interactive and direct modes**: Support for both interactive CLI and programmatic execution
- **Mock hardware support**: Works with mock implementations for testing

## Available Commands

### Robot Commands (`/robot`)
- `/robot connect` - Connect to robot hardware
- `/robot disconnect` - Disconnect from robot hardware
- `/robot status` - Show robot connection and motion status
- `/robot init` - Initialize robot system and axis configuration
- `/robot stop` - Execute emergency stop for immediate motion halt

### MCU Commands (`/mcu`)
- `/mcu connect` - Connect to MCU hardware
- `/mcu disconnect` - Disconnect from MCU hardware
- `/mcu status` - Show MCU connection and temperature status
- `/mcu temp` - Get current temperature
- `/mcu temp <value>` - Set temperature (e.g., `/mcu temp 85.0`)
- `/mcu testmode` - Enter test mode for MCU operations
- `/mcu fan <value>` - Set fan speed (e.g., `/mcu fan 75`)

### LoadCell Commands (`/loadcell`)
- `/loadcell connect` - Connect to LoadCell hardware
- `/loadcell disconnect` - Disconnect from LoadCell hardware
- `/loadcell status` - Show LoadCell connection and force status
- `/loadcell read` - Read current force measurement
- `/loadcell zero` - Perform zero calibration
- `/loadcell monitor` - Start real-time force monitoring (Ctrl+C to stop)

### Power Commands (`/power`)
- `/power connect` - Connect to Power supply hardware
- `/power disconnect` - Disconnect from Power supply hardware
- `/power status` - Show Power supply connection and output status
- `/power on` - Enable power output
- `/power off` - Disable power output
- `/power voltage <value>` - Set voltage (e.g., `/power voltage 24.0`)
- `/power current <value>` - Set current limit (e.g., `/power current 2.5`)

### System Commands
- `/all status` - Show status of all hardware components
- `/help` - Show general help information
- `/help <command>` - Show detailed help for specific command (e.g., `/help robot`)

## Usage Examples

### Basic Hardware Control
```bash
/robot connect          # Connect to robot
/robot status           # Check robot status
/robot init             # Initialize robot
/mcu connect            # Connect to MCU
/mcu temp 85.0          # Set MCU temperature to 85°C
/loadcell zero          # Calibrate loadcell
/power voltage 24.0     # Set power supply to 24V
/power on               # Enable power output
```

### Monitoring and Status
```bash
/all status             # Overview of all hardware
/loadcell monitor       # Real-time force monitoring
/mcu temp               # Check current temperature
/power status           # Check power supply status
```

### Getting Help
```bash
/help                   # General help
/help robot             # Detailed robot command help
/help mcu               # Detailed MCU command help
```

## Integration Points

### Enhanced CLI Integration
The slash command system is integrated into the Enhanced EOL Tester CLI as "Slash Command Mode":

1. Launch the Enhanced CLI
2. Select option "6. Slash Command Mode" 
3. Enter interactive slash command interface
4. Type commands and receive immediate feedback
5. Type `exit` to return to main menu

### Programmatic Usage
```python
from ui.cli.slash_command_handler import SlashCommandHandler
from ui.cli.slash_command_executor import SlashCommandExecutor

# Create handler with hardware services
handler = SlashCommandHandler(
    robot_service=robot_service,
    mcu_service=mcu_service,
    loadcell_service=loadcell_service,
    power_service=power_service
)

# Execute single command
success = await handler.execute_command("/robot connect")

# Or use executor for batch operations
executor = SlashCommandExecutor(handler)
results = await executor.execute_command_list([
    "/robot connect",
    "/mcu temp 85.0",
    "/loadcell zero"
])
```

### Direct Execution Mode
The system supports direct command execution from command line:

```bash
# Execute single command
python -m slash_command_executor --command "/robot status"

# Execute commands from file
python -m slash_command_executor --file commands.txt

# Interactive mode
python -m slash_command_executor --interactive

# Create demo script
python -m slash_command_executor --demo
```

## Architecture

### Core Components

1. **CommandParser**: Parses and validates slash command syntax
2. **HardwareCommandHandler**: Base class for hardware-specific handlers
3. **SlashCommandHandler**: Main coordinator for all command types
4. **SlashCommandExecutor**: Supports batch and direct execution modes

### Command Flow
1. Input text is parsed into CommandInfo structure
2. Command is validated against known patterns
3. Appropriate hardware handler executes the command
4. Results are formatted and displayed using Rich
5. Success/failure status is returned

### Error Handling
- Comprehensive validation at parse time
- Hardware-specific error handling in each handler
- User-friendly error messages with guidance
- Graceful failure with detailed logging
- Recovery suggestions for common issues

## File Structure

```
src/ui/cli/
├── slash_command_handler.py      # Main slash command system
├── slash_command_executor.py     # Direct execution support
├── enhanced_eol_tester_cli.py    # CLI integration
├── rich_formatter.py             # Rich UI formatting
└── rich_utils.py                 # Rich UI utilities
```

## Testing

The system includes comprehensive test coverage:

- Command parsing validation
- Hardware handler functionality
- Error condition handling
- Mock hardware integration
- Batch execution testing

Run tests with:
```bash
python test_slash_commands.py
```

## Mock Hardware Support

All commands work with mock hardware implementations, enabling:
- Development without physical hardware
- Automated testing and CI/CD
- Training and demonstration scenarios
- Safe experimentation with commands

## Future Enhancements

Potential areas for expansion:
- Command history and tab completion
- Macro/script recording and playback
- Remote command execution via network
- Command scheduling and automation
- Advanced monitoring and alerting integration

## Troubleshooting

### Common Issues

1. **Command not recognized**: Ensure command starts with `/` and uses valid syntax
2. **Hardware not connected**: Connect to hardware first using `/[hardware] connect`
3. **Invalid parameters**: Check parameter format and ranges in help
4. **Permission errors**: Ensure proper hardware access permissions

### Debug Mode
Enable debug logging to see detailed command execution:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

This slash command system provides a powerful, flexible interface for hardware control while maintaining ease of use and comprehensive error handling.