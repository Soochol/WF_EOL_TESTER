"""
Database Schema Definition

SQLAlchemy models for test data logging.
"""

# Standard library imports
from datetime import datetime
from typing import Optional

# Third-party imports
from sqlalchemy import JSON, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


class TestResult(Base):
    """Test result table - stores JSON test result data"""

    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    dut_id: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    operator_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    start_time: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    test_configuration: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationship to raw measurements
    raw_measurements: Mapped[list["RawMeasurement"]] = relationship(
        back_populates="test_result", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_test_id", "test_id"),
        Index("idx_serial_number", "serial_number"),
        Index("idx_created_at", "created_at"),
        Index("idx_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<TestResult(test_id='{self.test_id}', status='{self.status}')>"


class RawMeasurement(Base):
    """Raw measurement table - stores CSV raw data"""

    __tablename__ = "raw_measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("test_results.test_id", ondelete="CASCADE"), nullable=False
    )
    serial_number: Mapped[str] = mapped_column(String(255), nullable=False)
    cycle_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    force: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationship to test result
    test_result: Mapped["TestResult"] = relationship(back_populates="raw_measurements")

    # Indexes
    __table_args__ = (
        Index("idx_raw_test_id", "test_id"),
        Index("idx_raw_serial", "serial_number"),
        Index("idx_raw_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<RawMeasurement(test_id='{self.test_id}', temp={self.temperature}, force={self.force})>"
