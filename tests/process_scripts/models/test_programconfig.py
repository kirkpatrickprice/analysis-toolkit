from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig


@pytest.fixture
def mock_file_system() -> Generator[dict[str, MagicMock | AsyncMock], Any, None]:
    """Mock file system for testing."""
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
def valid_config_params() -> dict[str, str]:
    """Return valid parameters for creating a ProgramConfig instance."""
    return {
        "audit_config_file": "audit-all.yaml",
        "source_files_path": "testdata/",
        "source_files_spec": "*.txt",
        "out_path": "results/",
    }


class TestProgramConfig:
    """Tests for the ProgramConfig class."""

    def test_init_with_valid_params(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,  # noqa: ARG002
    ) -> None:
        """Test initialization with valid parameters."""
        config = ProgramConfig(**valid_config_params)

        assert isinstance(config.program_path, Path)
        assert isinstance(config.config_path, Path)
        assert config.source_files_spec == "*.txt"
        assert config.out_path == "results/"
        assert config.list_audit_configs is False
        assert config.list_sections is False
        assert config.list_source_files is False
        assert config.list_systems is False
        assert config.verbose is False

    def test_audit_config_file_validator_success(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,  # noqa: ARG002
    ) -> None:
        """Test successful validation of audit_config_file."""
        config = ProgramConfig(**valid_config_params)
        assert isinstance(config.audit_config_file, Path)

    def test_audit_config_file_validator_none(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,  # noqa: ARG002
    ) -> None:
        """Test validation error when audit_config_file is None."""
        params = valid_config_params.copy()
        params["audit_config_file"] = None

        with pytest.raises(
            ValidationError,
            match="Audit configuration file is required",
        ):
            ProgramConfig(**params)

    def test_audit_config_file_validator_nonexistent(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,
    ) -> None:
        """Test validation error when audit_config_file doesn't exist."""
        mock_file_system["is_file"].return_value = False

        with pytest.raises(ValidationError, match="Path .* is not a file"):
            ProgramConfig(**valid_config_params)

    def test_source_path_validator_success(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,  # noqa: ARG002
    ) -> None:
        """Test successful validation of source_files_path."""
        config = ProgramConfig(**valid_config_params)
        assert isinstance(config.source_files_path, Path)
        assert config.source_files_path.is_absolute()

    def test_source_path_validator_nonexistent(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,
    ) -> None:
        """Test validation error when source_files_path doesn't exist."""
        mock_file_system["exists"].return_value = False

        with pytest.raises(
            ValidationError,
            match="Source files path .* does not exist",
        ):
            ProgramConfig(**valid_config_params)

    def test_source_files_spec_validator_success(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,  # noqa: ARG002
    ) -> None:
        """Test successful validation of source_files_spec."""
        config = ProgramConfig(**valid_config_params)
        assert config.source_files_spec == "*.txt"

    def test_source_files_spec_validator_empty(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,  # noqa: ARG002
    ) -> None:
        """Test validation error when source_files_spec is empty."""
        params = valid_config_params.copy()
        params["source_files_spec"] = ""

        with pytest.raises(ValidationError, match="String cannot be empty"):
            ProgramConfig(**params)

    def test_out_path_validator_success(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,  # noqa: ARG002
    ) -> None:
        """Test successful validation of out_path."""
        config = ProgramConfig(**valid_config_params)
        assert config.out_path == "results/"

    def test_out_path_validator_empty(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,  # noqa: ARG002
    ) -> None:
        """Test validation error when out_path is empty."""
        params = valid_config_params.copy()
        params["out_path"] = ""

        with pytest.raises(ValidationError, match="String cannot be empty"):
            ProgramConfig(**params)

    def test_results_path_computed_property(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,  # noqa: ARG002
    ) -> None:
        """Test the results_path computed property."""
        config = ProgramConfig(**valid_config_params)
        expected_path = (
            Path(valid_config_params["source_files_path"]).absolute()
            / valid_config_params["out_path"]
        )

        assert config.results_path == expected_path
        assert config.results_path.is_absolute()

    def test_ensure_results_path_exists_when_exists(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,
    ) -> None:
        """Test ensure_results_path_exists when the path already exists."""
        mock_file_system["exists"].return_value = True

        config = ProgramConfig(**valid_config_params)
        config.ensure_results_path_exists()

        # Path exists, so mkdir should not be called
        mock_file_system["mkdir"].assert_not_called()

    def test_ensure_results_path_exists_when_not_exists(
        self,
        valid_config_params: dict[str, str | Path | bool],
        mock_file_system: callable,
    ) -> None:
        """Test ensure_results_path_exists when the path doesn't exist."""
        # Configure mock to return True for validation calls, then False for the results path check
        # Add extra True values to handle any additional calls in CI environments
        mock_file_system["exists"].side_effect = [True, True, True, False, True, True]

        config = ProgramConfig(**valid_config_params)
        config.ensure_results_path_exists()

        # Path doesn't exist, so mkdir should be called
        mock_file_system["mkdir"].assert_called_once_with(parents=True, exist_ok=True)
