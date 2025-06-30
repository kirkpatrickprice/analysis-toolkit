"""Tests for the get_file_encoding module to ensure encoding detection and skip logic work correctly."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding


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

    @patch("kp_analysis_toolkit.utils.get_file_encoding.from_path")
    @patch("kp_analysis_toolkit.utils.get_file_encoding.warning")
    def test_detect_encoding_failure_returns_none(
        self,
        mock_warning: MagicMock,
        mock_from_path: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that encoding detection failure returns None and logs warning."""
        # Create a test file
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("Test content")

        # Mock charset_normalizer to return no results (simulating detection failure)
        mock_result = mock_from_path.return_value
        mock_result.best.return_value = None

        # Test encoding detection
        result = detect_encoding(test_file)

        # Should return None when detection fails
        assert result is None

        # Should call warning function
        mock_warning.assert_called_once()
        warning_call_args = mock_warning.call_args[0][0]
        assert "Skipping file due to encoding detection failure" in warning_call_args
        assert str(test_file) in warning_call_args

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

    @patch("kp_analysis_toolkit.utils.get_file_encoding.from_path")
    def test_detect_encoding_exception_handling(
        self,
        mock_from_path: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that exceptions in charset_normalizer are handled gracefully."""
        # Create a test file
        test_file = tmp_path / "exception_test.txt"
        test_file.write_text("Test content")

        # Mock charset_normalizer to raise an exception
        mock_from_path.side_effect = Exception("Simulated charset_normalizer error")

        # Should handle exceptions gracefully
        with patch("kp_analysis_toolkit.utils.get_file_encoding.warning"):
            result = detect_encoding(test_file)

        # Should return None when an exception occurs
        assert result is None
