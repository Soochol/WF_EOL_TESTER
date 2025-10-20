"""
Main Window

Main application window with sidebar navigation and content area.
"""

# Standard library imports
from typing import Optional, TYPE_CHECKING

# Third-party imports
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from application.containers.simple_reloadable_container import SimpleReloadableContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.page_transition import PageTransitionManager
from ui.gui.widgets.content.about_widget import AboutWidget
from ui.gui.widgets.content.dashboard_widget import DashboardWidget
from ui.gui.widgets.content.digital_output import DigitalOutputControlWidget
from ui.gui.widgets.content.logs_widget import LogsWidget
from ui.gui.widgets.content.mcu import MCUControlWidget
from ui.gui.widgets.content.power_supply import PowerSupplyControlWidget
from ui.gui.widgets.content.results_widget import ResultsWidget
from ui.gui.widgets.content.robot import RobotControlWidget
from ui.gui.widgets.content.settings_widget import SettingsWidget
from ui.gui.widgets.content.test_control_widget import TestControlWidget
from ui.gui.widgets.header.modern_header_widget import ModernHeaderWidget
from ui.gui.widgets.sidebar.sidebar_widget import SidebarWidget


# Type-checking only imports to avoid circular dependencies
if TYPE_CHECKING:
    # Local application imports
    from ui.gui.widgets.content.statistics.pages.new_advanced_page import (
        NewAdvancedPage,
    )
    from ui.gui.widgets.content.statistics.pages.new_analysis_page import (
        NewAnalysisPage,
    )
    from ui.gui.widgets.content.statistics.pages.new_overview_page import (
        NewOverviewPage,
    )


