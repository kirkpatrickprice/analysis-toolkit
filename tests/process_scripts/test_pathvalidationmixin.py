from pathlib import Path

import pytest

from kp_analysis_toolkit.process_scripts.models.base import PathValidationMixin


class TestPathValidationMixin:
    """Tests for the PathValidationMixin class."""

    def test_validate_path_exists_with_existing_path(self, tmp_path) -> None:  # noqa: ANN001
        """Test validate_path_exists with an existing path."""
        # Test with a Path object
        result: Path = PathValidationMixin.validate_path_exists(tmp_path)
        assert result == tmp_path.absolute()

        # Test with a string value
        result = PathValidationMixin.validate_path_exists(str(tmp_path))
        assert result == tmp_path.absolute()

    def test_validate_path_exists_with_nonexistent_path(self) -> None:
        """Test validate_path_exists with a non-existent path."""
        non_existent_path = Path("/path/does/not/exist")

        with pytest.raises(ValueError) as excinfo:
            PathValidationMixin.validate_path_exists(non_existent_path)
        assert f"Path {non_existent_path} does not exist" in str(excinfo.value)

        # Test with a string
        with pytest.raises(ValueError) as excinfo:
            PathValidationMixin.validate_path_exists(str(non_existent_path))
        assert f"Path {non_existent_path} does not exist" in str(excinfo.value)

    def test_validate_file_exists_with_existing_file(self, tmp_path) -> None:  # noqa: ANN001
        """Test validate_file_exists with an existing file."""
        # Create a test file
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")

        # Test with a Path object
        result = PathValidationMixin.validate_file_exists(test_file)
        assert result == test_file.absolute()

        # Test with a string
        result = PathValidationMixin.validate_file_exists(str(test_file))
        assert result == test_file.absolute()

    def test_validate_file_exists_with_directory(self, tmp_path) -> None:  # noqa: ANN001
        """Test validate_file_exists with a directory (should fail)."""
        with pytest.raises(ValueError) as excinfo:
            PathValidationMixin.validate_file_exists(tmp_path)
        assert f"Path {tmp_path.absolute()} is not a file" in str(excinfo.value)

    def test_validate_file_exists_with_nonexistent_file(self) -> None:
        """Test validate_file_exists with a non-existent file."""
        non_existent_file = Path("/path/to/non_existent_file.txt")

        with pytest.raises(ValueError) as excinfo:
            PathValidationMixin.validate_file_exists(non_existent_file)
        assert f"Path {non_existent_file} does not exist" in str(excinfo.value)

    def test_validate_directory_exists_with_existing_directory(self, tmp_path) -> None:  # noqa: ANN001
        """Test validate_directory_exists with an existing directory."""
        # Create a test directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Test with a Path object
        result = PathValidationMixin.validate_directory_exists(test_dir)
        assert result == test_dir.absolute()

        # Test with a string
        result = PathValidationMixin.validate_directory_exists(str(test_dir))
        assert result == test_dir.absolute()

    def test_validate_directory_exists_with_file(self, tmp_path) -> None:  # noqa: ANN001
        """Test validate_directory_exists with a file (should fail)."""
        # Create a test file
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")

        with pytest.raises(ValueError) as excinfo:
            PathValidationMixin.validate_directory_exists(test_file)
        assert f"Path {test_file.absolute()} is not a directory" in str(excinfo.value)

    def test_validate_directory_exists_with_nonexistent_directory(self) -> None:
        """Test validate_directory_exists with a non-existent directory."""
        non_existent_dir = Path("/path/to/non_existent_dir")

        with pytest.raises(ValueError) as excinfo:
            PathValidationMixin.validate_directory_exists(non_existent_dir)
        assert f"Path {non_existent_dir} does not exist" in str(excinfo.value)
