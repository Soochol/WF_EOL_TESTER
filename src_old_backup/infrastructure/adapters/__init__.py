"""
Infrastructure Adapters

Adapter layer that provides business logic abstraction over hardware controllers.
This layer bridges the gap between domain requirements and hardware specifics.
"""

from .robot_adapter_impl import RobotAdapterImpl

__all__ = [
    'RobotAdapterImpl'
]