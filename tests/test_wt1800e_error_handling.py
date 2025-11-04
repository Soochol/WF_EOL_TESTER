"""
WT1800E Power Analyzer Error Handling Tests

Tests for WT1800E error checking, exception handling, and TCP communication.
"""

# Standard library imports
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

# Third-party imports
import pytest
import pytest_asyncio

# Local application imports
from domain.exceptions import HardwareConnectionError, HardwareOperationError
from driver.tcp.communication import TCPCommunication
from driver.tcp.exceptions import TCPConnectionError, TCPTimeoutError
from infrastructure.implementation.hardware.power_analyzer.wt1800e import (
    WT1800EPowerAnalyzer,
)


@pytest_asyncio.fixture
async def mock_tcp_comm() -> AsyncGenerator[MagicMock, None]:
    """Fixture providing mocked TCPCommunication"""
    tcp_mock = MagicMock(spec=TCPCommunication)

    # Configure async methods
    tcp_mock.connect = AsyncMock()
    tcp_mock.disconnect = AsyncMock(return_value=True)
    tcp_mock.query = AsyncMock(return_value="0,No error")
    tcp_mock.send_command = AsyncMock()
    tcp_mock.flush_buffer = AsyncMock()

    # Configure receive_response to return different values based on call order
    # This handles: *IDN?, error queue checks, etc.
    tcp_mock.receive_response = AsyncMock(side_effect=[
        "YOKOGAWA,WT1800E,12345678,1.00",  # *IDN? response
        "0,No error",  # Error check after *CLS
        "0,No error",  # Error check after configure_input
        "0,No error",  # Any additional error checks
        "0,No error",  # Fallback
    ])

    # Mock is_connected attribute
    tcp_mock.is_connected = True

    yield tcp_mock


@pytest_asyncio.fixture
async def wt1800e_with_mock_tcp(
    mock_tcp_comm: MagicMock,
) -> AsyncGenerator[WT1800EPowerAnalyzer, None]:
    """Fixture providing WT1800E with mocked TCP communication"""

    with patch(
        "infrastructure.implementation.hardware.power_analyzer.wt1800e.wt1800e_power_analyzer.TCPCommunication",
        return_value=mock_tcp_comm,
    ):
        analyzer = WT1800EPowerAnalyzer(
            host="192.168.1.100",
            port=10001,
            timeout=5.0,
            element=1,
        )

        # Manually set the TCP comm (since we're mocking)
        analyzer._tcp_comm = mock_tcp_comm  # type: ignore

        # Connect (using mocked TCP)
        await analyzer.connect()

        yield analyzer

        # Cleanup
        await analyzer.disconnect()


