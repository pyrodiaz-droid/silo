"""Unit tests for validation functions."""

import pytest
import sys
sys.path.insert(0, '.')

from utils.validators import (
    ValidationResult,
    validate_year,
    validate_url,
    validate_image_size
)


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_valid_result(self):
        """Test creating a valid result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.error_message is None

    def test_invalid_result(self):
        """Test creating an invalid result with message."""
        result = ValidationResult(is_valid=False, error_message="Test error")
        assert result.is_valid is False
        assert result.error_message == "Test error"


class TestYearValidation:
    """Test year validation."""

    def test_valid_year(self):
        """Test valid year inputs."""
        # Valid years
        assert validate_year("2024").is_valid is True
        assert validate_year("1000").is_valid is True
        assert validate_year("9999").is_valid is True

    def test_empty_year(self):
        """Test empty year (should be valid)."""
        assert validate_year("").is_valid is True
        assert validate_year("   ").is_valid is True  # Should handle whitespace

    def test_invalid_year_too_old(self):
        """Test year before minimum."""
        result = validate_year("999")
        assert result.is_valid is False
        assert "between 1000 and 9999" in result.error_message

    def test_invalid_year_too_new(self):
        """Test year after maximum."""
        result = validate_year("10000")
        assert result.is_valid is False
        assert "between 1000 and 9999" in result.error_message

    def test_invalid_year_not_number(self):
        """Test year that's not a number."""
        result = validate_year("abc")
        assert result.is_valid is False
        assert "must be a number" in result.error_message

    def test_invalid_year_partial_number(self):
        """Test year with mixed characters."""
        result = validate_year("2024a")
        assert result.is_valid is False
        assert "must be a number" in result.error_message


class TestURLValidation:
    """Test URL validation."""

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        assert validate_url("http://example.com/image.jpg").is_valid is True
        assert validate_url("http://example.com/path/to/image.png").is_valid is True

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        assert validate_url("https://example.com/image.jpg").is_valid is True
        assert validate_url("https://cdn.example.com/images/cover.png").is_valid is True

    def test_invalid_url_no_scheme(self):
        """Test URL without scheme."""
        result = validate_url("example.com/image.jpg")
        assert result.is_valid is False
        assert "Invalid URL" in result.error_message

    def test_invalid_url_wrong_scheme(self):
        """Test URL with unsupported scheme."""
        result = validate_url("ftp://example.com/image.jpg")
        assert result.is_valid is False
        assert "http or https" in result.error_message

    def test_invalid_url_no_netloc(self):
        """Test URL without network location."""
        result = validate_url("https://")
        assert result.is_valid is False
        assert "Invalid URL" in result.error_message


class TestImageSizeValidation:
    """Test image size validation."""

    def test_valid_small_image(self):
        """Test small image under limit."""
        small_image = b'x' * 1000  # 1KB
        assert validate_image_size(small_image).is_valid is True

    def test_valid_medium_image(self):
        """Test medium image under limit."""
        medium_image = b'x' * 5_000_000  # 5MB
        assert validate_image_size(medium_image).is_valid is True

    def test_valid_image_at_limit(self):
        """Test image exactly at limit."""
        max_image = b'x' * 10_000_000  # 10MB
        assert validate_image_size(max_image).is_valid is True

    def test_invalid_oversized_image(self):
        """Test image over limit."""
        large_image = b'x' * 15_000_000  # 15MB
        result = validate_image_size(large_image)
        assert result.is_valid is False
        assert "too large" in result.error_message
        assert "15.0MB" in result.error_message
        assert "10.0MB" in result.error_message

    def test_custom_size_limit(self):
        """Test validation with custom size limit."""
        image = b'x' * 5_000_000  # 5MB
        # Should fail with 1MB limit
        result = validate_image_size(image, max_size=1_000_000)
        assert result.is_valid is False
        assert "5.0MB" in result.error_message
        assert "1.0MB" in result.error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
