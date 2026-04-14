"""Validation utilities for Silo audiobook metadata editor."""

import logging
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from config.constants import MIN_YEAR, MAX_YEAR, MAX_IMAGE_SIZE

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    error_message: Optional[str] = None


def validate_year(value: str) -> ValidationResult:
    """Validate year input.

    Args:
        value: Year string to validate

    Returns:
        ValidationResult indicating validity
    """
    if not value:
        return ValidationResult(True)

    try:
        year = int(value)
        if not (MIN_YEAR <= year <= MAX_YEAR):
            return ValidationResult(
                False,
                f"Year must be between {MIN_YEAR} and {MAX_YEAR}"
            )
        return ValidationResult(True)
    except ValueError:
        return ValidationResult(False, "Year must be a number")


def validate_url(url: str) -> ValidationResult:
    """Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        ValidationResult indicating validity
    """
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return ValidationResult(False, "Invalid URL format")
        if result.scheme not in ['http', 'https']:
            return ValidationResult(False, "URL must use http or https")
        return ValidationResult(True)
    except Exception as e:
        logger.warning(f"URL validation error: {e}")
        return ValidationResult(False, "Invalid URL format")


def validate_image_size(image_data: bytes,
                       max_size: int = MAX_IMAGE_SIZE) -> ValidationResult:
    """Validate image size.

    Args:
        image_data: Image data as bytes
        max_size: Maximum allowed size in bytes

    Returns:
        ValidationResult indicating validity
    """
    if len(image_data) > max_size:
        return ValidationResult(
            False,
            f"Image too large ({len(image_data) / 1_000_000:.1f}MB, "
            f"max {max_size / 1_000_000}MB)"
        )
    return ValidationResult(True)
