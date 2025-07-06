"""Tests for the enhanced common file selection functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from kp_analysis_toolkit.cli.common.file_selection import (
    get_all_files_matching_pattern,
    get_input_file,
)


class TestEnhancedFileSelection:
    """Test the enhanced file selection functionality."""

    def test_get_input_file_with_process_all_option_disabled(self) -> None:
        """Test that process all option doesn't appear when disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            csv_file1 = tmpdir_path / "test1.csv"
            csv_file2 = tmpdir_path / "test2.csv"
            csv_file1.write_text("header1,header2\nvalue1,value2\n")
            csv_file2.write_text("header1,header2\nvalue3,value4\n")

            # User chooses first file (option 1)
            with patch("builtins.input", return_value="1"):
                result = get_input_file(
                    None,
                    tmpdir,
                    file_pattern="*.csv",
                    file_type_description="CSV",
                    include_process_all_option=False,
                )

            # Should return a Path object (not None)
            assert result is not None
            assert result.name in ["test1.csv", "test2.csv"]

    def test_get_input_file_with_process_all_option_enabled(self) -> None:
        """Test that process all option appears when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            csv_file1 = tmpdir_path / "test1.csv"
            csv_file2 = tmpdir_path / "test2.csv"
            csv_file1.write_text("header1,header2\nvalue1,value2\n")
            csv_file2.write_text("header1,header2\nvalue3,value4\n")

            # User chooses "process all files" (option 3 with 2 files)
            with patch("builtins.input", return_value="3"):
                result = get_input_file(
                    None,
                    tmpdir,
                    file_pattern="*.csv",
                    file_type_description="CSV",
                    include_process_all_option=True,
                )

            # Should return None to indicate "process all files"
            assert result is None

    def test_get_input_file_with_custom_file_pattern(self) -> None:
        """Test file selection with custom file pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_file = tmpdir_path / "test.log"
            log_file.write_text("Log entry 1\nLog entry 2\n")

            result = get_input_file(
                None,
                tmpdir,
                file_pattern="*.log",
                file_type_description="Log",
            )

            # Should auto-select the single log file
            assert result is not None
            assert result.name == "test.log"

    def test_get_input_file_with_custom_error_message(self) -> None:
        """Test that custom file type description appears in error messages."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            pytest.raises(ValueError, match="No XML files found"),
        ):
            get_input_file(
                None,
                tmpdir,
                file_pattern="*.xml",
                file_type_description="XML",
            )

    def test_get_all_files_matching_pattern(self) -> None:
        """Test the get_all_files_matching_pattern helper function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create various files
            csv_file1 = tmpdir_path / "data1.csv"
            csv_file2 = tmpdir_path / "data2.csv"
            txt_file = tmpdir_path / "readme.txt"

            csv_file1.write_text("csv,data\n1,2\n")
            csv_file2.write_text("csv,data\n3,4\n")
            txt_file.write_text("This is a readme file")

            # Test CSV pattern
            csv_files = get_all_files_matching_pattern(tmpdir, "*.csv")
            expected_csv_count = 2
            assert len(csv_files) == expected_csv_count
            csv_names = {f.name for f in csv_files}
            assert csv_names == {"data1.csv", "data2.csv"}

            # Test TXT pattern
            txt_files = get_all_files_matching_pattern(tmpdir, "*.txt")
            expected_txt_count = 1
            assert len(txt_files) == expected_txt_count
            assert txt_files[0].name == "readme.txt"

            # Test pattern with no matches
            log_files = get_all_files_matching_pattern(tmpdir, "*.log")
            assert len(log_files) == 0

    def test_single_file_auto_selection_with_process_all_disabled(self) -> None:
        """Test that single files are auto-selected when process all is disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            single_file = tmpdir_path / "only.csv"
            single_file.write_text("single,file\ndata,here\n")

            result = get_input_file(
                None,
                tmpdir,
                file_pattern="*.csv",
                file_type_description="CSV",
                include_process_all_option=False,
            )

            # Should auto-select the single file
            assert result is not None
            assert result.name == "only.csv"

    def test_single_file_with_process_all_enabled_shows_menu(self) -> None:
        """Test that single files still show menu when process all is enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            single_file = tmpdir_path / "only.csv"
            single_file.write_text("single,file\ndata,here\n")

            # User chooses the single file (option 1)
            with patch("builtins.input", return_value="1"):
                result = get_input_file(
                    None,
                    tmpdir,
                    file_pattern="*.csv",
                    file_type_description="CSV",
                    include_process_all_option=True,
                )

            # Should return the file
            assert result is not None
            assert result.name == "only.csv"

            # User chooses process all (option 2 with 1 file)
            with patch("builtins.input", return_value="2"):
                result = get_input_file(
                    None,
                    tmpdir,
                    file_pattern="*.csv",
                    file_type_description="CSV",
                    include_process_all_option=True,
                )

            # Should return None for "process all"
            assert result is None
