"""
BS205 LoadCell Service

Real hardware implementation for BS205 LoadCell.
Standalone version for EOL Tester package.
"""

import asyncio
from typing import Any, Dict, Optional
from loguru import logger


# Local application imports

__version__ = "1.1.0-brute-force"

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


class BS205Error(Exception):
    """Base BS205 LoadCell error"""
    pass


class BS205CommunicationError(BS205Error):
    """BS205 communication errors"""
    pass


class BS205DataError(BS205Error):
    """BS205 data processing errors"""
    pass

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

        # Hardcode mode to binary as per user request (skipping probe)
        self._detected_mode: Optional[str] = "binary"
        self._detected_id: Optional[int] = self._indicator_id
        self._probe_lock = asyncio.Lock()

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
            # Assert signals by default as some converters/devices require them
            # Disabled for BS205/RS485 as per user request to avoid interference
            # await self._connection.set_dtr(True)
            # await self._connection.set_rts(True)
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
        error_count = 0
        last_error = None
        while asyncio.get_event_loop().time() < target_end_time and sample_count < max_samples:
            try:
                force_value = await self.read_force()
                samples.append(force_value)
                sample_count += 1

                if sample_count < max_samples:
                    await asyncio.sleep(min_interval / 1000.0)
            except Exception as e:
                error_count += 1
                last_error = e
                logger.error(f"Force sample failed ({error_count}): {e}")
                continue

        if not samples:
            error_msg = f"No valid force samples collected (attempts: {sample_count + error_count}, errors: {error_count})"
            if last_error:
                error_msg += f", last error: {last_error}"
            raise RuntimeError(error_msg)

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
        """Send BS205 protocol command with auto-probing support."""
        if not self._connection:
            raise RuntimeError("No connection available")

        async with self._command_lock:
            # Auto-probe if mode not yet detected
            # if self._detected_mode is None:
            #     await self._probe_hardware()

            # If Stream Mode, we don't send commands for reading weight
            if self._detected_mode == "stream" and command == CMD_READ_WEIGHT:
                response_buffer = await self._read_response(timeout or 2.0)
                if response_buffer:
                    return self._parse_bs205_response(response_buffer)
                return None

            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self._last_command_time
            if time_since_last < self._min_command_interval:
                await asyncio.sleep(self._min_command_interval - time_since_last)

            cmd_timeout = timeout if timeout is not None else 3.0

            # Use detected mode or try both if still unknown
            modes_to_try = [self._detected_mode] if self._detected_mode else ["binary", "ascii"]
            
            for mode in modes_to_try:
                if mode == "binary" or mode is None:
                    target_id = self._detected_id if self._detected_id is not None else self._indicator_id
                    id_byte = 0x30 + target_id
                    binary_cmd = bytes([id_byte, ord(command), 0x0D, 0x0A])
                    logger.debug(f"Sending BS205 binary command: {binary_cmd.hex().upper()} (ID={target_id})")
                    await self._connection.write(binary_cmd)
                else:
                    ascii_cmd = (command + "\r").encode("ascii")
                    logger.debug(f"Sending BS205 ascii command: {ascii_cmd.hex().upper()}")
                    await self._connection.write(ascii_cmd)

                self._last_command_time = asyncio.get_event_loop().time()
                await asyncio.sleep(0.15)

                if command in [CMD_HOLD, CMD_HOLD_RELEASE, CMD_ZERO]:
                    return "OK"

                response_buffer = await self._read_response(cmd_timeout)
                if response_buffer:
                    if self._detected_mode is None:
                        self._detected_mode = mode
                        if mode == "binary":
                            self._detected_id = target_id
                        logger.info(f"Detected LoadCell mode: {mode} (ID={self._detected_id})")
                    
                    logger.debug(f"Received BS205 response: {response_buffer.hex().upper()}")
                    return self._parse_bs205_response(response_buffer)

            logger.warning(f"No response received for command {command}")
            return None

    async def _probe_hardware(self):
        """Deprecated: Probing removed as per user request (settings known)."""
        pass

    async def _read_response(self, timeout: float) -> bytes:
        """Read BS205 response with retry for incomplete reads.

        BS205 응답은 STX(1) + ID + Sign + Value(7) + ETX(1) = 10바이트 고정

        Args:
            timeout: Total timeout for reading

        Returns:
            Response bytes or empty bytes if failed
        """
        try:
            if not self._connection:
                raise RuntimeError("No connection available")

            # SDK Standard: Try to read up to 10 bytes (fixed frame size)
            response = await self._connection.read(size=10, timeout=timeout)

            # Greedy enhancement: check for any remaining data in short bursts
            # This helps if the protocol length varies or if there's trailing junk
            # Timeout here is expected (no more data), so catch and ignore
            try:
                while True:
                    additional = await self._connection.read(size=1024, timeout=0.1)
                    if not additional:
                        break
                    response += additional
            except Exception:
                # Timeout in greedy loop is normal - no more data available
                pass

            if response:
                logger.debug(f"Read {len(response)} bytes from LoadCell")
            return response

        except Exception as e:
            logger.error(f"Error reading LoadCell response: {e}")
            return b""

    def _parse_bs205_response(self, response_bytes: bytes) -> str:
        """Parse BS205 response to ASCII string (supports Binary STX/ETX and pure ASCII)."""
        if not response_bytes:
            return ""

        # Pattern 1: Binary Frame [STX (0x02) ... ETX (0x03)]
        stx_pos = response_bytes.find(0x02)
        if stx_pos != -1:
            etx_pos = response_bytes.find(0x03, stx_pos)
            data_bytes = response_bytes[stx_pos + 1 : etx_pos] if etx_pos != -1 else response_bytes[stx_pos + 1 :]
        else:
            # Pattern 2: Pure ASCII (Remove non-printable but keep digits/signs)
            data_bytes = response_bytes

        # Convert to ASCII and clean up
        ascii_data = ""
        for byte_val in response_bytes if stx_pos == -1 else data_bytes:
            # Keep printable ASCII, dots, signs, and digits
            if 0x20 <= byte_val <= 0x7E:
                # Map space to underscore for consistency with existing weight parser
                ascii_data += "_" if byte_val == 0x20 else chr(byte_val)
            elif byte_val == 0x3A: # ID 10
                ascii_data += "10"
            elif byte_val == 0x3F: # ID 15
                ascii_data += "15"
            elif byte_val in [0x0D, 0x0A]:
                ascii_data += " "

        return ascii_data.strip()

    def _parse_bs205_weight(self, response: str) -> float:
        """Parse BS205 weight response (SDK-standard logic)."""
        import re

        if not response or len(response) < 3:
            raise BS205DataError(f"Invalid BS205 response: '{response}'")

        # Find sign position (SDK-standard logic)
        sign_pos = -1
        for i, char in enumerate(response):
            if char in ["+", "-"]:
                sign_pos = i
                break

        if sign_pos == -1:
            raise BS205DataError(f"Cannot find sign (+/-) in BS205 response: '{response}'")

        sign = response[sign_pos]
        value_part = response[sign_pos + 1 :]

        # Value cleaning (SDK-standard logic)
        value_clean = value_part.replace("_", " ").strip()
        value_clean = re.sub(r"\s+", " ", value_clean)
        value_clean = value_clean.replace(" ", "")

        # Handle decimal point leading zeros
        if value_clean.startswith("."):
            value_clean = "0" + value_clean

        try:
            weight_value = float(value_clean)
        except ValueError:
            # Fallback for complex patterns
            numbers = re.findall(r"\d+\.?\d*", value_clean)
            if numbers:
                weight_value = float(numbers[0])
            else:
                raise BS205DataError(f"No valid number found in weight part: '{value_clean}'")

        if sign == "-":
            weight_value = -weight_value

        return weight_value
