"""Unit tests for the path utilities service."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from kp_analysis_toolkit.core.services.file_processing.path_utilities import (
    PathUtilitiesService,
)
from kp_analysis_toolkit.core.services.timestamp import TimeStamper

# Constants for test validation
EXPECTED_CALL_COUNT = 3


@pytest.mark.file_processing
@pytest.mark.core
@pytest.mark.unit
class TestPathUtilitiesService:
    """Test the PathUtilitiesService class."""

    def test_path_utilities_service_initialization(self) -> None:
        """Test that PathUtilitiesService can be initialized."""
        # Create mock for timestamp service
        timestamp_service = Mock(spec=TimeStamper)

        # Initialize service
        service = PathUtilitiesService(timestamp_service=timestamp_service)

        assert service.timestamp_service is timestamp_service

    def test_generate_timestamped_path_basic(self) -> None:
        """Test basic timestamped path generation."""
        # Create mock timestamp service
        timestamp_service = Mock(spec=TimeStamper)
        timestamp_service.get_timestamp.return_value = "20231225-143000"

        # Initialize service
        service = PathUtilitiesService(timestamp_service=timestamp_service)

        # Test path generation
        result = service.generate_timestamped_path(
            base_path="/test/dir",
            filename_prefix="output",
            extension=".xlsx",
        )

        # Verify result
        expected = Path("/test/dir/output_20231225-143000.xlsx")
        assert result == expected

        # Verify timestamp service was called
        timestamp_service.get_timestamp.assert_called_once()

    def test_generate_timestamped_path_with_path_object(self) -> None:
        """Test timestamped path generation with Path object as base_path."""
        # Create mock timestamp service
        timestamp_service = Mock(spec=TimeStamper)
        timestamp_service.get_timestamp.return_value = "20240101-120000"

        # Initialize service
        service = PathUtilitiesService(timestamp_service=timestamp_service)

        # Test with Path object
        base_path = Path("/results")
        result = service.generate_timestamped_path(
            base_path=base_path,
            filename_prefix="report",
            extension=".txt",
        )

        # Verify result
        expected = Path("/results/report_20240101-120000.txt")
        assert result == expected

    def test_generate_timestamped_path_different_extensions(self) -> None:
        """Test timestamped path generation with different file extensions."""
        # Create mock timestamp service
        timestamp_service = Mock(spec=TimeStamper)
        timestamp_service.get_timestamp.return_value = "20240115-093045"

        # Initialize service
        service = PathUtilitiesService(timestamp_service=timestamp_service)

        # Test various extensions
        test_cases = [
            (".csv", "data", "data_20240115-093045.csv"),
            (".json", "config", "config_20240115-093045.json"),
            (".log", "error", "error_20240115-093045.log"),
            ("", "backup", "backup_20240115-093045"),  # No extension
        ]

        for extension, prefix, expected_filename in test_cases:
            result = service.generate_timestamped_path(
                base_path="/test",
                filename_prefix=prefix,
                extension=extension,
            )
            expected = Path(f"/test/{expected_filename}")
            assert result == expected

    def test_generate_timestamped_path_nested_directory(self) -> None:
        """Test timestamped path generation with nested directory structure."""
        # Create mock timestamp service
        timestamp_service = Mock(spec=TimeStamper)
        timestamp_service.get_timestamp.return_value = "20240201-154500"

        # Initialize service
        service = PathUtilitiesService(timestamp_service=timestamp_service)

        # Test with nested path
        result = service.generate_timestamped_path(
            base_path="/project/outputs/results",
            filename_prefix="analysis",
            extension=".xlsx",
        )

        # Verify result
        expected = Path("/project/outputs/results/analysis_20240201-154500.xlsx")
        assert result == expected

    def test_generate_timestamped_path_multiple_calls(self) -> None:
        """Test that multiple calls to generate path use fresh timestamps."""
        # Create mock timestamp service
        timestamp_service = Mock(spec=TimeStamper)
        timestamp_service.get_timestamp.side_effect = [
            "20240301-100000",
            "20240301-100001",
            "20240301-100002",
        ]

        # Initialize service
        service = PathUtilitiesService(timestamp_service=timestamp_service)

        # Generate multiple paths
        results = []
        for i in range(EXPECTED_CALL_COUNT):
            result = service.generate_timestamped_path(
                base_path="/outputs",
                filename_prefix=f"file{i}",
                extension=".txt",
            )
            results.append(result)

        # Verify each call got a unique timestamp
        expected = [
            Path("/outputs/file0_20240301-100000.txt"),
            Path("/outputs/file1_20240301-100001.txt"),
            Path("/outputs/file2_20240301-100002.txt"),
        ]
        assert results == expected

        # Verify timestamp service was called expected number of times
        assert timestamp_service.get_timestamp.call_count == EXPECTED_CALL_COUNT

    def test_generate_timestamped_path_special_characters(self) -> None:
        """Test timestamped path generation with special characters in prefix."""
        # Create mock timestamp service
        timestamp_service = Mock(spec=TimeStamper)
        timestamp_service.get_timestamp.return_value = "20240315-083000"

        # Initialize service
        service = PathUtilitiesService(timestamp_service=timestamp_service)

        # Test with special characters in prefix
        result = service.generate_timestamped_path(
            base_path="/temp",
            filename_prefix="test-file_v2",
            extension=".data",
        )

        # Verify result (special characters should be preserved)
        expected = Path("/temp/test-file_v2_20240315-083000.data")
        assert result == expected

    def test_protocol_compliance(self) -> None:
        """Test that PathUtilitiesService implements expected behavior."""
        # Create mock timestamp service
        timestamp_service = Mock(spec=TimeStamper)
        timestamp_service.get_timestamp.return_value = "20240401-120000"

        # Initialize service
        service = PathUtilitiesService(timestamp_service=timestamp_service)

        # Should have generate_timestamped_path method
        assert hasattr(service, "generate_timestamped_path")
        assert callable(service.generate_timestamped_path)

        # Method should return Path object
        result = service.generate_timestamped_path("/test", "file", ".txt")
        assert isinstance(result, Path)
