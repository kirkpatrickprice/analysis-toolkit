"""Tests for file processing service and container."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from kp_analysis_toolkit.core.services.file_processing import (
    FileProcessingService,
)
from kp_analysis_toolkit.core.services.file_processing.protocols import (
    EncodingDetector,
    FileValidator,
    HashGenerator,
)


@pytest.mark.file_processing
@pytest.mark.core
@pytest.mark.unit
class TestFileProcessingService:
    """Test the FileProcessingService class."""

    def test_file_processing_service_initialization(self) -> None:
        """Test that FileProcessingService can be initialized."""
        # Create mocks for dependencies
        encoding_detector = Mock(spec=EncodingDetector)
        hash_generator = Mock(spec=HashGenerator)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock()

        # Initialize service
        service = FileProcessingService(
            encoding_detector=encoding_detector,
            hash_generator=hash_generator,
            file_validator=file_validator,
            rich_output=rich_output,
        )

        assert service.encoding_detector is encoding_detector
        assert service.hash_generator is hash_generator
        assert service.file_validator is file_validator
        assert service.rich_output is rich_output

    def test_process_file_success(self, tmp_path: Path) -> None:
        """Test successful file processing."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create mocks
        encoding_detector = Mock(spec=EncodingDetector)
        hash_generator = Mock(spec=HashGenerator)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock()

        # Configure mocks
        encoding_detector.detect_encoding.return_value = "utf-8"
        hash_generator.generate_hash.return_value = "abc123hash"
        file_validator.validate_file_exists.return_value = True

        # Initialize service
        service = FileProcessingService(
            encoding_detector=encoding_detector,
            hash_generator=hash_generator,
            file_validator=file_validator,
            rich_output=rich_output,
        )

        # Test process_file
        result = service.process_file(test_file)

        assert result["encoding"] == "utf-8"
        assert result["hash"] == "abc123hash"
        assert result["path"] == str(test_file)

        # Verify method calls
        file_validator.validate_file_exists.assert_called_once_with(test_file)
        encoding_detector.detect_encoding.assert_called_once_with(test_file)
        hash_generator.generate_hash.assert_called_once_with(test_file)

    def test_process_file_validation_failure(self, tmp_path: Path) -> None:
        """Test file processing when validation fails."""
        # Non-existent file
        test_file = tmp_path / "nonexistent.txt"

        # Create mocks
        encoding_detector = Mock(spec=EncodingDetector)
        hash_generator = Mock(spec=HashGenerator)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock()

        # Configure validation to fail
        file_validator.validate_file_exists.return_value = False

        # Initialize service
        service = FileProcessingService(
            encoding_detector=encoding_detector,
            hash_generator=hash_generator,
            file_validator=file_validator,
            rich_output=rich_output,
        )

        # Test process_file
        result = service.process_file(test_file)

        assert result == {}

        # Verify error was logged
        rich_output.error.assert_called_once()

        # Encoding and hash should not be called
        encoding_detector.detect_encoding.assert_not_called()
        hash_generator.generate_hash.assert_not_called()

    def test_process_file_encoding_detection_failure(self, tmp_path: Path) -> None:
        """Test file processing when encoding detection fails."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create mocks
        encoding_detector = Mock(spec=EncodingDetector)
        hash_generator = Mock(spec=HashGenerator)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock()

        # Configure mocks - encoding detection fails
        encoding_detector.detect_encoding.return_value = None
        file_validator.validate_file_exists.return_value = True

        # Initialize service
        service = FileProcessingService(
            encoding_detector=encoding_detector,
            hash_generator=hash_generator,
            file_validator=file_validator,
            rich_output=rich_output,
        )

        # Test process_file
        result = service.process_file(test_file)

        assert result == {}

        # Verify warning was logged
        rich_output.warning.assert_called_once()

        # Hash should not be called if encoding detection fails
        hash_generator.generate_hash.assert_not_called()

    def test_detect_encoding_delegation(self) -> None:
        """Test that detect_encoding method delegates correctly."""
        test_path = Path("/test/path")

        # Create mocks
        encoding_detector = Mock(spec=EncodingDetector)
        hash_generator = Mock(spec=HashGenerator)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock()

        encoding_detector.detect_encoding.return_value = "iso-8859-1"

        # Initialize service
        service = FileProcessingService(
            encoding_detector=encoding_detector,
            hash_generator=hash_generator,
            file_validator=file_validator,
            rich_output=rich_output,
        )

        # Test detect_encoding
        result = service.detect_encoding(test_path)

        assert result == "iso-8859-1"
        encoding_detector.detect_encoding.assert_called_once_with(test_path)

    def test_generate_hash_delegation(self) -> None:
        """Test that generate_hash method delegates correctly."""
        test_path = Path("/test/path")

        # Create mocks
        encoding_detector = Mock(spec=EncodingDetector)
        hash_generator = Mock(spec=HashGenerator)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock()

        hash_generator.generate_hash.return_value = "sha384hash"

        # Initialize service
        service = FileProcessingService(
            encoding_detector=encoding_detector,
            hash_generator=hash_generator,
            file_validator=file_validator,
            rich_output=rich_output,
        )

        # Test generate_hash
        result = service.generate_hash(test_path)

        assert result == "sha384hash"
        hash_generator.generate_hash.assert_called_once_with(test_path)
