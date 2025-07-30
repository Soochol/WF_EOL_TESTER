# Enhanced Input Manager Integration Guide

## Overview

The Enhanced Input Manager provides professional-grade command-line input capabilities for the EOL Tester CLI application. It integrates `prompt_toolkit` to deliver advanced features including auto-completion, command history, syntax highlighting, and real-time validation while maintaining full backward compatibility.

## Features

### 1. **Enhanced Input System**
- **Auto-completion**: Smart completion for commands, hardware names, and parameters
- **Command History**: Persistent history across sessions with search capabilities
- **Syntax Highlighting**: Visual highlighting for different command types
- **Multi-line Input**: Support for complex operations requiring multiple lines
- **Input Validation**: Real-time validation with visual feedback

### 2. **Auto-completion Features**
- **Slash Command Completion**: `/robot`, `/mcu`, `/loadcell`, `/power`
- **Subcommand Completion**: `connect`, `disconnect`, `status`, etc.
- **Parameter Suggestions**: Temperature values, voltage ranges, etc.
- **DUT ID Completion**: Common DUT identifiers and test parameters
- **File Path Completion**: For exports and imports

### 3. **Command History**
- **Persistent Storage**: History saved across sessions
- **Search Functionality**: Use `Ctrl+R` to search command history
- **Command Filtering**: Smart filtering and suggestions
- **Recent Commands Priority**: Most recent commands appear first

### 4. **Visual Enhancements**
- **Syntax Highlighting**: Different colors for command types
- **Real-time Validation**: Visual indicators for input errors
- **Professional Styling**: Consistent with Rich UI theme
- **Error Highlighting**: Clear error messages and suggestions

## Installation

The enhanced input system requires `prompt_toolkit`:

```bash
pip install prompt-toolkit>=3.0.38
```

This dependency is automatically included in the project's `pyproject.toml`.

## Integration Points

### 1. **Main Menu Navigation**
The enhanced menu system provides auto-completion for menu choices:

```python
# Enhanced main menu with auto-completion
choice = await enhanced_menu.show_main_menu_enhanced()
```

### 2. **DUT Information Collection**
Professional form interface with validation and auto-completion:

```python
# Enhanced DUT information collection
dut_info = await input_integrator.get_dut_information()
```

### 3. **Slash Command Mode**
Full-featured slash command interface:

```python
# Enhanced slash command mode
await enhanced_slash_interface.run_enhanced_slash_mode()
```

### 4. **General Input**
Enhanced input for any text collection:

```python
# Enhanced validated input
result = await input_integrator.get_validated_input(
    prompt="Enter value: ",
    input_type="dut_id",
    required=True,
    placeholder="e.g., WF001"
)
```

## Usage Examples

### Basic Input with Auto-completion

```python
from ui.cli.enhanced_input_manager import EnhancedInputManager
from rich.console import Console

console = Console()
formatter = RichFormatter(console)
input_manager = EnhancedInputManager(console, formatter)

# Get input with auto-completion
result = await input_manager.get_input(
    prompt_text="Enter command: ",
    input_type="slash_command",
    show_completions=True,
    enable_history=True
)
```

### DUT Information Collection

```python
from ui.cli.enhanced_cli_integration import create_enhanced_cli_integrator

integrator = create_enhanced_cli_integrator(console, formatter)

# Collect DUT information with validation
dut_info = await integrator.get_dut_information()
# Returns: {"id": "WF001", "model": "WF-2024-A", "serial": "S001", "operator": "Test"}
```

### Menu Navigation

```python
from ui.cli.enhanced_cli_integration import create_enhanced_menu_system

menu_system = create_enhanced_menu_system(integrator)

# Enhanced menu with auto-completion
choice = await menu_system.show_main_menu_enhanced()
```

### Slash Command Interface

```python
from ui.cli.enhanced_cli_integration import create_enhanced_slash_interface

slash_interface = create_enhanced_slash_interface(integrator, slash_handler)

# Full-featured slash command mode
await slash_interface.run_enhanced_slash_mode()
```

## Available Commands and Completions

### Slash Commands

#### Robot Control (`/robot`)
- `connect` - Connect to robot hardware
- `disconnect` - Disconnect from robot hardware
- `status` - Show robot connection and motion status
- `init` - Initialize robot system and axis configuration
- `stop` - Execute emergency stop for immediate motion halt

#### MCU Control (`/mcu`)
- `connect` - Connect to MCU hardware
- `disconnect` - Disconnect from MCU hardware
- `status` - Show MCU connection and temperature status
- `temp [value]` - Get current temperature or set with argument (°C)
- `testmode` - Enter test mode for MCU operations
- `fan [speed]` - Set fan speed with argument (0-100%)

