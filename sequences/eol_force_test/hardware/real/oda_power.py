"""
ODA Power Supply Service

Real hardware implementation for ODA power supply.
Standalone version for EOL Tester package.
"""

import asyncio
from typing import Any, Dict, Optional

from ...interfaces import PowerService
from ...driver.tcp import TCPCommunication
from ...driver.tcp.exceptions import TCPError


class OdaPower(PowerService):
    """ODA Power Supply real hardware implementation."""

    def __init__(
        self,
        host: str,
        port: int = 5025,
        timeout: float = 2.0,
        channel: int = 1,
    ):
        """
        Initialize ODA Power Supply.

        Args:
            host: IP address or hostname
            port: TCP port number (default: 5025)
            timeout: Connection timeout in seconds
            channel: Power channel number (default: 1)
        """
        self._host = host
        self._port = port
        self._timeout = timeout
        self._channel = channel

        self._is_connected = False
        self._output_enabled = False
        self._device_identity: Optional[str] = None
        self._tcp_comm: Optional[TCPCommunication] = None

    async def connect(self) -> None:
        """Connect to power supply hardware."""
        try:
            self._tcp_comm = TCPCommunication(self._host, self._port, self._timeout)
            await self._tcp_comm.connect()

            # Test connection with identification command
            response = await self._send_command("*IDN?")

            if response and len(response.strip()) > 0:
                self._is_connected = True
                self._device_identity = response.strip()

                # Clear error status
                await self._send_command("*CLS")
                await asyncio.sleep(0.2)
            else:
                raise ConnectionError("Device identification failed")

        except TCPError as e:
            self._is_connected = False
            raise ConnectionError(f"ODA Power connection failed: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from power supply hardware."""
        try:
            if self._tcp_comm:
                await self._tcp_comm.disconnect()
        except Exception:
            pass
        finally:
            self._tcp_comm = None
            self._is_connected = False
            self._output_enabled = False

    async def is_connected(self) -> bool:
        """Check connection status."""
        return self._is_connected and self._tcp_comm is not None and self._tcp_comm.is_connected

    async def set_voltage(self, voltage: float) -> None:
        """Set output voltage."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        await self._send_command(f"VOLT {voltage:.2f}")

    async def get_voltage(self) -> float:
        """Get current output voltage."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        response = await self._send_command("MEAS:VOLT?")

        if response is None:
            raise RuntimeError("No voltage response")

        return float(response.strip())

    async def set_current(self, current: float) -> None:
        """Set output current."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        await self._send_command(f"CURR {current:.2f}")

    async def get_current(self) -> float:
        """Get current output current."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        response = await self._send_command("MEAS:CURR?")

        if response is None:
            raise RuntimeError("No current response")

        return float(response.strip())

    async def set_current_limit(self, current: float) -> None:
        """Set current limit."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        await self._send_command(f"CURR {current:.2f}")

    async def get_current_limit(self) -> float:
        """Get current limit setting."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        response = await self._send_command("CURR:UCL?")

        if response is None:
            raise RuntimeError("No current limit response")

        return float(response.strip())

    async def enable_output(self) -> None:
        """Enable power output."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        await self._send_command("OUTP ON")
        self._output_enabled = True

    async def disable_output(self) -> None:
        """Disable power output."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        await self._send_command("OUTP OFF")
        self._output_enabled = False

    async def is_output_enabled(self) -> bool:
        """Check if power output is enabled."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        return self._output_enabled

    async def get_device_identity(self) -> Optional[str]:
        """Get device identification string."""
        return self._device_identity

    async def get_all_measurements(self) -> Dict[str, float]:
        """Get all measurements at once using MEAS:ALL? command."""
        if not await self.is_connected():
            raise RuntimeError("ODA Power is not connected")

        try:
            response = await self._send_command("MEAS:ALL?")

            if response is None:
                raise RuntimeError("No response from MEAS:ALL?")

            values = response.strip().split(",")

            if len(values) != 2:
                # Fallback to individual measurements
                return await self._get_measurements_fallback()

            voltage = float(values[0])
            current = float(values[1])
            power = voltage * current

            return {"voltage": voltage, "current": current, "power": power}

        except (ValueError, IndexError):
            return await self._get_measurements_fallback()

    async def _get_measurements_fallback(self) -> Dict[str, float]:
        """Fallback method for individual measurements."""
        voltage = await self.get_voltage()
        current = await self.get_current()
        power = voltage * current

        return {"voltage": voltage, "current": current, "power": power}

    async def get_status(self) -> Dict[str, Any]:
        """Get hardware status."""
        status = {
            "connected": await self.is_connected(),
            "host": self._host,
            "port": self._port,
            "timeout": self._timeout,
            "channel": self._channel,
            "output_enabled": self._output_enabled,
            "hardware_type": "ODA",
            "device_identity": self._device_identity,
        }

        if await self.is_connected():
            try:
                status["current_voltage"] = await self.get_voltage()
                status["current_current"] = await self.get_current()
                status["last_error"] = None
            except Exception as e:
                status["current_voltage"] = None
                status["current_current"] = None
                status["last_error"] = str(e)

        return status

    async def _send_command(self, command: str) -> Optional[str]:
        """Send command to ODA power supply."""
        if not self._tcp_comm or not self._tcp_comm.is_connected:
            raise RuntimeError("TCP connection not available")

        command_with_terminator = f"{command}\n"

        if command.endswith("?"):
            response = await self._tcp_comm.query(command_with_terminator)
        else:
            await self._tcp_comm.send_command(command_with_terminator)
            response = None

        if response:
            response = response.strip()

        await asyncio.sleep(0.05)

        return response
