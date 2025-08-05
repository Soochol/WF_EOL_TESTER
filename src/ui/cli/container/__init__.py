"""Dependency Injection Container Package

Provides service container for dependency management, interface-to-implementation
mapping, and lifecycle management for CLI components. Supports configuration-based
service registration and dependency resolution.

Components:
- DependencyContainer: Main service container for dependency management
- ServiceLifetime: Enumeration for service lifetime management
- ServiceRegistration: Registration information for services
"""

from .dependency_container import (
    DependencyContainer,
    ServiceLifetime,
    ServiceRegistration,
)

__all__ = [
    "DependencyContainer",
    "ServiceLifetime",
    "ServiceRegistration",
]