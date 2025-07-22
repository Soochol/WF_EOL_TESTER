"""
Ajinextek DIO Input Adapter

Concrete implementation of InputAdapter for Ajinextek DIO controller.
Provides business logic abstraction over DIO controller for input detection.
"""

import asyncio
import uuid
from typing import Dict, Any, Callable, List
from loguru import logger

from ....domain.entities.hardware_device import HardwareDevice
from ....domain.enums.hardware_status import HardwareStatus
from ....domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    HardwareNotReadyException
)

from ....controllers.dio_controller.ajinextek.dio_controller import AjinextekDIOController
from ...interfaces.input_adapter import InputAdapter, InputTriggerType


class AjinextekDIOAdapter(InputAdapter):
    """
    Ajinextek DIO Input adapter implementation
    
    Provides business logic abstraction over Ajinextek DIO controller
    for input detection and trigger management.
    """
    
    def __init__(self, controller: AjinextekDIOController):
        """
        Initialize Ajinextek DIO adapter
        
        Args:
            controller: AjinextekDIOController instance to wrap
        """
        super().__init__("ajinextek", "dio")
        self._controller = controller
        self._is_monitoring = False
        self._monitoring_task = None
        self._pin_states = {}  # Track pin states for edge detection
        self._hardware_device = self._create_hardware_device_from_controller()
    
    def _create_hardware_device_from_controller(self) -> HardwareDevice:
        """Create hardware device entity from controller information"""
        return self._create_hardware_device(
            connection_info="ajinextek://dio",
            device_id=f"ajinextek_dio_{id(self._controller)}",
            capabilities={
                "max_modules": 8,  # Typical for Ajinextek systems
                "pins_per_module": 32,
                "input_support": True,
                "output_support": True,
                "trigger_detection": True,
                "debounce_support": True,
                "monitoring_rate": 100  # Hz
            }
        )
    
    async def connect(self) -> None:
        """Connect to Ajinextek DIO controller"""
        try:
            # Initialize DIO controller
            success = self._controller.initialize()
            if not success:
                raise BusinessRuleViolationException(
                    "AJINEXTEK_DIO_INIT_FAILED",
                    "Failed to initialize Ajinextek DIO controller",
                    {"controller_type": "AjinextekDIO"}
                )
            
            self._hardware_device.set_status(HardwareStatus.CONNECTED)
            self._log_operation("connect", True)
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("connect", False, str(e))
            raise BusinessRuleViolationException(
                "AJINEXTEK_DIO_CONNECTION_FAILED",
                f"Failed to connect to Ajinextek DIO: {str(e)}",
                {"controller_type": "AjinextekDIO"}
            )
    
    async def disconnect(self) -> None:
        """Disconnect from Ajinextek DIO controller"""
        try:
            # Stop monitoring if active
            if self._is_monitoring:
                await self.stop_monitoring()
            
            # Cleanup controller
            self._controller.cleanup()
            self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
            self._log_operation("disconnect", True)
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("disconnect", False, str(e))
            raise BusinessRuleViolationException(
                "AJINEXTEK_DIO_DISCONNECTION_FAILED",
                f"Failed to disconnect from Ajinextek DIO: {str(e)}",
                {"controller_type": "AjinextekDIO"}
            )
    
    async def is_connected(self) -> bool:
        """Check connection status"""
        try:
            is_connected = self._controller.is_connected()
            
            # Update hardware device status
            if is_connected:
                if self._hardware_device.status != HardwareStatus.CONNECTED:
                    self._hardware_device.set_status(HardwareStatus.CONNECTED)
            else:
                if self._hardware_device.status == HardwareStatus.CONNECTED:
                    self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
            
            return is_connected
            
        except Exception as e:
            self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            self._log_operation("connection_check", False, str(e))
            return False
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device with updated status"""
        await self.is_connected()
        return self._hardware_device
    
    async def read_input(self, module: int, pin: int) -> bool:
        """Read digital input state"""
        self._validate_connection("read_input")
        
        try:
            state = self._controller.read_input(module, pin)
            self._log_operation("read_input", True)
            return state
            
        except Exception as e:
            self._log_operation("read_input", False, str(e))
            raise BusinessRuleViolationException(
                "DIO_READ_INPUT_FAILED",
                f"Failed to read input from module {module}, pin {pin}: {str(e)}",
                {"module": module, "pin": pin}
            )
    
    async def read_all_inputs(self, module: int) -> Dict[int, bool]:
        """Read all input states for a module"""
        self._validate_connection("read_all_inputs")
        
        try:
            states = self._controller.read_all_inputs(module)
            self._log_operation("read_all_inputs", True)
            return states
            
        except Exception as e:
            self._log_operation("read_all_inputs", False, str(e))
            raise BusinessRuleViolationException(
                "DIO_READ_ALL_INPUTS_FAILED",
                f"Failed to read all inputs from module {module}: {str(e)}",
                {"module": module}
            )
    
    async def setup_trigger(
        self, 
        module: int, 
        pin: int, 
        trigger_type: InputTriggerType,
        callback: Callable[[int, int, bool], None],
        debounce_ms: int = 50
    ) -> str:
        """Setup input trigger monitoring"""
        self._validate_connection("setup_trigger")
        
        # Generate unique trigger ID
        trigger_id = str(uuid.uuid4())
        
        # Validate parameters
        if debounce_ms < 1:
            raise BusinessRuleViolationException(
                "INVALID_DEBOUNCE_TIME",
                f"Debounce time must be at least 1ms, got {debounce_ms}ms",
                {"debounce_ms": debounce_ms}
            )
        
        try:
            # Store trigger information
            trigger_info = {
                "module": module,
                "pin": pin,
                "trigger_type": trigger_type,
                "callback": callback,
                "debounce_ms": debounce_ms,
                "last_trigger_time": 0
            }
            
            self._trigger_callbacks[trigger_id] = trigger_info
            
            # Initialize pin state tracking
            pin_key = f"{module}:{pin}"
            if pin_key not in self._pin_states:
                current_state = await self.read_input(module, pin)
                self._pin_states[pin_key] = current_state
            
            self._log_operation("setup_trigger", True)
            logger.info(f"Setup trigger {trigger_type} for module {module}, pin {pin}")
            
            return trigger_id
            
        except Exception as e:
            self._log_operation("setup_trigger", False, str(e))
            raise BusinessRuleViolationException(
                "DIO_SETUP_TRIGGER_FAILED",
                f"Failed to setup trigger: {str(e)}",
                {"module": module, "pin": pin, "trigger_type": trigger_type}
            )
    
    async def remove_trigger(self, trigger_id: str) -> None:
        """Remove input trigger monitoring"""
        if trigger_id not in self._trigger_callbacks:
            raise BusinessRuleViolationException(
                "TRIGGER_NOT_FOUND",
                f"Trigger ID {trigger_id} not found",
                {"trigger_id": trigger_id}
            )
        
        try:
            trigger_info = self._trigger_callbacks.pop(trigger_id)
            self._log_operation("remove_trigger", True)
            logger.info(f"Removed trigger for module {trigger_info['module']}, pin {trigger_info['pin']}")
            
        except Exception as e:
            self._log_operation("remove_trigger", False, str(e))
            raise BusinessRuleViolationException(
                "DIO_REMOVE_TRIGGER_FAILED",
                f"Failed to remove trigger: {str(e)}",
                {"trigger_id": trigger_id}
            )
    
    async def start_monitoring(self) -> None:
        """Start input monitoring loop"""
        self._validate_connection("start_monitoring")
        
        if self._is_monitoring:
            logger.warning("DIO monitoring already active")
            return
        
        try:
            self._is_monitoring = True
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self._log_operation("start_monitoring", True)
            logger.info("DIO input monitoring started")
            
        except Exception as e:
            self._is_monitoring = False
            self._log_operation("start_monitoring", False, str(e))
            raise BusinessRuleViolationException(
                "DIO_START_MONITORING_FAILED",
                f"Failed to start monitoring: {str(e)}",
                {}
            )
    
    async def stop_monitoring(self) -> None:
        """Stop input monitoring loop"""
        if not self._is_monitoring:
            return
        
        try:
            self._is_monitoring = False
            
            if self._monitoring_task and not self._monitoring_task.done():
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            self._monitoring_task = None
            self._log_operation("stop_monitoring", True)
            logger.info("DIO input monitoring stopped")
            
        except Exception as e:
            self._log_operation("stop_monitoring", False, str(e))
            raise BusinessRuleViolationException(
                "DIO_STOP_MONITORING_FAILED",
                f"Failed to stop monitoring: {str(e)}",
                {}
            )
    
    async def is_monitoring_active(self) -> bool:
        """Check if input monitoring is active"""
        return self._is_monitoring
    
    async def _monitoring_loop(self) -> None:
        """Internal monitoring loop for trigger detection"""
        monitor_rate = self._hardware_device.get_capability("monitoring_rate", 100)
        sleep_interval = 1.0 / monitor_rate  # Convert Hz to seconds
        
        while self._is_monitoring:
            try:
                current_time = asyncio.get_event_loop().time()
                
                # Check all monitored pins
                for trigger_id, trigger_info in self._trigger_callbacks.items():
                    module = trigger_info["module"]
                    pin = trigger_info["pin"]
                    trigger_type = trigger_info["trigger_type"]
                    callback = trigger_info["callback"]
                    debounce_ms = trigger_info["debounce_ms"]
                    last_trigger_time = trigger_info["last_trigger_time"]
                    
                    # Check debounce
                    if (current_time - last_trigger_time) < (debounce_ms / 1000.0):
                        continue
                    
                    # Read current state
                    pin_key = f"{module}:{pin}"
                    current_state = await self.read_input(module, pin)
                    previous_state = self._pin_states.get(pin_key, False)
                    
                    # Detect trigger conditions
                    trigger_detected = False
                    
                    if trigger_type == InputTriggerType.BUTTON_PRESS:
                        # Rising edge (False -> True)
                        trigger_detected = not previous_state and current_state
                    elif trigger_type == InputTriggerType.DIGITAL_HIGH:
                        # High state
                        trigger_detected = current_state
                    elif trigger_type == InputTriggerType.DIGITAL_LOW:
                        # Low state
                        trigger_detected = not current_state
                    elif trigger_type == InputTriggerType.DIGITAL_CHANGE:
                        # Any change
                        trigger_detected = previous_state != current_state
                    
                    # Execute callback if triggered
                    if trigger_detected:
                        try:
                            callback(module, pin, current_state)
                            trigger_info["last_trigger_time"] = current_time
                            logger.debug(f"Trigger detected: {trigger_type} on module {module}, pin {pin}")
                        except Exception as e:
                            logger.error(f"Error in trigger callback: {e}")
                    
                    # Update pin state
                    self._pin_states[pin_key] = current_state
                
                await asyncio.sleep(sleep_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in DIO monitoring loop: {e}")
                await asyncio.sleep(sleep_interval)
    
    async def get_module_info(self, module: int) -> Dict[str, Any]:
        """Get information about a specific module"""
        self._validate_connection("get_module_info")
        
        try:
            # Get basic module information
            max_modules = self._hardware_device.get_capability("max_modules", 8)
            pins_per_module = self._hardware_device.get_capability("pins_per_module", 32)
            
            if module < 0 or module >= max_modules:
                raise BusinessRuleViolationException(
                    "INVALID_MODULE",
                    f"Module {module} is outside valid range [0, {max_modules-1}]",
                    {"module": module, "max_modules": max_modules}
                )
            
            return {
                "module_number": module,
                "pin_count": pins_per_module,
                "input_support": True,
                "output_support": True,
                "current_states": await self.read_all_inputs(module),
                "active_triggers": len([t for t in self._trigger_callbacks.values() 
                                     if t["module"] == module])
            }
            
        except Exception as e:
            self._log_operation("get_module_info", False, str(e))
            raise BusinessRuleViolationException(
                "DIO_GET_MODULE_INFO_FAILED",
                f"Failed to get module info: {str(e)}",
                {"module": module}
            )
    
    async def get_available_modules(self) -> List[int]:
        """Get list of available module numbers"""
        self._validate_connection("get_available_modules")
        
        try:
            max_modules = self._hardware_device.get_capability("max_modules", 8)
            # For Ajinextek, typically modules 0-7 are available
            return list(range(max_modules))
            
        except Exception as e:
            self._log_operation("get_available_modules", False, str(e))
            raise BusinessRuleViolationException(
                "DIO_GET_AVAILABLE_MODULES_FAILED",
                f"Failed to get available modules: {str(e)}",
                {}
            )