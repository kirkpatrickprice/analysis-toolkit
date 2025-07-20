"""Tests for CSV processing service implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pandas as pd
import pytest

from kp_analysis_toolkit.core.services.csv_processing.service import CSVProcessorService
from kp_analysis_toolkit.core.services.file_processing.protocols import FileValidator
from kp_analysis_toolkit.core.services.file_processing.service import (
    FileProcessingService,
)
from kp_analysis_toolkit.core.services.rich_output import RichOutputService

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.csv_processing.protocols import CSVProcessor


# Test constants
EXPECTED_ROWS_BASIC = 2
EXPECTED_ROWS_SINGLE = 1


@pytest.mark.csv_processing
@pytest.mark.core
@pytest.mark.unit
class TestCSVProcessorService:
    """Test the CSVProcessorService class."""

    def test_csv_processor_service_initialization(self) -> None:
        """Test that CSVProcessorService can be initialized."""
        # Create mocks for dependencies
        file_processing: Mock = Mock(spec=FileProcessingService)
        rich_output: Mock = Mock(spec=RichOutputService)

        # Initialize service
        service: CSVProcessorService = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        assert service.file_processing is file_processing
        assert service.rich_output is rich_output

    def test_read_csv_file_success(self, tmp_path: Path) -> None:
        """Test successful CSV file reading."""
        # Create test CSV file
        test_file: Path = tmp_path / "test.csv"
        test_content: str = "Name,Age,City\nJohn,30,NYC\nJane,25,LA\n"
        test_file.write_text(test_content, encoding="utf-8")

        # Create mocks
        file_processing: Mock = Mock(spec=FileProcessingService)
        file_validator: Mock = Mock(spec=FileValidator)
        rich_output: Mock = Mock(spec=RichOutputService)

        # Configure mocks
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = True
        file_processing.detect_encoding.return_value = "utf-8"

        # Initialize service
        service: CSVProcessorService = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test read_csv_file
        result: pd.DataFrame = service.read_csv_file(test_file)

        # Verify DataFrame content
        assert isinstance(result, pd.DataFrame)
        assert len(result) == EXPECTED_ROWS_BASIC
        assert list(result.columns) == ["Name", "Age", "City"]
        assert result.iloc[0]["Name"] == "John"
        assert result.iloc[1]["Name"] == "Jane"

        # Verify method calls
        file_validator.validate_file_exists.assert_called_once_with(test_file)
        file_processing.detect_encoding.assert_called_once_with(test_file)
        rich_output.info.assert_called_with(f"Reading CSV file: {test_file}")
        rich_output.success.assert_called_once()

    def test_read_csv_file_not_found(self, tmp_path: Path) -> None:
        """Test CSV file reading when file doesn't exist."""
        # Non-existent file
        test_file: Path = tmp_path / "nonexistent.csv"

        # Create mocks
        file_processing: Mock = Mock(spec=FileProcessingService)
        file_validator: Mock = Mock(spec=FileValidator)
        rich_output: Mock = Mock(spec=RichOutputService)

        # Configure validation to fail
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = False

        # Initialize service
        service: CSVProcessorService = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test read_csv_file should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="CSV file not found") as exc_info:
            service.read_csv_file(test_file)

        assert str(test_file) in str(exc_info.value)

        # Verify error was logged
        rich_output.error.assert_called_once()

        # Encoding detection should not be called
        file_processing.detect_encoding.assert_not_called()

    def test_read_csv_file_encoding_detection_failure(self, tmp_path: Path) -> None:
        """Test CSV reading when encoding detection fails."""
        # Create test CSV file
        test_file: Path = tmp_path / "test.csv"
        test_content: str = "Name,Age\nJohn,30\n"
        test_file.write_text(test_content, encoding="utf-8")

        # Create mocks
        file_processing: Mock = Mock(spec=FileProcessingService)
        file_validator: Mock = Mock(spec=FileValidator)
        rich_output: Mock = Mock(spec=RichOutputService)

        # Configure mocks - encoding detection fails
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = True
        file_processing.detect_encoding.return_value = None

        # Initialize service
        service: CSVProcessorService = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test read_csv_file with fallback encoding
        result: pd.DataFrame = service.read_csv_file(test_file)

        # Verify DataFrame content
        assert isinstance(result, pd.DataFrame)
        assert len(result) == EXPECTED_ROWS_SINGLE
        assert "Name" in result.columns

        # Verify warning was logged about encoding
        rich_output.warning.assert_called_once()
        assert "Could not detect encoding" in rich_output.warning.call_args[0][0]

    def test_read_csv_file_empty_data_error(self, tmp_path: Path) -> None:
        """Test CSV reading with empty CSV file."""
        # Create empty CSV file
        test_file: Path = tmp_path / "empty.csv"
        test_file.write_text("", encoding="utf-8")

        # Create mocks
        file_processing: Mock = Mock(spec=FileProcessingService)
        file_validator: Mock = Mock(spec=FileValidator)
        rich_output: Mock = Mock(spec=RichOutputService)

        # Configure mocks
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = True
        file_processing.detect_encoding.return_value = "utf-8"

        # Initialize service
        service: CSVProcessorService = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test read_csv_file should raise ValueError
        with pytest.raises(ValueError, match="CSV file is empty") as exc_info:
            service.read_csv_file(test_file)

        assert str(test_file) in str(exc_info.value)
        rich_output.error.assert_called_once()

    def test_read_csv_file_parser_error(self, tmp_path: Path) -> None:
        """Test CSV reading with malformed CSV data."""
        # Create malformed CSV file - mismatched field count will cause ParserError
        test_file = tmp_path / "malformed.csv"
        test_content = "Name,Age,City\nJohn,30,NYC\nJane,25\nBob,35,LA,Extra"  # Extra field in last row
        test_file.write_text(test_content, encoding="utf-8")

        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock(spec=RichOutputService)

        # Configure mocks
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = True
        file_processing.detect_encoding.return_value = "utf-8"

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test read_csv_file should raise ValueError
        with pytest.raises(ValueError, match="Failed to parse CSV file") as exc_info:
            service.read_csv_file(test_file)

        assert str(test_file) in str(exc_info.value)
        rich_output.error.assert_called_once()

    def test_validate_required_columns_success(self) -> None:
        """Test successful column validation."""
        # Create test DataFrame
        data = {"Name": ["John", "Jane"], "Age": [30, 25], "City": ["NYC", "LA"]}
        test_dataframe = pd.DataFrame(data)

        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        rich_output = Mock(spec=RichOutputService)

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test validate_required_columns - should pass
        required_columns = ["Name", "Age"]
        service.validate_required_columns(test_dataframe, required_columns)

        # Verify success message was logged
        rich_output.success.assert_called_once()
        assert "Validated required columns" in rich_output.success.call_args[0][0]

    def test_validate_required_columns_missing(self) -> None:
        """Test column validation with missing columns."""
        # Create test DataFrame
        data = {"Name": ["John", "Jane"], "Age": [30, 25]}
        test_dataframe = pd.DataFrame(data)

        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        rich_output = Mock(spec=RichOutputService)

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test validate_required_columns with missing column
        required_columns = ["Name", "Age", "City"]
        with pytest.raises(KeyError, match="Missing required columns") as exc_info:
            service.validate_required_columns(test_dataframe, required_columns)

        # Verify error details
        error_msg = str(exc_info.value)
        assert "City" in error_msg
        assert "Available columns" in error_msg

        # Verify error was logged
        rich_output.error.assert_called_once()

    def test_validate_required_columns_empty_list(self) -> None:
        """Test column validation with empty required columns list."""
        # Create test DataFrame
        data = {"Name": ["John", "Jane"]}
        test_dataframe = pd.DataFrame(data)

        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        rich_output = Mock(spec=RichOutputService)

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test validate_required_columns with empty list - should pass
        service.validate_required_columns(test_dataframe, [])

        # Verify debug message was logged
        rich_output.debug.assert_called_once()
        assert "No required columns to validate" in rich_output.debug.call_args[0][0]

    def test_process_csv_with_validation_success(self, tmp_path: Path) -> None:
        """Test complete CSV processing pipeline success."""
        # Create test CSV file
        test_file = tmp_path / "test.csv"
        test_content = "Name,Age,City\nJohn,30,NYC\nJane,25,LA\n"
        test_file.write_text(test_content, encoding="utf-8")

        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock(spec=RichOutputService)

        # Configure mocks
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = True
        file_processing.detect_encoding.return_value = "utf-8"

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test process_csv_with_validation
        required_columns = ["Name", "Age"]
        result = service.process_csv_with_validation(test_file, required_columns)

        # Verify DataFrame content
        assert isinstance(result, pd.DataFrame)
        assert len(result) == EXPECTED_ROWS_BASIC
        assert list(result.columns) == ["Name", "Age", "City"]

        # Verify completion message was logged
        rich_output.info.assert_called()
        assert "CSV processing complete" in str(rich_output.info.call_args_list)

    def test_process_csv_with_validation_file_not_found(self, tmp_path: Path) -> None:
        """Test complete CSV processing pipeline with file not found."""
        # Non-existent file
        test_file = tmp_path / "nonexistent.csv"

        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock(spec=RichOutputService)

        # Configure validation to fail
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = False

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test process_csv_with_validation should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            service.process_csv_with_validation(test_file, ["Name"])

    def test_process_csv_with_validation_missing_columns(self, tmp_path: Path) -> None:
        """Test complete CSV processing pipeline with missing columns."""
        # Create test CSV file
        test_file = tmp_path / "test.csv"
        test_content = "Name,Age\nJohn,30\nJane,25\n"
        test_file.write_text(test_content, encoding="utf-8")

        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock(spec=RichOutputService)

        # Configure mocks
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = True
        file_processing.detect_encoding.return_value = "utf-8"

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test process_csv_with_validation with missing required column
        required_columns = ["Name", "Age", "City"]
        with pytest.raises(KeyError):
            service.process_csv_with_validation(test_file, required_columns)

    def test_service_implements_protocol(self) -> None:
        """Test that CSVProcessorService implements the CSVProcessor protocol."""
        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        rich_output = Mock(spec=RichOutputService)

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Verify service implements protocol methods
        assert hasattr(service, "read_csv_file")
        assert hasattr(service, "validate_required_columns")
        assert hasattr(service, "process_csv_with_validation")

        # Test that service can be used as protocol type
        csv_processor: CSVProcessor = service
        assert csv_processor is service

    def test_unicode_decode_error_handling(self, tmp_path: Path) -> None:
        """Test handling of Unicode decode errors."""
        # Create binary file that will cause encoding issues
        test_file = tmp_path / "bad_encoding.csv"
        # Write some binary data that's not valid UTF-8
        test_file.write_bytes(b"\xff\xfe\x00\x00Name,Age\nJohn,30")

        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock(spec=RichOutputService)

        # Configure mocks
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = True
        file_processing.detect_encoding.return_value = "utf-8"  # Wrong encoding

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Test read_csv_file should raise ValueError for encoding error
        with pytest.raises(
            ValueError,
            match="Encoding error reading CSV file",
        ) as exc_info:
            service.read_csv_file(test_file)

        assert str(test_file) in str(exc_info.value)
        rich_output.error.assert_called_once()

    def test_os_error_handling(self, tmp_path: Path) -> None:
        """Test handling of OS/permission errors."""
        # This test is more conceptual since we can't easily simulate
        # permission errors in a test environment, but we test the error path
        test_file = tmp_path / "test.csv"
        test_content = "Name,Age\nJohn,30\n"
        test_file.write_text(test_content, encoding="utf-8")

        # Create mocks
        file_processing = Mock(spec=FileProcessingService)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock(spec=RichOutputService)

        # Configure mocks
        file_processing.file_validator = file_validator
        file_validator.validate_file_exists.return_value = True
        file_processing.detect_encoding.return_value = "utf-8"

        # Initialize service
        service = CSVProcessorService(
            file_processing=file_processing,
            rich_output=rich_output,
        )

        # Mock pandas to raise OSError
        original_read_csv = pd.read_csv

        def mock_read_csv(*_: object, **__: object) -> None:
            permission_error_msg = "Permission denied"
            raise OSError(permission_error_msg)

        pd.read_csv = mock_read_csv

        try:
            # Test read_csv_file should raise OSError
            with pytest.raises(
                OSError,
                match="File access error reading CSV",
            ) as exc_info:
                service.read_csv_file(test_file)

            assert str(test_file) in str(exc_info.value)
            rich_output.error.assert_called_once()
        finally:
            # Restore original function
            pd.read_csv = original_read_csv
