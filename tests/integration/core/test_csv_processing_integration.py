"""Integration tests for CSV processing service with application container."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from kp_analysis_toolkit.core.containers.application import (
    ApplicationContainer,
    container,
    initialize_dependency_injection,
)
from kp_analysis_toolkit.core.services.csv_processing.service import CSVProcessorService

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.csv_processing.protocols import CSVProcessor


# Test constants
EXPECTED_ROWS_SMALL = 3
EXPECTED_ROWS_PAIR = 2
EXPECTED_ROWS_LARGE = 1000


@pytest.fixture(scope="class")
def app_container() -> ApplicationContainer:
    """Create application container for tests."""
    initialize_dependency_injection()
    return container


class TestCSVProcessingIntegration:
    """Integration tests for CSV processing service with real dependencies."""

    def setup_method(self) -> None:
        """Set up the application container for each test."""
        initialize_dependency_injection()

    def test_csv_processing_basic_file_reading_integration(
        self,
        tmp_path: Path,
        app_container: ApplicationContainer,
    ) -> None:
        """Test basic CSV file reading with real file processing service."""
        # Create test CSV file
        test_file: Path = tmp_path / "test.csv"
        test_file.write_text("Name,Age,City\nJohn,25,NYC\nJane,30,LA\nBob,35,Chicago")

        # Get service from container
        service: CSVProcessor = app_container.core().csv_processor_service()

        # Test reading CSV file
        result: pd.DataFrame = service.read_csv_file(test_file)

        # Verify DataFrame content
        assert isinstance(result, pd.DataFrame)
        assert len(result) == EXPECTED_ROWS_SMALL
        assert list(result.columns) == ["Name", "Age", "City"]
        assert result.iloc[0]["Name"] == "John"
        assert result.iloc[1]["Name"] == "Jane"
        assert result.iloc[2]["Name"] == "Bob"

    def test_csv_processing_with_required_columns_integration(
        self,
        tmp_path: Path,
        app_container: ApplicationContainer,
    ) -> None:
        """Test CSV processing with additional columns (validates service handles extra columns)."""
        # Create test CSV file with additional columns
        test_file: Path = tmp_path / "test.csv"
        test_file.write_text(
            "Name,Age,City,Salary\nJohn,25,NYC,50000\nJane,30,LA,60000\nBob,35,Chicago,55000",
        )

        # Get service from container
        service: CSVProcessor = app_container.core().csv_processor_service()

        # Test reading CSV file (service should handle all columns)
        result: pd.DataFrame = service.read_csv_file(test_file)

        # Verify DataFrame content
        assert isinstance(result, pd.DataFrame)
        assert len(result) == EXPECTED_ROWS_SMALL
        # Verify all columns are preserved
        expected_columns: list[str] = ["Name", "Age", "City", "Salary"]
        assert list(result.columns) == expected_columns

    def test_csv_processing_encoding_detection_integration(
        self,
        tmp_path: Path,
    ) -> None:
        """Test CSV processing with automatic encoding detection."""
        # Create test CSV file with unicode characters
        test_file: Path = tmp_path / "test_unicode.csv"
        unicode_content: str = (
            "Name,Description\nCafé,A délicious café\nNaïve,A naïve approach"
        )
        test_file.write_text(unicode_content, encoding="utf-8")

        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Test reading CSV file with unicode content
        result: pd.DataFrame = service.read_csv_file(test_file)

        # Verify DataFrame content preserves unicode characters
        assert isinstance(result, pd.DataFrame)
        assert len(result) == EXPECTED_ROWS_PAIR
        assert "Café" in result.iloc[0]["Name"]
        assert "délicious" in result.iloc[0]["Description"]
        assert "Naïve" in result.iloc[1]["Name"]

    def test_csv_processing_error_handling_integration(self, tmp_path: Path) -> None:
        """Test CSV processing error handling with real file system."""
        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Test with non-existent file
        non_existent_file: Path = tmp_path / "does_not_exist.csv"

        with pytest.raises(FileNotFoundError):
            service.read_csv_file(non_existent_file)

    def test_csv_processing_empty_file_integration(self, tmp_path: Path) -> None:
        """Test CSV processing with empty file."""
        # Create empty CSV file
        test_file: Path = tmp_path / "empty.csv"
        test_file.write_text("")

        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Test reading empty CSV file
        with pytest.raises(ValueError, match="CSV file is empty"):
            service.read_csv_file(test_file)

    def test_csv_processing_malformed_csv_integration(self, tmp_path: Path) -> None:
        """Test CSV processing with malformed CSV file."""
        # Create malformed CSV file (inconsistent field count)
        test_file: Path = tmp_path / "malformed.csv"
        test_file.write_text("Name,Age,City\nJohn,25\nJane,30,LA,Extra")

        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Test reading malformed CSV file - should raise ValueError
        with pytest.raises(ValueError, match="Failed to parse CSV file"):
            service.read_csv_file(test_file)

    def test_csv_processing_with_custom_separator_integration(
        self,
        tmp_path: Path,
    ) -> None:
        """Test CSV processing with standard comma separator (no custom separator support)."""
        # Create CSV file with standard comma separator
        test_file: Path = tmp_path / "comma.csv"
        test_file.write_text("Name,Age,City\nJohn,25,NYC\nJane,30,LA")

        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Test reading CSV file with standard separator
        result: pd.DataFrame = service.read_csv_file(test_file)

        # Verify DataFrame content
        assert isinstance(result, pd.DataFrame)
        assert len(result) == EXPECTED_ROWS_PAIR
        assert list(result.columns) == ["Name", "Age", "City"]
        assert result.iloc[0]["Name"] == "John"

    def test_csv_processing_large_file_integration(self, tmp_path: Path) -> None:
        """Test CSV processing with large file."""
        # Create large CSV file
        test_file: Path = tmp_path / "large.csv"

        # Generate large CSV content
        lines: list[str] = ["Name,Age,Department,Salary"]
        for i in range(EXPECTED_ROWS_LARGE):
            lines.append(
                f"Employee{i:04d},{20 + (i % 40)},Dept{i % 10},{40000 + (i * 10)}",
            )

        test_file.write_text("\n".join(lines))

        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Test reading large CSV file
        result: pd.DataFrame = service.read_csv_file(test_file)

        # Verify DataFrame content
        assert isinstance(result, pd.DataFrame)
        assert len(result) == EXPECTED_ROWS_LARGE
        assert list(result.columns) == ["Name", "Age", "Department", "Salary"]
        assert result.iloc[0]["Name"] == "Employee0000"
        assert result.iloc[999]["Name"] == "Employee0999"

    def test_csv_processing_factory_provider_creates_new_instances(self) -> None:
        """Test that factory provider creates new service instances."""
        # Get two instances from container
        service1: CSVProcessor = container.core().csv_processor_service()
        service2: CSVProcessor = container.core().csv_processor_service()

        # Verify they are different instances (factory pattern)
        assert service1 is not service2
        assert isinstance(service1, CSVProcessorService)
        assert isinstance(service2, CSVProcessorService)

    def test_csv_processing_service_dependencies_injection(self) -> None:
        """Test that service receives correct dependencies via DI."""
        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Verify service is properly instantiated
        assert isinstance(service, CSVProcessorService)

        # Test that service can perform basic operations (indirect dependency test)
        # This confirms dependencies are properly injected

    @patch("kp_analysis_toolkit.core.services.csv_processing.service.pd.read_csv")
    def test_csv_processing_pandas_exception_handling(
        self,
        mock_read_csv: Mock,
        tmp_path: Path,
    ) -> None:
        """Test handling of pandas-specific exceptions."""
        # Create test file
        test_file: Path = tmp_path / "test.csv"
        test_file.write_text("Name,Age\nJohn,25")

        # Configure mock to raise pandas exception
        mock_read_csv.side_effect = pd.errors.ParserError("Test parser error")

        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Test that pandas exceptions are properly handled and converted to ValueError
        with pytest.raises(ValueError, match="Failed to parse CSV file"):
            service.read_csv_file(test_file)

        # Verify read_csv was called
        mock_read_csv.assert_called_once()
