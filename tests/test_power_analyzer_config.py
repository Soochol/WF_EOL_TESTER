"""
PowerAnalyzerConfig Validation Tests

Tests for PowerAnalyzerConfig value object validation and immutability.
"""

# Third-party imports
import pytest

# Local application imports
from domain.value_objects.hardware_config import PowerAnalyzerConfig, HardwareConfig


class TestPowerAnalyzerConfigValidation:
    """Test suite for PowerAnalyzerConfig validation logic"""

    def test_default_configuration(self):
        """Test default PowerAnalyzerConfig values"""
        config = PowerAnalyzerConfig()

        assert config.model == "mock"
        assert config.host == "192.168.1.100"
        assert config.port == 10001
        assert config.timeout == 5.0
        assert config.element == 1
        assert config.voltage_range is None
        assert config.current_range is None
        assert config.auto_range is True
        assert config.line_filter is None
        assert config.frequency_filter is None

    def test_wt1800e_configuration(self):
        """Test WT1800E-specific configuration"""
        config = PowerAnalyzerConfig(
            model="wt1800e",
            host="192.168.1.50",
            port=10002,
            timeout=10.0,
            element=2,
            voltage_range="300V",
            current_range="10A",
            auto_range=False,
            line_filter="10KHZ",
            frequency_filter="1HZ",
        )

        assert config.model == "wt1800e"
        assert config.host == "192.168.1.50"
        assert config.port == 10002
        assert config.timeout == 10.0
        assert config.element == 2
        assert config.voltage_range == "300V"
        assert config.current_range == "10A"
        assert config.auto_range is False
        assert config.line_filter == "10KHZ"
        assert config.frequency_filter == "1HZ"

    def test_immutability(self):
        """Test that PowerAnalyzerConfig is immutable (frozen dataclass)"""
        config = PowerAnalyzerConfig(model="wt1800e", host="192.168.1.100")

        with pytest.raises(AttributeError):
            config.model = "mock"  # type: ignore

        with pytest.raises(AttributeError):
            config.host = "192.168.1.200"  # type: ignore

    def test_is_mock_detection(self):
        """Test mock hardware detection"""
        mock_config = PowerAnalyzerConfig(model="mock")
        wt1800e_config = PowerAnalyzerConfig(model="wt1800e")

        assert mock_config.model == "mock"
        assert wt1800e_config.model == "wt1800e"

    def test_element_range(self):
        """Test measurement element number configuration"""
        # Element 1 (typical)
        config1 = PowerAnalyzerConfig(element=1)
        assert config1.element == 1

        # Element 2 (multi-channel measurements)
        config2 = PowerAnalyzerConfig(element=2)
        assert config2.element == 2

        # Element 4 (maximum typical channels)
        config4 = PowerAnalyzerConfig(element=4)
        assert config4.element == 4

    def test_voltage_range_options(self):
        """Test various voltage range configurations"""
        ranges = ["15V", "30V", "60V", "150V", "300V", "600V", "1000V"]

        for voltage_range in ranges:
            config = PowerAnalyzerConfig(voltage_range=voltage_range)
            assert config.voltage_range == voltage_range

    def test_current_range_options(self):
        """Test various current range configurations"""
        ranges = ["500MA", "1A", "2A", "5A", "10A", "20A", "30A"]

        for current_range in ranges:
            config = PowerAnalyzerConfig(current_range=current_range)
            assert config.current_range == current_range

    def test_auto_range_toggle(self):
        """Test auto-range enable/disable"""
        auto_enabled = PowerAnalyzerConfig(auto_range=True)
        auto_disabled = PowerAnalyzerConfig(auto_range=False)

        assert auto_enabled.auto_range is True
        assert auto_disabled.auto_range is False

    def test_filter_configurations(self):
        """Test line and frequency filter configurations"""
        config = PowerAnalyzerConfig(
            line_filter="10KHZ",
            frequency_filter="1HZ",
        )

        assert config.line_filter == "10KHZ"
        assert config.frequency_filter == "1HZ"

    def test_timeout_values(self):
        """Test different timeout configurations"""
        fast_config = PowerAnalyzerConfig(timeout=1.0)
        default_config = PowerAnalyzerConfig(timeout=5.0)
        slow_config = PowerAnalyzerConfig(timeout=30.0)

        assert fast_config.timeout == 1.0
        assert default_config.timeout == 5.0
        assert slow_config.timeout == 30.0

    def test_network_configuration(self):
        """Test various network host/port combinations"""
        configs = [
            ("192.168.1.100", 10001),
            ("192.168.1.50", 10002),
            ("10.0.0.100", 5025),
        ]

        for host, port in configs:
            config = PowerAnalyzerConfig(host=host, port=port)
            assert config.host == host
            assert config.port == port


