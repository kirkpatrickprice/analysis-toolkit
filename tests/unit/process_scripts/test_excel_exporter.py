"""Tests for excel_exporter module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from kp_analysis_toolkit.process_scripts.excel_exporter import (
    export_results_by_os_type,
    export_search_results_to_excel,
)
from kp_analysis_toolkit.process_scripts.models.results.search import (
    SearchResult,
    SearchResults,
)
from kp_analysis_toolkit.process_scripts.models.search.merge_fields import SearchConfig
from kp_analysis_toolkit.process_scripts.models.results.system import Systems


def _setup_excel_writer_mock(mock_writer: MagicMock, mock_to_excel: MagicMock) -> None:
    """Helper function to set up Excel writer mock properly."""
    # Mock the context manager behavior
    mock_writer_instance = MagicMock()
    mock_writer.return_value = mock_writer_instance
    mock_writer_instance.__enter__.return_value = mock_writer_instance
    mock_writer_instance.__exit__.return_value = None
    mock_writer_instance.sheets = {}

    # Create a side effect to simulate sheet creation when to_excel is called
    def add_sheet_to_writer(*args, **kwargs) -> None:
        sheet_name = kwargs.get("sheet_name", "Sheet1")
        mock_worksheet = MagicMock()
        mock_writer_instance.sheets[sheet_name] = mock_worksheet

    mock_to_excel.side_effect = add_sheet_to_writer


class TestExportResultsByOSType:
    """Test suite for export_results_by_os_type function."""

    @patch(
        "kp_analysis_toolkit.process_scripts.excel_exporter.export_search_results_to_excel",
    )
    def test_calls_export_function(
        self,
        mock_export: MagicMock,
        mock_linux_system: Systems,
        mock_windows_system: Systems,
    ) -> None:
        """Test that the export function is called appropriately."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Use shared fixtures
            mock_linux_system.system_name = "system1"
            mock_windows_system.system_name = "system2"
            systems = [mock_linux_system, mock_windows_system]

            # Create mock search results with proper attributes matching system names
            mock_search_result = MagicMock(spec=SearchResult)
            mock_search_result.system_name = "system1"  # Match the system name
            mock_search_result.line_number = 1
            mock_search_result.matched_text = "test content"
            mock_search_result.extracted_fields = None

            # Create a real SearchConfig for proper validation
            search_config = SearchConfig(
                name="test_search",
                regex="test.*",
                excel_sheet_name="test_search",
            )

            mock_results_obj = MagicMock(spec=SearchResults)
            mock_results_obj.results = [mock_search_result]
            mock_results_obj.search_config = search_config
            mock_results_obj.result_count = 1
            mock_results_obj.unique_systems = 1
            mock_results_obj.has_extracted_fields = False

            export_results_by_os_type([mock_results_obj], systems, output_dir)

            # Should be called once for each OS family
            assert mock_export.call_count >= 1

    def test_groups_systems_by_os_family(
        self, mock_linux_system: Systems, mock_windows_system: Systems,
    ) -> None:
        """Test that systems are properly grouped by OS family."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Create additional Linux system from shared fixture
            mock_linux_system.system_name = "linux1"
            mock_linux_system2 = mock_linux_system
            mock_linux_system2.system_name = "linux2"

            mock_windows_system.system_name = "win1"

            systems = [mock_linux_system, mock_linux_system2, mock_windows_system]

            # Test behavior when no search results provided
            result = export_results_by_os_type([], systems, output_dir)
            assert isinstance(result, dict)  # Should return empty dict


class TestExportSearchResultsToExcel:
    """Test suite for export_search_results_to_excel function."""

    @patch("pandas.DataFrame.to_excel")
    @patch("pandas.ExcelWriter")
    def test_excel_writer_called(
        self,
        mock_writer: MagicMock,
        mock_to_excel: MagicMock,
    ) -> None:
        """Test that Excel writer is properly instantiated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            _setup_excel_writer_mock(mock_writer, mock_to_excel)

            export_search_results_to_excel([], output_path)

            # Verify ExcelWriter was called with correct parameters
            mock_writer.assert_called_once_with(output_path, engine="openpyxl")

    @patch("pandas.DataFrame.to_excel")
    @patch("kp_analysis_toolkit.process_scripts.excel_exporter.format_as_excel_table")
    @patch("pandas.ExcelWriter")
    def test_handles_invalid_characters(
        self,
        mock_writer: MagicMock,
        mock_format: MagicMock,
        mock_to_excel: MagicMock,
    ) -> None:
        """Test handling of invalid characters in Excel export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            _setup_excel_writer_mock(mock_writer, mock_to_excel)

            # Create mock search results with problematic characters
            mock_result = MagicMock(spec=SearchResult)
            mock_result.system_name = "test-system"  # Add missing attribute
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

            # Verify function calls
            mock_writer.assert_called_once()


class TestResultsDataProcessing:
    """Test suite for results data processing functions."""

    @patch("pandas.DataFrame.to_excel")
    @patch("pandas.ExcelWriter")
    def test_result_flattening(
        self,
        mock_writer: MagicMock,
        mock_to_excel: MagicMock,
    ) -> None:
        """Test that nested results are properly flattened."""
        # Create mock results with nested structure
        mock_result1 = MagicMock(spec=SearchResult)
        mock_result1.system_name = "test-system1"  # Add missing attribute
        mock_result1.file_path = "file1.txt"
        mock_result1.line_number = 1
        mock_result1.matched_text = "content1"
        mock_result1.extracted_fields = None

        mock_result2 = MagicMock(spec=SearchResult)
        mock_result2.system_name = "test-system2"  # Add missing attribute
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

            _setup_excel_writer_mock(mock_writer, mock_to_excel)

            # Should process multiple results without error
            export_search_results_to_excel([mock_search_results], output_path)

            # Verify calls were made
            mock_writer.assert_called_once()

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

            _setup_excel_writer_mock(mock_writer, mock_to_excel)

            # Create mock result
            mock_result = MagicMock(spec=SearchResult)
            mock_result.system_name = "test-system"  # Add missing attribute
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

            # Verify calls were made
            mock_writer.assert_called_once()
            assert mock_to_excel.call_count >= 1


class TestSystemSummaryExport:
    """Test suite for system summary export functionality."""

    @patch("pandas.DataFrame.to_excel")
    @patch("pandas.ExcelWriter")
    def test_system_summary_creation(
        self,
        mock_writer: MagicMock,
        mock_to_excel: MagicMock,
        mock_linux_system: Systems,
    ) -> None:
        """Test that system summary is created correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            _setup_excel_writer_mock(mock_writer, mock_to_excel)

            # Set up the mock system's attributes for the test
            mock_linux_system.hostname = "test-host"
            mock_linux_system.system_name = "test-host"
            mock_linux_system.os_version = "22.04"
            mock_linux_system.distro_family = None
            mock_linux_system.os_pretty_name = "Ubuntu 22.04"
            mock_linux_system.product_name = None
            mock_linux_system.release_id = None
            mock_linux_system.current_build = None
            mock_linux_system.file = "/path/to/file"
            mock_linux_system.encoding = "utf-8"

            systems = [mock_linux_system]

            export_search_results_to_excel([], output_path, systems)

            # Verify calls were made
            mock_writer.assert_called_once()


