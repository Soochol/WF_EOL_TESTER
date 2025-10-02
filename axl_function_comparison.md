# AXL Function Coverage Analysis

## Summary

This document compares the AXL library functions available in the header files and web manual against the current implementation in `axl_wrapper.py`.

---

## Motion Functions (AxmMove*)

### ✅ Implemented in axl_wrapper.py
- `AxmMoveVel` → `move_start_vel()`
- `AxmMoveStartPos` → `move_start_pos()`
- `AxmMoveStop` → `move_stop()`
- `AxmMoveEStop` → `move_emergency_stop()`
- `AxmMoveSStop` → `move_smooth_stop()`
- `AxmMoveMultiPos` → `move_multi_start()`
- `AxmMoveMultiStop` → `move_multi_stop()`
- `AxmMoveSignalSearch` → `move_signal_search()`

### ❌ Missing from axl_wrapper.py
- `AxmMovePos` - Blocking position move with wait
- `AxmMovePosEx` - Extended position move
- `AxmMoveToAbsPos` - Move to absolute position
- `AxmMoveStartMultiPos` - Start multi-axis position move
- `AxmMoveStartMultiVel` - Start multi-axis velocity move
- `AxmMoveStartLineVel` - Start synchronized line velocity move
- `AxmMoveSignalCapture` - Capture position at signal
- `AxmMoveGetCapturePos` - Get captured position
- `AxmMoveMultiEStop` - Multi-axis emergency stop
- `AxmMoveMultiSStop` - Multi-axis smooth stop
- `AxmMoveStartPosEx` - Extended start position move
- `AxmMoveStartPosWithList` - Position move with velocity/accel list
- `AxmMoveStartPosWithPosEvent` - Position move with position event trigger
- `AxmMoveStartTorque` - Start torque mode move
- `AxmMoveTorqueStop` - Stop torque mode
- `AxmMovePVT` - PVT (Position-Velocity-Time) move
- `AxmMoveSignalSearchEx` - Extended signal search
- `AxmMoveSignalSearchAtDis` - Signal search at distance

---

## Status Functions (AxmStatus*)

### ✅ Implemented in axl_wrapper.py
- `AxmStatusGetCmdPos` → `get_cmd_pos()`
- `AxmStatusSetCmdPos` → `set_cmd_pos()`
- `AxmStatusGetActPos` → `get_act_pos()`
- `AxmStatusSetActPos` → `set_act_pos()`
- `AxmStatusReadInMotion` → `read_in_motion()`
- `AxmStatusSetReadServoLoadRatio` → `status_set_read_servo_load_ratio()`
- `AxmStatusReadServoLoadRatio` → `status_read_servo_load_ratio()`
- `AxmStatusReadTorque` → `status_read_torque()` (with graceful degradation)

### ❌ Missing from axl_wrapper.py
- `AxmStatusReadVel` - Read current velocity
- `AxmStatusReadActVel` - Read actual velocity
- `AxmStatusReadMotion` - Read motion status
- `AxmStatusReadStop` - Read stop status
- `AxmStatusReadMechanical` - Read mechanical signal status
- `AxmStatusReadPosError` - Read position error
- `AxmStatusReadDriveDistance` - Read total drive distance
- `AxmStatusReadDrivePulseCount` - Read drive pulse count
- `AxmStatusReadMotionInfo` - Read comprehensive motion information
- `AxmStatusSetPosMatch` - Match command and actual positions
- `AxmStatusReadServoAlarm` - Read servo alarm (partially implemented)
- `AxmStatusReadServoAlarmHistory` - Read servo alarm history
- `AxmStatusGetServoAlarmString` - Get alarm string description
- `AxmStatusSetServoMonitor` - Set servo monitor
- `AxmStatusGetServoMonitor` - Get servo monitor settings
- `AxmStatusReadServoMonitorValue` - Read servo monitor value
- `AxmStatusReadRemainQueueCount` - Read remaining queue count
- `AxmStatusSetAbsOrgOffset` - Set absolute origin offset
- `AxmStatusGetAmpActPos` - Get amplifier actual position

---

## Home Search Functions (AxmHome*)

### ✅ Implemented in axl_wrapper.py
- `AxmHomeSetMethod` → `home_set_method()`
- `AxmHomeSetVel` → `home_set_vel()`
- `AxmHomeSetStart` → `home_set_start()`
- `AxmHomeGetResult` → `home_get_result()`
- `AxmHomeGetRate` → `home_get_rate()`

### ❌ Missing from axl_wrapper.py
- `AxmHomeGetMethod` - Get homing method configuration
- `AxmHomeGetVel` - Get homing velocity settings
- `AxmHomeSetSignalLevel` - Set home signal level
- `AxmHomeGetSignalLevel` - Get home signal level
- `AxmHomeReadSignal` - Read home signal status
- `AxmHomeSetFineAdjust` - Set fine adjustment parameters
- `AxmHomeGetFineAdjust` - Get fine adjustment parameters
- `AxmHomeSetInterlock` - Set interlock for homing
- `AxmHomeGetInterlock` - Get interlock settings
- `AxmHomeSetResult` - Set home search result

