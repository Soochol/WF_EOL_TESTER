# WF EOL Tester - GUI Application

A complete PySide6 GUI application for the WF EOL Tester system with industrial-themed interface and comprehensive testing capabilities.

## Features

### 🎯 Core Functionality
- **Complete EOL Force Testing** with real-time progress monitoring
- **Simple MCU Communication Tests** with command sequence tracking
- **Manual Hardware Control** with connection management
- **System Configuration** with validation and file management
- **Real-time Dashboard** with hardware status and system monitoring

### 🎨 Industrial Design
- **Professional industrial theme** with WCAG 2.1 AA accessibility compliance
- **High contrast colors** optimized for manufacturing environments
- **Touch-friendly interface** with 44px minimum touch targets
- **Keyboard navigation** support throughout the application
- **Screen reader compatibility** with proper accessibility labeling

### 🏗️ Architecture
- **MVC Pattern** with clean separation of concerns
- **Dependency Injection** via ApplicationContainer integration
- **Async Operation Support** for hardware communication
- **State Management** with centralized GUI state tracking
- **Signal/Slot Architecture** for responsive UI updates

## Quick Start

### 1. Launch the GUI Application
```bash
# From the project root directory
source .venv/bin/activate
python src/main_gui.py
```

### 2. Main Interface Overview
The application consists of four main areas:

- **Header**: Application title, test status, hardware indicators, system time
- **Side Menu**: Navigation between different panels
- **Content Area**: Main working area that changes based on selected panel
- **Status Bar**: Hardware connection status, test progress, system information

### 3. Navigation Panels

#### Dashboard Panel
- **System Overview**: Hardware status cards showing connection states
- **Test Statistics**: Recent test results and success rates
- **System Messages**: Real-time log of system events
- **Quick Actions**: Shortcuts for common operations

#### EOL Force Test Panel
- **Test Configuration**: Operator ID, test mode, serial number settings
- **Test Control**: Start, stop, and reset test operations
- **Progress Monitoring**: Real-time progress bar and status updates
- **Results Display**: Detailed test results with step-by-step breakdown

#### Simple MCU Test Panel
- **Test Parameters**: Operator settings and auto-repeat options
- **Test Statistics**: Success rate, average duration, total test count
- **Command Results**: Detailed view of each MCU command execution
- **Real-time Logging**: Live test execution log

#### Hardware Control Panel
- **Connection Management**: Individual hardware component connections
- **Quick Actions**: Emergency stop, reset all, robot homing
- **Manual Commands**: Send custom commands to hardware
- **Status Monitoring**: Real-time hardware status indicators

#### Configuration Panel
- **Hardware Settings**: Serial ports, IP addresses, communication parameters
- **Application Settings**: Logging, data storage, UI preferences
- **Test Parameters**: Thresholds, timeouts, retry counts
- **File Management**: Load, save, validate, and reset configurations

## Key Capabilities

### ✅ Test Execution
- **Full EOL Force Tests**: Complete end-of-line testing with force measurements
- **MCU Communication Tests**: Verify MCU command sequences and responses
- **Auto-repeat functionality**: Run multiple test iterations automatically
- **Progress tracking**: Real-time progress updates with detailed status messages

### ✅ Hardware Integration  
- **Multi-device support**: Robot, MCU, Load Cell, Power Supply, Digital I/O
- **Connection management**: Individual connect/disconnect for each device
- **Status monitoring**: Real-time connection status with visual indicators
- **Emergency stop**: Immediate halt of all operations with F1 key

### ✅ Data Management
- **Test results storage**: Automatic saving of test results and logs
- **Configuration persistence**: Save and load system configurations
- **Export capabilities**: Export test data for analysis
- **Backup management**: Configurable backup retention policies

### ✅ User Experience
- **Intuitive navigation**: Clear menu structure with visual feedback
- **Responsive interface**: Smooth animations and immediate user feedback
- **Error handling**: User-friendly error messages with recovery suggestions
- **Keyboard shortcuts**: Power user shortcuts for common operations

## Keyboard Shortcuts

- **Ctrl+Q**: Exit application
- **F1**: Emergency stop (stops all running operations)
- **F5**: Refresh current panel and status
- **Tab/Shift+Tab**: Navigate between UI elements
- **Enter**: Activate focused button or confirm input

## Industrial Environment Features

### 🏭 Manufacturing Optimized
- **Large touch targets**: All interactive elements are minimum 44px for touch operation
- **High contrast visuals**: Colors meet industrial display requirements
- **Noise resistant**: Clear visual indicators that work in bright environments
- **Operator friendly**: Simplified workflows designed for manufacturing operators

### 🔒 Safety Features
- **Emergency stop**: Prominent emergency stop button and F1 shortcut
- **Confirmation dialogs**: Critical operations require user confirmation
- **Status visibility**: Clear indication of system state at all times
- **Error recovery**: Graceful error handling with recovery instructions

### ⚡ Performance
- **Responsive UI**: Non-blocking operations with background processing
- **Efficient updates**: Smart state management reduces unnecessary updates
- **Memory management**: Proper cleanup and resource management
- **Scalable architecture**: Supports additional hardware and test types

## Configuration

The GUI automatically loads configurations from:
- `configuration/application.yaml` - Application settings
- `configuration/hardware_config.yaml` - Hardware parameters

Configuration can be modified through the Configuration panel in the GUI or by editing the YAML files directly.

## Troubleshooting

### Common Issues

1. **Hardware Connection Errors**
   - Check hardware connections and power
   - Verify configuration settings in Hardware Control panel
   - Use manual connection test buttons

2. **Test Failures**
   - Ensure all hardware is connected and operational
   - Check test parameters in Configuration panel
   - Review test logs for specific error messages

3. **Performance Issues**
   - Close unused panels to reduce resource usage
   - Check system resources and available memory
   - Restart application if needed

### Log Files
System logs are displayed in real-time in various panel log areas and can be found in the application's log directory.

## Development

The GUI is built with:
- **PySide6**: Modern Qt6-based Python GUI framework
- **Industrial Design System**: WCAG-compliant industrial theme
- **Async Integration**: Proper asyncio integration with Qt event loop
- **Type Safety**: Comprehensive type hints and validation

For development setup and API documentation, see the main project README.

## Support

For issues, feature requests, or questions:
1. Check the troubleshooting section above
2. Review system logs for error details
3. Consult the main project documentation
4. Contact the development team

---

**WF EOL Tester GUI v2.0** - Industrial-grade testing interface for manufacturing environments.