class TestExecutorThread(QThread):
    """
    Thread for executing all hardware operations in background without blocking GUI.

    Handles:
    - Test execution (EOL, Heating/Cooling, MCU tests)
    - Robot operations (connect, move, servo, etc.)
    - MCU operations (connect, temperature, etc.)

    All operations run on a single event loop to prevent conflicts.
    """

    # Signals for communicating with GUI
    test_started = Signal(str)  # test_name
    test_progress = Signal(int, int, str)  # current_cycle, total_cycles, status
    test_result = Signal(object)  # test result data
    test_completed = Signal(bool, str)  # success, message
    test_error = Signal(str)  # error message
    log_message = Signal(str, str, str)  # level, component, message

    # Hardware operation signals
    operation_completed = Signal(str, object)  # operation_id, result
    operation_failed = Signal(str, str)  # operation_id, error_message

    # Hardware status signals (for syncing with Hardware pages)
    hardware_status_changed = Signal(str, bool)  # hardware_name, is_connected

    def __init__(self, container, parent=None):
        super().__init__(parent)
        self.container = container

        # Test-specific state (for backward compatibility)
        self.test_sequence: Optional[str] = None
        self.serial_number: Optional[str] = None
        self.should_stop: bool = False
        self.is_test_running: bool = False  # ✅ Track if a test is currently executing

        # Task queue for operations
        # Standard library imports
        from queue import Queue

        self.task_queue = Queue()
        self._running = True

    def stop_test(self):
        """Request test to stop"""
        self.should_stop = True

    def stop(self):
        """Stop the executor thread gracefully"""
        # Third-party imports
        from loguru import logger

        logger.info("🛑 Stopping TestExecutorThread...")
        self._running = False

    def submit_task(self, operation_id: str, coroutine):
        """
        Submit a hardware operation task.

        Args:
            operation_id: Unique identifier for this operation
            coroutine: Async coroutine to execute
        """
        # Third-party imports
        from loguru import logger

        task_info = {"id": operation_id, "coroutine": coroutine, "type": "operation"}
        self.task_queue.put(task_info)
        logger.debug(f"Task submitted: {operation_id}")

    def submit_test(self, test_sequence: str, serial_number: str):
        """
        Submit a test execution task.

        Args:
            test_sequence: Test sequence name
            serial_number: DUT serial number
        """
        # Third-party imports
        from loguru import logger

        # Set test-specific state
        self.test_sequence = test_sequence
        self.serial_number = serial_number
        self.should_stop = False

        task_info = {
            "id": f"test_{test_sequence}",
            "test_sequence": test_sequence,
            "serial_number": serial_number,
            "type": "test",
        }
        self.task_queue.put(task_info)
        logger.debug(f"Test submitted: {test_sequence}")

    async def _ensure_hardware_connected(self):
        """
        Ensure hardware is connected in this thread's event loop.

        Only connects if not already connected. If already connected in a
        different event loop, reconnects in the current loop.
        """
        # Third-party imports

        # Third-party imports
        from loguru import logger

        try:
            hardware_facade = self.container.hardware_service_facade()
            # Access loadcell_service as a property, not a method
            loadcell = hardware_facade.loadcell_service

            if not loadcell:
                return

            is_connected = await loadcell.is_connected()

            if not is_connected:
                # Not connected - connect in this thread's event loop
                self.log_message.emit(
                    "INFO", "HARDWARE", "Connecting BS205 loadcell in test thread's event loop"
                )
                await loadcell.connect()
                self.log_message.emit("INFO", "HARDWARE", "BS205 loadcell connected successfully")
            else:
                # Already connected - but might be in wrong loop
                # Reconnect to ensure it's in the correct event loop
                self.log_message.emit(
                    "INFO", "HARDWARE", "Reconnecting BS205 loadcell to test thread's event loop"
                )

                try:
                    await loadcell.disconnect()
                except Exception as e:
                    logger.warning(f"Disconnect error (expected if from different loop): {e}")

                await loadcell.connect()
                self.log_message.emit("INFO", "HARDWARE", "BS205 loadcell reconnected successfully")

        except Exception as e:
            logger.error(f"Error ensuring hardware connection: {e}")
            self.log_message.emit(
                "WARNING", "HARDWARE", f"Failed to ensure hardware connection: {e}"
            )

    async def _emit_hardware_status(self):
        """
        Emit hardware status signals to update Hardware page button states.

        This method checks the connection status of all hardware and emits
        hardware_status_changed signals so that Robot/MCU pages can sync their states.
        """
        try:
            hardware_facade = self.container.hardware_service_facade()

            # Check Robot connection status
            is_robot_connected = await hardware_facade.robot_service.is_connected()
            self.hardware_status_changed.emit("robot", is_robot_connected)

            # Check MCU connection status
            is_mcu_connected = await hardware_facade.mcu_service.is_connected()
            self.hardware_status_changed.emit("mcu", is_mcu_connected)

        except Exception as e:
            # Third-party imports
            from loguru import logger

            logger.warning(f"Failed to emit hardware status: {e}")

    def _evaluate_test_result(self, result):
        """
        Evaluate test result to determine actual success/failure status.

        Args:
            result: Test result object (EOLTestResult, HeatingCoolingTestResult, etc.) or None

        Returns:
            tuple: (success: bool, message: str)
        """
        # Third-party imports
        from loguru import logger

        # Handle None result (test was cancelled or failed to execute)
        if result is None:
            logger.debug("Test result is None - treating as failure")
            return False, "Test failed to execute or was cancelled"

        # Handle EOLTestResult
        if hasattr(result, "test_status"):
            # Local application imports
            from domain.enums.test_status import TestStatus

            logger.debug(f"Evaluating EOLTestResult with status: {result.test_status}")

            if result.test_status == TestStatus.COMPLETED:
                # For COMPLETED status, check if test actually passed
                if hasattr(result, "is_passed") and result.is_passed:
                    return True, "EOL Force Test completed successfully"
                else:
                    return False, "EOL Force Test completed but failed validation"
            elif result.test_status == TestStatus.FAILED:
                return False, "EOL Force Test failed"
            elif result.test_status == TestStatus.ERROR:
                return False, "EOL Force Test encountered an error"
            elif result.test_status == TestStatus.CANCELLED:
                return False, "EOL Force Test was cancelled"
            else:
                logger.warning(f"Unknown test status: {result.test_status}")
                return False, f"Test completed with unknown status: {result.test_status}"

        # Handle HeatingCoolingTestResult
        if hasattr(result, "success") or hasattr(result, "passed"):
            success_field = getattr(result, "success", getattr(result, "passed", False))
            logger.debug(f"Evaluating HeatingCoolingTestResult with success: {success_field}")

            if success_field:
                return True, "Heating Cooling Test completed successfully"
            else:
                return False, "Heating Cooling Test failed"

        # Handle dict results (Custom Test)
        if isinstance(result, dict):
            status = result.get("status", "").upper()
            logger.debug(f"Evaluating dict result with status: {status}")

            if status == "SUCCESS":
                return True, result.get("message", "Custom test completed successfully")
            else:
                return False, result.get("message", "Custom test failed")

        # Handle Simple MCU Test result (placeholder - should check actual result structure)
        if hasattr(result, "is_passed"):
            logger.debug(f"Evaluating MCU test result with is_passed: {result.is_passed}")

            if result.is_passed:
                return True, "Simple MCU Test completed successfully"
            else:
                return False, "Simple MCU Test failed"

        # Unknown result type - assume success if object exists (fallback for backward compatibility)
        logger.warning(f"Unknown result type: {type(result)} - assuming success")
        return True, "Test completed (result type unknown)"

    def _execute_test_task(self, loop, task_info):
        """Execute a test task"""
        # Third-party imports
        from loguru import logger

        # Set test-specific state
        self.test_sequence = task_info["test_sequence"]
        self.serial_number = task_info["serial_number"]
        self.should_stop = False
        self.is_test_running = True  # ✅ Mark test as running

        try:
            # Run the test
            result = loop.run_until_complete(self._execute_test())

            # Check actual test success/failure based on result type and content
            success, message = self._evaluate_test_result(result)
            logger.debug(f"Test completed, emitting signal: success={success}, message={message}")
            self.test_completed.emit(success, message)

        except KeyboardInterrupt:
            # Emergency Stop으로 인한 중단 - 정상적인 상황
            logger.info("Test cancelled by Emergency Stop")
            self.test_completed.emit(False, "Test cancelled by Emergency Stop")
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            self.test_error.emit(str(e))
        finally:
            self.is_test_running = False  # ✅ Mark test as finished
            logger.debug("Test execution completed, is_test_running set to False")

            # ✅ Emit hardware status after test completion (hardware may be disconnected)
            loop.run_until_complete(self._emit_hardware_status())

    def _execute_operation_task(self, loop, task_info):
        """Execute a hardware operation task (Robot/MCU)"""
        # Third-party imports
        from loguru import logger

        operation_id = task_info["id"]
        coroutine = task_info["coroutine"]

        try:
            logger.debug(f"Executing operation: {operation_id}")
            result = loop.run_until_complete(coroutine)
            self.operation_completed.emit(operation_id, result)
            logger.debug(f"Operation completed: {operation_id}")
        except Exception as e:
            logger.error(f"Operation failed: {operation_id} - {e}")
            self.operation_failed.emit(operation_id, str(e))

    def run(self):
        """Run hardware executor thread with persistent event loop"""
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        # Standard library imports
        import time

        # Third-party imports
        import asyncio
        from loguru import logger

        logger.info("🔧 TestExecutorThread started (Hardware Executor)")

        loop = None
        try:
            # Create persistent event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # ✅ Main execution loop - runs continuously until app shutdown
            while self._running:
                try:
                    # Check for tasks in queue
                    if not self.task_queue.empty():
                        task_info = self.task_queue.get_nowait()

                        if task_info["type"] == "test":
                            # Test execution
                            self._execute_test_task(loop, task_info)
                        elif task_info["type"] == "operation":
                            # Hardware operation (Robot/MCU)
                            self._execute_operation_task(loop, task_info)
                    else:
                        # No tasks - sleep briefly to avoid busy waiting
                        time.sleep(0.01)

                except Exception as e:
                    logger.error(f"Task processing error: {e}")

        except Exception as e:
            logger.error(f"TestExecutorThread fatal error: {e}")
        finally:
            # Cleanup event loop
            if loop:
                try:
                    # Gracefully cleanup all pending tasks before closing the loop
                    pending_tasks = asyncio.all_tasks(loop)
                    if pending_tasks:
                        logger.debug(
                            f"🧹 EXECUTOR_CLEANUP: Found {len(pending_tasks)} pending tasks to cleanup"
                        )

                        # Cancel all pending tasks
                        for task in pending_tasks:
                            if not task.done():
                                task.cancel()

                        # Wait for all tasks to finish cancellation (with timeout)
                        try:
                            loop.run_until_complete(
                                asyncio.wait_for(
                                    asyncio.gather(*pending_tasks, return_exceptions=True),
                                    timeout=2.0,  # 2 second timeout for cleanup
                                )
                            )
                            logger.debug("🧹 EXECUTOR_CLEANUP: All tasks cleaned up successfully")
                        except asyncio.TimeoutError:
                            logger.warning("🧹 EXECUTOR_CLEANUP: Task cleanup timed out")
                        except Exception as cleanup_error:
                            logger.debug(
                                f"🧹 EXECUTOR_CLEANUP: Task cleanup with exceptions: {cleanup_error}"
                            )

                    # Now it's safe to close the loop
                    loop.close()
                    logger.info("🔧 TestExecutorThread stopped - Event loop closed")

                except Exception as e:
                    logger.error(f"🧹 EXECUTOR_CLEANUP: Error during cleanup: {e}")
                    try:
                        loop.close()
                    except Exception:
                        pass

    async def _execute_test(self):
        """Execute the selected test asynchronously"""
        # Local application imports
        from domain.value_objects.dut_command_info import DUTCommandInfo

        # Validate test parameters
        if not self.serial_number or not self.test_sequence:
            raise ValueError("Test parameters not set (serial_number or test_sequence is None)")

        try:
            # Create DUT command info
            dut_info = DUTCommandInfo(
                dut_id=f"DUT_{self.serial_number}",
                model_number="WF_EOL_MODEL",
                serial_number=self.serial_number,
                manufacturer="Withforce",
            )

            self.log_message.emit(
                "INFO", "TEST", f"Starting {self.test_sequence} for SN: {self.serial_number}"
            )
            self.test_started.emit(self.test_sequence)

            # Select and execute the appropriate UseCase
            if self.test_sequence == "EOL Force Test":
                result = await self._execute_eol_force_test(dut_info)
            elif self.test_sequence == "Heating Cooling Time Test":
                result = await self._execute_heating_cooling_test(dut_info)
            elif self.test_sequence == "Simple MCU Test":
                result = await self._execute_simple_mcu_test(dut_info)
            elif self.test_sequence == "Custom Test Sequence":
                result = await self._execute_custom_test(dut_info)
            else:
                raise ValueError(f"Unknown test sequence: {self.test_sequence}")

            # Emit the result for GUI processing
            self.test_result.emit(result)
            self.log_message.emit("INFO", "TEST", f"Test {self.test_sequence} completed")
            return result

        except Exception as e:
            self.log_message.emit("ERROR", "TEST", f"Test execution failed: {str(e)}")
            raise

    async def _execute_eol_force_test(self, dut_info):
        """Execute EOL Force Test with Task-based cancellation"""
        # Third-party imports
        import asyncio

        # Local application imports
        from application.use_cases.eol_force_test.main_use_case import EOLForceTestInput

        # Check for stop signal before starting
        if self.should_stop:
            self.log_message.emit("WARNING", "EOL_TEST", "EOL Force Test cancelled before start")
            return None

        # CRITICAL FIX: Ensure hardware is connected in this thread's event loop
        # This ensures all asyncio tasks use the correct event loop
        await self._ensure_hardware_connected()

        # Create test input
        test_input = EOLForceTestInput(dut_info=dut_info, operator_id="GUI_USER")

        # Get use case from container
        self.log_message.emit("INFO", "EOL_TEST", f"Using container ID: {id(self.container)}")

        # Verify GUI State Manager connection before test execution
        hardware_facade = self.container.hardware_service_facade()
        # pylint: disable=protected-access  # Intentional access for verification
        gui_state_manager_status = (
            hasattr(hardware_facade, "_gui_state_manager")
            and hardware_facade._gui_state_manager is not None
        )
        self.log_message.emit(
            "INFO", "EOL_TEST", f"Pre-test GUI State Manager status: {gui_state_manager_status}"
        )

        if gui_state_manager_status:
            self.log_message.emit(
                "INFO",
                "EOL_TEST",
                f"Hardware facade GUI State Manager ID: {id(hardware_facade._gui_state_manager)}",
            )
        else:
            self.log_message.emit(
                "WARNING",
                "EOL_TEST",
                "GUI State Manager not connected - attempting runtime injection",
            )
            # Try to get state manager from parent main window and inject it
            parent_state_manager = getattr(self.parent(), "state_manager", None)
            if parent_state_manager:
                hardware_facade._gui_state_manager = parent_state_manager
                self.log_message.emit(
                    "INFO",
                    "EOL_TEST",
                    f"Runtime GUI State Manager injection completed with ID: {id(parent_state_manager)}",
                )
            else:
                self.log_message.emit(
                    "ERROR", "EOL_TEST", "No state manager available for runtime injection"
                )
        # pylint: enable=protected-access

        eol_test_use_case = self.container.eol_force_test_use_case()

        self.log_message.emit("INFO", "EOL_TEST", "Executing EOL Force Test...")

        # ✅ Emit hardware status changes (test connects hardware)
        await self._emit_hardware_status()

        # Create Task for UseCase execution
        task = asyncio.create_task(eol_test_use_case.execute(test_input))

        # Monitor task execution and check for cancellation every 100ms
        while not task.done():
            if self.should_stop:
                self.log_message.emit(
                    "WARNING", "EOL_TEST", "EOL Force Test cancelled - stopping UseCase"
                )
                task.cancel()  # Cancel the UseCase Task
                try:
                    await task  # Wait for CancelledError processing
                except (asyncio.CancelledError, KeyboardInterrupt):
                    self.log_message.emit(
                        "INFO", "EOL_TEST", "EOL Force Test cancelled successfully"
                    )
                except Exception as e:
                    self.log_message.emit(
                        "WARNING", "EOL_TEST", f"Exception during cancellation: {e}"
                    )
                return None

            # Check every 100ms for responsive cancellation
            await asyncio.sleep(0.1)

        # Get result from completed task - ensure all exceptions are handled
        try:
            result = await task
            self.log_message.emit(
                "INFO", "EOL_TEST", f"EOL Force Test result: {result.test_status.value}"
            )
            return result
        except (asyncio.CancelledError, KeyboardInterrupt):
            self.log_message.emit("INFO", "EOL_TEST", "EOL Force Test was cancelled")
            return None
        except Exception as e:
            self.log_message.emit("ERROR", "EOL_TEST", f"EOL Force Test failed with exception: {e}")
            return None

    async def _execute_heating_cooling_test(self, dut_info):
        """Execute Heating Cooling Time Test with Task-based cancellation"""
        # Third-party imports
        import asyncio

        # Local application imports
        from application.use_cases.heating_cooling_time_test.main_use_case import (
            HeatingCoolingTimeTestInput,
        )

        # Check for stop signal before starting
        if self.should_stop:
            self.log_message.emit(
                "WARNING", "HEATING_COOLING", "Heating Cooling Test cancelled before start"
            )
            return None

        # CRITICAL FIX: Ensure hardware is connected in this thread's event loop
        await self._ensure_hardware_connected()

        # Create test input
        test_input = HeatingCoolingTimeTestInput(dut_info=dut_info, operator_id="GUI_USER")

        # Get use case from container
        heating_cooling_use_case = self.container.heating_cooling_time_test_use_case()

        self.log_message.emit("INFO", "HEATING_COOLING", "Executing Heating Cooling Time Test...")

        # ✅ Emit hardware status changes (test connects hardware)
        await self._emit_hardware_status()

        # Create Task for UseCase execution
        task = asyncio.create_task(heating_cooling_use_case.execute(test_input))

        # Monitor task execution and check for cancellation every 100ms
        while not task.done():
            if self.should_stop:
                self.log_message.emit(
                    "WARNING",
                    "HEATING_COOLING",
                    "Heating Cooling Test cancelled - stopping UseCase",
                )
                task.cancel()  # Cancel the UseCase Task
                try:
                    await task  # Wait for CancelledError processing
                except (asyncio.CancelledError, KeyboardInterrupt):
                    self.log_message.emit(
                        "INFO", "HEATING_COOLING", "Heating Cooling Test cancelled successfully"
                    )
                except Exception as e:
                    self.log_message.emit(
                        "WARNING", "HEATING_COOLING", f"Exception during cancellation: {e}"
                    )
                return None

            # Check every 100ms for responsive cancellation
            await asyncio.sleep(0.1)

        # Get result from completed task - ensure all exceptions are handled
        try:
            result = await task
            self.log_message.emit(
                "INFO",
                "HEATING_COOLING",
                f"Heating Cooling Test result: {result.test_status.value}",
            )
            return result
        except (asyncio.CancelledError, KeyboardInterrupt):
            self.log_message.emit("INFO", "HEATING_COOLING", "Heating Cooling Test was cancelled")
            return None
        except Exception as e:
            self.log_message.emit(
                "ERROR", "HEATING_COOLING", f"Heating Cooling Test failed with exception: {e}"
            )
            return None

    async def _execute_simple_mcu_test(self, _dut_info):  # pylint: disable=unused-argument
        """Execute Simple MCU Test (placeholder implementation)"""
        # Third-party imports
        import asyncio

        # Local application imports
        from domain.value_objects.eol_test_result import EOLTestResult
        from domain.value_objects.identifiers import TestId
        from domain.value_objects.time_values import TestDuration

        # Check for stop signal before starting
        if self.should_stop:
            self.log_message.emit("WARNING", "MCU_TEST", "Simple MCU Test cancelled before start")
            return None

        # CRITICAL FIX: Ensure hardware is connected in this thread's event loop
        await self._ensure_hardware_connected()

        self.log_message.emit("INFO", "MCU_TEST", "Executing Simple MCU Test (placeholder)...")

        # Simulate test duration with cancellation checking
        for _ in range(20):  # 2 seconds = 20 * 0.1s
            if self.should_stop:
                self.log_message.emit(
                    "WARNING", "MCU_TEST", "Simple MCU Test cancelled during execution"
                )
                return None
            await asyncio.sleep(0.1)

        # Create a placeholder result
        result = EOLTestResult.create_success(
            test_id=TestId.generate(),
            is_passed=True,
            duration=TestDuration.from_seconds(2.0),
            notes="Placeholder MCU test - not yet implemented",
        )

        self.log_message.emit(
            "INFO", "MCU_TEST", f"Simple MCU Test result: {result.test_status.value}"
        )
        return result

    async def _execute_custom_test(self, _dut_info):  # pylint: disable=unused-argument
        """Execute Custom Test Sequence"""
        # Third-party imports
        import asyncio

        # Check for stop signal before starting
        if self.should_stop:
            self.log_message.emit("WARNING", "CUSTOM_TEST", "Custom test cancelled before start")
            return None

        self.log_message.emit("INFO", "CUSTOM_TEST", "Custom test sequence not yet implemented")

        # TODO: Implement custom test sequence
        # For now, simulate test duration with cancellation checking
        for _ in range(20):  # 2 seconds = 20 * 0.1s
            if self.should_stop:
                self.log_message.emit(
                    "WARNING", "CUSTOM_TEST", "Custom test cancelled during execution"
                )
                return None
            await asyncio.sleep(0.1)

        return {"status": "SUCCESS", "message": "Custom test completed (mock)"}


