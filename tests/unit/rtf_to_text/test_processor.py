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
    EXPECTED_PARTIAL_SUCCESS_COUNT,
    EXPECTED_SUCCESS_COUNT,
    SAMPLE_RTF_CONTENT,
    TEST_FILE_COUNT,
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
            input_file.write_text("test content")

            config = ProgramConfig(
                input_file=input_file,
                source_files_path=tmpdir_path,
            )

            output_file: Path = config.output_file
            assert output_file.parent == input_file.parent
            assert output_file.suffix == ".txt"
            assert "sample_converted-" in output_file.name


class TestRtfConverterService:
    """Test the RtfConverterService using centralized fixtures."""

    def test_convert_rtf_to_text_file_not_found(
        self,
        mock_rich_output_service: Mock,
        mock_file_processing_service: Mock,
    ) -> None:
        """Test conversion with non-existent file."""
        service = RtfConverterService(
            rich_output=mock_rich_output_service,
            file_processing=mock_file_processing_service,
        )

        nonexistent_file = Path("/nonexistent/file.rtf")

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            service.convert_rtf_to_text(nonexistent_file)

    def test_convert_rtf_to_text_wrong_extension(
        self,
        mock_rich_output_service: Mock,
        mock_file_processing_service: Mock,
        rtf_test_files: dict[str, Path],
    ) -> None:
        """Test conversion with wrong file extension using test data."""
        service = RtfConverterService(
            rich_output=mock_rich_output_service,
            file_processing=mock_file_processing_service,
        )

        wrong_file = rtf_test_files["invalid_extension"]

        with pytest.raises(ValueError, match="Input file must have .rtf extension"):
            service.convert_rtf_to_text(wrong_file)

    @patch("striprtf.striprtf.rtf_to_text")
    def test_convert_rtf_to_text_valid(
        self,
        mock_rtf_to_text: Mock,
        mock_rich_output_service: Mock,
        mock_file_processing_service: Mock,
        rtf_test_files: dict[str, Path],
    ) -> None:
        """Test successful RTF conversion using centralized fixtures."""
        # Configure mock behavior
        mock_file_processing_service.detect_encoding.return_value = "utf-8"
        mock_rtf_to_text.return_value = CONVERTED_TEXT_CONTENT

        service = RtfConverterService(
            rich_output=mock_rich_output_service,
            file_processing=mock_file_processing_service,
        )

        rtf_file = rtf_test_files["valid_rtf"]
        result = service.convert_rtf_to_text(rtf_file)

        assert result == CONVERTED_TEXT_CONTENT
        mock_file_processing_service.detect_encoding.assert_called_once_with(rtf_file)
        mock_rtf_to_text.assert_called_once()

    def test_save_as_text(
        self,
        mock_rich_output_service: Mock,
        mock_file_processing_service: Mock,
        tmp_path: Path,
    ) -> None:
        """Test saving text content to file using centralized fixtures."""
        service = RtfConverterService(
            rich_output=mock_rich_output_service,
            file_processing=mock_file_processing_service,
        )

        output_file = tmp_path / "output.txt"
        test_content = CONVERTED_TEXT_CONTENT

        service.save_as_text(test_content, output_file)

        assert output_file.exists()
        # Read with ASCII encoding to match the save method
        saved_content = output_file.read_text(encoding="ascii")
        assert saved_content == test_content


