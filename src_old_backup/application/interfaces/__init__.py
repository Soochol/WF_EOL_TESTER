"""
Application Interfaces Package

Contains interface definitions that must be implemented by infrastructure layer.
These interfaces define contracts for external dependencies like hardware services,
repositories, and external services.
"""

from .power_service import PowerService
from .loadcell_service import LoadCellService
from .dio_service import DIOService
from .mcu_service import MCUService
from .robot_service import RobotService
from .test_repository import TestRepository
from .measurement_repository import MeasurementRepository
from .notification_service import NotificationService
from .report_generator_service import ReportGeneratorService

__all__ = [
    'PowerService',
    'LoadCellService',
    'DIOService',
    'MCUService', 
    'RobotService',
    'TestRepository',
    'MeasurementRepository',
    'NotificationService',
    'ReportGeneratorService'
]