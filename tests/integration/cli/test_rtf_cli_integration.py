"""Tests for RTF to text CLI functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from kp_analysis_toolkit.cli.commands.rtf_to_text import process_command_line
from kp_analysis_toolkit.cli.common.file_selection import get_input_file


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
                get_input_file(
                    None,
                    tmpdir,
                    file_pattern="*.rtf",
                    file_type_description="RTF",
                )

    def test_get_input_file_single_rtf_file(self) -> None:
        """Test automatic selection when only one RTF file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            rtf_file = tmpdir_path / "test.rtf"
            rtf_file.write_text("{\rtf1 test}")

            result = get_input_file(
                None,
                tmpdir,
                file_pattern="*.rtf",
                file_type_description="RTF",
            )
            # Resolve both paths to handle Windows short/long path differences
            assert result.resolve() == rtf_file.resolve()

    def test_get_input_file_multiple_rtf_files_user_choice(self) -> None:
        """Test user choice when multiple RTF files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            rtf_file1 = tmpdir_path / "test1.rtf"
            rtf_file2 = tmpdir_path / "test2.rtf"
            rtf_file1.write_text("{\rtf1 test1}")
            rtf_file2.write_text("{\rtf1 test2}")

            with patch("builtins.input", return_value="1"):
                result = get_input_file(
                    None,
                    tmpdir,
                    file_pattern="*.rtf",
                    file_type_description="RTF",
                )

            # Result should be one of the files (order may vary based on filesystem)
            # Resolve paths to handle Windows short/long path differences
            resolved_result = result.resolve()
            resolved_files = [rtf_file1.resolve(), rtf_file2.resolve()]
            assert resolved_result in resolved_files

    def test_get_input_file_process_all_option(self) -> None:
        """Test the 'process all files' option functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            rtf_file1 = tmpdir_path / "test1.rtf"
            rtf_file2 = tmpdir_path / "test2.rtf"
            rtf_file1.write_text("{\rtf1 test1}")
            rtf_file2.write_text("{\rtf1 test2}")

            # User chooses option 3 (process all files)
            with patch("builtins.input", return_value="3"):
                result = get_input_file(
                    None,
                    tmpdir,
                    file_pattern="*.rtf",
                    file_type_description="RTF",
                    include_process_all_option=True,
                )

            # Should return None to indicate "process all files"
            assert result is None


class TestProcessCommandLine:
    """Test the CLI command functionality."""

    def test_process_command_line_help(self, cli_runner: CliRunner) -> None:
        """Test that help command works."""
        result = cli_runner.invoke(process_command_line, ["--help"])
        assert result.exit_code == 0
        assert "Convert RTF files to plain text format" in result.output

    def test_process_command_line_with_invalid_file(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test error handling with invalid file."""
        result = cli_runner.invoke(process_command_line, ["-f", "nonexistent.rtf"])
        assert result.exit_code == 1
        assert "Error processing RTF file" in result.output

    def test_process_all_files_integration(self, cli_runner: CliRunner) -> None:
        """Test the integration of the 'process all files' functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            rtf_file1 = tmpdir_path / "test1.rtf"
            rtf_file2 = tmpdir_path / "test2.rtf"

            # Create RTF files with proper RTF content
            rtf_content1 = r"{\rtf1\ansi\deff0 Test RTF content 1}"
            rtf_content2 = r"{\rtf1\ansi\deff0 Test RTF content 2}"
            rtf_file1.write_text(rtf_content1)
            rtf_file2.write_text(rtf_content2)

            # First, test that both files would be found
            from kp_analysis_toolkit.cli.utils.path_helpers import (
                discover_files_by_pattern,
            )

            files = discover_files_by_pattern(tmpdir_path, "*.rtf")
            expected_file_count = 2
            assert len(files) == expected_file_count

            # Mock user input to select "process all files" (option 3 with 2 files)
            with patch("builtins.input", return_value="3"):
                result = cli_runner.invoke(
                    process_command_line,
                    ["-d", str(tmpdir_path)],
                )

            # Debug output in case of failure
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            if result.exception:
                print(f"Exception: {result.exception}")

            # Should exit normally after processing all files
            assert result.exit_code == 0

            # Check that output files were created (they have timestamps in the name)
            # Look for files matching the pattern test1_converted-*.txt and test2_converted-*.txt
            output_files = list(tmpdir_path.glob("*_converted-*.txt"))

            # List all files in directory for debugging
            print(f"Files in directory: {list(tmpdir_path.iterdir())}")
            print(f"Output files found: {output_files}")

            assert len(output_files) == expected_file_count, (
                f"Expected {expected_file_count} output files, found {len(output_files)}"
            )

            # Find the specific output files
            test1_output = next(
                (f for f in output_files if f.name.startswith("test1_converted-")),
                None,
            )
            test2_output = next(
                (f for f in output_files if f.name.startswith("test2_converted-")),
                None,
            )

            assert test1_output is not None, "Expected test1 output file to exist"
            assert test2_output is not None, "Expected test2 output file to exist"

            # Verify content was processed
            content1 = test1_output.read_text()
            content2 = test2_output.read_text()
            assert "Test RTF content 1" in content1
            assert "Test RTF content 2" in content2
