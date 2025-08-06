# Windows Deployment Guide for AJINEXTEK Hardware Integration

This guide explains how to deploy and troubleshoot the AJINEXTEK AXL hardware integration on Windows systems.

## Prerequisites

1. **Windows System**: The AXL library only works on Windows
2. **AXL Hardware**: AJINEXTEK motion control hardware properly connected
3. **AXL Library**: AJINEXTEK AXL library installed in the system

## AXL Library Installation

1. Install the AJINEXTEK AXL library to the standard location:
   ```
   C:\AJINEXTEK\AXL\Library\64Bit\AXL.dll (for 64-bit systems)
   C:\AJINEXTEK\AXL\Library\32Bit\AXL.dll (for 32-bit systems)
   ```

2. Or place the AXL.dll in the project directory:
   ```
   src/driver/ajinextek/AXL(Library)/Library/64Bit/AXL.dll
   src/driver/ajinextek/AXL(Library)/Library/32Bit/AXL.dll
   ```

## Configuration

The system automatically handles:
- ✅ Missing AXL functions (reports as warnings, continues operation)
- ✅ Library initialization failures with retry logic
- ✅ Hardware detection errors with fallback values
- ✅ Progressive backoff for connection attempts

## Deployment Steps

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Hardware Configuration**:
   ```json
   {
     "robot": {
       "model": "ajinextek",
       "axis_id": 0,
       "irq_no": 7
     }
   }
   ```

3. **Run the Application**:
   ```bash
   python src/main.py
   ```

## Troubleshooting

### Error 1053: "Library initialization failed"

**Symptoms**: 
```
ERROR | Failed to create services: Robot (AJINEXTEK AXL): AxlGetBoardCount: Library initialization failed (Error Code: 1053)
```

**Solutions**:
1. **Check Hardware Connection**: Ensure AJINEXTEK hardware is properly connected and powered
2. **Verify IRQ Setting**: Try different IRQ numbers (typically 7, 5, or 3)
3. **Run as Administrator**: Some hardware requires elevated privileges
4. **Check DLL Path**: Verify AXL.dll is in the correct location
5. **Hardware Compatibility**: Ensure hardware is supported by the AXL library version

### Missing AXL Functions

**Symptoms**:
```
Warning: 4 AXL functions not found in DLL:
  - AxmMoveStartVel
  - AxmMoveMultiStart
  - AxmMotLoadPara
  - AxmMotSavePara
```

**Solution**: This is normal and expected. The system will continue to work with available functions.

### Development Mode (Non-Windows)

For development and testing on Linux/Mac:

```bash
export AXL_MOCK_MODE=true
python src/main.py
```

This enables mock mode that simulates the AXL wrapper without requiring Windows or actual hardware.

## Hardware Configuration Files

The system expects these configuration files:

1. **Robot Parameters**: `configuration/robot_params.mot`
   - Contains axis-specific motion parameters
   - Loaded automatically during initialization

2. **Hardware Config**: `configuration/hardware_config.json`
   - Contains hardware connection settings
   - Specifies IRQ, axis mapping, etc.

## Error Codes Reference

| Code | Meaning | Solution |
|------|---------|----------|
| 0 | Success | Normal operation |
| 1001 | Library not open | Call initialization first |
| 1002 | Library already open | Normal, will reuse connection |
| 1053 | Initialization failed | Check hardware/IRQ/permissions |
| 4051 | No motion module | Verify hardware installation |
| 4101 | Invalid axis | Check axis_id configuration |

## Performance Optimizations

The improved system includes:

1. **Retry Logic**: Automatic retry with progressive backoff
2. **Function Detection**: Skip missing functions gracefully  
3. **Error Recovery**: Continue operation despite non-critical failures
4. **Mock Mode**: Development testing without hardware

## Production Deployment Checklist

- [ ] Windows system with proper hardware drivers
- [ ] AXL.dll in correct location
- [ ] Hardware connected and powered
- [ ] Configuration files in place
- [ ] IRQ settings verified
- [ ] Application runs as Administrator (if required)
- [ ] Test basic motion operations
- [ ] Verify error handling works correctly

## Support

For hardware-specific issues:
1. Check AJINEXTEK documentation
2. Verify hardware compatibility
3. Contact AJINEXTEK support for driver issues

For software integration issues:
1. Check error logs for specific error codes
2. Verify configuration files
3. Test with mock mode first