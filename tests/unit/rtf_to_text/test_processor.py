# AI-GEN: claude-3.5-sonnet|2025-01-19|batch-processing-service|reviewed:yes
"""Tests for RTF processing functionality using DI services."""

import tempfile
from pathlib import Path
from typing import cast
from unittest.mock import Mock, patch

import pytest

from kp_analysis_toolkit.rtf_to_text.models.program_config import ProgramConfig
from kp_analysis_toolkit.rtf_to_text.service import RtfToTextService
from kp_analysis_toolkit.rtf_to_text.services.rtf_converter import RtfConverterService

# Import centralized test constants only
from tests.fixtures.rtf_fixtures import (
    CONVERTED_TEXT_CONTENT,
    SAMPLE_RTF_CONTENT,
)


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
            output_file: Path = config.output_file
            assert output_file.name.startswith("test_converted-")
            assert output_file.name.endswith(".txt")

    def test_program_config_invalid_input_file(self) -> None:
        """Test ProgramConfig with invalid input file."""
        with pytest.raises(ValueError, match="Input file is required"):
            ProgramConfig(input_file=None)

    def test_program_config_output_file_generation(self) -> None:
        """Test that output file is correctly generated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "sample.rtf"
            input_file.write_text("{\rtf1 sample}")

            config = ProgramConfig(
                input_file=input_file,
                source_files_path=tmpdir_path,
            )

            output_file: Path = config.output_file
            assert output_file.suffix == ".txt"
            assert "sample_converted-" in output_file.name


class TestRtfConverterService:
    """Test the RtfConverterService class."""

    def test_convert_rtf_to_text_file_not_found(self) -> None:
        """Test converting a non-existent RTF file."""
        service = RtfConverterService(Mock(), Mock())
        with pytest.raises(FileNotFoundError):
            service.convert_rtf_to_text(Path("nonexistent.rtf"))

    def test_convert_rtf_to_text_wrong_extension(self) -> None:
        """Test converting a file with wrong extension."""
        service = RtfConverterService(Mock(), Mock())
        with tempfile.TemporaryDirectory() as tmpdir:
            wrong_file = Path(tmpdir) / "test.txt"
            wrong_file.write_text("not rtf")
            with pytest.raises(ValueError, match="must have .rtf extension"):
                service.convert_rtf_to_text(wrong_file)

    @patch("striprtf.striprtf.rtf_to_text")
    def test_convert_rtf_to_text_valid(self, mock_striprtf: Mock) -> None:
        """Test converting a valid RTF file."""
        mock_striprtf.return_value = CONVERTED_TEXT_CONTENT

        # Mock the file processing service to return utf-8 encoding
        mock_file_processing = Mock()
        mock_file_processing.detect_encoding.return_value = "utf-8"

        service = RtfConverterService(Mock(), mock_file_processing)

        with tempfile.TemporaryDirectory() as tmpdir:
            rtf_file = Path(tmpdir) / "test.rtf"
            rtf_file.write_text(SAMPLE_RTF_CONTENT, encoding="utf-8")

            result = service.convert_rtf_to_text(rtf_file)

            assert result == CONVERTED_TEXT_CONTENT
            mock_striprtf.assert_called_once_with(SAMPLE_RTF_CONTENT)

    def test_save_as_text(self) -> None:
        """Test saving text content with ASCII encoding."""
        service = RtfConverterService(Mock(), Mock())

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.txt"
            text_content = "Test ASCII content"

            service.save_as_text(text_content, output_file, encoding="ascii")

            assert output_file.exists()
            assert output_file.read_text(encoding="ascii") == text_content


class TestRtfToTextService:
    """Test the RtfToTextService class."""

    def test_convert_file(
        self,
        mock_rtf_to_text_service: RtfToTextService,
    ) -> None:
        """Test converting a single RTF file using centralized fixture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test.rtf"
            output_file = Path(tmpdir) / "test.txt"

            input_file.write_text(SAMPLE_RTF_CONTENT)

            mock_rtf_to_text_service.convert_file(input_file, output_file)

            # Verify service calls
            mock_converter = cast("Mock", mock_rtf_to_text_service.rtf_converter)
            mock_rich_output = cast("Mock", mock_rtf_to_text_service.rich_output)

            mock_converter.convert_rtf_to_text.assert_called_once_with(
                input_file,
            )
            mock_converter.save_as_text.assert_called_once_with(
                CONVERTED_TEXT_CONTENT,
                output_file,
                encoding="ascii",
            )
            mock_rich_output.info.assert_called_once()
            mock_rich_output.success.assert_called_once()


# END AI-GEN
