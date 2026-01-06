"""
LMA MCU Service

Real hardware implementation for LMA MCU.
Standalone version for EOL Tester package.
"""

import asyncio
import struct
import time
from typing import Any, Dict, List, Optional

import serial

from ...interfaces import MCUService


# LMA MCU Constants
TEMP_SCALE_FACTOR = 10
DEFAULT_TIMEOUT = 5.0


class LMAMCU(MCUService):
    """LMA MCU real hardware implementation."""

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 5.0,
        bytesize: int = 8,
        stopbits: int = 1,
        parity: Optional[str] = None,
    ):
        """
        Initialize LMA MCU.

        Args:
            port: Serial port (e.g., "COM3")
            baudrate: Baud rate (default: 115200)
            timeout: Connection timeout in seconds
            bytesize: Data bits (default: 8)
            stopbits: Stop bits (default: 1)
            parity: Parity setting (default: None)
        """
        self.serial_conn: Optional[serial.Serial] = None
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._bytesize = bytesize
        self._stopbits = stopbits
        self._parity = parity

        self._is_connected = False
        self._current_temperature = 0.0
        self._target_temperature = 0.0
        self._current_test_mode = 1
        self._current_fan_speed = 0

        self._heating_timing_history: List[Dict[str, Any]] = []
        self._cooling_timing_history: List[Dict[str, Any]] = []
        self._current_operating_temp: Optional[float] = None
        self._current_standby_temp: Optional[float] = None

        self._packet_buffer: List[bytes] = []

    async def connect(self) -> None:
        """Connect to MCU hardware."""
        try:
            self.serial_conn = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                bytesize=self._bytesize,
                parity=serial.PARITY_NONE if self._parity is None else self._parity,
                stopbits=self._stopbits,
                timeout=self._timeout,
            )
            self._is_connected = True

        except Exception as e:
            self._is_connected = False
            raise ConnectionError(f"LMA MCU connection failed: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from MCU hardware."""
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
        except Exception:
            pass
        finally:
            self.serial_conn = None
            self._is_connected = False

    async def is_connected(self) -> bool:
        """Check connection status."""
        return bool(self._is_connected and self.serial_conn and self.serial_conn.is_open)

    def _ensure_connected(self) -> None:
        """Ensure MCU is connected."""
        if not self._is_connected or not self.serial_conn or not self.serial_conn.is_open:
            raise RuntimeError("LMA MCU not connected")

    def _send_packet_sync(
        self, packet_hex: str, description: str = "", timeout: Optional[float] = None
    ) -> Optional[bytes]:
        """Send packet and receive response (synchronous)."""
        self._ensure_connected()

        actual_timeout = timeout if timeout is not None else self._timeout
        self._packet_buffer.clear()

        packet_bytes = bytes.fromhex(packet_hex.replace(" ", ""))
        start_time = time.time()

        if self.serial_conn:
            self.serial_conn.write(packet_bytes)

        response_data = b""

        while time.time() - start_time < actual_timeout:
            if self.serial_conn and self.serial_conn.in_waiting > 0:
                new_data = self.serial_conn.read(self.serial_conn.in_waiting)
                response_data += new_data

                if response_data.endswith(b"\xfe\xfe") and len(response_data) >= 6:
                    valid_packet = self._extract_valid_packet(response_data)
                    if valid_packet:
                        return valid_packet

            time.sleep(0.001)

        return None

    def _extract_valid_packet(self, buffer: bytes) -> Optional[bytes]:
        """Extract valid packet from buffer."""
        if len(buffer) < 6:
            return None

        i = 0
        while i <= len(buffer) - 6:
            ffff_pos = buffer.find(b"\xff\xff", i)
            if ffff_pos == -1:
                break

            if ffff_pos + 3 >= len(buffer):
                break

            length = buffer[ffff_pos + 3]
            expected_end = ffff_pos + 4 + length + 2

            if expected_end <= len(buffer):
                if buffer[expected_end - 2 : expected_end] == b"\xfe\xfe":
                    return buffer[ffff_pos:expected_end]
                elif length == 0 and buffer[ffff_pos + 4 : ffff_pos + 6] == b"\xfe\xfe":
                    return buffer[ffff_pos : ffff_pos + 6]

            i = ffff_pos + 1

        return None

    async def _send_packet(
        self, packet_hex: str, description: str = "", timeout: Optional[float] = None
    ) -> Optional[bytes]:
        """Async wrapper for packet transmission."""
        return self._send_packet_sync(packet_hex, description, timeout)

    async def _wait_for_additional_response(
        self,
        timeout: float = 15.0,
        description: str = "",
        expected_cmd: Optional[int] = None,
    ) -> Optional[bytes]:
        """Wait for additional response."""
        self._ensure_connected()

        if self._packet_buffer:
            packet = self._packet_buffer.pop(0)
            if expected_cmd is None or (len(packet) >= 3 and packet[2] == expected_cmd):
                return packet

        start_time = time.time()
        response_data = b""

        while time.time() - start_time < timeout:
            if self.serial_conn and self.serial_conn.in_waiting > 0:
                new_data = self.serial_conn.read(self.serial_conn.in_waiting)
                response_data += new_data

                while response_data:
                    valid_packet = self._extract_valid_packet(response_data)
                    if not valid_packet:
                        break

                    packet_len = len(valid_packet)
                    response_data = response_data[packet_len:]

                    if expected_cmd is None or valid_packet[2] == expected_cmd:
                        return valid_packet

            await asyncio.sleep(0.01)

        return None

    async def wait_boot_complete(self) -> None:
        """Wait for MCU boot complete signal."""
        self._ensure_connected()

        boot_timeout = 60.0
        start_time = time.time()
        response_data = b""

        while time.time() - start_time < boot_timeout:
            if self.serial_conn and self.serial_conn.in_waiting > 0:
                new_data = self.serial_conn.read(self.serial_conn.in_waiting)
                response_data += new_data

                if response_data.endswith(b"\xfe\xfe") and len(response_data) >= 6:
                    valid_packet = self._extract_valid_packet(response_data)
                    if valid_packet and len(valid_packet) >= 6 and valid_packet[2] == 0x00:
                        return

                    response_data = b""

            await asyncio.sleep(0.1)

        raise RuntimeError("MCU boot complete signal timeout")

    async def get_temperature(self) -> float:
        """Get current temperature reading."""
        self._ensure_connected()

        packet = "FFFF0700FEFE"
        response = await self._send_packet(packet, "CMD_REQUEST_TEMP", timeout=self._timeout)

        if response and len(response) >= 14 and response[2] == 0x07:
            ir_temp_data = response[4:8]
            ir_temp_scaled = struct.unpack(">I", ir_temp_data)[0]
            ir_temp_celsius = ir_temp_scaled / 10.0
            self._current_temperature = ir_temp_celsius
            return ir_temp_celsius

        raise RuntimeError("Invalid temperature response or timeout")

    def get_cached_temperature(self) -> Optional[float]:
        """Get last cached temperature without sending command."""
        if self._current_temperature == 0.0:
            return None
        return self._current_temperature

    async def set_test_mode(self, mode: int) -> None:
        """Set test mode."""
        self._ensure_connected()

        packet = f"FFFF0104{mode:08X}FEFE"
        packet_bytes = bytes.fromhex(packet.replace(" ", ""))

        if self.serial_conn:
            self.serial_conn.write(packet_bytes)

        response = await self._wait_for_additional_response(
            timeout=self._timeout, expected_cmd=0x01
        )

        if not response or len(response) < 6 or response[2] != 0x01:
            raise RuntimeError("Invalid test mode response")

        self._current_test_mode = mode

    async def get_test_mode(self) -> int:
        """Get current test mode."""
        return self._current_test_mode

    async def set_operating_temperature(self, target_temp: float) -> None:
        """Set operating temperature."""
        self._ensure_connected()

        temp_scaled = int(target_temp * TEMP_SCALE_FACTOR)
        packet = f"FFFF0504{temp_scaled:08X}FEFE"
        packet_bytes = bytes.fromhex(packet.replace(" ", ""))

        if self.serial_conn:
            self.serial_conn.write(packet_bytes)

        response = await self._wait_for_additional_response(
            timeout=self._timeout, expected_cmd=0x05
        )

        if not response or len(response) < 6 or response[2] != 0x05:
            raise RuntimeError("Invalid operating temperature ACK response")

        temp_response = await self._wait_for_additional_response(
            timeout=10.0, expected_cmd=0x0B
        )

        if temp_response and len(temp_response) >= 6 and temp_response[2] == 0x0B:
            self._target_temperature = target_temp
        else:
            raise RuntimeError("Operating temperature reached signal not received")

    async def set_cooling_temperature(self, target_temp: float) -> None:
        """Set cooling temperature."""
        self._ensure_connected()

        temp_scaled = int(target_temp * TEMP_SCALE_FACTOR)
        packet = f"FFFF0604{temp_scaled:08X}FEFE"
        packet_bytes = bytes.fromhex(packet.replace(" ", ""))

        if self.serial_conn:
            self.serial_conn.write(packet_bytes)

        response = await self._wait_for_additional_response(
            timeout=self._timeout, expected_cmd=0x06
        )

        if not response or len(response) < 6 or response[2] != 0x06:
            raise RuntimeError("Invalid cooling temperature ACK response")

        cooling_response = await self._wait_for_additional_response(
            timeout=40.0, expected_cmd=0x0D
        )

        if cooling_response and len(cooling_response) >= 6 and cooling_response[2] == 0x0D:
            self._target_temperature = target_temp
        else:
            raise RuntimeError("Cooling temperature reached signal not received")

    async def set_upper_temperature(self, upper_temp: float) -> None:
        """Set upper temperature limit."""
        self._ensure_connected()

        temp_scaled = int(upper_temp * TEMP_SCALE_FACTOR)
        packet = f"FFFF0204{temp_scaled:08X}FEFE"
        packet_bytes = bytes.fromhex(packet.replace(" ", ""))

        if self.serial_conn:
            self.serial_conn.write(packet_bytes)

        response = await self._wait_for_additional_response(
            timeout=self._timeout, expected_cmd=0x02
        )

        if not response or len(response) < 6 or response[2] != 0x02:
            raise RuntimeError("Invalid upper temperature response")

    async def set_fan_speed(self, fan_level: int) -> None:
        """Set fan speed level."""
        self._ensure_connected()

        packet = f"FFFF0304{fan_level:08X}FEFE"
        packet_bytes = bytes.fromhex(packet.replace(" ", ""))

        if self.serial_conn:
            self.serial_conn.write(packet_bytes)

        response = await self._wait_for_additional_response(
            timeout=self._timeout, expected_cmd=0x03
        )

        if not response or len(response) < 6 or response[2] != 0x03:
            raise RuntimeError("Invalid fan speed response")

        self._current_fan_speed = fan_level

    async def get_fan_speed(self) -> int:
        """Get current fan speed."""
        return self._current_fan_speed

    async def start_standby_heating(
        self,
        operating_temp: float,
        standby_temp: float,
        hold_time_ms: int = 60000,
    ) -> None:
        """Start standby heating mode."""
        self._ensure_connected()

        self._current_operating_temp = operating_temp
        self._current_standby_temp = standby_temp

        op_temp_scaled = int(operating_temp * TEMP_SCALE_FACTOR)
        standby_temp_scaled = int(standby_temp * TEMP_SCALE_FACTOR)

        data = f"{op_temp_scaled:08X}{standby_temp_scaled:08X}{hold_time_ms:08X}"
        packet = f"FFFF040C{data}FEFE"
        packet_bytes = bytes.fromhex(packet.replace(" ", ""))

        start_time = time.perf_counter()

        if self.serial_conn:
            self.serial_conn.write(packet_bytes)

        response = await self._wait_for_additional_response(
            timeout=self._timeout, expected_cmd=0x04
        )

        if not response or len(response) < 6 or response[2] != 0x04:
            raise RuntimeError("Invalid standby heating ACK response")

        temp_response = await self._wait_for_additional_response(
            timeout=10.0, expected_cmd=0x0B
        )

        if temp_response and len(temp_response) >= 6 and temp_response[2] == 0x0B:
            total_time = (time.perf_counter() - start_time) * 1000
            self._heating_timing_history.append({
                "transition": f"{standby_temp}C -> {operating_temp}C",
                "total_duration_ms": total_time,
            })
        else:
            raise RuntimeError("Temperature reached signal not received")

    async def start_standby_cooling(self) -> None:
        """Start standby cooling mode."""
        self._ensure_connected()

        packet = "FFFF0800FEFE"
        packet_bytes = bytes.fromhex(packet.replace(" ", ""))

        start_time = time.perf_counter()

        if self.serial_conn:
            self.serial_conn.write(packet_bytes)

        response = await self._wait_for_additional_response(
            timeout=self._timeout, expected_cmd=0x08
        )

        if not response or len(response) < 6 or response[2] != 0x08:
            raise RuntimeError("Invalid standby cooling ACK response")

        cooling_response = await self._wait_for_additional_response(
            timeout=40.0, expected_cmd=0x0C
        )

        if cooling_response and len(cooling_response) >= 6 and cooling_response[2] == 0x0C:
            total_time = (time.perf_counter() - start_time) * 1000
            self._cooling_timing_history.append({
                "transition": f"{self._current_operating_temp}C -> {self._current_standby_temp}C",
                "total_duration_ms": total_time,
            })
        else:
            raise RuntimeError("Cooling complete signal not received")

    def get_all_timing_data(self) -> Dict[str, Any]:
        """Get all heating/cooling timing data."""
        return {
            "heating_transitions": self._heating_timing_history,
            "cooling_transitions": self._cooling_timing_history,
            "total_heating_count": len(self._heating_timing_history),
            "total_cooling_count": len(self._cooling_timing_history),
        }

    def clear_timing_history(self) -> None:
        """Clear timing history."""
        self._heating_timing_history = []
        self._cooling_timing_history = []
        self._current_operating_temp = None
        self._current_standby_temp = None

    async def get_status(self) -> Dict[str, Any]:
        """Get hardware status."""
        return {
            "connected": await self.is_connected(),
            "port": self._port,
            "baudrate": self._baudrate,
            "current_temperature": self._current_temperature,
            "target_temperature": self._target_temperature,
            "test_mode": self._current_test_mode,
            "fan_speed": self._current_fan_speed,
            "hardware_type": "LMA",
            "timing_data": self.get_all_timing_data(),
        }
