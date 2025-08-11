"""
Hardware Control Manager

Orchestrates individual hardware controllers and provides unified
hardware management interface with Rich UI integration.
"""

import asyncio
from typing import List, Optional

from loguru import logger
from rich.console import Console

from src.application.services.configuration_service import ConfigurationService
from src.application.services.hardware_service_facade import HardwareServiceFacade

from ...rich_formatter import RichFormatter
from ..base.hardware_controller import HardwareController, simple_interactive_menu
from ..hardware.digital_io_controller import DigitalIOController
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
        logger.info("Loading hardware configurations for CLI controllers...")
        self.hardware_config = self._load_hardware_configurations()

        # Debug logging for configuration status
        if self.hardware_config:
            logger.info("Hardware configuration loaded successfully")
            logger.info(f"  - LoadCell port: {self.hardware_config.loadcell.port}")
            logger.info(f"  - MCU port: {self.hardware_config.mcu.port}")
            logger.info(
                f"  - Power host: {self.hardware_config.power.host}:{self.hardware_config.power.port}"
            )
            logger.info(f"  - Robot axis_id: {self.hardware_config.robot.axis_id}")
        else:
            logger.warning("Hardware configuration is None - CLI will use fallback defaults!")
            logger.warning("This may cause connection issues with hardware devices.")

        # Extract axis_id for backward compatibility
        self.axis_id = self.hardware_config.robot.axis_id if self.hardware_config else 0
        logger.info(f"Robot axis_id set to: {self.axis_id}")

        # Initialize hardware controllers with configuration
        logger.info("Initializing CLI controllers with hardware configuration...")
        self.controllers = {
            "Robot": RobotController(
                hardware_facade._robot,
                self.formatter,
                self.hardware_config.robot if self.hardware_config else None,
            ),
            "MCU": MCUController(
                hardware_facade._mcu,
                self.formatter,
                self.hardware_config.mcu if self.hardware_config else None,
            ),
            "LoadCell": LoadCellController(
                hardware_facade._loadcell,
                self.formatter,
                self.hardware_config.loadcell if self.hardware_config else None,
            ),
            "Power": PowerController(
                hardware_facade._power,
                self.formatter,
                self.hardware_config.power if self.hardware_config else None,
            ),
            "DigitalIO": DigitalIOController(
                hardware_facade._digital_io,
                self.formatter,
                self.hardware_config.digital_io if self.hardware_config else None,
            ),
        }

        # Debug: Check if controllers received configuration
        for name, controller in self.controllers.items():
            config_attr = f"{name.lower()}_config"
            if name == "Robot":
                has_config = (
                    hasattr(controller, "robot_config") and controller.robot_config is not None
                )
                logger.info(
                    f"  {name} Controller: {'has config' if has_config else 'config is None'}"
                )
            elif name == "DigitalIO":
                has_config = (
                    hasattr(controller, "digital_io_config")
                    and controller.digital_io_config is not None
                )
                logger.info(
                    f"  {name} Controller: {'has config' if has_config else 'config is None'}"
                )
            else:
                has_config = (
                    hasattr(controller, config_attr)
                    and getattr(controller, config_attr) is not None
                )
                logger.info(
                    f"  {name} Controller: {'has config' if has_config else 'config is None'}"
                )

        logger.info(f"Initialized {len(self.controllers)} hardware controllers")

    def _load_hardware_configurations(self):
        """Load all hardware configurations from YAML file with enhanced debugging"""
        logger.debug("Starting hardware configuration loading process")

        try:
            if not self.configuration_service:
                logger.error("Configuration service is None - cannot load hardware config!")
                logger.error("This indicates a CLI initialization problem.")
                return None

            logger.debug(
                f"Configuration service available: {type(self.configuration_service).__name__}"
            )

            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
                if loop:
                    logger.debug(f"Event loop status: exists=True, running={loop.is_running()}")
                else:
                    logger.debug("Event loop status: exists=False")

                if loop.is_running():
                    # We're in an async context but need to run sync
                    # Try to use asyncio.create_task or run in thread to avoid blocking
                    logger.warning(
                        "Running event loop detected - attempting alternative config loading"
                    )
                    try:
                        # Try using run_in_executor to run async code in thread
                        import concurrent.futures

                        def load_config_sync():
                            # Create new event loop in thread
                            new_loop = asyncio.new_event_loop()
                            try:
                                asyncio.set_event_loop(new_loop)
                                if self.configuration_service is not None:
                                    return new_loop.run_until_complete(
                                        self.configuration_service.load_hardware_config()
                                    )
                                return None
                            finally:
                                new_loop.close()

                        # Run in thread to avoid event loop conflict
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(load_config_sync)
                            hw_config = future.result(timeout=10)  # 10 second timeout

                        if hw_config:
                            logger.info("Successfully loaded hardware config using thread executor")
                            return hw_config
                        else:
                            logger.error("Thread executor returned None config")
                            return None

                    except Exception as thread_e:
                        logger.error(f"Thread executor failed: {thread_e}")
                        logger.error("Falling back to default configurations")
                        return None
                else:
                    logger.debug("Loading hardware config using existing event loop")
                    if self.configuration_service is not None:
                        hw_config = loop.run_until_complete(
                            self.configuration_service.load_hardware_config()
                        )
                        logger.info(
                            "Successfully loaded hardware configurations from YAML using existing loop"
                        )
                        return hw_config
                    else:
                        logger.error("Configuration service is None")
                        return None

            except RuntimeError as e:
                logger.debug(f"RuntimeError in event loop: {e} - creating new loop")
                # No event loop running, create one
                if self.configuration_service is not None:
                    hw_config = asyncio.run(self.configuration_service.load_hardware_config())
                    logger.info(
                        "Successfully loaded hardware configurations from YAML using new loop"
                    )
                    return hw_config
                else:
                    logger.error("❌ Configuration service is None")
                    return None

        except Exception as e:
            logger.error(f"Exception in hardware configuration loading: {type(e).__name__}: {e}")
            logger.error("Using default hardware configurations as fallback")
            import traceback

            logger.debug(f"Full traceback: {traceback.format_exc()}")
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
            "5": "Digital Output Control",
            "6": "All Hardware Status",
            "b": "Back to Main Menu",
        }

        return simple_interactive_menu(
            self.console, menu_options, "Hardware Control Center", "Select hardware to control"
        )

    async def execute_hardware_control(self, selection: str) -> None:
        """Execute hardware control based on selection"""
        if selection == "b":
            return

        if selection == "6":
            await self._show_all_hardware_status()
            return

        # Map selection to controller
        controller_map = {"1": "Robot", "2": "MCU", "3": "LoadCell", "4": "Power", "5": "DigitalIO"}

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

    async def execute_robot_home(self) -> bool:
        """Execute complete Robot Home sequence: Connect → Servo On → Home.

        Performs the full robot initialization sequence with user feedback:
        1. Robot Connect - Verify/establish connection
        2. Robot Servo On - Enable servo for movement
        3. Robot Home - Move robot to home position

        Returns:
            bool: True if complete sequence succeeded, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from src.application.use_cases.robot_home import (
                RobotHomeCommand,
                RobotHomeUseCase,
            )

            # Get robot controller and service
            robot_controller = self.controllers.get("Robot")
            if not robot_controller:
                logger.error("Robot controller not available")
                self.formatter.print_message(
                    "Robot controller not available. Please check system configuration.",
                    message_type="error",
                    title="Robot Controller Error"
                )
                return False

            robot_service = robot_controller.robot_service
            if not robot_service:
                logger.error("Robot service not available")
                self.formatter.print_message(
                    "Robot service not available. Please check hardware configuration.",
                    message_type="error",
                    title="Robot Service Error"
                )
                return False

            # Step 1: Robot Connect - Verify/establish connection
            self.formatter.print_message(
                "Step 1/3: Checking robot connection...",
                message_type="info",
                title="🔗 Robot Connect"
            )
            
            try:
                # Check if robot is already connected
                is_connected = await robot_service.is_connected()
                
                if not is_connected:
                    logger.info("Robot not connected, attempting to connect...")
                    self.formatter.print_message(
                        "Robot not connected. Establishing connection...",
                        message_type="warning"
                    )
                    
                    # Attempt to connect
                    await robot_service.connect()
                    
                    # Verify connection was successful
                    is_connected = await robot_service.is_connected()
                    
                if is_connected:
                    self.formatter.print_message(
                        "✅ Robot connection verified successfully",
                        message_type="success"
                    )
                    logger.info("Robot connection verified")
                else:
                    raise Exception("Failed to establish robot connection")
                    
            except Exception as connect_error:
                logger.error(f"Robot connection failed: {connect_error}")
                self.formatter.print_message(
                    f"❌ Robot connection failed: {str(connect_error)}",
                    message_type="error",
                    title="Connection Error"
                )
                return False

            # Step 2: Robot Servo On - Enable servo for movement
            self.formatter.print_message(
                "Step 2/3: Enabling robot servo...",
                message_type="info",
                title="⚡ Robot Servo On"
            )
            
            try:
                # Use configured axis_id from hardware configuration
                axis_id = self.axis_id
                logger.info(f"Enabling servo for axis {axis_id}")
                
                await robot_service.enable_servo(axis_id)
                
                self.formatter.print_message(
                    f"✅ Robot servo enabled successfully (axis {axis_id})",
                    message_type="success"
                )
                logger.info(f"Robot servo enabled for axis {axis_id}")
                
            except Exception as servo_error:
                logger.error(f"Robot servo enable failed: {servo_error}")
                self.formatter.print_message(
                    f"❌ Robot servo enable failed: {str(servo_error)}",
                    message_type="error",
                    title="Servo Error"
                )
                return False

            # Step 3: Robot Home - Move robot to home position
            self.formatter.print_message(
                "Step 3/3: Executing robot home operation...",
                message_type="info",
                title="🏠 Robot Home"
            )

            # Create a minimal hardware facade for the Robot Home use case
            from src.infrastructure.implementation.hardware.digital_io.mock.mock_dio import (
                MockDIO,
            )
            from src.infrastructure.implementation.hardware.loadcell.mock.mock_loadcell import (
                MockLoadCell,
            )
            from src.infrastructure.implementation.hardware.mcu.mock.mock_mcu import (
                MockMCU,
            )
            from src.infrastructure.implementation.hardware.power.mock.mock_power import (
                MockPower,
            )

            # Create minimal facade with real robot service and mock others for robot home operation
            facade = HardwareServiceFacade(
                robot_service=robot_service,
                mcu_service=MockMCU(),
                loadcell_service=MockLoadCell(),
                power_service=MockPower(),
                digital_io_service=MockDIO({}),
            )

            # Create Robot Home use case
            robot_home_use_case = RobotHomeUseCase(facade)

            # Create Robot Home command
            command = RobotHomeCommand(operator_id="cli_user")

            # Execute Robot Home operation
            logger.info("Executing robot homing operation...")
            result = await robot_home_use_case.execute(command)

            if result.is_success:
                self.formatter.print_message(
                    f"✅ Robot home operation completed successfully in {result.execution_duration.seconds:.2f}s",
                    message_type="success",
                    title="Home Complete"
                )
                logger.info(
                    f"Robot homing completed successfully in {result.execution_duration.seconds:.2f}s"
                )
                
                # Display complete sequence success
                self.formatter.print_message(
                    "🎉 Complete robot home sequence finished successfully!\n"
                    "   1. ✅ Robot Connected\n"
                    "   2. ✅ Servo Enabled\n" 
                    "   3. ✅ Home Position Reached",
                    message_type="success",
                    title="Robot Home Sequence Complete"
                )
                
                return True
            else:
                logger.error(f"Robot homing failed: {result.error_message}")
                self.formatter.print_message(
                    f"❌ Robot home operation failed: {result.error_message}",
                    message_type="error",
                    title="Home Failed"
                )
                return False

        except Exception as e:
            logger.error(f"Robot home sequence error: {e}")
            self.formatter.print_message(
                f"❌ Robot home sequence failed: {str(e)}",
                message_type="error",
                title="Sequence Error"
            )
            return False
