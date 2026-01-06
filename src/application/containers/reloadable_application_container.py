"""
Reloadable Application Container (Orchestrator)

Coordinates all container layers and implements intelligent hot-reload mechanisms.
Provides selective reload strategies based on change types while preserving connections.
"""

# Standard library imports
from enum import Enum
from typing import Optional, Dict, Callable
import hashlib
import json

# Third-party imports
from dependency_injector import containers, providers
from loguru import logger

# Local application imports
from application.containers.configuration_container import ConfigurationContainer
from application.containers.connection_container import ConnectionContainer
from application.containers.service_container import ServiceContainer


class ChangeType(Enum):
    """Types of configuration changes that require different reload strategies."""
    CONFIG_ONLY = "config_only"        # Parameter changes only
    MODEL_CHANGE = "model_change"      # Hardware model changes
    SERVICE_LOGIC = "service_logic"    # Business logic changes
    FULL_RELOAD = "full_reload"        # Complete reload required


class ReloadableApplicationContainer:
    """
    Orchestrator for layered container architecture with intelligent hot-reload.

    This container coordinates three layers:
    1. ConfigurationContainer - Configuration management
    2. ConnectionContainer - Hardware connection lifecycle
    3. ServiceContainer - Business services and use cases

    Implements selective reload strategies to minimize disruption:
    - Config-only changes: reload ConfigurationContainer only
    - Model changes: reload ConnectionContainer + dependent services
    - Service logic changes: reload ServiceContainer only
    - Full reload: complete container recreation
    """

    def __init__(self):
        self._config_container: Optional[ConfigurationContainer] = None
        self._connection_container: Optional[ConnectionContainer] = None
        self._service_container: Optional[ServiceContainer] = None

        # Configuration change detection
        self._last_config_hash: Optional[str] = None
        self._last_hardware_config_hash: Optional[str] = None

        # Reload callbacks for external components
        self._reload_callbacks: Dict[str, Callable] = {}

        logger.info("🏗️ ReloadableApplicationContainer initialized")

    # ============================================================================
    # INITIALIZATION METHODS
    # ============================================================================

    @classmethod
    def create(cls) -> "ReloadableApplicationContainer":
        """
        Create and initialize the complete container stack.

        Returns:
            Configured ReloadableApplicationContainer instance
        """
        container = cls()

        try:
            # Layer 1: Configuration
            container._config_container = ConfigurationContainer.create()

            # Layer 2: Connections (depends on Configuration)
            container._connection_container = ConnectionContainer.create(
                container._config_container
            )

            # Layer 3: Services (depends on Configuration + Connections)
            container._service_container = ServiceContainer.create(
                container._config_container,
                container._connection_container
            )

            # Initialize configuration hashes for change detection
            container._update_config_hashes()

            logger.info("🏗️ ReloadableApplicationContainer created successfully")

        except Exception as e:
            logger.error(f"❌ Failed to create ReloadableApplicationContainer: {e}")
            raise

        return container

    @classmethod
    def create_with_paths(cls, **kwargs) -> "ReloadableApplicationContainer":
        """
        Create container with configuration paths (legacy compatibility method).

        Note: Path arguments are ignored as they're managed internally via value objects.

        Returns:
            Configured ReloadableApplicationContainer instance
        """
        # Path arguments are silently ignored for compatibility
        if kwargs:
            logger.warning(f"Path arguments are ignored: {list(kwargs.keys())}")

        return cls.create()

    @classmethod
    def ensure_config_exists(cls, **kwargs) -> None:
        """
        Ensure configuration files exist, create from defaults if missing.

        Note: Path arguments are ignored. Uses default paths from ConfigPaths.
        """
        if kwargs:
            logger.warning(f"Path arguments are ignored: {list(kwargs.keys())}")

        try:
            ConfigurationContainer.ensure_config_exists()
            logger.info("🔧 Configuration files ensured via ReloadableApplicationContainer")
        except Exception as e:
            logger.error(f"Failed to ensure configuration files exist: {e}")

    # ============================================================================
    # CONTAINER ACCESS METHODS
    # ============================================================================

    @property
    def config_container(self) -> ConfigurationContainer:
        """Get the configuration container."""
        if self._config_container is None:
            raise RuntimeError("ConfigurationContainer not initialized")
        return self._config_container

    @property
    def connection_container(self) -> ConnectionContainer:
        """Get the connection container."""
        if self._connection_container is None:
            raise RuntimeError("ConnectionContainer not initialized")
        return self._connection_container

    @property
    def service_container(self) -> ServiceContainer:
        """Get the service container."""
        if self._service_container is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._service_container

    # Legacy compatibility properties - delegate to appropriate containers
    @property
    def configuration_service(self):
        """Legacy compatibility: get configuration service."""
        return self.config_container.configuration_service

    @property
    def hardware_service_facade(self):
        """Legacy compatibility: get hardware service facade."""
        return self.connection_container.hardware_service_facade

    @property
    def eol_force_test_use_case(self):
        """Legacy compatibility: get EOL force test use case."""
        return self.service_container.eol_force_test_use_case

    @property
    def robot_home_use_case(self):
        """Legacy compatibility: get robot home use case."""
        return self.service_container.robot_home_use_case

    @property
    def heating_cooling_time_test_use_case(self):
        """Legacy compatibility: get heating cooling test use case."""
        return self.service_container.heating_cooling_time_test_use_case

    @property
    def simple_mcu_test_use_case(self):
        """Legacy compatibility: get simple MCU test use case."""
        return self.service_container.simple_mcu_test_use_case

    @property
    def gui_state_manager(self):
        """Legacy compatibility: get/set GUI state manager."""
        return self.connection_container.gui_state_manager

    @gui_state_manager.setter
    def gui_state_manager(self, value):
        """Legacy compatibility: set GUI state manager."""
        self.connection_container.gui_state_manager.override(value)

    # ============================================================================
    # CHANGE DETECTION METHODS
    # ============================================================================

    def _compute_config_hash(self, config_data: dict) -> str:
        """Compute hash of configuration data for change detection."""
        try:
            # Sort keys to ensure consistent hashing
            config_json = json.dumps(config_data, sort_keys=True)
            return hashlib.md5(config_json.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to compute config hash: {e}")
            return ""

    def _update_config_hashes(self) -> None:
        """Update stored configuration hashes for change detection."""
        try:
            # Get current configurations
            app_config = self.config_container.get_application_config()
            hardware_config = self.config_container.get_hardware_config()

            # Update hashes
            self._last_config_hash = self._compute_config_hash(app_config)
            self._last_hardware_config_hash = self._compute_config_hash(hardware_config)

        except Exception as e:
            logger.error(f"Failed to update config hashes: {e}")

    def _detect_change_type(self) -> ChangeType:
        """
        Detect the type of configuration change to determine reload strategy.

        Returns:
            ChangeType: The type of change detected
        """
        try:
            # Get current configurations
            app_config = self.config_container.get_application_config()
            hardware_config = self.config_container.get_hardware_config()

            # Compute current hashes
            current_config_hash = self._compute_config_hash(app_config)
            current_hardware_hash = self._compute_config_hash(hardware_config)

            # Compare with previous hashes
            config_changed = current_config_hash != self._last_config_hash
            hardware_changed = current_hardware_hash != self._last_hardware_config_hash

            if not config_changed and not hardware_changed:
                return ChangeType.CONFIG_ONLY  # No real changes

            if hardware_changed:
                # Check if it's a model change (affects connections)
                prev_hardware = self.config_container.get_hardware_config()
                models_changed = self._detect_model_changes(prev_hardware, hardware_config)

                if models_changed:
                    return ChangeType.MODEL_CHANGE
                else:
                    return ChangeType.CONFIG_ONLY

            if config_changed:
                return ChangeType.SERVICE_LOGIC

            return ChangeType.CONFIG_ONLY

        except Exception as e:
            logger.error(f"Error detecting change type: {e}")
            return ChangeType.FULL_RELOAD

    def _detect_model_changes(self, old_config: dict, new_config: dict) -> bool:
        """Detect if hardware model configurations changed."""
        try:
            # Check model fields that affect connections
            model_fields = [
                ('robot', 'model'),
                ('power', 'model'),
                ('mcu', 'model'),
                ('loadcell', 'model'),
                ('digital_io', 'model'),
            ]

            for category, field in model_fields:
                old_value = old_config.get(category, {}).get(field)
                new_value = new_config.get(category, {}).get(field)

                if old_value != new_value:
                    logger.info(f"🔄 Model change detected: {category}.{field} {old_value} -> {new_value}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error detecting model changes: {e}")
            return True  # Assume model change to be safe

    # ============================================================================
    # RELOAD METHODS
    # ============================================================================

    def reload_configuration(self) -> bool:
        """
        Intelligent configuration reload with change detection.

        Analyzes the type of changes and applies the most appropriate reload strategy:
        - Config-only changes: minimal reload
        - Model changes: connection-preserving reload
        - Service logic changes: service reload only
        - Full reload: complete recreation

        Returns:
            bool: True if reload was successful
        """
        try:
            logger.info("🔄 Starting intelligent configuration reload...")

            # Step 1: Reload configuration data
            config_reload_success = self.config_container.reload_configuration()
            if not config_reload_success:
                logger.error("❌ Configuration reload failed")
                return False

            # Step 2: Detect change type
            change_type = self._detect_change_type()
            logger.info(f"🔍 Detected change type: {change_type.value}")

            # Step 3: Apply appropriate reload strategy
            reload_success = False

            if change_type == ChangeType.CONFIG_ONLY:
                reload_success = self._reload_config_only()

            elif change_type == ChangeType.MODEL_CHANGE:
                reload_success = self._reload_with_connection_preservation()

            elif change_type == ChangeType.SERVICE_LOGIC:
                reload_success = self._reload_services_only()

            else:  # FULL_RELOAD
                reload_success = self._reload_full()

            # Step 4: Update hashes if successful
            if reload_success:
                self._update_config_hashes()
                self._notify_reload_callbacks()
                logger.info("✅ Intelligent configuration reload completed successfully")
            else:
                logger.error("❌ Configuration reload failed")

            return reload_success

        except Exception as e:
            logger.error(f"❌ Intelligent configuration reload failed: {e}")
            return False

    def _reload_config_only(self) -> bool:
        """Reload configuration data only, no service reset required."""
        try:
            logger.info("🔄 Performing config-only reload...")

            # Configuration container already reloaded, just sync dependencies
            sync_success = True

            # Sync configuration to connection container
            sync_success &= self.connection_container.sync_configuration(self.config_container)

            # Sync configuration to service container
            sync_success &= self.service_container.sync_configuration(
                self.config_container, self.connection_container
            )

            logger.info("✅ Config-only reload completed")
            return sync_success

        except Exception as e:
            logger.error(f"❌ Config-only reload failed: {e}")
            return False

    def _reload_with_connection_preservation(self) -> bool:
        """Reload with hardware connection preservation (for model changes)."""
        try:
            logger.info("🔄 Performing connection-preserving reload...")

            # Reload connection container with preservation
            connection_success = self.connection_container.reload_with_connection_preservation(
                self.config_container
            )

            if not connection_success:
                logger.error("❌ Connection container reload failed")
                return False

            # Sync and reload service container
            service_sync_success = self.service_container.sync_configuration(
                self.config_container, self.connection_container
            )
            service_reload_success = self.service_container.reload_services()

            success = connection_success and service_sync_success and service_reload_success
            logger.info("✅ Connection-preserving reload completed")
            return success

        except Exception as e:
            logger.error(f"❌ Connection-preserving reload failed: {e}")
            return False

    def _reload_services_only(self) -> bool:
        """Reload business services only (for service logic changes)."""
        try:
            logger.info("🔄 Performing services-only reload...")

            # Sync configuration to service container
            sync_success = self.service_container.sync_configuration(
                self.config_container, self.connection_container
            )

            # Reload services
            reload_success = self.service_container.reload_services()

            success = sync_success and reload_success
            logger.info("✅ Services-only reload completed")
            return success

        except Exception as e:
            logger.error(f"❌ Services-only reload failed: {e}")
            return False

    def _reload_full(self) -> bool:
        """Perform full container recreation (fallback for complex changes)."""
        try:
            logger.info("🔄 Performing full container reload...")

            # Disconnect all hardware before recreation
            self.connection_container.disconnect_all_hardware()

            # Recreate all containers
            self._config_container = ConfigurationContainer.create()
            self._connection_container = ConnectionContainer.create(self._config_container)
            self._service_container = ServiceContainer.create(
                self._config_container, self._connection_container
            )

            logger.info("✅ Full container reload completed")
            return True

        except Exception as e:
            logger.error(f"❌ Full container reload failed: {e}")
            return False

    # ============================================================================
    # CALLBACK MANAGEMENT
    # ============================================================================

    def register_reload_callback(self, name: str, callback: Callable) -> None:
        """Register a callback to be notified when reload completes."""
        self._reload_callbacks[name] = callback
        logger.debug(f"📞 Registered reload callback: {name}")

    def unregister_reload_callback(self, name: str) -> None:
        """Unregister a reload callback."""
        if name in self._reload_callbacks:
            del self._reload_callbacks[name]
            logger.debug(f"📞 Unregistered reload callback: {name}")

    def _notify_reload_callbacks(self) -> None:
        """Notify all registered callbacks that reload completed."""
        for name, callback in self._reload_callbacks.items():
            try:
                callback()
                logger.debug(f"📞 Notified reload callback: {name}")
            except Exception as e:
                logger.error(f"Error in reload callback {name}: {e}")

    # ============================================================================
    # CLEANUP METHODS
    # ============================================================================

    def shutdown(self) -> None:
        """Gracefully shutdown all containers and disconnect hardware."""
        try:
            logger.info("🔌 Shutting down ReloadableApplicationContainer...")

            # Disconnect all hardware connections
            if self._connection_container:
                self._connection_container.disconnect_all_hardware()

            # Clear containers
            self._service_container = None
            self._connection_container = None
            self._config_container = None

            # Clear callbacks
            self._reload_callbacks.clear()

            logger.info("✅ ReloadableApplicationContainer shutdown completed")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def __del__(self):
        """Ensure cleanup on deletion."""
        try:
            self.shutdown()
        except Exception:
            pass  # Ignore errors during cleanup
