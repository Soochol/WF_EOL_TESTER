# Hardware Monitoring Dashboard - EOL Tester CLI

## Overview

The Hardware Monitoring Dashboard is a comprehensive real-time monitoring system for the EOL (End-of-Line) Tester CLI. It provides live hardware status updates, key metrics display, and professional Rich UI formatting for monitoring Robot, MCU, LoadCell, and Power components.

## Features

### 🎯 Real-time Hardware Monitoring
- **Live Status Updates**: Real-time connection status for all hardware components
- **Color-coded Indicators**: Green (Connected), Red (Disconnected), Yellow (Warning states)
- **Automatic Refresh**: Configurable refresh rates from 1-10 seconds
- **Error Recovery**: Graceful handling of hardware disconnections with automatic retry

### 📊 Comprehensive Metrics Display

#### Robot Controller
- Connection status and current position readings
- Motion status (Idle, Moving, Error, etc.)
- Velocity information and movement detection
- Real-time axis status indicators

#### MCU (Microcontroller)
- Temperature readings with warning levels
- Fan speed monitoring and control status
- Test mode display (Mode 1, Mode 2, Mode 3)
- Thermal status indicators (Normal/Warm/High)

#### LoadCell Sensor
- Real-time force measurements in Newtons
- Raw ADC values for detailed analysis
- Calibration status monitoring
- Force level warnings and indicators

#### Power Supply
- Voltage and current measurements
- Output enable/disable status
- Power level warnings for out-of-range values
- Connection and safety status

### 🎨 Professional UI Design
- **Rich Layout**: Professional grid-based dashboard layout
- **Live Updates**: Smooth real-time updates without screen flicker
- **Status Summary**: Overall system status at a glance
- **Interactive Controls**: Easy navigation and configuration

### 💾 Data Management
- **Session Recording**: Automatic data collection during monitoring sessions
- **Export Functionality**: JSON export with complete metrics history
- **Memory Efficient**: Automatic history limiting (100 data points max)
- **Session Summaries**: Statistical analysis of monitoring sessions

## Installation & Integration

### File Structure
```
src/ui/cli/
├── hardware_monitoring_dashboard.py    # Core dashboard implementation
├── dashboard_integration.py            # CLI integration helper
├── dashboard_demo.py                   # Standalone demonstration
└── enhanced_eol_tester_cli.py          # Updated CLI with dashboard
```

### Dependencies
- `rich`: For professional terminal UI components
- `asyncio`: For asynchronous hardware data collection
- `json`: For data export functionality
- `loguru`: For logging (optional, falls back to standard logging)

### Integration Steps

1. **Import Dashboard Components** (already done):
```python
from .dashboard_integration import create_dashboard_integrator
```

2. **Initialize in CLI Constructor** (already done):
```python
if self._hardware_facade:
    self._dashboard_integrator = create_dashboard_integrator(
        self._hardware_facade, self._console, self._formatter
    )
```

3. **Add Menu Option** (already done):
```python
# Menu option 4: Real-time Monitoring Dashboard
elif choice == "4":
    await self._real_time_monitoring_dashboard()
```

## Usage

### From Enhanced CLI

1. **Start the Enhanced EOL Tester CLI**
2. **Select Option 4**: "Real-time Monitoring Dashboard"
3. **Choose Dashboard Action**:
   - `1` - Start Real-time Monitoring Dashboard
   - `2` - Configure Dashboard Settings
   - `3` - View Last Monitoring Session Data
   - `4` - Export Historical Data
   - `5` - Dashboard Help & Information

### Standalone Demo

Run the dashboard demonstration:
```bash
python3 src/ui/cli/dashboard_demo.py
```

### Direct Integration

```python
from ui.cli.hardware_monitoring_dashboard import create_dashboard_manager
from infrastructure.factory import create_hardware_service_facade

# Create hardware facade
hardware_facade = create_hardware_service_facade(use_mock=True)

# Create dashboard
dashboard = create_dashboard_manager(hardware_facade, console)

# Start monitoring
await dashboard.start_monitoring(refresh_rate=2.0)
```

## Configuration Options

### Refresh Rate
- **Range**: 1.0 - 10.0 seconds
- **Default**: 2.0 seconds
- **Impact**: Lower rates = more responsive, higher system load

### Export Directory
- **Default**: `./dashboard_exports`
- **Customizable**: Any accessible directory path
- **Auto-creation**: Creates directory if it doesn't exist

### Memory Management
- **History Limit**: 100 data points maximum
- **Estimated Duration**: 3-17 minutes of data (depending on refresh rate)
- **Automatic Cleanup**: Oldest data removed when limit exceeded

## Data Export Format

