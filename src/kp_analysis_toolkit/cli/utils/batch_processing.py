"""Batch processing utilities for CLI commands."""

from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

from pydantic import Field

from kp_analysis_toolkit.cli.common.config_validation import handle_fatal_error
from kp_analysis_toolkit.core.containers.application import container
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.models.types import PathLike


class ErrorHandlingStrategy(Enum):
    """Strategies for handling errors during batch processing."""

    FAIL_FAST = "fail_fast"  # Stop on first error
    CONTINUE_ON_ERROR = "continue_on_error"  # Log error and continue
    COLLECT_ERRORS = "collect_errors"  # Collect all errors and report at end


class BatchResult(KPATBaseModel):
    """Results from batch processing operation."""

    total_files: int = 0
    successful: int = 0
    failed: int = 0
    errors: list[tuple[Path, Exception]] = Field(default_factory=list)
    success_details: list[tuple[Path, str]] = Field(default_factory=list)

    def add_success(self, file_path: Path, message: str = "") -> None:
        """Record a successful file processing."""
        self.successful += 1
        if message:
            self.success_details.append((file_path, message))

    def add_failure(self, file_path: Path, error: Exception) -> None:
        """Record a failed file processing."""
        self.failed += 1
        self.errors.append((file_path, error))

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful / self.total_files) * 100


class FileProcessor(Protocol):
    """Protocol for file processing functions."""

    def __call__(self, file_path: Path) -> Any:  # noqa: ANN401
        """Process a single file and return result or raise exception."""
        ...


class BatchProcessingConfig(KPATBaseModel):
    """Configuration for batch processing operations."""

    operation_description: str = "Processing files"
    progress_description: str = "Processing files..."
    error_handling: ErrorHandlingStrategy = ErrorHandlingStrategy.CONTINUE_ON_ERROR
    success_message_formatter: Callable[[Path, Any], str] | None = None
    rich_output: RichOutputService | None = None


def process_files_batch(
    file_list: list[Path],
    processor: FileProcessor,
    config: BatchProcessingConfig | None = None,
) -> BatchResult:
    """
    Process a list of files with progress tracking and error handling.

    Args:
        file_list: List of file paths to process
        processor: Function that processes a single file
        config: Configuration for batch processing

    Returns:
        BatchResult containing processing statistics and details

    Raises:
        Exception: If error_handling is FAIL_FAST and an error occurs

    Example:
        from dependency_injector.wiring import inject, Provide
        from kp_analysis_toolkit.core.containers.application import ApplicationContainer
        from kp_analysis_toolkit.rtf_to_text.service import RtfToTextService

        @inject
        def process_rtf(
            file_path: Path,
            rtf_service: RtfToTextService = Provide[
                ApplicationContainer.rtf_to_text.rtf_to_text_service
            ]
        ) -> str:
            # Process RTF file using DI service and return output filename
            config = create_rtf_config(file_path)
            rtf_service.convert_file(config.input_file, config.output_file)
            return config.output_file.name

        def format_success(file_path: Path, result: str) -> str:
            return f"Converted: {file_path.name} -> {result}"

        batch_config = BatchProcessingConfig(
            operation_description="Converting RTF files",
            progress_description="Converting RTF files...",
            success_message_formatter=format_success,
        )

        result = process_files_batch(rtf_files, process_rtf, batch_config)

    """
    if config is None:
        config = BatchProcessingConfig()

    if config.rich_output is None:
        config.rich_output = container.core.rich_output()

    result = BatchResult()
    result.total_files = len(file_list)

    if not file_list:
        config.rich_output.warning("No files to process")
        return result

    config.rich_output.info(
        f"{config.operation_description}: {result.total_files} files",
    )

    # Process files with progress tracking
    result = _process_file_list(file_list, processor, config, result)

    # Display summary and handle collected errors
    _finalize_batch_processing(result, config)

    return result


def _process_file_list(
    file_list: list[Path],
    processor: FileProcessor,
    config: BatchProcessingConfig,
    result: BatchResult,
) -> BatchResult:
    """Process the file list with progress tracking."""
    # Ensure rich_output is available
    if config.rich_output is None:
        config.rich_output = container.core.rich_output()

    # Create progress bar
    with config.rich_output.progress() as progress:
        task = progress.add_task(config.progress_description, total=result.total_files)

        for file_path in file_list:
            _process_single_file(file_path, processor, config, result)
            progress.update(task, advance=1)

    return result


def _process_single_file(
    file_path: Path,
    processor: FileProcessor,
    config: BatchProcessingConfig,
    result: BatchResult,
) -> None:
    """Process a single file and handle success/failure."""
    try:
        # Process the file
        process_result = processor(file_path)
        _handle_file_success(file_path, process_result, config, result)

    except (ValueError, FileNotFoundError, OSError, KeyError) as e:
        _handle_file_error(file_path, e, config, result)


def _handle_file_success(
    file_path: Path,
    process_result: Any,  # noqa: ANN401
    config: BatchProcessingConfig,
    result: BatchResult,
) -> None:
    """Handle successful file processing."""
    # Ensure rich_output is available
    if config.rich_output is None:
        config.rich_output = container.core.rich_output()

    if config.success_message_formatter:
        success_msg = config.success_message_formatter(file_path, process_result)
        config.rich_output.success(success_msg)
        result.add_success(file_path, success_msg)
    else:
        config.rich_output.success(f"Processed: {file_path.name}")
        result.add_success(file_path)


