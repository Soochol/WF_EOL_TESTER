"""
Hardware Control Manager

Orchestrates individual hardware controllers and provides unified
hardware management interface with Rich UI integration.
"""

import asyncio
from typing import List, Optional

from loguru import logger
from rich.console import Console

from application.services.configuration_service import ConfigurationService
from application.services.hardware_service_facade import HardwareServiceFacade

from ...rich_formatter import RichFormatter
from ..base.hardware_controller import HardwareController, simple_interactive_menu
from ..hardware.loadcell_controller import LoadCellController
from ..hardware.mcu_controller import MCUController
from ..hardware.power_controller import PowerController
from ..hardware.robot_controller import RobotController


class HardwareControlManager:
    """Manages individual hardware control with Rich UI

    Coordinates multiple hardware controllers and provides unified
    menu system for hardware selection and control.
    """

    def __init__(
        self,
        hardware_facade: HardwareServiceFacade,
        console: Optional[Console] = None,
        configuration_service: Optional[ConfigurationService] = None,
    ):
        self.console = console or Console()
        self.formatter = RichFormatter(self.console)
        self.configuration_service = configuration_service

        # Load hardware configuration for all hardware
        self.hardware_config = self._load_hardware_configurations()
        
        # Extract axis_id for backward compatibility
        self.axis_id = self.hardware_config.robot.axis_id if self.hardware_config else 0

        # Initialize hardware controllers with configuration
        self.controllers = {
            "Robot": RobotController(hardware_facade._robot, self.formatter, self.axis_id),
            "MCU": MCUController(hardware_facade._mcu, self.formatter, self.hardware_config.mcu if self.hardware_config else None),
            "LoadCell": LoadCellController(hardware_facade._loadcell, self.formatter, self.hardware_config.loadcell if self.hardware_config else None),
            "Power": PowerController(hardware_facade._power, self.formatter, self.hardware_config.power if self.hardware_config else None),
        }

        logger.info(f"Initialized {len(self.controllers)} hardware controllers")
        
    def _load_hardware_configurations(self):
        """Load all hardware configurations from YAML file"""
        try:
            if self.configuration_service:
                # Get the current event loop or create a new one
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context but need to run sync
                        # This is a limitation - we'll use defaults and log a warning
                        logger.warning(
                            "Cannot load hardware config in running event loop, using defaults"
                        )
                        return None
                    else:
                        hw_config = loop.run_until_complete(
                            self.configuration_service.load_hardware_config()
                        )
                        logger.info("Successfully loaded hardware configurations from YAML")
                        return hw_config
                except RuntimeError:
                    # No event loop running, create one
                    hw_config = asyncio.run(self.configuration_service.load_hardware_config())
                    logger.info("Successfully loaded hardware configurations from YAML")
                    return hw_config
            else:
                logger.warning("No configuration service available, using defaults")
                return None
        except Exception as e:
            logger.error(f"Failed to load hardware configurations: {e}")
            logger.info("Using default hardware configurations")
            return None

    def _load_robot_axis_id(self) -> int:
        """Load robot axis_id from hardware configuration"""
        try:
            if self.configuration_service:
                # Get the current event loop or create a new one
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context but need to run sync
                        # This is a limitation - we'll use a default and log a warning
                        logger.warning(
                            "Cannot load hardware config in running event loop, using default axis_id=0"
                        )
                        return 0
                    else:
                        hw_config = loop.run_until_complete(
                            self.configuration_service.load_hardware_config()
                        )
                        return hw_config.robot.axis_id
                except RuntimeError:
                    # No event loop running, create one
                    hw_config = asyncio.run(self.configuration_service.load_hardware_config())
                    return hw_config.robot.axis_id
            else:
                logger.warning("No configuration service available, using default axis_id=0")
                return 0
        except Exception as e:
            logger.error(f"Failed to load robot axis_id from configuration: {e}")
            logger.info("Using default axis_id=0")
            return 0

    async def show_hardware_menu(self) -> Optional[str]:
        """Display hardware selection menu"""
        menu_options = {
            "1": "Robot Control",
            "2": "MCU Control",
            "3": "LoadCell Control",
            "4": "Power Control",
            "5": "All Hardware Status",
            "b": "Back to Main Menu",
        }

        return simple_interactive_menu(
            self.console, menu_options, "Hardware Control Center", "Select hardware to control"
        )

    async def execute_hardware_control(self, selection: str) -> None:
        """Execute hardware control based on selection"""
        if selection == "b":
            return

        if selection == "5":
            await self._show_all_hardware_status()
            return

        # Map selection to controller
        controller_map = {"1": "Robot", "2": "MCU", "3": "LoadCell", "4": "Power"}

        controller_name = controller_map.get(selection)
        if not controller_name:
            self.formatter.print_message("Invalid selection", message_type="warning")
            return

        controller = self.controllers[controller_name]
        await self._run_hardware_controller(controller)

    async def _run_hardware_controller(self, controller: HardwareController) -> None:
        """Run hardware controller loop"""
        self.formatter.print_header(
            getattr(controller, "name", "Hardware"),
            f"Individual control for {getattr(controller, 'name', 'Hardware').split()[0]} hardware",
        )

        while True:
            try:
                selection = await controller.show_control_menu()
                if not selection or selection == "b":
                    break

                await controller.execute_command(selection)
                # All operations return to menu immediately - no pauses

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                self.formatter.print_message(
                    f"Hardware control error: {str(e)}", message_type="error"
                )
                logger.error(f"Hardware control error: {e}")

    async def _show_all_hardware_status(self) -> None:
        """Show status of all hardware components"""
        self.formatter.print_header("All Hardware Status", "Overview of all hardware components")

        for name, controller in self.controllers.items():
            try:
                await controller.show_status()
                self.formatter.console.print("")  # Add spacing
            except Exception as e:
                self.formatter.print_message(
                    f"Failed to get {name} status: {str(e)}", message_type="error"
                )

    def get_controller(self, name: str) -> Optional[HardwareController]:
        """Get specific hardware controller by name"""
        return self.controllers.get(name)

    def list_controllers(self) -> List[str]:
        """Get list of available controller names"""
        return list(self.controllers.keys())