class TestRtfToTextService:
    """Test the RtfToTextService using centralized fixtures and best practices."""

    def test_convert_file(self, mock_rtf_to_text_service: RtfToTextService) -> None:
        """Test single file conversion using centralized service fixture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.rtf"
            output_file = tmpdir_path / "test.txt"
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

    def test_discover_rtf_files_single_file(
        self,
        mock_rtf_to_text_service: RtfToTextService,
        rtf_test_files: dict[str, Path],
    ) -> None:
        """Test discovering a single RTF file using test data."""
        rtf_file = rtf_test_files["valid_rtf"]

        result = mock_rtf_to_text_service.discover_rtf_files(rtf_file)

        assert result == [rtf_file]

    def test_discover_rtf_files_directory(
        self,
        mock_rtf_to_text_service: RtfToTextService,
        rtf_batch_test_files: dict[str, Path | list[Path]],
    ) -> None:
        """Test discovering RTF files in a directory using batch test data."""
        directory = rtf_batch_test_files["directory"]
        assert isinstance(directory, Path)

        expected_rtf_files = rtf_batch_test_files["rtf_files"]
        assert isinstance(expected_rtf_files, list)

        non_rtf_files = rtf_batch_test_files["non_rtf_files"]
        assert isinstance(non_rtf_files, list)

        result = mock_rtf_to_text_service.discover_rtf_files(directory)

        # Use constant for expected file count
        expected_count = TEST_FILE_COUNT
        assert len(result) == expected_count
        for expected_file in expected_rtf_files:
            assert expected_file in result
        for non_rtf_file in non_rtf_files:
            assert non_rtf_file not in result

    def test_convert_files_batch_success(
        self,
        mock_rtf_to_text_service: RtfToTextService,
        rtf_batch_test_files: dict[str, Path | list[Path]],
    ) -> None:
        """Test successful batch conversion using centralized fixtures."""
        rtf_files = cast("list[Path]", rtf_batch_test_files["rtf_files"])
        output_dir = cast("Path", rtf_batch_test_files["output_dir"])

        # Configure mock behavior for batch processing
        mock_converter = cast("Mock", mock_rtf_to_text_service.rtf_converter)

        mock_converter.convert_rtf_to_text.side_effect = [
            f"{CONVERTED_TEXT_CONTENT} 1",
            f"{CONVERTED_TEXT_CONTENT} 2",
            f"{CONVERTED_TEXT_CONTENT} 3",
        ]

        mock_rtf_to_text_service.convert_files_batch(rtf_files, output_dir)

        # Verify batch processing calls using constants
        assert (
            mock_rtf_to_text_service.rtf_converter.convert_rtf_to_text.call_count
            == TEST_FILE_COUNT
        )
        assert (
            mock_rtf_to_text_service.rtf_converter.save_as_text.call_count
            == TEST_FILE_COUNT
        )
        mock_rtf_to_text_service.rich_output.header.assert_called_once_with(
            f"Converting {TEST_FILE_COUNT} RTF files",
        )
        mock_rtf_to_text_service.rich_output.success.assert_called_with(
            f"Successfully converted {EXPECTED_SUCCESS_COUNT}/{TEST_FILE_COUNT} RTF files",
        )

    def test_convert_files_batch_empty_list(
        self,
        mock_rtf_to_text_service: RtfToTextService,
    ) -> None:
        """Test batch conversion with empty file list using centralized fixture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir()

            mock_rtf_to_text_service.convert_files_batch([], output_dir)

            # Verify warning is shown and no processing happens
            mock_rtf_to_text_service.rich_output.warning.assert_called_once_with(
                "No RTF files provided for conversion",
            )
            mock_rtf_to_text_service.rtf_converter.convert_rtf_to_text.assert_not_called()

    def test_convert_files_batch_partial_failure(
        self,
        mock_rtf_to_text_service: RtfToTextService,
        rtf_batch_test_files: dict[str, Path | list[Path]],
    ) -> None:
        """Test batch conversion with some files failing using centralized fixtures."""
        rtf_files = cast("list[Path]", rtf_batch_test_files["rtf_files"])
        output_dir = cast("Path", rtf_batch_test_files["output_dir"])

        # Mock converter to succeed for first file, fail for second, succeed for third
        mock_converter = cast("Mock", mock_rtf_to_text_service.rtf_converter)

        mock_converter.convert_rtf_to_text.side_effect = [
            f"{CONVERTED_TEXT_CONTENT} 1",
            ValueError("Conversion failed"),
            f"{CONVERTED_TEXT_CONTENT} 3",
        ]

        mock_rtf_to_text_service.convert_files_batch(rtf_files, output_dir)

        # Verify calls using constants
        assert (
            mock_rtf_to_text_service.rtf_converter.convert_rtf_to_text.call_count
            == TEST_FILE_COUNT
        )
        mock_rtf_to_text_service.rich_output.header.assert_called_once_with(
            f"Converting {TEST_FILE_COUNT} RTF files",
        )
        # Error should be called at least once for the failed file
        assert mock_rtf_to_text_service.rich_output.error.call_count >= 1
        mock_rtf_to_text_service.rich_output.success.assert_called_with(
            f"Successfully converted {EXPECTED_PARTIAL_SUCCESS_COUNT}/{TEST_FILE_COUNT} RTF files",
        )

    def test_convert_files_batch_preserve_structure_false(
        self,
        mock_rtf_to_text_service: RtfToTextService,
        temp_rtf_workspace: Path,
    ) -> None:
        """Test batch conversion with flat output structure using workspace fixture."""
        # Use the workspace fixture that has nested structure
        rtf_files = list(temp_rtf_workspace.rglob("*.rtf"))
        output_dir = temp_rtf_workspace / "output"
        output_dir.mkdir()

        mock_rtf_to_text_service.rtf_converter.convert_rtf_to_text.return_value = (
            CONVERTED_TEXT_CONTENT
        )

        # Test file in subdirectory
        subdir_rtf = next(f for f in rtf_files if f.parent != temp_rtf_workspace)

        mock_rtf_to_text_service.convert_files_batch(
            [subdir_rtf],
            output_dir,
            preserve_structure=False,
        )

        # Verify the file was processed
        mock_rtf_to_text_service.rtf_converter.convert_rtf_to_text.assert_called_once_with(
            subdir_rtf,
        )
        # The output path should be flat
        expected_calls = (
            mock_rtf_to_text_service.rtf_converter.save_as_text.call_args_list
        )
        assert len(expected_calls) == 1
        output_path = expected_calls[0][0][1]  # Second argument to save_as_text
        assert output_path.parent == output_dir
        assert output_path.name == f"{subdir_rtf.stem}.txt"

    def test_convert_files_batch_output_path_structure(
        self,
        mock_rtf_to_text_service: RtfToTextService,
        rtf_test_files: dict[str, Path],
    ) -> None:
        """Test that batch conversion creates proper output file paths."""
        rtf_file = rtf_test_files["valid_rtf"]
        output_dir = rtf_file.parent / "output"
        output_dir.mkdir()

        mock_rtf_to_text_service.rtf_converter.convert_rtf_to_text.return_value = (
            CONVERTED_TEXT_CONTENT
        )

        mock_rtf_to_text_service.convert_files_batch([rtf_file], output_dir)

        # Verify the file was processed
        mock_rtf_to_text_service.rtf_converter.convert_rtf_to_text.assert_called_once_with(
            rtf_file,
        )
        # Check that save_as_text was called with proper output path
        expected_calls = (
            mock_rtf_to_text_service.rtf_converter.save_as_text.call_args_list
        )
        assert len(expected_calls) == 1
        output_path = expected_calls[0][0][1]  # Second argument to save_as_text
        assert output_path.parent == output_dir
        assert output_path.suffix == ".txt"
        assert rtf_file.stem in output_path.name

    def test_discover_rtf_files_no_files_found(
        self,
        mock_rtf_to_text_service: RtfToTextService,
    ) -> None:
        """Test file discovery when no RTF files exist using test data."""
        # Create a temporary directory with only non-RTF files
        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            # Create only non-RTF files
            txt_file = directory / "test.txt"
            doc_file = directory / "test.doc"
            txt_file.write_text("not rtf")
            doc_file.write_text("also not rtf")

            result = mock_rtf_to_text_service.discover_rtf_files(directory)

            assert result == []
            mock_rtf_to_text_service.rich_output.info.assert_called_once_with(
                f"Found 0 RTF files in {directory}",
            )

    def test_discover_rtf_files_nonexistent_path(
        self,
        mock_rtf_to_text_service: RtfToTextService,
    ) -> None:
        """Test file discovery with nonexistent path using centralized fixture."""
        nonexistent_path = Path("/nonexistent/path")
        result = mock_rtf_to_text_service.discover_rtf_files(nonexistent_path)

        assert result == []
        mock_rtf_to_text_service.rich_output.warning.assert_called_once_with(
            f"No RTF files found at {nonexistent_path}",
        )