---

## Signal Functions (AxmSignal*)

### ✅ Implemented in axl_wrapper.py
- `AxmSignalServoOn` → `servo_on()`
- `AxmSignalIsServoOn` → `is_servo_on()`
- `AxmSignalReadServoAlarm` → `read_servo_alarm()`
- `AxmSignalReadLimit` → `read_limit_status()`
- `AxmSignalSetLimit` → `set_limit_config()`

### ❌ Missing from axl_wrapper.py
- `AxmSignalGetInpos` - Get in-position signal configuration
- `AxmSignalSetInpos` - Set in-position signal
- `AxmSignalReadInpos` - Read in-position status
- `AxmSignalGetInposRange` - Get in-position range
- `AxmSignalSetInposRange` - Set in-position range
- `AxmSignalReadInput` - Read input signals
- `AxmSignalReadInputBit` - Read single input bit
- `AxmSignalReadOutput` - Read output signals
- `AxmSignalReadOutputBit` - Read single output bit
- `AxmSignalWriteOutput` - Write output signals
- `AxmSignalWriteOutputBit` - Write single output bit
- `AxmSignalOutputOn` - Turn output on
- `AxmSignalOutputOff` - Turn output off
- `AxmSignalGetServoAlarm` - Get servo alarm configuration
- `AxmSignalSetServoAlarm` - Set servo alarm configuration
- `AxmSignalReadServoAlarmCode` - Read servo alarm code
- `AxmSignalServoAlarmReset` - Reset servo alarm
- `AxmSignalGetServoOnLevel` - Get servo-on signal level
- `AxmSignalSetServoOnLevel` - Set servo-on signal level
- `AxmSignalGetServoAlarmResetLevel` - Get alarm reset level
- `AxmSignalSetServoAlarmResetLevel` - Set alarm reset level
- `AxmSignalReadStop` - Read stop signal
- `AxmSignalGetStop` - Get stop signal configuration
- `AxmSignalSetStop` - Set stop signal configuration
- `AxmSignalReadSoftLimit` - Read software limit status
- `AxmSignalGetSoftLimit` - Get software limit settings
- `AxmSignalSetSoftLimit` - Set software limit
- `AxmSignalGetLimit` - Get hardware limit configuration
- `AxmSignalSetZphaseLevel` - Set Z-phase level
- `AxmSignalGetZphaseLevel` - Get Z-phase level
- `AxmSignalSetHomeLevel` - Set home signal level
- `AxmSignalSetFilterBandwidth` - Set filter bandwidth
- `AxmSignalReadBrakeOn` - Read brake status
- `AxmSignalWriteBrakeOn` - Write brake control
- `AxmSignalSetWriteOutputBitAtPos` - Set output at position
- `AxmSignalGetWriteOutputBitAtPos` - Get output at position setting

---

## Motion Parameter Functions (AxmMot*)

### ✅ Implemented in axl_wrapper.py
- `AxmMotSetPulseOutMethod` → `set_pulse_out_method()`
- `AxmMotSetMoveUnitPerPulse` → `set_move_unit_per_pulse()`
- `AxmMotSetAbsRelMode` → `set_abs_rel_mode()`
- `AxmMotGetAbsRelMode` → `get_abs_rel_mode()`
- `AxmMotSetMaxVel` → `set_max_vel()`
- `AxmMotGetMaxVel` → `get_max_vel()`
- `AxmMotSetMinVel` → `set_min_vel()`
- `AxmMotGetMinVel` → `get_min_vel()`
- `AxmMotSetAccelUnit` → `set_accel_unit()`
- `AxmMotGetAccelUnit` → `get_accel_unit()`
- `AxmMotSetProfileMode` → `set_profile_mode()`
- `AxmMotGetProfileMode` → `get_profile_mode()`
- `AxmMotLoadParaAll` → `load_para_all()`
- `AxmMotSaveParaAll` → `save_para_all()`

