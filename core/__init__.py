"""Core functionality modules for Silo audiobook metadata editor."""

from core.metadata_handler import (
    read_metadata,
    apply_metadata,
    get_audio_format,
    MetadataError,
    FileAccessError
)
from core.chapter_handler import (
    Chapter,
    read_chapters,
    embed_chapters,
    auto_generate_chapters
)
from core.cover_handler import (
    extract_cover,
    load_cover_from_file,
    load_cover_from_url,
    validate_cover_image,
    save_cover_to_file
)
from core.undo_manager import (
    Command,
    MetadataChangeCommand,
    UndoManager
)

__all__ = [
    # Metadata handler
    'read_metadata',
    'apply_metadata',
    'get_audio_format',
    'MetadataError',
    'FileAccessError',
    # Chapter handler
    'Chapter',
    'read_chapters',
    'embed_chapters',
    'auto_generate_chapters',
    # Cover handler
    'extract_cover',
    'load_cover_from_file',
    'load_cover_from_url',
    'validate_cover_image',
    'save_cover_to_file',
    # Undo manager
    'Command',
    'MetadataChangeCommand',
    'UndoManager'
]
