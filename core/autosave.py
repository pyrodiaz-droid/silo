"""Auto-save manager for Silo audiobook metadata editor."""

import logging
import threading
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class AutoSaveManager:
    """Manage auto-save functionality."""

    def __init__(self, interval: int = 300, callback: Optional[Callable] = None):
        """Initialize auto-save manager.

        Args:
            interval: Save interval in seconds (default 300 = 5 minutes)
            callback: Function to call for auto-save
        """
        self.interval = interval
        self.callback = callback
        self.timer: Optional[threading.Timer] = None
        self.enabled = True

    def start(self) -> None:
        """Start auto-save timer."""
        if self.enabled and self.callback:
            self._schedule_next_save()

    def _schedule_next_save(self) -> None:
        """Schedule next auto-save."""
        if self.timer:
            self.timer.cancel()

        self.timer = threading.Timer(self.interval, self._trigger)
        self.timer.daemon = True
        self.timer.start()

    def _trigger(self) -> None:
        """Trigger auto-save callback."""
        if self.enabled and self.callback:
            try:
                self.callback()
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")

        # Schedule next save
        if self.enabled:
            self._schedule_next_save()

    def stop(self) -> None:
        """Stop auto-save timer."""
        self.enabled = False
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def set_interval(self, interval: int) -> None:
        """Change auto-save interval.

        Args:
            interval: New interval in seconds
        """
        self.interval = interval
        if self.enabled:
            self._schedule_next_save()
