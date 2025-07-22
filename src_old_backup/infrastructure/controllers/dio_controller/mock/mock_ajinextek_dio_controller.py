"""
Mock AJINEXTEK DIO Controller

This module provides a mock implementation of the AJINEXTEK DIO controller
for testing and development purposes. It simulates all digital I/O operations
without requiring actual hardware.
"""

from typing import Optional, Dict, Any

from loguru import logger

from ....domain.enums.hardware_status import HardwareStatus


class MockAjinextekDIOController:
    """Mock AJINEXTEK DIO controller for testing"""

    def __init__(self, irq_no: int = 7):
        self.controller_type = "dio"
        self.vendor = "ajinextek_mock"
        self.connection_info = f'Mock AXL DIO (IRQ: {irq_no})'
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        self.irq_no = irq_no
        self.module_count = 4  # Simulate 4 modules
        
        # Mock state - simulate digital I/O states
        # Each module has 32 input pins and 32 output pins
        self.input_states = {}
        self.output_states = {}
        
        # Initialize all pins to LOW (False)
        for module in range(self.module_count):
            self.input_states[module] = [False] * 32
            self.output_states[module] = [False] * 32

    def connect(self) -> None:
        """Connect to mock DIO controller"""
        logger.info(f"Mock DIO controller connected (IRQ: {self.irq_no})")
        self.status = HardwareStatus.CONNECTED

    def disconnect(self) -> None:
        """Disconnect mock DIO controller"""
        logger.info("Mock DIO controller disconnected")
        self.status = HardwareStatus.DISCONNECTED

    def set_output_high(self, module: int, pin: int) -> None:
        """Set digital output pin to HIGH"""
        self._check_module_pin(module, pin)
        
        self.output_states[module][pin] = True
        logger.debug(f"Mock DIO output {module}:{pin} set to HIGH")

    def set_output_low(self, module: int, pin: int) -> None:
        """Set digital output pin to LOW"""
        self._check_module_pin(module, pin)
        
        self.output_states[module][pin] = False
        logger.debug(f"Mock DIO output {module}:{pin} set to LOW")

    def set_output(self, module: int, pin: int, value: bool) -> None:
        """Set digital output pin to specified value"""
        if value:
            self.set_output_high(module, pin)
        else:
            self.set_output_low(module, pin)

    def read_input(self, module: int, pin: int) -> bool:
        """Read digital input pin value"""
        self._check_module_pin(module, pin)
        
        # Simulate some dynamic input behavior
        # For testing, we can make some inputs toggle periodically
        # Disabled to reduce log spam during normal operation
        # import time
        # if pin == 0:  # Make pin 0 toggle every 2 seconds
        #     self.input_states[module][pin] = (int(time.time()) % 4) < 2
        
        return self.input_states[module][pin]

    def read_output(self, module: int, pin: int) -> bool:
        """Read digital output pin value"""
        self._check_module_pin(module, pin)
        
        return self.output_states[module][pin]

    def set_output_port(self, module: int, port: int, value: int) -> None:
        """Set entire output port value"""
        from ..exceptions import AXLDIOError
        
        self._check_module(module)
        
        if port != 0:  # Only support port 0 for simplicity
            logger.error(f"Mock DIO invalid port: {port}")
            raise AXLDIOError(f"Invalid port number: {port} (only port 0 supported)", function_name="set_output_port")
        
        # Convert 32-bit value to individual pin states
        for pin in range(32):
            self.output_states[module][pin] = bool(value & (1 << pin))
        
        logger.debug(f"Mock DIO output port {module}:{port} set to 0x{value:08X}")

    def read_input_port(self, module: int, port: int) -> int:
        """Read entire input port value"""
        from ..exceptions import AXLDIOError
        
        self._check_module(module)
        
        if port != 0:  # Only support port 0 for simplicity
            logger.error(f"Mock DIO invalid port: {port}")
            raise AXLDIOError(f"Invalid port number: {port} (only port 0 supported)", function_name="read_input_port")
        
        # Convert individual pin states to 32-bit value
        value = 0
        for pin in range(32):
            input_value = self.read_input(module, pin)
            if input_value:
                value |= (1 << pin)
        
        return value

    def get_module_info(self) -> Dict[str, Any]:
        """Get detailed information about connected DIO modules"""
        modules = {}
        
        for module in range(self.module_count):
            modules[f'module_{module}'] = {
                'type': 'Mock DIO Module',
                'input_pins': 32,
                'output_pins': 32,
                'status': 'connected' if self.status == HardwareStatus.CONNECTED else 'disconnected'
            }
        
        return {
            'modules': modules,
            'total_modules': self.module_count
        }

    def _check_module(self, module: int) -> None:
        """Check if module number is valid"""
        from ..exceptions import AXLDIOError, AXLDIOConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            logger.error("Mock DIO controller not initialized")
            raise AXLDIOConnectionError("Mock DIO controller not connected")
        
        if module < 0 or module >= self.module_count:
            logger.error(f"Invalid module number: {module} (valid: 0-{self.module_count-1})")
            raise AXLDIOError(f"Invalid module number: {module} (valid: 0-{self.module_count-1})", function_name="_check_module")

    def _check_module_pin(self, module: int, pin: int) -> None:
        """Check if module and pin numbers are valid"""
        from ..exceptions import AXLDIOError
        
        self._check_module(module)
        
        if pin < 0 or pin >= 32:
            logger.error(f"Invalid pin number: {pin} (valid: 0-31)")
            raise AXLDIOError(f"Invalid pin number: {pin} (valid: 0-31)", function_name="_check_module_pin")

    def is_alive(self) -> bool:
        """Check if mock DIO controller is alive"""
        return self.status == HardwareStatus.CONNECTED

    # Additional helper methods for testing
    def simulate_input_change(self, module: int, pin: int, value: bool) -> None:
        """Simulate input pin change for testing purposes"""
        self._check_module_pin(module, pin)
        
        self.input_states[module][pin] = value
        logger.debug(f"Mock DIO input {module}:{pin} simulated as {'HIGH' if value else 'LOW'}")

    def get_all_output_states(self) -> Dict[int, Dict[int, bool]]:
        """Get all output states for testing verification"""
        states = {}
        for module in range(self.module_count):
            states[module] = {}
            for pin in range(32):
                states[module][pin] = self.output_states[module][pin]
        return states

    def get_all_input_states(self) -> Dict[int, Dict[int, bool]]:
        """Get all input states for testing verification"""
        states = {}
        for module in range(self.module_count):
            states[module] = {}
            for pin in range(32):
                states[module][pin] = self.input_states[module][pin]
        return states
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> bool:
        """Context manager exit"""
        # Always disconnect regardless of exception
        try:
            self.disconnect()
        except Exception as e:
            logger.warning(f"Error during disconnect in context manager: {e}")
        # Return False to propagate any exceptions
        return False