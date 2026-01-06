"""
Connection Container (Layer 2)

Manages hardware connection lifecycle and pooling.
Preserves active connections during configuration changes and provides
connection state management for hardware services.
"""

# Standard library imports
from typing import Dict, Optional, Any
import weakref

# Third-party imports
from dependency_injector import containers, providers
from loguru import logger

# Local application imports
from application.containers.configuration_container import ConfigurationContainer
from application.services.hardware_facade import HardwareServiceFacade
from infrastructure.factories.hardware_factory import HardwareFactory


class ConnectionManager:
    """
    Manages hardware connection lifecycle and state preservation.

    This class tracks active connections and provides mechanisms to preserve
    them during configuration changes, avoiding unnecessary disconnections.
    """

    def __init__(self):
        self._active_connections: Dict[str, Any] = {}
        self._connection_states: Dict[str, dict] = {}
        self._weak_refs: Dict[str, weakref.ReferenceType] = {}

    def register_connection(self, service_name: str, service_instance: Any) -> None:
        """Register an active hardware service connection."""
        try:
            self._active_connections[service_name] = service_instance

            # Create weak reference to avoid circular dependencies
            self._weak_refs[service_name] = weakref.ref(service_instance)

            # Store connection state if available
            if hasattr(service_instance, 'get_connection_state'):
                self._connection_states[service_name] = service_instance.get_connection_state()

            logger.debug(f"🔌 Registered connection for {service_name}")

        except Exception as e:
            logger.error(f"Failed to register connection for {service_name}: {e}")

    def get_connection(self, service_name: str) -> Optional[Any]:
        """Get an active connection if it exists and is still valid."""
        try:
            # Check if we have an active connection
            if service_name in self._active_connections:
                service = self._active_connections[service_name]

                # Verify connection is still alive using weak reference
                weak_ref = self._weak_refs.get(service_name)
                if weak_ref and weak_ref() is not None:
                    # Additional health check if available
                    if hasattr(service, 'is_connected') and service.is_connected():
                        logger.debug(f"🔌 Reusing active connection for {service_name}")
                        return service
                    elif not hasattr(service, 'is_connected'):
                        # No health check available, assume it's good
                        logger.debug(f"🔌 Reusing connection for {service_name} (no health check)")
                        return service

                # Connection is dead, clean up
                self._cleanup_connection(service_name)

            return None

        except Exception as e:
            logger.error(f"Error checking connection for {service_name}: {e}")
            self._cleanup_connection(service_name)
            return None

    def _cleanup_connection(self, service_name: str) -> None:
        """Clean up a dead or invalid connection."""
        try:
            if service_name in self._active_connections:
                del self._active_connections[service_name]
            if service_name in self._weak_refs:
                del self._weak_refs[service_name]
            if service_name in self._connection_states:
                del self._connection_states[service_name]

            logger.debug(f"🧹 Cleaned up connection for {service_name}")

        except Exception as e:
            logger.error(f"Error cleaning up connection for {service_name}: {e}")

    def preserve_connections(self) -> Dict[str, Any]:
        """Get all active connections for preservation during reload."""
        preserved = {}

        for service_name, service in self._active_connections.items():
            weak_ref = self._weak_refs.get(service_name)
            if weak_ref and weak_ref() is not None:
                preserved[service_name] = service

        logger.info(f"🔒 Preserving {len(preserved)} active connections")
        return preserved

    def restore_connections(self, preserved_connections: Dict[str, Any]) -> None:
        """Restore preserved connections after reload."""
        try:
            for service_name, service in preserved_connections.items():
                self.register_connection(service_name, service)

            logger.info(f"🔄 Restored {len(preserved_connections)} connections")

        except Exception as e:
            logger.error(f"Error restoring connections: {e}")

    def disconnect_all(self) -> None:
        """Disconnect all active connections (used during shutdown)."""
        try:
            for service_name, service in self._active_connections.items():
                if hasattr(service, 'disconnect'):
                    try:
                        service.disconnect()
                        logger.debug(f"🔌 Disconnected {service_name}")
                    except Exception as e:
                        logger.error(f"Error disconnecting {service_name}: {e}")

            self._active_connections.clear()
            self._weak_refs.clear()
            self._connection_states.clear()

            logger.info("🔌 All connections disconnected")

        except Exception as e:
            logger.error(f"Error during disconnect_all: {e}")


