"""Theme management for Silo audiobook metadata editor."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ColorScheme:
    """Color scheme for the application."""
    bg: str           # Main background
    fg: str           # Main foreground/text
    bg_secondary: str # Secondary background (frames, panels)
    bg_tertiary: str  # Tertiary background (entries, listboxes)
    accent: str       # Accent color (buttons, highlights)
    accent_hover: str # Hover state
    success: str      # Success color
    border: str       # Border color
    select_bg: str    # Selection background
    select_fg: str    # Selection foreground
    button_secondary: str  # Secondary button color

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of color scheme
        """
        return {
            'bg': self.bg,
            'fg': self.fg,
            'bg_secondary': self.bg_secondary,
            'bg_tertiary': self.bg_tertiary,
            'accent': self.accent,
            'accent_hover': self.accent_hover,
            'success': self.success,
            'border': self.border,
            'select_bg': self.select_bg,
            'select_fg': self.select_fg,
            'button_secondary': self.button_secondary
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ColorScheme':
        """Create ColorScheme from dictionary.

        Args:
            data: Dictionary containing color values

        Returns:
            ColorScheme instance
        """
        return cls(**data)


class ThemeManager:
    """Manage application themes and color schemes."""

    # Built-in themes
    BUILT_IN_THEMES = {
        'dark': ColorScheme(
            bg='#2b2b2b',
            fg='#e0e0e0',
            bg_secondary='#3c3c3c',
            bg_tertiary='#4a4a4a',
            accent='#2196F3',
            accent_hover='#42A5F5',
            success='#1976D2',
            border='#555555',
            select_bg='#1976D2',
            select_fg='#ffffff',
            button_secondary='#0D47A1'
        ),
        'darker': ColorScheme(
            bg='#1a1a1a',
            fg='#e0e0e0',
            bg_secondary='#2a2a2a',
            bg_tertiary='#3a3a3a',
            accent='#2196F3',
            accent_hover='#42A5F5',
            success='#1976D2',
            border='#404040',
            select_bg='#1976D2',
            select_fg='#ffffff',
            button_secondary='#0D47A1'
        ),
        'ocean': ColorScheme(
            bg='#0d1b2a',
            fg='#e0f7fa',
            bg_secondary='#1b263b',
            bg_tertiary='#263545',
            accent='#00bcd4',
            accent_hover='#26c6da',
            success='#0097a7',
            border='#37474f',
            select_bg='#0097a7',
            select_fg='#ffffff',
            button_secondary='#006064'
        ),
        'forest': ColorScheme(
            bg='#1b5e20',
            fg='#e8f5e9',
            bg_secondary='#2e7d32',
            bg_tertiary='#43a047',
            accent='#66bb6a',
            accent_hover='#81c784',
            success='#4caf50',
            border='#1b5e20',
            select_bg='#4caf50',
            select_fg='#ffffff',
            button_secondary='#2e7d32'
        ),
        'light': ColorScheme(
            bg='#ffffff',
            fg='#212121',
            bg_secondary='#f5f5f5',
            bg_tertiary='#e0e0e0',
            accent='#1976D2',
            accent_hover='#2196F3',
            success='#388E3C',
            border='#bdbdbd',
            select_bg='#1976D2',
            select_fg='#ffffff',
            button_secondary='#424242'
        )
    }

    def __init__(self, theme_dir: Optional[Path] = None):
        """Initialize theme manager.

        Args:
            theme_dir: Directory for custom themes (defaults to ~/.silo/themes/)
        """
        if theme_dir is None:
            theme_dir = Path.home() / '.silo' / 'themes'

        self.theme_dir = Path(theme_dir)
        self.theme_dir.mkdir(parents=True, exist_ok=True)

    def get_theme(self, name: str) -> Optional[ColorScheme]:
        """Get theme by name.

        Args:
            name: Theme name

        Returns:
            ColorScheme if found, None otherwise
        """
        # Check built-in themes first
        if name in self.BUILT_IN_THEMES:
            return self.BUILT_IN_THEMES[name]

        # Check custom themes
        theme_file = self.theme_dir / f"{name}.json"
        if theme_file.exists():
            try:
                with open(theme_file, 'r') as f:
                    data = json.load(f)
                return ColorScheme.from_dict(data)
            except Exception as e:
                logger.error(f"Failed to load theme {name}: {e}")

        return None

    def list_themes(self) -> list:
        """List all available themes.

        Returns:
            List of theme names
        """
        themes = list(self.BUILT_IN_THEMES.keys())

        # Add custom themes
        for theme_file in self.theme_dir.glob("*.json"):
            theme_name = theme_file.stem
            if theme_name not in themes:
                themes.append(theme_name)

        return sorted(themes)

    def save_custom_theme(self, name: str, theme: ColorScheme) -> bool:
        """Save a custom theme.

        Args:
            name: Theme name
            theme: ColorScheme to save

        Returns:
            True if successful
        """
        try:
            theme_file = self.theme_dir / f"{name}.json"
            with open(theme_file, 'w') as f:
                json.dump(theme.to_dict(), f, indent=2)

            logger.info(f"Saved custom theme: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to save theme {name}: {e}")
            return False

    def create_theme_from_current(self, name: str, current_colors: Dict[str, str]) -> bool:
        """Create a custom theme from current application colors.

        Args:
            name: Theme name
            current_colors: Current color dictionary

        Returns:
            True if successful
        """
        try:
            theme = ColorScheme.from_dict(current_colors)
            return self.save_custom_theme(name, theme)

        except Exception as e:
            logger.error(f"Failed to create theme from colors: {e}")
            return False
