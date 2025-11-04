"""
Mock Power Analyzer Integration Tests

Tests for MockPowerAnalyzer hardware implementation.
"""

# Standard library imports
from typing import Dict

# Third-party imports
import pytest

# Local application imports
from domain.exceptions import HardwareConnectionError, HardwareOperationError
from infrastructure.implementation.hardware.power_analyzer.mock import MockPowerAnalyzer


class TestMockPowerAnalyzerConnection:
    """Test suite for Mock power analyzer connection management"""

    @pytest.mark.asyncio
    async def test_connect_success(self, mock_power_analyzer_disconnected: MockPowerAnalyzer):
        """Test successful connection"""
        analyzer = mock_power_analyzer_disconnected

        # Should not be connected initially
        assert await analyzer.is_connected() is False

        # Connect
        await analyzer.connect()

        # Should be connected now
        assert await analyzer.is_connected() is True

        # Cleanup
        await analyzer.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect_success(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test successful disconnection"""
        analyzer = mock_power_analyzer

        # Should be connected (fixture already connected)
        assert await analyzer.is_connected() is True

        # Disconnect
        await analyzer.disconnect()

        # Should not be connected
        assert await analyzer.is_connected() is False

    @pytest.mark.asyncio
    async def test_reconnection(self, mock_power_analyzer_disconnected: MockPowerAnalyzer):
        """Test multiple connect/disconnect cycles"""
        analyzer = mock_power_analyzer_disconnected

        for _ in range(3):
            # Connect
            await analyzer.connect()
            assert await analyzer.is_connected() is True

            # Disconnect
            await analyzer.disconnect()
            assert await analyzer.is_connected() is False

    @pytest.mark.asyncio
    async def test_double_connect(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test connecting when already connected"""
        analyzer = mock_power_analyzer

        # Already connected from fixture
        assert await analyzer.is_connected() is True

        # Connect again (should not raise error)
        await analyzer.connect()

        assert await analyzer.is_connected() is True


class TestMockPowerAnalyzerMeasurements:
    """Test suite for Mock power analyzer measurements"""

    @pytest.mark.asyncio
    async def test_get_measurements_structure(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test get_measurements returns correct data structure"""
        measurements = await mock_power_analyzer.get_measurements()

        # Should return dictionary with required keys
        assert isinstance(measurements, dict)
        assert "voltage" in measurements
        assert "current" in measurements
        assert "power" in measurements

        # All values should be floats
        assert isinstance(measurements["voltage"], float)
        assert isinstance(measurements["current"], float)
        assert isinstance(measurements["power"], float)

    @pytest.mark.asyncio
    async def test_get_measurements_values(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test get_measurements returns realistic values"""
        measurements = await mock_power_analyzer.get_measurements()

        voltage = measurements["voltage"]
        current = measurements["current"]
        power = measurements["power"]

        # Default base values: 24V, 2.5A
        # Values should be close to base values (±noise)
        assert 23.5 < voltage < 24.5  # ±0.5V margin
        assert 2.3 < current < 2.7  # ±0.2A margin

        # Power should be approximately V × A
        expected_power = voltage * current
        assert abs(power - expected_power) < 0.01  # Very tight tolerance for calculation

    @pytest.mark.asyncio
    async def test_get_measurements_non_negative(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test measurements are always non-negative"""
        for _ in range(10):
            measurements = await mock_power_analyzer.get_measurements()

            assert measurements["voltage"] >= 0.0
            assert measurements["current"] >= 0.0
            assert measurements["power"] >= 0.0

    @pytest.mark.asyncio
    async def test_measurements_when_disconnected(
        self, mock_power_analyzer_disconnected: MockPowerAnalyzer
    ):
        """Test get_measurements raises error when disconnected"""
        analyzer = mock_power_analyzer_disconnected

        with pytest.raises(HardwareConnectionError):
            await analyzer.get_measurements()

    @pytest.mark.asyncio
    async def test_set_base_values(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test set_base_values allows controlling simulated measurements"""
        analyzer = mock_power_analyzer

        # Set custom base values
        custom_voltage = 12.0
        custom_current = 3.0

        analyzer.set_base_values(voltage=custom_voltage, current=custom_current)

        # Get measurements
        measurements = await analyzer.get_measurements()

        # Should be close to custom values (±noise)
        assert 11.5 < measurements["voltage"] < 12.5
        assert 2.8 < measurements["current"] < 3.2

    @pytest.mark.asyncio
    async def test_set_noise_levels(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test set_noise_levels controls measurement variation"""
        analyzer = mock_power_analyzer

        # Set very low noise
        analyzer.set_noise_levels(voltage_noise=0.001, current_noise=0.0001)

        # Take multiple measurements
        measurements_list = []
        for _ in range(10):
            measurements = await analyzer.get_measurements()
            measurements_list.append(measurements)

        # Calculate variance
        voltages = [m["voltage"] for m in measurements_list]
        voltage_range = max(voltages) - min(voltages)

        # Variance should be very small with low noise
        assert voltage_range < 0.01  # Less than 10mV variation


class TestMockPowerAnalyzerDeviceIdentity:
    """Test suite for device identity queries"""

    @pytest.mark.asyncio
    async def test_get_device_identity_format(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test get_device_identity returns correct format"""
        identity = await mock_power_analyzer.get_device_identity()

        # Should return string
        assert isinstance(identity, str)

        # Should contain expected components (SCPI *IDN? format)
        assert "MOCK" in identity
        assert "WT1800E" in identity

        # Should have comma-separated format
        parts = identity.split(",")
        assert len(parts) == 4  # Manufacturer, Model, Serial, Firmware

    @pytest.mark.asyncio
    async def test_get_device_identity_disconnected(
        self, mock_power_analyzer_disconnected: MockPowerAnalyzer
    ):
        """Test get_device_identity raises error when disconnected"""
        analyzer = mock_power_analyzer_disconnected

        with pytest.raises(HardwareConnectionError):
            await analyzer.get_device_identity()


class TestMockPowerAnalyzerConfiguration:
    """Test suite for configuration methods"""

    @pytest.mark.asyncio
    async def test_configure_input_auto_range(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test configure_input with auto-range enabled"""
        analyzer = mock_power_analyzer

        # Should not raise error (no-op in mock)
        await analyzer.configure_input(auto_range=True)

    @pytest.mark.asyncio
    async def test_configure_input_manual_ranges(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test configure_input with manual ranges"""
        analyzer = mock_power_analyzer

        # Should not raise error (no-op in mock)
        await analyzer.configure_input(
            voltage_range="300V",
            current_range="5A",
            auto_range=False,
        )

    @pytest.mark.asyncio
    async def test_configure_filter(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test configure_filter method"""
        analyzer = mock_power_analyzer

        # Should not raise error (no-op in mock)
        await analyzer.configure_filter(
            line_filter="10KHZ",
            frequency_filter="1HZ",
        )

    @pytest.mark.asyncio
    async def test_configure_when_disconnected(
        self, mock_power_analyzer_disconnected: MockPowerAnalyzer
    ):
        """Test configuration raises error when disconnected"""
        analyzer = mock_power_analyzer_disconnected

        with pytest.raises(HardwareConnectionError):
            await analyzer.configure_input(auto_range=True)

        with pytest.raises(HardwareConnectionError):
            await analyzer.configure_filter(line_filter="10KHZ")


class TestMockPowerAnalyzerIntegration:
    """Test suite for integration measurement features"""

    @pytest.mark.asyncio
    async def test_setup_integration(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test integration setup"""
        analyzer = mock_power_analyzer

        # Should not raise error
        await analyzer.setup_integration(mode="normal", timer=3600)

    @pytest.mark.asyncio
    async def test_start_stop_integration(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test integration start/stop sequence"""
        analyzer = mock_power_analyzer

        # Setup
        await analyzer.setup_integration(mode="normal", timer=3600)

        # Start
        await analyzer.start_integration()

        # Stop
        await analyzer.stop_integration()

    @pytest.mark.asyncio
    async def test_reset_integration(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test integration reset"""
        analyzer = mock_power_analyzer

        # Should not raise error
        await analyzer.reset_integration()

    @pytest.mark.asyncio
    async def test_get_integration_time(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test get_integration_time returns correct structure"""
        analyzer = mock_power_analyzer

        time_data = await analyzer.get_integration_time()

        # Should return dictionary
        assert isinstance(time_data, dict)
        assert "start" in time_data
        assert "end" in time_data

        # Start should be a time string
        assert isinstance(time_data["start"], str)

        # End can be None (ongoing integration)
        assert time_data["end"] is None or isinstance(time_data["end"], str)

    @pytest.mark.asyncio
    async def test_get_integration_data_structure(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test get_integration_data returns correct structure"""
        analyzer = mock_power_analyzer

        integration_data = await analyzer.get_integration_data()

        # Should return dictionary with energy values
        assert isinstance(integration_data, dict)
        assert "active_energy_wh" in integration_data
        assert "apparent_energy_vah" in integration_data
        assert "reactive_energy_varh" in integration_data

        # All values should be floats
        assert isinstance(integration_data["active_energy_wh"], float)
        assert isinstance(integration_data["apparent_energy_vah"], float)
        assert isinstance(integration_data["reactive_energy_varh"], float)

    @pytest.mark.asyncio
    async def test_get_integration_data_values(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test get_integration_data returns realistic values"""
        analyzer = mock_power_analyzer

        integration_data = await analyzer.get_integration_data()

        active_energy = integration_data["active_energy_wh"]
        apparent_energy = integration_data["apparent_energy_vah"]
        reactive_energy = integration_data["reactive_energy_varh"]

        # Base simulation: ~60Wh active, ~65VAh apparent, ~10varh reactive
        assert 50.0 < active_energy < 70.0
        assert 55.0 < apparent_energy < 75.0
        assert 5.0 < reactive_energy < 15.0

    @pytest.mark.asyncio
    async def test_integration_when_disconnected(
        self, mock_power_analyzer_disconnected: MockPowerAnalyzer
    ):
        """Test integration methods raise error when disconnected"""
        analyzer = mock_power_analyzer_disconnected

        with pytest.raises(HardwareConnectionError):
            await analyzer.setup_integration()

        with pytest.raises(HardwareConnectionError):
            await analyzer.start_integration()

        with pytest.raises(HardwareConnectionError):
            await analyzer.stop_integration()

        with pytest.raises(HardwareConnectionError):
            await analyzer.reset_integration()

        with pytest.raises(HardwareConnectionError):
            await analyzer.get_integration_time()

        with pytest.raises(HardwareConnectionError):
            await analyzer.get_integration_data()

    @pytest.mark.asyncio
    async def test_full_integration_workflow(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test complete integration measurement workflow"""
        analyzer = mock_power_analyzer

        # 1. Setup integration
        await analyzer.setup_integration(mode="normal", timer=1800)

        # 2. Reset to clear any previous data
        await analyzer.reset_integration()

        # 3. Start measurement
        await analyzer.start_integration()

        # 4. Check time (should show start time)
        time_data = await analyzer.get_integration_time()
        assert time_data["start"] is not None

        # 5. Get integration data
        integration_data = await analyzer.get_integration_data()
        assert integration_data["active_energy_wh"] > 0

        # 6. Stop measurement
        await analyzer.stop_integration()


class TestMockPowerAnalyzerStressTest:
    """Stress tests for Mock power analyzer"""

    @pytest.mark.asyncio
    async def test_rapid_measurements(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test rapid consecutive measurements"""
        analyzer = mock_power_analyzer

        # Take 100 rapid measurements
        for _ in range(100):
            measurements = await analyzer.get_measurements()

            # Should always return valid data
            assert measurements["voltage"] > 0
            assert measurements["current"] > 0
            assert measurements["power"] > 0

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mock_power_analyzer: MockPowerAnalyzer):
        """Test multiple operations can be performed in sequence"""
        analyzer = mock_power_analyzer

        # Mix of operations
        await analyzer.configure_input(auto_range=True)
        measurements1 = await analyzer.get_measurements()

        await analyzer.configure_filter(line_filter="10KHZ")
        measurements2 = await analyzer.get_measurements()

        identity = await analyzer.get_device_identity()

        await analyzer.setup_integration()
        await analyzer.start_integration()
        integration_data = await analyzer.get_integration_data()
        await analyzer.stop_integration()

        # All should complete successfully
        assert measurements1 is not None
        assert measurements2 is not None
        assert identity is not None
        assert integration_data is not None
