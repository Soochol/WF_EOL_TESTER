"""
Mock Power Analyzer Service

Mock implementation for testing and development without real hardware.
Simulates power measurement functionality of a power analyzer.
"""

# Standard library imports
import random
from typing import Dict, Optional

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.interfaces.hardware.power_analyzer import PowerAnalyzerService
from domain.exceptions import HardwareConnectionError, HardwareOperationError


class MockPowerAnalyzer(PowerAnalyzerService):
    """Mock power analyzer service for testing"""

    def __init__(
        self,
        host: str = "192.168.1.100",
        port: int = 10001,
        timeout: float = 5.0,
        element: int = 1,
        voltage_range: Optional[str] = None,
        current_range: Optional[str] = None,
        auto_range: bool = True,
        line_filter: Optional[str] = None,
        frequency_filter: Optional[str] = None,
    ):
        """
        Initialize Mock Power Analyzer

        Args:
            host: IP address or hostname (for simulation)
            port: TCP port number (for simulation)
            timeout: Connection timeout in seconds
            element: Measurement element/channel number
            voltage_range: Voltage range (ignored in mock)
            current_range: Current range (ignored in mock)
            auto_range: Enable automatic range adjustment (ignored in mock)
            line_filter: Line filter frequency (ignored in mock)
            frequency_filter: Frequency filter (ignored in mock)
        """
        # Initialize state
        self._is_connected = False

        # Connection parameters
        self._host = host
        self._port = port
        self._timeout = timeout
        self._element = element

        # Configuration parameters (stored but not actively used in mock)
        self._voltage_range = voltage_range
        self._current_range = current_range
        self._auto_range = auto_range
        self._line_filter = line_filter
        self._frequency_filter = frequency_filter

        # Mock operational parameters
        self._connection_delay = 0.2
        self._response_delay = 0.05

        # Simulated measurement values with realistic ranges
        self._base_voltage = 24.0  # Base voltage in volts
        self._base_current = 2.5  # Base current in amperes
        self._voltage_noise = 0.02  # Voltage measurement noise (±20mV)
        self._current_noise = 0.005  # Current measurement noise (±5mA)

        logger.info(
            f"MockPowerAnalyzer initialized (Element {self._element}, {self._host}:{self._port}, "
            f"Auto-range: {self._auto_range})"
        )

    async def connect(self) -> None:
        """
        Connect to power analyzer hardware (simulation)

        Raises:
            HardwareConnectionError: If connection fails
        """
        logger.info(f"Connecting to mock Power Analyzer at {self._host}:{self._port}...")

        try:
            # Simulate connection delay
            await asyncio.sleep(self._connection_delay)

            self._is_connected = True
            logger.info(
                f"Mock Power Analyzer connected successfully (Element {self._element})"
            )

        except Exception as e:
            logger.error(f"Failed to connect to mock Power Analyzer: {e}")
            raise HardwareConnectionError("mock_power_analyzer", str(e)) from e

    async def disconnect(self) -> None:
        """
        Disconnect from power analyzer hardware (simulation)

        Raises:
            HardwareOperationError: If disconnection fails
        """
        try:
            logger.info("Disconnecting mock Power Analyzer...")

            await asyncio.sleep(0.1)

            self._is_connected = False

            logger.info("Mock Power Analyzer disconnected")

        except Exception as e:
            logger.error(f"Error disconnecting mock Power Analyzer: {e}")
            raise HardwareOperationError("mock_power_analyzer", "disconnect", str(e)) from e

    async def is_connected(self) -> bool:
        """
        Check if power analyzer is connected

        Returns:
            True if connected, False otherwise
        """
        return self._is_connected

    async def get_measurements(self) -> Dict[str, float]:
        """
        Get all measurements at once (voltage, current, power) - simulation

        Simulates realistic power analyzer measurements with small variations
        to mimic real hardware behavior.

        Returns:
            Dictionary containing:
            - 'voltage': Simulated voltage in volts
            - 'current': Simulated current in amperes
            - 'power': Calculated power in watts (V × A)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If measurement fails
        """
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        try:
            # Simulate communication delay
            await asyncio.sleep(self._response_delay)

            # Simulate voltage with small random noise
            voltage = self._base_voltage + random.uniform(
                -self._voltage_noise, self._voltage_noise
            )

            # Simulate current with small random noise
            current = self._base_current + random.uniform(
                -self._current_noise, self._current_noise
            )

            # Ensure non-negative values
            voltage = max(0.0, voltage)
            current = max(0.0, current)

            # Calculate power (V × A)
            power = voltage * current

            logger.debug(
                f"Mock Power Analyzer measurements - "
                f"Voltage: {voltage:.4f}V, Current: {current:.4f}A, Power: {power:.4f}W"
            )

            return {
                "voltage": voltage,
                "current": current,
                "power": power,
            }

        except Exception as e:
            logger.error(f"Failed to get mock Power Analyzer measurements: {e}")
            raise HardwareOperationError(
                "mock_power_analyzer", "get_measurements", str(e)
            ) from e

    async def get_device_identity(self) -> str:
        """
        Get device identification string (mock)

        Returns:
            Mock device identification string

        Raises:
            HardwareConnectionError: If not connected
        """
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        return f"MOCK,WT1800E,MOCK-{self._element:06d},1.00"

    def set_base_values(self, voltage: float, current: float) -> None:
        """
        Set base measurement values for simulation

        This method allows test code to control the simulated measurements
        for predictable testing scenarios.

        Args:
            voltage: Base voltage in volts
            current: Base current in amperes
        """
        self._base_voltage = voltage
        self._base_current = current
        logger.info(f"Mock base values updated: {voltage}V, {current}A")

    def set_noise_levels(self, voltage_noise: float, current_noise: float) -> None:
        """
        Set noise levels for measurement simulation

        Args:
            voltage_noise: Voltage noise amplitude in volts
            current_noise: Current noise amplitude in amperes
        """
        self._voltage_noise = voltage_noise
        self._current_noise = current_noise
        logger.info(f"Mock noise levels updated: ±{voltage_noise}V, ±{current_noise}A")

    async def configure_input(
        self,
        voltage_range: Optional[str] = None,
        current_range: Optional[str] = None,
        auto_range: bool = True,
    ) -> None:
        """
        Configure voltage and current input ranges (mock - no-op)

        This method is provided for interface compatibility with WT1800E.
        In mock mode, it only logs the configuration request.

        Args:
            voltage_range: Voltage range (e.g., "300V")
            current_range: Current range (e.g., "5A")
            auto_range: Enable automatic range adjustment
        """
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        # Update internal configuration
        self._voltage_range = voltage_range
        self._current_range = current_range
        self._auto_range = auto_range

        if auto_range:
            logger.info("Mock Power Analyzer: auto-range enabled (simulated)")
        else:
            logger.info(
                f"Mock Power Analyzer: ranges set to {voltage_range or 'default'} / "
                f"{current_range or 'default'} (simulated)"
            )

    async def configure_filter(
        self,
        line_filter: Optional[str] = None,
        frequency_filter: Optional[str] = None,
    ) -> None:
        """
        Configure measurement filters (mock - no-op)

        This method is provided for interface compatibility with WT1800E.
        In mock mode, it only logs the configuration request.

        Args:
            line_filter: Line filter frequency (e.g., "10KHZ")
            frequency_filter: Frequency filter (e.g., "1HZ")
        """
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        # Update internal configuration
        self._line_filter = line_filter
        self._frequency_filter = frequency_filter

        if line_filter or frequency_filter:
            logger.info(
                f"Mock Power Analyzer: filters set to line={line_filter or 'default'}, "
                f"freq={frequency_filter or 'default'} (simulated)"
            )

    async def setup_integration(
        self,
        mode: str = "normal",
        timer: int = 3600,
    ) -> None:
        """
        Configure integration measurement (mock - simulated)

        This method is provided for interface compatibility with WT1800E.
        In mock mode, it simulates integration setup.

        Args:
            mode: Integration mode - "normal" or "continuous"
            timer: Integration timer in seconds
        """
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        # Simulate setup delay
        await asyncio.sleep(0.05)

        logger.info(
            f"Mock Power Analyzer: integration setup (mode={mode}, timer={timer}s) (simulated)"
        )

    async def start_integration(self) -> None:
        """Start integration measurement (mock - simulated)"""
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        await asyncio.sleep(0.02)
        logger.info("Mock Power Analyzer: integration started (simulated)")

    async def stop_integration(self) -> None:
        """Stop integration measurement (mock - simulated)"""
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        await asyncio.sleep(0.02)
        logger.info("Mock Power Analyzer: integration stopped (simulated)")

    async def reset_integration(self) -> None:
        """Reset integration measurement (mock - simulated)"""
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        await asyncio.sleep(0.02)
        logger.info("Mock Power Analyzer: integration reset (simulated)")

    async def get_integration_time(self) -> Dict[str, Optional[str]]:
        """
        Get integration elapsed time (mock - simulated)

        Returns:
            Dictionary with simulated start and end times
        """
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        import time
        await asyncio.sleep(self._response_delay)

        # Simulate time data
        current_time = time.strftime("%H:%M:%S")
        result = {
            'start': current_time,
            'end': None,  # Simulating ongoing integration
        }

        logger.debug(f"Mock Power Analyzer: integration time query (simulated): {result}")
        return result

    async def get_integration_data(self, element: Optional[int] = None) -> Dict[str, float]:
        """
        Get integration data (mock - simulated)

        Args:
            element: Measurement element (ignored in mock)

        Returns:
            Dictionary with simulated energy values
        """
        if not self._is_connected:
            raise HardwareConnectionError(
                "mock_power_analyzer",
                "Power Analyzer is not connected",
            )

        await asyncio.sleep(self._response_delay)

        # Simulate realistic integration values
        # Assume 1 hour at base power: P = 24V * 2.5A = 60W -> 60Wh
        active_energy_wh = 60.0 + random.uniform(-5.0, 5.0)
        apparent_energy_vah = 65.0 + random.uniform(-5.0, 5.0)
        reactive_energy_varh = 10.0 + random.uniform(-2.0, 2.0)

        logger.debug(
            f"Mock Power Analyzer: integration data (simulated) - "
            f"Active: {active_energy_wh:.4f}Wh, Apparent: {apparent_energy_vah:.4f}VAh, "
            f"Reactive: {reactive_energy_varh:.4f}varh"
        )

        return {
            "active_energy_wh": active_energy_wh,
            "apparent_energy_vah": apparent_energy_vah,
            "reactive_energy_varh": reactive_energy_varh,
        }
