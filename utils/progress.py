"""Progress dialog utilities for Silo audiobook metadata editor."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ProgressDialog:
    """Progress dialog for long operations."""

    def __init__(self, parent: tk.Tk, title: str, total: int) -> None:
        """Initialize progress dialog.

        Args:
            parent: Parent window
            title: Dialog title
            total: Total items to process
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x100")
        self.dialog.resizable(False, False)

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Progress bar
        self.progress = ttk.Progressbar(
            self.dialog,
            maximum=total,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, padx=20, pady=10)

        # Status label
        self.label = tk.Label(self.dialog, text="Initializing...")
        self.label.pack(pady=5)

        # Update display
        self.dialog.update_idletasks()

    def update(self, current: int, message: str) -> None:
        """Update progress.

        Args:
            current: Current item number
            message: Status message
        """
        self.progress['value'] = current
        self.label.config(text=message)
        self.dialog.update_idletasks()

    def close(self) -> None:
        """Close dialog."""
        self.dialog.destroy()
