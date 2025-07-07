# tests/conftest.py
"""Shared pytest configuration and fixtures."""

from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from kp_analysis_toolkit.process_scripts.models.enums import OSFamilyType, ProducerType
from kp_analysis_toolkit.process_scripts.models.systems import Systems


@pytest.fixture(scope="session")
def testdata_dir() -> Path:
    """Return the testdata directory path."""
    return Path(__file__).parent.parent / "testdata"


@pytest.fixture(scope="session")
def temp_workspace(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a temporary workspace for tests."""
    return tmp_path_factory.mktemp("test_workspace")


@pytest.fixture
def mock_file_system() -> Generator[dict[str, MagicMock], Any, None]:
    """
    Mock file system operations for testing.

    Returns a dictionary of mocked pathlib.Path methods:
    - exists: Mock for Path.exists()
    - is_file: Mock for Path.is_file()
    - is_dir: Mock for Path.is_dir()
    - mkdir: Mock for Path.mkdir()
    """
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("pathlib.Path.is_file") as mock_is_file,
        patch("pathlib.Path.is_dir") as mock_is_dir,
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        # Default behavior - everything exists
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_is_dir.return_value = True
        mock_mkdir.return_value = None

        yield {
            "exists": mock_exists,
            "is_file": mock_is_file,
            "is_dir": mock_is_dir,
            "mkdir": mock_mkdir,
        }


@pytest.fixture
def mock_linux_system() -> Systems:
    """Create a mock Linux Systems object for testing."""
    system: Systems = Mock(spec=Systems)
    system.system_name = "test-linux-system"
    system.os_family = OSFamilyType.LINUX
    system.producer = ProducerType.KPNIXAUDIT
    system.producer_version = "1.0.0"
    system.file = Mock()
    system.file.name = "test-system.log"
    return system


@pytest.fixture
def mock_windows_system() -> Systems:
    """Create a mock Windows Systems object for testing."""
    system: Systems = Mock(spec=Systems)
    system.system_name = "test-windows-system"
    system.os_family = OSFamilyType.WINDOWS
    system.producer = ProducerType.KPWINAUDIT
    system.producer_version = "1.0.0"
    system.file = Mock()
    system.file.name = "test-system.log"
    return system


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI runner for testing CLI commands."""
    return CliRunner()


@pytest.fixture
def isolated_cli_runner(tmp_path: Path) -> CliRunner:
    """Create an isolated CLI runner with temporary working directory."""
    return CliRunner(env={"HOME": str(tmp_path)})


# Automatic test marking based on directory structure


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:  # noqa: ARG001
    """
    Automatically mark tests based on their directory structure.

    This function automatically applies pytest markers to tests based on their location
    within the test directory structure. It's designed to be easily extensible for
    future marking needs.

    Args:
        config: pytest configuration object (unused but required by pytest)
        items: list of collected test items

    """
    # Define directory-based marking rules
    # Each entry maps a directory path pattern to a list of markers to apply
    directory_markers = {
        # Mark all regex tests as slow (they take ~54 seconds for 169 tests)
        "unit/process_scripts/regex": ["slow"],
        # Future extensions can be added here:
        # "integration/workflows": ["integration", "slow"],
        # "e2e": ["e2e", "slow"],
        # "performance": ["performance", "slow"],
        # "unit/large_datasets": ["slow"],
    }

    # Process each test item
    for item in items:
        # Get the test file path relative to the tests directory
        test_file_path = Path(item.fspath)
        tests_dir = Path(__file__).parent  # This is the tests/ directory

        try:
            # Get relative path from tests/ directory
            relative_path = test_file_path.relative_to(tests_dir)
            relative_dir = str(relative_path.parent)

            # Normalize path separators for cross-platform compatibility
            relative_dir = relative_dir.replace("\\", "/")

            # Apply markers based on directory patterns
            for dir_pattern, markers in directory_markers.items():
                if _path_matches_pattern(relative_dir, dir_pattern):
                    for marker_name in markers:
                        # Add the marker to the test item
                        marker = getattr(pytest.mark, marker_name)
                        item.add_marker(marker)

        except ValueError:
            # Path is not relative to tests directory - skip marking
            continue


def _path_matches_pattern(path: str, pattern: str) -> bool:
    """
    Check if a path matches a given pattern.

    This function supports exact matches and can be extended to support
    more sophisticated pattern matching in the future.

    Args:
        path: The path to check (e.g., "unit/process_scripts/regex/windows")
        pattern: The pattern to match against (e.g., "unit/process_scripts/regex")

    Returns:
        True if the path matches the pattern, False otherwise

    """
    # For now, use startswith for directory matching
    # This allows subdirectories to inherit markers from parent directories
    return path.startswith(pattern)


# Alternative implementation for exact directory matching:
def _path_matches_pattern_exact(path: str, pattern: str) -> bool:
    """
    Check if a path exactly matches a pattern or is a subdirectory of it.

    This is an alternative implementation that can be used if more precise
    control over directory matching is needed.
    """
    path_parts = path.split("/")
    pattern_parts = pattern.split("/")

    # Pattern must be shorter or equal length to path
    if len(pattern_parts) > len(path_parts):
        return False

    # All pattern parts must match the beginning of the path
    return path_parts[: len(pattern_parts)] == pattern_parts
