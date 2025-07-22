"""
Input Service Implementation

Concrete implementation of InputService interface using InputAdapter.
"""

from typing import Dict, Any, Callable, List, Optional, Tuple
from loguru import logger

from ...application.interfaces.input_service import InputService, InputTriggerType
from ...domain.entities.hardware_device import HardwareDevice

# Import adapter interface
from ..adapters.interfaces.input_adapter import InputAdapter


class InputServiceImpl(InputService):
    """Input service implementation using InputAdapter"""
    
    def __init__(self, adapter: InputAdapter):
        """
        Initialize service with Input adapter
        
        Args:
            adapter: InputAdapter implementation
        """
        self._adapter = adapter
        logger.info(f"InputServiceImpl initialized with {adapter.vendor} adapter")
    
    async def connect(self) -> None:
        """Connect to input device via adapter"""
        try:
            await self._adapter.connect()
            logger.info(f"Input service connected via {self._adapter.vendor} adapter")
            
        except Exception as e:
            logger.error(f"Input service connection failed: {e}")
            raise  # Re-raise adapter exceptions as-is
    
    async def disconnect(self) -> None:
        """Disconnect from input device via adapter"""
        await self._adapter.disconnect()
        logger.info(f"Input service disconnected via {self._adapter.vendor} adapter")
    
    async def is_connected(self) -> bool:
        """Check if input device is connected via adapter"""
        return await self._adapter.is_connected()
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device entity from adapter"""
        return await self._adapter.get_hardware_device()
    
    # Input Reading
    async def read_input(self, module: int, pin: int) -> bool:
        """Read digital input state via adapter"""
        return await self._adapter.read_input(module, pin)
    
    async def read_all_inputs(self, module: int) -> Dict[int, bool]:
        """Read all input states for a module via adapter"""
        return await self._adapter.read_all_inputs(module)
    
    async def read_multiple_modules(self, modules: List[int]) -> Dict[int, Dict[int, bool]]:
        """Read input states for multiple modules via adapter"""
        result = {}
        for module in modules:
            try:
                result[module] = await self._adapter.read_all_inputs(module)
            except Exception as e:
                logger.error(f"Failed to read module {module}: {e}")
                result[module] = {}
        return result
    
    # Trigger Management
    async def setup_trigger(
        self, 
        module: int, 
        pin: int, 
        trigger_type: InputTriggerType,
        callback: Callable[[int, int, bool], None],
        debounce_ms: int = 50
    ) -> str:
        """Setup input trigger monitoring via adapter"""
        trigger_id = await self._adapter.setup_trigger(module, pin, trigger_type, callback, debounce_ms)
        logger.info(f"Setup trigger {trigger_type.value} for module {module}, pin {pin} via adapter")
        return trigger_id
    
    async def setup_multiple_triggers(
        self, 
        trigger_configs: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Setup multiple triggers at once via adapter"""
        results = {}
        for i, config in enumerate(trigger_configs):
            try:
                config_name = config.get('name', f'trigger_{i}')
                trigger_id = await self.setup_trigger(
                    module=config['module'],
                    pin=config['pin'],
                    trigger_type=config['trigger_type'],
                    callback=config['callback'],
                    debounce_ms=config.get('debounce_ms', 50)
                )
                results[config_name] = trigger_id
            except Exception as e:
                logger.error(f"Failed to setup trigger {config_name}: {e}")
                # Continue with other triggers
        
        logger.info(f"Setup {len(results)} triggers via adapter")
        return results
    
    async def remove_trigger(self, trigger_id: str) -> None:
        """Remove input trigger monitoring via adapter"""
        await self._adapter.remove_trigger(trigger_id)
        logger.info(f"Removed trigger {trigger_id} via adapter")
    
    async def remove_all_triggers(self) -> None:
        """Remove all active triggers via adapter"""
        active_triggers = await self.get_active_triggers()
        for trigger_id in active_triggers.keys():
            try:
                await self.remove_trigger(trigger_id)
            except Exception as e:
                logger.error(f"Failed to remove trigger {trigger_id}: {e}")
        
        logger.info("Removed all triggers via adapter")
    
    async def get_active_triggers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active triggers via adapter"""
        return self._adapter.get_active_triggers()
    
    # Monitoring Control
    async def start_monitoring(self) -> None:
        """Start input monitoring loop via adapter"""
        await self._adapter.start_monitoring()
        logger.info("Started input monitoring via adapter")
    
    async def stop_monitoring(self) -> None:
        """Stop input monitoring loop via adapter"""
        await self._adapter.stop_monitoring()
        logger.info("Stopped input monitoring via adapter")
    
    async def is_monitoring_active(self) -> bool:
        """Check if input monitoring is active via adapter"""
        return await self._adapter.is_monitoring_active()
    
    async def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get monitoring performance statistics via adapter"""
        active_triggers = await self.get_active_triggers()
        is_active = await self.is_monitoring_active()
        
        return {
            "monitoring_active": is_active,
            "active_trigger_count": len(active_triggers),
            "active_triggers": list(active_triggers.keys()),
            "adapter_vendor": self._adapter.vendor,
            "device_subtype": self._adapter.device_subtype
        }
    
    # Module and Device Information
    async def get_module_info(self, module: int) -> Dict[str, Any]:
        """Get information about a specific module via adapter"""
        return await self._adapter.get_module_info(module)
    
    async def get_available_modules(self) -> List[int]:
        """Get list of available module numbers via adapter"""
        return await self._adapter.get_available_modules()
    
    async def get_pin_configuration(self, module: int, pin: int) -> Dict[str, Any]:
        """Get configuration information for a specific pin"""
        # This is a business logic method that combines adapter data
        await self._adapter._validate_connection("get_pin_configuration")
        
        # Validate module/pin first
        if not await self.validate_module_pin(module, pin):
            from ...domain.exceptions.business_rule_exceptions import BusinessRuleViolationException
            raise BusinessRuleViolationException(
                "INVALID_MODULE_PIN",
                f"Invalid module {module} or pin {pin}",
                {"module": module, "pin": pin}
            )
        
        # Get module info and derive pin configuration
        module_info = await self.get_module_info(module)
        
        return {
            "module": module,
            "pin": pin,
            "supported_triggers": [trigger.value for trigger in InputTriggerType],
            "debounce_support": True,
            "current_state": await self.read_input(module, pin),
            "module_info": module_info
        }
    
    # Event History and Logging (simplified implementation)
    async def get_event_history(
        self, 
        module: Optional[int] = None, 
        pin: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get history of input events (basic implementation)"""
        # Note: This would require event storage in the adapter
        # For now, return empty list as this is a placeholder
        logger.info(f"Event history requested for module={module}, pin={pin}, limit={limit}")
        return []
    
    async def clear_event_history(self) -> None:
        """Clear stored event history (basic implementation)"""
        logger.info("Event history cleared")
        # Placeholder implementation
        pass
    
    async def enable_event_logging(self, enabled: bool) -> None:
        """Enable or disable event logging"""
        logger.info(f"Event logging {'enabled' if enabled else 'disabled'}")
        # Placeholder implementation
        pass
    
    # Button Press Utilities
    async def wait_for_button_press(
        self, 
        module: int, 
        pin: int,
        timeout_ms: int = 30000,
        debounce_ms: int = 50
    ) -> bool:
        """Wait for button press on specific pin"""
        import asyncio
        
        button_pressed = False
        press_event = asyncio.Event()
        
        def button_callback(cb_module: int, cb_pin: int, state: bool):
            nonlocal button_pressed
            if cb_module == module and cb_pin == pin and state:
                button_pressed = True
                press_event.set()
        
        # Setup trigger
        trigger_id = await self.setup_trigger(
            module, pin, InputTriggerType.BUTTON_PRESS, 
            button_callback, debounce_ms
        )
        
        try:
            # Start monitoring if not already active
            was_monitoring = await self.is_monitoring_active()
            if not was_monitoring:
                await self.start_monitoring()
            
            # Wait for button press or timeout
            try:
                await asyncio.wait_for(press_event.wait(), timeout=timeout_ms / 1000.0)
            except asyncio.TimeoutError:
                pass
            
            # Stop monitoring if we started it
            if not was_monitoring:
                await self.stop_monitoring()
            
            return button_pressed
            
        finally:
            # Clean up trigger
            try:
                await self.remove_trigger(trigger_id)
            except Exception as e:
                logger.error(f"Failed to remove trigger: {e}")
    
    async def wait_for_any_button_press(
        self, 
        module_pins: List[Tuple[int, int]],
        timeout_ms: int = 30000,
        debounce_ms: int = 50
    ) -> Optional[Tuple[int, int]]:
        """Wait for button press on any of the specified pins"""
        import asyncio
        
        pressed_pin = None
        press_event = asyncio.Event()
        
        def button_callback(cb_module: int, cb_pin: int, state: bool):
            nonlocal pressed_pin
            if state and (cb_module, cb_pin) in module_pins:
                pressed_pin = (cb_module, cb_pin)
                press_event.set()
        
        # Setup triggers for all pins
        trigger_ids = []
        for module, pin in module_pins:
            trigger_id = await self.setup_trigger(
                module, pin, InputTriggerType.BUTTON_PRESS,
                button_callback, debounce_ms
            )
            trigger_ids.append(trigger_id)
        
        try:
            # Start monitoring if not already active
            was_monitoring = await self.is_monitoring_active()
            if not was_monitoring:
                await self.start_monitoring()
            
            # Wait for any button press or timeout
            try:
                await asyncio.wait_for(press_event.wait(), timeout=timeout_ms / 1000.0)
            except asyncio.TimeoutError:
                pass
            
            # Stop monitoring if we started it
            if not was_monitoring:
                await self.stop_monitoring()
            
            return pressed_pin
            
        finally:
            # Clean up all triggers
            for trigger_id in trigger_ids:
                try:
                    await self.remove_trigger(trigger_id)
                except Exception as e:
                    logger.error(f"Failed to remove trigger: {e}")
    
    # Safety and Validation
    async def validate_module_pin(self, module: int, pin: int) -> bool:
        """Validate if module and pin combination is valid"""
        try:
            available_modules = await self.get_available_modules()
            if module not in available_modules:
                return False
            
            module_info = await self.get_module_info(module)
            pin_count = module_info.get('pin_count', 0)
            
            return 0 <= pin < pin_count
            
        except Exception as e:
            logger.error(f"Validation failed for module {module}, pin {pin}: {e}")
            return False
    
    async def validate_debounce_time(self, debounce_ms: int) -> bool:
        """Validate if debounce time is within acceptable range"""
        # Use the same validation as the adapter
        return 1 <= debounce_ms <= 1000  # 1ms to 1s
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get input device information and capabilities via adapter"""
        return await self._adapter.get_device_info()
    
    async def run_self_test(self) -> Dict[str, Any]:
        """Run input device self-test diagnostics via adapter"""
        result = await self._adapter.run_self_test()
        logger.info(f"Input device self-test completed via adapter: {result.get('test_passed', False)}")
        return result