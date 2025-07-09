"""Tests for excel_utils module."""

import tempfile
from pathlib import Path

import pandas as pd

from kp_analysis_toolkit.utils.excel_utils import (
    export_dataframe_to_excel,
    get_column_letter,
    sanitize_sheet_name,
)

# Constants
MAX_SHEET_NAME_LENGTH = 31


class TestSanitizeSheetName:
    """Test sheet name sanitization."""

    def test_normal_name(self) -> None:
        """Test normal sheet name is preserved."""
        result = sanitize_sheet_name("Test Sheet")
        assert result == "Test_Sheet"

    def test_invalid_characters_removed(self) -> None:
        """Test invalid characters are replaced with underscores."""
        result = sanitize_sheet_name("Test/Sheet\\With*Invalid[:?]Chars")
        # Check that invalid characters are replaced
        assert "/" not in result
        assert "\\" not in result
        assert "*" not in result
        assert "[" not in result
        assert ":" not in result
        assert "?" not in result
        assert "]" not in result
        # Check that result is within length limit
        assert len(result) <= MAX_SHEET_NAME_LENGTH

    def test_empty_name_default(self) -> None:
        """Test empty name gets default value."""
        result = sanitize_sheet_name("")
        assert result == "Unnamed_Sheet"

    def test_length_limit_enforced(self) -> None:
        """Test sheet name is truncated to 31 characters."""
        long_name = "This_is_a_very_long_sheet_name_that_exceeds_the_limit"
        result = sanitize_sheet_name(long_name)
        assert len(result) == MAX_SHEET_NAME_LENGTH
        assert result.endswith("...")


class TestGetColumnLetter:
    """Test column letter conversion."""

    def test_single_letters(self) -> None:
        """Test single letter columns."""
        assert get_column_letter(1) == "A"
        assert get_column_letter(26) == "Z"

    def test_double_letters(self) -> None:
        """Test double letter columns."""
        assert get_column_letter(27) == "AA"
        assert get_column_letter(52) == "AZ"


class TestExportDataframeToExcel:
    """Test DataFrame export to Excel."""

    def test_basic_export(self) -> None:
        """Test basic export functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.xlsx"

            test_data = pd.DataFrame(
                {
                    "Column1": [1, 2, 3],
                    "Column2": ["A", "B", "C"],
                },
            )

            export_dataframe_to_excel(test_data, output_path)

            # Verify file was created
            assert output_path.exists()

            # Just verify basic structure since exact format may vary
            result_data = pd.read_excel(output_path)
            assert not result_data.empty

    def test_export_with_title(self) -> None:
        """Test export with title."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_with_title.xlsx"

            test_data = pd.DataFrame({"Col1": [1, 2]})
            title = "Test Report"

            export_dataframe_to_excel(test_data, output_path, title=title)

            assert output_path.exists()

    def test_export_empty_dataframe(self) -> None:
        """Test export of empty DataFrame."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "empty.xlsx"

            empty_data = pd.DataFrame()

            export_dataframe_to_excel(empty_data, output_path)

            assert output_path.exists()

    def test_custom_sheet_name(self) -> None:
        """Test export with custom sheet name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "custom_sheet.xlsx"

            test_data = pd.DataFrame({"Col1": [1, 2]})

            export_dataframe_to_excel(test_data, output_path, sheet_name="Custom")

            assert output_path.exists()

            # Verify sheet name by reading with pandas ExcelFile (closes file properly)
            with pd.ExcelFile(output_path) as excel_file:
                assert "Custom" in excel_file.sheet_names

    def test_directory_creation(self) -> None:
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "subdir" / "test.xlsx"

            test_data = pd.DataFrame({"Col1": [1, 2]})

            export_dataframe_to_excel(test_data, output_path)

            assert output_path.exists()
            assert output_path.parent.exists()
