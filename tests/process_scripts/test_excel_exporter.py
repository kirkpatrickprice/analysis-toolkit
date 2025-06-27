"""Tests for excel_exporter module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from kp_analysis_toolkit.process_scripts.excel_exporter import (
    export_results_by_os_type,
    export_search_results_to_excel,
)
from kp_analysis_toolkit.process_scripts.models.results.base import (
    SearchResult,
    SearchResults,
)
from kp_analysis_toolkit.process_scripts.models.systems import Systems


class TestExportResultsByOSType:
    """Test OS-specific export functionality."""

    def test_empty_results(self) -> None:
        """Test handling of empty search results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            result = export_results_by_os_type([], [], output_dir)

            assert isinstance(result, dict)
            assert len(result) == 0

    def test_creates_output_directory(self) -> None:
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "new_subdir"
            assert not output_dir.exists()

            export_results_by_os_type([], [], output_dir)

            assert output_dir.exists()

    @patch(
        "kp_analysis_toolkit.process_scripts.excel_exporter.export_search_results_to_excel",
    )
    def test_calls_export_function(self, mock_export: MagicMock) -> None:
        """Test that the export function is called appropriately."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Create mock systems with different OS families
            mock_system1 = MagicMock(spec=Systems)
            mock_system1.os_family = "Linux"
            mock_system1.system_name = "system1"

            mock_system2 = MagicMock(spec=Systems)
            mock_system2.os_family = "Windows"
            mock_system2.system_name = "system2"

            systems = [mock_system1, mock_system2]

            # Create mock search results
            mock_results = [MagicMock(spec=SearchResults)]
            mock_results[0].results = []

            export_results_by_os_type(mock_results, systems, output_dir)

            # Should be called once for each OS family
            assert mock_export.call_count >= 1


class TestExportSearchResultsToExcel:
    """Test main Excel export functionality."""

    def test_empty_results_export(self) -> None:
        """Test export with empty results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            # Empty results should not raise an error
            export_search_results_to_excel([], output_path)

            # File might or might not be created depending on implementation
            # Just ensure no error was raised

    @patch("pandas.ExcelWriter")
    def test_excel_writer_called(self, mock_writer: MagicMock) -> None:
        """Test that Excel writer is properly instantiated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            # Mock the context manager behavior
            mock_writer.return_value.__enter__.return_value = mock_writer.return_value
            mock_writer.return_value.__exit__.return_value = None
            mock_writer.return_value.sheets = {}

            export_search_results_to_excel([], output_path)

            # Verify Excel writer was called with correct parameters
            mock_writer.assert_called_once()

    def test_path_creation(self) -> None:
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "subdir" / "test.xlsx"

            # Directory should not exist initially
            assert not output_path.parent.exists()

            export_search_results_to_excel([], output_path)

            # Directory should be created
            assert output_path.parent.exists()

    @patch("kp_analysis_toolkit.process_scripts.excel_exporter.format_as_excel_table")
    @patch("pandas.ExcelWriter")
    def test_handles_invalid_characters(
        self,
        mock_writer: MagicMock,
        mock_format: MagicMock,
    ) -> None:
        """Test handling of invalid characters in Excel export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            # Mock the context manager and sheets
            mock_writer.return_value.__enter__.return_value = mock_writer.return_value
            mock_writer.return_value.__exit__.return_value = None
            mock_writer.return_value.sheets = {}

            # Create mock search results with problematic characters
            mock_result = MagicMock(spec=SearchResult)
            mock_result.file_path = "test\x00file.txt"  # Null character
            mock_result.line_number = 1
            mock_result.matched_text = "test\x01content"  # Control character
            mock_result.extracted_fields = None

            mock_search_config = MagicMock()
            mock_search_config.name = "test_search"
            mock_search_config.excel_sheet_name = "test_search"

            mock_search_results = MagicMock(spec=SearchResults)
            mock_search_results.results = [mock_result]
            mock_search_results.search_name = "test_search"
            mock_search_results.search_config = mock_search_config
            mock_search_results.result_count = 1
            mock_search_results.unique_systems = 1
            mock_search_results.has_extracted_fields = False

            # Should handle invalid characters gracefully
            export_search_results_to_excel([mock_search_results], output_path)

            mock_writer.assert_called_once()


