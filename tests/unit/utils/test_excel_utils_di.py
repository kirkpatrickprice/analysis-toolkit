"""Tests for Excel export dependency injection implementation."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pandas as pd

from kp_analysis_toolkit.utils.excel_utils import (
    auto_adjust_column_widths,
    clear_excel_export_service,
    export_dataframe_to_excel,
    format_date_columns,
    get_column_letter,
    get_di_state,
    get_excel_export_service,
    sanitize_sheet_name,
    set_excel_export_service,
)

# Constants
MAX_SHEET_NAME_LENGTH = 31


class TestExcelUtilsDI:
    """Test Excel utils with dependency injection."""

    def setup_method(self) -> None:
        """Set up test environment."""
        # Clear any existing service
        clear_excel_export_service()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        # Clear service after each test
        clear_excel_export_service()

    def test_get_excel_export_service_none_by_default(self) -> None:
        """Test that no service is set by default."""
        service = get_excel_export_service()
        assert service is None

    def test_set_and_get_excel_export_service(self) -> None:
        """Test setting and getting Excel export service."""
        mock_service = Mock()
        set_excel_export_service(mock_service)

        service = get_excel_export_service()
        assert service is mock_service

    def test_clear_excel_export_service(self) -> None:
        """Test clearing Excel export service."""
        mock_service = Mock()
        set_excel_export_service(mock_service)

        assert get_excel_export_service() is mock_service

        clear_excel_export_service()
        assert get_excel_export_service() is None

    def test_sanitize_sheet_name_with_di(self) -> None:
        """Test sanitize_sheet_name with DI service."""
        mock_service = Mock()
        mock_service.sheet_name_sanitizer.sanitize_sheet_name.return_value = "DI_Result"
        set_excel_export_service(mock_service)

        result = sanitize_sheet_name("Test Sheet")

        mock_service.sheet_name_sanitizer.sanitize_sheet_name.assert_called_once_with(
            "Test Sheet"
        )
        assert result == "DI_Result"

    def test_sanitize_sheet_name_fallback(self) -> None:
        """Test sanitize_sheet_name fallback when no DI service."""
        result = sanitize_sheet_name("Test/Sheet")

        # Should use direct implementation
        assert result == "Test_Sheet"

    def test_sanitize_sheet_name_di_exception_fallback(self) -> None:
        """Test sanitize_sheet_name falls back when DI service raises exception."""
        mock_service = Mock()
        mock_service.sheet_name_sanitizer.sanitize_sheet_name.side_effect = (
            AttributeError("No method")
        )
        set_excel_export_service(mock_service)

        result = sanitize_sheet_name("Test/Sheet")

        # Should fall back to direct implementation
        assert result == "Test_Sheet"

    def test_get_column_letter_with_di(self) -> None:
        """Test get_column_letter with DI service."""
        mock_service = Mock()
        mock_service.sheet_name_sanitizer.get_column_letter.return_value = "DI_A"
        set_excel_export_service(mock_service)

        result = get_column_letter(1)

        mock_service.sheet_name_sanitizer.get_column_letter.assert_called_once_with(1)
        assert result == "DI_A"

    def test_get_column_letter_fallback(self) -> None:
        """Test get_column_letter fallback when no DI service."""
        result = get_column_letter(1)

        # Should use direct implementation
        assert result == "A"

    def test_export_dataframe_to_excel_with_di(self) -> None:
        """Test export_dataframe_to_excel with DI service."""
        mock_service = Mock()
        set_excel_export_service(mock_service)

        test_data = pd.DataFrame({"Col1": [1, 2]})
        output_path = Path("test.xlsx")

        export_dataframe_to_excel(
            test_data, output_path, "Sheet1", "Title", as_table=True
        )

        mock_service.export_dataframe_to_excel.assert_called_once_with(
            test_data,
            output_path,
            "Sheet1",
            "Title",
            as_table=True,
        )

    def test_export_dataframe_to_excel_fallback(self) -> None:
        """Test export_dataframe_to_excel fallback when no DI service."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"
            test_data = pd.DataFrame({"Col1": [1, 2]})

            export_dataframe_to_excel(test_data, output_path)

            # Should use direct implementation and create file
            assert output_path.exists()

    def test_auto_adjust_column_widths_with_di(self) -> None:
        """Test auto_adjust_column_widths with DI service."""
        mock_service = Mock()
        set_excel_export_service(mock_service)

        mock_worksheet = Mock()
        test_data = pd.DataFrame({"Col1": [1, 2]})

        auto_adjust_column_widths(mock_worksheet, test_data)

        mock_service.column_width_adjuster.auto_adjust_column_widths.assert_called_once_with(
            mock_worksheet,
            test_data,
        )

    def test_format_date_columns_with_di(self) -> None:
        """Test format_date_columns with DI service."""
        mock_service = Mock()
        set_excel_export_service(mock_service)

        mock_worksheet = Mock()
        date_data = pd.DataFrame({"date_col": ["2023-01-01", "2023-01-02"]})

        format_date_columns(mock_worksheet, date_data, 1)

        mock_service.date_formatter.format_date_columns.assert_called_once_with(
            mock_worksheet,
            date_data,
            1,
        )

    def test_get_di_state(self) -> None:
        """Test getting DI state for compatibility."""
        di_state = get_di_state()
        assert di_state is not None
        # Verify it has the expected methods from DIState
        assert hasattr(di_state, "get_service")
        assert hasattr(di_state, "set_service")
        assert hasattr(di_state, "clear_service")
        assert hasattr(di_state, "is_enabled")


class TestExcelUtilsDirectImplementation:
    """Test Excel utils direct implementation without DI."""

    def setup_method(self) -> None:
        """Set up test environment."""
        # Ensure no DI service is set
        clear_excel_export_service()

    def test_sanitize_sheet_name_invalid_chars(self) -> None:
        """Test sanitize_sheet_name removes invalid characters."""
        result = sanitize_sheet_name("Test/Sheet\\With*Invalid[:?]Chars")

        # Should not contain invalid characters
        invalid_chars = "/\\*[:?]"
        for char in invalid_chars:
            assert char not in result

        # Should be within length limit
        assert len(result) <= MAX_SHEET_NAME_LENGTH

    def test_sanitize_sheet_name_empty(self) -> None:
        """Test sanitize_sheet_name handles empty string."""
        result = sanitize_sheet_name("")
        assert result == "Unnamed_Sheet"

    def test_sanitize_sheet_name_long_name(self) -> None:
        """Test sanitize_sheet_name truncates long names."""
        long_name = "This_is_a_very_long_sheet_name_that_exceeds_the_Excel_limit"
        result = sanitize_sheet_name(long_name)

        assert len(result) == MAX_SHEET_NAME_LENGTH
        assert result.endswith("...")

    def test_get_column_letter_single_letters(self) -> None:
        """Test get_column_letter for single letter columns."""
        assert get_column_letter(1) == "A"
        assert get_column_letter(26) == "Z"

    def test_get_column_letter_double_letters(self) -> None:
        """Test get_column_letter for double letter columns."""
        assert get_column_letter(27) == "AA"
        assert get_column_letter(52) == "AZ"
        assert get_column_letter(702) == "ZZ"

    def test_get_column_letter_triple_letters(self) -> None:
        """Test get_column_letter for triple letter columns."""
        assert get_column_letter(703) == "AAA"
        assert get_column_letter(728) == "AAZ"
