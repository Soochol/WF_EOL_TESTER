"""
NeuroHub MES 연동 설정 Value Object

NeuroHub Client와의 TCP/IP 통신 설정을 담는 불변 Value Object.
"""

from dataclasses import dataclass

from domain.exceptions.validation_exceptions import ValidationException


@dataclass(frozen=True)
class NeuroHubConfig:
    """
    NeuroHub MES 연동 설정

    Attributes:
        enabled: NeuroHub 연동 활성화 여부
        host: NeuroHub Client 호스트 주소
        port: NeuroHub Client TCP 포트
        timeout: 연결 타임아웃 (초)
        retry_attempts: 재시도 횟수
        retry_delay: 재시도 간격 (초)
    """

    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 9000
    timeout: float = 5.0
    retry_attempts: int = 3
    retry_delay: float = 1.0

    def __post_init__(self) -> None:
        """설정 유효성 검증"""
        if not 1 <= self.port <= 65535:
            raise ValidationException(
                "neurohub.port",
                self.port,
                "Port must be between 1 and 65535",
            )
        if self.timeout <= 0:
            raise ValidationException(
                "neurohub.timeout",
                self.timeout,
                "Timeout must be positive",
            )
        if self.retry_attempts < 1:
            raise ValidationException(
                "neurohub.retry_attempts",
                self.retry_attempts,
                "Retry attempts must be at least 1",
            )
        if self.retry_delay < 0:
            raise ValidationException(
                "neurohub.retry_delay",
                self.retry_delay,
                "Retry delay must be non-negative",
            )