#### LoadCell Control (`/loadcell`)
- `connect` - Connect to LoadCell hardware
- `disconnect` - Disconnect from LoadCell hardware
- `status` - Show LoadCell connection and force status
- `read` - Read current force measurement
- `zero` - Perform zero calibration on LoadCell
- `monitor` - Start real-time force monitoring (Ctrl+C to stop)

#### Power Control (`/power`)
- `connect` - Connect to Power supply hardware
- `disconnect` - Disconnect from Power supply hardware
- `status` - Show Power supply connection and output status
- `on` - Enable power output
- `off` - Disable power output
- `voltage [value]` - Get current voltage or set with argument (V)
- `current [value]` - Get current reading or set limit with argument (A)

#### System Commands
- `/all status` - Show all hardware status
- `/help [command]` - Show help information

### Parameter Auto-completion

#### Temperature Values (MCU)
- `25.0` - Room temperature
- `85.0` - Standard high temperature test
- `105.0` - Extended temperature test

#### Voltage Values (Power)
- `5.0` - 5V supply
- `12.0` - 12V supply
- `24.0` - 24V supply
- `48.0` - 48V supply

#### Current Values (Power)
- `0.5` - 500mA limit
- `1.0` - 1A limit
- `2.0` - 2A limit
- `5.0` - 5A limit

#### Fan Speed (MCU)
- `0` - Fan off
- `25` - Low speed
- `50` - Medium speed
- `75` - High speed
- `100` - Maximum speed

### DUT Information Auto-completion

#### Common DUT IDs
- `WF001`, `WF002` - Wafer fabrication samples
- `TEST001` - Test sample
- `PROTO01` - Prototype sample
- `SAMPLE1` - Generic sample

#### Common Models
- `WF-2024-A` - 2024 Model A
- `WF-2024-B` - 2024 Model B
- `WF-2023-X` - 2023 Model X

#### Common Operators
- `Test` - Default test operator
- `Engineer1` - Engineering operator
- `QA_Team` - Quality assurance team
- `Production` - Production operator

## Keyboard Shortcuts

### Navigation
- `Ctrl+A` - Move to beginning of line
- `Ctrl+E` - Move to end of line
- `Ctrl+W` - Delete previous word
- `Ctrl+U` - Clear entire line
- `Ctrl+L` - Clear screen

### History
- `Up/Down` arrows - Browse command history
- `Ctrl+R` - Search command history
- `Page Up/Down` - Navigate through history pages

### Completion
- `Tab` - Show available completions
- `Ctrl+Space` - Force completion menu
- `Arrow keys` - Navigate completion options
- `Enter` - Select completion

### Multi-line Input
- `Alt+Enter` - New line in multi-line mode
- `Ctrl+D` - Finish multi-line input

### Cancellation
- `Ctrl+C` - Cancel current input
- `Ctrl+D` - Exit (on empty line)

## Configuration

### Input Configuration

```python
class EnhancedInputConfig:
    # History settings
    MAX_HISTORY_ENTRIES = 1000
    HISTORY_FILE_NAME = ".eol_tester_history"
    
    # Input validation settings
    MAX_INPUT_LENGTH = 500
    TIMEOUT_SECONDS = 300  # 5 minutes
    
    # Auto-completion settings
    MAX_COMPLETIONS = 50
    COMPLETION_TIMEOUT = 0.5  # seconds
```

### Validation Patterns

```python
PATTERNS = {
    'dut_id': r'^[A-Z0-9_-]{1,20}$',
    'model': r'^[A-Za-z0-9_\-\s\.]{1,50}$',
    'serial': r'^[A-Za-z0-9_\-]{1,30}$',
    'operator': r'^[A-Za-z0-9_\-\s]{1,30}$',
    'slash_command': r'^/\w+(\s+\w+(\s+.*)?)?$',
    'general': r'^.{1,500}$'
}
```

## Error Handling and Fallbacks

### Graceful Degradation
If `prompt_toolkit` is not available, the system automatically falls back to basic input methods:

```python
# Automatic fallback detection
if not PROMPT_TOOLKIT_AVAILABLE:
    return await self._fallback_input(prompt_text, input_type)
```

### Error Recovery
- **Connection Timeouts**: Graceful handling of hardware timeouts
- **Invalid Input**: Clear error messages with retry options
- **Keyboard Interrupts**: Clean cancellation with user feedback
- **System Errors**: Fallback to basic functionality

