"""Dependency Injection Container

Service container for dependency management with interface-to-implementation
mapping, lifecycle management, and configuration-based service registration.
Supports singleton and transient lifetimes with circular dependency detection.

Key Features:
- Interface-to-implementation mapping
- Service lifetime management (singleton, transient)
- Circular dependency detection and resolution
- Configuration-driven service registration
- Type-safe dependency resolution
"""

from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, TypeVar, cast

from loguru import logger

# Type variable for generic type handling
T = TypeVar("T")


class ServiceLifetime(Enum):
    """Enumeration for service lifetime management.

    Defines how long service instances should be kept alive
    and when new instances should be created.
    """

    SINGLETON = "singleton"  # Single instance shared across all requests
    TRANSIENT = "transient"  # New instance created for each request


class ServiceRegistration:
    """Registration information for a service.

    Contains all information needed to create and manage a service instance
    including the implementation type, factory function, and lifetime.
    """

    def __init__(
        self,
        interface_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    ):
        """Initialize service registration.

        Args:
            interface_type: The interface type being registered
            implementation_type: The concrete implementation type
            factory: Optional factory function for creating instances
            lifetime: Service lifetime management strategy
        """
        self.interface_type = interface_type
        self.implementation_type = implementation_type
        self.factory = factory
        self.lifetime = lifetime

        if not implementation_type and not factory:
            raise ValueError("Either implementation_type or factory must be provided")


class DependencyContainer:
    """Service container for dependency injection and lifecycle management.

    Provides interface-to-implementation mapping with lifecycle management,
    circular dependency detection, and configuration-driven service registration.
    Supports both singleton and transient service lifetimes.
    """

    def __init__(self):
        """Initialize the dependency container."""
        self._registrations: Dict[Type, ServiceRegistration] = {}
        self._singletons: Dict[Type, Any] = {}
        self._resolution_stack: set = set()  # For circular dependency detection

    def register(
        self,
        interface_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    ) -> "DependencyContainer":
        """Register a service with the container.

        Args:
            interface_type: The interface type to register
            implementation_type: The concrete implementation type
            factory: Optional factory function for creating instances
            lifetime: Service lifetime management strategy

        Returns:
            Self for method chaining

        Raises:
            ValueError: If neither implementation_type nor factory is provided
        """
        registration = ServiceRegistration(
            interface_type=interface_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=lifetime,
        )

        self._registrations[interface_type] = registration
        logger.debug(f"Registered {interface_type.__name__} with lifetime {lifetime.value}")

        return self

    def register_singleton(
        self,
        interface_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> "DependencyContainer":
        """Register a singleton service with the container.

        Args:
            interface_type: The interface type to register
            implementation_type: The concrete implementation type
            factory: Optional factory function for creating instances

        Returns:
            Self for method chaining
        """
        return self.register(
            interface_type=interface_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=ServiceLifetime.SINGLETON,
        )

    def register_transient(
        self,
        interface_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> "DependencyContainer":
        """Register a transient service with the container.

        Args:
            interface_type: The interface type to register
            implementation_type: The concrete implementation type
            factory: Optional factory function for creating instances

        Returns:
            Self for method chaining
        """
        return self.register(
            interface_type=interface_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=ServiceLifetime.TRANSIENT,
        )

    def register_instance(self, interface_type: Type[T], instance: T) -> "DependencyContainer":
        """Register a specific instance as a singleton.

        Args:
            interface_type: The interface type to register
            instance: The specific instance to use

        Returns:
            Self for method chaining
        """
        self._registrations[interface_type] = ServiceRegistration(
            interface_type=interface_type,
            factory=lambda: instance,
            lifetime=ServiceLifetime.SINGLETON,
        )
        self._singletons[interface_type] = instance
        logger.debug(f"Registered instance for {interface_type.__name__}")

        return self

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance from the container.

        Args:
            service_type: The service type to resolve

        Returns:
            Service instance implementing the requested type

        Raises:
            ValueError: If service is not registered or circular dependency detected
        """
        # Check for circular dependency
        if service_type in self._resolution_stack:
            raise ValueError(f"Circular dependency detected for {service_type.__name__}")

        # Check if service is registered
        if service_type not in self._registrations:
            raise ValueError(f"Service {service_type.__name__} is not registered")

        registration = self._registrations[service_type]

        # Handle singleton lifetime
        if registration.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singletons:
                return self._singletons[service_type]

        # Add to resolution stack for circular dependency detection
        self._resolution_stack.add(service_type)

        try:
            # Create instance
            if registration.factory:
                instance = registration.factory()
            elif registration.implementation_type:
                instance = self._create_instance(registration.implementation_type)
            else:
                raise ValueError(f"No implementation or factory for {service_type.__name__}")

            # Store singleton instance
            if registration.lifetime == ServiceLifetime.SINGLETON:
                self._singletons[service_type] = instance

            logger.debug(f"Resolved {service_type.__name__} as {type(instance).__name__}")
            return cast(T, instance)

        finally:
            # Remove from resolution stack
            self._resolution_stack.discard(service_type)

    def _create_instance(self, implementation_type: Type[T]) -> T:
        """Create an instance with dependency injection.

        Args:
            implementation_type: The concrete type to instantiate

        Returns:
            New instance with dependencies injected
        """
        try:
            # Get constructor signature
            import inspect

            signature = inspect.signature(implementation_type.__init__)

            # Resolve constructor dependencies
            kwargs = {}
            for param_name, param in signature.parameters.items():
                if param_name == "self":
                    continue

                # Check if parameter has type annotation
                if param.annotation != inspect.Parameter.empty:
                    # Try to resolve dependency
                    try:
                        dependency = self.resolve(param.annotation)
                        kwargs[param_name] = dependency
                    except ValueError:
                        # Dependency not registered - check if parameter has default
                        if param.default == inspect.Parameter.empty:
                            logger.warning(
                                f"Could not resolve dependency {param.annotation.__name__} "
                                f"for {implementation_type.__name__}.{param_name}"
                            )

            # Create instance with resolved dependencies
            return implementation_type(**kwargs)

        except Exception as e:
            logger.error(f"Failed to create instance of {implementation_type.__name__}: {e}")
            raise ValueError(f"Failed to create {implementation_type.__name__}: {e}") from e

    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered.

        Args:
            service_type: The service type to check

        Returns:
            True if the service is registered, False otherwise
        """
        return service_type in self._registrations

    def clear(self) -> None:
        """Clear all registrations and singleton instances."""
        self._registrations.clear()
        self._singletons.clear()
        self._resolution_stack.clear()
        logger.debug("Dependency container cleared")

    def get_registered_services(self) -> Dict[Type, ServiceRegistration]:
        """Get all registered services.

        Returns:
            Dictionary of registered services and their registrations
        """
        return self._registrations.copy()
