"""
Safety Alert Service

Service for handling safety sensor violations and user notifications.
Provides GUI popups, console alerts, and audio warnings for safety issues.
"""

# Standard library imports
from enum import Enum
from typing import Dict, List, Optional, TYPE_CHECKING

# Third-party imports
from loguru import logger

# Local application imports
from domain.value_objects.hardware_config import DigitalPin


if TYPE_CHECKING:
    # Local application imports
    from application.services.industrial.tower_lamp_service import TowerLampService


class SafetyViolationType(Enum):
    """Types of safety violations"""

    DOOR_OPEN = "door_open"
    CLAMP_NOT_ENGAGED = "clamp_not_engaged"
    CHAIN_NOT_READY = "chain_not_ready"
    MULTIPLE_SENSORS = "multiple_sensors"
    EMERGENCY_STOP_ACTIVE = "emergency_stop_active"


class SafetyAlertLevel(Enum):
    """Safety alert severity levels"""

    WARNING = "warning"  # 경고 - 노란색 표시
    CRITICAL = "critical"  # 위험 - 빨간색 표시
    EMERGENCY = "emergency"  # 비상 - 빨간색 점멸


class SafetyAlert:
    """Safety alert information"""

    def __init__(
        self,
        violation_type: SafetyViolationType,
        level: SafetyAlertLevel,
        title: str,
        message: str,
        affected_sensors: List[str],
        korean_title: str = "",
        korean_message: str = "",
    ):
        self.violation_type = violation_type
        self.level = level
        self.title = title
        self.message = message
        self.affected_sensors = affected_sensors
        self.korean_title = korean_title
        self.korean_message = korean_message


