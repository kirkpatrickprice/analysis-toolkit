from pathlib import Path
from typing import Literal

import pytest
from pydantic import BaseModel, ConfigDict

from kp_analysis_toolkit.process_scripts.models.base import FileModel
from kp_analysis_toolkit.utils import get_file_encoding


class TestFile(BaseModel, FileModel):
    """Test cases for FileModel."""

    model_config: ConfigDict = FileModel.model_config.copy()


class TestFileModel:
    """Test cases for FileModel."""

    def test_init_with_valid_file(self, tmp_path: Path | str) -> None:
        """Test initialization with a valid file path."""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        # Initialize FileModel with the file
        model = TestFile(file=test_file)

        # Check that the file is correctly set
        assert model.file == test_file.absolute()
        assert model.encoding is None
        assert model.file_hash is None

    def test_init_with_nonexistent_file(self) -> None:
        """Test initialization with a non-existent file raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            TestFile(file=Path("nonexistent_file.txt"))
        assert "does not exist" in str(excinfo.value)

    def test_validate_file_method(self, tmp_path: Path | str) -> None:
        """Test the validate_file class method."""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        # Validate the file
        validated_path = TestFile.validate_file(test_file)
        assert validated_path == test_file.absolute()

    def test_read_line_with_encoding(self, tmp_path: Path | str) -> None:
        """Test read_line method with specified encoding."""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_content = "Line 1\nLine 2\nLine 3"
        test_file.write_text(test_content)

        # Initialize FileModel with the file and specify encoding directly
        model = TestFile(file=test_file, encoding="utf-8")

        # Read lines and check content
        lines = list(model.read_line())
        assert len(lines) == 3  # noqa: PLR2004
        assert lines[0] == "Line 1\n"
        assert lines[1] == "Line 2\n"
        assert lines[2] == "Line 3"
        assert model.encoding == "utf-8"

    def test_read_line_without_encoding(
        self,
        tmp_path: Path | str,
        monkeypatch,  # noqa: ANN001
    ) -> None:
        """Test read_line method with auto-detected encoding."""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_content = "Line 1\nLine 2\nLine 3"
        test_file.write_text(test_content)

        # Mock the detect_encoding function
        def mock_detect_encoding(file_path: Path | str) -> Literal["ascii"]:  # noqa: ARG001
            return "ascii"

        monkeypatch.setattr(get_file_encoding, "detect_encoding", mock_detect_encoding)

        # Initialize FileModel without specifying encoding
        model = TestFile(file=test_file)

        # Read lines and check that encoding was auto-detected
        list(model.read_line())
        assert model.encoding == "ascii"

    def test_generate_file_hash(self, tmp_path: Path | str) -> None:
        """Test generate_file_hash method."""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_content = "Test content for hashing"
        test_file.write_text(test_content, encoding="utf-8")

        # Initialize FileModel with the file
        model = TestFile(file=test_file)

        # Generate hash
        file_hash = model.generate_file_hash()

        # Check that the hash is a non-empty string
        assert isinstance(file_hash, str)
        assert len(file_hash) > 0

        # Check that the hash is stored in the model
        assert model.file_hash == file_hash

        # Create a model with different content and check that hash differs
        different_file = tmp_path / "different.txt"
        different_file.write_text("Different content", encoding="utf-8")
        different_model = TestFile(file=different_file)
        different_hash = different_model.generate_file_hash()

        assert file_hash != different_hash

    def test_same_content_same_hash(self, tmp_path: Path | str) -> None:
        """Test that identical file content produces identical hashes."""
        # Create two files with the same content
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "Same content in both files"

        file1.write_text(content)
        file2.write_text(content)

        # Generate hashes
        model1 = TestFile(file=file1)
        model2 = TestFile(file=file2)

        hash1 = model1.generate_file_hash()
        hash2 = model2.generate_file_hash()

        # Hashes should be identical
        assert hash1 == hash2
