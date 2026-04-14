"""Cover art handler for managing audiobook cover images."""

import logging
import os
from typing import Optional
from PIL import Image
from io import BytesIO

from utils.validators import validate_image_size

logger = logging.getLogger(__name__)


def extract_cover(audio: Any) -> Optional[bytes]:
    """Extract cover art from audio file.

    Args:
        audio: Mutagen audio object

    Returns:
        Cover art as bytes, or None if not found
    """
    try:
        if hasattr(audio, 'pictures') and audio.pictures:
            # FLAC format
            if audio.pictures:
                return audio.pictures[0].data
        elif hasattr(audio, 'tags') and audio.tags:
            # M4B/M4A format
            if 'covr' in audio.tags:
                cover_data = audio.tags['covr']
                if isinstance(cover_data, list) and cover_data:
                    return cover_data[0]
                elif cover_data:
                    return cover_data
            # MP3 format
            elif 'APIC:' in str(audio.tags):
                for key in audio.tags.keys():
                    if 'APIC' in str(key):
                        apic = audio.tags[key]
                        if hasattr(apic, 'data'):
                            return apic.data
    except (AttributeError, KeyError, IndexError) as e:
        logger.warning(f"Error extracting cover art: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error extracting cover art: {str(e)}")

    return None


def load_cover_from_file(file_path: str) -> bytes:
    """Load cover art from image file.

    Args:
        file_path: Path to image file

    Returns:
        Image data as bytes

    Raises:
        FileAccessError: If file cannot be read
        MetadataError: If image validation fails
    """
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()

        # Validate image size
        validation = validate_image_size(image_data)
        if not validation.is_valid:
            raise MetadataError(validation.error_message)

        logger.info(f"Loaded cover art from {file_path}")
        return image_data

    except FileNotFoundError:
        raise FileAccessError(f"File not found: {file_path}")
    except PermissionError:
        raise FileAccessError(f"Permission denied: {file_path}")
    except Exception as e:
        raise MetadataError(f"Failed to load cover art: {str(e)}")


def load_cover_from_url(url: str, timeout: int = 30) -> bytes:
    """Load cover art from URL.

    Args:
        url: URL to image
        timeout: Request timeout in seconds

    Returns:
        Image data as bytes

    Raises:
        FileAccessError: If URL cannot be accessed
        MetadataError: If image validation fails
    """
    try:
        import urllib.request

        # Download the image
        with urllib.request.urlopen(url, timeout=timeout) as response:
            image_data = response.read()

        # Validate image size
        validation = validate_image_size(image_data)
        if not validation.is_valid:
            raise MetadataError(validation.error_message)

        logger.info(f"Loaded cover art from URL: {url}")
        return image_data

    except Exception as e:
        raise FileAccessError(f"Failed to download image from URL: {str(e)}")


def validate_cover_image(image_data: bytes) -> None:
    """Validate cover image (size, format).

    Args:
        image_data: Image data as bytes

    Raises:
        MetadataError: If validation fails
    """
    # Validate size
    validation = validate_image_size(image_data)
    if not validation.is_valid:
        raise MetadataError(validation.error_message)

    # Validate it's actually an image
    try:
        img = Image.open(BytesIO(image_data))
        img.verify()
        logger.debug(f"Image validation passed: {img.format} {img.size}")
    except Exception as e:
        raise MetadataError(f"Invalid image format: {str(e)}")


def save_cover_to_file(cover_data: bytes, output_path: str) -> None:
    """Save cover art to file.

    Args:
        cover_data: Cover art data as bytes
        output_path: Path where to save the cover art

    Raises:
        FileAccessError: If file cannot be written
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(cover_data)

        logger.info(f"Saved cover art to {output_path}")

    except PermissionError:
        raise FileAccessError(f"Permission denied: {output_path}")
    except Exception as e:
        raise FileAccessError(f"Failed to save cover art: {str(e)}")


class MetadataError(Exception):
    """Raised when metadata operations fail."""
    pass


class FileAccessError(Exception):
    """Raised when file access operations fail."""
    pass