class SafetyAlertService:
    """
    Safety Alert Service

    Handles safety sensor violations with user notifications and visual/audio alerts.
    Provides multi-language support and different alert methods for CLI/GUI environments.
    """

    def __init__(self, tower_lamp_service: Optional["TowerLampService"] = None):
        """
        Initialize Safety Alert Service

        Args:
            tower_lamp_service: Optional tower lamp service for visual alerts
        """
        self.tower_lamp_service = tower_lamp_service

        # Alert configuration
        self._alert_definitions = self._setup_alert_definitions()

        # GUI callback for popup alerts (will be set by GUI if available)
        self._gui_alert_callback = None

        logger.info("🔒 SAFETY_ALERT: Safety Alert Service initialized")

    def set_gui_alert_callback(self, callback) -> None:
        """
        Set GUI alert callback for popup notifications

        Args:
            callback: Function to call for GUI alerts (title, message, level)
        """
        self._gui_alert_callback = callback
        logger.info("🔒 SAFETY_ALERT: GUI alert callback configured")

    async def check_safety_sensors(
        self,
        door_sensor: DigitalPin,
        clamp_sensor: DigitalPin,
        chain_sensor: DigitalPin,
        current_states: Dict[int, bool],
    ) -> Optional[SafetyAlert]:
        """
        Check safety sensor states and return alert if violation found

        Args:
            door_sensor: Door safety sensor configuration
            clamp_sensor: Clamp safety sensor configuration
            chain_sensor: Chain safety sensor configuration
            current_states: Current digital input states (channel -> state)

        Returns:
            SafetyAlert if violation found, None if all sensors OK
        """
        # Get sensor states (apply contact type logic)
        door_ok = self._get_logical_state(door_sensor, current_states)
        clamp_ok = self._get_logical_state(clamp_sensor, current_states)
        chain_ok = self._get_logical_state(chain_sensor, current_states)

        logger.debug(
            f"🔒 SAFETY_CHECK: Sensor states - Door: {door_ok}, Clamp: {clamp_ok}, Chain: {chain_ok}"
        )

        # Check for violations
        failed_sensors = []
        if not door_ok:
            failed_sensors.append("door")
        if not clamp_ok:
            failed_sensors.append("clamp")
        if not chain_ok:
            failed_sensors.append("chain")

        if not failed_sensors:
            return None  # All sensors OK

        # Determine violation type
        if len(failed_sensors) > 1:
            violation_type = SafetyViolationType.MULTIPLE_SENSORS
        elif "door" in failed_sensors:
            violation_type = SafetyViolationType.DOOR_OPEN
        elif "clamp" in failed_sensors:
            violation_type = SafetyViolationType.CLAMP_NOT_ENGAGED
        else:  # chain
            violation_type = SafetyViolationType.CHAIN_NOT_READY

        # Create and return alert
        alert = self._create_alert(violation_type, failed_sensors)
        logger.warning(f"🔒 SAFETY_VIOLATION: {alert.title} - Sensors: {failed_sensors}")

        return alert

    async def trigger_safety_alert(self, alert: SafetyAlert) -> None:
        """
        Trigger safety alert with all configured notification methods

        Args:
            alert: Safety alert to trigger
        """
        logger.warning(f"🚨 SAFETY_ALERT: Triggering alert - {alert.title}")

        # 1. Console/Log alert (always available)
        await self._show_console_alert(alert)

        # 2. GUI popup alert (if GUI is available)
        if self._gui_alert_callback:
            await self._show_gui_alert(alert)

        # 3. Tower lamp/audio alert (if tower lamp service is available)
        if self.tower_lamp_service:
            await self._show_visual_alert(alert)

    async def trigger_emergency_stop_alert(self) -> None:
        """Trigger emergency stop specific alert"""
        alert = SafetyAlert(
            violation_type=SafetyViolationType.EMERGENCY_STOP_ACTIVE,
            level=SafetyAlertLevel.EMERGENCY,
            title="EMERGENCY STOP ACTIVATED",
            message="Emergency stop button has been pressed. All operations stopped immediately.",
            affected_sensors=["emergency_stop"],
            korean_title="비상 정지 작동",
            korean_message="비상정지 버튼이 눌렸습니다. 모든 작업이 즉시 중단되었습니다.",
        )

        logger.critical(f"🚨 EMERGENCY_ALERT: {alert.title}")
        await self.trigger_safety_alert(alert)

    def _get_logical_state(self, sensor: DigitalPin, current_states: Dict[int, bool]) -> bool:
        """
        Get logical state of sensor considering contact type

        Args:
            sensor: Digital pin configuration
            current_states: Current raw states (channel -> raw_state)

        Returns:
            Logical state (True = sensor condition satisfied)
        """
        channel = sensor.pin_number
        raw_state = current_states.get(channel, False)

        # Apply contact type logic
        if sensor.contact_type == "A":  # A-contact (Normally Open)
            return raw_state  # True when activated
        else:  # B-contact (Normally Closed)
            return not raw_state  # True when not activated (closed)

    def _create_alert(
        self, violation_type: SafetyViolationType, failed_sensors: List[str]
    ) -> SafetyAlert:
        """
        Create safety alert based on violation type

        Args:
            violation_type: Type of safety violation
            failed_sensors: List of failed sensor names

        Returns:
            SafetyAlert object with appropriate message
        """
        if violation_type in self._alert_definitions:
            alert_def = self._alert_definitions[violation_type]
            return SafetyAlert(
                violation_type=violation_type,
                level=alert_def["level"],
                title=alert_def["title"],
                message=alert_def["message"].format(sensors=", ".join(failed_sensors)),
                affected_sensors=failed_sensors,
                korean_title=alert_def["korean_title"],
                korean_message=alert_def["korean_message"].format(
                    sensors=", ".join(failed_sensors)
                ),
            )
        else:
            # Fallback for unknown violation types
            return SafetyAlert(
                violation_type=violation_type,
                level=SafetyAlertLevel.WARNING,
                title="Safety Sensor Issue",
                message=f"Safety sensors not satisfied: {', '.join(failed_sensors)}",
                affected_sensors=failed_sensors,
                korean_title="안전 센서 문제",
                korean_message=f"안전 센서가 만족되지 않음: {', '.join(failed_sensors)}",
            )

    async def _show_console_alert(self, alert: SafetyAlert) -> None:
        """Show alert in console/logs"""
        level_emoji = {
            SafetyAlertLevel.WARNING: "⚠️",
            SafetyAlertLevel.CRITICAL: "🚨",
            SafetyAlertLevel.EMERGENCY: "🆘",
        }

        emoji = level_emoji.get(alert.level, "⚠️")

        logger.warning(f"{emoji} SAFETY_ALERT: {alert.title}")
        logger.warning(f"{emoji} SAFETY_ALERT: {alert.message}")
        logger.warning(
            f"{emoji} SAFETY_ALERT: Affected sensors: {', '.join(alert.affected_sensors)}"
        )

        # Also log Korean message if available
        if alert.korean_title:
            logger.warning(f"{emoji} 안전_경고: {alert.korean_title}")
        if alert.korean_message:
            logger.warning(f"{emoji} 안전_경고: {alert.korean_message}")

    async def _show_gui_alert(self, alert: SafetyAlert) -> None:
        """Show alert in GUI popup"""
        try:
            if self._gui_alert_callback:
                # Use Korean message if available, otherwise English
                title = alert.korean_title if alert.korean_title else alert.title
                message = alert.korean_message if alert.korean_message else alert.message

                # Call GUI alert callback
                await self._gui_alert_callback(title, message, alert.level.value)
                logger.info("🔒 SAFETY_ALERT: GUI popup alert shown")
        except Exception as e:
            logger.error(f"🔒 SAFETY_ALERT: Failed to show GUI alert: {e}")

    async def _show_visual_alert(self, alert: SafetyAlert) -> None:
        """Show alert with tower lamp and beep"""
        try:
            if not self.tower_lamp_service:
                return

            # Type narrowing for Pylance - ensure tower_lamp_service is not None
            assert self.tower_lamp_service is not None

            # Import SystemStatus here to avoid circular imports
            # Local application imports
            from application.services.industrial.tower_lamp_service import SystemStatus

            # Map alert level to tower lamp status
            if alert.level == SafetyAlertLevel.EMERGENCY:
                await self.tower_lamp_service.set_system_status(SystemStatus.SYSTEM_EMERGENCY)
            elif alert.level == SafetyAlertLevel.CRITICAL:
                await self.tower_lamp_service.set_system_status(SystemStatus.SYSTEM_ERROR)
            else:  # WARNING
                await self.tower_lamp_service.set_system_status(SystemStatus.SAFETY_VIOLATION)

            logger.info("🚦 SAFETY_ALERT: Visual alert triggered via tower lamp")

        except Exception as e:
            logger.error(f"🚦 SAFETY_ALERT: Failed to show visual alert: {e}")

    def _setup_alert_definitions(self) -> Dict[SafetyViolationType, Dict]:
        """Setup predefined alert definitions"""
        return {
            SafetyViolationType.DOOR_OPEN: {
                "level": SafetyAlertLevel.CRITICAL,
                "title": "Safety Door Open",
                "message": "Safety door is open. Close the door before starting test.",
                "korean_title": "안전문 열림",
                "korean_message": "안전문이 열려있습니다. 테스트 시작 전에 문을 닫아주세요.",
            },
            SafetyViolationType.CLAMP_NOT_ENGAGED: {
                "level": SafetyAlertLevel.CRITICAL,
                "title": "Clamp Not Engaged",
                "message": "DUT clamp is not properly engaged. Check clamp position.",
                "korean_title": "클램프 미체결",
                "korean_message": "DUT 클램프가 제대로 체결되지 않았습니다. 클램프 위치를 확인하세요.",
            },
            SafetyViolationType.CHAIN_NOT_READY: {
                "level": SafetyAlertLevel.CRITICAL,
                "title": "Chain Not Ready",
                "message": "Safety chain is not in ready position. Check chain alignment.",
                "korean_title": "체인 미준비",
                "korean_message": "안전 체인이 준비 위치에 있지 않습니다. 체인 정렬을 확인하세요.",
            },
            SafetyViolationType.MULTIPLE_SENSORS: {
                "level": SafetyAlertLevel.CRITICAL,
                "title": "Multiple Safety Issues",
                "message": "Multiple safety sensors are not satisfied: {sensors}. Check all safety conditions.",
                "korean_title": "복수 안전장치 문제",
                "korean_message": "여러 안전 센서가 만족되지 않음: {sensors}. 모든 안전 조건을 확인하세요.",
            },
            SafetyViolationType.EMERGENCY_STOP_ACTIVE: {
                "level": SafetyAlertLevel.EMERGENCY,
                "title": "EMERGENCY STOP ACTIVE",
                "message": "Emergency stop is active. Reset emergency stop and check system before continuing.",
                "korean_title": "비상정지 작동 중",
                "korean_message": "비상정지가 작동 중입니다. 비상정지를 해제하고 시스템을 점검한 후 계속하세요.",
            },
        }

    async def test_alert_system(self) -> None:
        """Test all alert methods (for debugging/maintenance)"""
        logger.info("🔒 SAFETY_ALERT: Testing alert system...")

        test_alert = SafetyAlert(
            violation_type=SafetyViolationType.DOOR_OPEN,
            level=SafetyAlertLevel.WARNING,
            title="Test Alert",
            message="This is a test alert to verify the safety alert system is working.",
            affected_sensors=["test_sensor"],
            korean_title="테스트 경고",
            korean_message="안전 경고 시스템이 작동하는지 확인하는 테스트 경고입니다.",
        )

        await self.trigger_safety_alert(test_alert)
        logger.info("🔒 SAFETY_ALERT: Alert system test completed")