class TestWT1800EErrorChecking:
    """Test suite for WT1800E error queue checking mechanism"""

    @pytest.mark.asyncio
    async def test_check_errors_no_error(self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer):
        """Test _check_errors when no errors present"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock error queue response (no error)
        mock_tcp.query.return_value = "0,No error"

        # Should not raise exception
        await analyzer._check_errors()  # type: ignore

        # Should query error queue
        mock_tcp.query.assert_called()

    @pytest.mark.asyncio
    async def test_check_errors_with_error(self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer):
        """Test _check_errors when error is present"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock error queue response (error present)
        mock_tcp.query.return_value = "101,Invalid parameter"

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError) as exc_info:
            await analyzer._check_errors()  # type: ignore

        # Exception should contain error details
        assert "101" in str(exc_info.value)
        assert "Invalid parameter" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_check_errors_multiple_queries(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test _check_errors queries until queue is empty"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock multiple errors in queue
        mock_tcp.query.side_effect = [
            "102,Syntax error",
            "103,Command error",
            "0,No error",  # Queue empty
        ]

        # Should raise on first error
        with pytest.raises(HardwareOperationError) as exc_info:
            await analyzer._check_errors()  # type: ignore

        # Should contain first error
        assert "102" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_check_errors_connection_error(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test _check_errors when TCP communication fails"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock TCP query failure
        mock_tcp.query.side_effect = TCPTimeoutError(
            "Timeout during error check",
            host="192.168.1.100",
            port=10001,
        )

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError):
            await analyzer._check_errors()  # type: ignore


class TestWT1800EConnectionHandling:
    """Test suite for WT1800E connection error handling"""

    @pytest.mark.asyncio
    async def test_connect_tcp_failure(self):
        """Test connect when TCP connection fails"""

        with patch(
            "infrastructure.implementation.hardware.power_analyzer.wt1800e.wt1800e_power_analyzer.TCPCommunication"
        ) as mock_tcp_class:
            # Mock TCP connection failure
            mock_tcp = AsyncMock()
            mock_tcp.connect.side_effect = TCPConnectionError(
                "Connection refused",
                host="192.168.1.100",
                port=10001,
            )
            mock_tcp_class.return_value = mock_tcp

            analyzer = WT1800EPowerAnalyzer(
                host="192.168.1.100",
                port=10001,
                timeout=5.0,
                element=1,
            )

            # Should raise HardwareConnectionError
            with pytest.raises(HardwareConnectionError) as exc_info:
                await analyzer.connect()

            assert "wt1800e" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_disconnect_tcp_failure(self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer):
        """Test disconnect when TCP disconnection fails"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock disconnect failure
        mock_tcp.disconnect.side_effect = Exception("TCP close error")

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError):
            await analyzer.disconnect()

    @pytest.mark.asyncio
    async def test_operations_when_disconnected(self):
        """Test operations raise error when not connected"""
        analyzer = WT1800EPowerAnalyzer(
            host="192.168.1.100",
            port=10001,
            timeout=5.0,
            element=1,
        )

        # Do not connect

        # All operations should raise HardwareConnectionError
        with pytest.raises(HardwareConnectionError):
            await analyzer.get_measurements()

        with pytest.raises(HardwareConnectionError):
            await analyzer.configure_input()

        with pytest.raises(HardwareConnectionError):
            await analyzer.get_device_identity()


class TestWT1800EMeasurementErrors:
    """Test suite for WT1800E measurement error handling"""

    @pytest.mark.asyncio
    async def test_get_measurements_tcp_timeout(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test get_measurements when TCP query times out"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock timeout on measurement query
        mock_tcp.query.side_effect = TCPTimeoutError(
            "Measurement query timeout",
            host="192.168.1.100",
            port=10001,
        )

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError) as exc_info:
            await analyzer.get_measurements()

        assert "get_measurements" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_measurements_invalid_response(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test get_measurements with malformed response"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock invalid response (not enough values)
        mock_tcp.query.return_value = "24.0,2.5"  # Missing power value

        # Should raise HardwareOperationError (ValueError during parsing)
        with pytest.raises(HardwareOperationError):
            await analyzer.get_measurements()

    @pytest.mark.asyncio
    async def test_get_measurements_non_numeric_response(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test get_measurements with non-numeric values"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock non-numeric response
        mock_tcp.query.return_value = "ERROR,ERROR,ERROR"

        # Should raise HardwareOperationError (ValueError during float conversion)
        with pytest.raises(HardwareOperationError):
            await analyzer.get_measurements()


class TestWT1800EConfigurationErrors:
    """Test suite for WT1800E configuration error handling"""

    @pytest.mark.asyncio
    async def test_configure_input_tcp_failure(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test configure_input when TCP command fails"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock TCP send failure
        mock_tcp.send_command.side_effect = TCPTimeoutError(
            "Configuration command timeout",
            host="192.168.1.100",
            port=10001,
        )

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError):
            await analyzer.configure_input(voltage_range="300V")

    @pytest.mark.asyncio
    async def test_configure_input_device_error(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test configure_input when device reports error"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock successful command send
        mock_tcp.send_command.return_value = None

        # Mock error in error queue (device rejected configuration)
        mock_tcp.query.return_value = "201,Invalid range setting"

        # Should raise HardwareOperationError during error check
        with pytest.raises(HardwareOperationError) as exc_info:
            await analyzer.configure_input(voltage_range="999V")  # Invalid range

        assert "201" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_configure_filter_tcp_failure(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test configure_filter when TCP command fails"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock TCP send failure
        mock_tcp.send_command.side_effect = TCPTimeoutError(
            "Filter configuration timeout",
            host="192.168.1.100",
            port=10001,
        )

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError):
            await analyzer.configure_filter(line_filter="10KHZ")


class TestWT1800EIntegrationErrors:
    """Test suite for WT1800E integration measurement error handling"""

    @pytest.mark.asyncio
    async def test_setup_integration_tcp_failure(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test setup_integration when TCP command fails"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock TCP send failure
        mock_tcp.send_command.side_effect = TCPTimeoutError(
            "Integration setup timeout",
            host="192.168.1.100",
            port=10001,
        )

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError):
            await analyzer.setup_integration()

    @pytest.mark.asyncio
    async def test_start_integration_tcp_failure(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test start_integration when TCP command fails"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock TCP send failure
        mock_tcp.send_command.side_effect = TCPTimeoutError(
            "Integration start timeout",
            host="192.168.1.100",
            port=10001,
        )

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError):
            await analyzer.start_integration()

    @pytest.mark.asyncio
    async def test_get_integration_data_invalid_response(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test get_integration_data with malformed response"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock invalid response
        mock_tcp.query.return_value = "100.0,200.0"  # Missing reactive energy

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError):
            await analyzer.get_integration_data()

    @pytest.mark.asyncio
    async def test_get_integration_time_invalid_response(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test get_integration_time with malformed response"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock invalid response (not enough parts)
        mock_tcp.query.return_value = "10:30:00"  # Missing end time

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError):
            await analyzer.get_integration_time()


class TestWT1800ERecovery:
    """Test suite for WT1800E error recovery mechanisms"""

    @pytest.mark.asyncio
    async def test_measurement_retry_on_transient_error(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test that measurements can recover from transient errors"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # First call fails, second succeeds
        mock_tcp.query.side_effect = [
            TCPTimeoutError("Transient timeout", host="192.168.1.100", port=10001),
            "24.0,2.5,60.0",  # Successful measurement
        ]

        # First attempt should fail
        with pytest.raises(HardwareOperationError):
            await analyzer.get_measurements()

        # Second attempt should succeed (after reset)
        mock_tcp.query.side_effect = None
        mock_tcp.query.return_value = "24.0,2.5,60.0"

        measurements = await analyzer.get_measurements()
        assert measurements["voltage"] == 24.0

    @pytest.mark.asyncio
    async def test_connection_state_tracking(self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer):
        """Test that connection state is properly tracked"""
        analyzer = wt1800e_with_mock_tcp

        # Should be connected
        assert await analyzer.is_connected() is True

        # Disconnect
        await analyzer.disconnect()

        # Should not be connected
        assert await analyzer.is_connected() is False

        # Reconnect
        await analyzer.connect()

        # Should be connected again
        assert await analyzer.is_connected() is True


class TestWT1800EEdgeCases:
    """Test suite for WT1800E edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_get_device_identity_tcp_failure(
        self, wt1800e_with_mock_tcp: WT1800EPowerAnalyzer
    ):
        """Test get_device_identity when TCP query fails"""
        analyzer = wt1800e_with_mock_tcp
        mock_tcp = analyzer._tcp_comm  # type: ignore

        # Mock TCP query failure
        mock_tcp.query.side_effect = TCPTimeoutError(
            "Identity query timeout",
            host="192.168.1.100",
            port=10001,
        )

        # Should raise HardwareOperationError
        with pytest.raises(HardwareOperationError):
            await analyzer.get_device_identity()

    @pytest.mark.asyncio
    async def test_element_parameter_validation(self):
        """Test element parameter is properly used in queries"""
        with patch(
            "infrastructure.implementation.hardware.power_analyzer.wt1800e.wt1800e_power_analyzer.TCPCommunication"
        ) as mock_tcp_class:
            mock_tcp = AsyncMock()
            mock_tcp.connect = AsyncMock()
            mock_tcp.query = AsyncMock(return_value="24.0,2.5,60.0")
            mock_tcp.send_command = AsyncMock()
            mock_tcp.is_connected = True
            mock_tcp_class.return_value = mock_tcp

            # Create analyzer with element=2
            analyzer = WT1800EPowerAnalyzer(
                host="192.168.1.100",
                port=10001,
                timeout=5.0,
                element=2,  # Element 2
            )

            analyzer._tcp_comm = mock_tcp  # type: ignore
            await analyzer.connect()

            # Get measurements
            await analyzer.get_measurements()

            # Verify element 2 was used in query
            query_calls = [call for call in mock_tcp.query.call_args_list]
            assert any("2" in str(call) for call in query_calls)

            await analyzer.disconnect()