class ConnectionContainer(containers.DeclarativeContainer):
    """
    Layer 2: Connection Management Container

    Responsibilities:
    - Hardware connection lifecycle management
    - Connection pooling and preservation
    - Hardware factory management with configuration sync
    - Connection state tracking and restoration

    This container preserves active connections during configuration changes.
    """

    # ============================================================================
    # CONFIGURATION DEPENDENCY (will be set dynamically)
    # ============================================================================

    # Configuration data (will be injected dynamically)
    config = providers.Configuration()

    # ============================================================================
    # CONNECTION MANAGEMENT
    # ============================================================================

    # Connection manager for lifecycle management
    connection_manager = providers.Singleton(ConnectionManager)

    # ============================================================================
    # HARDWARE INFRASTRUCTURE
    # ============================================================================

    # Hardware factory with configuration dependency
    hardware_factory = providers.Container(HardwareFactory, config=config.hardware)

    # GUI State Manager (optional, set by GUI application)
    gui_state_manager = providers.Object(None)

    # Hardware service facade with connection management
    hardware_service_facade = providers.Singleton(
        HardwareServiceFacade,
        robot_service=hardware_factory.robot_service,
        mcu_service=hardware_factory.mcu_service,
        loadcell_service=hardware_factory.loadcell_service,
        power_service=hardware_factory.power_service,
        digital_io_service=hardware_factory.digital_io_service,
        gui_state_manager=gui_state_manager,
    )

    # ============================================================================
    # CONNECTION MANAGEMENT METHODS
    # ============================================================================

    def sync_configuration(self, config_container: ConfigurationContainer) -> bool:
        """
        Synchronize hardware configuration with new config container.

        Args:
            config_container: Updated configuration container

        Returns:
            bool: True if sync was successful
        """
        try:
            logger.info("🔄 Synchronizing ConnectionContainer configuration...")

            # Get all configuration data from the config container
            app_config = config_container.get_application_config()
            hardware_config = config_container.get_hardware_config()

            # Update our configuration provider with the combined data
            combined_config = app_config.copy()
            combined_config['hardware'] = hardware_config

            self.config.from_dict(combined_config)
            logger.info("🔄 ConnectionContainer configuration synchronized")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to synchronize ConnectionContainer config: {e}")
            return False

    def reload_with_connection_preservation(self, config_container: ConfigurationContainer) -> bool:
        """
        Reload hardware services while preserving active connections where possible.

        Args:
            config_container: Updated configuration container

        Returns:
            bool: True if reload was successful
        """
        try:
            logger.info("🔄 Starting connection-preserving reload...")

            # Step 1: Preserve current connections
            connection_mgr = self.connection_manager()
            preserved_connections = connection_mgr.preserve_connections()

            # Step 2: Synchronize configuration
            sync_success = self.sync_configuration(config_container)
            if not sync_success:
                logger.warning("⚠️ Configuration sync failed, proceeding with reload anyway")

            # Step 3: Reset hardware factory providers to pick up new config
            self._reset_hardware_factory_providers()

            # Step 4: Reset hardware service facade to force recreation
            if hasattr(self.hardware_service_facade, 'reset'):
                self.hardware_service_facade.reset()
                logger.info("🔄 Reset hardware_service_facade")

            # Step 5: Restore connections where possible
            connection_mgr.restore_connections(preserved_connections)

            logger.info("✅ Connection-preserving reload completed")
            return True

        except Exception as e:
            logger.error(f"❌ Connection-preserving reload failed: {e}")
            return False

    def _reset_hardware_factory_providers(self) -> None:
        """Reset HardwareFactory providers to pick up new configuration."""
        hardware_factory_providers = [
            "robot_service",
            "power_service",
            "mcu_service",
            "loadcell_service",
            "digital_io_service",
        ]

        for provider_name in hardware_factory_providers:
            try:
                provider = getattr(self.hardware_factory, provider_name)
                if hasattr(provider, 'reset'):
                    provider.reset()
                    logger.info(f"🔄 Reset HardwareFactory.{provider_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to reset HardwareFactory.{provider_name}: {e}")

    def register_hardware_service(self, service_name: str, service_instance: Any) -> None:
        """Register a hardware service with the connection manager."""
        connection_mgr = self.connection_manager()
        connection_mgr.register_connection(service_name, service_instance)

    def get_preserved_connection(self, service_name: str) -> Optional[Any]:
        """Get a preserved connection if available."""
        connection_mgr = self.connection_manager()
        return connection_mgr.get_connection(service_name)

    def disconnect_all_hardware(self) -> None:
        """Disconnect all hardware connections (used during shutdown)."""
        try:
            connection_mgr = self.connection_manager()
            connection_mgr.disconnect_all()
            logger.info("🔌 All hardware connections disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting all hardware: {e}")

    @classmethod
    def create(cls, config_container: ConfigurationContainer) -> "ConnectionContainer":
        """
        Create connection container with configuration dependency.

        Args:
            config_container: Configuration container to use

        Returns:
            Configured ConnectionContainer instance
        """
        container = cls()

        # Synchronize configuration data
        container.sync_configuration(config_container)

        logger.info("🔌 ConnectionContainer created successfully")
        return container
