"""General purpose mock fixtures for testing."""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


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