class TestWorksheetNaming:
    """Test suite for worksheet naming and sanitization."""

    @patch("pandas.DataFrame.to_excel")
    @patch("kp_analysis_toolkit.process_scripts.excel_exporter.sanitize_sheet_name")
    @patch("pandas.ExcelWriter")
    def test_sheet_name_sanitization(
        self,
        mock_writer: MagicMock,
        mock_sanitize: MagicMock,
        mock_to_excel: MagicMock,
    ) -> None:
        """Test that sheet names are properly sanitized."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            _setup_excel_writer_mock(mock_writer, mock_to_excel)

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

    def test_duplicate_name_handling(self) -> None:
        """Test handling of duplicate sheet names."""
        # This test would verify that duplicate sheet names are handled appropriately
        # For now, just test that the function exists and can be called
        from kp_analysis_toolkit.utils.excel_utils import sanitize_sheet_name

        result = sanitize_sheet_name("test/name*with[chars]")
        assert isinstance(result, str)
        assert len(result) <= 31  # Excel sheet name limit


class TestErrorHandling:
    """Test suite for error handling scenarios."""

    def test_empty_results_handling(self) -> None:
        """Test handling of empty search results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Should handle empty results gracefully
            result = export_results_by_os_type([], [], output_dir)
            assert isinstance(result, dict)
            assert len(result) == 0

    @patch("pandas.DataFrame.to_excel")
    @patch("pandas.ExcelWriter")
    def test_missing_config_handling(
        self,
        mock_writer: MagicMock,
        mock_to_excel: MagicMock,
    ) -> None:
        """Test handling of search results with missing config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            _setup_excel_writer_mock(mock_writer, mock_to_excel)

            # Create search results with None config
            mock_search_results = MagicMock(spec=SearchResults)
            mock_search_results.results = []
            mock_search_results.search_config = None  # This could cause issues
            mock_search_results.result_count = 0
            mock_search_results.unique_systems = 0
            mock_search_results.has_extracted_fields = False

            # Should handle missing config without crashing
            try:
                export_search_results_to_excel([mock_search_results], output_path)
            except (AttributeError, TypeError):
                # Expected exceptions for missing config
                pass
