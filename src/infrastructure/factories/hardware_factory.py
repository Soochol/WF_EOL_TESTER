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
