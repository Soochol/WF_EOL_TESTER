"""
Settings Management Form Component
Magic MCP Generated - Modern form with validation and accessibility
"""

# Standard library imports
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
)


class ValidationRule(Enum):
    """Form validation rules"""

    REQUIRED = "required"
    EMAIL = "email"
    NUMBER = "number"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    RANGE = "range"


@dataclass
class ValidationError:
    """Form validation error"""

    field_name: str
    rule: ValidationRule
    message: str
    value: Any = None


@dataclass
class FormField:
    """Form field configuration"""

    name: str
    label: str
    field_type: str  # text, number, select, checkbox, textarea
    value: Any = None
    placeholder: str = ""
    help_text: str = ""
    required: bool = False
    disabled: bool = False
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    options: Optional[List[Dict[str, str]]] = None  # For select fields


class SettingsCategory(Enum):
    """Settings categories for organization"""

    HARDWARE = "hardware"
    TESTING = "testing"
    COMMUNICATION = "communication"
    UI_PREFERENCES = "ui_preferences"
    ADVANCED = "advanced"


@dataclass
class SettingsSchema:
    """Complete settings schema definition"""

    categories: Dict[str, List[FormField]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize default settings schema"""
        if not self.categories:
            self._initialize_default_schema()

    def _initialize_default_schema(self) -> None:
        """Initialize default EOL tester settings schema"""
        self.categories = {
            SettingsCategory.HARDWARE.value: [
                FormField(
                    name="loadcell_port",
                    label="Load Cell Serial Port",
                    field_type="text",
                    value="/dev/ttyUSB0",
                    placeholder="e.g., /dev/ttyUSB0 or COM3",
                    help_text="Serial port for BS205 load cell communication",
                    required=True,
                    validation_rules=[
                        {
                            "rule": "required",
                            "message": "Serial port is required",
                        },
                        {
                            "rule": "pattern",
                            "pattern": r"^(/dev/tty|COM)\w+",
                            "message": "Invalid port format",
                        },
                    ],
                ),
                FormField(
                    name="loadcell_baudrate",
                    label="Load Cell Baud Rate",
                    field_type="select",
                    value="9600",
                    required=True,
                    options=[
                        {"value": "9600", "label": "9600"},
                        {
                            "value": "19200",
                            "label": "19200",
                        },
                        {
                            "value": "38400",
                            "label": "38400",
                        },
                        {
                            "value": "115200",
                            "label": "115200",
                        },
                    ],
                ),
                FormField(
                    name="power_supply_ip",
                    label="Power Supply IP Address",
                    field_type="text",
                    value="192.168.1.100",
                    placeholder="192.168.1.100",
                    help_text="IP address for ODA power supply",
                    required=True,
                    validation_rules=[
                        {
                            "rule": "required",
                            "message": "IP address is required",
                        },
                        {
                            "rule": "pattern",
                            "pattern": r"^(\d{1,3}\.){3}\d{1,3}$",
                            "message": "Invalid IP format",
                        },
                    ],
                ),
                FormField(
                    name="dio_card_enabled",
                    label="Enable DIO Card",
                    field_type="checkbox",
                    value=True,
                    help_text="Enable Ajinextek DIO card for input control",
                ),
            ],
            SettingsCategory.TESTING.value: [
                FormField(
                    name="test_timeout",
                    label="Test Timeout (seconds)",
                    field_type="number",
                    value=300,
                    help_text="Maximum test execution time",
                    required=True,
                    validation_rules=[
                        {
                            "rule": "required",
                            "message": "Timeout is required",
                        },
                        {
                            "rule": "range",
                            "min": 10,
                            "max": 3600,
                            "message": "Timeout must be between 10-3600 seconds",
                        },
                    ],
                ),
                FormField(
                    name="measurement_samples",
                    label="Measurement Samples",
                    field_type="number",
                    value=10,
                    help_text="Number of samples per measurement",
                    required=True,
                    validation_rules=[
                        {
                            "rule": "range",
                            "min": 1,
                            "max": 100,
                            "message": "Samples must be between 1-100",
                        }
                    ],
                ),
                FormField(
                    name="retry_attempts",
                    label="Retry Attempts",
                    field_type="number",
                    value=3,
                    help_text="Number of retry attempts for failed tests",
                    validation_rules=[
                        {
                            "rule": "range",
                            "min": 0,
                            "max": 10,
                            "message": "Retries must be between 0-10",
                        }
                    ],
                ),
                FormField(
                    name="auto_save_results",
                    label="Auto-save Test Results",
                    field_type="checkbox",
                    value=True,
                    help_text="Automatically save test results to JSON file",
                ),
            ],
            SettingsCategory.COMMUNICATION.value: [
                FormField(
                    name="connection_timeout",
                    label="Connection Timeout (ms)",
                    field_type="number",
                    value=5000,
                    help_text="Timeout for hardware connections",
                    validation_rules=[
                        {
                            "rule": "range",
                            "min": 1000,
                            "max": 30000,
                            "message": "Timeout must be between 1000-30000ms",
                        }
                    ],
                ),
                FormField(
                    name="retry_delay",
                    label="Retry Delay (ms)",
                    field_type="number",
                    value=1000,
                    help_text="Delay between retry attempts",
                    validation_rules=[
                        {
                            "rule": "range",
                            "min": 100,
                            "max": 10000,
                            "message": "Delay must be between 100-10000ms",
                        }
                    ],
                ),
                FormField(
                    name="debug_communication",
                    label="Enable Communication Debug",
                    field_type="checkbox",
                    value=False,
                    help_text="Log detailed communication messages",
                ),
            ],
            SettingsCategory.UI_PREFERENCES.value: [
                FormField(
                    name="theme",
                    label="UI Theme",
                    field_type="select",
                    value="light",
                    options=[
                        {
                            "value": "light",
                            "label": "Light",
                        },
                        {"value": "dark", "label": "Dark"},
                        {
                            "value": "high_contrast",
                            "label": "High Contrast",
                        },
                    ],
                ),
                FormField(
                    name="auto_refresh",
                    label="Auto-refresh Dashboard",
                    field_type="checkbox",
                    value=True,
                    help_text="Automatically refresh dashboard data",
                ),
                FormField(
                    name="refresh_interval",
                    label="Refresh Interval (seconds)",
                    field_type="number",
                    value=5,
                    help_text="Dashboard refresh interval",
                    validation_rules=[
                        {
                            "rule": "range",
                            "min": 1,
                            "max": 60,
                            "message": "Interval must be between 1-60 seconds",
                        }
                    ],
                ),
            ],
        }


class SettingsFormComponent:
    """
    Modern settings form component with:
    - Real-time validation
    - Accessibility compliance
    - Category organization
    - Import/export functionality
    - Undo/redo support
    """

    def __init__(self, schema: Optional[SettingsSchema] = None):
        self.schema = schema or SettingsSchema()
        self._form_data: Dict[str, Any] = {}
        self._validation_errors: List[ValidationError] = []
        self._change_listeners: List[Callable[[str, Any, Any], None]] = []
        self._dirty_fields: set[str] = set()
        self._history: List[Dict[str, Any]] = []
        self._history_index = -1

        # Load initial values from schema
        self._load_initial_values()

    def _load_initial_values(self) -> None:
        """Load initial values from schema"""
        for category_fields in self.schema.categories.values():
            for form_field in category_fields:
                self._form_data[form_field.name] = form_field.value

    def get_field_value(self, field_name: str) -> Any:
        """Get current field value"""
        return self._form_data.get(field_name)

    def set_field_value(
        self,
        field_name: str,
        value: Any,
        validate: bool = True,
    ) -> bool:
        """Set field value with optional validation"""
        old_value = self._form_data.get(field_name)
        self._form_data[field_name] = value
        self._dirty_fields.add(field_name)

        if validate:
            field_errors = self._validate_field(field_name, value)
            # Remove old errors for this field
            self._validation_errors = [
                err for err in self._validation_errors if err.field_name != field_name
            ]
            # Add new errors
            self._validation_errors.extend(field_errors)

        # Notify listeners
        self._notify_change(field_name, old_value, value)

        return len([err for err in self._validation_errors if err.field_name == field_name]) == 0

    def _validate_field(self, field_name: str, value: Any) -> List[ValidationError]:
        """Validate individual field"""
        errors: List[ValidationError] = []
        form_field = self._find_field(field_name)

        if not form_field:
            return errors

        # Required validation
        if form_field.required and (value is None or value == ""):
            errors.append(
                ValidationError(
                    field_name=field_name,
                    rule=ValidationRule.REQUIRED,
                    message=f"{form_field.label} is required",
                    value=value,
                )
            )
            return errors  # Skip other validations if required field is empty

        # Skip other validations for empty optional fields
        if value is None or value == "":
            return errors

        # Apply validation rules
        for rule_config in form_field.validation_rules:
            rule_type = rule_config.get("rule")

            if rule_type == "pattern":
                pattern = rule_config.get("pattern")
                if pattern and not re.match(pattern, str(value)):
                    errors.append(
                        ValidationError(
                            field_name=field_name,
                            rule=ValidationRule.PATTERN,
                            message=rule_config.get(
                                "message",
                                f"Invalid format for {form_field.label}",
                            ),
                            value=value,
                        )
                    )

            elif rule_type == "range":
                min_val = rule_config.get("min")
                max_val = rule_config.get("max")
                try:
                    num_value = float(value)
                    if min_val is not None and num_value < min_val:
                        errors.append(
                            ValidationError(
                                field_name=field_name,
                                rule=ValidationRule.RANGE,
                                message=rule_config.get(
                                    "message",
                                    f"{form_field.label} must be at least {min_val}",
                                ),
                                value=value,
                            )
                        )
                    elif max_val is not None and num_value > max_val:
                        errors.append(
                            ValidationError(
                                field_name=field_name,
                                rule=ValidationRule.RANGE,
                                message=rule_config.get(
                                    "message",
                                    f"{form_field.label} must be at most {max_val}",
                                ),
                                value=value,
                            )
                        )
                except (ValueError, TypeError):
                    errors.append(
                        ValidationError(
                            field_name=field_name,
                            rule=ValidationRule.NUMBER,
                            message=f"{form_field.label} must be a valid number",
                            value=value,
                        )
                    )

        return errors

    def _find_field(self, field_name: str) -> Optional[FormField]:
        """Find field by name across all categories"""
        for category_fields in self.schema.categories.values():
            for form_field in category_fields:
                if form_field.name == field_name:
                    return form_field
        return None

    def validate_all(self) -> bool:
        """Validate all form fields"""
        self._validation_errors.clear()

        for field_name, value in self._form_data.items():
            field_errors = self._validate_field(field_name, value)
            self._validation_errors.extend(field_errors)

        return len(self._validation_errors) == 0

    def get_validation_errors(self, field_name: Optional[str] = None) -> List[ValidationError]:
        """Get validation errors for specific field or all"""
        if field_name:
            return [err for err in self._validation_errors if err.field_name == field_name]
        return self._validation_errors.copy()

    def save_to_history(self) -> None:
        """Save current state to history for undo/redo"""
        current_state = self._form_data.copy()

        # Remove states after current index (for redo)
        self._history = self._history[: self._history_index + 1]

        # Add new state
        self._history.append(current_state)
        self._history_index += 1

        # Limit history size
        if len(self._history) > 50:
            self._history = self._history[-50:]
            self._history_index = len(self._history) - 1

    def undo(self) -> bool:
        """Undo last change"""
        if self._history_index > 0:
            self._history_index -= 1
            self._form_data = self._history[self._history_index].copy()
            self._notify_change("undo", None, self._form_data)
            return True
        return False

    def redo(self) -> bool:
        """Redo last undone change"""
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._form_data = self._history[self._history_index].copy()
            self._notify_change("redo", None, self._form_data)
            return True
        return False

    def export_settings(self) -> Dict[str, Any]:
        """Export settings to dictionary"""
        return {
            "settings": self._form_data.copy(),
            "exported_at": datetime.now().isoformat(),
            "version": "1.0",
        }

    def import_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Import settings from dictionary"""
        try:
            if "settings" not in settings_data:
                return False

            # Validate imported data
            imported_settings = settings_data["settings"]
            for (
                field_name,
                value,
            ) in imported_settings.items():
                if self._find_field(field_name):
                    self.set_field_value(field_name, value, validate=True)

            return self.validate_all()

        except Exception:
            return False

    def reset_to_defaults(self) -> None:
        """Reset all fields to default values"""
        self.save_to_history()
        self._load_initial_values()
        self._dirty_fields.clear()
        self._validation_errors.clear()
        self._notify_change("reset", None, self._form_data)

    def is_dirty(self) -> bool:
        """Check if form has unsaved changes"""
        return len(self._dirty_fields) > 0

    def mark_clean(self) -> None:
        """Mark form as clean (saved)"""
        self._dirty_fields.clear()

    def render_form_ascii(self) -> str:
        """Render form as ASCII for CLI interface"""
        form_output = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                              Settings Configuration                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

"""

        for (
            category,
            fields,
        ) in self.schema.categories.items():
            form_output += (
                f"┌─ {category.upper().replace('_', ' ')} ─" + "─" * (70 - len(category)) + "┐\n"
            )

            for form_field in fields:
                value = self._form_data.get(form_field.name, "")
                errors = self.get_validation_errors(form_field.name)

                # Field label and value
                form_output += f"│ {form_field.label:.<30} : {str(value):<35} │\n"

                # Show validation errors
                if errors:
                    for error in errors:
                        form_output += f"│   ❌ {error.message:<65} │\n"

                # Show help text
                if form_field.help_text:
                    form_output += f"│   💡 {form_field.help_text:<65} │\n"

                form_output += "│" + " " * 74 + "│\n"

            form_output += "└" + "─" * 74 + "┘\n\n"

        # Show form status
        if self._validation_errors:
            form_output += f"⚠️  Form has {len(self._validation_errors)} validation errors\n"
        elif self.is_dirty():
            form_output += "📝 Form has unsaved changes\n"
        else:
            form_output += "✅ Form is valid and saved\n"

        return form_output

    def add_change_listener(self, callback: Callable[[str, Any, Any], None]) -> None:
        """Add change event listener"""
        self._change_listeners.append(callback)

    def _notify_change(
        self,
        field_name: str,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """Notify all change listeners"""
        for listener in self._change_listeners:
            try:
                listener(field_name, old_value, new_value)
            except Exception as e:
                print(f"Settings form listener error: {e}")


# Accessibility helper for form rendering
class FormAccessibilityHelper:
    """WCAG 2.1 AA compliance helper for forms"""

    @staticmethod
    def get_field_aria_attributes(form_field: FormField, has_errors: bool) -> Dict[str, str]:
        """Generate ARIA attributes for field"""
        attrs = {
            "aria-label": form_field.label,
            "aria-required": "true" if form_field.required else "false",
        }

        if form_field.help_text:
            attrs["aria-describedby"] = f"{form_field.name}_help"

        if has_errors:
            attrs["aria-invalid"] = "true"
            attrs["aria-describedby"] += f" {form_field.name}_error"

        return attrs

    @staticmethod
    def generate_error_announcement(
        errors: List[ValidationError],
    ) -> str:
        """Generate screen reader announcement for errors"""
        if not errors:
            return ""

        count = len(errors)
        return f"Form has {count} error{'s' if count > 1 else ''}. Please review and correct."
