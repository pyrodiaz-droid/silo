"""Settings management for Silo audiobook metadata editor."""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Settings:
    """Application settings manager."""

    def __init__(self, **kwargs):
        """Initialize settings with default values.

        Args:
            **kwargs: Setting key-value pairs
        """
        # Window settings
        self.window_geometry: str = kwargs.get('window_geometry', '1200x800+100+100')

        # Auto-save settings
        self.auto_save_enabled: bool = kwargs.get('auto_save_enabled', True)
        self.auto_save_interval: int = kwargs.get('auto_save_interval', 300)  # 5 minutes

        # Validation settings
        self.max_image_size: int = kwargs.get('max_image_size', 10_000_000)  # 10MB
        self.validate_urls: bool = kwargs.get('validate_urls', True)

        # UI settings
        self.show_tooltips: bool = kwargs.get('show_tooltips', True)
        self.remember_window_state: bool = kwargs.get('remember_window_state', True)

        # Genre list (can be customized)
        self.genre_list: list = kwargs.get('genre_list', [
            "Fiction", "Non-Fiction", "Mystery", "Sci-Fi",
            "Fantasy", "Romance", "Biography", "History",
            "Self-Help", "Other"
        ])

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary.

        Returns:
            Dictionary representation of settings
        """
        return {
            'window_geometry': self.window_geometry,
            'auto_save_enabled': self.auto_save_enabled,
            'auto_save_interval': self.auto_save_interval,
            'max_image_size': self.max_image_size,
            'validate_urls': self.validate_urls,
            'show_tooltips': self.show_tooltips,
            'remember_window_state': self.remember_window_state,
            'genre_list': self.genre_list
        }

    @classmethod
    def load(cls) -> 'Settings':
        """Load settings from config file.

        Returns:
            Settings instance with loaded values
        """
        config_path = cls._get_config_path()

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Loaded settings from {config_path}")
                return cls(**data)
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Error loading config: {e}, using defaults")
                return cls()
        else:
            logger.info("No config file found, using defaults")
            return cls()

    def save(self) -> None:
        """Save settings to config file."""
        config_path = self._get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Saved settings to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    @staticmethod
    def _get_config_path() -> Path:
        """Get config file path.

        Returns:
            Path to config file
        """
        config_dir = Path.home() / '.silo'
        return config_dir / 'config.json'


def load_settings() -> Settings:
    """Convenience function to load settings.

    Returns:
        Settings instance
    """
    return Settings.load()


def save_settings(settings: Settings) -> None:
    """Convenience function to save settings.

    Args:
        settings: Settings instance to save
    """
    settings.save()
