"""Undo/Redo system for Silo audiobook metadata editor."""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class Command(ABC):
    """Command interface for undoable operations."""

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass

    @abstractmethod
    def description(self) -> str:
        """Get command description."""
        pass


@dataclass
class MetadataChangeCommand:
    """Command for metadata changes."""

    editor: Any  # 'AudiobookMetadataEditor' - forward reference
    file_path: str
    old_metadata: Dict[str, Any]
    new_metadata: Dict[str, Any]
    old_cover: Optional[bytes]
    new_cover: Optional[bytes]

    def execute(self) -> None:
        """Execute the metadata change."""
        self.editor.apply_changes_to_file(
            self.file_path,
            self.new_metadata,
            self.new_cover
        )

    def undo(self) -> None:
        """Undo the metadata change."""
        self.editor.apply_changes_to_file(
            self.file_path,
            self.old_metadata,
            self.old_cover
        )

    def description(self) -> str:
        """Get command description."""
        return f"Change metadata for {os.path.basename(self.file_path)}"


class UndoManager:
    """Manages undo/redo history."""

    def __init__(self, max_history: int = 50):
        """Initialize undo manager.

        Args:
            max_history: Maximum number of commands to store
        """
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.max_history = max_history

    def execute(self, command: Command) -> None:
        """Execute command and add to history.

        Args:
            command: Command to execute
        """
        command.execute()
        self.undo_stack.append(command)

        # Limit history size
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        # Clear redo stack when new command executed
        self.redo_stack.clear()

    def undo(self) -> bool:
        """Undo last command.

        Returns:
            True if successful, False if nothing to undo
        """
        if not self.undo_stack:
            return False

        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True

    def redo(self) -> bool:
        """Redo last undone command.

        Returns:
            True if successful, False if nothing to redo
        """
        if not self.redo_stack:
            return False

        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        return True

    def can_undo(self) -> bool:
        """Check if undo is available.

        Returns:
            True if undo available
        """
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available.

        Returns:
            True if redo available
        """
        return len(self.redo_stack) > 0

    def get_undo_description(self) -> str:
        """Get description of undo action.

        Returns:
            Description string
        """
        return self.undo_stack[-1].description() if self.undo_stack else ""

    def get_redo_description(self) -> str:
        """Get description of redo action.

        Returns:
            Description string
        """
        return self.redo_stack[-1].description() if self.redo_stack else ""