class TestHardwareConfigIntegration:
    """Test PowerAnalyzerConfig integration with HardwareConfig"""

    def test_hardware_config_with_power_analyzer(self):
        """Test HardwareConfig includes PowerAnalyzerConfig"""
        hw_config = HardwareConfig()

        # PowerAnalyzerConfig should be present
        assert hasattr(hw_config, "power_analyzer")
        assert isinstance(hw_config.power_analyzer, PowerAnalyzerConfig)

    def test_mock_mode_detection_with_power_analyzer(self):
        """Test is_mock_mode() includes power analyzer check"""
        # All mock configuration
        all_mock = HardwareConfig(
            power_analyzer=PowerAnalyzerConfig(model="mock"),
        )

        # Mixed configuration
        mixed_config = HardwareConfig(
            power_analyzer=PowerAnalyzerConfig(model="wt1800e"),
        )

        # Verify is_mock_mode() logic
        assert all_mock.is_mock_mode() is True
        assert mixed_config.is_mock_mode() is False

    def test_hardware_config_serialization(self):
        """Test PowerAnalyzerConfig serialization in HardwareConfig"""
        config = HardwareConfig(
            power_analyzer=PowerAnalyzerConfig(
                model="wt1800e",
                host="192.168.1.100",
                voltage_range="300V",
                current_range="5A",
            )
        )

        # Convert to dict
        config_dict = config.to_dict()

        assert "power_analyzer" in config_dict
        assert config_dict["power_analyzer"]["model"] == "wt1800e"
        assert config_dict["power_analyzer"]["voltage_range"] == "300V"

        # Convert back from dict
        restored_config = HardwareConfig.from_dict(config_dict)

        assert restored_config.power_analyzer.model == "wt1800e"
        assert restored_config.power_analyzer.voltage_range == "300V"
        assert restored_config.power_analyzer.current_range == "5A"


class TestPowerAnalyzerConfigEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_optional_fields(self):
        """Test configuration with all optional fields as None"""
        config = PowerAnalyzerConfig(
            voltage_range=None,
            current_range=None,
            line_filter=None,
            frequency_filter=None,
        )

        assert config.voltage_range is None
        assert config.current_range is None
        assert config.line_filter is None
        assert config.frequency_filter is None

    def test_very_short_timeout(self):
        """Test very short timeout configuration"""
        config = PowerAnalyzerConfig(timeout=0.1)
        assert config.timeout == 0.1

    def test_very_long_timeout(self):
        """Test very long timeout configuration"""
        config = PowerAnalyzerConfig(timeout=120.0)
        assert config.timeout == 120.0

    def test_high_element_number(self):
        """Test high element number configuration"""
        config = PowerAnalyzerConfig(element=6)
        assert config.element == 6

    def test_equality_comparison(self):
        """Test equality comparison between identical configs"""
        config1 = PowerAnalyzerConfig(
            model="wt1800e",
            host="192.168.1.100",
            voltage_range="300V",
        )

        config2 = PowerAnalyzerConfig(
            model="wt1800e",
            host="192.168.1.100",
            voltage_range="300V",
        )

        config3 = PowerAnalyzerConfig(
            model="wt1800e",
            host="192.168.1.200",  # Different host
            voltage_range="300V",
        )

        assert config1 == config2
        assert config1 != config3

    def test_hash_consistency(self):
        """Test that identical configs have same hash (for use in sets/dicts)"""
        config1 = PowerAnalyzerConfig(model="wt1800e", host="192.168.1.100")
        config2 = PowerAnalyzerConfig(model="wt1800e", host="192.168.1.100")

        # Frozen dataclasses should be hashable
        assert hash(config1) == hash(config2)

        # Should work in sets
        config_set = {config1, config2}
        assert len(config_set) == 1  # Should deduplicate
