"""Tests for RTF processing functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from kp_analysis_toolkit.rtf_to_text.models.program_config import ProgramConfig
from kp_analysis_toolkit.rtf_to_text.process_rtf import process_rtf_file


class TestProgramConfig:
    """Test the ProgramConfig model."""

    def test_program_config_valid(self) -> None:
        """Test creating a valid program configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.rtf"
            input_file.write_text("{\rtf1 test}")

            config = ProgramConfig(
                input_file=input_file,
                source_files_path=tmpdir_path,
            )

            assert config.input_file == input_file
            assert config.output_file.name.startswith("test_converted-")
            assert config.output_file.name.endswith(".txt")
            assert config.output_file.parent == tmpdir_path

    def test_program_config_none_input_file(self) -> None:
        """Test error when input file is None."""
        with pytest.raises(ValueError, match="Input file is required"):
            ProgramConfig(input_file=None, source_files_path="./")

    def test_encoding_detection_used(self) -> None:
        """Test that encoding detection is being used."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.rtf"

            # Create a simple RTF file
            rtf_content = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}} \f0\fs24 Test encoding detection.}"
            input_file.write_text(rtf_content)

            config = ProgramConfig(
                input_file=input_file,
                source_files_path=tmpdir_path,
            )

            # Mock the detect_encoding function to verify it's called
            with patch(
                "kp_analysis_toolkit.rtf_to_text.process_rtf.detect_encoding"
            ) as mock_detect:
                mock_detect.return_value = "utf-8"

                process_rtf_file(config)

                # Verify detect_encoding was called
                assert mock_detect.call_count >= 1
                # Verify it was called with our input file
                mock_detect.assert_called_with(input_file)


class TestProcessRtfFile:
    """Test the RTF processing functionality."""

    def test_process_rtf_file_nonexistent(self) -> None:
        """Test error when input file doesn't exist."""
        config = ProgramConfig(
            input_file=Path("nonexistent.rtf"),
            source_files_path="./",
        )

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            process_rtf_file(config)

    def test_process_rtf_file_wrong_extension(self) -> None:
        """Test error when file doesn't have RTF extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.txt"
            input_file.write_text("not rtf")

            config = ProgramConfig(
                input_file=input_file,
                source_files_path=tmpdir_path,
            )

            with pytest.raises(ValueError, match="Input file must have .rtf extension"):
                process_rtf_file(config)

    def test_process_rtf_file_valid(self) -> None:
        """Test successful RTF processing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.rtf"

            # Create a simple RTF file
            rtf_content = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}} \f0\fs24 Hello World \par This is a test.}"
            input_file.write_text(rtf_content)

            config = ProgramConfig(
                input_file=input_file,
                source_files_path=tmpdir_path,
            )

            process_rtf_file(config)

            # Check that output file was created (it will have a timestamp in the name)
            assert config.output_file.exists()

            # Check that content was converted (should contain "Hello World" and "This is a test")
            output_content = config.output_file.read_text(
                encoding="ascii", errors="ignore"
            )
            assert "Hello World" in output_content
            assert "This is a test" in output_content
