"""RTF-specific test fixtures for centralized mock creation."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from kp_analysis_toolkit.rtf_to_text.service import RtfToTextService
from kp_analysis_toolkit.rtf_to_text.services.rtf_converter import RtfConverterService

# =============================================================================
# RTF SERVICE FIXTURES - Using Centralized Mocks
# =============================================================================


@pytest.fixture
def mock_rtf_converter_service() -> Mock:
    """
    Create a properly configured mock RtfConverterService.

    This centralizes the mock setup to reduce repetition across tests
    and ensures consistent behavior.
    """
    mock_service: Mock = Mock(spec=RtfConverterService)

    # Default successful behavior
    mock_service.convert_rtf_to_text.return_value = "converted text content"
    mock_service.save_as_text.return_value = None

    return mock_service


@pytest.fixture
def mock_rtf_to_text_service(
    mock_rtf_converter_service: Mock,
    mock_file_processing_service: Mock,
    mock_rich_output_service: Mock,
) -> RtfToTextService:
    """
    Create a RtfToTextService with mocked dependencies.

    This fixture uses other centralized fixtures to create a properly
    configured service for testing, following DI patterns.
    """
    return RtfToTextService(
        rtf_converter=mock_rtf_converter_service,
        rich_output=mock_rich_output_service,
        file_processing=mock_file_processing_service,
    )


@pytest.fixture
def mock_rich_output_service() -> Mock:
    """
    Create a properly configured mock RichOutputService for RTF tests.

    This provides consistent mock behavior for output operations.
    """
    mock_service: Mock = Mock()

    # Default behavior for common operations
    mock_service.info.return_value = None
    mock_service.success.return_value = None
    mock_service.warning.return_value = None
    mock_service.error.return_value = None
    mock_service.header.return_value = None

    # Properties
    mock_service.verbose = False
    mock_service.quiet = False

    return mock_service


# =============================================================================
# RTF TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def rtf_test_files(tmp_path: Path) -> dict[str, Path]:
    """
    Create a set of test RTF files for testing.

    Returns a dictionary with different types of test files:
    - valid_rtf: A properly formatted RTF file
    - invalid_extension: A non-RTF file
    - empty_rtf: An empty RTF file
    """
    files = {}

    # Valid RTF file
    valid_rtf = tmp_path / "test.rtf"
    valid_rtf.write_text("{\\rtf1 Sample RTF content for testing}")
    files["valid_rtf"] = valid_rtf

    # Invalid extension file
    invalid_ext = tmp_path / "test.txt"
    invalid_ext.write_text("Not an RTF file")
    files["invalid_extension"] = invalid_ext

    # Empty RTF file
    empty_rtf = tmp_path / "empty.rtf"
    empty_rtf.write_text("{\\rtf1}")
    files["empty_rtf"] = empty_rtf

    return files


@pytest.fixture
def rtf_batch_test_files(tmp_path: Path) -> dict[str, Path | list[Path]]:
    """
    Create multiple RTF files for batch processing tests.

    Returns a dictionary with:
    - directory: The containing directory
    - rtf_files: List of RTF files
    - non_rtf_files: List of non-RTF files
    - output_dir: Directory for output files
    """
    # Create multiple RTF files
    rtf_files: list[Path] = []
    for i in range(1, 4):
        rtf_file = tmp_path / f"test{i}.rtf"
        rtf_file.write_text(f"{{\\rtf1 Test content {i}}}")
        rtf_files.append(rtf_file)

    # Create non-RTF files
    non_rtf_files: list[Path] = []
    for i in range(1, 3):
        txt_file = tmp_path / f"test{i}.txt"
        txt_file.write_text(f"Not RTF content {i}")
        non_rtf_files.append(txt_file)

    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    return {
        "directory": tmp_path,
        "rtf_files": rtf_files,
        "non_rtf_files": non_rtf_files,
        "output_dir": output_dir,
    }


@pytest.fixture
def temp_rtf_workspace(tmp_path: Path) -> Path:
    """
    Create a temporary workspace with RTF files and subdirectories.

    This fixture creates a more complex directory structure for testing
    file discovery and batch processing with nested directories.
    """
    # Create subdirectories
    subdir1 = tmp_path / "subdir1"
    subdir2 = tmp_path / "subdir2"
    subdir1.mkdir()
    subdir2.mkdir()

    # Create RTF files in various locations
    (tmp_path / "root.rtf").write_text("{\\rtf1 Root RTF}")
    (subdir1 / "sub1.rtf").write_text("{\\rtf1 Subdir1 RTF}")
    (subdir2 / "sub2.rtf").write_text("{\\rtf1 Subdir2 RTF}")

    # Create some non-RTF files
    (tmp_path / "readme.txt").write_text("Not RTF")
    (subdir1 / "notes.txt").write_text("Also not RTF")

    return tmp_path


# =============================================================================
# CONSTANTS FOR CONSISTENT TESTING
# =============================================================================


# Test constants to avoid magic numbers
TEST_FILE_COUNT = 3
EXPECTED_SUCCESS_COUNT = 3
EXPECTED_PARTIAL_SUCCESS_COUNT = 2
EXPECTED_FAILURE_COUNT = 1

# Common test content
SAMPLE_RTF_CONTENT = "{\\rtf1 Sample RTF content for testing}"
CONVERTED_TEXT_CONTENT = "converted text content"
