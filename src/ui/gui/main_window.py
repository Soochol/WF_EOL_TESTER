"""
Main Window

Main application window with sidebar navigation and content area.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
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
from ui.gui.widgets.content.about_widget import AboutWidget
from ui.gui.widgets.content.dashboard_widget import DashboardWidget
from ui.gui.widgets.content.hardware_widget import HardwareWidget
from ui.gui.widgets.content.logs_widget import LogsWidget
from ui.gui.widgets.content.results_widget import ResultsWidget
from ui.gui.widgets.content.settings_widget import SettingsWidget
from ui.gui.widgets.content.test_control_widget import TestControlWidget
from ui.gui.widgets.header.header_widget import HeaderWidget
from ui.gui.widgets.sidebar.sidebar_widget import SidebarWidget


class TestExecutorThread(QThread):
    """
    Thread for executing tests in background without blocking GUI.
    """

    # Signals for communicating with GUI
    test_started = Signal(str)  # test_name
    test_progress = Signal(int, int, str)  # current_cycle, total_cycles, status
    test_result = Signal(object)  # test result data
    test_completed = Signal(bool, str)  # success, message
    test_error = Signal(str)  # error message
    log_message = Signal(str, str, str)  # level, component, message

    def __init__(self, container, test_sequence: str, serial_number: str, parent=None):
        super().__init__(parent)
        self.container = container
        self.test_sequence = test_sequence
        self.serial_number = serial_number
        self.should_stop = False

    def stop_test(self):
        """Request test to stop"""
        self.should_stop = True

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

    def run(self):
        """Run the selected test in background thread"""
        # Third-party imports
        import asyncio
        from loguru import logger

        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the test
            result = loop.run_until_complete(self._execute_test())

            # Check actual test success/failure based on result type and content
            success, message = self._evaluate_test_result(result)
            self.test_completed.emit(success, message)

        except KeyboardInterrupt:
            # Emergency Stop으로 인한 중단 - 정상적인 상황
            logger.info("Test cancelled by Emergency Stop")
            self.test_completed.emit(False, "Test cancelled by Emergency Stop")
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            self.test_error.emit(str(e))
        finally:
            try:
                # Gracefully cleanup all pending tasks before closing the loop
                pending_tasks = asyncio.all_tasks(loop)
                if pending_tasks:
                    logger.debug(
                        f"🧹 TEST_CLEANUP: Found {len(pending_tasks)} pending tasks to cleanup"
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
                        logger.debug("🧹 TEST_CLEANUP: All tasks cleaned up successfully")
                    except asyncio.TimeoutError:
                        logger.warning(
                            "🧹 TEST_CLEANUP: Task cleanup timed out, some tasks may not have finished"
                        )
                    except Exception as cleanup_error:
                        logger.debug(
                            f"🧹 TEST_CLEANUP: Task cleanup completed with exceptions (expected): {cleanup_error}"
                        )

                # Now it's safe to close the loop
                loop.close()
                logger.debug("🧹 TEST_CLEANUP: Event loop closed successfully")

            except Exception as e:
                logger.error(f"🧹 TEST_CLEANUP: Error during cleanup: {e}")
                try:
                    loop.close()
                except Exception:
                    pass

    async def _execute_test(self):
        """Execute the selected test asynchronously"""
        # Local application imports
        from domain.value_objects.dut_command_info import DUTCommandInfo

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

        # Create test input
        test_input = EOLForceTestInput(dut_info=dut_info, operator_id="GUI_USER")

        # Get use case from container
        self.log_message.emit("INFO", "EOL_TEST", f"Using container ID: {id(self.container)}")

        # Verify GUI State Manager connection before test execution
        hardware_facade = self.container.hardware_service_facade()
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

        eol_test_use_case = self.container.eol_force_test_use_case()

        self.log_message.emit("INFO", "EOL_TEST", "Executing EOL Force Test...")

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

        # Create test input
        test_input = HeatingCoolingTimeTestInput(dut_info=dut_info, operator_id="GUI_USER")

        # Get use case from container
        heating_cooling_use_case = self.container.heating_cooling_time_test_use_case()

        self.log_message.emit("INFO", "HEATING_COOLING", "Executing Heating Cooling Time Test...")

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
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.test_executor_thread: Optional[TestExecutorThread] = (
            None  # For background test execution
        )
        self.robot_home_thread: Optional[RobotHomeThread] = (
            None  # For background robot home execution
        )
        self.emergency_stop_active = False  # Track emergency stop state

        # GUI State Manager is already injected in main_gui.py during initialization
        # No need to inject again here to avoid overwriting the connection

        self.setup_ui()
        self.setup_status_bar()
        self.setup_update_timer()
        # Start maximized for industrial use
        self.showMaximized()

    def setup_ui(self) -> None:
        """Setup the main window UI"""
        # Window properties
        self.setWindowTitle("WF EOL Tester - Industrial GUI")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout (vertical to accommodate header)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        self.header = HeaderWidget(container=self.container, state_manager=self.state_manager)
        self.header.emergency_stop_requested.connect(self._on_emergency_stop_requested)
        self.header.settings_requested.connect(self._on_header_settings_clicked)
        self.header.notifications_requested.connect(self._on_header_notifications_clicked)
        main_layout.addWidget(self.header)

        # Content area layout (sidebar + main content)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.page_changed.connect(self.change_page)
        content_layout.addWidget(self.sidebar)

        # Content stack
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)

        # Add content area to main layout
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        # Create and add content pages
        self.create_content_pages()

        # Set initial page
        self.change_page("dashboard")

    def create_content_pages(self) -> None:
        """Create and add content pages to stack"""
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

        # Hardware page
        self.hardware_page = HardwareWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.content_stack.addWidget(self.hardware_page)

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
            "hardware": self.hardware_page,
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

        # Add to status bar
        self.status_bar.addWidget(self.system_status_label)
        self.status_bar.addWidget(self._create_separator())
        self.status_bar.addWidget(self.connection_status_label)
        self.status_bar.addWidget(self._create_separator())
        self.status_bar.addWidget(self.test_status_label)
        self.status_bar.addWidget(self._create_separator())
        self.status_bar.addWidget(self.time_label)
        self.status_bar.addWidget(self._create_separator())
        self.status_bar.addPermanentWidget(self.progress_label)

        # Style status bar
        self.status_bar.setStyleSheet(
            """
            QStatusBar {
                background-color: #2d2d2d;
                color: #cccccc;
                border-top: 1px solid #404040;
                padding: 2px;
            }
            QLabel {
                padding: 2px 8px;
                font-size: 14px;
            }
        """
        )

    def setup_update_timer(self) -> None:
        """Setup timer for periodic UI updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status_bar)
        self.update_timer.start(1000)  # Update every second

    def _create_separator(self) -> QFrame:
        """Create a status bar separator"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #404040;")
        return separator

    def change_page(self, page_id: str) -> None:
        """Change to a different content page"""
        if page_id in self.pages:
            page_widget = self.pages[page_id]
            self.content_stack.setCurrentWidget(page_widget)
            self.sidebar.set_current_page(page_id)

            # Auto-select serial number when navigating to test control
            if page_id == "test_control" and self.test_control_page.serial_edit:
                self.test_control_page.serial_edit.selectAll()
                self.test_control_page.serial_edit.setFocus()

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

    def closeEvent(self, event) -> None:
        """Handle window close event"""
        # TODO: Add cleanup logic if needed
        event.accept()

    # Header Signal Handlers
    # ============================================================================

    def _on_header_settings_clicked(self) -> None:
        """Handle settings button click from header"""
        # Navigate to settings page
        self.change_page("settings")

    def _on_header_notifications_clicked(self) -> None:
        """Handle notifications button click from header"""
        # Third-party imports
        from PySide6.QtWidgets import QMessageBox

        # Show notifications dialog (placeholder)
        QMessageBox.information(
            self,
            "Notifications",
            "No new notifications.\n\n" "System notifications and alerts will appear here.",
        )

    # Test Control Signal Handlers
    # ============================================================================

    def _on_test_started(self) -> None:
        """Handle test start request"""
        # Third-party imports
        from loguru import logger

        try:
            # Check if test is already running
            if self.test_executor_thread and self.test_executor_thread.isRunning():
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
            if not self.test_control_page.serial_edit or not self.test_control_page.sequence_combo:
                self.test_control_page.update_test_status(
                    "Test controls not initialized", "status_error"
                )
                return

            serial_number = self.test_control_page.serial_edit.text().strip()
            test_sequence = self.test_control_page.sequence_combo.currentText()

            if not serial_number:
                self.test_control_page.update_test_status(
                    "Please enter a serial number", "status_warning"
                )
                return

            logger.info(f"Starting {test_sequence} for serial number: {serial_number}")

            # Clear previous test results from Results table and chart
            if self.results_page.results_table:
                self.results_page.results_table.clear_results()
            if self.results_page.temp_force_chart:
                self.results_page.temp_force_chart.clear_data()

            # Clear live logs when starting a new test
            if self.logs_page.log_viewer:
                self.logs_page.log_viewer.clear_logs()
            if self.test_control_page.log_viewer:
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
            self.test_control_page.update_test_status(
                f"Failed to start test: {str(e)}", "status_error"
            )
            self._set_test_running_state(False)

    def _on_test_stopped(self) -> None:
        """Handle test stop request"""
        # Third-party imports
        from loguru import logger

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
        self.header.set_system_status("Ready", "ready")

    def _on_test_paused(self) -> None:
        """Handle test pause request"""
        # Third-party imports
        from loguru import logger

        logger.info("Test pause requested")
        self.state_manager.add_log_message("INFO", "TEST", "Test pause requested by user")

        # TODO: Implement test pause logic
        # Update test control status
        self.test_control_page.update_test_status("Test Paused", "⏸️")

    def _on_robot_home_requested(self) -> None:
        """Handle robot home request"""
        # Third-party imports
        from loguru import logger

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
            self.test_control_page.update_test_status("Robot Home Failed", "status_error")

    def _on_emergency_stop_requested(self) -> None:
        """Handle emergency stop request"""
        # Third-party imports
        from PySide6.QtCore import QTimer
        from loguru import logger

        logger.critical("EMERGENCY STOP REQUESTED")

        # PRIORITY 1: Immediate UI updates (must happen first)
        def immediate_ui_updates():
            """Execute immediate UI updates with high priority"""
            logger.info("Executing immediate UI updates for Emergency Stop")

            # Update test control status immediately for user feedback
            self.test_control_page.update_test_status(
                "EMERGENCY STOP ACTIVATED! - HOME REQUIRED", "status_emergency"
            )

            # Update header status
            self.header.set_system_status("EMERGENCY STOP", "emergency")

            # Set emergency stop flag and disable START TEST button
            self.emergency_stop_active = True
            logger.info("Emergency stop state activated - START TEST button disabled")
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

        if success:
            logger.info(f"✅ {message}")
            self.state_manager.add_log_message("INFO", "ROBOT", message)
            self.test_control_page.update_test_status("Robot Home Completed", "status_success")

            # Update header to show "Robot Homed" status
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
        from PySide6.QtCore import QTimer
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

            # Create and configure test executor thread with main container (preserves GUI State Manager)
            self.test_executor_thread = TestExecutorThread(
                container=self.container,  # Use main container instead of fresh one
                test_sequence=test_sequence,
                serial_number=serial_number,
                parent=self,
            )

            # Connect thread signals
            self._connect_test_thread_signals()

            # Start the test execution thread
            self.test_executor_thread.start()
            logger.info(f"Test execution thread started for {test_sequence}")

        except Exception as e:
            logger.error(f"Failed to start test execution thread: {e}")
            self.state_manager.add_log_message("ERROR", "TEST", f"Failed to start test: {str(e)}")
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

    def _set_test_running_state(self, running: bool) -> None:
        """Set GUI state for test running/stopped"""
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

        progress_percent = int((current_cycle / total_cycles) * 100) if total_cycles > 0 else 0

        # Update test control progress bar
        self.test_control_page.update_test_progress(
            progress_percent, f"Progress: {current_cycle}/{total_cycles} cycles"
        )

        # Update header progress
        self.header.show_test_progress(progress_percent)

        progress = TestProgress(
            current_test=(
                self.test_executor_thread.test_sequence if self.test_executor_thread else "Unknown"
            ),
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
        # Third-party imports
        from loguru import logger

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

                # Individual cycle results are already processed in real-time by hardware facade
                # No need to process them again here to avoid duplication
                logger.info(f"Test result received: {status_text}")
                if (
                    hasattr(result_data, "individual_cycle_results")
                    and result_data.individual_cycle_results
                ):
                    logger.info(
                        f"Test completed with {len(result_data.individual_cycle_results)} cycles (already displayed in real-time)"
                    )
                else:
                    logger.info("Test completed (single cycle or no individual cycle data)")

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

        # Add completion message to logs
        log_level = "INFO" if success else "ERROR"
        self.state_manager.add_log_message(log_level, "TEST", f"Test completed: {message}")

        # Reset GUI state
        self._set_test_running_state(False)
        self.state_manager.set_system_status("Ready")

        # Update header and hide progress
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
            self.test_control_page.update_test_status("Test Failed", "status_error", 0)

    def _on_thread_test_error(self, error_message: str) -> None:
        """Handle test error from thread"""
        # Third-party imports
        from loguru import logger

        logger.error(f"Test execution error: {error_message}")

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