def _handle_file_error(
    file_path: Path,
    error: Exception,
    config: BatchProcessingConfig,
    result: BatchResult,
) -> None:
    """Handle file processing error based on strategy."""
    # Ensure rich_output is available
    if config.rich_output is None:
        config.rich_output = container.core.rich_output()

    error_msg = f"Failed to process {file_path.name}: {error}"

    if config.error_handling == ErrorHandlingStrategy.FAIL_FAST:
        handle_fatal_error(error, error_prefix=f"Error processing {file_path.name}")

    elif config.error_handling == ErrorHandlingStrategy.CONTINUE_ON_ERROR:
        config.rich_output.error(error_msg)
        result.add_failure(file_path, error)

    elif config.error_handling == ErrorHandlingStrategy.COLLECT_ERRORS:
        result.add_failure(file_path, error)


def _finalize_batch_processing(
    result: BatchResult,
    config: BatchProcessingConfig,
) -> None:
    """Display summary and handle collected errors."""
    # Ensure rich_output is available
    if config.rich_output is None:
        config.rich_output = container.core.rich_output()

    _display_batch_summary(result, config.operation_description, config.rich_output)

    # Report collected errors if using COLLECT_ERRORS strategy
    if config.error_handling == ErrorHandlingStrategy.COLLECT_ERRORS and result.errors:
        _display_collected_errors(result.errors, config.rich_output)


def _display_batch_summary(
    result: BatchResult,
    operation_description: str,
    rich_output: RichOutputService,
) -> None:
    """Display batch processing summary."""
    summary_msg = (
        f"{operation_description} complete: "
        f"{result.successful} successful, {result.failed} failed"
    )

    if result.failed == 0:
        rich_output.success(summary_msg)
    elif result.successful > 0:
        rich_output.info(summary_msg)
    else:
        rich_output.error(summary_msg)

    if result.total_files > 0:
        rich_output.debug(f"Success rate: {result.success_rate:.1f}%")


def _display_collected_errors(
    errors: list[tuple[Path, Exception]],
    rich_output: RichOutputService,
) -> None:
    """Display collected errors from batch processing."""
    rich_output.subheader("Processing Errors")

    for file_path, error in errors:
        rich_output.error(f"{file_path.name}: {error}")


def discover_and_process_files(
    base_path: PathLike,
    file_pattern: str,
    processor: FileProcessor,
    config: BatchProcessingConfig | None = None,
    *,
    recursive: bool = True,
) -> BatchResult:
    """
    Discover files by pattern and process them in batch.

    Args:
        base_path: Base directory to search for files
        file_pattern: Glob pattern for file discovery (e.g., "*.rtf", "*.csv")
        processor: Function that processes a single file
        config: Configuration for batch processing
        recursive: Whether to search subdirectories recursively

    Returns:
        BatchResult containing processing statistics and details

    Example:
        def process_csv(file_path: Path) -> str:
            # Process CSV file
            return "processed"

        batch_config = BatchProcessingConfig(
            operation_description="Processing CSV files"
        )

        result = discover_and_process_files(
            "./data",
            "*.csv",
            process_csv,
            batch_config,
        )

    """
    if config is None:
        config = BatchProcessingConfig()

    if config.rich_output is None:
        config.rich_output = container.core.rich_output()

    # Auto-generate descriptions if not provided
    if config.operation_description == "Processing files":
        file_type = file_pattern.replace("*.", "").upper()
        config.operation_description = f"Processing {file_type} files"

    if config.progress_description == "Processing files...":
        config.progress_description = f"{config.operation_description}..."

    # Discover files
    try:
        file_processing_service = container.core.file_processing_service()
        file_list = file_processing_service.discover_files_by_pattern(
            base_path=base_path,
            pattern=file_pattern,
            recursive=recursive,
        )
    except ValueError as e:
        handle_fatal_error(e, error_prefix="Error discovering files")

    if not file_list:
        config.rich_output.warning(
            f"No files matching '{file_pattern}' found in {base_path}",
        )
        return BatchResult()

    return process_files_batch(file_list, processor, config)


# Convenience function for RTF-style processing with config creation
def process_files_with_config(
    file_list: list[Path],
    config_creator: Callable[[Path], Any],
    processor: Callable[[Any], Any],
    config: BatchProcessingConfig | None = None,
) -> BatchResult:
    """
    Process files that require configuration object creation.

    This is a specialized version for the common pattern where each file
    needs a configuration object created before processing.

    Args:
        file_list: List of file paths to process
        config_creator: Function that creates config from file path
        processor: Function that processes using the config
        config: Configuration for batch processing

    Returns:
        BatchResult containing processing statistics and details

    Example:
        def create_rtf_config(file_path: Path) -> ProgramConfig:
            return validate_program_config(
                ProgramConfig,
                input_file=file_path,
                source_files_path=file_path.parent,
            )

        def format_rtf_success(file_path: Path, result: tuple) -> str:
            program_config, _ = result
            return f"Converted: {file_path.name} -> {program_config.output_file.name}"

        batch_config = BatchProcessingConfig(
            operation_description="Converting RTF files",
            success_message_formatter=format_rtf_success,
        )

        result = process_files_with_config(
            rtf_files,
            create_rtf_config,
            process_rtf_with_di_service,  # Using DI-based processor
            batch_config,
        )

    """

    def combined_processor(file_path: Path) -> tuple[Any, Any]:
        """Create config and process file, returning both for success message."""
        file_config = config_creator(file_path)
        process_result = processor(file_config)
        return file_config, process_result

    return process_files_batch(file_list, combined_processor, config)