### ❌ Missing from axl_wrapper.py
- `AxmMotGetPulseOutMethod` - Get pulse output method
- `AxmMotGetMoveUnitPerPulse` - Get move unit per pulse
- `AxmMotSetEncInputMethod` - Set encoder input method
- `AxmMotGetEncInputMethod` - Get encoder input method
- `AxmMotSetAccelJerk` - Set acceleration jerk
- `AxmMotGetAccelJerk` - Get acceleration jerk
- `AxmMotSetDecelJerk` - Set deceleration jerk
- `AxmMotGetDecelJerk` - Get deceleration jerk
- `AxmMotSetEndVel` - Set end velocity
- `AxmMotGetEndVel` - Get end velocity
- `AxmMotSetDecelMode` - Set deceleration mode
- `AxmMotGetDecelMode` - Get deceleration mode
- `AxmMotSetProfilePriority` - Set profile priority
- `AxmMotGetProfilePriority` - Get profile priority
- `AxmMotSetElectricGearRatio` - Set electronic gear ratio
- `AxmMotGetElectricGearRatio` - Get electronic gear ratio
- `AxmMotSetScaleCoeff` - Set scale coefficient
- `AxmMotGetScaleCoeff` - Get scale coefficient
- `AxmMotSetTorqueLimit` - Set torque limit
- `AxmMotGetTorqueLimit` - Get torque limit
- `AxmMotSetTorqueLimitEx` - Set torque limit extended
- `AxmMotGetTorqueLimitEx` - Get torque limit extended
- `AxmMotSetTorqueLimitAtPos` - Set torque limit at position
- `AxmMotGetTorqueLimitAtPos` - Get torque limit at position
- `AxmMotSetTorqueLimitEnable` - Enable/disable torque limit
- `AxmMotGetTorqueLimitEnable` - Get torque limit enable status
- `AxmMotSetOverridePosMode` - Set override position mode
- `AxmMotGetOverridePosMode` - Get override position mode
- `AxmMotSetOverrideLinePosMode` - Set override line position mode
- `AxmMotGetOverrideLinePosMode` - Get override line position mode
- `AxmMotGetFileName` - Get loaded parameter filename
- `AxmMotSetParaLoad` - Set parameter load (28-31)
- `AxmMotGetParaLoad` - Get parameter load (28-31)
- `AxmMotGetRemainPulse` - Get remaining pulse count

---

## Coverage Statistics

### Overall Function Coverage
- **Total AXL Motion Functions**: ~150+
- **Implemented in axl_wrapper.py**: ~50
- **Coverage Rate**: ~33%

### Category Breakdown
| Category | Total | Implemented | Coverage |
|----------|-------|-------------|----------|
| Move Functions | ~35 | 8 | 23% |
| Status Functions | ~30 | 8 | 27% |
| Home Functions | ~15 | 5 | 33% |
| Signal Functions | ~40 | 5 | 13% |
| Parameter Functions | ~50 | 14 | 28% |
| Digital I/O Functions | ~30 | 30 | 100% |

---

## Recommendations

### High Priority (Core Motion Control)
1. **Status Reading Functions**
   - `AxmStatusReadVel` - Essential for velocity monitoring
   - `AxmStatusReadPosError` - Critical for position error detection
   - `AxmStatusReadMotion` - General motion status

2. **Advanced Move Functions**
   - `AxmMovePos` - Blocking move (simpler than StartPos)
   - `AxmMoveSignalCapture` - Position capture functionality
   - `AxmMoveGetCapturePos` - Get captured positions

3. **Signal Functions**
   - `AxmSignalReadInpos` - In-position signal reading
   - `AxmSignalSetInpos` - In-position configuration

### Medium Priority (Enhanced Functionality)
1. **Parameter Get Functions**
   - Complete getter functions for all setters
   - `AxmMotGetPulseOutMethod`
   - `AxmMotGetEncInputMethod`

2. **Home Search**
   - `AxmHomeGetMethod` - Verify homing configuration
   - `AxmHomeGetVel` - Verify homing velocities

3. **Multi-axis Functions**
   - `AxmMoveStartMultiVel` - Multi-axis velocity mode
   - `AxmMoveMultiEStop` - Multi-axis emergency stop

### Low Priority (Advanced Features)
1. **Torque Control**
   - `AxmMoveStartTorque` - Torque mode control
   - `AxmMotSetTorqueLimit` - Torque limiting

2. **Override Functions**
   - `AxmOverridePos` - Position override
   - `AxmOverrideVel` - Velocity override

3. **Advanced Motion**
   - `AxmMovePVT` - PVT interpolation
   - Circular interpolation functions

---

## Notes

1. **Digital I/O Coverage**: 100% - All DIO functions are implemented
2. **Function Naming**: Python wrapper uses snake_case while AXL uses PascalCase
3. **Graceful Degradation**: Some functions (like `AxmStatusReadTorque`) have graceful degradation for hardware compatibility
4. **Missing Individual Parameter Functions**: `AxmMotLoadPara` and `AxmMotSavePara` don't exist in AXL library (only `*All` versions exist)

---

## Function Name Mapping Verification

### ✅ Correctly Named Functions
- `move_start_vel()` → `AxmMoveVel` ✓
- `move_multi_start()` → `AxmMoveMultiPos` ✓
- All other implemented functions match correctly

### ❌ Previous Issues (Now Fixed)
- ~~`AxmMoveStartVel`~~ → Fixed to `AxmMoveVel`
- ~~`AxmMoveMultiStart`~~ → Fixed to `AxmMoveMultiPos`
- ~~`AxmMotLoadPara`~~ → Removed (doesn't exist in DLL)
- ~~`AxmMotSavePara`~~ → Removed (doesn't exist in DLL)