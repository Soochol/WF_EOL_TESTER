"""
Pytest Configuration and Shared Fixtures

Provides reusable test fixtures for power analyzer testing.
"""

# Standard library imports
from typing import AsyncGenerator

# Third-party imports
import pytest
import pytest_asyncio

# Local application imports
from domain.value_objects.hardware_config import PowerAnalyzerConfig
from infrastructure.implementation.hardware.power_analyzer.mock import MockPowerAnalyzer
from infrastructure.implementation.hardware.power_analyzer.wt1800e import (
    WT1800EPowerAnalyzer,
)


@pytest.fixture
def default_power_analyzer_config() -> PowerAnalyzerConfig:
    """Fixture providing default PowerAnalyzerConfig for testing"""
    return PowerAnalyzerConfig(
        model="mock",
        host="192.168.1.100",
        port=10001,
        timeout=5.0,
        element=1,
        voltage_range=None,
        current_range=None,
        auto_range=True,
        line_filter=None,
        frequency_filter=None,
    )


@pytest.fixture
def wt1800e_config() -> PowerAnalyzerConfig:
    """Fixture providing WT1800E PowerAnalyzerConfig for testing"""
    return PowerAnalyzerConfig(
        model="wt1800e",
        host="192.168.1.100",
        port=10001,
        timeout=5.0,
        element=1,
        voltage_range="300V",
        current_range="5A",
        auto_range=False,
        line_filter="10KHZ",
        frequency_filter="1HZ",
    )


@pytest_asyncio.fixture
async def mock_power_analyzer(
    default_power_analyzer_config: PowerAnalyzerConfig,
) -> AsyncGenerator[MockPowerAnalyzer, None]:
    """Fixture providing connected MockPowerAnalyzer instance"""
    analyzer = MockPowerAnalyzer(
        host=default_power_analyzer_config.host,
        port=default_power_analyzer_config.port,
        timeout=default_power_analyzer_config.timeout,
        element=default_power_analyzer_config.element,
        voltage_range=default_power_analyzer_config.voltage_range,
        current_range=default_power_analyzer_config.current_range,
        auto_range=default_power_analyzer_config.auto_range,
        line_filter=default_power_analyzer_config.line_filter,
        frequency_filter=default_power_analyzer_config.frequency_filter,
    )

    # Connect before yielding
    await analyzer.connect()

    yield analyzer

    # Cleanup: disconnect after test
    await analyzer.disconnect()


@pytest.fixture
def mock_power_analyzer_disconnected(
    default_power_analyzer_config: PowerAnalyzerConfig,
) -> MockPowerAnalyzer:
    """Fixture providing disconnected MockPowerAnalyzer instance (for connection tests)"""
    return MockPowerAnalyzer(
        host=default_power_analyzer_config.host,
        port=default_power_analyzer_config.port,
        timeout=default_power_analyzer_config.timeout,
        element=default_power_analyzer_config.element,
    )
