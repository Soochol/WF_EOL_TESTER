"""
Hardware Services Factory

Factory for creating hardware service instances using dependency-injector.
Manages robot, power, MCU, loadcell, and digital I/O services creation.
Uses Abstract Factory pattern to select appropriate hardware implementations.
"""

# Third-party imports
from dependency_injector import containers, providers

# Local application imports
from infrastructure.implementation.hardware.digital_io.ajinextek.ajinextek_dio import (
    AjinextekDIO,
)
from infrastructure.implementation.hardware.digital_io.mock.mock_dio import MockDIO
from infrastructure.implementation.hardware.loadcell.bs205.bs205_loadcell import (
    BS205LoadCell,
)
from infrastructure.implementation.hardware.loadcell.mock.mock_loadcell import (
    MockLoadCell,
)
from infrastructure.implementation.hardware.mcu.lma.lma_mcu import LMAMCU
from infrastructure.implementation.hardware.mcu.mock.mock_mcu import MockMCU
from infrastructure.implementation.hardware.power.mock.mock_power import MockPower
from infrastructure.implementation.hardware.power.oda.oda_power import OdaPower
from infrastructure.implementation.hardware.power_analyzer.mock.mock_power_analyzer import (
    MockPowerAnalyzer,
)
from infrastructure.implementation.hardware.power_analyzer.wt1800e.wt1800e_power_analyzer import (
    WT1800EPowerAnalyzer,
)

# Hardware implementations - Real hardware
from infrastructure.implementation.hardware.robot.ajinextek.ajinextek_robot import (
    AjinextekRobot,
)

# Hardware implementations - Mock hardware
from infrastructure.implementation.hardware.robot.mock.mock_robot import MockRobot


class HardwareFactory(containers.DeclarativeContainer):
    """Factory for creating hardware services based on configuration"""

    # Configuration
    config = providers.Configuration()

    # Robot service - Mock or Real hardware based on configuration
    robot_service = providers.Selector(
        config.robot.model,
        mock=providers.Factory(
            MockRobot,
            axis_id=config.robot.axis_id,
            irq_no=config.robot.irq_no,
        ),
        ajinextek=providers.Factory(
            AjinextekRobot,
            axis_id=config.robot.axis_id,
            irq_no=config.robot.irq_no,
        ),
    )

    # Power service - Mock or Real hardware based on configuration
    power_service = providers.Selector(
        config.power.model,
        mock=providers.Factory(
            MockPower,
            host=config.power.host,
            port=config.power.port,
            timeout=config.power.timeout,
            channel=config.power.channel,
        ),
        oda=providers.Factory(
            OdaPower,
            host=config.power.host,
            port=config.power.port,
            timeout=config.power.timeout,
            channel=config.power.channel,
        ),
    )

    # Power Analyzer service - Mock or Real hardware based on configuration
    power_analyzer_service = providers.Selector(
        config.power_analyzer.model,
        mock=providers.Factory(
            MockPowerAnalyzer,
            interface_type=config.power_analyzer.interface_type,
            host=config.power_analyzer.host,
            port=config.power_analyzer.port,
            usb_vendor_id=config.power_analyzer.usb_vendor_id,
            usb_model_code=config.power_analyzer.usb_model_code,
            usb_serial_number=config.power_analyzer.usb_serial_number,
            gpib_board=config.power_analyzer.gpib_board,
            gpib_address=config.power_analyzer.gpib_address,
            timeout=config.power_analyzer.timeout,
            element=config.power_analyzer.element,
            voltage_range=config.power_analyzer.voltage_range,
            current_range=config.power_analyzer.current_range,
            auto_range=config.power_analyzer.auto_range,
            line_filter=config.power_analyzer.line_filter,
            frequency_filter=config.power_analyzer.frequency_filter,
        ),
        wt1800e=providers.Factory(
            WT1800EPowerAnalyzer,
            interface_type=config.power_analyzer.interface_type,
            host=config.power_analyzer.host,
            port=config.power_analyzer.port,
            usb_vendor_id=config.power_analyzer.usb_vendor_id,
            usb_model_code=config.power_analyzer.usb_model_code,
            usb_serial_number=config.power_analyzer.usb_serial_number,
            gpib_board=config.power_analyzer.gpib_board,
            gpib_address=config.power_analyzer.gpib_address,
            timeout=config.power_analyzer.timeout,
            element=config.power_analyzer.element,
            voltage_range=config.power_analyzer.voltage_range,
            current_range=config.power_analyzer.current_range,
            auto_range=config.power_analyzer.auto_range,
            line_filter=config.power_analyzer.line_filter,
            frequency_filter=config.power_analyzer.frequency_filter,
            # External current sensor configuration
            external_current_sensor_enabled=config.power_analyzer.external_current_sensor.enabled,
            external_current_sensor_voltage_range=config.power_analyzer.external_current_sensor.voltage_range,
            external_current_sensor_scaling_ratio=config.power_analyzer.external_current_sensor.scaling_ratio,
        ),
    )

    # MCU service - Mock or Real hardware based on configuration
    mcu_service = providers.Selector(
        config.mcu.model,
        mock=providers.Factory(
            MockMCU,
            port=config.mcu.port,
            baudrate=config.mcu.baudrate,
            timeout=config.mcu.timeout,
            bytesize=config.mcu.bytesize,
            stopbits=config.mcu.stopbits,
            parity=config.mcu.parity,
        ),
        lma=providers.Factory(
            LMAMCU,
            port=config.mcu.port,
            baudrate=config.mcu.baudrate,
            timeout=config.mcu.timeout,
        ),
        ajinextek=providers.Factory(
            LMAMCU,  # Ajinextek MCU uses LMA implementation
            port=config.mcu.port,
            baudrate=config.mcu.baudrate,
            timeout=config.mcu.timeout,
        ),
    )

    # LoadCell service - Mock or Real hardware based on configuration
    loadcell_service = providers.Selector(
        config.loadcell.model,
        mock=providers.Factory(
            MockLoadCell,
            port=config.loadcell.port,
            baudrate=config.loadcell.baudrate,
            timeout=config.loadcell.timeout,
            bytesize=config.loadcell.bytesize,
            stopbits=config.loadcell.stopbits,
            parity=config.loadcell.parity,
            indicator_id=config.loadcell.indicator_id,
        ),
        bs205=providers.Factory(
            BS205LoadCell,
            port=config.loadcell.port,
            baudrate=config.loadcell.baudrate,
            timeout=config.loadcell.timeout,
            bytesize=config.loadcell.bytesize,
            stopbits=config.loadcell.stopbits,
            parity=config.loadcell.parity,
            indicator_id=config.loadcell.indicator_id,
        ),
        ajinextek=providers.Factory(
            BS205LoadCell,  # Ajinextek loadcell uses BS205 implementation
            port=config.loadcell.port,
            baudrate=config.loadcell.baudrate,
            timeout=config.loadcell.timeout,
            bytesize=config.loadcell.bytesize,
            stopbits=config.loadcell.stopbits,
            parity=config.loadcell.parity,
            indicator_id=config.loadcell.indicator_id,
        ),
    )

    # Digital I/O service - Mock or Real hardware based on configuration
    digital_io_service = providers.Selector(
        config.digital_io.model,
        mock=providers.Factory(
            MockDIO,
            config=config.digital_io,
            irq_no=config.robot.irq_no,  # DIO uses same IRQ as robot
        ),
        ajinextek=providers.Factory(
            AjinextekDIO,
            irq_no=config.robot.irq_no,  # DIO uses same IRQ as robot
        ),
    )