### JSON Structure
```json
{
  "export_timestamp": "2024-01-15T10:30:00",
  "refresh_rate": 2.0,
  "metrics_count": 150,
  "metrics_history": [
    {
      "timestamp": 1705315800.123,
      "robot_connected": true,
      "robot_position": 25.450,
      "robot_velocity": 10.0,
      "robot_motion_status": "IDLE",
      "robot_is_moving": false,
      "mcu_connected": true,
      "mcu_temperature": 65.2,
      "mcu_fan_speed": 75.0,
      "mcu_test_mode": "MODE_1",
      "loadcell_connected": true,
      "loadcell_force": 2.345,
      "loadcell_raw_value": 12450.0,
      "power_connected": true,
      "power_voltage": 24.1,
      "power_current": 1.85,
      "power_output_enabled": true
    }
    // ... more data points
  ]
}
```

## Dashboard Controls

### During Monitoring
- **Ctrl+C**: Stop monitoring and return to menu
- **Automatic Updates**: Dashboard refreshes at configured rate
- **Status Indicators**: Real-time visual feedback

### Menu Navigation
- **Numeric Selection**: Use numbers 1-5 to select options
- **Back Navigation**: Use 'b' to return to previous menu
- **Ctrl+C**: Exit current operation or menu

## Error Handling

### Hardware Disconnections
- **Graceful Degradation**: Dashboard continues running with last known data
- **Visual Indicators**: Clear indication of disconnected components
- **Automatic Recovery**: Attempts to reconnect on next refresh cycle

### Data Collection Errors
- **Individual Component Isolation**: Failure in one component doesn't affect others
- **Fallback Data**: Uses last successful data when collection fails
- **Debug Logging**: Detailed error information for troubleshooting

### UI Resilience
- **Screen Size Adaptation**: Works with various terminal sizes
- **Refresh Stability**: No screen flicker during updates
- **Memory Management**: Automatic cleanup prevents memory leaks

## Mock Hardware Support

The dashboard works seamlessly with mock hardware implementations:

- **Safe Testing**: No risk of hardware damage during development
- **Complete Simulation**: All hardware types supported in mock mode
- **Realistic Data**: Mock hardware provides realistic sensor values
- **Connection Simulation**: Simulates connection/disconnection scenarios

## Technical Architecture

### Component Structure
```
HardwareMonitoringDashboard
├── HardwareDataCollector    # Safe data collection with error handling
├── DashboardRenderer        # UI layout and Rich formatting
├── HardwareMetrics         # Data structure for metrics storage
└── DashboardIntegrator     # CLI integration and menu handling
```

### Async Architecture
- **Non-blocking UI**: Dashboard updates don't block user interaction
- **Concurrent Data Collection**: All hardware components queried simultaneously
- **Efficient Resource Usage**: Minimal CPU and memory footprint

### Memory Efficiency
- **Circular Buffer**: Fixed-size history buffer with automatic cleanup
- **Lazy Evaluation**: Data collected only when needed
- **Optimized Updates**: Only changed data triggers UI refresh

## Best Practices

### Performance Optimization
1. **Choose Appropriate Refresh Rate**: Balance responsiveness vs. system load
2. **Monitor Memory Usage**: Export and clear history for long-running sessions
3. **Use Mock Hardware**: For development and testing scenarios

### Data Management
1. **Regular Exports**: Export important monitoring sessions
2. **Directory Organization**: Use descriptive export directory names
3. **Timestamp Tracking**: Exported files include timestamps for organization

### Troubleshooting
1. **Check Hardware Connections**: Verify physical connections first
2. **Review Export Data**: Use exported data for detailed analysis
3. **Monitor System Resources**: Ensure adequate CPU and memory

## Future Enhancements

### Planned Features
- **Historical Trend Analysis**: Graphical display of trends over time
- **Alert System**: Configurable alerts for threshold violations
- **Remote Monitoring**: Web-based dashboard for remote access
- **Data Analytics**: Statistical analysis and reporting features

### Extension Points
- **Custom Metrics**: Add new hardware-specific metrics
- **Plugin Architecture**: Support for additional hardware types
- **Integration APIs**: REST API for external monitoring systems
- **Database Storage**: Long-term data storage and retrieval

## Support & Troubleshooting

### Common Issues
1. **Dashboard Won't Start**: Check hardware facade initialization
2. **No Data Display**: Verify hardware connections and mock mode settings
3. **Export Failures**: Check directory permissions and disk space
4. **Performance Issues**: Adjust refresh rate or check system resources

### Debug Information
- **Log Files**: Check application logs for detailed error information
- **Export Data**: Review exported metrics for data collection issues
- **Console Output**: Monitor console for real-time error messages

### Getting Help
- **Documentation**: This README and inline code documentation
- **Demo Script**: Use `dashboard_demo.py` for feature exploration
- **Test Script**: Use `test_dashboard_integration.py` for validation

## License & Credits

This dashboard implementation is part of the EOL Tester CLI system and follows the same licensing terms as the main project. It uses the Rich library for professional terminal UI components and integrates with the existing hardware abstraction layer.

---

*For technical support or feature requests, please refer to the main project documentation or contact the development team.*