class RobotHomeThread(QThread):
    """
    Thread for executing robot home operation in background without blocking GUI.
    """

    # Signals for communicating with GUI
    started = Signal()
    progress = Signal(str)  # progress message
    completed = Signal(bool, str)  # success, message

    def __init__(self, container):
        super().__init__()
        self.container = container

    def run(self):
        """Execute robot home operation in separate thread"""
        # Third-party imports
        import asyncio
        from loguru import logger

        self.started.emit()
        logger.info("Robot home thread started")

        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Use START TEST pattern: create_task + monitoring loop
            result = loop.run_until_complete(self._run_robot_home_task())

            if result and result.is_success:
                self.completed.emit(True, "Robot home completed successfully")
            else:
                error_msg = result.error_message if result else "Unknown error"
                self.completed.emit(False, f"Robot home failed: {error_msg}")

        except Exception as e:
            logger.error(f"Robot home thread exception: {e}")
            self.completed.emit(False, f"Robot home exception: {str(e)}")
        finally:
            try:
                loop.close()
            except Exception:
                pass

    async def _run_robot_home_task(self):
        """Run robot home task using START TEST pattern"""
        # Third-party imports
        import asyncio

        # Create task for robot home operation (like START TEST)
        task = asyncio.create_task(self._execute_robot_home())

        # Monitor task execution (like START TEST pattern)
        while not task.done():
            await asyncio.sleep(0.1)

        # Get result
        return task.result()

    async def _execute_robot_home(self):
        """Execute the robot home operation asynchronously using task-based pattern like START TEST"""
        # Third-party imports
        import asyncio
        from loguru import logger

        self.progress.emit("Starting robot home operation...")
        logger.info("Starting robot home operation...")

        try:
            # Get robot home use case from container
            self.progress.emit("Getting robot home use case...")
            robot_home_use_case = self.container.robot_home_use_case()

            # Import required input class
            self.progress.emit("Creating robot home input...")
            # Local application imports
            from application.use_cases.robot_operations.input import RobotHomeInput

            # Create input for robot home operation
            home_input = RobotHomeInput()

            # Execute robot home operation using Task-based pattern (like START TEST)
            self.progress.emit("Executing robot home operation...")

            # Create Task for UseCase execution (same pattern as TestExecutorThread)
            task = asyncio.create_task(robot_home_use_case.execute(home_input))

            # Monitor task execution (same pattern as START TEST)
            while not task.done():
                # Check every 100ms for task completion
                await asyncio.sleep(0.1)

            # Get result from completed task (same pattern as START TEST)
            try:
                result = await task
                return result
            except (asyncio.CancelledError, KeyboardInterrupt):
                logger.info("Robot home operation was cancelled")
                return None
            except Exception as e:
                logger.error(f"Robot home task exception: {e}")
                raise

        except Exception as e:
            logger.error(f"Robot home operation exception: {e}")
            raise


