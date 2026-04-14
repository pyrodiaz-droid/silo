"""Metadata handler for reading and writing audio file metadata."""

import logging
import os
from typing import Dict, Any, Optional
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
try:
    from mutagen.oggvorbis import OggVorbis
except ImportError:
    OggVorbis = None

logger = logging.getLogger(__name__)


# Custom Exceptions
class MetadataError(Exception):
    """Raised when metadata operations fail."""
    pass


class FileAccessError(Exception):
    """Raised when file access operations fail."""
    pass


def get_audio_format(file_path: str) -> Optional[str]:
    """Detect audio file format.

    Args:
        file_path: Path to audio file

    Returns:
        File extension (lowercase, with dot) or None if unsupported
    """
    ext = os.path.splitext(file_path)[1].lower()
    supported_extensions = ['.mp3', '.flac', '.ogg', '.m4a', '.m4b', '.mp4']

    if ext in supported_extensions:
        return ext
    return None


def _detect_audio_class(file_path: str):
    """Detect audio file type and return appropriate mutagen handler.

    Args:
        file_path: Path to audio file

    Returns:
        Mutagen audio class or None if unsupported
    """
    ext = os.path.splitext(file_path)[1].lower()

    format_map = {
        '.mp3': MP3,
        '.flac': FLAC,
        '.ogg': OggVorbis,
        '.m4a': MP4,
        '.m4b': MP4,
        '.mp4': MP4
    }

    return format_map.get(ext)


