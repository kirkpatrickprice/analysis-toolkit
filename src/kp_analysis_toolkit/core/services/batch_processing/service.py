# AI-GEN: claude-3.5-sonnet|2025-01-19|batch-processing-service|reviewed:yes
"""Main batch processing service implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kp_analysis_toolkit.core.services.batch_processing.models import (
    BatchProcessingConfig,
    BatchResult,
    ErrorHandlingStrategy,
)
from kp_analysis_toolkit.core.services.batch_processing.protocols import (
    BatchProcessingService,
)
from kp_analysis_toolkit.core.services.batch_processing.utils import (
    DefaultConfigExtractor,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService


class DefaultBatchProcessingService(BatchProcessingService):
    """Default implementation of the batch processing service."""

    def __init__(
        self,
        rich_output: RichOutputService,
        file_processing: FileProcessingService,
    ) -> None:
        """Initialize the batch processing service with injected dependencies."""
        self.rich_output = rich_output
        self.file_processing = file_processing
        self.config_extractor = DefaultConfigExtractor()

    def process_files_with_service(
        self,
        file_list: list[Path],
        config_creator: Callable[[Path], object],
        service_method: Callable[[Path, Path], None],
        config: BatchProcessingConfig | None = None,
    ) -> BatchResult:
        """
        Process files using a service method directly.

        Args:
            file_list: List of file paths to process
            config_creator: Function that creates config from file path
            service_method: Service method that accepts (input_file, output_file)
            config: Configuration for batch processing

        Returns:
            BatchResult containing processing statistics and details

        Raises:
            ValueError: If file_list is empty or config_creator fails
            Exception: If error_handling is FAIL_FAST and an error occurs

        """
        if config is None:
            config = BatchProcessingConfig()

        result = BatchResult()
        result.total_files = len(file_list)

        if not file_list:
            self.rich_output.warning("No files to process")
            return result

        self.rich_output.info(
            f"{config.operation_description}: {result.total_files} files",
        )

        # Process files with progress tracking
        result = self._process_file_list(
            file_list,
            config_creator,
            service_method,
            config,
            result,
        )

        # Display summary and handle collected errors
        self._finalize_batch_processing(result, config)

        return result

    def discover_and_process_files(     #noqa: PLR0913
        self,
        base_path: Path,
        file_pattern: str,
        config_creator: Callable[[Path], object],
        service_method: Callable[[Path, Path], None],
        config: BatchProcessingConfig | None = None,
        *,
        recursive: bool = True,
    ) -> BatchResult:
        """
        Discover files by pattern and process them using a service method.

        Args:
            base_path: Base directory to search for files
            file_pattern: Glob pattern for file discovery (e.g., "*.rtf", "*.csv")
            config_creator: Function that creates config from file path
            service_method: Service method that accepts (input_file, output_file)
            config: Configuration for batch processing
            recursive: Whether to search subdirectories recursively

        Returns:
            BatchResult containing processing statistics and details

        Raises:
            ValueError: If no files found matching pattern
            Exception: If error_handling is FAIL_FAST and an error occurs

        """
        if config is None:
            config = BatchProcessingConfig()

        # Auto-generate descriptions if not provided
        if config.operation_description == "Processing files":
            file_type = file_pattern.replace("*.", "").upper()
            config.operation_description = f"Processing {file_type} files"

        if config.progress_description == "Processing files...":
            config.progress_description = f"{config.operation_description}..."

        # Discover files (lazy import to avoid circular dependency)
        from kp_analysis_toolkit.cli.utils.path_helpers import discover_files_by_pattern

        try:
            file_list = discover_files_by_pattern(
                base_path,
                file_pattern,
                recursive=recursive,
            )
        except ValueError as e:
            self.rich_output.error(f"Error discovering files: {e}")
            raise

        if not file_list:
            self.rich_output.warning(
                f"No files matching '{file_pattern}' found in {base_path}",
            )
            return BatchResult()

        return self.process_files_with_service(
            file_list,
            config_creator,
            service_method,
            config,
        )

    def create_file_conversion_success_formatter(
        self,
        operation_verb: str = "Processed",
    ) -> Callable[[Path, object], str]:
        """
        Create a standard success formatter for file conversion operations.

        Args:
            operation_verb: The verb to use in success messages (e.g., "Converted", "Processed")

        Returns:
            Function that formats success messages for batch processing

        """

        def formatter(file_path: Path, file_config: object) -> str:
            """Format success message for file conversion."""
            try:
                _, output_file = self.config_extractor.extract_file_paths(file_config)
            except (AttributeError, TypeError):
                # Fallback if config doesn't have expected structure
                return f"{operation_verb}: {file_path.name}"
            else:
                return f"{operation_verb}: {file_path.name} -> {output_file.name}"

        return formatter

    def _process_file_list(
        self,
        file_list: list[Path],
        config_creator: Callable[[Path], object],
        service_method: Callable[[Path, Path], None],
        config: BatchProcessingConfig,
        result: BatchResult,
    ) -> BatchResult:
        """Process the file list with progress tracking."""
        # Create progress bar
        with self.rich_output.progress() as progress:
            task = progress.add_task(
                config.progress_description,
                total=result.total_files,
            )

            for file_path in file_list:
                self._process_single_file(
                    file_path,
                    config_creator,
                    service_method,
                    config,
                    result,
                )
                progress.update(task, advance=1)

        return result

    def _process_single_file(
        self,
        file_path: Path,
        config_creator: Callable[[Path], object],
        service_method: Callable[[Path, Path], None],
        config: BatchProcessingConfig,
        result: BatchResult,
    ) -> None:
        """Process a single file and handle success/failure."""
        try:
            # Create configuration for this file
            file_config = config_creator(file_path)

            # Extract input and output paths
            input_file, output_file = self.config_extractor.extract_file_paths(
                file_config,
            )

            # Process the file using the service method
            service_method(input_file, output_file)

            # Handle success
            self._handle_file_success(file_path, file_config, config, result)

        except (
            ValueError,
            FileNotFoundError,
            OSError,
            KeyError,
            AttributeError,
            TypeError,
        ) as e:
            self._handle_file_error(file_path, e, config, result)

    def _handle_file_success(
        self,
        file_path: Path,
        file_config: object,
        config: BatchProcessingConfig,
        result: BatchResult,
    ) -> None:
        """Handle successful file processing."""
        if config.success_message_formatter:
            success_msg = config.success_message_formatter(file_path, file_config)
            self.rich_output.success(success_msg)
            result.add_success(file_path, success_msg)
        else:
            self.rich_output.success(f"Processed: {file_path.name}")
            result.add_success(file_path)

    def _handle_file_error(
        self,
        file_path: Path,
        error: Exception,
        config: BatchProcessingConfig,
        result: BatchResult,
    ) -> None:
        """Handle file processing error based on strategy."""
        error_msg = f"Failed to process {file_path.name}: {error}"

        if config.error_handling == ErrorHandlingStrategy.FAIL_FAST:
            self.rich_output.error(error_msg)
            raise error  # Re-raise for fail-fast behavior

        if config.error_handling == ErrorHandlingStrategy.CONTINUE_ON_ERROR:
            self.rich_output.error(error_msg)
            result.add_failure(file_path, error)

        elif config.error_handling == ErrorHandlingStrategy.COLLECT_ERRORS:
            result.add_failure(file_path, error)

    def _finalize_batch_processing(
        self,
        result: BatchResult,
        config: BatchProcessingConfig,
    ) -> None:
        """Display summary and handle collected errors."""
        self._display_batch_summary(result, config.operation_description)

        # Report collected errors if using COLLECT_ERRORS strategy
        if (
            config.error_handling == ErrorHandlingStrategy.COLLECT_ERRORS
            and result.errors
        ):
            self._display_collected_errors(result.errors)

    def _display_batch_summary(
        self,
        result: BatchResult,
        operation_description: str,
    ) -> None:
        """Display batch processing summary."""
        summary_msg = (
            f"{operation_description} complete: "
            f"{result.successful} successful, {result.failed} failed"
        )

        if result.failed == 0:
            self.rich_output.success(summary_msg)
        elif result.successful > 0:
            self.rich_output.info(summary_msg)
        else:
            self.rich_output.error(summary_msg)

        if result.total_files > 0:
            self.rich_output.debug(f"Success rate: {result.success_rate:.1f}%")

    def _display_collected_errors(
        self,
        errors: list[tuple[Path, Exception]],
    ) -> None:
        """Display collected errors from batch processing."""
        self.rich_output.subheader("Processing Errors")

        for file_path, error in errors:
            self.rich_output.error(f"{file_path.name}: {error}")


# END AI-GEN
