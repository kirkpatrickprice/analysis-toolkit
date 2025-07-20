"""Protocol definitions for batch processing services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from kp_analysis_toolkit.core.services.batch_processing.models import (
        BatchProcessingConfig,
        BatchResult,
    )


class BatchProcessingService(Protocol):
    """Protocol for the main batch processing service."""

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
        ...

    def discover_and_process_files(  # noqa: PLR0913
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
        ...

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
        ...


class ConfigExtractor(Protocol):
    """Protocol for extracting file paths from configuration objects."""

    def extract_file_paths(self, config: object) -> tuple[Path, Path]:
        """
        Extract input and output file paths from a config object.

        Args:
            config: Configuration object with input_file and output_file attributes

        Returns:
            Tuple of (input_file_path, output_file_path)

        Raises:
            AttributeError: If config doesn't have required attributes
            TypeError: If file paths are not Path objects

        """
        ...