## Integration with Existing CLI

### Backward Compatibility
The enhanced input system is fully backward compatible:

```python
# Old method (still works)
choice = input("Select option: ")

# New enhanced method
choice = await integrator.get_validated_input(
    "Select option: ",
    input_type="general"
)
```

### Migration Guide

1. **Replace basic input calls**:
   ```python
   # Before
   user_input = input("Enter value: ")
   
   # After
   user_input = await integrator.get_validated_input("Enter value: ")
   ```

2. **Add validation types**:
   ```python
   # Add input type for validation
   dut_id = await integrator.get_validated_input(
       "Enter DUT ID: ",
       input_type="dut_id",
       required=True
   )
   ```

3. **Use enhanced menus**:
   ```python
   # Before
   print("1. Option 1\n2. Option 2")
   choice = input("Select: ")
   
   # After
   choice = await menu_system.show_main_menu_enhanced()
   ```

## Performance Considerations

### Memory Usage
- History limited to 1000 entries by default
- Completion cache with timeout mechanism
- Efficient string matching for completions

### Response Time
- Sub-second completion response
- Async input handling prevents blocking
- Optimized validation patterns

## Testing

### Running Tests
```bash
python3 test_enhanced_input.py
```

### Test Coverage
- ✅ Basic input functionality
- ✅ Auto-completion system
- ✅ Input validation
- ✅ Command history
- ✅ Error handling
- ✅ Fallback mechanisms

### Interactive Testing
The test script includes an interactive demo mode:
```bash
# Run with interactive demo
python3 test_enhanced_input.py
# Select 'y' when prompted for interactive demo
```

## Troubleshooting

### Common Issues

#### 1. prompt_toolkit Not Available
**Problem**: Enhanced features not working
**Solution**: Install prompt_toolkit
```bash
pip install prompt-toolkit>=3.0.38
```

#### 2. History Not Saving
**Problem**: Command history not persisting
**Solution**: Check file permissions for history file
```bash
ls -la ~/.eol_tester_history
chmod 644 ~/.eol_tester_history
```

#### 3. Auto-completion Not Working
**Problem**: Tab completion not showing suggestions
**Solution**: Ensure terminal supports advanced features
- Use a modern terminal (Windows Terminal, iTerm2, etc.)
- Check TERM environment variable

#### 4. Input Validation Errors
**Problem**: Valid input being rejected
**Solution**: Check validation patterns
```python
# Test validation
valid, message = input_manager.validate_input_format("YOUR_INPUT", "dut_id")
print(f"Valid: {valid}, Message: {message}")
```

### Debug Mode
Enable debug logging:
```python
import logging
logging.getLogger('ui.cli.enhanced_input_manager').setLevel(logging.DEBUG)
```

## Best Practices

### 1. Input Type Selection
Always specify appropriate input types:
```python
# Good
dut_id = await integrator.get_validated_input("DUT ID: ", input_type="dut_id")

# Less optimal
dut_id = await integrator.get_validated_input("DUT ID: ", input_type="general")
```

### 2. User Experience
Provide helpful placeholders:
```python
result = await integrator.get_validated_input(
    "Enter voltage: ",
    input_type="general",
    placeholder="e.g., 24.0 (in volts)"
)
```

### 3. Error Handling
Always handle potential cancellation:
```python
result = await integrator.get_validated_input("Enter value: ")
if result is None:
    console.print("Operation cancelled")
    return
```

### 4. Performance
Use appropriate completion settings:
```python
# For frequently used inputs, enable completions
result = await input_manager.get_input(show_completions=True)

# For one-time inputs, disable for better performance
result = await input_manager.get_input(show_completions=False)
```

## Future Enhancements

### Planned Features
- [ ] Multi-language support for command completion
- [ ] Custom completion plugins for hardware-specific parameters
- [ ] Advanced history search with fuzzy matching
- [ ] Voice input integration for accessibility
- [ ] Cloud-based command history synchronization

### Extension Points
The system is designed for easy extension:
```python
# Custom completer
class CustomCompleter(Completer):
    def get_completions(self, document, complete_event):
        # Custom completion logic
        pass

# Register custom completer
input_manager.completer = CustomCompleter()
```

## Support

For issues, questions, or feature requests:
1. Check this documentation
2. Run the test suite to verify installation
3. Enable debug logging for detailed error information
4. Review the source code for implementation details

The Enhanced Input Manager is designed to provide a professional, efficient, and user-friendly command-line experience while maintaining full compatibility with existing CLI functionality.