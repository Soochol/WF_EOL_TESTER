"""
Measurement Units Enumeration

Defines the units of measurement used in the EOL testing system.
"""

from enum import Enum


class MeasurementUnit(Enum):
    """Measurement unit enumeration"""
    # Force units
    NEWTON = "N"
    KILOGRAM_FORCE = "kgf"
    POUND_FORCE = "lbf"

    # Electrical units
    VOLT = "V"
    MILLIVOLT = "mV"
    AMPERE = "A"
    MILLIAMPERE = "mA"
    MICROAMPERE = "μA"
    OHM = "Ω"
    KILOOHM = "kΩ"
    MEGAOHM = "MΩ"

    # Time units
    SECOND = "s"
    MILLISECOND = "ms"
    MICROSECOND = "μs"

    # Temperature units
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    KELVIN = "K"

    # Position units
    MILLIMETER = "mm"
    MICROMETER = "μm"
    METER = "m"

    # Velocity units
    MM_PER_SEC = "mm/s"
    M_PER_SEC = "m/s"

    def __str__(self) -> str:
        return self.value

    @property
    def is_force_unit(self) -> bool:
        """Check if unit is for force measurement"""
        return self in (MeasurementUnit.NEWTON, MeasurementUnit.KILOGRAM_FORCE, MeasurementUnit.POUND_FORCE)

    @property
    def is_electrical_unit(self) -> bool:
        """Check if unit is for electrical measurement"""
        return self in (
            MeasurementUnit.VOLT, MeasurementUnit.MILLIVOLT,
            MeasurementUnit.AMPERE, MeasurementUnit.MILLIAMPERE, MeasurementUnit.MICROAMPERE,
            MeasurementUnit.OHM, MeasurementUnit.KILOOHM, MeasurementUnit.MEGAOHM
        )

    @property
    def is_time_unit(self) -> bool:
        """Check if unit is for time measurement"""
        return self in (MeasurementUnit.SECOND, MeasurementUnit.MILLISECOND, MeasurementUnit.MICROSECOND)
