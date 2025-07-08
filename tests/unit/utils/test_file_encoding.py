"""Tests for the get_file_encoding module to ensure encoding detection and skip logic work correctly."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from kp_analysis_toolkit.utils.get_file_encoding import (
    clear_file_processing_service,
    detect_encoding,
    set_file_processing_service,
)


class TestDetectEncoding:
    """Tests for the detect_encoding function."""

    def test_detect_encoding_utf8_file(self, tmp_path: Path) -> None:
        """Test that UTF-8 files are correctly detected."""
        # Create a UTF-8 encoded file
        test_file = tmp_path / "utf8_test.txt"
        content = "This is a UTF-8 encoded file with some content."
        test_file.write_text(content, encoding="utf-8")

        # Test encoding detection
        result = detect_encoding(test_file)

        # Should detect UTF-8 encoding
        assert result is not None
        assert result.lower() in [
            "utf-8",
            "utf_8",
            "ascii",
        ]  # ASCII is a subset of UTF-8

    def test_detect_encoding_ascii_file(self, tmp_path: Path) -> None:
        """Test that ASCII files are correctly detected."""
        # Create an ASCII file
        test_file = tmp_path / "ascii_test.txt"
        content = "Simple ASCII text file with basic characters only."
        test_file.write_text(content, encoding="ascii")

        # Test encoding detection
        result = detect_encoding(test_file)

        # Should detect ASCII or UTF-8 (ASCII is a subset of UTF-8)
        assert result is not None
        assert result.lower() in ["ascii", "utf-8", "utf_8"]

    def test_detect_encoding_windows_1252_file(self, tmp_path: Path) -> None:
        """Test that Windows-1252 files are correctly detected."""
        # Create a Windows-1252 encoded file with special characters
        test_file = tmp_path / "windows1252_test.txt"
        content = "Windows-1252 file with special chars: €•™"
        test_file.write_bytes(content.encode("windows-1252"))

        # Test encoding detection
        result = detect_encoding(test_file)

        # Should detect some encoding (could be windows-1252, cp1252, or similar)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_detect_encoding_failure_returns_none(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that encoding detection failure returns None via DI service."""
        # Test with DI service that returns None (simulating detection failure)

        # Create mock service that fails encoding detection
        mock_service = MagicMock()
        mock_service.detect_encoding.return_value = None

        # Set up DI service
        set_file_processing_service(mock_service)

        try:
            # Create a test file
            test_file = tmp_path / "test_file.txt"
            test_file.write_text("Test content")

            # Test encoding detection with DI service that returns None
            result = detect_encoding(test_file)

            # Should return None when DI service fails detection
            assert result is None

            # Should have called the DI service
            mock_service.detect_encoding.assert_called_once_with(test_file)

        finally:
            # Clean up DI service
            clear_file_processing_service()

    def test_detect_encoding_with_string_path(self, tmp_path: Path) -> None:
        """Test that function works with string paths as well as Path objects."""
        # Create a test file
        test_file = tmp_path / "string_path_test.txt"
        content = "Test file for string path handling."
        test_file.write_text(content, encoding="utf-8")

        # Test with string path
        result = detect_encoding(str(test_file))

        # Should detect encoding successfully
        assert result is not None
        assert isinstance(result, str)

    def test_detect_encoding_nonexistent_file(self) -> None:
        """Test behavior with non-existent file."""
        nonexistent_file = Path("/nonexistent/path/file.txt")

        # Should handle gracefully (charset_normalizer will return None)
        with patch("kp_analysis_toolkit.utils.get_file_encoding.warning"):
            result = detect_encoding(nonexistent_file)

        # Should return None for non-existent files
        assert result is None

    def test_detect_encoding_empty_file(self, tmp_path: Path) -> None:
        """Test encoding detection on empty files."""
        # Create an empty file
        test_file = tmp_path / "empty_test.txt"
        test_file.touch()

        # Test encoding detection on empty file
        # Note: charset_normalizer behavior with empty files may vary
        result = detect_encoding(test_file)

        # Result could be None (no content to analyze) or a default encoding
        # We just verify it doesn't crash
        assert result is None or isinstance(result, str)

    def test_detect_encoding_binary_file(self, tmp_path: Path) -> None:
        """Test encoding detection on binary files (should return None)."""
        # Create a binary file
        test_file = tmp_path / "binary_test.bin"
        # Write some binary data
        binary_data = bytes(range(256))
        test_file.write_bytes(binary_data)

        # Test encoding detection on binary file
        with patch("kp_analysis_toolkit.utils.get_file_encoding.warning"):
            result = detect_encoding(test_file)

        # Binary files should typically fail encoding detection
        # (though this depends on charset_normalizer's behavior)
        assert result is None or isinstance(result, str)

    def test_detect_encoding_exception_handling(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that exceptions in DI service are handled gracefully with fallback."""
        # Create mock service that raises an exception
        mock_service = MagicMock()
        mock_service.detect_encoding.side_effect = Exception(
            "Simulated DI service error"
        )

        # Set up DI service
        set_file_processing_service(mock_service)

        try:
            # Create a test file
            test_file = tmp_path / "exception_test.txt"
            test_file.write_text("Test content")

            # Should handle DI service exceptions gracefully and fallback to direct implementation
            result = detect_encoding(test_file)

            # Should have tried the DI service first
            mock_service.detect_encoding.assert_called_once_with(test_file)

            # Should fallback to direct implementation and return a valid encoding
            # (since we have real content, charset_normalizer should detect something)
            assert result is not None
            assert isinstance(result, str)

        finally:
            # Clean up DI service
            clear_file_processing_service()

    def test_detect_encoding_fallback_to_direct_implementation(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that fallback to direct implementation works when DI is not available."""
        # Ensure no DI service is set
        clear_file_processing_service()

        try:
            # Create a test file
            test_file = tmp_path / "fallback_test.txt"
            test_file.write_text("Test content for fallback")

            # Should use direct implementation when no DI service is available
            result = detect_encoding(test_file)

            # Should still return a valid encoding via direct implementation
            assert result is not None
            assert isinstance(result, str)

        finally:
            # Ensure clean state
            clear_file_processing_service()
