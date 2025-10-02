"""
Robot Control Widget

Modern robot control interface with Material Design 3 styling.
Provides comprehensive robot control operations from CLI.
"""

# Standard library imports
import asyncio
from typing import Optional, Tuple

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QDoubleSpinBox,
    QMessageBox,
    QProgressBar,
)
from PySide6.QtGui import QFont
from loguru import logger

# Local application imports
from application.containers.simple_reloadable_container import SimpleReloadableContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class RobotControlWidget(QWidget):
    """
    Modern robot control widget with comprehensive functionality.

    Features:
    - Connection management
    - Servo control (motor enable/disable)
    - Motion control (absolute/relative movement)
    - Homing operations
    - Real-time status display
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
        self.robot_service = container.hardware_service_facade().robot_service
        self.axis_id = 0  # Primary axis

        # Initialize attributes (will be set in setup_ui)
        self.status_card: QGroupBox
        self.connection_status: Tuple[QLabel, QLabel]
        self.position_status: Tuple[QLabel, QLabel]
        self.servo_status: Tuple[QLabel, QLabel]
        self.connect_btn: QPushButton
        self.disconnect_btn: QPushButton
        self.servo_on_btn: QPushButton
        self.servo_off_btn: QPushButton
        self.home_btn: QPushButton
        self.abs_pos_input: QDoubleSpinBox
        self.abs_vel_input: QDoubleSpinBox
        self.abs_move_btn: QPushButton
        self.rel_pos_input: QDoubleSpinBox
        self.rel_vel_input: QDoubleSpinBox
        self.rel_move_btn: QPushButton
        self.get_pos_btn: QPushButton
        self.stop_btn: QPushButton
        self.emergency_btn: QPushButton
        self.progress_bar: QProgressBar

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the robot control UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🤖 Robot Control System")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2196F3; margin-bottom: 10px;")
        layout.addWidget(title)

        # Status Card
        self.status_card = self._create_status_card()
        layout.addWidget(self.status_card)

        # Connection Card
        connection_card = self._create_connection_card()
        layout.addWidget(connection_card)

        # Servo Control Card
        servo_card = self._create_servo_card()
        layout.addWidget(servo_card)

        # Motion Control Card
        motion_card = self._create_motion_card()
        layout.addWidget(motion_card)

        # Emergency Controls
        emergency_card = self._create_emergency_card()
        layout.addWidget(emergency_card)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(self._get_progress_style())
        layout.addWidget(self.progress_bar)

        # Add stretch
        layout.addStretch()

        # Apply overall style
        self.setStyleSheet(self._get_overall_style())

    def _create_status_card(self) -> QGroupBox:
        """Create status display card"""
        card = QGroupBox("📊 Status")
        card.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout = QGridLayout(card)
        layout.setSpacing(10)

        # Status labels
        self.connection_status = self._create_status_label("Connection:", "Disconnected", "#FF5722")
        self.position_status = self._create_status_label("Position:", "Unknown", "#9E9E9E")
        self.servo_status = self._create_status_label("Servo:", "Disabled", "#FFC107")

        layout.addWidget(self.connection_status[0], 0, 0)
        layout.addWidget(self.connection_status[1], 0, 1)
        layout.addWidget(self.position_status[0], 1, 0)
        layout.addWidget(self.position_status[1], 1, 1)
        layout.addWidget(self.servo_status[0], 2, 0)
        layout.addWidget(self.servo_status[1], 2, 1)

        card.setStyleSheet(self._get_card_style())
        return card

    def _create_status_label(self, name: str, value: str, color: str) -> Tuple[QLabel, QLabel]:
        """Create a status label pair"""
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        name_label.setStyleSheet("color: #CCCCCC;")

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; padding: 5px; border-radius: 4px; background-color: rgba(255, 255, 255, 0.05);")

        return (name_label, value_label)

    def _create_connection_card(self) -> QGroupBox:
        """Create connection control card"""
        card = QGroupBox("🔌 Connection")
        card.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout = QHBoxLayout(card)
        layout.setSpacing(10)

        self.connect_btn = self._create_button("Connect", "#4CAF50", self._on_connect)
        self.disconnect_btn = self._create_button("Disconnect", "#F44336", self._on_disconnect)
        self.disconnect_btn.setEnabled(False)

        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)

        card.setStyleSheet(self._get_card_style())
        return card

    def _create_servo_card(self) -> QGroupBox:
        """Create servo control card"""
        card = QGroupBox("⚡ Servo Control")
        card.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout = QHBoxLayout(card)
        layout.setSpacing(10)

        self.servo_on_btn = self._create_button("Servo ON", "#4CAF50", self._on_servo_on)
        self.servo_off_btn = self._create_button("Servo OFF", "#FF9800", self._on_servo_off)
        self.servo_on_btn.setEnabled(False)
        self.servo_off_btn.setEnabled(False)

        layout.addWidget(self.servo_on_btn)
        layout.addWidget(self.servo_off_btn)

        card.setStyleSheet(self._get_card_style())
        return card

    def _create_motion_card(self) -> QGroupBox:
        """Create motion control card"""
        card = QGroupBox("🎯 Motion Control")
        card.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout = QVBoxLayout(card)
        layout.setSpacing(15)

        # Home button
        home_layout = QHBoxLayout()
        self.home_btn = self._create_button("🏠 Home Axis", "#2196F3", self._on_home)
        self.home_btn.setEnabled(False)
        home_layout.addWidget(self.home_btn)
        layout.addLayout(home_layout)

        # Absolute Move
        abs_group = self._create_move_group("Absolute Move", "abs")
        layout.addWidget(abs_group)

        # Relative Move
        rel_group = self._create_move_group("Relative Move", "rel")
        layout.addWidget(rel_group)

        # Position and Stop
        action_layout = QHBoxLayout()
        self.get_pos_btn = self._create_button("📍 Get Position", "#9C27B0", self._on_get_position)
        self.stop_btn = self._create_button("⏹️ Stop Motion", "#F44336", self._on_stop)
        self.get_pos_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        action_layout.addWidget(self.get_pos_btn)
        action_layout.addWidget(self.stop_btn)
        layout.addLayout(action_layout)

        card.setStyleSheet(self._get_card_style())
        return card

    def _create_move_group(self, title: str, move_type: str) -> QGroupBox:
        """Create a move control group (absolute or relative)"""
        group = QGroupBox(title)
        layout = QGridLayout(group)
        layout.setSpacing(8)

        # Position/Distance input
        label_text = "Position (μm):" if move_type == "abs" else "Distance (μm):"
        pos_label = QLabel(label_text)
        pos_input = QDoubleSpinBox()
        pos_input.setRange(0, 500000)
        pos_input.setDecimals(2)
        pos_input.setValue(10000.0)
        pos_input.setStyleSheet(self._get_input_style())

        # Velocity input
        vel_label = QLabel("Velocity (μm/s):")
        vel_input = QDoubleSpinBox()
        vel_input.setRange(1, 100000)
        vel_input.setDecimals(1)
        vel_input.setValue(1000.0)
        vel_input.setStyleSheet(self._get_input_style())

        # Move button
        move_btn = self._create_button(
            f"Move {move_type.upper()}",
            "#00BCD4",
            lambda: self._on_move(move_type, pos_input.value(), vel_input.value())
        )
        move_btn.setEnabled(False)

        # Store references
        if move_type == "abs":
            self.abs_pos_input = pos_input
            self.abs_vel_input = vel_input
            self.abs_move_btn = move_btn
        else:
            self.rel_pos_input = pos_input
            self.rel_vel_input = vel_input
            self.rel_move_btn = move_btn

        # Layout
        layout.addWidget(pos_label, 0, 0)
        layout.addWidget(pos_input, 0, 1)
        layout.addWidget(vel_label, 1, 0)
        layout.addWidget(vel_input, 1, 1)
        layout.addWidget(move_btn, 2, 0, 1, 2)

        group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: 600;
                color: #AAAAAA;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
                background-color: rgba(255, 255, 255, 0.02);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        return group

    def _create_emergency_card(self) -> QGroupBox:
        """Create emergency controls card"""
        card = QGroupBox("🚨 Emergency")
        card.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout = QHBoxLayout(card)

        self.emergency_btn = self._create_button("EMERGENCY STOP", "#D32F2F", self._on_emergency_stop)
        self.emergency_btn.setMinimumHeight(60)
        self.emergency_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(self.emergency_btn)

        card.setStyleSheet(self._get_card_style("#D32F2F"))
        return card

    def _create_button(self, text: str, color: str, callback) -> QPushButton:
        """Create a styled button"""
        btn = QPushButton(text)
        btn.setMinimumHeight(45)
        btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:disabled {{
                background-color: #3A3A3A;
                color: #666666;
            }}
        """)
        return btn

    def _lighten_color(self, color: str) -> str:
        """Lighten a hex color"""
        # Simple lightening by increasing RGB values
        return color  # Simplified for now

    def _darken_color(self, color: str) -> str:
        """Darken a hex color"""
        return color  # Simplified for now

    def _update_status(self) -> None:
        """Update robot status display (runs in Qt thread - non-blocking check)"""
        try:
            # Quick synchronous check - don't use async operations in Qt timer
            # Just update UI based on cached state
            # Actual async operations happen in button callbacks
            pass
        except Exception as e:
            logger.debug(f"Status update error: {e}")

    async def _async_update_status(self) -> None:
        """Async status update (called from button callbacks, not timer)"""
        try:
            is_connected = await self.robot_service.is_connected()

            # Update connection status
            if is_connected:
                self.connection_status[1].setText("Connected")
                self.connection_status[1].setStyleSheet("color: #4CAF50; padding: 5px; border-radius: 4px; background-color: rgba(76, 175, 80, 0.1);")
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                self.servo_on_btn.setEnabled(True)
                self.servo_off_btn.setEnabled(True)
                self.home_btn.setEnabled(True)
                self.abs_move_btn.setEnabled(True)
                self.rel_move_btn.setEnabled(True)
                self.get_pos_btn.setEnabled(True)
                self.stop_btn.setEnabled(True)

                # Try to get position
                try:
                    position = await self.robot_service.get_position(self.axis_id)
                    self.position_status[1].setText(f"{position:.2f} μm")
                    self.position_status[1].setStyleSheet("color: #2196F3; padding: 5px; border-radius: 4px; background-color: rgba(33, 150, 243, 0.1);")
                except Exception:
                    self.position_status[1].setText("Unknown")
                    self.position_status[1].setStyleSheet("color: #9E9E9E; padding: 5px; border-radius: 4px; background-color: rgba(255, 255, 255, 0.05);")
            else:
                self.connection_status[1].setText("Disconnected")
                self.connection_status[1].setStyleSheet("color: #FF5722; padding: 5px; border-radius: 4px; background-color: rgba(255, 87, 34, 0.1);")
                self.connect_btn.setEnabled(True)
                self.disconnect_btn.setEnabled(False)
                self.servo_on_btn.setEnabled(False)
                self.servo_off_btn.setEnabled(False)
                self.home_btn.setEnabled(False)
                self.abs_move_btn.setEnabled(False)
                self.rel_move_btn.setEnabled(False)
                self.get_pos_btn.setEnabled(False)
                self.stop_btn.setEnabled(False)
                self.position_status[1].setText("Unknown")
                self.position_status[1].setStyleSheet("color: #9E9E9E; padding: 5px; border-radius: 4px; background-color: rgba(255, 255, 255, 0.05);")

        except Exception as e:
            logger.error(f"Status update failed: {e}")

    # Button Callbacks
    def _on_connect(self) -> None:
        """Handle connect button"""
        asyncio.create_task(self._async_connect())

    async def _async_connect(self) -> None:
        """Async connect operation"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            await self.robot_service.connect()
            self.state_manager.add_log_message("INFO", "ROBOT", "Robot connected successfully")

            # Update status after connection
            await self._async_update_status()

            QMessageBox.information(self, "Success", "Robot connected successfully")
        except Exception as e:
            logger.error(f"Connect failed: {e}")
            self.state_manager.add_log_message("ERROR", "ROBOT", f"Connect failed: {e}")
            QMessageBox.critical(self, "Error", f"Connect failed:\n{e}")
        finally:
            self.progress_bar.setVisible(False)

    def _on_disconnect(self) -> None:
        """Handle disconnect button"""
        asyncio.create_task(self._async_disconnect())

    async def _async_disconnect(self) -> None:
        """Async disconnect operation"""
        try:
            await self.robot_service.disconnect()
            self.state_manager.add_log_message("INFO", "ROBOT", "Robot disconnected")

            # Update status after disconnection
            await self._async_update_status()

            QMessageBox.information(self, "Success", "Robot disconnected")
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")
            QMessageBox.critical(self, "Error", f"Disconnect failed:\n{e}")

    def _on_servo_on(self) -> None:
        """Handle servo on button"""
        asyncio.create_task(self._async_servo_on())

    async def _async_servo_on(self) -> None:
        """Async servo on operation"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            await self.robot_service.enable_servo(self.axis_id)
            self.servo_status[1].setText("Enabled")
            self.servo_status[1].setStyleSheet("color: #4CAF50; padding: 5px; border-radius: 4px; background-color: rgba(76, 175, 80, 0.1);")
            self.state_manager.add_log_message("INFO", "ROBOT", "Servo enabled")
        except Exception as e:
            logger.error(f"Servo on failed: {e}")
            QMessageBox.critical(self, "Error", f"Servo on failed:\n{e}")
        finally:
            self.progress_bar.setVisible(False)

    def _on_servo_off(self) -> None:
        """Handle servo off button"""
        asyncio.create_task(self._async_servo_off())

    async def _async_servo_off(self) -> None:
        """Async servo off operation"""
        try:
            await self.robot_service.disable_servo(self.axis_id)
            self.servo_status[1].setText("Disabled")
            self.servo_status[1].setStyleSheet("color: #FFC107; padding: 5px; border-radius: 4px; background-color: rgba(255, 193, 7, 0.1);")
            self.state_manager.add_log_message("INFO", "ROBOT", "Servo disabled")
        except Exception as e:
            logger.error(f"Servo off failed: {e}")
            QMessageBox.critical(self, "Error", f"Servo off failed:\n{e}")

    def _on_home(self) -> None:
        """Handle home button"""
        asyncio.create_task(self._async_home())

    async def _async_home(self) -> None:
        """Async home operation"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            await self.robot_service.home_axis(self.axis_id)
            self.state_manager.add_log_message("INFO", "ROBOT", "Homing completed")
            QMessageBox.information(self, "Success", "Homing completed")
        except Exception as e:
            logger.error(f"Homing failed: {e}")
            QMessageBox.critical(self, "Error", f"Homing failed:\n{e}")
        finally:
            self.progress_bar.setVisible(False)

    def _on_move(self, move_type: str, position: float, velocity: float) -> None:
        """Handle move button"""
        asyncio.create_task(self._async_move(move_type, position, velocity))

    async def _async_move(self, move_type: str, position: float, velocity: float) -> None:
        """Async move operation"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)

            if move_type == "abs":
                await self.robot_service.move_absolute(
                    position=position,
                    axis_id=self.axis_id,
                    velocity=velocity,
                    acceleration=5000.0,
                    deceleration=5000.0
                )
                self.state_manager.add_log_message("INFO", "ROBOT", f"Moved to {position:.2f} μm")
            else:
                await self.robot_service.move_relative(
                    distance=position,
                    axis_id=self.axis_id,
                    velocity=velocity,
                    acceleration=5000.0,
                    deceleration=5000.0
                )
                self.state_manager.add_log_message("INFO", "ROBOT", f"Moved by {position:.2f} μm")
        except Exception as e:
            logger.error(f"Move failed: {e}")
            QMessageBox.critical(self, "Error", f"Move failed:\n{e}")
        finally:
            self.progress_bar.setVisible(False)

    def _on_get_position(self) -> None:
        """Handle get position button"""
        asyncio.create_task(self._async_get_position())

    async def _async_get_position(self) -> None:
        """Async get position operation"""
        try:
            position = await self.robot_service.get_position(self.axis_id)
            self.position_status[1].setText(f"{position:.2f} μm")
            QMessageBox.information(self, "Position", f"Current position: {position:.2f} μm")
        except Exception as e:
            logger.error(f"Get position failed: {e}")
            QMessageBox.critical(self, "Error", f"Get position failed:\n{e}")

    def _on_stop(self) -> None:
        """Handle stop button"""
        asyncio.create_task(self._async_stop())

    async def _async_stop(self) -> None:
        """Async stop operation"""
        try:
            await self.robot_service.stop_motion(self.axis_id, 5000.0)
            self.state_manager.add_log_message("WARNING", "ROBOT", "Motion stopped")
            QMessageBox.warning(self, "Stopped", "Motion stopped")
        except Exception as e:
            logger.error(f"Stop failed: {e}")
            QMessageBox.critical(self, "Error", f"Stop failed:\n{e}")

    def _on_emergency_stop(self) -> None:
        """Handle emergency stop button"""
        asyncio.create_task(self._async_emergency_stop())

    async def _async_emergency_stop(self) -> None:
        """Async emergency stop operation"""
        try:
            await self.robot_service.emergency_stop(self.axis_id)
            self.state_manager.add_log_message("CRITICAL", "ROBOT", "EMERGENCY STOP ACTIVATED")
            QMessageBox.critical(self, "Emergency Stop", "EMERGENCY STOP ACTIVATED!")
        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            QMessageBox.critical(self, "Error", f"Emergency stop failed:\n{e}")

    # Styling Methods
    def _get_card_style(self, border_color: str = "#2196F3") -> str:
        """Get card stylesheet"""
        return f"""
            QGroupBox {{
                font-size: 12px;
                font-weight: bold;
                color: #CCCCCC;
                border: 2px solid {border_color};
                border-radius: 12px;
                padding: 20px;
                margin-top: 15px;
                background-color: rgba(255, 255, 255, 0.03);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: {border_color};
            }}
        """

    def _get_input_style(self) -> str:
        """Get input field stylesheet"""
        return """
            QDoubleSpinBox {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px;
                color: #FFFFFF;
                font-size: 11px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #2196F3;
            }
        """

    def _get_progress_style(self) -> str:
        """Get progress bar stylesheet"""
        return """
            QProgressBar {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                background-color: rgba(255, 255, 255, 0.05);
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 5px;
            }
        """

    def _get_overall_style(self) -> str:
        """Get overall widget stylesheet"""
        return """
            QWidget {
                background-color: #1e1e1e;
                color: #FFFFFF;
            }
        """