def _normalize_metadata_keys(audio, file_path: str) -> Dict[str, Any]:
    """Normalize metadata keys across different formats.

    Args:
        audio: Mutagen audio object
        file_path: Path to audio file

    Returns:
        Dictionary with normalized metadata keys
    """
    metadata = {}
    ext = os.path.splitext(file_path)[1].lower()

    # Field mappings for different formats
    if ext in ['.m4a', '.m4b', '.mp4']:
        # M4B/M4A mappings
        field_map = {
            '©nam': 'title',
            '©ART': 'author',
            'aART': 'narrator',
            '©alb': 'series',
            'trkn': 'series_number',
            '©day': 'year',
            '©gen': 'genre',
            'desc': 'description',
            '----:com.apple.iTunes:Publisher': 'publisher'
        }
    elif ext == '.mp3':
        # MP3 ID3 mappings
        field_map = {
            'TIT2': 'title',
            'TPE1': 'author',
            'TPE2': 'narrator',
            'TALB': 'series',
            'TRCK': 'series_number',
            'TDRC': 'year',
            'TCON': 'genre',
            'COMM': 'description',
            'TCOP': 'publisher'
        }
    elif ext == '.flac':
        # FLAC mappings
        field_map = {
            'TITLE': 'title',
            'ARTIST': 'author',
            'ALBUMARTIST': 'narrator',
            'ALBUM': 'series',
            'TRACKNUMBER': 'series_number',
            'DATE': 'year',
            'GENRE': 'genre',
            'DESCRIPTION': 'description'
        }
    else:
        field_map = {}

    # Extract and map metadata
    if hasattr(audio, 'tags') and audio.tags:
        for key, value in audio.tags.items():
            normalized_key = field_map.get(str(key), str(key).lower())

            # Handle different value types
            if isinstance(value, list):
                if value:
                    metadata[normalized_key] = str(value[0])
                else:
                    metadata[normalized_key] = ''
            else:
                metadata[normalized_key] = str(value)

    # Get audio length
    if hasattr(audio, 'info'):
        minutes = int(audio.info.length // 60)
        seconds = int(audio.info.length % 60)
        metadata['length'] = f"{minutes}:{seconds:02d}"
        metadata['length_seconds'] = audio.info.length

    return metadata


def read_metadata(file_path: str) -> Dict[str, Any]:
    """Read metadata from audiobook file.

    Args:
        file_path: Path to audio file

    Returns:
        Dictionary containing metadata with keys:
        - title, author, narrator, series, series_number, publisher, year, genre, description
        - length (formatted as "MM:SS")
        - length_seconds (total seconds)

    Raises:
        FileAccessError: If file cannot be accessed
        MetadataError: If metadata cannot be read or format is unsupported
    """
    audio_class = _detect_audio_class(file_path)

    if not audio_class:
        raise MetadataError(f"Unsupported format: {os.path.splitext(file_path)[1]}")

    try:
        audio = audio_class(file_path)
        metadata = _normalize_metadata_keys(audio, file_path)

        # Extract cover art
        from core.cover_handler import extract_cover_art
        cover_art = extract_cover_art(audio)

        # Read chapters (for M4B/M4A)
        from core.chapter_handler import read_chapters
        chapters = read_chapters(audio, file_path)

        # Return metadata with additional info
        metadata['_audio_object'] = audio
        metadata['_cover_art'] = cover_art
        metadata['_chapters'] = chapters

        return metadata

    except FileNotFoundError:
        raise FileAccessError(f"File not found: {file_path}")
    except PermissionError:
        raise FileAccessError(f"Permission denied: {file_path}")
    except Exception as e:
        raise MetadataError(f"Failed to read metadata: {str(e)}")


def apply_metadata(file_path: str, metadata: Dict[str, Any],
                  cover_art: Optional[bytes] = None,
                  audio_object: Optional[Any] = None) -> None:
    """Apply metadata changes to audio file.

    Args:
        file_path: Path to audio file
        metadata: Dictionary containing metadata fields to apply
        cover_art: Cover art image data (bytes), None to remove, or omit to keep existing
        audio_object: Optional cached mutagen audio object (for performance)

    Raises:
        FileAccessError: If file cannot be accessed
        MetadataError: If metadata cannot be applied
    """
    ext = os.path.splitext(file_path)[1].lower()

    # Get audio object from cache or load it
    if audio_object is None:
        audio_class = _detect_audio_class(file_path)
        if not audio_class:
            raise MetadataError(f"Unsupported format: {ext}")

        try:
            audio = audio_class(file_path)
        except FileNotFoundError:
            raise FileAccessError(f"File not found: {file_path}")
        except PermissionError:
            raise FileAccessError(f"Permission denied: {file_path}")
    else:
        audio = audio_object

    try:
        # Apply metadata changes
        if ext in ['.m4a', '.m4b', '.mp4']:
            # M4B/M4A format
            reverse_map = {
                'title': '©nam',
                'author': '©ART',
                'narrator': 'aART',
                'series': '©alb',
                'series_number': 'trkn',
                'year': '©day',
                'genre': '©gen',
                'description': 'desc',
                'publisher': '----:com.apple.iTunes:Publisher'
            }

            for field, value in metadata.items():
                if value and not field.startswith('_'):
                    key = reverse_map.get(field)
                    if key:
                        audio.tags[key] = value

            # Handle cover art
            if cover_art is not None:
                audio.tags['covr'] = [cover_art]
            elif cover_art is None and 'covr' in audio.tags:
                del audio.tags['covr']

        elif ext == '.mp3':
            # MP3 format
            from mutagen.id3 import TIT2, TPE1, TPE2, TALB, TRCK, TDRC, TCON, COMM, TCOP

            # Direct mapping
            for field, value in metadata.items():
                if value and not field.startswith('_'):
                    if field == 'title':
                        audio.tags['TIT2'] = TIT2(encoding=3, text=value)
                    elif field == 'author':
                        audio.tags['TPE1'] = TPE1(encoding=3, text=value)
                    elif field == 'narrator':
                        audio.tags['TPE2'] = TPE2(encoding=3, text=value)
                    elif field == 'series':
                        audio.tags['TALB'] = TALB(encoding=3, text=value)
                    elif field == 'series_number':
                        audio.tags['TRCK'] = TRCK(encoding=3, text=value)
                    elif field == 'year':
                        audio.tags['TDRC'] = TDRC(encoding=3, text=value)
                    elif field == 'genre':
                        audio.tags['TCON'] = TCON(encoding=3, text=value)
                    elif field == 'description':
                        audio.tags['COMM:'] = COMM(encoding=3, lang='eng', text=value)
                    elif field == 'publisher':
                        audio.tags['TCOP'] = TCOP(encoding=3, text=value)

            # Handle cover art
            if cover_art is not None:
                from mutagen.id3 import APIC
                audio.tags['APIC:'] = APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=cover_art
                )
            elif cover_art is None and 'APIC:' in audio.tags:
                del audio.tags['APIC:']

        elif ext == '.flac':
            # FLAC format
            reverse_map = {
                'title': 'TITLE',
                'author': 'ARTIST',
                'narrator': 'ALBUMARTIST',
                'series': 'ALBUM',
                'series_number': 'TRACKNUMBER',
                'year': 'DATE',
                'genre': 'GENRE',
                'description': 'DESCRIPTION'
            }

            for field, value in metadata.items():
                if value and not field.startswith('_'):
                    key = reverse_map.get(field)
                    if key:
                        audio[key] = value

            # Note: FLAC cover art handling is complex and would require
            # working with picture blocks - not implemented in this version

        # Save the file
        audio.save()
        logger.info(f"Successfully applied metadata to {file_path}")

    except Exception as e:
        raise MetadataError(f"Failed to apply metadata: {str(e)}")
