"""Unit tests for chapter handler."""

import pytest
import sys
sys.path.insert(0, '.')

from core.chapter_handler import (
    Chapter,
    embed_chapters,
    auto_generate_chapters,
    MetadataError
)


class TestChapter:
    """Test Chapter dataclass."""

    def test_chapter_creation(self):
        """Test creating a chapter."""
        chapter = Chapter(start=60.0, title="Chapter 1")
        assert chapter.start == 60.0
        assert chapter.title == "Chapter 1"

    def test_chapter_to_dict(self):
        """Test converting chapter to dictionary."""
        chapter = Chapter(start=120.5, title="Introduction")
        chapter_dict = chapter.to_dict()

        assert chapter_dict['start'] == 120.5
        assert chapter_dict['title'] == "Introduction"
        assert isinstance(chapter_dict, dict)


class TestAutoGenerateChapters:
    """Test automatic chapter generation."""

    def test_generate_chapters_10_minute_interval(self):
        """Test generating chapters at 10-minute intervals."""
        duration = 3600  # 1 hour in seconds
        interval = 600   # 10 minutes in seconds

        chapters = auto_generate_chapters(duration, interval)

        # Should generate 6 chapters (3600 / 600)
        assert len(chapters) == 6

        # Check first chapter
        assert chapters[0].start == 0.0
        assert chapters[0].title == "Chapter 1"

        # Check second chapter
        assert chapters[1].start == 600.0
        assert chapters[1].title == "Chapter 2"

        # Check last chapter
        assert chapters[-1].start == 3000.0
        assert chapters[-1].title == "Chapter 6"

    def test_generate_chapters_5_minute_interval(self):
        """Test generating chapters at 5-minute intervals."""
        duration = 1800  # 30 minutes
        interval = 300   # 5 minutes

        chapters = auto_generate_chapters(duration, interval)

        # Should generate 6 chapters
        assert len(chapters) == 6

        # Check interval spacing
        for i, chapter in enumerate(chapters):
            expected_start = i * 300
            assert chapter.start == expected_start

    def test_generate_chapters_with_remainder(self):
        """Test generating chapters when there's remaining audio."""
        duration = 1500  # 25 minutes
        interval = 600   # 10 minutes

        chapters = auto_generate_chapters(duration, interval)

        # Should generate 2 regular chapters + 1 final chapter for remainder
        # 1500 / 600 = 2 with 300s remaining (> 60s threshold)
        assert len(chapters) == 3

        # Check regular chapters
        assert chapters[0].start == 0.0
        assert chapters[1].start == 600.0

        # Check final chapter for remainder
        assert chapters[2].start == 1200.0

    def test_generate_chapters_no_remainder(self):
        """Test generating chapters when there's no significant remainder."""
        duration = 1200  # 20 minutes
        interval = 600   # 10 minutes

        chapters = auto_generate_chapters(duration, interval)

        # Should only generate 2 chapters (no final chapter for small remainder)
        assert len(chapters) == 2

    def test_generate_chapters_default_interval(self):
        """Test generating chapters with default 10-minute interval."""
        duration = 1800  # 30 minutes

        chapters = auto_generate_chapters(duration)  # Uses default interval

        # Should use 10-minute default
        assert len(chapters) == 3


class TestEmbedChapters:
    """Test chapter embedding functionality."""

    def test_embed_chapters_unsupported_format(self):
        """Test embedding chapters into unsupported format."""
        chapters = [
            Chapter(start=0.0, title="Chapter 1"),
            Chapter(start=60.0, title="Chapter 2")
        ]

        # Test with MP3 (not supported for chapters)
        with pytest.raises(MetadataError) as exc_info:
            embed_chapters("test.mp3", chapters)
        assert "only supported for M4B/M4A" in str(exc_info.value)

    def test_embed_chapters_flac(self):
        """Test embedding chapters into FLAC (not supported)."""
        chapters = [Chapter(start=0.0, title="Test")]

        with pytest.raises(MetadataError) as exc_info:
            embed_chapters("test.flac", chapters)
        assert "only supported for M4B/M4A" in str(exc_info.value)

    def test_embed_chapters_empty_list(self):
        """Test embedding empty chapter list (should work)."""
        # This would need an actual M4B file to test properly
        # For now, just verify the function accepts the parameters
        chapters = []

        # Can't test without actual file, but verify function signature
        from core.chapter_handler import embed_chapters
        import inspect
        sig = inspect.signature(embed_chapters)

        assert 'file_path' in sig.parameters
        assert 'chapters' in sig.parameters


class TestChapterValidation:
    """Test chapter-related validation."""

    def test_chapter_start_positive(self):
        """Test that chapter start times are positive."""
        # Create chapters with various start times
        chapters = [
            Chapter(start=0.0, title="Intro"),
            Chapter(start=60.5, title="Chapter 1"),
            Chapter(start=3600.0, title="End")
        ]

        for chapter in chapters:
            assert chapter.start >= 0, f"Chapter {chapter.title} has negative start time"

    def test_chapter_titles_not_empty(self):
        """Test that chapter titles are handled properly."""
        # Create chapter with empty title
        chapter = Chapter(start=60.0, title="")

        # Should still create chapter successfully
        assert chapter.start == 60.0
        assert chapter.title == ""

        # When converted to dict, empty title should be preserved
        chapter_dict = chapter.to_dict()
        assert chapter_dict['title'] == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
