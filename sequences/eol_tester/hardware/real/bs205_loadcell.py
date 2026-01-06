"""
BS205 LoadCell Service

Real hardware implementation for BS205 LoadCell.
Standalone version for EOL Tester package.
"""

import asyncio
from typing import Any, Dict, Optional

from ...interfaces import LoadCellService
from ...driver.serial import SerialConnection, SerialManager
from ...driver.serial.exceptions import (
    SerialCommunicationError,
    SerialConnectionError,
    SerialTimeoutError,
)


# BS205 Protocol Commands
CMD_READ_WEIGHT = "R"
CMD_ZERO = "Z"
CMD_HOLD = "H"
CMD_HOLD_RELEASE = "L"

# Timing
ZERO_OPERATION_DELAY = 1.0  # seconds


class BS205LoadCell(LoadCellService):
    """BS205 LoadCell real hardware implementation."""

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0,
        bytesize: int = 8,
        stopbits: int = 1,
        parity: Optional[str] = None,
        indicator_id: int = 1,
    ):
        """
        Initialize BS205 LoadCell.

        Args:
            port: Serial port (e.g., "COM3")
            baudrate: Baud rate (default: 9600)
            timeout: Connection timeout in seconds
            bytesize: Data bits (default: 8)
            stopbits: Stop bits (default: 1)
            parity: Parity setting (default: None)
            indicator_id: Indicator device ID (default: 1)
        """
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._bytesize = bytesize
        self._stopbits = stopbits
        self._parity = parity
        self._indicator_id = indicator_id

        self._connection: Optional[SerialConnection] = None
        self._is_connected = False

        self._last_command_time = 0.0
        self._min_command_interval = 0.2
        self._command_lock = asyncio.Lock()

    async def connect(self) -> None:
        """Connect to BS205 LoadCell."""
        if self._connection or self._is_connected:
            await self.disconnect()
            await asyncio.sleep(0.1)

        try:
            self._connection = await SerialManager.create_connection(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout,
                bytesize=self._bytesize,
                stopbits=self._stopbits,
                parity=self._parity,
            )
            self._is_connected = True

        except (SerialCommunicationError, SerialConnectionError, SerialTimeoutError) as e:
            self._is_connected = False
            raise ConnectionError(f"Failed to connect to BS205 LoadCell: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from BS205 LoadCell."""
        try:
            if self._connection:
                await self._connection.disconnect()
        except Exception:
            pass
        finally:
            self._connection = None
            self._is_connected = False

    async def is_connected(self) -> bool:
        """Check connection status."""
        return self._is_connected and self._connection is not None

    async def read_force(self) -> float:
        """
        Read force measurement.

        Returns:
            Force value in kgf
        """
        if not await self.is_connected():
            raise RuntimeError("BS205 LoadCell is not connected")

        response = await self._send_bs205_command(CMD_READ_WEIGHT)

        if not response:
            raise RuntimeError("No response from BS205 LoadCell")

        weight_value = self._parse_bs205_weight(response)
        return weight_value

    async def read_peak_force(
        self, duration_ms: int = 1000, sampling_interval_ms: int = 200
    ) -> float:
        """
        Read peak force over a duration.

        Args:
            duration_ms: Sampling duration in milliseconds
            sampling_interval_ms: Interval between samples

        Returns:
            Peak force value in kgf
        """
        if not await self.is_connected():
            raise RuntimeError("BS205 LoadCell is not connected")

        min_interval = max(sampling_interval_ms, self._min_command_interval * 1000)
        max_samples = max(1, duration_ms // int(min_interval))

        samples = []
        start_time = asyncio.get_event_loop().time()
        target_end_time = start_time + (duration_ms / 1000.0)

        sample_count = 0
        while asyncio.get_event_loop().time() < target_end_time and sample_count < max_samples:
            try:
                force_value = await self.read_force()
                samples.append(force_value)
                sample_count += 1

                if sample_count < max_samples:
                    await asyncio.sleep(min_interval / 1000.0)
            except Exception:
                continue

        if not samples:
            raise RuntimeError("No valid force samples collected")

        return max(samples, key=abs)

    async def hold(self) -> bool:
        """Set hold mode."""
        if not await self.is_connected():
            raise RuntimeError("BS205 LoadCell is not connected")

        await self._send_bs205_command(CMD_HOLD)
        return True

    async def hold_release(self) -> bool:
        """Release hold mode."""
        if not await self.is_connected():
            raise RuntimeError("BS205 LoadCell is not connected")

        await self._send_bs205_command(CMD_HOLD_RELEASE)
        return True

    async def zero_calibration(self) -> None:
        """Perform zero calibration."""
        if not await self.is_connected():
            raise RuntimeError("BS205 LoadCell is not connected")

        await self._send_bs205_command(CMD_ZERO)
        await asyncio.sleep(ZERO_OPERATION_DELAY)

    async def get_status(self) -> Dict[str, Any]:
        """Get hardware status."""
        return {
            "connected": await self.is_connected(),
            "port": self._port,
            "baudrate": self._baudrate,
            "indicator_id": self._indicator_id,
            "hardware_type": "BS205",
        }

    async def _send_bs205_command(
        self, command: str, timeout: Optional[float] = None
    ) -> Optional[str]:
        """Send BS205 binary protocol command."""
        if not self._connection:
            raise RuntimeError("No connection available")

        async with self._command_lock:
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self._last_command_time

            if time_since_last < self._min_command_interval:
                await asyncio.sleep(self._min_command_interval - time_since_last)

            cmd_timeout = timeout if timeout is not None else 3.0

            # BS205 binary command: ID + Command
            id_byte = 0x30 + self._indicator_id
            cmd_byte = ord(command)
            command_bytes = bytes([id_byte, cmd_byte])

            await self._connection.write(command_bytes)
            self._last_command_time = asyncio.get_event_loop().time()

            await asyncio.sleep(0.15)

            # Hold, Hold Release, and Zero commands don't return responses
            if command in [CMD_HOLD, CMD_HOLD_RELEASE, CMD_ZERO]:
                return "OK"

            response_buffer = await self._connection.read(size=10, timeout=cmd_timeout)

            if not response_buffer:
                return None

            return self._parse_bs205_response(response_buffer)

    def _parse_bs205_response(self, response_bytes: bytes) -> str:
        """Parse BS205 binary response to ASCII string."""
        if len(response_bytes) < 10:
            return ""

        # Extract data between STX (0x02) and ETX (0x03)
        stx_pos = response_bytes.find(0x02)
        if stx_pos != -1:
            etx_pos = response_bytes.find(0x03, stx_pos)
            if etx_pos != -1:
                data_bytes = response_bytes[stx_pos + 1 : etx_pos]
            else:
                data_bytes = response_bytes[stx_pos + 1 :]
        else:
            data_bytes = response_bytes

        # Convert to ASCII
        ascii_data = ""
        for byte_val in data_bytes:
            if 0x20 <= byte_val <= 0x7E:
                ascii_data += "_" if byte_val == 0x20 else chr(byte_val)
            elif 0x30 <= byte_val <= 0x39:
                ascii_data += chr(byte_val)

        return ascii_data

    def _parse_bs205_weight(self, response: str) -> float:
        """Parse BS205 weight response."""
        import re

        if not response or len(response) < 3:
            raise ValueError(f"Invalid BS205 response: '{response}'")

        # Find sign position
        sign_pos = -1
        for i, char in enumerate(response):
            if char in ["+", "-"]:
                sign_pos = i
                break

        if sign_pos == -1:
            raise ValueError(f"Cannot find sign in BS205 response: '{response}'")

        sign = response[sign_pos]
        value_part = response[sign_pos + 1 :]

        # Clean value
        value_clean = value_part.replace("_", " ").strip()
        value_clean = re.sub(r"\s+", " ", value_clean)
        value_clean = value_clean.replace(" ", "")

        if value_clean.startswith("."):
            value_clean = "0" + value_clean

        try:
            weight_value = float(value_clean)
        except ValueError:
            numbers = re.findall(r"\d+\.?\d*", value_clean)
            if numbers:
                weight_value = float(numbers[0])
            else:
                raise ValueError(f"No valid number found in '{value_clean}'")

        if sign == "-":
            weight_value = -weight_value

        return weight_value