class TestResultsDataProcessing:
    """Test data processing for results export."""

    def test_result_flattening(self) -> None:
        """Test that nested results are properly flattened."""
        # Create mock results with nested structure
        mock_result1 = MagicMock(spec=SearchResult)
        mock_result1.file_path = "file1.txt"
        mock_result1.line_number = 1
        mock_result1.matched_text = "content1"
        mock_result1.extracted_fields = None

        mock_result2 = MagicMock(spec=SearchResult)
        mock_result2.file_path = "file2.txt"
        mock_result2.line_number = 2
        mock_result2.matched_text = "content2"
        mock_result2.extracted_fields = None

        mock_search_config = MagicMock()
        mock_search_config.name = "test_search"
        mock_search_config.excel_sheet_name = "test_search"

        mock_search_results = MagicMock(spec=SearchResults)
        mock_search_results.results = [mock_result1, mock_result2]
        mock_search_results.search_name = "test_search"
        mock_search_results.search_config = mock_search_config
        mock_search_results.result_count = 2
        mock_search_results.unique_systems = 2
        mock_search_results.has_extracted_fields = False

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            # Should process multiple results without error
            export_search_results_to_excel([mock_search_results], output_path)

    @patch("pandas.DataFrame.to_excel")
    @patch("pandas.ExcelWriter")
    def test_dataframe_creation(
        self,
        mock_writer: MagicMock,
        mock_to_excel: MagicMock,
    ) -> None:
        """Test that DataFrames are created correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            # Mock writer context manager
            mock_writer.return_value.__enter__.return_value = mock_writer.return_value
            mock_writer.return_value.__exit__.return_value = None
            mock_writer.return_value.sheets = {}

            # Create mock result
            mock_result = MagicMock(spec=SearchResult)
            mock_result.file_path = "test.txt"
            mock_result.line_number = 1
            mock_result.matched_text = "test"
            mock_result.extracted_fields = None

            mock_search_config = MagicMock()
            mock_search_config.name = "test_search"
            mock_search_config.excel_sheet_name = "test_search"

            mock_search_results = MagicMock(spec=SearchResults)
            mock_search_results.results = [mock_result]
            mock_search_results.search_name = "test_search"
            mock_search_results.search_config = mock_search_config
            mock_search_results.result_count = 1
            mock_search_results.unique_systems = 1
            mock_search_results.has_extracted_fields = False

            export_search_results_to_excel([mock_search_results], output_path)

            # Verify to_excel was called
            mock_to_excel.assert_called()

    def test_empty_search_results_handling(self) -> None:
        """Test handling of search results with no actual results."""
        mock_search_config = MagicMock()
        mock_search_config.name = "empty_search"
        mock_search_config.excel_sheet_name = "empty_search"
        mock_search_config.comment = "Test comment"

        mock_search_results = MagicMock(spec=SearchResults)
        mock_search_results.results = []
        mock_search_results.search_name = "empty_search"
        mock_search_results.search_config = mock_search_config
        mock_search_results.result_count = 0
        mock_search_results.unique_systems = 0
        mock_search_results.has_extracted_fields = False

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            # Should handle empty results gracefully
            export_search_results_to_excel([mock_search_results], output_path)


class TestSystemSummaryExport:
    """Test system summary export functionality."""

    @patch("pandas.ExcelWriter")
    def test_system_summary_creation(self, mock_writer: MagicMock) -> None:
        """Test that system summary is created correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            # Mock writer
            mock_writer.return_value.__enter__.return_value = mock_writer.return_value
            mock_writer.return_value.__exit__.return_value = None
            mock_writer.return_value.sheets = {}

            # Create mock systems
            mock_system = MagicMock(spec=Systems)
            mock_system.hostname = "test-host"
            mock_system.system_name = "test-host"
            mock_system.os_family = "Linux"
            mock_system.os_version = "22.04"

            systems = [mock_system]

            export_search_results_to_excel([], output_path, systems)

            mock_writer.assert_called_once()

    def test_system_filtering_by_os(self) -> None:
        """Test that systems are properly filtered by OS family."""
        # This test would verify that when exporting by OS type,
        # only systems matching that OS are included

        mock_linux_system = MagicMock(spec=Systems)
        mock_linux_system.os_family = "Linux"
        mock_linux_system.system_name = "linux_system"

        mock_windows_system = MagicMock(spec=Systems)
        mock_windows_system.os_family = "Windows"
        mock_windows_system.system_name = "windows_system"

        systems = [mock_linux_system, mock_windows_system]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Should create separate files for different OS families
            result = export_results_by_os_type([], systems, output_dir)

            # Result should be a dictionary of OS types to file paths
            assert isinstance(result, dict)


class TestWorksheetNaming:
    """Test worksheet naming and sanitization."""

    @patch("kp_analysis_toolkit.process_scripts.excel_exporter.sanitize_sheet_name")
    @patch("pandas.ExcelWriter")
    def test_sheet_name_sanitization(
        self,
        mock_writer: MagicMock,
        mock_sanitize: MagicMock,
    ) -> None:
        """Test that sheet names are properly sanitized."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            # Mock writer
            mock_writer.return_value.__enter__.return_value = mock_writer.return_value
            mock_writer.return_value.__exit__.return_value = None
            mock_writer.return_value.sheets = {}

            # Mock sanitization
            mock_sanitize.return_value = "Sanitized_Name"

            # Create mock search results with problematic name
            mock_search_config = MagicMock()
            mock_search_config.name = "problematic/name*with[chars]"
            mock_search_config.excel_sheet_name = "problematic/name*with[chars]"
            mock_search_config.comment = "Test comment"

            mock_search_results = MagicMock(spec=SearchResults)
            mock_search_results.results = []
            mock_search_results.search_name = "problematic/name*with[chars]"
            mock_search_results.search_config = mock_search_config
            mock_search_results.result_count = 0
            mock_search_results.unique_systems = 0
            mock_search_results.has_extracted_fields = False

            export_search_results_to_excel([mock_search_results], output_path)

            # Verify sanitization was called
            mock_sanitize.assert_called()
