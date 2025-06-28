"""Tests for RTF to text CLI functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from kp_analysis_toolkit.rtf_to_text.cli import get_input_file, process_command_line


class TestGetInputFile:
    """Test the get_input_file function."""

    def test_get_input_file_with_specific_file(self) -> None:
        """Test getting input file when specific file is provided."""
        result = get_input_file("test.rtf", "./")
        assert result == Path("test.rtf")

    def test_get_input_file_no_rtf_files(self) -> None:
        """Test error when no RTF files are found."""
        with tempfile.TemporaryDirectory() as tmpdir:  # noqa: SIM117
            with pytest.raises(ValueError, match="No RTF files found"):
                get_input_file(None, tmpdir)

    def test_get_input_file_single_rtf_file(self) -> None:
        """Test automatic selection when only one RTF file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            rtf_file = tmpdir_path / "test.rtf"
            rtf_file.write_text("{\rtf1 test}")

            result = get_input_file(None, tmpdir)
            assert result == rtf_file

    def test_get_input_file_multiple_rtf_files_user_choice(self) -> None:
        """Test user choice when multiple RTF files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            rtf_file1 = tmpdir_path / "test1.rtf"
            rtf_file2 = tmpdir_path / "test2.rtf"
            rtf_file1.write_text("{\rtf1 test1}")
            rtf_file2.write_text("{\rtf1 test2}")

            with patch("builtins.input", return_value="1"):
                result = get_input_file(None, tmpdir)

            # Result should be one of the files (order may vary based on filesystem)
            assert result in [rtf_file1, rtf_file2]


class TestProcessCommandLine:
    """Test the CLI command functionality."""

    def test_process_command_line_help(self) -> None:
        """Test that help command works."""
        runner = CliRunner()
        result = runner.invoke(process_command_line, ["--help"])
        assert result.exit_code == 0
        assert "Convert RTF files to plain text format" in result.output

    def test_process_command_line_with_invalid_file(self) -> None:
        """Test error handling with invalid file."""
        runner = CliRunner()
        result = runner.invoke(process_command_line, ["-f", "nonexistent.rtf"])
        assert result.exit_code == 1
        assert "Error processing RTF file" in result.output
