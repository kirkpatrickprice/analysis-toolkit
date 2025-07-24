"""Unit tests for the file discovery service."""

from pathlib import Path

import pytest

from kp_analysis_toolkit.core.services.file_processing.discovery import (
    FileDiscoveryService,
)

# Constants for test validation
EXPECTED_FILE_COUNT_TWO = 2
EXPECTED_FILE_COUNT_THREE = 3
EXPECTED_FILE_COUNT_FOUR = 4


@pytest.mark.file_processing
@pytest.mark.core
@pytest.mark.unit
class TestFileDiscoveryService:
    """Test the FileDiscoveryService class."""

    def test_file_discovery_service_initialization(self) -> None:
        """Test that FileDiscoveryService can be initialized."""
        service = FileDiscoveryService()
        assert service is not None
        assert hasattr(service, "discover_files_by_pattern")

    def test_discover_files_by_pattern_default(self, tmp_path: Path) -> None:
        """Test basic file discovery with default pattern."""
        # Create test files
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.csv").write_text("content2")
        (tmp_path / "file3.json").write_text("content3")

        # Initialize service
        service = FileDiscoveryService()

        # Test discovery with default pattern (*)
        results = service.discover_files_by_pattern(tmp_path)

        # Should find all files
        assert len(results) == EXPECTED_FILE_COUNT_THREE
        result_names = {p.name for p in results}
        assert result_names == {"file1.txt", "file2.csv", "file3.json"}

        # All results should be Path objects
        for result in results:
            assert isinstance(result, Path)
            assert result.is_file()

    def test_discover_files_by_pattern_specific_extension(self, tmp_path: Path) -> None:
        """Test file discovery with specific file extension pattern."""
        # Create test files with different extensions
        (tmp_path / "data1.csv").write_text("csv content")
        (tmp_path / "data2.csv").write_text("csv content")
        (tmp_path / "config.json").write_text("json content")
        (tmp_path / "readme.txt").write_text("text content")

        # Initialize service
        service = FileDiscoveryService()

        # Test discovery for CSV files only
        csv_results = service.discover_files_by_pattern(tmp_path, "*.csv")

        # Should find only CSV files
        assert len(csv_results) == EXPECTED_FILE_COUNT_TWO
        csv_names = {p.name for p in csv_results}
        assert csv_names == {"data1.csv", "data2.csv"}

        # Test discovery for JSON files only
        json_results = service.discover_files_by_pattern(tmp_path, "*.json")

        # Should find only JSON file
        assert len(json_results) == 1
        assert json_results[0].name == "config.json"

    def test_discover_files_by_pattern_no_matches(self, tmp_path: Path) -> None:
        """Test file discovery when no files match the pattern."""
        # Create test files
        (tmp_path / "file1.txt").write_text("content")
        (tmp_path / "file2.csv").write_text("content")

        # Initialize service
        service = FileDiscoveryService()

        # Test discovery for non-existent pattern
        results = service.discover_files_by_pattern(tmp_path, "*.xyz")

        # Should return empty list
        assert results == []
        assert isinstance(results, list)

    def test_discover_files_by_pattern_recursive_false(self, tmp_path: Path) -> None:
        """Test non-recursive file discovery."""
        # Create files in root directory
        (tmp_path / "root1.txt").write_text("content")
        (tmp_path / "root2.txt").write_text("content")

        # Create subdirectory with files
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "sub1.txt").write_text("content")
        (subdir / "sub2.txt").write_text("content")

        # Initialize service
        service = FileDiscoveryService()

        # Test non-recursive discovery
        results = service.discover_files_by_pattern(tmp_path, "*.txt", recursive=False)

        # Should find only root-level files
        assert len(results) == EXPECTED_FILE_COUNT_TWO
        result_names = {p.name for p in results}
        assert result_names == {"root1.txt", "root2.txt"}

        # Verify all results are in the root directory
        for result in results:
            assert result.parent == tmp_path

    def test_discover_files_by_pattern_recursive_true(self, tmp_path: Path) -> None:
        """Test recursive file discovery."""
        # Create files in root directory
        (tmp_path / "root1.txt").write_text("content")
        (tmp_path / "root2.txt").write_text("content")

        # Create nested subdirectories with files
        subdir1 = tmp_path / "subdir1"
        subdir1.mkdir()
        (subdir1 / "sub1.txt").write_text("content")

        subdir2 = subdir1 / "nested"
        subdir2.mkdir()
        (subdir2 / "nested.txt").write_text("content")

        # Initialize service
        service = FileDiscoveryService()

        # Test recursive discovery
        results = service.discover_files_by_pattern(tmp_path, "*.txt", recursive=True)

        # Should find all files recursively
        assert len(results) == EXPECTED_FILE_COUNT_FOUR
        result_names = {p.name for p in results}
        assert result_names == {"root1.txt", "root2.txt", "sub1.txt", "nested.txt"}

    def test_discover_files_by_pattern_with_path_string(self, tmp_path: Path) -> None:
        """Test file discovery with string path instead of Path object."""
        # Create test files
        (tmp_path / "test1.txt").write_text("content")
        (tmp_path / "test2.txt").write_text("content")

        # Initialize service
        service = FileDiscoveryService()

        # Test with string path
        results = service.discover_files_by_pattern(str(tmp_path), "*.txt")

        # Should work the same as with Path object
        assert len(results) == EXPECTED_FILE_COUNT_TWO
        result_names = {p.name for p in results}
        assert result_names == {"test1.txt", "test2.txt"}

    def test_discover_files_by_pattern_complex_patterns(self, tmp_path: Path) -> None:
        """Test file discovery with complex glob patterns."""
        # Create test files with various names
        (tmp_path / "data_001.csv").write_text("content")
        (tmp_path / "data_002.csv").write_text("content")
        (tmp_path / "config.csv").write_text("content")
        (tmp_path / "backup_data.txt").write_text("content")

        # Initialize service
        service = FileDiscoveryService()

        # Test pattern matching files starting with "data_"
        results = service.discover_files_by_pattern(tmp_path, "data_*.csv")
        assert len(results) == EXPECTED_FILE_COUNT_TWO
        result_names = {p.name for p in results}
        assert result_names == {"data_001.csv", "data_002.csv"}

        # Test pattern matching files containing "data"
        results = service.discover_files_by_pattern(tmp_path, "*data*")
        assert len(results) == EXPECTED_FILE_COUNT_THREE
        result_names = {p.name for p in results}
        assert result_names == {"data_001.csv", "data_002.csv", "backup_data.txt"}

    def test_discover_files_by_pattern_nonexistent_path(self) -> None:
        """Test file discovery with non-existent base path."""
        # Initialize service
        service = FileDiscoveryService()

        # Test with non-existent path
        nonexistent_path = Path("/nonexistent/path/that/does/not/exist")

        with pytest.raises(ValueError, match="Path does not exist"):
            service.discover_files_by_pattern(nonexistent_path, "*.txt")

    def test_discover_files_by_pattern_file_instead_of_directory(
        self,
        tmp_path: Path,
    ) -> None:
        """Test file discovery when base path is a file, not a directory."""
        # Create a test file
        test_file = tmp_path / "testfile.txt"
        test_file.write_text("content")

        # Initialize service
        service = FileDiscoveryService()

        # Test with file path instead of directory
        with pytest.raises(ValueError, match="Path is not a directory"):
            service.discover_files_by_pattern(test_file, "*.txt")

    def test_discover_files_by_pattern_empty_directory(self, tmp_path: Path) -> None:
        """Test file discovery in empty directory."""
        # Create empty subdirectory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Initialize service
        service = FileDiscoveryService()

        # Test discovery in empty directory
        results = service.discover_files_by_pattern(empty_dir, "*")

        # Should return empty list
        assert results == []
        assert isinstance(results, list)

    def test_discover_files_by_pattern_directories_excluded(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that directories are excluded from file discovery results."""
        # Create files and directories
        (tmp_path / "file1.txt").write_text("content")
        (tmp_path / "file2.txt").write_text("content")
        (tmp_path / "subdir1").mkdir()
        (tmp_path / "subdir2").mkdir()

        # Initialize service
        service = FileDiscoveryService()

        # Test discovery - should only return files, not directories
        results = service.discover_files_by_pattern(tmp_path, "*")

        # Should find only files, not directories
        assert len(results) == EXPECTED_FILE_COUNT_TWO
        result_names = {p.name for p in results}
        assert result_names == {"file1.txt", "file2.txt"}

        # Verify all results are files
        for result in results:
            assert result.is_file()
            assert not result.is_dir()

    def test_protocol_compliance(self, tmp_path: Path) -> None:
        """Test that FileDiscoveryService implements expected protocol behavior."""
        # Create test file
        (tmp_path / "test.txt").write_text("content")

        # Initialize service
        service = FileDiscoveryService()

        # Should have discover_files_by_pattern method
        assert hasattr(service, "discover_files_by_pattern")
        assert callable(service.discover_files_by_pattern)

        # Method should return list of Path objects
        result = service.discover_files_by_pattern(tmp_path, "*.txt")
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Path)
