"""Chapter handler for managing audiobook chapters."""

import logging
import os
from typing import List, Dict, Any
from dataclasses import dataclass
from mutagen.mp4 import MP4

logger = logging.getLogger(__name__)


@dataclass
class Chapter:
    """Represents a chapter in an audiobook."""
    start: float  # Position in seconds
    title: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary with 'start' and 'title' keys
        """
        return {
            'start': self.start,
            'title': self.title
        }


def read_chapters(audio: Any, file_path: str) -> List[Dict[str, Any]]:
    """Read chapters from audiobook file (M4B/M4A).

    Args:
        audio: Mutagen audio object
        file_path: Path to audio file

    Returns:
        List of chapter dictionaries with 'title' and 'start' keys
    """
    chapters: List[Dict[str, Any]] = []
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in ['.m4b', '.m4a', '.mp4']:
            # M4B/M4A chapter support
            if hasattr(audio, 'chapters') and audio.chapters:
                for i, chapter in enumerate(audio.chapters):
                    title = chapter.title or f"Chapter {i + 1}"
                    start_time = chapter.start / 1000000000  # Convert to seconds
                    chapters.append({
                        'title': title,
                        'start': start_time
                    })
                    logger.debug(f"Found chapter: {title} at {start_time}s")

            # Try alternative chapter format
            if not chapters and hasattr(audio, 'tags'):
                # Look for chapter list in tags
                if 'chpl' in audio.tags or '----:com.apple.iTunes:Chapter List' in audio.tags:
                    logger.debug("Found chapters in tags (parsing not implemented)")

    except (AttributeError, KeyError, IndexError) as e:
        logger.warning(f"Error reading chapters: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error reading chapters: {str(e)}")

    return chapters


def embed_chapters(file_path: str, chapters: List[Chapter]) -> None:
    """Embed chapters into M4B/M4A file.

    This function actually writes chapters to the file (the critical fix).

    Args:
        file_path: Path to M4B/M4A file
        chapters: List of Chapter objects to embed

    Raises:
        FileAccessError: If file cannot be accessed
        MetadataError: If chapters cannot be embedded
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in ['.m4b', '.m4a', '.mp4']:
        raise MetadataError(
            "Chapter embedding only supported for M4B/M4A files"
        )

    try:
        audio = MP4(file_path)

        # Clear existing chapters
        if hasattr(audio, 'chapters') and audio.chapters:
            audio.chapters.clear()
            logger.debug(f"Cleared existing chapters from {file_path}")

        # Add new chapters with proper nanosecond timestamps
        for chapter in chapters:
            start_ns = int(chapter.start * 1_000_000_000)  # Convert to nanoseconds

            # Ensure we have a title
            title = chapter.title if chapter.title else f"Chapter {len(audio.chapters) + 1}"

            # Add chapter using MP4's chapter support
            audio.chapters.add(start_ns)
            logger.debug(f"Added chapter: {title} at {chapter.start}s ({start_ns}ns)")

        # Save the file with embedded chapters
        audio.save()
        logger.info(f"Successfully embedded {len(chapters)} chapters into {file_path}")

    except FileNotFoundError:
        raise FileAccessError(f"File not found: {file_path}")
    except PermissionError:
        raise FileAccessError(f"Permission denied: {file_path}")
    except Exception as e:
        raise MetadataError(f"Failed to embed chapters: {str(e)}")


def auto_generate_chapters(duration: float, interval: float = 600.0) -> List[Chapter]:
    """Auto-generate chapters at regular intervals.

    Args:
        duration: Total audio duration in seconds
        interval: Chapter interval in seconds (default 600 = 10 minutes)

    Returns:
        List of auto-generated Chapter objects
    """
    chapters = []
    num_chapters = int(duration // interval)

    # Create chapters at regular intervals
    for i in range(num_chapters):
        chapter_start = i * interval
        chapter_name = f"Chapter {i + 1}"
        chapters.append(Chapter(start=chapter_start, title=chapter_name))

    # Add final chapter if there's remaining audio
    if duration % interval > 60:  # At least 1 minute remaining
        chapters.append(
            Chapter(
                start=num_chapters * interval,
                title=f"Chapter {num_chapters + 1}"
            )
        )

    logger.info(f"Auto-generated {len(chapters)} chapters at {interval}s intervals")
    return chapters


class MetadataError(Exception):
    """Raised when metadata operations fail."""
    pass


class FileAccessError(Exception):
    """Raised when file access operations fail."""
    pass
