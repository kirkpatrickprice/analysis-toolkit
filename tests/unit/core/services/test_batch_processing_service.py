# AI-GEN: claude-3.5-sonnet|2025-01-19|batch-processing-service|reviewed:yes
"""Tests for batch processing service implementation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from kp_analysis_toolkit.core.services.batch_processing.models import (
    BatchProcessingConfig,
    BatchResult,
    ErrorHandlingStrategy,
)
from kp_analysis_toolkit.core.services.batch_processing.service import (
    DefaultBatchProcessingService,
)

# Test constants
TEST_FILE_COUNT_SMALL = 2
TEST_FILE_COUNT_MEDIUM = 3
EXPECTED_SUCCESS_RATE = 100.0


class TestDefaultBatchProcessingService:
    """Test the DefaultBatchProcessingService class."""

    def test_batch_processing_service_initialization(self) -> None:
        """Test that DefaultBatchProcessingService can be initialized."""
        # Create mocks for dependencies
        rich_output = Mock()
        file_processing = Mock()

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        assert service.rich_output is rich_output
        assert service.file_processing is file_processing
        assert service.config_extractor is not None

    def test_process_files_with_service_success(self, tmp_path: Path) -> None:
        """Test successful file processing with service method."""
        # Create test files
        files = []
        for i in range(TEST_FILE_COUNT_MEDIUM):
            file_path = tmp_path / f"test_file_{i}.txt"
            file_path.write_text(f"Content of file {i}")
            files.append(file_path)

        # Create mocks
        rich_output = Mock()
        rich_output.progress.return_value.__enter__ = Mock()
        rich_output.progress.return_value.__exit__ = Mock()
        rich_output.progress.return_value.add_task.return_value = "task_id"
        rich_output.progress.return_value.update = Mock()
        file_processing = Mock()

        # Create config creator
        def create_config(file_path: Path) -> Mock:
            config = Mock()
            config.input_file = file_path
            config.output_file = file_path.with_suffix(".out")
            return config

        # Create service method
        def process_file(input_file: Path, output_file: Path) -> None:
            output_file.write_text(f"Processed: {input_file.read_text()}")

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Test processing
        result = service.process_files_with_service(
            file_list=files,
            config_creator=create_config,
            service_method=process_file,
        )

        # Verify results
        assert isinstance(result, BatchResult)
        assert result.total_files == TEST_FILE_COUNT_MEDIUM
        assert result.successful == TEST_FILE_COUNT_MEDIUM
        assert result.failed == 0
        assert result.success_rate == EXPECTED_SUCCESS_RATE

        # Verify all output files were created
        for file_path in files:
            output_file = file_path.with_suffix(".out")
            assert output_file.exists()
            assert "Processed:" in output_file.read_text()

    def test_process_files_with_service_empty_list(self) -> None:
        """Test processing with empty file list."""
        # Create mocks
        rich_output = Mock()
        file_processing = Mock()

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Test processing empty list
        result = service.process_files_with_service(
            file_list=[],
            config_creator=Mock(),
            service_method=Mock(),
        )

        # Verify results
        assert result.total_files == 0
        assert result.successful == 0
        assert result.failed == 0
        rich_output.warning.assert_called_once_with("No files to process")

    def test_process_files_with_service_error_continue(self, tmp_path: Path) -> None:
        """Test error handling with CONTINUE_ON_ERROR strategy."""
        # Create test files
        files = []
        for i in range(TEST_FILE_COUNT_MEDIUM):
            file_path = tmp_path / f"test_file_{i}.txt"
            file_path.write_text(f"Content of file {i}")
            files.append(file_path)

        # Create mocks
        rich_output = Mock()
        rich_output.progress.return_value.__enter__ = Mock()
        rich_output.progress.return_value.__exit__ = Mock()
        rich_output.progress.return_value.add_task.return_value = "task_id"
        rich_output.progress.return_value.update = Mock()
        file_processing = Mock()

        # Create config creator
        def create_config(file_path: Path) -> Mock:
            config = Mock()
            config.input_file = file_path
            config.output_file = file_path.with_suffix(".out")
            return config

        # Create failing service method
        def failing_process(input_file: Path, output_file: Path) -> None:
            if "file_1" in str(input_file):
                msg = f"Failed to process {input_file}"
                raise ValueError(msg)
            output_file.write_text(f"Processed: {input_file.read_text()}")

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Test processing with errors
        config = BatchProcessingConfig(
            error_handling=ErrorHandlingStrategy.CONTINUE_ON_ERROR,
        )
        result = service.process_files_with_service(
            file_list=files,
            config_creator=create_config,
            service_method=failing_process,
            config=config,
        )

        # Verify results
        assert result.total_files == TEST_FILE_COUNT_MEDIUM
        assert result.successful == TEST_FILE_COUNT_SMALL  # 2 files succeeded
        assert result.failed == 1  # 1 file failed
        assert len(result.errors) == 1

    def test_process_files_with_service_error_fail_fast(self, tmp_path: Path) -> None:
        """Test error handling with FAIL_FAST strategy."""
        # Create test files
        files = []
        for i in range(TEST_FILE_COUNT_MEDIUM):
            file_path = tmp_path / f"test_file_{i}.txt"
            file_path.write_text(f"Content of file {i}")
            files.append(file_path)

        # Create mocks
        rich_output = Mock()
        rich_output.progress.return_value.__enter__ = Mock()
        rich_output.progress.return_value.__exit__ = Mock(
            return_value=False,
        )  # Don't suppress exceptions
        rich_output.progress.return_value.add_task.return_value = "task_id"
        rich_output.progress.return_value.update = Mock()
        file_processing = Mock()

        # Create config creator
        def create_config(file_path: Path) -> Mock:
            config = Mock()
            config.input_file = file_path
            config.output_file = file_path.with_suffix(".out")
            return config

        # Create failing service method
        def failing_process(input_file: Path, _output_file: Path) -> None:
            msg = f"Failed to process {input_file}"
            raise ValueError(msg)

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Test processing with fail fast
        config = BatchProcessingConfig(error_handling=ErrorHandlingStrategy.FAIL_FAST)

        with pytest.raises(ValueError):  # Our implementation raises ValueError directly
            service.process_files_with_service(
                file_list=files,
                config_creator=create_config,
                service_method=failing_process,
                config=config,
            )

    def test_process_files_with_service_collect_errors(self, tmp_path: Path) -> None:
        """Test error handling with COLLECT_ERRORS strategy."""
        # Create test files
        files = []
        for i in range(TEST_FILE_COUNT_MEDIUM):
            file_path = tmp_path / f"test_file_{i}.txt"
            file_path.write_text(f"Content of file {i}")
            files.append(file_path)

        # Create mocks
        rich_output = Mock()
        rich_output.progress.return_value.__enter__ = Mock()
        rich_output.progress.return_value.__exit__ = Mock()
        rich_output.progress.return_value.add_task.return_value = "task_id"
        rich_output.progress.return_value.update = Mock()
        file_processing = Mock()

        # Create config creator
        def create_config(file_path: Path) -> Mock:
            config = Mock()
            config.input_file = file_path
            config.output_file = file_path.with_suffix(".out")
            return config

        # Create failing service method
        def failing_process(input_file: Path, _output_file: Path) -> None:
            msg = f"Failed to process {input_file}"
            raise ValueError(msg)

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Test processing with collect errors
        config = BatchProcessingConfig(
            error_handling=ErrorHandlingStrategy.COLLECT_ERRORS,
        )
        result = service.process_files_with_service(
            file_list=files,
            config_creator=create_config,
            service_method=failing_process,
            config=config,
        )

        # Verify results
        assert result.total_files == TEST_FILE_COUNT_MEDIUM
        assert result.successful == 0
        assert result.failed == TEST_FILE_COUNT_MEDIUM
        assert len(result.errors) == TEST_FILE_COUNT_MEDIUM

    def test_create_file_conversion_success_formatter(self) -> None:
        """Test creation of success message formatter."""
        # Create mocks
        rich_output = Mock()
        file_processing = Mock()

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Test formatter creation
        formatter = service.create_file_conversion_success_formatter("Converted")

        # Create mock config with proper structure
        config = Mock()
        config.input_file = Path("input.txt")
        config.output_file = Path("output.txt")

        # Test formatter
        result = formatter(Path("input.txt"), config)
        assert result == "Converted: input.txt -> output.txt"

    def test_create_file_conversion_success_formatter_fallback(self) -> None:
        """Test success formatter fallback for malformed config."""
        # Create mocks
        rich_output = Mock()
        file_processing = Mock()

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Test formatter creation
        formatter = service.create_file_conversion_success_formatter("Converted")

        # Create malformed config (missing attributes)
        bad_config = Mock()
        del bad_config.input_file  # Remove the attribute to trigger fallback

        # Test formatter fallback
        result = formatter(Path("input.txt"), bad_config)
        assert result == "Converted: input.txt"

    @patch("kp_analysis_toolkit.cli.utils.path_helpers.discover_files_by_pattern")
    def test_discover_and_process_files_success(
        self,
        mock_discover: Mock,
        tmp_path: Path,
    ) -> None:
        """Test successful file discovery and processing."""
        # Create test files
        files = []
        for i in range(TEST_FILE_COUNT_SMALL):
            file_path = tmp_path / f"test_{i}.csv"
            file_path.write_text(f"data,{i}")
            files.append(file_path)

        # Mock file discovery
        mock_discover.return_value = files

        # Create mocks
        rich_output = Mock()
        rich_output.progress.return_value.__enter__ = Mock()
        rich_output.progress.return_value.__exit__ = Mock()
        rich_output.progress.return_value.add_task.return_value = "task_id"
        rich_output.progress.return_value.update = Mock()
        file_processing = Mock()

        # Create config creator and service method
        def create_config(file_path: Path) -> Mock:
            config = Mock()
            config.input_file = file_path
            config.output_file = file_path.with_suffix(".out")
            return config

        def process_file(input_file: Path, output_file: Path) -> None:
            output_file.write_text(f"Processed: {input_file.read_text()}")

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Test discovery and processing
        result = service.discover_and_process_files(
            base_path=tmp_path,
            file_pattern="*.csv",
            config_creator=create_config,
            service_method=process_file,
        )

        # Verify results
        assert result.total_files == TEST_FILE_COUNT_SMALL
        assert result.successful == TEST_FILE_COUNT_SMALL
        assert result.failed == 0
        mock_discover.assert_called_once_with(tmp_path, "*.csv", recursive=True)

    @patch("kp_analysis_toolkit.cli.utils.path_helpers.discover_files_by_pattern")
    def test_discover_and_process_files_no_files_found(
        self,
        mock_discover: Mock,
        tmp_path: Path,
    ) -> None:
        """Test file discovery when no files are found."""
        # Mock empty file discovery
        mock_discover.return_value = []

        # Create mocks
        rich_output = Mock()
        file_processing = Mock()

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Test discovery with no files
        result = service.discover_and_process_files(
            base_path=tmp_path,
            file_pattern="*.csv",
            config_creator=Mock(),
            service_method=Mock(),
        )

        # Verify results
        assert result.total_files == 0
        rich_output.warning.assert_called_once()

    def test_success_message_formatter_integration(self, tmp_path: Path) -> None:
        """Test integration of success message formatter."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create mocks
        rich_output = Mock()
        rich_output.progress.return_value.__enter__ = Mock()
        rich_output.progress.return_value.__exit__ = Mock()
        rich_output.progress.return_value.add_task.return_value = "task_id"
        rich_output.progress.return_value.update = Mock()
        file_processing = Mock()

        # Initialize service
        service = DefaultBatchProcessingService(
            rich_output=rich_output,
            file_processing=file_processing,
        )

        # Create config creator and service method
        def create_config(file_path: Path) -> Mock:
            config = Mock()
            config.input_file = file_path
            config.output_file = file_path.with_suffix(".out")
            return config

        def process_file(input_file: Path, output_file: Path) -> None:
            output_file.write_text(f"Processed: {input_file.read_text()}")

        # Create custom success formatter
        formatter = service.create_file_conversion_success_formatter("Converted")
        config = BatchProcessingConfig(
            operation_description="Converting files",
            success_message_formatter=formatter,
        )

        # Test processing with custom formatter
        result = service.process_files_with_service(
            file_list=[test_file],
            config_creator=create_config,
            service_method=process_file,
            config=config,
        )

        # Verify results
        assert result.successful == 1
        assert len(result.success_details) == 1
        success_msg = result.success_details[0][1]
        assert success_msg == "Converted: test.txt -> test.out"


# END AI-GEN
