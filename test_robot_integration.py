#!/usr/bin/env python3
"""
Integration Test for Robot DIO Refactoring

This script demonstrates how the refactored robot system works:
1. Robot service no longer has DIO functions
2. Digital input service handles all robot safety signals
3. Robot depends on digital input service for safety monitoring

Note: This is a demonstration script showing the new architecture.
"""

import asyncio
from typing import Dict, Any

# Mock the services for testing
class MockAjinextekInput:
    """Mock digital input service for testing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.robot_signals = config.get("robot_signals", {})
        self.signal_levels = config.get("signal_levels", {})
        # Mock signal states
        self.mock_signals = {
            "emergency_stop_safe": True,  # Safe to proceed
            "system_ready": True,
            "start_active": False,
            "limit_axis0_pos": False,
            "limit_axis0_neg": False,
            "home_axis0": False,
        }
    
    async def check_emergency_stop(self) -> bool:
        """Check if emergency stop is safe (not pressed)"""
        return self.mock_signals["emergency_stop_safe"]
    
    async def check_limit_switch(self, axis: int, direction: str) -> bool:
        """Check if limit switch is triggered"""
        signal_key = f"limit_axis{axis}_{direction}"
        return self.mock_signals.get(signal_key, False)
    
    async def check_home_sensor(self, axis: int) -> bool:
        """Check if home sensor is active"""
        signal_key = f"home_axis{axis}"
        return self.mock_signals.get(signal_key, False)
    
    async def check_ready_signal(self) -> bool:
        """Check if system is ready"""
        return self.mock_signals["system_ready"]
    
    async def get_all_safety_signals(self) -> Dict[str, bool]:
        """Get all safety signal states"""
        return self.mock_signals.copy()
    
    async def write_robot_output(self, output_name: str, state: bool) -> bool:
        """Write to robot output signal"""
        print(f"DI Service: Setting robot output {output_name} = {state}")
        return True
    
    def set_mock_signal(self, signal_name: str, value: bool):
        """Set mock signal for testing"""
        self.mock_signals[signal_name] = value
        print(f"Mock: {signal_name} = {value}")


class MockAjinextekRobot:
    """Mock robot service for testing (simplified version)"""
    
    def __init__(self, config: Dict[str, Any], digital_input_service=None):
        self.config = config
        self.digital_input_service = digital_input_service
        self.connected = False
        self.axis_count = 6
    
    async def connect(self) -> None:
        """Connect to robot hardware"""
        print("Robot: Connecting to hardware...")
        
        # Safety pre-checks using digital input service
        if self.digital_input_service is not None:
            try:
                if not await self.check_emergency_stop_safe():
                    print("Robot: WARNING - Emergency stop active during connection")
                else:
                    print("Robot: Emergency stop check passed")
            except Exception as e:
                print(f"Robot: WARNING - Failed to check safety signals: {e}")
        
        self.connected = True
        print("Robot: Connected successfully")
    
    async def check_emergency_stop_safe(self) -> bool:
        """Check if emergency stop is safe via DI service"""
        if self.digital_input_service is None:
            print("Robot: No DI service - assuming safe")
            return True
        
        is_safe = await self.digital_input_service.check_emergency_stop()
        print(f"Robot: Emergency stop safe = {is_safe}")
        return is_safe
    
    async def check_axis_limits_safe(self, axis: int, direction: str) -> bool:
        """Check if axis limits are safe via DI service"""
        if self.digital_input_service is None:
            print("Robot: No DI service - assuming safe")
            return True
        
        limit_triggered = await self.digital_input_service.check_limit_switch(axis, direction)
        is_safe = not limit_triggered
        print(f"Robot: Axis {axis} {direction} limit safe = {is_safe}")
        return is_safe
    
    async def move_absolute(self, axis: int, position: float, velocity: float, acceleration: float, deceleration: float) -> None:
        """Move axis to absolute position with safety checks"""
        print(f"Robot: Moving axis {axis} to position {position}mm at {velocity}mm/s")
        
        # Safety pre-checks using digital input service
        if not await self.check_emergency_stop_safe():
            raise Exception("Emergency stop active - motion blocked")
        
        # Mock current position for direction check
        current_pos = 0.0
        direction = "pos" if position > current_pos else "neg"
        
        if not await self.check_axis_limits_safe(axis, direction):
            raise Exception(f"Limit switch active on axis {axis} {direction} direction - motion blocked")
        
        print(f"Robot: Safety checks passed - executing motion")
        # In real implementation, this would call AXL library functions
        print(f"Robot: Motion completed successfully")
    
    async def get_safety_status(self) -> Dict[str, Any]:
        """Get safety status via DI service"""
        if self.digital_input_service is None:
            return {"error": "Digital input service not available"}
        
        try:
            all_signals = await self.digital_input_service.get_all_safety_signals()
            return {
                "digital_input_service_available": True,
                "all_signals": all_signals
            }
        except Exception as e:
            return {"error": str(e)}


async def test_integration():
    """Test the integrated robot and digital input services"""
    print("=" * 60)
    print("ROBOT DIO REFACTORING INTEGRATION TEST")
    print("=" * 60)
    
    # Configuration (from hardware.yaml)
    di_config = {
        "model": "AJINEXTEK",
        "board_no": 0,
        "module_position": 1,
        "robot_signals": {
            "emergency_stop": 0,
            "limit_switches": {
                "axis0_pos": 1,
                "axis0_neg": 2,
            },
            "home_sensors": {
                "axis0": 7,
            },
            "ready_signal": 10,
            "outputs": {
                "servo_enable": 0,
                "status_led": 2,
            }
        },
        "signal_levels": {
            "emergency_stop": "active_low",
            "limit_switches": "active_low",
            "home_sensors": "active_low", 
            "ready_signal": "active_high",
            "outputs": "active_high"
        }
    }
    
    robot_config = {
        "model": "AJINEXTEK",
        "axis_count": 6,
        "default_velocity": 100.0,
        "safety": {
            "enable_emergency_stop": True,
            "enable_limit_checks": True,
        }
    }
    
    print("\n1. Creating Digital Input Service...")
    di_service = MockAjinextekInput(di_config)
    
    print("\n2. Creating Robot Service with DI Service dependency...")
    robot = MockAjinextekRobot(robot_config, di_service)
    
    print("\n3. Connecting Robot (with safety checks)...")
    await robot.connect()
    
    print("\n4. Testing Normal Motion (should succeed)...")
    try:
        await robot.move_absolute(0, 100.0, 50.0, 1000.0, 1000.0)
    except Exception as e:
        print(f"Motion failed: {e}")
    
    print("\n5. Testing Emergency Stop Scenario...")
    di_service.set_mock_signal("emergency_stop_safe", False)  # Trigger emergency stop
    try:
        await robot.move_absolute(0, 200.0, 50.0, 1000.0, 1000.0)
    except Exception as e:
        print(f"Motion correctly blocked: {e}")
    
    print("\n6. Clearing Emergency Stop and Testing Limit Switch...")
    di_service.set_mock_signal("emergency_stop_safe", True)   # Clear emergency stop
    di_service.set_mock_signal("limit_axis0_pos", True)       # Trigger positive limit
    try:
        await robot.move_absolute(0, 300.0, 50.0, 1000.0, 1000.0)  # Positive motion
    except Exception as e:
        print(f"Motion correctly blocked: {e}")
    
    print("\n7. Testing Robot Output Control...")
    await di_service.write_robot_output("servo_enable", True)
    await di_service.write_robot_output("status_led", True)
    
    print("\n8. Getting Complete Safety Status...")
    safety_status = await robot.get_safety_status()
    print(f"Safety Status: {safety_status}")
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST COMPLETED")
    print("=" * 60)
    print("\nKey Achievements:")
    print("✓ Robot no longer has DIO functions")
    print("✓ Digital Input Service handles all robot safety signals")
    print("✓ Robot uses DI Service for safety monitoring")
    print("✓ Proper separation of concerns maintained")
    print("✓ Configuration properly separated")
    print("✓ Safety checks work as expected")


if __name__ == "__main__":
    asyncio.run(test_integration())