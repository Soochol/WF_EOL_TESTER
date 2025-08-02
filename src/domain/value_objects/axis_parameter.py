"""
Axis Parameter Value Object

로봇 축 모션 파라미터를 담는 불변 값 객체
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AxisParameter:
    """로봇 축 모션 파라미터 값 객체"""

    axis: int
    velocity: float
    acceleration: float
    deceleration: float

    def validate_axis(self, expected_axis: int) -> None:
        """
        축 번호 검증

        Args:
            expected_axis: 예상되는 축 번호

        Raises:
            ValueError: 축 번호가 일치하지 않을 때
        """
        if self.axis != expected_axis:
            raise ValueError(f"Expected axis {expected_axis}, got {self.axis}")

    def __post_init__(self) -> None:
        """파라미터 유효성 검증"""
        if self.axis < 0:
            raise ValueError("Axis number cannot be negative")
        if self.velocity <= 0:
            raise ValueError("Velocity must be positive")
        if self.acceleration <= 0:
            raise ValueError("Acceleration must be positive")
        if self.deceleration <= 0:
            raise ValueError("Deceleration must be positive")