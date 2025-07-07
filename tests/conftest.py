# tests/conftest.py
"""Shared pytest configuration and fixtures."""

from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

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


# Add other shared fixtures as needed
