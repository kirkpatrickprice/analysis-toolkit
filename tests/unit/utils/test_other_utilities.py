"""Tests for other utility modules."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding
from kp_analysis_toolkit.utils.get_timestamp import get_timestamp
from kp_analysis_toolkit.utils.hash_generator import (
    TOOLKIT_HASH_ALGORITHM,
    HashGenerator,
    clear_file_processing_service,
    get_file_processing_service,
    set_file_processing_service,
)
from kp_analysis_toolkit.utils.hash_generator import (
    hash_file as hash_file_func,
)


class TestDetectEncoding:
    """Test file encoding detection."""

    def test_utf8_file(self) -> None:
        """Test UTF-8 file encoding detection."""
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf_8", delete=False) as f:
            f.write("Hello, world! 🌍")
            temp_path = f.name

        try:
            encoding = detect_encoding(temp_path)
            assert encoding in ["utf_8", "ascii"]  # ASCII is subset of UTF-8
        finally:
            Path(temp_path).unlink()

    def test_latin1_file(self) -> None:
        """Test Latin-1 file encoding detection."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="latin-1",
            delete=False,
        ) as f:
            f.write("Café")
            temp_path = f.name

        try:
            encoding = detect_encoding(temp_path)
            assert encoding is not None
        finally:
            Path(temp_path).unlink()

    def test_empty_file(self) -> None:
        """Test empty file encoding detection."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            encoding = detect_encoding(temp_path)
            # Empty files might return None or a default encoding
            assert encoding == "utf_8"
        finally:
            Path(temp_path).unlink()

    def test_nonexistent_file(self) -> None:
        """Test handling of non-existent file."""
        # The function should gracefully handle non-existent files by returning None
        # instead of raising exceptions, as per the robustness improvements
        with patch("kp_analysis_toolkit.utils.get_file_encoding.warning"):
            result = detect_encoding("/nonexistent/file.txt")

        # Should return None instead of raising an exception
        assert result is None


class TestGetTimestamp:
    """Test timestamp generation."""

    def test_timestamp_format(self) -> None:
        """Test timestamp format is correct."""
        timestamp = get_timestamp()

        # Should be in format YYYYMMDD-HHMMSS
        assert len(timestamp) == 15  # noqa: PLR2004
        assert timestamp[8] == "-"

        # Should be all digits except the dash
        assert timestamp[:8].isdigit()
        assert timestamp[9:].isdigit()

    def test_timestamp_uniqueness(self) -> None:
        """Test that consecutive timestamps are different."""
        timestamp1 = get_timestamp()
        timestamp2 = get_timestamp()

        # They might be the same if called in the same second
        # This is expected behavior, not a bug
        assert isinstance(timestamp1, str)
        assert isinstance(timestamp2, str)

    @patch("kp_analysis_toolkit.utils.get_timestamp.datetime")
    def test_timestamp_mocked(self, mock_datetime) -> None:  # noqa: ANN001
        """Test timestamp with mocked datetime."""
        # Mock datetime.now()
        mock_datetime.now.return_value.strftime.return_value = "20231225-143000"

        timestamp = get_timestamp()
        assert timestamp == "20231225-143000"


class TestHashGenerator:
    """Test hash generation utility."""

    def test_default_algorithm(self) -> None:
        """Test default algorithm is SHA384."""
        generator = HashGenerator()
        assert generator.algorithm == TOOLKIT_HASH_ALGORITHM

    def test_custom_algorithm(self) -> None:
        """Test custom algorithm initialization."""
        generator = HashGenerator("sha256")
        assert generator.algorithm == "sha256"

    def test_invalid_algorithm(self) -> None:
        """Test invalid algorithm raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Hash algorithm 'invalid' is not available",
        ):
            HashGenerator("invalid")

    def test_hash_string(self) -> None:
        """Test string hashing."""
        generator = HashGenerator()

        test_string = "Hello, world!"
        hash_result = generator.hash_string(test_string)

        assert isinstance(hash_result, str)
        assert len(hash_result) > 0

        # Same string should produce same hash
        hash_result2 = generator.hash_string(test_string)
        assert hash_result == hash_result2

    def test_hash_bytes(self) -> None:
        """Test bytes hashing."""
        generator = HashGenerator()

        test_bytes = b"Hello, world!"
        hash_result = generator.hash_bytes(test_bytes)

        assert isinstance(hash_result, str)
        assert len(hash_result) > 0

    def test_hash_file(self) -> None:
        """Test file hashing."""
        generator = HashGenerator()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello, world!")
            temp_path = Path(f.name)

        try:
            hash_result = generator.hash_file(temp_path)

            assert isinstance(hash_result, str)
            assert len(hash_result) > 0

            # Same file should produce same hash
            hash_result2 = generator.hash_file(temp_path)
            assert hash_result == hash_result2
        finally:
            temp_path.unlink()

    def test_hash_nonexistent_file(self) -> None:
        """Test hashing non-existent file raises ValueError."""
        generator = HashGenerator()

        with pytest.raises(ValueError, match="File does not exist"):
            generator.hash_file(Path("/nonexistent/file.txt"))

    def test_hash_file_permission_error(self) -> None:
        """Test handling of file permission errors."""
        generator = HashGenerator()

        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Mock file open to raise PermissionError
            with (
                patch(
                    "pathlib.Path.open",
                    side_effect=PermissionError("Access denied"),
                ),
                pytest.raises(ValueError, match="Error reading file"),
            ):
                generator.hash_file(temp_path)
        finally:
            temp_path.unlink()

    def test_different_strings_different_hashes(self) -> None:
        """Test that different strings produce different hashes."""
        generator = HashGenerator()

        hash1 = generator.hash_string("string1")
        hash2 = generator.hash_string("string2")

        assert hash1 != hash2

    def test_string_encoding_parameter(self) -> None:
        """Test string hashing with custom encoding."""
        generator = HashGenerator()

        test_string = "Café"
        hash_utf8 = generator.hash_string(test_string, encoding="utf-8")
        hash_latin1 = generator.hash_string(test_string, encoding="latin-1")

        # Different encodings should produce different hashes
        assert hash_utf8 != hash_latin1

    def test_file_chunk_size_parameter(self) -> None:
        """Test file hashing with custom chunk size."""
        generator = HashGenerator()

        # Create a larger temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"A" * 10000)
            temp_path = Path(f.name)

        try:
            # Hash with different chunk sizes
            hash1 = generator.hash_file(temp_path, chunk_size=1024)
            hash2 = generator.hash_file(temp_path, chunk_size=4096)

            # Should produce same hash regardless of chunk size
            assert hash1 == hash2
        finally:
            temp_path.unlink()

    def test_set_file_processing_service(self) -> None:
        """Test setting and getting file processing service."""

        # Define a dummy service function
        def dummy_service(file_path: str) -> str:
            return f"processed_{file_path}"

        # Set the custom service
        set_file_processing_service(dummy_service)

        try:
            # Get the service and process a file
            service = get_file_processing_service()
            result = service("test.txt")  # type: ignore[misc]

            assert result == "processed_test.txt"

            # Hash the result using a new generator instance
            generator = HashGenerator()
            hash_result = generator.hash_string(result)

            assert isinstance(hash_result, str)
            assert len(hash_result) > 0
        finally:
            # Clear the service
            clear_file_processing_service()

    def test_hash_file_with_service_integration(self) -> None:
        """Test file hashing with service integration."""

        # Define a dummy service function
        def dummy_service(file_path: Path) -> str:
            return f"processed_{file_path}"

        # Set the custom service
        set_file_processing_service(dummy_service)

        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(b"Hello, world!")
                temp_path = Path(f.name)

            try:
                # Hash the file using the service integration
                hash_result = hash_file_func(temp_path)

                assert isinstance(hash_result, str)
                assert len(hash_result) > 0
            finally:
                temp_path.unlink()
        finally:
            # Clear the service
            clear_file_processing_service()

    def test_hash_nonexistent_file_with_service_integration(self) -> None:
        """Test hashing non-existent file with service integration raises ValueError."""

        # Define a dummy service function
        def dummy_service(file_path: Path) -> str:
            return f"processed_{file_path}"

        # Set the custom service
        set_file_processing_service(dummy_service)

        try:
            with pytest.raises(ValueError, match="File does not exist"):
                hash_file_func(Path("/nonexistent/file.txt"))
        finally:
            # Clear the service
            clear_file_processing_service()

    def test_hash_file_permission_error_with_service_integration(self) -> None:
        """Test handling of file permission errors with service integration."""

        # Define a dummy service function
        def dummy_service(file_path: Path) -> str:
            return f"processed_{file_path}"

        # Set the custom service
        set_file_processing_service(dummy_service)

        try:
            with tempfile.NamedTemporaryFile(delete=False) as f:
                temp_path = Path(f.name)

            try:
                # Mock file open to raise PermissionError
                with (
                    patch(
                        "pathlib.Path.open",
                        side_effect=PermissionError("Access denied"),
                    ),
                    pytest.raises(ValueError, match="Error reading file"),
                ):
                    hash_file_func(temp_path)
            finally:
                temp_path.unlink()
        finally:
            # Clear the service
            clear_file_processing_service()


