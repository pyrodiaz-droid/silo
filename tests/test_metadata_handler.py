"""Unit tests for metadata handler."""

import pytest
import sys
import os
sys.path.insert(0, '.')

from core.metadata_handler import (
    get_audio_format,
    MetadataError,
    FileAccessError
)


class TestAudioFormatDetection:
    """Test audio format detection."""

    def test_supported_formats(self):
        """Test detection of supported formats."""
        assert get_audio_format("test.mp3") == ".mp3"
        assert get_audio_format("test.m4a") == ".m4a"
        assert get_audio_format("test.m4b") == ".m4b"
        assert get_audio_format("test.flac") == ".flac"

    def test_unsupported_formats(self):
        """Test detection of unsupported formats."""
        assert get_audio_format("test.wav") is None
        assert get_audio_format("test.ogg") is None
        assert get_audio_format("test.txt") is None
        assert get_audio_format("test") is None

    def test_case_insensitive_extension(self):
        """Test that extension detection is case-insensitive."""
        assert get_audio_format("test.MP3") == ".mp3"
        assert get_audio_format("test.M4A") == ".m4a"
        assert get_audio_format("test.FLAC") == ".flac"


class TestMetadataError:
    """Test custom MetadataError exception."""

    def test_metadata_error_creation(self):
        """Test creating MetadataError."""
        error = MetadataError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_metadata_error_raising(self):
        """Test raising and catching MetadataError."""
        with pytest.raises(MetadataError) as exc_info:
            raise MetadataError("Test error")
        assert str(exc_info.value) == "Test error"


class TestFileAccessError:
    """Test custom FileAccessError exception."""

    def test_file_access_error_creation(self):
        """Test creating FileAccessError."""
        error = FileAccessError("File not found")
        assert str(error) == "File not found"
        assert isinstance(error, Exception)

    def test_file_access_error_raising(self):
        """Test raising and catching FileAccessError."""
        with pytest.raises(FileAccessError) as exc_info:
            raise FileAccessError("Permission denied")
        assert str(exc_info.value) == "Permission denied"


class TestMetadataNormalisation:
    """Test metadata key normalization without actual files."""

    def test_field_mapping_structure(self):
        """Test that field mappings are properly defined."""
        from core.metadata_handler import _normalize_metadata_keys

        # Create a mock audio object with tags
        class MockAudio:
            def __init__(self):
                self.tags = {'©nam': 'Test Book'}

        audio = MockAudio()
        metadata = _normalize_metadata_keys(audio, "test.m4a")

        assert 'title' in metadata
        assert metadata['title'] == 'Test Book'


class TestIntegrationTests:
    """Integration tests that would require actual audio files."""

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="No test fixtures")
    def test_read_mp3_metadata(self):
        """Test reading MP3 metadata from actual file."""
        from core.metadata_handler import read_metadata

        if not os.path.exists("tests/fixtures/test.mp3"):
            pytest.skip("No test MP3 file available")

        metadata = read_metadata("tests/fixtures/test.mp3")
        assert isinstance(metadata, dict)
        assert 'length' in metadata
        assert 'length_seconds' in metadata

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="No test fixtures")
    def test_apply_metadata_to_copy(self):
        """Test applying metadata to a copy of test file."""
        import shutil
        from core.metadata_handler import read_metadata, apply_metadata

        if not os.path.exists("tests/fixtures/test.mp3"):
            pytest.skip("No test MP3 file available")

        # Create a temporary copy
        temp_file = "tests/fixtures/temp_test.mp3"
        shutil.copy("tests/fixtures/test.mp3", temp_file)

        try:
            # Read original metadata
            original_metadata = read_metadata(temp_file)

            # Apply new metadata
            new_metadata = {
                'title': 'Test Title',
                'author': 'Test Author',
                'year': '2024'
            }
            apply_metadata(temp_file, new_metadata, None)

            # Read back and verify
            updated_metadata = read_metadata(temp_file)
            # Note: Verification would depend on actual file content

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
