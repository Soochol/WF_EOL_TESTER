"""
Mock MCU Adapter

Mock implementation of MCUAdapter for testing and development.
Simulates MCU operations without requiring real hardware.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, Callable
from loguru import logger

from ....domain.entities.hardware_device import HardwareDevice
from ....domain.enums.hardware_status import HardwareStatus
from ....domain.enums.measurement_units import MeasurementUnit
from ....domain.value_objects.measurements import TemperatureValue
from ....domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    HardwareNotReadyException,
    UnsafeOperationException
)

from ....controllers.mcu_controller.base import TestMode, MCUStatus
from ...interfaces.mcu_adapter import MCUAdapter


class MockMCUAdapter(MCUAdapter):
    """
    Mock MCU adapter implementation
    
    Simulates MCU operations for testing and development.
    Provides realistic behavior without requiring real hardware.
    """
    
    def __init__(self):
        """Initialize Mock MCU adapter"""
        super().__init__("mock", "simulated")
        self._is_connected = False
        self._is_monitoring = False
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        self._hardware_device = self._create_mock_hardware_device()
        
        # Mock state
        self._current_temperature = TemperatureValue(25.0, MeasurementUnit.CELSIUS)
        self._target_temperature = TemperatureValue(25.0, MeasurementUnit.CELSIUS)
        self._upper_temperature = TemperatureValue(80.0, MeasurementUnit.CELSIUS)
        self._cooling_temperature = TemperatureValue(20.0, MeasurementUnit.CELSIUS)
        self._fan_speed = 3
        self._mcu_status = MCUStatus.IDLE
        
        # Initialize safety limits
        self._safety_limits = {
            "max_temperature": TemperatureValue(150.0, MeasurementUnit.CELSIUS),
            "min_temperature": TemperatureValue(-40.0, MeasurementUnit.CELSIUS),
            "max_fan_speed": 10,
            "min_fan_speed": 1
        }
    
    def _create_mock_hardware_device(self) -> HardwareDevice:
        """Create mock hardware device entity"""
        return self._create_hardware_device(
            connection_info="mock://mcu_simulator",
            device_id="mock_mcu_001",
            capabilities={
                "temperature_control": True,
                "test_modes": [mode.name for mode in TestMode],
                "fan_control": True,
                "temperature_monitoring": True,
                "safety_shutdown": True,
                "self_test": True,
                "max_temperature": 150.0,  # °C
                "min_temperature": -40.0,  # °C
                "temperature_precision": 0.1,  # °C
                "fan_levels": 10,
                "hold_time_range": {"min": 100, "max": 60000},  # ms
                "simulation": True
            }
        )
    
    async def connect(self) -> None:
        """Connect to mock MCU"""
        try:
            # Simulate connection delay
            await asyncio.sleep(0.1)
            
            self._is_connected = True
            self._hardware_device.set_status(HardwareStatus.CONNECTED)
            self._log_operation("connect", True)
            logger.info("Connected to mock MCU")
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("connect", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_MCU_CONNECTION_FAILED",
                f"Failed to connect to mock MCU: {str(e)}",
                {"controller_type": "MockMCU"}
            )
    
    async def disconnect(self) -> None:
        """Disconnect from mock MCU"""
        try:
            # Stop all monitoring sessions
            for session_id in list(self._monitoring_tasks.keys()):
                await self.stop_temperature_monitoring(session_id)
            
            self._is_connected = False
            self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
            self._log_operation("disconnect", True)
            logger.info("Disconnected from mock MCU")
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("disconnect", False, str(e))
            raise BusinessRuleViolationException(
                "MOCK_MCU_DISCONNECTION_FAILED",
                f"Failed to disconnect from mock MCU: {str(e)}",
                {"controller_type": "MockMCU"}
            )
    
    async def is_connected(self) -> bool:
        """Check connection status"""
        if self._is_connected:
            if self._hardware_device.status != HardwareStatus.CONNECTED:
                self._hardware_device.set_status(HardwareStatus.CONNECTED)
        else:
            if self._hardware_device.status == HardwareStatus.CONNECTED:
                self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
        
        return self._is_connected
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device with updated status"""
        await self.is_connected()
        return self._hardware_device
    
    # Test Mode Management
    async def enter_test_mode(self, mode: TestMode) -> None:
        """Enter specified test mode"""
        self._validate_connection("enter_test_mode")
        
        try:
            # Simulate mode entry delay
            await asyncio.sleep(0.05)
            
            self._current_mode = mode
            self._mcu_status = MCUStatus.HEATING if mode != TestMode.MODE_1 else MCUStatus.IDLE
            
            self._log_operation("enter_test_mode", True)
            logger.info(f"Entered test mode: {mode.name}")
            
        except Exception as e:
            self._log_operation("enter_test_mode", False, str(e))
            raise BusinessRuleViolationException(
                "TEST_MODE_ENTRY_FAILED",
                f"Failed to enter test mode {mode.name}: {str(e)}",
                {"mode": mode.name}
            )
    
    async def exit_test_mode(self) -> None:
        """Exit current test mode and return to idle"""
        self._validate_connection("exit_test_mode")
        
        if self._current_mode is None:
            return  # Already in idle mode
        
        try:
            # Simulate mode exit delay
            await asyncio.sleep(0.05)
            
            previous_mode = self._current_mode
            self._current_mode = None
            self._mcu_status = MCUStatus.IDLE
            
            self._log_operation("exit_test_mode", True)
            logger.info(f"Exited test mode: {previous_mode.name if previous_mode else 'unknown'}")
            
        except Exception as e:
            self._log_operation("exit_test_mode", False, str(e))
            raise BusinessRuleViolationException(
                "TEST_MODE_EXIT_FAILED",
                f"Failed to exit test mode: {str(e)}",
                {"current_mode": self._current_mode}
            )
    
    async def get_current_test_mode(self) -> Optional[TestMode]:
        """Get current test mode"""
        self._validate_connection("get_current_test_mode")
        return self._current_mode
    
    # Temperature Control
    async def set_temperature_profile(
        self, 
        upper_temp: TemperatureValue,
        operating_temp: TemperatureValue, 
        cooling_temp: TemperatureValue
    ) -> None:
        """Set complete temperature profile with safety validation"""
        self._validate_connection("set_temperature_profile")
        
        # Validate temperature safety
        self._validate_temperature_safety(operating_temp, upper_temp, cooling_temp)
        
        try:
            # Simulate setting delay
            await asyncio.sleep(0.02)
            
            self._upper_temperature = upper_temp
            self._target_temperature = operating_temp
            self._cooling_temperature = cooling_temp
            
            self._log_operation("set_temperature_profile", True)
            logger.info(f"Set temperature profile: upper={upper_temp}, operating={operating_temp}, cooling={cooling_temp}")
            
        except Exception as e:
            self._log_operation("set_temperature_profile", False, str(e))
            raise BusinessRuleViolationException(
                "TEMPERATURE_PROFILE_SET_FAILED",
                f"Failed to set temperature profile: {str(e)}",
                {"upper_temp": upper_temp.to_celsius(), "operating_temp": operating_temp.to_celsius(), "cooling_temp": cooling_temp.to_celsius()}
            )
    
    async def set_operating_temperature(self, temperature: TemperatureValue) -> None:
        """Set operating temperature target with safety checks"""
        self._validate_connection("set_operating_temperature")
        
        # Validate temperature range
        if not await self.validate_temperature_range(temperature):
            raise UnsafeOperationException(
                "TEMPERATURE_OUT_OF_RANGE",
                f"Temperature {temperature} is outside safe operating range",
                {"temperature": temperature.to_celsius(), "safe_range": f"{self._safety_limits['min_temperature']} to {self._safety_limits['max_temperature']}"}
            )
        
        try:
            # Simulate setting delay
            await asyncio.sleep(0.02)
            
            self._target_temperature = temperature
            
            self._log_operation("set_operating_temperature", True)
            logger.info(f"Set operating temperature: {temperature}")
            
        except Exception as e:
            self._log_operation("set_operating_temperature", False, str(e))
            raise BusinessRuleViolationException(
                "SET_OPERATING_TEMPERATURE_FAILED",
                f"Failed to set operating temperature: {str(e)}",
                {"temperature": temperature.to_celsius()}
            )
    
    async def get_current_temperature(self) -> TemperatureValue:
        """Get current temperature reading"""
        self._validate_connection("get_current_temperature")
        
        try:
            # Simulate gradual temperature change towards target
            current_celsius = self._current_temperature.to_celsius()
            target_celsius = self._target_temperature.to_celsius()
            
            # Simple temperature simulation: move 10% towards target
            if abs(current_celsius - target_celsius) > 0.1:
                diff = target_celsius - current_celsius
                new_temp = current_celsius + (diff * 0.1)
                self._current_temperature = TemperatureValue(new_temp, MeasurementUnit.CELSIUS)
            
            # Add small random variation (±0.2°C)
            import random
            variation = random.uniform(-0.2, 0.2)
            measured_temp = self._current_temperature.to_celsius() + variation
            
            temperature = TemperatureValue(measured_temp, MeasurementUnit.CELSIUS)
            self._log_operation("get_current_temperature", True)
            return temperature
            
        except Exception as e:
            self._log_operation("get_current_temperature", False, str(e))
            raise BusinessRuleViolationException(
                "TEMPERATURE_READ_FAILED",
                f"Failed to read current temperature: {str(e)}",
                {}
            )
    
    async def get_temperature_profile(self) -> Dict[str, TemperatureValue]:
        """Get current temperature profile settings"""
        self._validate_connection("get_temperature_profile")
        
        try:
            profile = {
                "upper": self._upper_temperature,
                "operating": self._target_temperature,
                "cooling": self._cooling_temperature,
                "current": await self.get_current_temperature()
            }
            
            return profile
            
        except Exception as e:
            self._log_operation("get_temperature_profile", False, str(e))
            raise BusinessRuleViolationException(
                "GET_TEMPERATURE_PROFILE_FAILED",
                f"Failed to get temperature profile: {str(e)}",
                {}
            )
    
    # Fan Control
    async def set_fan_speed(self, level: int) -> None:
        """Set fan speed level with validation"""
        self._validate_connection("set_fan_speed")
        self._validate_fan_speed_range(level)
        
        try:
            # Simulate setting delay
            await asyncio.sleep(0.01)
            
            self._fan_speed = level
            
            self._log_operation("set_fan_speed", True)
            logger.info(f"Set fan speed to level {level}")
            
        except Exception as e:
            self._log_operation("set_fan_speed", False, str(e))
            raise BusinessRuleViolationException(
                "SET_FAN_SPEED_FAILED",
                f"Failed to set fan speed: {str(e)}",
                {"level": level}
            )
    
    async def get_fan_speed(self) -> int:
        """Get current fan speed level"""
        self._validate_connection("get_fan_speed")
        
        try:
            self._log_operation("get_fan_speed", True)
            return self._fan_speed
            
        except Exception as e:
            self._log_operation("get_fan_speed", False, str(e))
            raise BusinessRuleViolationException(
                "FAN_SPEED_READ_FAILED",
                f"Failed to read fan speed: {str(e)}",
                {}
            )
    
    # MCU Initialization and Configuration
    async def initialize_mcu(
        self, 
        operating_temp: TemperatureValue,
        standby_temp: TemperatureValue, 
        hold_time_ms: int
    ) -> None:
        """Initialize MCU with operation parameters and safety validation"""
        self._validate_connection("initialize_mcu")
        self._validate_hold_time(hold_time_ms)
        
        # Validate temperatures
        if not await self.validate_temperature_range(operating_temp):
            raise UnsafeOperationException(
                "UNSAFE_OPERATING_TEMPERATURE",
                f"Operating temperature {operating_temp} is outside safe range",
                {"temperature": operating_temp.to_celsius()}
            )
        
        if not await self.validate_temperature_range(standby_temp):
            raise UnsafeOperationException(
                "UNSAFE_STANDBY_TEMPERATURE",
                f"Standby temperature {standby_temp} is outside safe range",
                {"temperature": standby_temp.to_celsius()}
            )
        
        try:
            # Simulate initialization delay
            await asyncio.sleep(0.1)
            
            # Set initial state
            self._target_temperature = operating_temp
            self._mcu_status = MCUStatus.IDLE
            
            self._log_operation("initialize_mcu", True)
            logger.info(f"MCU initialized: operating={operating_temp}, standby={standby_temp}, hold_time={hold_time_ms}ms")
            
        except Exception as e:
            self._log_operation("initialize_mcu", False, str(e))
            raise BusinessRuleViolationException(
                "MCU_INITIALIZATION_FAILED",
                f"Failed to initialize MCU: {str(e)}",
                {
                    "operating_temp": operating_temp.to_celsius(),
                    "standby_temp": standby_temp.to_celsius(),
                    "hold_time_ms": hold_time_ms
                }
            )
    
    # Status and Monitoring
    async def get_mcu_status(self) -> MCUStatus:
        """Get current MCU operational status"""
        self._validate_connection("get_mcu_status")
        
        try:
            # Update status based on current conditions
            current_temp = await self.get_current_temperature()
            target_temp = self._target_temperature.to_celsius()
            
            if self._current_mode is None:
                self._mcu_status = MCUStatus.IDLE
            elif abs(current_temp.to_celsius() - target_temp) > 2.0:
                if current_temp.to_celsius() < target_temp:
                    self._mcu_status = MCUStatus.HEATING
                else:
                    self._mcu_status = MCUStatus.COOLING
            else:
                self._mcu_status = MCUStatus.HOLDING
            
            self._log_operation("get_mcu_status", True)
            return self._mcu_status
            
        except Exception as e:
            self._log_operation("get_mcu_status", False, str(e))
            raise BusinessRuleViolationException(
                "GET_MCU_STATUS_FAILED",
                f"Failed to get MCU status: {str(e)}",
                {}
            )
    
    async def start_temperature_monitoring(
        self, 
        callback: Callable[[TemperatureValue, MCUStatus], None],
        interval_ms: int = 1000
    ) -> str:
        """Start temperature monitoring with callback"""
        self._validate_connection("start_temperature_monitoring")
        self._validate_monitoring_interval(interval_ms)
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        try:
            # Create monitoring task
            task = asyncio.create_task(
                self._temperature_monitoring_loop(callback, interval_ms, session_id)
            )
            
            self._monitoring_tasks[session_id] = task
            self._monitoring_sessions[session_id] = {
                "callback": callback,
                "interval_ms": interval_ms,
                "started_at": asyncio.get_event_loop().time()
            }
            
            self._log_operation("start_temperature_monitoring", True)
            logger.info(f"Started temperature monitoring session {session_id} with {interval_ms}ms interval")
            
            return session_id
            
        except Exception as e:
            self._log_operation("start_temperature_monitoring", False, str(e))
            raise BusinessRuleViolationException(
                "START_MONITORING_FAILED",
                f"Failed to start temperature monitoring: {str(e)}",
                {"interval_ms": interval_ms}
            )
    
    async def stop_temperature_monitoring(self, session_id: str) -> None:
        """Stop temperature monitoring session"""
        if session_id not in self._monitoring_tasks:
            raise BusinessRuleViolationException(
                "MONITORING_SESSION_NOT_FOUND",
                f"Monitoring session {session_id} not found",
                {"session_id": session_id}
            )
        
        try:
            task = self._monitoring_tasks.pop(session_id)
            self._monitoring_sessions.pop(session_id, None)
            
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self._log_operation("stop_temperature_monitoring", True)
            logger.info(f"Stopped temperature monitoring session {session_id}")
            
        except Exception as e:
            self._log_operation("stop_temperature_monitoring", False, str(e))
            raise BusinessRuleViolationException(
                "STOP_MONITORING_FAILED",
                f"Failed to stop temperature monitoring: {str(e)}",
                {"session_id": session_id}
            )
    
    async def _temperature_monitoring_loop(
        self, 
        callback: Callable[[TemperatureValue, MCUStatus], None],
        interval_ms: int,
        session_id: str
    ) -> None:
        """Internal temperature monitoring loop"""
        sleep_interval = interval_ms / 1000.0
        
        while session_id in self._monitoring_tasks:
            try:
                temperature = await self.get_current_temperature()
                status = await self.get_mcu_status()
                
                # Execute callback
                try:
                    callback(temperature, status)
                except Exception as e:
                    logger.error(f"Error in temperature monitoring callback: {e}")
                
                await asyncio.sleep(sleep_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in temperature monitoring loop: {e}")
                await asyncio.sleep(sleep_interval)
    
    # Safety and Validation
    async def validate_temperature_range(self, temperature: TemperatureValue) -> bool:
        """Validate if temperature is within safe operating range"""
        try:
            temp_celsius = temperature.to_celsius()
            min_temp = self._safety_limits["min_temperature"].to_celsius()
            max_temp = self._safety_limits["max_temperature"].to_celsius()
            
            return min_temp <= temp_celsius <= max_temp
            
        except Exception:
            return False
    
    async def emergency_shutdown(self) -> None:
        """Perform emergency shutdown of MCU operations"""
        try:
            # Set fan to maximum speed
            self._fan_speed = 10
            
            # Exit test mode
            if self._current_mode:
                await self.exit_test_mode()
            
            # Stop all monitoring
            for session_id in list(self._monitoring_tasks.keys()):
                await self.stop_temperature_monitoring(session_id)
            
            # Set status to safe state
            self._mcu_status = MCUStatus.IDLE
            self._target_temperature = TemperatureValue(25.0, MeasurementUnit.CELSIUS)
            
            self._log_operation("emergency_shutdown", True)
            logger.warning("Emergency shutdown completed")
            
        except Exception as e:
            self._log_operation("emergency_shutdown", False, str(e))
            raise BusinessRuleViolationException(
                "EMERGENCY_SHUTDOWN_FAILED",
                f"Failed to perform emergency shutdown: {str(e)}",
                {}
            )
    
    async def reset_mcu(self) -> None:
        """Reset MCU to default state"""
        try:
            # Stop monitoring
            for session_id in list(self._monitoring_tasks.keys()):
                await self.stop_temperature_monitoring(session_id)
            
            # Exit test mode
            if self._current_mode:
                await self.exit_test_mode()
            
            # Reset to defaults
            self._current_temperature = TemperatureValue(25.0, MeasurementUnit.CELSIUS)
            self._target_temperature = TemperatureValue(25.0, MeasurementUnit.CELSIUS)
            self._upper_temperature = TemperatureValue(80.0, MeasurementUnit.CELSIUS)
            self._cooling_temperature = TemperatureValue(20.0, MeasurementUnit.CELSIUS)
            self._fan_speed = 3
            self._mcu_status = MCUStatus.IDLE
            
            self._log_operation("reset_mcu", True)
            logger.info("MCU reset completed")
            
        except Exception as e:
            self._log_operation("reset_mcu", False, str(e))
            raise BusinessRuleViolationException(
                "MCU_RESET_FAILED",
                f"Failed to reset MCU: {str(e)}",
                {}
            )
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get MCU device information and capabilities"""
        try:
            return {
                "device_type": "MCU",
                "vendor": self.vendor,
                "model": "Mock Simulator",
                "connection": {
                    "type": "simulation",
                    "url": "mock://mcu_simulator"
                },
                "capabilities": self._hardware_device.capabilities,
                "current_status": {
                    "test_mode": self._current_mode.name if self._current_mode else "IDLE",
                    "mcu_status": self._mcu_status.name,
                    "monitoring_sessions": len(self._monitoring_tasks),
                    "current_temperature": self._current_temperature.to_celsius(),
                    "target_temperature": self._target_temperature.to_celsius(),
                    "fan_speed": self._fan_speed
                },
                "safety_limits": {
                    "max_temperature": self._safety_limits["max_temperature"].to_celsius(),
                    "min_temperature": self._safety_limits["min_temperature"].to_celsius(),
                    "max_fan_speed": self._safety_limits["max_fan_speed"],
                    "min_fan_speed": self._safety_limits["min_fan_speed"]
                }
            }
            
        except Exception as e:
            self._log_operation("get_device_info", False, str(e))
            raise BusinessRuleViolationException(
                "GET_DEVICE_INFO_FAILED",
                f"Failed to get device info: {str(e)}",
                {}
            )
    
    async def run_self_test(self) -> Dict[str, Any]:
        """Run MCU self-test diagnostics"""
        self._validate_connection("run_self_test")
        
        test_results = {
            "test_passed": True,
            "tests": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Simulate test delay
            await asyncio.sleep(0.2)
            
            # Test connection
            test_results["tests"]["connection"] = await self.is_connected()
            if not test_results["tests"]["connection"]:
                test_results["test_passed"] = False
                test_results["errors"].append("Connection test failed")
            
            # Test temperature reading
            try:
                temperature = await self.get_current_temperature()
                test_results["tests"]["temperature_read"] = True
                test_results["current_temperature"] = temperature.to_celsius()
            except Exception as e:
                test_results["tests"]["temperature_read"] = False
                test_results["test_passed"] = False
                test_results["errors"].append(f"Temperature reading failed: {str(e)}")
            
            # Test fan speed reading
            try:
                fan_speed = await self.get_fan_speed()
                test_results["tests"]["fan_read"] = True
                test_results["current_fan_speed"] = fan_speed
            except Exception as e:
                test_results["tests"]["fan_read"] = False
                test_results["test_passed"] = False
                test_results["errors"].append(f"Fan speed reading failed: {str(e)}")
            
            # Test MCU status
            try:
                mcu_status = await self.get_mcu_status()
                test_results["tests"]["mcu_status"] = True
                test_results["mcu_status"] = mcu_status.name
            except Exception as e:
                test_results["tests"]["mcu_status"] = False
                test_results["test_passed"] = False
                test_results["errors"].append(f"MCU status reading failed: {str(e)}")
            
            self._log_operation("run_self_test", test_results["test_passed"])
            return test_results
            
        except Exception as e:
            self._log_operation("run_self_test", False, str(e))
            raise BusinessRuleViolationException(
                "SELF_TEST_FAILED",
                f"Failed to run self-test: {str(e)}",
                {}
            )