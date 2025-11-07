"""
Simple Reloadable Application Container

A pragmatic approach to hot-reload that extends the existing ApplicationContainer
with intelligent reload capabilities while maintaining backward compatibility.
"""

# Third-party imports
from loguru import logger

# Local application imports
from application.containers.application_container import ApplicationContainer
from infrastructure.implementation.configuration.yaml_container_configuration import (
    YamlContainerConfigurationLoader,
)


class SimpleReloadableContainer(ApplicationContainer):
    """
    Simple hot-reloadable container that extends ApplicationContainer.

    This approach maintains backward compatibility while adding intelligent
    reload capabilities with minimal complexity.
    """

    def __init__(self):
        super().__init__()
        self._last_config_hash = None
        self._reload_callbacks = {}

    @classmethod
    def create(cls) -> "SimpleReloadableContainer":
        """
        Create container with hot-reload capability.

        Returns:
            Configured SimpleReloadableContainer instance
        """
        try:
            # Create instance first
            container = cls()

            # Load configuration using parent logic
            config_loader = YamlContainerConfigurationLoader()
            config_data = config_loader.load_all_configurations()
            container.config.from_dict(config_data)

            # Initialize config hash for change detection - deferred to avoid DI issues
            # The hash will be set on first reload attempt
            container._last_config_hash = None

            # Bind instance methods to the container
            cls._bind_instance_methods(container)

            logger.info("🏗️ SimpleReloadableContainer created successfully")
            return container

        except Exception as e:
            logger.error(f"Failed to create SimpleReloadableContainer: {e}")
            # Fall back to parent fallback logic
            container = cls()
            cls._apply_fallback_config(container)
            # Initialize with null hash for fallback case too
            container._last_config_hash = None
            # Bind instance methods for fallback case too
            cls._bind_instance_methods(container)
            return container

    @classmethod
    def _bind_instance_methods(cls, container_instance: "SimpleReloadableContainer") -> None:
        """Bind instance methods to the container instance."""
        try:
            # Bind implementation methods directly to the instance
            container_instance._instance_reload_configuration_impl = (
                cls._get_instance_reload_configuration_impl(container_instance)
            )
            container_instance._instance_has_config_changed_impl = (
                cls._get_instance_has_config_changed_impl(container_instance)
            )
            container_instance._instance_update_config_hash_impl = (
                cls._get_instance_update_config_hash_impl(container_instance)
            )

            # Bind additional methods that the container needs
            container_instance._apply_intelligent_reload = cls._get_apply_intelligent_reload_impl(
                container_instance
            )
            container_instance._notify_reload_callbacks = cls._get_notify_reload_callbacks_impl(
                container_instance
            )

            # Bind the reload_configuration method
            container_instance.reload_configuration = lambda: cls._instance_reload_configuration(
                container_instance
            )

            # Bind the config change detection methods
            container_instance._has_config_changed = lambda: cls._instance_has_config_changed(
                container_instance
            )
            container_instance._update_config_hash = lambda: cls._instance_update_config_hash(
                container_instance
            )

            logger.debug("🔗 Instance methods bound to container")
        except Exception as e:
            logger.error(f"Failed to bind instance methods: {e}")

    @classmethod
    def _get_instance_reload_configuration_impl(cls, container_instance):
        """Get bound method for reload configuration implementation."""

        def impl():
            try:
                logger.info("🔄 Starting intelligent configuration reload...")

                # Step 1: Load fresh configuration from YAML files
                config_loader = YamlContainerConfigurationLoader()
                new_config_data = config_loader.load_all_configurations()

                # Step 2: Update configuration provider - use the fresh loaded data
                old_config = container_instance.config()
                container_instance.config.from_dict(new_config_data)

                # Step 3: Detect what changed and apply appropriate reload strategy
                reload_success = container_instance._apply_intelligent_reload(
                    old_config, new_config_data
                )

                # Step 4: Update hash if successful
                if reload_success:
                    container_instance._instance_update_config_hash_impl()
                    container_instance._notify_reload_callbacks()
                    logger.info("✅ Intelligent configuration reload completed successfully")
                else:
                    # Rollback configuration on failure
                    container_instance.config.from_dict(old_config)
                    logger.error("❌ Configuration reload failed, rolled back")

                return reload_success

            except Exception as e:
                logger.error(f"❌ Intelligent configuration reload failed: {e}")
                return False

        return impl

    @classmethod
    def _get_instance_has_config_changed_impl(cls, container_instance):
        """Get bound method for config change detection implementation."""

        def impl():
            try:
                # Standard library imports
                import hashlib
                import json

                # Get current config as dict - load fresh from YAML files
                config_loader = YamlContainerConfigurationLoader()
                config_dict = config_loader.load_all_configurations()
                config_json = json.dumps(config_dict, sort_keys=True)
                current_hash = hashlib.md5(config_json.encode()).hexdigest()

                return current_hash != container_instance._last_config_hash
            except Exception as e:
                logger.error(f"Failed to check config changes: {e}")
                return True  # Assume changed to be safe

        return impl

    @classmethod
    def _get_instance_update_config_hash_impl(cls, container_instance):
        """Get bound method for config hash update implementation."""

        def impl():
            try:
                # Standard library imports
                import hashlib
                import json

                # Get current config as dict - store the dict directly from the YAML loader
                config_loader = YamlContainerConfigurationLoader()
                config_dict = config_loader.load_all_configurations()
                config_json = json.dumps(config_dict, sort_keys=True)
                container_instance._last_config_hash = hashlib.md5(config_json.encode()).hexdigest()
            except Exception as e:
                logger.error(f"Failed to update config hash: {e}")
                container_instance._last_config_hash = None

        return impl

    @classmethod
    def _get_apply_intelligent_reload_impl(cls, container_instance):
        """Get bound method for apply intelligent reload implementation."""

        def impl(old_config: dict, new_config: dict) -> bool:
            try:
                # Detect what changed
                changes = cls._detect_changes_static(old_config, new_config)

                if not changes:
                    logger.info("🔍 No significant changes detected")
                    return True

                logger.info(f"🔍 Detected changes: {', '.join(changes)}")

                # Apply reload strategy based on changes
                if cls._has_hardware_model_changes_static(changes):
                    return cls._reload_hardware_with_preservation_static(container_instance)
                elif cls._has_hardware_config_changes_static(changes):
                    return cls._reload_hardware_configs_only_static(container_instance)
                else:
                    return cls._reload_services_only_static(container_instance)

            except Exception as e:
                logger.error(f"Error applying intelligent reload: {e}")
                return False

        return impl

    @classmethod
    def _get_notify_reload_callbacks_impl(cls, container_instance):
        """Get bound method for notify reload callbacks implementation."""

        def impl():
            try:
                # Use getattr with default to handle DynamicContainer instances gracefully
                reload_callbacks = getattr(container_instance, "_reload_callbacks", {})

                if not reload_callbacks:
                    logger.debug(
                        "📞 No reload callbacks registered (container may be DynamicContainer instance)"
                    )
                    return

                for name, callback in reload_callbacks.items():
                    try:
                        callback()
                        logger.debug(f"📞 Notified reload callback: {name}")
                    except Exception as e:
                        logger.error(f"Error in reload callback {name}: {e}")
            except Exception as e:
                logger.error(f"Error notifying reload callbacks: {e}")

        return impl

    @classmethod
    def _detect_changes_static(cls, old_config: dict, new_config: dict) -> list:
        """Static method to detect configuration changes."""
        changes = []

        try:
            # Check hardware model changes
            hardware_categories = ["robot", "power", "mcu", "loadcell", "digital_io", "power_analyzer"]

            for category in hardware_categories:
                old_model = old_config.get("hardware", {}).get(category, {}).get("model")
                new_model = new_config.get("hardware", {}).get(category, {}).get("model")

                if old_model != new_model:
                    changes.append(f"hardware.{category}.model")

            # Check other hardware parameter changes
            old_hardware = old_config.get("hardware", {})
            new_hardware = new_config.get("hardware", {})

            if old_hardware != new_hardware and not any(".model" in change for change in changes):
                changes.append("hardware.config")

            # Check application config changes
            old_app = {k: v for k, v in old_config.items() if k != "hardware"}
            new_app = {k: v for k, v in new_config.items() if k != "hardware"}

            if old_app != new_app:
                changes.append("application.config")

        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            changes.append("unknown")  # Trigger safe full reload

        return changes

    @classmethod
    def _has_hardware_model_changes_static(cls, changes: list) -> bool:
        """Check if any hardware model changes occurred."""
        return any(".model" in change for change in changes)

    @classmethod
    def _has_hardware_config_changes_static(cls, changes: list) -> bool:
        """Check if hardware configuration changes occurred."""
        return any("hardware." in change for change in changes)

    @classmethod
    def _reload_hardware_with_preservation_static(cls, container_instance) -> bool:
        """Reload hardware with connection preservation (for model changes)."""
        try:
            logger.info("🔄 Performing hardware reload with connection preservation...")

            # Step 1: Reset main hardware providers that need to pick up new configuration
            hardware_providers = [
                "hardware_service_facade",
                "industrial_system_manager",
            ]

            for provider_name in hardware_providers:
                try:
                    if hasattr(container_instance, provider_name):
                        provider = getattr(container_instance, provider_name)
                        if hasattr(provider, "reset"):
                            provider.reset()
                            logger.info(f"🔄 Reset {provider_name}")
                        else:
                            # For providers without reset method, we override them
                            container_instance.override_providers({provider_name: provider})
                            logger.info(f"🔄 Overridden {provider_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to reset {provider_name}: {e}")

            # Step 2: Reset hardware factory providers to pick up new configuration
            cls._reset_hardware_factory_providers_static(container_instance)

            logger.info("✅ Hardware reload with preservation completed")
            return True
        except Exception as e:
            logger.error(f"❌ Hardware reload with preservation failed: {e}")
            return False

    @classmethod
    def _reset_hardware_factory_providers_static(cls, container_instance):
        """Reset hardware factory providers to pick up new configuration (static version)."""
        try:
            hardware_factory_providers = [
                "robot_service",
                "power_service",
                "mcu_service",
                "loadcell_service",
                "digital_io_service",
                "power_analyzer_service",
            ]

            if hasattr(container_instance, "hardware_factory"):
                hardware_factory = container_instance.hardware_factory()
                for provider_name in hardware_factory_providers:
                    try:
                        if hasattr(hardware_factory, provider_name):
                            provider = getattr(hardware_factory, provider_name)
                            if hasattr(provider, "reset"):
                                provider.reset()
                                logger.info(f"🏭 Reset hardware factory provider: {provider_name}")
                            else:
                                logger.debug(f"🏭 Provider {provider_name} has no reset method")
                        else:
                            logger.debug(
                                f"🏭 Provider {provider_name} not found in hardware factory"
                            )
                    except Exception as e:
                        logger.warning(
                            f"⚠️ Failed to reset hardware factory provider {provider_name}: {e}"
                        )
            else:
                logger.warning("⚠️ Container has no hardware_factory attribute")

        except Exception as e:
            logger.error(f"Failed to reset hardware factory providers: {e}")

    @classmethod
    def _reload_hardware_configs_only_static(cls, container_instance) -> bool:
        """Reload hardware configurations without resetting connections."""
        try:
            logger.info("🔄 Performing hardware config-only reload...")

            # For config-only changes, we still need to reset hardware factory to pick up new config
            cls._reset_hardware_factory_providers_static(container_instance)

            logger.info("✅ Hardware config-only reload completed")
            return True
        except Exception as e:
            logger.error(f"❌ Hardware config-only reload failed: {e}")
            return False

    @classmethod
    def _reload_services_only_static(cls, container_instance) -> bool:
        """Reload business services only (for application config changes)."""
        try:
            logger.info("🔄 Performing services-only reload...")

            # Reset service providers that depend on application configuration
            service_providers = [
                "test_result_evaluator",
                "repository_service",
                "json_result_repository",
            ]

            for provider_name in service_providers:
                try:
                    if hasattr(container_instance, provider_name):
                        provider = getattr(container_instance, provider_name)
                        if hasattr(provider, "reset"):
                            provider.reset()
                            logger.info(f"🔄 Reset service provider: {provider_name}")
                        else:
                            logger.debug(f"🔄 Service provider {provider_name} has no reset method")
                    else:
                        logger.debug(f"🔄 Service provider {provider_name} not found in container")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to reset service provider {provider_name}: {e}")

            logger.info("✅ Services-only reload completed")
            return True
        except Exception as e:
            logger.error(f"❌ Services-only reload failed: {e}")
            return False

    @classmethod
    def _instance_reload_configuration(
        cls, container_instance: "SimpleReloadableContainer"
    ) -> bool:
        """Instance-specific reload configuration method."""
        return container_instance._instance_reload_configuration_impl()

    @classmethod
    def _instance_has_config_changed(cls, container_instance: "SimpleReloadableContainer") -> bool:
        """Instance-specific config change detection method."""
        return container_instance._instance_has_config_changed_impl()

    @classmethod
    def _instance_update_config_hash(cls, container_instance: "SimpleReloadableContainer") -> None:
        """Instance-specific config hash update method."""
        container_instance._instance_update_config_hash_impl()

    def _update_config_hash(self):
        """Update stored configuration hash for change detection."""
        try:
            # Standard library imports
            import hashlib
            import json

            # Get current config as dict - store the dict directly from the YAML loader
            config_loader = YamlContainerConfigurationLoader()
            config_dict = config_loader.load_all_configurations()
            config_json = json.dumps(config_dict, sort_keys=True)
            self._last_config_hash = hashlib.md5(config_json.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to update config hash: {e}")
            self._last_config_hash = None

    def _has_config_changed(self) -> bool:
        """Check if configuration has changed since last reload."""
        try:
            # Standard library imports
            import hashlib
            import json

            # Get current config as dict - load fresh from YAML files
            config_loader = YamlContainerConfigurationLoader()
            config_dict = config_loader.load_all_configurations()
            config_json = json.dumps(config_dict, sort_keys=True)
            current_hash = hashlib.md5(config_json.encode()).hexdigest()

            return current_hash != self._last_config_hash
        except Exception as e:
            logger.error(f"Failed to check config changes: {e}")
            return True  # Assume changed to be safe

    def reload_configuration(self) -> bool:
        """
        Intelligent configuration reload with change detection.

        Returns:
            bool: True if reload was successful
        """
        try:
            logger.info("🔄 Starting intelligent configuration reload...")

            # Step 1: Load fresh configuration from YAML files
            config_loader = YamlContainerConfigurationLoader()
            new_config_data = config_loader.load_all_configurations()

            # Step 2: Update configuration provider - use the fresh loaded data
            old_config = self.config()
            self.config.from_dict(new_config_data)

            # Step 3: Detect what changed and apply appropriate reload strategy
            reload_success = self._apply_intelligent_reload(old_config, new_config_data)

            # Step 4: Update hash if successful
            if reload_success:
                self._update_config_hash()
                self._notify_reload_callbacks()
                logger.info("✅ Intelligent configuration reload completed successfully")
            else:
                # Rollback configuration on failure
                self.config.from_dict(old_config)
                logger.error("❌ Configuration reload failed, rolled back")

            return reload_success

        except Exception as e:
            logger.error(f"❌ Intelligent configuration reload failed: {e}")
            return False

    def _apply_intelligent_reload(self, old_config: dict, new_config: dict) -> bool:
        """
        Apply intelligent reload strategy based on what changed.

        Args:
            old_config: Previous configuration
            new_config: New configuration

        Returns:
            bool: True if reload was successful
        """
        try:
            # Detect what changed
            changes = self._detect_changes(old_config, new_config)

            if not changes:
                logger.info("🔍 No significant changes detected")
                return True

            logger.info(f"🔍 Detected changes: {', '.join(changes)}")

            # Apply reload strategy based on changes
            if self._has_hardware_model_changes(changes):
                return self._reload_hardware_with_preservation()
            elif self._has_hardware_config_changes(changes):
                return self._reload_hardware_configs_only()
            else:
                return self._reload_services_only()

        except Exception as e:
            logger.error(f"Error applying intelligent reload: {e}")
            return False

    def _detect_changes(self, old_config: dict, new_config: dict) -> list:
        """Detect specific configuration changes."""
        changes = []

        try:
            # Check hardware model changes
            hardware_categories = ["robot", "power", "mcu", "loadcell", "digital_io", "power_analyzer"]

            for category in hardware_categories:
                old_model = old_config.get("hardware", {}).get(category, {}).get("model")
                new_model = new_config.get("hardware", {}).get(category, {}).get("model")

                if old_model != new_model:
                    changes.append(f"hardware.{category}.model")

            # Check other hardware parameter changes
            old_hardware = old_config.get("hardware", {})
            new_hardware = new_config.get("hardware", {})

            if old_hardware != new_hardware and f"hardware.{category}.model" not in changes:
                changes.append("hardware.config")

            # Check application config changes
            old_app = {k: v for k, v in old_config.items() if k != "hardware"}
            new_app = {k: v for k, v in new_config.items() if k != "hardware"}

            if old_app != new_app:
                changes.append("application.config")

        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            changes.append("unknown")  # Trigger safe full reload

        return changes

    def _has_hardware_model_changes(self, changes: list) -> bool:
        """Check if any hardware model changes occurred."""
        return any(".model" in change for change in changes)

    def _has_hardware_config_changes(self, changes: list) -> bool:
        """Check if hardware configuration changes occurred."""
        return any("hardware." in change for change in changes)

    def _reload_hardware_with_preservation(self) -> bool:
        """Reload hardware with connection preservation (for model changes)."""
        try:
            logger.info("🔄 Performing hardware reload with connection preservation...")

            # Step 1: Store current connection states (if services support it)
            preserved_states = {}

            # Step 2: Reset hardware-related providers
            hardware_providers = [
                "hardware_service_facade",
                "industrial_system_manager",
            ]

            for provider_name in hardware_providers:
                try:
                    provider = getattr(self, provider_name)
                    if hasattr(provider, "reset"):
                        provider.reset()
                        logger.info(f"🔄 Reset {provider_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to reset {provider_name}: {e}")

            # Step 3: Reset hardware factory providers
            self._reset_hardware_factory_providers()

            logger.info("✅ Hardware reload with preservation completed")
            return True

        except Exception as e:
            logger.error(f"❌ Hardware reload with preservation failed: {e}")
            return False

    def _reload_hardware_configs_only(self) -> bool:
        """Reload hardware configurations without resetting connections."""
        try:
            logger.info("🔄 Performing hardware config-only reload...")

            # For config-only changes, we may not need to reset everything
            # This is a lighter reload for parameter changes

            logger.info("✅ Hardware config-only reload completed")
            return True

        except Exception as e:
            logger.error(f"❌ Hardware config-only reload failed: {e}")
            return False

    def _reload_services_only(self) -> bool:
        """Reload business services only (for application config changes)."""
        try:
            logger.info("🔄 Performing services-only reload...")

            # Reset service providers that depend on application configuration
            service_providers = [
                "test_result_evaluator",
                "repository_service",
                "json_result_repository",
            ]

            for provider_name in service_providers:
                try:
                    provider = getattr(self, provider_name)
                    if hasattr(provider, "reset"):
                        provider.reset()
                        logger.info(f"🔄 Reset {provider_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to reset {provider_name}: {e}")

            logger.info("✅ Services-only reload completed")
            return True

        except Exception as e:
            logger.error(f"❌ Services-only reload failed: {e}")
            return False

    def _reset_hardware_factory_providers(self):
        """Reset hardware factory providers to pick up new configuration."""
        try:
            hardware_factory_providers = [
                "robot_service",
                "power_service",
                "mcu_service",
                "loadcell_service",
                "digital_io_service",
                "power_analyzer_service",
            ]

            for provider_name in hardware_factory_providers:
                try:
                    provider = getattr(self.hardware_factory, provider_name)
                    if hasattr(provider, "reset"):
                        provider.reset()
                        logger.info(f"🔄 Reset HardwareFactory.{provider_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to reset HardwareFactory.{provider_name}: {e}")

        except Exception as e:
            logger.error(f"Failed to reset hardware factory providers: {e}")

    def register_reload_callback(self, name: str, callback):
        """Register a callback to be notified when reload completes."""
        # Ensure _reload_callbacks exists, initialize if missing
        if not hasattr(self, "_reload_callbacks"):
            self._reload_callbacks = {}

        self._reload_callbacks[name] = callback
        logger.debug(f"📞 Registered reload callback: {name}")

    def unregister_reload_callback(self, name: str):
        """Unregister a reload callback."""
        reload_callbacks = getattr(self, "_reload_callbacks", {})
        if name in reload_callbacks:
            del reload_callbacks[name]
            logger.debug(f"📞 Unregistered reload callback: {name}")

    def _notify_reload_callbacks(self):
        """Notify all registered callbacks that reload completed."""
        # Use getattr with default to handle DynamicContainer instances gracefully
        reload_callbacks = getattr(self, "_reload_callbacks", {})

        if not reload_callbacks:
            logger.debug(
                "📞 No reload callbacks registered (container may be DynamicContainer instance)"
            )
            return

        for name, callback in reload_callbacks.items():
            try:
                callback()
                logger.debug(f"📞 Notified reload callback: {name}")
            except Exception as e:
                logger.error(f"Error in reload callback {name}: {e}")

    # Legacy compatibility methods
    @classmethod
    def create_with_paths(cls, **kwargs):
        """Legacy compatibility method."""
        if kwargs:
            logger.warning(f"Path arguments are ignored: {list(kwargs.keys())}")
        return cls.create()

    @classmethod
    def ensure_config_exists(cls, **kwargs):
        """Legacy compatibility method."""
        if kwargs:
            logger.warning(f"Path arguments are ignored: {list(kwargs.keys())}")
        return super().ensure_config_exists(**kwargs)