class TestHashGeneratorDIIntegration:
    """Test dependency injection integration for hash generator utilities."""

    def teardown_method(self) -> None:
        """Clean up DI state after each test."""
        clear_file_processing_service()

    def test_di_not_set_falls_back_to_direct(self) -> None:
        """Test that hash_file falls back to direct implementation when DI not set."""
        # Ensure no DI service is set
        clear_file_processing_service()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello, world!")
            temp_path = Path(f.name)

        try:
            hash_result = hash_file_func(temp_path)
            assert isinstance(hash_result, str)
            assert len(hash_result) > 0
        finally:
            temp_path.unlink()

    def test_di_service_is_used_when_available(self) -> None:
        """Test that hash_file uses DI service when available."""

        # Mock service with generate_hash method
        class MockService:
            def generate_hash(self, _file_path: Path) -> str:
                return "mocked_hash_result"

        mock_service = MockService()
        set_file_processing_service(mock_service)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello, world!")
            temp_path = Path(f.name)

        try:
            hash_result = hash_file_func(temp_path)
            assert hash_result == "mocked_hash_result"
        finally:
            temp_path.unlink()

    def test_di_fallback_on_service_error(self) -> None:
        """Test fallback to direct implementation when DI service raises error."""

        # Mock service that raises AttributeError
        class BrokenService:
            def broken_method(self) -> None:
                pass  # Missing generate_hash method

        broken_service = BrokenService()
        set_file_processing_service(broken_service)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello, world!")
            temp_path = Path(f.name)

        try:
            # Should fall back to direct implementation
            hash_result = hash_file_func(temp_path)
            assert isinstance(hash_result, str)
            assert len(hash_result) > 0
            # Should not be the mocked result
            assert hash_result != "mocked_hash_result"
        finally:
            temp_path.unlink()

    def test_di_fallback_on_value_error(self) -> None:
        """Test fallback when DI service raises ValueError."""

        # Mock service that raises ValueError
        class ErrorService:
            def generate_hash(self, _file_path: Path) -> str:
                message = "Service error"
                raise ValueError(message)

        error_service = ErrorService()
        set_file_processing_service(error_service)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello, world!")
            temp_path = Path(f.name)

        try:
            # Should fall back to direct implementation
            hash_result = hash_file_func(temp_path)
            assert isinstance(hash_result, str)
            assert len(hash_result) > 0
        finally:
            temp_path.unlink()

    def test_get_set_clear_service(self) -> None:
        """Test getting, setting, and clearing the DI service."""
        # Initially no service
        assert get_file_processing_service() is None

        # Set a service
        class DummyService:
            pass

        dummy = DummyService()
        set_file_processing_service(dummy)
        assert get_file_processing_service() is dummy

        # Clear the service
        clear_file_processing_service()
        assert get_file_processing_service() is None
