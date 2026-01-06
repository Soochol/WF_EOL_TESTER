"""Unit Converter for Position Values

Converts position values between micrometers (μm) and millimeters (mm).
"""


class PositionUnitConverter:
    """Position unit conversion utility (μm ↔ mm)"""

    @staticmethod
    def um_to_mm(position_um: float) -> float:
        """
        Convert micrometers to millimeters

        Args:
            position_um: Position in micrometers (μm)

        Returns:
            Position in millimeters (mm)

        Examples:
            >>> PositionUnitConverter.um_to_mm(170000.0)
            170.0
            >>> PositionUnitConverter.um_to_mm(150000.0)
            150.0
        """
        return position_um / 1000.0

    @staticmethod
    def mm_to_um(position_mm: float) -> float:
        """
        Convert millimeters to micrometers

        Args:
            position_mm: Position in millimeters (mm)

        Returns:
            Position in micrometers (μm)

        Examples:
            >>> PositionUnitConverter.mm_to_um(170.0)
            170000.0
            >>> PositionUnitConverter.mm_to_um(150.0)
            150000.0
        """
        return position_mm * 1000.0

    @staticmethod
    def format_position_mm(position_um: float, precision: int = 1) -> str:
        """
        Format position in μm as mm string

        Args:
            position_um: Position in micrometers (μm)
            precision: Number of decimal places (default: 1)

        Returns:
            Formatted string (e.g., "170.0 mm")

        Examples:
            >>> PositionUnitConverter.format_position_mm(170000.0)
            "170.0 mm"
            >>> PositionUnitConverter.format_position_mm(170000.0, 2)
            "170.00 mm"
            >>> PositionUnitConverter.format_position_mm(150000.0)
            "150.0 mm"
        """
        mm = position_um / 1000.0
        return f"{mm:.{precision}f} mm"
