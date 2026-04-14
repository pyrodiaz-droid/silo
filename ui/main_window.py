"""Main window for Silo audiobook metadata editor.

This module contains the main application window class that orchestrates
all UI components and manages user interactions.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import logging
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import config
from core.metadata_handler import read_metadata, apply_metadata, MetadataError, FileAccessError
from core.chapter_handler import Chapter, embed_chapters, auto_generate_chapters
from core.cover_handler import load_cover_from_file, load_cover_from_url
from core.undo_manager import UndoManager, MetadataChangeCommand
from ui.widgets import Tooltip
from utils.validators import validate_year, validate_url
from utils.progress import ProgressDialog
from config.constants import COLORS, GENRES, SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class AudiobookMetadataEditor:
    """Main application window for the audiobook metadata editor."""

    def __init__(self, root: tk.Tk, settings: Optional[Any] = None) -> None:
        """Initialize the application.

        Args:
            root: Root Tk window
            settings: Optional settings object
        """
        self.root = root
        self.root.title("Silo")
        self.root.state('zoomed')  # Start maximized

        # Load window state if available
        self.load_window_state()

        # Use colors from config
        self.colors = COLORS

        # Apply dark theme to root window
        self.root.configure(bg=self.colors['bg'])

        # Configure ttk style for dark theme
        self._setup_ttk_style()

        # Data structures
        self.files: List[str] = []
        self.metadata_cache: Dict[str, Dict[str, Any]] = {}
        self.current_file_index: Optional[int] = None
        self.metadata_entries: Dict[str, Any] = {}
        self.batch_vars: Dict[str, Dict[str, Any]] = {}
        self.current_cover_art: Optional[bytes] = None
        self.current_cover_label: Optional[tk.Label] = None
        self.chapter_marks: List[Tuple[float, str]] = []

        # Genre options from config
        self.genres = GENRES

        # Status bar variable
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        # Undo/Redo manager
        self.undo_manager = UndoManager()

        # Auto-save manager (will be initialized if settings provided)
        self.auto_save_manager = None
        if settings and hasattr(settings, 'auto_save_enabled') and settings.auto_save_enabled:
            from core.autosave import AutoSaveManager
            interval = getattr(settings, 'auto_save_interval', 300)
            self.auto_save_manager = AutoSaveManager(
                interval=interval,
                callback=self.auto_save_callback
            )
            self.auto_save_manager.start()

        self.create_widgets()
        self.setup_keyboard_shortcuts()

        # Save window state on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_ttk_style(self) -> None:
        """Setup ttk style for dark theme."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure notebook (tabs)
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', background=self.colors['bg_secondary'],
                       foreground=self.colors['fg'], padding=[10, 5], borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', self.colors['accent'])],
                  foreground=[('selected', self.colors['select_fg'])])

        # Configure combobox
        style.configure('TCombobox', fieldbackground=self.colors['bg_tertiary'],
                       background=self.colors['bg_secondary'], foreground=self.colors['fg'],
                       borderwidth=1, bordercolor=self.colors['border'])
        style.map('TCombobox', fieldbackground=[('readonly', self.colors['bg_tertiary'])])

        # Configure panedwindow
        style.configure('TPanedwindow', background=self.colors['bg'])

    # Continue with the rest of the implementation...
    # (This would include all the methods from the original silo.py)

    def load_window_state(self) -> None:
        """Load window state from config file."""
        config_path = Path.home() / '.silo' / 'window_state.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    state = json.load(f)
                if 'geometry' in state:
                    self.root.geometry(state['geometry'])
            except Exception as e:
                logger.warning(f"Failed to load window state: {e}")

    def save_window_state(self) -> None:
        """Save window state to config file."""
        config_path = Path.home() / '.silo' / 'window_state.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)

        state = {'geometry': self.root.geometry()}

        try:
            with open(config_path, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            logger.warning(f"Failed to save window state: {e}")

    def update_status(self, message: str) -> None:
        """Update status bar message."""
        self.status_var.set(message)
        logger.info(f"Status: {message}")

    def on_closing(self) -> None:
        """Handle window closing event."""
        if self.auto_save_manager:
            self.auto_save_manager.stop()
        self.save_window_state()
        self.root.destroy()

    def auto_save_callback(self) -> None:
        """Auto-save callback."""
        saved_count = 0
        for file_path, cached_data in self.metadata_cache.items():
            if cached_data.get('modified', False):
                try:
                    metadata = cached_data.get('metadata', {})
                    cover_art = cached_data.get('cover_art')
                    audio_object = cached_data.get('_audio_object')

                    apply_metadata(file_path, metadata, cover_art, audio_object)
                    cached_data['modified'] = False
                    saved_count += 1
                    logger.info(f"Auto-saved: {file_path}")
                except Exception as e:
                    logger.error(f"Auto-save failed for {file_path}: {e}")

        if saved_count > 0:
            self.refresh_file_list()
            self.update_status(f"Auto-saved {saved_count} file(s)")

    # Placeholder for remaining methods
    # (These would be copied from the original silo.py)
    def create_widgets(self):
        """Build the UI layout"""
        pass  # To be implemented

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        pass  # To be implemented

    def refresh_file_list(self):
        """Refresh the file list display"""
        pass  # To be implemented

    def load_files(self):
        """Load audiobook files"""
        pass  # To be implemented

    def save_single_file(self):
        """Save metadata for currently selected file"""
        pass  # To be implemented

    # ... (more methods would go here)
