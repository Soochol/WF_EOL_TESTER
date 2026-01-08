"""
Hardware Factory

Factory for creating hardware service instances based on configuration.
Supports both mock (development/testing) and real (production) hardware.
"""

import platform
from typing import Any, Dict

from ..interfaces import (
    LoadCellService,
    MCUService,
    PowerService,
    RobotService,
    DigitalIOService,
)
from .mock import (
    MockLoadCell,
    MockMCU,
    MockPower,
    MockRobot,
    MockDigitalIO,
)


# Hardware type constants
HARDWARE_TYPE_MOCK = "mock"
HARDWARE_TYPE_BS205 = "bs205"
HARDWARE_TYPE_LMA = "lma"
HARDWARE_TYPE_ODA = "oda"
HARDWARE_TYPE_AJINEXTEK = "ajinextek"


class HardwareFactory:
    """Factory for creating hardware service instances."""

    @staticmethod
    def create_loadcell(config: Dict[str, Any]) -> LoadCellService:
        """
        Create LoadCell service instance.

        Args:
            config: Hardware configuration dict with 'type' and 'connection' keys

        Returns:
            LoadCellService instance

        Config Examples:
            Mock: {"type": "mock"}
            BS205: {"type": "bs205", "connection": {"port": "COM1", "baudrate": 9600}}
        """
        hw_type = config.get("type", HARDWARE_TYPE_MOCK).lower()

        if hw_type == HARDWARE_TYPE_MOCK:
            return MockLoadCell()

        elif hw_type == HARDWARE_TYPE_BS205:
            from .real import BS205LoadCell

            conn = config.get("connection", {})
            return BS205LoadCell(
                port=conn.get("port", "COM1"),
                baudrate=conn.get("baudrate", 9600),
                timeout=conn.get("timeout", 1.0),
                bytesize=conn.get("bytesize", 8),
                stopbits=conn.get("stopbits", 1),
                parity=conn.get("parity"),
                indicator_id=conn.get("indicator_id", 1),
            )

        else:
            raise ValueError(f"Unknown loadcell type: {hw_type}")

    @staticmethod
    def create_mcu(config: Dict[str, Any]) -> MCUService:
        """
        Create MCU service instance.

        Args:
            config: Hardware configuration dict

        Returns:
            MCUService instance

        Config Examples:
            Mock: {"type": "mock"}
            LMA: {"type": "lma", "connection": {"port": "COM2", "baudrate": 115200}}
        """
        hw_type = config.get("type", HARDWARE_TYPE_MOCK).lower()

        if hw_type == HARDWARE_TYPE_MOCK:
            return MockMCU()

        elif hw_type == HARDWARE_TYPE_LMA:
            from .real import LMAMCU

            conn = config.get("connection", {})
            return LMAMCU(
                port=conn.get("port", "COM2"),
                baudrate=conn.get("baudrate", 115200),
                timeout=conn.get("timeout", 5.0),
                bytesize=conn.get("bytesize", 8),
                stopbits=conn.get("stopbits", 1),
                parity=conn.get("parity"),
            )

        else:
            raise ValueError(f"Unknown MCU type: {hw_type}")

    @staticmethod
    def create_power(config: Dict[str, Any]) -> PowerService:
        """
        Create Power service instance.

        Args:
            config: Hardware configuration dict

        Returns:
            PowerService instance

        Config Examples:
            Mock: {"type": "mock"}
            ODA: {"type": "oda", "connection": {"host": "192.168.1.10", "port": 5025}}
        """
        hw_type = config.get("type", HARDWARE_TYPE_MOCK).lower()

        if hw_type == HARDWARE_TYPE_MOCK:
            return MockPower()

        elif hw_type == HARDWARE_TYPE_ODA:
            from .real import OdaPower

            conn = config.get("connection", {})
            return OdaPower(
                host=conn.get("host", "192.168.1.10"),
                port=conn.get("port", 5025),
                timeout=conn.get("timeout", 2.0),
                channel=conn.get("channel", 1),
            )

        else:
            raise ValueError(f"Unknown power type: {hw_type}")

    @staticmethod
    def create_robot(config: Dict[str, Any]) -> RobotService:
        """
        Create Robot service instance.

        Args:
            config: Hardware configuration dict

        Returns:
            RobotService instance

        Config Examples:
            Mock: {"type": "mock"}
            Ajinextek: {"type": "ajinextek", "axis_count": 4}

        Note:
            Ajinextek robot is Windows-only. On non-Windows platforms,
            it will fall back to mock implementation.
        """
        hw_type = config.get("type", HARDWARE_TYPE_MOCK).lower()

        if hw_type == HARDWARE_TYPE_MOCK:
            return MockRobot()

        elif hw_type == HARDWARE_TYPE_AJINEXTEK:
            # Check platform - Ajinextek requires Windows
            if platform.system() != "Windows":
                import warnings
                warnings.warn(
                    "Ajinextek robot is only supported on Windows. "
                    "Falling back to mock implementation."
                )
                return MockRobot()

            from .real import AjinextekRobot

            return AjinextekRobot(
                axis_count=config.get("axis_count", 4),
                velocity=config.get("velocity", 100.0),
                acceleration=config.get("acceleration", 500.0),
                deceleration=config.get("deceleration", 500.0),
                motion_param_file=config.get("motion_param_file"),
            )

        else:
            raise ValueError(f"Unknown robot type: {hw_type}")

    @staticmethod
    def create_digital_io(config: Dict[str, Any]) -> DigitalIOService:
        """
        Create Digital I/O service instance.

        Args:
            config: Hardware configuration dict

        Returns:
            DigitalIOService instance

        Config Examples:
            Mock: {"type": "mock"}
            Ajinextek: {"type": "ajinextek", "input_module_no": 0, "output_module_no": 1}

        Note:
            Ajinextek DIO is Windows-only. On non-Windows platforms,
            it will fall back to mock implementation.
        """
        hw_type = config.get("type", HARDWARE_TYPE_MOCK).lower()

        if hw_type == HARDWARE_TYPE_MOCK:
            return MockDigitalIO()

        elif hw_type == HARDWARE_TYPE_AJINEXTEK:
            # Check platform - Ajinextek requires Windows
            if platform.system() != "Windows":
                import warnings
                warnings.warn(
                    "Ajinextek DIO is only supported on Windows. "
                    "Falling back to mock implementation."
                )
                return MockDigitalIO()

            from .real import AjinextekDIO

            return AjinextekDIO(
                input_module_no=config.get("input_module_no", 0),
                output_module_no=config.get("output_module_no", 1),
                input_count=config.get("input_count", 32),
                output_count=config.get("output_count", 32),
            )

        else:
            raise ValueError(f"Unknown digital_io type: {hw_type}")

    @classmethod
    def create_all_hardware(
        cls, hardware_config: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create all hardware services from configuration.

        Args:
            hardware_config: Configuration dictionary with keys for each hardware type

        Returns:
            Dictionary with hardware service instances

        Example Config:
            {
                "loadcell": {"type": "mock"},
                "mcu": {"type": "lma", "connection": {"port": "COM2"}},
                "power": {"type": "oda", "connection": {"host": "192.168.1.10"}},
                "robot": {"type": "ajinextek"},
                "digital_io": {"type": "ajinextek"}
            }
        """
        hardware = {}

        if "loadcell" in hardware_config:
            hardware["loadcell"] = cls.create_loadcell(hardware_config["loadcell"])

        if "mcu" in hardware_config:
            hardware["mcu"] = cls.create_mcu(hardware_config["mcu"])

        if "power" in hardware_config:
            hardware["power"] = cls.create_power(hardware_config["power"])

        if "robot" in hardware_config:
            hardware["robot"] = cls.create_robot(hardware_config["robot"])

        if "digital_io" in hardware_config:
            hardware["digital_io"] = cls.create_digital_io(hardware_config["digital_io"])

        return hardware

    @staticmethod
    def get_default_mock_config() -> Dict[str, Dict[str, Any]]:
        """Get default configuration for all mock hardware."""
        return {
            "loadcell": {"type": "mock"},
            "mcu": {"type": "mock"},
            "power": {"type": "mock"},
            "robot": {"type": "mock"},
            "digital_io": {"type": "mock"},
        }

    @staticmethod
    def get_default_real_config() -> Dict[str, Dict[str, Any]]:
        """
        Get default configuration for real hardware.

        Note: You should customize connection parameters for your setup.
        """
        return {
            "loadcell": {
                "type": "bs205",
                "connection": {
                    "port": "COM1",
                    "baudrate": 9600,
                    "timeout": 1.0,
                    "indicator_id": 1,
                },
            },
            "mcu": {
                "type": "lma",
                "connection": {
                    "port": "COM2",
                    "baudrate": 115200,
                    "timeout": 5.0,
                },
            },
            "power": {
                "type": "oda",
                "connection": {
                    "host": "192.168.1.10",
                    "port": 5025,
                    "timeout": 2.0,
                    "channel": 1,
                },
            },
            "robot": {
                "type": "ajinextek",
                "axis_count": 4,
                "velocity": 100.0,
                "acceleration": 500.0,
                "deceleration": 500.0,
            },
            "digital_io": {
                "type": "ajinextek",
                "input_module_no": 0,
                "output_module_no": 1,
                "input_count": 32,
                "output_count": 32,
            },
        }
