"""Plugin system for extending Silo functionality."""

import sys
import os
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SiloPlugin(ABC):
    """Base class for Silo plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass

    @abstractmethod
    def initialize(self, app) -> bool:
        """Initialize the plugin.

        Args:
            app: Application instance

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup when plugin is unloaded."""
        pass


class PluginManager:
    """Manage plugin lifecycle and registration."""

    def __init__(self, plugin_dir: Optional[Path] = None):
        """Initialize plugin manager.

        Args:
            plugin_dir: Directory containing plugins (defaults to ~/.silo/plugins/)
        """
        if plugin_dir is None:
            plugin_dir = Path.home() / '.silo' / 'plugins'

        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        self.loaded_plugins: Dict[str, SiloPlugin] = {}
        self.plugin_hooks: Dict[str, List[callable]] = {}

    def discover_plugins(self) -> List[str]:
        """Discover available plugins.

        Returns:
            List of plugin names
        """
        plugins = []

        if not self.plugin_dir.exists():
            return plugins

        for plugin_file in self.plugin_dir.glob("*_plugin.py"):
            plugin_name = plugin_file.stem
            plugins.append(plugin_name)

        return plugins

    def load_plugin(self, plugin_name: str, app) -> bool:
        """Load a plugin.

        Args:
            plugin_name: Name of plugin (without _plugin suffix)
            app: Application instance

        Returns:
            True if successful
        """
        if plugin_name in self.loaded_plugins:
            logger.warning(f"Plugin {plugin_name} already loaded")
            return True

        try:
            # Find plugin file
            plugin_file = self.plugin_dir / f"{plugin_name}_plugin.py"
            if not plugin_file.exists():
                logger.error(f"Plugin file not found: {plugin_file}")
                return False

            # Load module dynamically
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            if spec is None or spec.loader is None:
                logger.error(f"Failed to load plugin spec: {plugin_name}")
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, SiloPlugin) and attr != SiloPlugin:
                    plugin_class = attr
                    break

            if plugin_class is None:
                logger.error(f"No SiloPlugin class found in {plugin_name}")
                return False

            # Instantiate and initialize plugin
            plugin = plugin_class()
            if not plugin.initialize(app):
                logger.error(f"Plugin {plugin_name} failed to initialize")
                return False

            self.loaded_plugins[plugin_name] = plugin
            logger.info(f"Loaded plugin: {plugin_name} v{plugin.version}")
            return True

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            True if successful
        """
        if plugin_name not in self.loaded_plugins:
            logger.warning(f"Plugin {plugin_name} not loaded")
            return False

        try:
            plugin = self.loaded_plugins[plugin_name]
            plugin.shutdown()
            del self.loaded_plugins[plugin_name]
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False

    def register_hook(self, hook_name: str, callback: callable) -> None:
        """Register a callback for a specific hook.

        Args:
            hook_name: Name of the hook
            callback: Function to call when hook is triggered
        """
        if hook_name not in self.plugin_hooks:
            self.plugin_hooks[hook_name] = []

        self.plugin_hooks[hook_name].append(callback)
        logger.debug(f"Registered hook: {hook_name}")

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger all callbacks for a hook.

        Args:
            hook_name: Name of the hook
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks

        Returns:
            List of results from callbacks
        """
        results = []

        if hook_name in self.plugin_hooks:
            for callback in self.plugin_hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Hook callback failed: {e}")

        return results

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, str]]:
        """Get information about a loaded plugin.

        Args:
            plugin_name: Name of plugin

        Returns:
            Plugin information dict or None
        """
        if plugin_name not in self.loaded_plugins:
            return None

        plugin = self.loaded_plugins[plugin_name]
        return {
            'name': plugin.name,
            'version': plugin.version,
            'description': plugin.description
        }

    def list_loaded_plugins(self) -> List[Dict[str, str]]:
        """List all loaded plugins.

        Returns:
            List of plugin information dicts
        """
        plugins = []
        for plugin_name in self.loaded_plugins:
            info = self.get_plugin_info(plugin_name)
            if info:
                plugins.append(info)

        return plugins


class PluginAPI:
    """API provided to plugins for interacting with Silo."""

    def __init__(self, app):
        """Initialize Plugin API.

        Args:
            app: Application instance
        """
        self.app = app

    def get_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a file.

        Args:
            file_path: Path to audio file

        Returns:
            Metadata dict or None
        """
        try:
            from core.metadata_handler import read_metadata
            return read_metadata(file_path)
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return None

    def set_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """Set metadata for a file.

        Args:
            file_path: Path to audio file
            metadata: Metadata dictionary

        Returns:
            True if successful
        """
        try:
            from core.metadata_handler import apply_metadata
            apply_metadata(file_path, metadata, None)
            return True
        except Exception as e:
            logger.error(f"Failed to set metadata: {e}")
            return False

    def get_files(self) -> List[str]:
        """Get list of loaded files.

        Returns:
            List of file paths
        """
        return getattr(self.app, 'files', [])

    def register_menu_item(self, menu_name: str, item_text: str, callback: callable) -> bool:
        """Register a custom menu item.

        Args:
            menu_name: Name of menu (e.g., 'Tools', 'Plugins')
            item_text: Text for menu item
            callback: Function to call when item is clicked

        Returns:
            True if successful
        """
        # This would be implemented in the UI layer
        logger.info(f"Plugin registered menu item: {menu_name} -> {item_text}")
        return True


# Example plugin template
class ExamplePlugin(SiloPlugin):
    """Example plugin showing how to create plugins."""

    @property
    def name(self) -> str:
        return "Example Plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "An example plugin template"

    def initialize(self, app) -> bool:
        """Initialize the plugin."""
        self.api = PluginAPI(app)

        # Register custom functionality
        logger.info(f"{self.name} initialized")

        return True

    def shutdown(self) -> None:
        """Cleanup."""
        logger.info(f"{self.name} shut down")
