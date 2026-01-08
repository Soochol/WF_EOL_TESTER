"""
Ajinextek Digital I/O Service

Real hardware implementation for Ajinextek Digital I/O.
Standalone version for EOL Tester package (Windows only).
"""

from typing import Any, Dict, List, Optional

from ...interfaces import DigitalIOService
from ...driver.ajinextek import (
    AXLWrapper,
)
from ...driver.ajinextek.exceptions import AXLError, AXLDIOError


class AjinextekDIO(DigitalIOService):
    """Ajinextek Digital I/O real hardware implementation."""

    def __init__(
        self,
        input_module_no: int = 0,
        output_module_no: int = 1,
        input_count: int = 32,
        output_count: int = 32,
    ):
        """
        Initialize Ajinextek Digital I/O.

        Args:
            input_module_no: DIO module number for inputs (default: 0)
            output_module_no: DIO module number for outputs (default: 1)
            input_count: Number of input channels (default: 32)
            output_count: Number of output channels (default: 32)
        """
        self._input_module_no = input_module_no
        self._output_module_no = output_module_no
        self._input_count = input_count
        self._output_count = output_count

        self._axl: Optional[AXLWrapper] = None
        self._is_connected = False

    async def connect(self) -> None:
        """Connect to Ajinextek DIO module."""
        try:
            self._axl = AXLWrapper.get_instance()
            self._axl.connect()

            # Check if DIO module exists
            if not self._axl.is_dio_module():
                raise AXLDIOError("No DIO module found")

            # Get actual input/output counts from respective modules
            actual_input_count = self._axl.get_input_count(self._input_module_no)
            actual_output_count = self._axl.get_output_count(self._output_module_no)

            print(f"DEBUG: Input Module {self._input_module_no} - Inputs: {actual_input_count}")
            print(f"DEBUG: Output Module {self._output_module_no} - Outputs: {actual_output_count}")

            # Scan all modules for debugging purposes
            try:
                module_count = self._axl.get_dio_module_count()
                print(f"DEBUG: Total DIO Modules detected: {module_count}")
                for i in range(module_count):
                    try:
                        in_cnt = self._axl.get_input_count(i)
                        out_cnt = self._axl.get_output_count(i)
                        print(f"DEBUG: Module {i} - Inputs: {in_cnt}, Outputs: {out_cnt}")
                    except Exception:
                        pass
            except Exception as e:
                print(f"DEBUG: Failed to scan modules: {e}")

            if actual_input_count != self._input_count:
                self._input_count = actual_input_count

            if actual_output_count != self._output_count:
                self._output_count = actual_output_count

            self._is_connected = True

        except AXLError as e:
            self._is_connected = False
            raise ConnectionError(f"Ajinextek DIO connection failed: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from DIO module."""
        try:
            if self._axl:
                self._axl.disconnect()
        except Exception:
            pass
        finally:
            self._is_connected = False

    async def is_connected(self) -> bool:
        """Check connection status."""
        if not self._axl:
            return False
        try:
            return self._is_connected and self._axl.is_opened()
        except Exception:
            return False

    async def read_input(self, channel: int) -> bool:
        """Read single input channel."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek DIO is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if channel < 0 or channel >= self._input_count:
            raise ValueError(f"Invalid input channel: {channel}")

        return self._axl.read_input_bit(self._input_module_no, channel)

    async def read_all_inputs(self) -> List[bool]:
        """Read all input channels."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek DIO is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        return self._axl.batch_read_inputs(self._input_module_no, 0, self._input_count)

    async def read_inputs(self, start: int, count: int) -> List[bool]:
        """Read range of input channels."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek DIO is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if start < 0 or start + count > self._input_count:
            raise ValueError(f"Invalid input range: {start} to {start + count}")

        return self._axl.batch_read_inputs(self._input_module_no, start, count)

    async def write_output(self, channel: int, value: bool) -> None:
        """Write single output channel."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek DIO is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if channel < 0 or channel >= self._output_count:
            raise ValueError(f"Invalid output channel: {channel}")

        self._axl.write_output_bit(self._output_module_no, channel, value)

    async def write_outputs(self, start: int, values: List[bool]) -> None:
        """Write multiple output channels."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek DIO is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if start < 0 or start + len(values) > self._output_count:
            raise ValueError(f"Invalid output range: {start} to {start + len(values)}")

        self._axl.batch_write_outputs(self._output_module_no, start, values)

    async def read_output(self, channel: int) -> bool:
        """Read current state of output channel."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek DIO is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if channel < 0 or channel >= self._output_count:
            raise ValueError(f"Invalid output channel: {channel}")

        return self._axl.read_output_bit(self._output_module_no, channel)

    async def read_all_outputs(self) -> List[bool]:
        """Read all output channel states."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek DIO is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        return self._axl.batch_read_outputs(self._output_module_no, 0, self._output_count)

    async def set_all_outputs(self, value: bool) -> None:
        """Set all outputs to the same value."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek DIO is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        values = [value] * self._output_count
        self._axl.batch_write_outputs(self._output_module_no, 0, values)

    async def get_status(self) -> Dict[str, Any]:
        """Get hardware status."""
        status = {
            "connected": await self.is_connected(),
            "input_module_no": self._input_module_no,
            "output_module_no": self._output_module_no,
            "input_count": self._input_count,
            "output_count": self._output_count,
            "hardware_type": "Ajinextek DIO",
        }

        if await self.is_connected():
            try:
                status["inputs"] = await self.read_all_inputs()
                status["outputs"] = await self.read_all_outputs()
            except Exception as e:
                status["last_error"] = str(e)

        return status

    async def get_input_count(self) -> int:
        """Get number of input channels."""
        return self._input_count

    async def get_output_count(self) -> int:
        """Get number of output channels."""
        return self._output_count

    async def reset_all_outputs(self) -> bool:
        """Reset all outputs to LOW."""
        try:
            await self.set_all_outputs(False)
            return True
        except Exception:
            return False