class MainWindow(QMainWindow):
    """
    Main application window.

    Contains sidebar navigation and stacked content area for different pages.
    """

    def __init__(
        self,
        container: SimpleReloadableContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
        lazy_init: bool = False,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager

        # ✅ Create persistent TestExecutorThread at startup
        self.test_executor_thread = TestExecutorThread(container, self)
        self.test_executor_thread.start()
        # Third-party imports
        from loguru import logger

        logger.info("🔧 TestExecutorThread created and started at application startup")

        self.robot_home_thread: Optional[RobotHomeThread] = (
            None  # For background robot home execution
        )
        self.emergency_stop_active = False  # Track emergency stop state
        self.page_transition_manager: Optional[PageTransitionManager] = None  # Page transitions

        # GUI State Manager is already injected in main_gui.py during initialization
        # No need to inject again here to avoid overwriting the connection

        # Initialize widgets containers for lazy loading
        self.content_widgets = {}
        self.sidebar: Optional[SidebarWidget] = None
        self.content_stack: Optional[QStackedWidget] = None
        self.header: Optional[ModernHeaderWidget] = None

        # Initialize page attributes (set to None until created)
        self.dashboard_page: Optional[QWidget] = None
        self.test_control_page: Optional[TestControlWidget] = None
        self.robot_page: Optional[RobotControlWidget] = None
        self.mcu_page: Optional[MCUControlWidget] = None
        self.power_supply_page: Optional[QWidget] = None
        self.digital_output_page: Optional[QWidget] = None
        self.digital_input_page: Optional[QWidget] = None
        self.loadcell_page: Optional[QWidget] = None
        self.results_page: Optional[ResultsWidget] = None
        self.statistics_page: Optional[QWidget] = None
        self.statistics_header: Optional[QWidget] = None
        self.overview_page: Optional["NewOverviewPage"] = None
        self.analysis_page: Optional["NewAnalysisPage"] = None
        self.advanced_page: Optional["NewAdvancedPage"] = None
        self.logs_page: Optional[LogsWidget] = None
        self.about_page: Optional[QWidget] = None
        self.settings_page: Optional[SettingsWidget] = None
        self.pages: dict = {}

        # Test execution state
        self._test_signals_connected: bool = False

        if lazy_init:
            self.setup_basic_ui()
        else:
            self.setup_ui()
            self.setup_status_bar()
            self.setup_update_timer()
            # Start maximized for industrial use
            self.showMaximized()

    def setup_basic_ui(self) -> None:
        """Setup basic window structure for lazy loading"""
        # Window properties
        self.setWindowTitle("")
        self.setMinimumSize(1200, 1100)  # Increased height for better content visibility
        self.resize(1400, 1200)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout (vertical to accommodate header)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Content area layout (sidebar + main content) - use proper horizontal layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 10, 0, 0)  # 10px top margin for alignment

        # Create proper SidebarWidget with navigation functionality
        self.sidebar = SidebarWidget()
        self.sidebar.page_changed.connect(self.change_page)
        self.sidebar.settings_clicked.connect(self._on_header_settings_clicked)

        # Content stack - create but don't populate (remove problematic margins)
        self.content_stack = QStackedWidget()
        self.content_stack.setContentsMargins(10, 0, 0, 0)  # Small left separation margin only
        self.content_stack.setMinimumWidth(400)  # Ensure content has minimum space

        # Initialize page transition manager
        self.page_transition_manager = PageTransitionManager(self.content_stack)

        # Add widgets to layout with proper stretch factors
        content_layout.addWidget(self.sidebar)  # Sidebar: fixed width (200px)
        content_layout.addWidget(self.content_stack)  # Content: expandable

        # Set stretch factors: sidebar fixed (0), content expandable (1)
        content_layout.setStretchFactor(self.sidebar, 0)  # Fixed: 200px
        content_layout.setStretchFactor(self.content_stack, 1)  # Expandable: remaining space

        # Add content area to main layout with stretch factor to take remaining space
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(
            content_widget, 1
        )  # Stretch factor 1: take all remaining vertical space

        # Show maximized for industrial use
        self.showMaximized()

    def init_header(self) -> None:
        """Initialize header widget"""
        if self.header is not None:
            return  # Already initialized

        # Get main layout
        layout = self.centralWidget().layout()
        if layout is None:
            return

        # Ensure it's a QVBoxLayout (should be based on setup_basic_ui)
        if not isinstance(layout, QVBoxLayout):
            return

        # Create modern header
        self.header = ModernHeaderWidget(container=self.container, state_manager=self.state_manager)
        self.header.notifications_requested.connect(self._on_header_notifications_clicked)

        # Insert header at the beginning
        layout.insertWidget(0, self.header)

    def init_sidebar(self) -> None:
        """Initialize sidebar widget"""
        if self.sidebar is not None:
            return  # Already initialized

        # Get content layout - find the content widget
        main_layout: Optional[QLayout] = self.centralWidget().layout()
        if main_layout is None:
            return

        content_widget = None

        # Find the content widget in the main layout
        for i in range(main_layout.count()):
            item = main_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if widget.layout() and widget.layout().count() > 0:
                    # This should be our content widget
                    content_widget = widget
                    break

        if content_widget is None:
            # Third-party imports
            from loguru import logger

            logger.error("Could not find content widget for sidebar initialization")
            return

        layout = content_widget.layout()
        if layout is None:
            # Third-party imports
            from loguru import logger

            logger.error("Content widget has no layout for sidebar initialization")
            return

        # Ensure it's a QHBoxLayout (should be based on setup_basic_ui)
        if not isinstance(layout, QHBoxLayout):
            # Third-party imports
            from loguru import logger

            logger.error("Content layout is not QHBoxLayout for sidebar initialization")
            return

        # Create sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.page_changed.connect(self.change_page)

        # Insert sidebar at the beginning of content layout
        layout.insertWidget(0, self.sidebar)

        # Remove fixed margin - let stretch factors handle spacing automatically
        if self.content_stack is not None:
            self.content_stack.setContentsMargins(0, 0, 0, 0)

            # Set stretch factors: sidebar fixed, content takes remaining space
            layout.setStretchFactor(self.sidebar, 0)  # Sidebar: fixed size
            layout.setStretchFactor(self.content_stack, 1)  # Content: expand to fill

    def init_dashboard_tab(self) -> None:
        """Initialize dashboard tab"""
        if "dashboard" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.dashboard_page = DashboardWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.dashboard_page)
        self.content_widgets["dashboard"] = self.dashboard_page

    def init_test_control_tab(self) -> None:
        """Initialize test control tab"""
        if "test_control" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.test_control_page = TestControlWidget(
            container=self.container,
            state_manager=self.state_manager,
            executor_thread=self.test_executor_thread,  # Pass executor thread for async operations
        )
        # Connect test control signals
        self.test_control_page.test_started.connect(self._on_test_started)
        self.test_control_page.test_stopped.connect(self._on_test_stopped)
        self.test_control_page.test_paused.connect(self._on_test_paused)
        self.test_control_page.robot_home_requested.connect(self._on_robot_home_requested)
        self.test_control_page.emergency_stop_requested.connect(self._on_emergency_stop_requested)

        # Set initial test status
        self.test_control_page.update_test_status("Ready", "status_ready", 0)

        self.content_stack.addWidget(self.test_control_page)
        self.content_widgets["test_control"] = self.test_control_page

    def init_robot_tab(self) -> None:
        """Initialize robot tab"""
        if "robot" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.robot_page = RobotControlWidget(
            container=self.container,
            state_manager=self.state_manager,
            executor_thread=self.test_executor_thread,  # ✅ Pass executor
        )
        self.content_stack.addWidget(self.robot_page)
        self.content_widgets["robot"] = self.robot_page
        self.pages["robot"] = self.robot_page  # Add to pages dictionary

    def init_mcu_tab(self) -> None:
        """Initialize MCU tab"""
        if "mcu" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.mcu_page = MCUControlWidget(
            container=self.container,
            state_manager=self.state_manager,
            executor_thread=self.test_executor_thread,  # ✅ Pass executor
        )
        self.content_stack.addWidget(self.mcu_page)
        self.content_widgets["mcu"] = self.mcu_page
        self.pages["mcu"] = self.mcu_page  # Add to pages dictionary

    def init_power_supply_tab(self) -> None:
        """Initialize Power Supply tab"""
        if "power_supply" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.power_supply_page = PowerSupplyControlWidget(
            container=self.container,
            state_manager=self.state_manager,
            executor_thread=self.test_executor_thread,  # ✅ Pass executor
        )
        self.content_stack.addWidget(self.power_supply_page)
        self.content_widgets["power_supply"] = self.power_supply_page
        self.pages["power_supply"] = self.power_supply_page  # Add to pages dictionary

    def init_digital_output_tab(self) -> None:
        """Initialize Digital Output tab"""
        if "digital_output" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.digital_output_page = DigitalOutputControlWidget(
            container=self.container,
            state_manager=self.state_manager,
            executor_thread=self.test_executor_thread,  # ✅ Pass executor
        )
        self.content_stack.addWidget(self.digital_output_page)
        self.content_widgets["digital_output"] = self.digital_output_page
        self.pages["digital_output"] = self.digital_output_page  # Add to pages dictionary

    def init_digital_input_tab(self) -> None:
        """Initialize Digital Input tab"""
        if "digital_input" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        # Local imports
        # Local application imports
        from ui.gui.widgets.content.digital_input import DigitalInputControlWidget

        self.digital_input_page = DigitalInputControlWidget(
            container=self.container,
            state_manager=self.state_manager,
            executor_thread=self.test_executor_thread,  # ✅ Pass executor
        )
        self.content_stack.addWidget(self.digital_input_page)
        self.content_widgets["digital_input"] = self.digital_input_page
        self.pages["digital_input"] = self.digital_input_page  # Add to pages dictionary

    def init_loadcell_tab(self) -> None:
        """Initialize Loadcell tab"""
        if "loadcell" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        # Local imports
        # Local application imports
        from ui.gui.widgets.content.loadcell import LoadcellControlWidget

        self.loadcell_page = LoadcellControlWidget(
            container=self.container,
            state_manager=self.state_manager,
            executor_thread=self.test_executor_thread,  # ✅ Pass executor
        )
        self.content_stack.addWidget(self.loadcell_page)
        self.content_widgets["loadcell"] = self.loadcell_page
        self.pages["loadcell"] = self.loadcell_page  # Add to pages dictionary

    def init_results_tab(self) -> None:
        """Initialize results tab"""
        if "results" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.results_page = ResultsWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.results_page)
        self.content_widgets["results"] = self.results_page

    def init_statistics_tab(self) -> None:
        """Initialize 3 statistics pages with enhanced shared header"""
        # Third-party imports
        from loguru import logger

        if "statistics_overview" in self.content_widgets:
            logger.info("⚠️ Statistics pages already initialized")
            return  # Already initialized

        if self.content_stack is None:
            logger.error("Content stack is None, cannot initialize statistics tab")
            return

        try:
            logger.info("🔧 Initializing 3 enhanced statistics pages...")

            # Import enhanced components
            # Third-party imports
            from PySide6.QtWidgets import QTabWidget

            # Local application imports
            from ui.gui.widgets.content.statistics.enhanced_header_controls import (
                EnhancedStatisticsHeaderControls,
            )
            from ui.gui.widgets.content.statistics.pages.new_advanced_page import (
                NewAdvancedPage,
            )
            from ui.gui.widgets.content.statistics.pages.new_analysis_page import (
                NewAnalysisPage,
            )
            from ui.gui.widgets.content.statistics.pages.new_overview_page import (
                NewOverviewPage,
            )

            # Get statistics service
            statistics_service = self.container.eol_statistics_service()
            logger.info("✅ Statistics service obtained")

            # Create main statistics container with shared header
            statistics_container = QWidget()
            container_layout = QVBoxLayout(statistics_container)
            container_layout.setSpacing(12)
            container_layout.setContentsMargins(12, 12, 12, 12)

            # Create enhanced shared header (sticky)
            self.statistics_header = EnhancedStatisticsHeaderControls(
                data_folder="logs/test_results/json"
            )
            container_layout.addWidget(self.statistics_header)
            logger.info("✅ Enhanced statistics header created with data scanning")

            # Create tab widget for 3 pages
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet(
                """
                QTabWidget::pane {
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    background-color: #1e1e1e;
                }
                QTabBar::tab {
                    background-color: rgba(45, 45, 45, 0.8);
                    color: #cccccc;
                    padding: 10px 20px;
                    margin-right: 4px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QTabBar::tab:selected {
                    background-color: rgba(33, 150, 243, 0.3);
                    color: #ffffff;
                    border-bottom: 2px solid #2196F3;
                }
                QTabBar::tab:hover {
                    background-color: rgba(255, 255, 255, 0.05);
                }
            """
            )

            # Create 3 pages
            self.overview_page = NewOverviewPage(statistics_service=statistics_service)
            self.analysis_page = NewAnalysisPage(statistics_service=statistics_service)
            self.advanced_page = NewAdvancedPage(statistics_service=statistics_service)

            # Add pages to tab widget
            tab_widget.addTab(self.overview_page, "📊 Overview")
            tab_widget.addTab(self.analysis_page, "📈 Analysis")
            tab_widget.addTab(self.advanced_page, "🔬 Advanced")

            container_layout.addWidget(tab_widget)

            # Connect header filter changes to all pages
            def on_filters_changed(filters):
                logger.info(f"Filters changed: {filters}")
                # Update all 3 pages with new filters
                # Third-party imports
                import asyncio

                if self.overview_page:
                    asyncio.create_task(self.overview_page.update_data(filters))
                if self.analysis_page:
                    asyncio.create_task(self.analysis_page.update_data(filters))
                if self.advanced_page:
                    asyncio.create_task(self.advanced_page.update_data(filters))

            self.statistics_header.filter_changed.connect(on_filters_changed)
            logger.info("✅ Filter change handler connected to all pages")

            # Add to content stack
            self.content_stack.addWidget(statistics_container)
            self.pages["statistics_overview"] = statistics_container
            self.content_widgets["statistics_overview"] = statistics_container

            logger.info("✅ All 3 statistics pages initialized successfully")
            logger.info("   📊 Overview: Quick Insights + Key Metrics + Performance")
            logger.info("   📈 Analysis: Charts + Heatmaps + Statistics Tables")
            logger.info("   🔬 Advanced: 3D/4D Visualizations")

        except Exception as e:
            logger.error(f"❌ Failed to initialize statistics pages: {e}")
            # Standard library imports
            import traceback

            traceback.print_exc()

    def init_logs_tab(self) -> None:
        """Initialize logs tab"""
        if "logs" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.logs_page = LogsWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.logs_page)
        self.content_widgets["logs"] = self.logs_page

    def init_about_tab(self) -> None:
        """Initialize about tab"""
        if "about" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.about_page = AboutWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.about_page)
        self.content_widgets["about"] = self.about_page

    def init_settings_tab(self) -> None:
        """Initialize settings tab"""
        if "settings" in self.content_widgets:
            return  # Already initialized

        if self.content_stack is None:
            return

        self.settings_page = SettingsWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.settings_page)
        self.content_widgets["settings"] = self.settings_page

    def finalize_initialization(self) -> None:
        """Finalize window initialization"""
        # Create self.pages dictionary for compatibility with existing code
        self.pages = {}

        # Map content_widgets to pages dictionary using proper attribute names
        for tab_name in self.content_widgets:
            if tab_name == "dashboard" and hasattr(self, "dashboard_page"):
                self.pages["dashboard"] = self.dashboard_page
            elif tab_name == "test_control" and hasattr(self, "test_control_page"):
                self.pages["test_control"] = self.test_control_page
            elif tab_name == "robot" and hasattr(self, "robot_page"):
                self.pages["robot"] = self.robot_page
            elif tab_name == "results" and hasattr(self, "results_page"):
                self.pages["results"] = self.results_page
            elif tab_name == "statistics" and hasattr(self, "statistics_page"):
                self.pages["statistics"] = self.statistics_page
            elif tab_name == "logs" and hasattr(self, "logs_page"):
                self.pages["logs"] = self.logs_page
            elif tab_name == "settings" and hasattr(self, "settings_page"):
                self.pages["settings"] = self.settings_page
            elif tab_name == "about" and hasattr(self, "about_page"):
                self.pages["about"] = self.about_page

        # Setup status bar and update timer
        self.setup_status_bar()
        self.setup_update_timer()

        # Set initial page if sidebar is initialized
        if self.sidebar is not None and "dashboard" in self.content_widgets:
            self.change_page("dashboard")

    def setup_ui(self) -> None:
        """Setup the main window UI"""
        # Window properties
        self.setWindowTitle("")
        self.setMinimumSize(1200, 1100)  # Increased height for better content visibility
        self.resize(1400, 1200)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout (vertical to accommodate header)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Modern Header
        self.header = ModernHeaderWidget(container=self.container, state_manager=self.state_manager)
        self.header.notifications_requested.connect(self._on_header_notifications_clicked)
        main_layout.addWidget(self.header)

        # Content area layout (sidebar + main content)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 10, 0, 0)  # 10px top margin for alignment

        # Create sidebar container for top alignment
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.page_changed.connect(self.change_page)
        self.sidebar.settings_clicked.connect(self._on_header_settings_clicked)

        # Add sidebar to container with top alignment
        sidebar_layout.addWidget(self.sidebar, 0, Qt.AlignmentFlag.AlignTop)
        sidebar_layout.addStretch(1)  # Push sidebar to top

        # Set container width to match sidebar (increased to 220px for modern design)
        sidebar_container.setFixedWidth(220)

        # Content stack with explicit sizing constraints
        self.content_stack = QStackedWidget()
        # Enforce clear separation between sidebar and content
        self.content_stack.setContentsMargins(10, 0, 0, 0)  # 10px left margin for separation

        # Set explicit minimum width to prevent overlap
        self.content_stack.setMinimumWidth(400)  # Ensure content has minimum space

        # Add widgets to layout
        content_layout.addWidget(sidebar_container)
        content_layout.addWidget(self.content_stack)

        # Set stretch factors: sidebar fixed (0), content expandable (1)
        content_layout.setStretchFactor(sidebar_container, 0)  # Fixed: 200px
        content_layout.setStretchFactor(self.content_stack, 1)  # Expandable: remaining space

        # Add content area to main layout with stretch factor to take remaining space
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(
            content_widget, 1
        )  # Stretch factor 1: take all remaining vertical space

        # Create and add content pages
        self.create_content_pages()

        # Set initial page
        self.change_page("dashboard")

    def create_content_pages(self) -> None:
        """Create and add content pages to stack"""
        if self.content_stack is None:
            return

        # Dashboard page
        self.dashboard_page = DashboardWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.dashboard_page)

        # Test Control page
        self.test_control_page = TestControlWidget(
            container=self.container,
            state_manager=self.state_manager,
            executor_thread=self.test_executor_thread,  # Pass executor thread for async operations
        )
        # Connect test control signals
        self.test_control_page.test_started.connect(self._on_test_started)
        self.test_control_page.test_stopped.connect(self._on_test_stopped)
        self.test_control_page.test_paused.connect(self._on_test_paused)
        self.test_control_page.robot_home_requested.connect(self._on_robot_home_requested)
        self.test_control_page.emergency_stop_requested.connect(self._on_emergency_stop_requested)

        # Set initial test status
        self.test_control_page.update_test_status("Ready", "status_ready", 0)

        self.content_stack.addWidget(self.test_control_page)

        # Results page
        self.results_page = ResultsWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.results_page)

        # Statistics page - Note: StatisticsWidget doesn't exist as a single widget
        # Statistics functionality is now split into multiple sub-pages (see init_statistics_tab)
        # This placeholder is kept for compatibility but statistics pages are created separately
        # Third-party imports
        from loguru import logger

        logger.info("ℹ️ Statistics pages handled separately via init_statistics_tab()")
        placeholder = QLabel("Statistics - Use sidebar navigation to access statistics pages")
        self.statistics_page = placeholder
        self.content_stack.addWidget(placeholder)

        # Robot page
        self.robot_page = RobotControlWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.robot_page)

        # Logs page
        self.logs_page = LogsWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.logs_page)

        # About page
        self.about_page = AboutWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.about_page)

        # Settings page
        self.settings_page = SettingsWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.settings_page)

        # Store pages for easy access
        self.pages = {
            "dashboard": self.dashboard_page,
            "test_control": self.test_control_page,
            "results": self.results_page,
            "statistics": self.statistics_page,
            "robot": self.robot_page,
            "logs": self.logs_page,
            "about": self.about_page,
            "settings": self.settings_page,
        }

    def setup_status_bar(self) -> None:
        """Setup status bar with system information"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status indicators
        self.system_status_label = QLabel("🟢 System Ready")
        self.connection_status_label = QLabel("📡 5/5 Connected")
        self.test_status_label = QLabel("⚡ Test: IDLE")
        self.time_label = QLabel("🕐 --:--:--")
        self.progress_label = QLabel("📊 0/0 Done")

        # Add to status bar (left side)
        self.status_bar.addWidget(self.system_status_label)
        self.status_bar.addWidget(self._create_separator())
        self.status_bar.addWidget(self.connection_status_label)
        self.status_bar.addWidget(self._create_separator())
        self.status_bar.addWidget(self.test_status_label)
        self.status_bar.addWidget(self._create_separator())
        self.status_bar.addWidget(self.time_label)
        self.status_bar.addWidget(self._create_separator())
        self.status_bar.addWidget(self.progress_label)

        # Add zoom control (right side, permanent)
        # Local application imports
        from ui.gui.widgets.footer import ZoomControl

        self.zoom_control = ZoomControl(container=self.container)
        self.zoom_control.zoom_changed.connect(self._on_zoom_changed)
        self.status_bar.addPermanentWidget(self._create_separator())
        self.status_bar.addPermanentWidget(self.zoom_control)

        # Style status bar - Modern Material Design 3
        self.status_bar.setStyleSheet(
            """
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                color: #ffffff;
                border-top: 1px solid rgba(33, 150, 243, 0.3);
                padding: 8px 12px;
                min-height: 32px;
            }
            QStatusBar::item {
                border: none;
            }
            QLabel {
                padding: 4px 12px;
                font-size: 13px;
                font-weight: 500;
                color: #cccccc;
                background-color: transparent;
                border-radius: 8px;
            }
            QLabel:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """
        )

    def setup_update_timer(self) -> None:
        """Setup timer for periodic UI updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status_bar)
        self.update_timer.start(1000)  # Update every second

    def _create_separator(self) -> QFrame:
        """Create a modern status bar separator"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        separator.setStyleSheet(
            """
            QFrame {
                color: rgba(255, 255, 255, 0.1);
                background-color: rgba(255, 255, 255, 0.1);
                max-width: 1px;
                margin: 4px 8px;
            }
        """
        )
        return separator

    def change_page(self, page_id: str) -> None:
        """Change to a different content page"""
        # Third-party imports
        from loguru import logger

        logger.info(f"📄 change_page called with page_id: {page_id}")

        # Lazy load statistics sub-pages if needed
        if page_id.startswith("statistics"):
            if "statistics_overview" not in self.pages:
                logger.info("⚙️ Lazy loading statistics sub-pages...")
                self.init_statistics_tab()
        # Lazy load robot page if needed
        elif page_id == "robot":
            if "robot" not in self.pages:
                logger.info("⚙️ Lazy loading robot page...")
                self.init_robot_tab()
                # ✅ Sync initial hardware status immediately after creating page
                self._sync_hardware_page_status("robot")
        # Lazy load MCU page if needed
        elif page_id == "mcu":
            if "mcu" not in self.pages:
                logger.info("⚙️ Lazy loading MCU page...")
                self.init_mcu_tab()
                # ✅ Sync initial hardware status immediately after creating page
                self._sync_hardware_page_status("mcu")
        # Lazy load Power Supply page if needed
        elif page_id == "power_supply":
            if "power_supply" not in self.pages:
                logger.info("⚙️ Lazy loading Power Supply page...")
                self.init_power_supply_tab()
                # ✅ Sync initial hardware status immediately after creating page
                self._sync_hardware_page_status("power_supply")
        # Lazy load Power Supply page if needed
        elif page_id == "power_supply":
            if "power_supply" not in self.pages:
                logger.info("⚙️ Lazy loading Power Supply page...")
                self.init_power_supply_tab()
                # ✅ Sync initial hardware status immediately after creating page
                self._sync_hardware_page_status("power_supply")
        # Lazy load Digital Output page if needed
        elif page_id == "digital_output":
            if "digital_output" not in self.pages:
                logger.info("⚙️ Lazy loading Digital Output page...")
                self.init_digital_output_tab()
                # ✅ Sync initial hardware status immediately after creating page
                self._sync_hardware_page_status("digital_output")
        # Lazy load Digital Input page if needed
        elif page_id == "digital_input":
            if "digital_input" not in self.pages:
                logger.info("⚙️ Lazy loading Digital Input page...")
                self.init_digital_input_tab()
                # ✅ Sync initial hardware status immediately after creating page
                self._sync_hardware_page_status("digital_input")
        # Lazy load Loadcell page if needed
        elif page_id == "loadcell":
            if "loadcell" not in self.pages:
                logger.info("⚙️ Lazy loading Loadcell page...")
                self.init_loadcell_tab()
                # ✅ Sync initial hardware status immediately after creating page
                self._sync_hardware_page_status("loadcell")
        # Standard lazy loading for other pages
        elif page_id not in self.pages:
            logger.info(f"⚙️ Lazy loading {page_id} page...")
            # Other lazy loading logic here if needed

        if page_id in self.pages:
            page_widget = self.pages[page_id]
            logger.info(f"✅ Found page widget: {type(page_widget).__name__}")

            if self.content_stack is not None:
                # Use smooth transition if manager is available
                if self.page_transition_manager:
                    self.page_transition_manager.transition_to(page_widget)
                else:
                    self.content_stack.setCurrentWidget(page_widget)

            # Update sidebar
            if self.sidebar is not None:
                # No need to toggle submenu - Statistics now has 3 tabs inside
                self.sidebar.set_current_page(page_id)

            # Test control page - no auto-focus needed (popup-based serial number)
        else:
            logger.error(f"❌ Page '{page_id}' not found in self.pages!")

    def update_status_bar(self) -> None:
        """Update status bar information"""
        # Standard library imports
        from datetime import datetime

        # Update time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(f"🕐 {current_time}")

        # Update header system status
        # TODO: Get actual system status from state manager
        # For now, keep the header status synchronized

    def _on_zoom_changed(self, new_scale: float) -> None:
        """Handle zoom level changes - requires restart for complete scaling"""
        # Third-party imports
        from loguru import logger

        logger.info(f"Zoom changed to {int(new_scale * 100)}%")

        # Show restart dialog
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Restart Required")
        msg_box.setText(f"UI Zoom changed to {int(new_scale * 100)}%")
        msg_box.setInformativeText(
            "The application must be restarted for the zoom change to take effect.\n\n"
            "Would you like to restart now?"
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        msg_box.setStyleSheet(
            """
            QMessageBox {
                background-color: #1e1e1e;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2196F3;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 6px 20px;
                min-width: 80px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
        """
        )

        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            # Restart application
            logger.info("Restarting application to apply zoom changes")
            # Standard library imports
            import os
            import sys

            # Third-party imports
            from PySide6.QtCore import QCoreApplication

            # Get the current executable/script path
            if getattr(sys, "frozen", False):
                # Running as compiled executable
                executable = sys.executable
            else:
                # Running as script
                executable = sys.executable

            QCoreApplication.quit()
            os.execv(executable, [executable] + sys.argv)

    def closeEvent(self, event) -> None:
        """Handle window close event with comprehensive cleanup"""
        # Third-party imports
        from loguru import logger

        logger.info("🚪 Application closing - cleaning up resources...")

        # 1. Disconnect ALL signals to prevent memory leaks
        try:
            logger.info("🔌 Disconnecting signals...")

            # Sidebar signals
            if hasattr(self, "sidebar") and self.sidebar is not None:
                try:
                    self.sidebar.page_changed.disconnect()
                    self.sidebar.settings_clicked.disconnect()
                except (RuntimeError, AttributeError):
                    pass

            # Header signals
            if hasattr(self, "header") and self.header is not None:
                try:
                    self.header.notifications_requested.disconnect()
                except (RuntimeError, AttributeError):
                    pass

            # Test control page signals
            if hasattr(self, "test_control_page") and self.test_control_page is not None:
                try:
                    self.test_control_page.test_started.disconnect()
                    self.test_control_page.test_stopped.disconnect()
                    self.test_control_page.test_paused.disconnect()
                    self.test_control_page.robot_home_requested.disconnect()
                    self.test_control_page.emergency_stop_requested.disconnect()
                except (RuntimeError, AttributeError):
                    pass

            # Zoom control signals
            if hasattr(self, "zoom_control") and self.zoom_control is not None:
                try:
                    self.zoom_control.zoom_changed.disconnect()
                except (RuntimeError, AttributeError):
                    pass

            # Robot home thread signals
            if hasattr(self, "robot_home_thread") and self.robot_home_thread:
                try:
                    self.robot_home_thread.started.disconnect()
                    self.robot_home_thread.progress.disconnect()
                    self.robot_home_thread.completed.disconnect()
                except (RuntimeError, AttributeError):
                    pass

            # Test executor thread signals
            if hasattr(self, "test_executor_thread") and self.test_executor_thread:
                # Disconnect each signal individually with error handling
                signals_to_disconnect = [
                    "test_started",
                    "test_progress",
                    "test_result",
                    "test_completed",
                    "test_error",
                    "log_message",
                ]
                for signal_name in signals_to_disconnect:
                    try:
                        signal = getattr(self.test_executor_thread, signal_name, None)
                        if signal:
                            signal.disconnect()
                    except (RuntimeError, TypeError, AttributeError):
                        # Signal not connected or already disconnected - safe to ignore
                        pass

            logger.info("✅ All signals disconnected")

        except Exception as e:
            logger.warning(f"Error disconnecting signals (non-critical): {e}")

        # 2. Clean up graphics effects to prevent memory leaks
        if hasattr(self, "content_stack") and self.content_stack is not None:
            try:
                logger.info("🎨 Cleaning up graphics effects...")
                # Narrow type for Pylance - content_stack is guaranteed non-None here
                content_stack = self.content_stack
                for i in range(content_stack.count()):
                    widget = content_stack.widget(i)
                    if widget:
                        widget.setGraphicsEffect(None)  # type: ignore[arg-type]  # PySide6 accepts None
                logger.info("✅ Graphics effects cleaned")
            except Exception as e:
                logger.debug(f"Graphics effect cleanup error: {e}")

        # 3. Stop TestExecutorThread
        if hasattr(self, "test_executor_thread") and self.test_executor_thread:
            logger.info("🛑 Stopping TestExecutorThread...")
            self.test_executor_thread.stop()
            if self.test_executor_thread.isRunning():
                self.test_executor_thread.wait(2000)  # Wait max 2 seconds
                if self.test_executor_thread.isRunning():
                    logger.warning("TestExecutorThread did not stop gracefully")
                    self.test_executor_thread.terminate()
            logger.info("✅ TestExecutorThread stopped")

        # 4. Stop RobotHomeThread
        if hasattr(self, "robot_home_thread") and self.robot_home_thread:
            if self.robot_home_thread.isRunning():
                logger.info("🛑 Stopping RobotHomeThread...")
                self.robot_home_thread.wait(1000)  # Wait max 1 second
                if self.robot_home_thread.isRunning():
                    logger.warning("RobotHomeThread did not stop gracefully")
                    self.robot_home_thread.terminate()
                logger.info("✅ RobotHomeThread stopped")

        logger.info("🚪 All resources cleaned up - closing application")
        event.accept()

    # Header Signal Handlers
    # ============================================================================

    def _on_header_settings_clicked(self) -> None:
        """Handle settings button click from header"""
        # Navigate to settings page
        self.change_page("settings")

    def _on_header_notifications_clicked(self) -> None:
        """Handle notifications button click from header"""
        # Show notifications dialog (placeholder)
        QMessageBox.information(
            self,
            "Notifications",
            "No new notifications.\n\nSystem notifications and alerts will appear here.",
        )

    # Test Control Signal Handlers
    # ============================================================================

    def _on_test_started(self) -> None:
        """Handle test start request"""
        # Third-party imports
        from loguru import logger

        # Validate required widgets exist
        if not self.test_control_page or not self.results_page:
            logger.error("Test control or results page not initialized")
            return

        try:
            # ✅ Check if a test is already executing (not if thread is running)
            if self.test_executor_thread and self.test_executor_thread.is_test_running:
                logger.warning("Test start blocked - another test is currently running")
                self.test_control_page.update_test_status(
                    "Test already running. Please wait or stop first.", "⚠️"
                )
                return

            # Mutex check: Prevent test start if robot home is running
            if (
                hasattr(self, "robot_home_thread")
                and self.robot_home_thread
                and self.robot_home_thread.isRunning()
            ):
                logger.warning("Test start blocked - robot home is currently running")
                self.test_control_page.update_test_status(
                    "Test unavailable during robot home", "status_warning"
                )
                self.state_manager.add_log_message(
                    "WARNING", "TEST", "Test start blocked - robot home currently running"
                )
                return

            # Get serial number and test sequence from test control widget
            if not self.test_control_page.sequence_combo:
                self.test_control_page.update_test_status(
                    "Test controls not initialized", "status_error"
                )
                return

            # Get serial number from popup dialog (validation already done in dialog)
            serial_number = self.test_control_page.get_current_serial_number()
            test_sequence = self.test_control_page.sequence_combo.currentText()

            logger.info(f"Starting {test_sequence} for serial number: {serial_number}")

            # Reload configuration before starting test to pick up any changes from Settings
            if hasattr(self.container, "reload_configuration"):
                logger.info("🔄 Reloading configuration before test start...")
                reload_success = self.container.reload_configuration()
                if reload_success:
                    logger.info("✅ Configuration reloaded successfully")
                    self.state_manager.add_log_message(
                        "INFO", "CONFIG", "Configuration reloaded from files"
                    )
                else:
                    logger.warning("⚠️ Configuration reload failed, using cached configuration")
                    self.state_manager.add_log_message(
                        "WARNING", "CONFIG", "Configuration reload failed, using cached values"
                    )

            # Clear previous test results from Results table and chart
            if self.results_page.results_table:
                self.results_page.results_table.clear_results()
            if self.results_page.temp_force_chart:
                self.results_page.temp_force_chart.clear_data()

            # Clear live logs when starting a new test
            if (
                self.logs_page
                and hasattr(self.logs_page, "log_viewer")
                and self.logs_page.log_viewer
            ):
                self.logs_page.log_viewer.clear_logs()
            if (
                self.test_control_page
                and hasattr(self.test_control_page, "log_viewer")
                and self.test_control_page.log_viewer
            ):
                self.test_control_page.log_viewer.clear_logs()
            logger.info("Previous test results and live logs cleared. Starting new test...")
            self.state_manager.add_log_message(
                "INFO", "TEST", "Previous test results and logs cleared"
            )

            # Update GUI state
            self.state_manager.set_system_status("Testing")
            self.state_manager.add_log_message(
                "INFO", "TEST", f"Starting {test_sequence} for SN: {serial_number}"
            )

            # Update header status
            if self.header is not None:
                self.header.set_system_status("Testing", "testing")

            # Update test control status
            self.test_control_page.update_test_status(
                f"Running {test_sequence}...", "status_loading", 0
            )

            # Update button states
            self._set_test_running_state(True)

            # Start test execution in background
            self._start_test_execution(test_sequence, serial_number)

        except Exception as e:
            logger.error(f"Failed to start test: {e}")
            self.test_control_page.stop_indeterminate_progress()
            self.test_control_page.update_test_status(
                f"Failed to start test: {str(e)}", "status_error"
            )
            self._set_test_running_state(False)

    def _on_test_stopped(self) -> None:
        """Handle test stop request"""
        # Third-party imports
        from loguru import logger

        if not self.test_control_page:
            return

        logger.info("Test stop requested")
        self.state_manager.add_log_message("INFO", "TEST", "Test stop requested by user")
        self.state_manager.set_system_status("Stopping")

        # Stop the test thread if it's running
        if self.test_executor_thread and self.test_executor_thread.isRunning():
            self.test_executor_thread.stop_test()
            self.test_executor_thread.quit()
            self.test_executor_thread.wait(5000)  # Wait up to 5 seconds
            logger.info("Test thread stopped")

        # Update test control status
        self.test_control_page.update_test_status("Test Stopped", "stop", 0)

        # Reset GUI state
        self._set_test_running_state(False)
        self.state_manager.set_system_status("Ready")

        # Update header status
        if self.header is not None:
            self.header.set_system_status("Ready", "ready")

    def _on_test_paused(self) -> None:
        """Handle test pause request"""
        # Third-party imports
        from loguru import logger

        if not self.test_control_page:
            return

        logger.info("Test pause requested")
        self.state_manager.add_log_message("INFO", "TEST", "Test pause requested by user")

        # TODO: Implement test pause logic
        # Update test control status
        self.test_control_page.update_test_status("Test Paused", "⏸️")

    def _on_robot_home_requested(self) -> None:
        """Handle robot home request"""
        # Third-party imports
        from loguru import logger

        if not self.test_control_page:
            return

        logger.critical("🔥 DEBUG: _on_robot_home_requested method called!")
        try:
            # Mutex check: Prevent robot home if test is running
            if self.test_executor_thread and self.test_executor_thread.isRunning():
                logger.warning("Robot home blocked - test is currently running")
                self.test_control_page.update_test_status(
                    "Robot home unavailable during test", "status_warning"
                )
                self.state_manager.add_log_message(
                    "WARNING", "ROBOT", "Robot home blocked - test currently running"
                )
                return

            # Mutex check: Prevent multiple robot home operations
            if (
                hasattr(self, "robot_home_thread")
                and self.robot_home_thread
                and self.robot_home_thread.isRunning()
            ):
                logger.warning("Robot home already in progress")
                self.test_control_page.update_test_status(
                    "Robot home already in progress", "status_warning"
                )
                self.state_manager.add_log_message(
                    "WARNING", "ROBOT", "Robot home already in progress"
                )
                return

            logger.info("Robot home requested")
            self.state_manager.add_log_message("INFO", "ROBOT", "Robot home requested by user")

            # Update test control status to show homing in progress
            self.test_control_page.update_test_status("Homing Robot...", "status_homing")

            # Execute robot homing using QTimer for proper Qt-asyncio integration
            logger.debug("🔥 DEBUG: About to call _execute_robot_home_async()")
            try:
                self._execute_robot_home_async()
                logger.debug("🔥 DEBUG: _execute_robot_home_async() call completed")
            except Exception as async_error:
                logger.error(f"🔥 DEBUG: _execute_robot_home_async() failed: {async_error}")
                self.test_control_page.update_test_status("Robot Home Setup Failed", "status_error")
                raise

        except Exception as e:
            logger.error(f"Robot home failed: {e}")
            self.test_control_page.stop_indeterminate_progress()
            self.test_control_page.update_test_status("Robot Home Failed", "status_error")

    def _on_emergency_stop_requested(self) -> None:
        """Handle emergency stop request"""
        # Third-party imports
        from loguru import logger

        if not self.test_control_page:
            return

        logger.critical("EMERGENCY STOP REQUESTED")

        # PRIORITY 1: Immediate UI updates (must happen first)
        def immediate_ui_updates():
            """Execute immediate UI updates with high priority"""
            logger.info("Executing immediate UI updates for Emergency Stop")

            # Update test control status immediately for user feedback
            if self.test_control_page:
                self.test_control_page.update_test_status(
                    "EMERGENCY STOP ACTIVATED! - HOME REQUIRED", "status_emergency"
                )

            # Update header status
            if self.header is not None:
                self.header.set_system_status("EMERGENCY STOP", "emergency")

            # Set emergency stop flag and disable START TEST button
            self.emergency_stop_active = True
            logger.info("Emergency stop state activated - START TEST button disabled")
            if self.test_control_page:
                self.test_control_page.disable_start_button()
                logger.info("START TEST button disabled successfully")

        # Execute UI updates immediately
        immediate_ui_updates()

        # PRIORITY 2: Stop running test thread (after UI updates)
        def stop_test_thread():
            """Stop running test thread"""
            if (
                hasattr(self, "test_executor_thread")
                and self.test_executor_thread
                and self.test_executor_thread.isRunning()
            ):
                logger.info("Stopping running test thread...")
                self.test_executor_thread.stop_test()
                self.test_executor_thread.wait(1000)  # Wait up to 1 second
                logger.info("Test thread stopped")

            # PRIORITY 3: Execute hardware emergency stop (after thread stop)
            self._execute_emergency_stop_async()

        # Use QTimer.singleShot to ensure proper event loop handling
        QTimer.singleShot(0, stop_test_thread)

    def _execute_robot_home_async(self) -> None:
        """Execute robot home operation using QThread (non-blocking)"""
        # Third-party imports
        from loguru import logger

        # Check if robot home is already running
        if self.robot_home_thread and self.robot_home_thread.isRunning():
            logger.warning("Robot home already running")
            return

        logger.info("Starting robot home thread...")

        # Create fresh container for robot home to avoid event loop conflicts
        # Local application imports

        fresh_container = ApplicationContainer.create()

        # Create and configure robot home thread with fresh container
        self.robot_home_thread = RobotHomeThread(fresh_container)

        # Connect signals
        self.robot_home_thread.started.connect(self._on_robot_home_started)
        self.robot_home_thread.progress.connect(self._on_robot_home_progress)
        self.robot_home_thread.completed.connect(self._on_robot_home_completed)

        # Start the thread
        self.robot_home_thread.start()

    def _on_robot_home_started(self) -> None:
        """Handle robot home thread started"""
        # Third-party imports
        from loguru import logger

        if not self.test_control_page:
            return

        logger.info("Robot home operation started in background thread")
        self.test_control_page.update_test_status("Robot Homing...", "status_running")

        # Mutual exclusion: Disable START TEST button during robot home
        self.test_control_page.disable_start_button()

    def _on_robot_home_progress(self, message: str) -> None:
        """Handle robot home progress updates"""
        # Third-party imports
        from loguru import logger

        logger.info(f"Robot home progress: {message}")
        self.state_manager.add_log_message("INFO", "ROBOT", message)

    def _on_robot_home_completed(self, success: bool, message: str) -> None:
        """Handle robot home completion"""
        # Third-party imports
        from loguru import logger

        if not self.test_control_page:
            return

        # Stop progress bar animation
        if hasattr(self.test_control_page, "handle_robot_home_completed"):
            self.test_control_page.handle_robot_home_completed(success)

        if success:
            logger.info(f"✅ {message}")
            self.state_manager.add_log_message("INFO", "ROBOT", message)
            self.test_control_page.update_test_status("Robot Home Completed", "status_success")

            # Update header to show "Robot Homed" status
            if self.header is not None:
                self.header.set_system_status("Robot Homed", "homed")
                logger.info("Header status updated to 'Robot Homed'")

            # Clear emergency stop state and re-enable START TEST button
            self.emergency_stop_active = False
            self.test_control_page.enable_start_button()
            logger.info(
                "Emergency stop cleared - START TEST button re-enabled after successful robot home"
            )

        else:
            logger.error(f"❌ {message}")
            self.state_manager.add_log_message("ERROR", "ROBOT", message)
            self.test_control_page.stop_indeterminate_progress()
            self.test_control_page.update_test_status("Robot Home Failed", "status_error")

            # Re-enable START TEST button even on failure (mutual exclusion complete)
            # but respect emergency stop state
            if not self.emergency_stop_active:
                self.test_control_page.enable_start_button()

        # Clean up thread
        if self.robot_home_thread:
            self.robot_home_thread.deleteLater()
            self.robot_home_thread = None

    def _execute_emergency_stop_async(self) -> None:
        """Execute emergency stop asynchronously using QTimer"""
        # Third-party imports
        import asyncio
        from loguru import logger

        try:
            # Create a single-shot timer to execute the async function
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: asyncio.ensure_future(self._run_emergency_stop()))
            timer.start(10)  # Start after 10ms
        except Exception as e:
            logger.error(f"Failed to setup emergency stop async execution: {e}")
            # Fallback to UI-only emergency stop
            self.state_manager.add_log_message(
                "ERROR", "EMERGENCY", f"Emergency stop setup failed: {str(e)}"
            )
            self.state_manager.set_system_status("EMERGENCY STOP - ERROR")

    async def _run_emergency_stop(self) -> None:
        """Actually run the emergency stop procedure"""
        # Third-party imports
        from loguru import logger

        try:
            await self.state_manager.execute_emergency_stop()
            logger.info("Emergency stop completed successfully from GUI")
        except Exception as e:
            logger.error(f"Emergency stop execution failed: {e}")
            self.state_manager.add_log_message(
                "ERROR", "EMERGENCY", f"Emergency stop failed: {str(e)}"
            )
            self.state_manager.set_system_status("EMERGENCY STOP - ERROR")

    def _start_test_execution(self, test_sequence: str, serial_number: str) -> None:
        """Start test execution in background"""
        # Third-party imports
        from loguru import logger

        try:
            # Use the same container instance to maintain GUI State Manager connection
            # DO NOT create fresh container as it loses GUI State Manager override
            logger.info(f"Using main container ID: {id(self.container)} for test execution")

            # Verify GUI State Manager is still connected in main container
            hardware_facade = self.container.hardware_service_facade()
            # pylint: disable=protected-access  # Intentional access for verification
            gui_manager_connected = (
                hasattr(hardware_facade, "_gui_state_manager")
                and hardware_facade._gui_state_manager is not None
            )
            logger.info(f"Main container GUI State Manager connected: {gui_manager_connected}")

            if not gui_manager_connected:
                logger.warning(
                    "GUI State Manager not connected in main container - applying runtime injection"
                )
                hardware_facade._gui_state_manager = self.state_manager
                logger.info("Runtime GUI State Manager injection applied to main container")
            # pylint: enable=protected-access

            # ✅ Submit test to persistent TestExecutorThread (no new thread creation)
            # Connect thread signals if not already connected
            if not self._test_signals_connected:
                logger.info("🔗 Connecting test thread signals for the first time...")
                self._connect_test_thread_signals()
                self._test_signals_connected = True
                logger.info("✅ Test thread signals connected successfully")

            # Submit test task to executor
            self.test_executor_thread.submit_test(test_sequence, serial_number)
            logger.info(f"Test submitted to TestExecutorThread: {test_sequence}")

        except Exception as e:
            logger.error(f"Failed to start test execution thread: {e}")
            self.state_manager.add_log_message("ERROR", "TEST", f"Failed to start test: {str(e)}")
            if self.test_control_page:
                self.test_control_page.stop_indeterminate_progress()
                self.test_control_page.update_test_status(
                    f"Test start failed: {str(e)}", "status_error"
                )
            self._set_test_running_state(False)

    def _connect_test_thread_signals(self) -> None:
        """Connect test thread signals to GUI handlers"""
        if self.test_executor_thread:
            self.test_executor_thread.test_started.connect(self._on_thread_test_started)
            self.test_executor_thread.test_progress.connect(self._on_thread_test_progress)
            self.test_executor_thread.test_result.connect(self._on_thread_test_result)
            self.test_executor_thread.test_completed.connect(self._on_thread_test_completed)
            self.test_executor_thread.test_error.connect(self._on_thread_test_error)
            self.test_executor_thread.log_message.connect(self._on_thread_log_message)

            # ✅ Connect hardware status signal for syncing Hardware pages
            self.test_executor_thread.hardware_status_changed.connect(
                self._on_hardware_status_changed
            )

    def _on_hardware_status_changed(self, hardware_name: str, is_connected: bool) -> None:
        """
        Handle hardware status changes from TestExecutorThread.

        When test execution connects/disconnects hardware, this handler updates
        the corresponding Hardware page's state to keep button states in sync.

        Args:
            hardware_name: Name of hardware ("robot", "mcu", etc.)
            is_connected: Current connection status
        """
        # Third-party imports
        from loguru import logger

        logger.debug(f"Hardware status changed: {hardware_name} = {is_connected}")

        # Update Robot page state
        if hardware_name == "robot" and hasattr(self, "robot_page") and self.robot_page is not None:
            self.robot_page.robot_state.set_connected(is_connected)
            logger.debug(f"Robot page state updated: connected={is_connected}")

        # Update MCU page state
        elif hardware_name == "mcu" and hasattr(self, "mcu_page") and self.mcu_page is not None:
            self.mcu_page.mcu_state.set_connected(is_connected)
            logger.debug(f"MCU page state updated: connected={is_connected}")

    def _sync_hardware_page_status(self, hardware_name: str) -> None:
        """
        Sync hardware page GUI state with current hardware connection status.

        Called when a hardware page is lazy-loaded to ensure it displays
        the correct initial button states (especially if hardware is already connected).

        This is a synchronous GUI-only update - it doesn't perform actual hardware operations.

        Args:
            hardware_name: Name of hardware page ("robot", "mcu", etc.)
        """
        # Third-party imports
        from loguru import logger

        logger.info(f"🔄 Syncing initial GUI state for {hardware_name} page...")

        try:
            # Get hardware facade to check connection status
            hardware_facade = self.container.hardware_service_facade()

            # Synchronously check if hardware is connected (mock services return immediately)
            # Real hardware services may cache connection status, so this is safe
            if (
                hardware_name == "robot"
                and hasattr(self, "robot_page")
                and self.robot_page is not None
            ):
                # Check if robot service thinks it's connected
                # Note: For mock hardware, this will return False unless explicitly connected
                # For real hardware during test, this should return True if test connected it
                try:
                    # Third-party imports
                    import asyncio

                    # Create a simple async check
                    loop = asyncio.new_event_loop()
                    is_connected = loop.run_until_complete(
                        hardware_facade.robot_service.is_connected()
                    )
                    loop.close()

                    logger.info(f"🔌 Robot hardware connection status: {is_connected}")
                    # Update Robot page state directly
                    self.robot_page.robot_state.set_connected(is_connected)
                    logger.info(f"✅ Robot page GUI state updated: connected={is_connected}")
                except Exception as e:
                    logger.warning(f"Could not check robot connection status: {e}")

            elif hardware_name == "mcu" and hasattr(self, "mcu_page") and self.mcu_page is not None:
                try:
                    # Third-party imports
                    import asyncio

                    loop = asyncio.new_event_loop()
                    is_connected = loop.run_until_complete(
                        hardware_facade.mcu_service.is_connected()
                    )
                    loop.close()

                    logger.info(f"🔌 MCU hardware connection status: {is_connected}")
                    # Update MCU page state directly
                    self.mcu_page.mcu_state.set_connected(is_connected)
                    logger.info(f"✅ MCU page GUI state updated: connected={is_connected}")
                except Exception as e:
                    logger.warning(f"Could not check MCU connection status: {e}")

        except Exception as e:
            logger.warning(f"Failed to sync {hardware_name} GUI state: {e}")

    def _set_test_running_state(self, running: bool) -> None:
        """Set GUI state for test running/stopped"""
        if not self.test_control_page:
            return

        # Update test control buttons
        if hasattr(self.test_control_page, "start_btn") and self.test_control_page.start_btn:
            # Only enable start button if not running AND not in emergency stop state
            should_enable_start = not running and not self.emergency_stop_active
            self.test_control_page.start_btn.setEnabled(should_enable_start)
        if hasattr(self.test_control_page, "stop_btn") and self.test_control_page.stop_btn:
            self.test_control_page.stop_btn.setEnabled(running)
        if hasattr(self.test_control_page, "pause_btn") and self.test_control_page.pause_btn:
            self.test_control_page.pause_btn.setEnabled(running)

        # Mutual exclusion: Disable HOME button during test execution
        if running:
            self.test_control_page.disable_home_button()
        else:
            self.test_control_page.enable_home_button()

    # Test Thread Signal Handlers
    # ============================================================================

    def _on_thread_test_started(self, test_name: str) -> None:
        """Handle test started from thread"""
        # Local application imports
        from ui.gui.services.gui_state_manager import TestProgress

        progress = TestProgress(
            current_test=test_name,
            progress_percent=0,
            current_cycle=0,
            total_cycles=10,  # Default, will be updated
            status="Starting...",
            elapsed_time="00:00:00",
            estimated_remaining="--:--:--",
        )
        self.state_manager.update_test_progress(progress)

    def _on_thread_test_progress(self, current_cycle: int, total_cycles: int, status: str) -> None:
        """Handle test progress from thread"""
        # Local application imports
        from ui.gui.services.gui_state_manager import TestProgress

        if not self.test_control_page:
            return

        progress_percent = int((current_cycle / total_cycles) * 100) if total_cycles > 0 else 0

        # Update test control progress bar
        self.test_control_page.update_test_progress(
            progress_percent, f"Progress: {current_cycle}/{total_cycles} cycles"
        )

        # Update header progress
        if self.header is not None:
            self.header.show_test_progress(progress_percent)

        # Get current test name, ensuring it's never None
        current_test_name = "Unknown"
        if self.test_executor_thread and self.test_executor_thread.test_sequence:
            current_test_name = self.test_executor_thread.test_sequence

        progress = TestProgress(
            current_test=current_test_name,
            progress_percent=progress_percent,
            current_cycle=current_cycle,
            total_cycles=total_cycles,
            status=status,
            elapsed_time="00:00:00",  # TODO: Calculate actual elapsed time
            estimated_remaining="--:--:--",  # TODO: Calculate estimated remaining time
        )
        self.state_manager.update_test_progress(progress)

    def _on_thread_test_result(self, result_data) -> None:
        """Handle test result from thread"""
        # Standard library imports
        from datetime import datetime

        # Third-party imports
        from loguru import logger

        # Local application imports
        # Local imports
        from ui.gui.services.gui_state_manager import CycleData, TestResult

        logger.info(f"Received test result: {result_data}")

        try:
            # Convert test result to GUI TestResult for display
            if hasattr(result_data, "test_status"):
                # Check for EOL-specific attributes first
                if hasattr(result_data, "is_device_passed"):
                    # This is an EOLTestResult from domain layer
                    if result_data.is_device_passed:
                        status_text = "PASS"
                    elif result_data.is_device_failed:
                        status_text = "FAIL"
                    elif result_data.is_failed_execution:
                        status_text = "ERROR"
                    else:
                        status_text = result_data.test_status.value
                # For other result types (like HeatingCoolingTimeTestResult), use is_success or error_message
                elif hasattr(result_data, "is_success"):
                    if result_data.is_success and not result_data.error_message:
                        status_text = "PASS"
                    else:
                        status_text = "FAIL" if result_data.error_message else "PASS"
                else:
                    status_text = result_data.test_status.value

                logger.info(f"Test result received: {status_text}")

                # Convert domain result to GUI TestResult
                cycles = []
                if (
                    hasattr(result_data, "individual_cycle_results")
                    and result_data.individual_cycle_results
                ):
                    logger.info(
                        f"Converting {len(result_data.individual_cycle_results)} cycles to GUI format"
                    )
                    for idx, cycle_result in enumerate(result_data.individual_cycle_results, 1):
                        # Extract data from CycleResult
                        # CycleResult has: cycle_number, test_status, is_passed, measurements (TestMeasurements)

                        if cycle_result.measurements:
                            measurements = cycle_result.measurements

                            # Get temperature from measurements
                            if isinstance(measurements, dict):
                                # Dict format from hardware_service_facade:
                                # {"measurements": {temp: {pos: {"force": val}}}, "timing_data": {...}}
                                measurements_dict = measurements.get("measurements", {})
                                timing_data_dict = measurements.get("timing_data", {})

                                if measurements_dict:
                                    # Iterate through ALL temperatures (not just first one)
                                    temps = list(measurements_dict.keys())
                                    logger.info(
                                        f"Cycle {idx} - Found {len(temps)} temperatures: {temps}"
                                    )
                                    logger.info(
                                        f"Cycle {idx} - timing_data_dict keys: {list(timing_data_dict.keys())}"
                                    )

                                    for temp in temps:
                                        # Extract data for this temperature
                                        temperature = (
                                            float(temp)
                                            if isinstance(temp, (int, float, str))
                                            else 0.0
                                        )
                                        force = 0.0
                                        stroke = 0.0
                                        heating_time = 0.0
                                        cooling_time = 0.0

                                        # Get force from first position
                                        positions = measurements_dict.get(temp, {})
                                        if positions:
                                            first_pos = list(positions.keys())[0]
                                            force_data = positions.get(first_pos, {})
                                            force = force_data.get("force", 0.0)
                                            stroke = (
                                                first_pos
                                                if isinstance(first_pos, (int, float))
                                                else 0.0
                                            )

                                        # Extract heating/cooling times from timing_data for this temperature
                                        if timing_data_dict:
                                            # Find timing data for this temperature
                                            # timing_data keys are like: "temp_38", "temp_52", "temp_66"
                                            temp_int = int(temperature)
                                            timing_key = f"temp_{temp_int}"
                                            timing_info = timing_data_dict.get(timing_key, {})
                                            if timing_info:
                                                # Timing data is already in seconds, keep as float with 2 decimal places
                                                heating_time = round(
                                                    timing_info.get("heating_time_s", 0.0), 2
                                                )
                                                cooling_time = round(
                                                    timing_info.get("cooling_time_s", 0.0), 2
                                                )

                                        # Create CycleData for this temperature
                                        cycle_data = CycleData(
                                            cycle=idx,
                                            temperature=temperature,
                                            stroke=stroke,
                                            force=force,
                                            heating_time=heating_time,
                                            cooling_time=cooling_time,
                                            status="PASS" if cycle_result.is_passed else "FAIL",
                                        )
                                        cycles.append(cycle_data)
                                        logger.info(
                                            f"Cycle {idx}, Temp {temperature}°C - Force: {force:.2f}kgf, "
                                            f"Heat: {heating_time:.2f}s, Cool: {cooling_time:.2f}s"
                                        )
                            else:
                                # TestMeasurements object - iterate through all temperatures
                                try:
                                    # Local application imports
                                    from domain.value_objects.measurements import TestMeasurements

                                    if isinstance(measurements, TestMeasurements):
                                        logger.info(
                                            f"Cycle {idx} - TestMeasurements object detected"
                                        )

                                        # Get all temperatures
                                        temps = measurements.get_temperatures()
                                        logger.info(
                                            f"Cycle {idx} - Found {len(temps)} temperatures: {temps}"
                                        )

                                        timing_data = measurements.get_timing_data()

                                        # Iterate through each temperature
                                        for temp in temps:
                                            temperature = temp
                                            force = 0.0
                                            stroke = 0.0
                                            heating_time = 0.0
                                            cooling_time = 0.0

                                            # Get measurements for this temperature
                                            temp_measurements = (
                                                measurements.get_temperature_measurements(temp)
                                            )
                                            if temp_measurements:
                                                # Get positions for this temperature
                                                positions = temp_measurements.get_positions()
                                                if positions:
                                                    first_pos = positions[0]
                                                    stroke = first_pos
                                                    force_val = temp_measurements.get_force(
                                                        first_pos
                                                    )
                                                    if force_val is not None:
                                                        force = force_val

                                            # Get timing data for this temperature
                                            if timing_data:
                                                # timing_data keys are like: "temp_38", "temp_52", "temp_66"
                                                temp_int = int(temp)
                                                timing_key = f"temp_{temp_int}"
                                                timing_info = timing_data.get(timing_key, {})
                                                if timing_info:
                                                    # Timing data is already in seconds, keep as float with 2 decimal places
                                                    heating_time = round(
                                                        timing_info.get("heating_time_s", 0.0), 2
                                                    )
                                                    cooling_time = round(
                                                        timing_info.get("cooling_time_s", 0.0), 2
                                                    )

                                            # Create CycleData for this temperature
                                            cycle_data = CycleData(
                                                cycle=idx,
                                                temperature=temperature,
                                                stroke=stroke,
                                                force=force,
                                                heating_time=heating_time,
                                                cooling_time=cooling_time,
                                                status="PASS" if cycle_result.is_passed else "FAIL",
                                            )
                                            cycles.append(cycle_data)
                                            logger.info(
                                                f"Cycle {idx}, Temp {temperature}°C - Force: {force:.2f}kgf, "
                                                f"Heat: {heating_time:.2f}s, Cool: {cooling_time:.2f}s"
                                            )
                                except Exception as e:
                                    logger.warning(f"Failed to extract from TestMeasurements: {e}")
                                    # Standard library imports
                                    import traceback

                                    logger.warning(traceback.format_exc())
                else:
                    logger.info("Test completed (single cycle or no individual cycle data)")

                # Extract serial number from test_id or use stored serial_number from TestExecutorThread
                serial_number = "N/A"
                if hasattr(result_data, "test_id") and result_data.test_id:
                    # Try to extract serial number from TestId
                    extracted_serial = result_data.test_id.extract_serial_number()
                    if extracted_serial:
                        serial_number = extracted_serial
                    else:
                        # Fall back to stored serial_number from TestExecutorThread
                        if self.test_executor_thread and hasattr(
                            self.test_executor_thread, "serial_number"
                        ):
                            serial_number = self.test_executor_thread.serial_number or "N/A"
                elif self.test_executor_thread and hasattr(
                    self.test_executor_thread, "serial_number"
                ):
                    # Use serial number from TestExecutorThread
                    serial_number = self.test_executor_thread.serial_number or "N/A"

                # Create GUI TestResult
                test_result = TestResult(
                    test_id=str(getattr(result_data, "test_id", "Unknown")),
                    serial_number=serial_number,
                    status=status_text,
                    timestamp=datetime.now(),
                    duration_seconds=getattr(result_data, "test_duration_seconds", 0.0),
                    cycles=cycles,
                )

                # Add result to state manager (will be displayed in Results page)
                self.state_manager.add_test_result(test_result)
                logger.info(
                    f"Test result added to Results page: {test_result.test_id}, Serial: {serial_number}"
                )

                # TODO: Save test result to repository (logs/EOL Force Test/raw_data)
                # Currently, EOLTestResult doesn't contain EOLTest entity
                # This should be implemented at Use Case level, not here

            elif result_data is None:
                logger.info("Test result is None (likely cancelled by Emergency Stop)")
            else:
                logger.warning(f"Received unknown result format: {type(result_data)}")

        except Exception as e:
            logger.error(f"Failed to process test result: {e}")
            self.state_manager.add_log_message(
                "ERROR", "GUI", f"Failed to process test result: {str(e)}"
            )

    def _on_thread_test_completed(self, success: bool, message: str) -> None:
        """Handle test completion from thread"""
        # Third-party imports
        from loguru import logger

        logger.info(f"Test completed: success={success}, message={message}")

        if not self.test_control_page:
            logger.warning("test_control_page is None, skipping UI update")
            return

        # Stop progress bar animation
        if hasattr(self.test_control_page, "handle_test_completed"):
            self.test_control_page.handle_test_completed(success)

        # Add completion message to logs
        log_level = "INFO" if success else "ERROR"
        self.state_manager.add_log_message(log_level, "TEST", f"Test completed: {message}")

        # Reset GUI state
        self._set_test_running_state(False)
        self.state_manager.set_system_status("Ready")

        # Update header and hide progress
        if self.header is not None:
            if success:
                self.header.set_system_status("Test Complete", "ready")
            else:
                self.header.set_system_status("Test Failed", "error")
            self.header.hide_test_progress()

        # Update test control status instead of showing popup
        if success:
            self.test_control_page.update_test_status(
                "Test Completed Successfully", "status_success", 100
            )
        else:
            self.test_control_page.stop_indeterminate_progress()
            self.test_control_page.update_test_status("Test Failed", "status_error", 0)

    def _on_thread_test_error(self, error_message: str) -> None:
        """Handle test error from thread"""
        # Third-party imports
        from loguru import logger

        if not self.test_control_page:
            return

        logger.error(f"Test execution error: {error_message}")

        # Stop progress bar animation
        self.test_control_page.stop_indeterminate_progress()

        # Update test control status
        self.test_control_page.update_test_status(f"Test Error: {error_message}", "status_error", 0)

        # Reset GUI state
        self._set_test_running_state(False)
        self.state_manager.set_system_status("Error")

        # Show error message
        QMessageBox.critical(
            self, "Test Execution Error", f"Test execution failed:\n\n{error_message}"
        )

    def _on_thread_log_message(self, level: str, component: str, message: str) -> None:
        """Handle log message from thread"""
        # Forward log message to state manager
        self.state_manager.add_log_message(level, component, message)
