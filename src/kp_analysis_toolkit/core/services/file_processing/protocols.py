"""Protocol definitions for file processing service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from kp_analysis_toolkit.models.types import PathLike


class EncodingDetector(Protocol):
    """Protocol for file encoding detection."""

    def detect_encoding(self, file_path: Path) -> str | None:
        """
        Detect the encoding of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected encoding name, or None if detection fails

        """
        ...


class HashGenerator(Protocol):
    """Protocol for file hash generation."""

    def generate_hash(self, file_path: Path) -> str:
        """
        Generate a hash for a file.

        Args:
            file_path: Path to the file to hash

        Returns:
            The generated hash as a hexadecimal string

        """
        ...


class FileValidator(Protocol):
    """Protocol for file validation."""

    def validate_file_exists(self, file_path: Path) -> bool:
        """
        Validate that a file exists and is accessible.

        Args:
            file_path: Path to validate

        Returns:
            True if the file exists and is a file, False otherwise

        """
        ...

    def validate_directory_exists(self, dir_path: Path) -> bool:
        """
        Validate that a directory exists and is accessible.

        Args:
            dir_path: Path to validate

        Returns:
            True if the directory exists and is a directory, False otherwise

        """
        ...


class FileDiscoverer(Protocol):
    """Protocol for discovering files in a directory."""

    def discover_files_by_pattern(
        self,
        base_path: PathLike,
        pattern: str = "*",
        *,
        recursive: bool = False,
    ) -> list[Path]:
        """
        Discover files matching a pattern in a directory.

        Args:
            base_path: Directory to search for files
            pattern: Glob pattern to match files
            recursive: If True, search subdirectories recursively (default: False)

        Returns:
            List of Path objects for all matching files

        """
        ...


class PathUtilities(Protocol):
    """Protocol for path utilities."""

    def generate_timestamped_path(
        self,
        base_path: PathLike,
        filename_prefix: str,
        extension: str,
    ) -> Path:
        """
        Generate a timestamped file path.

        Args:
            base_path: Base directory for the file
            filename_prefix: Prefix for the filename
            extension: File extension

        Returns:
            A Path object representing the generated file path

        """
        ...


class ContentStreamer(Protocol):
    """Protocol for streaming file content with targeted access patterns."""

    def get_file_header(self, lines: int = 10) -> list[str]:
        """
        Get the first N lines of the file.

        Args:
            lines: Number of lines to retrieve from the beginning

        Returns:
            List of strings, one per line

        """
        ...

    def stream_pattern_matches(
        self,
        pattern: str,
        *,
        max_matches: int | None = None,
        ignore_case: bool = True,
    ) -> Generator[str, None, None]:
        """
        Stream lines that match a regex pattern.

        Args:
            pattern: Regular expression pattern to match
            max_matches: Maximum number of matches to return (None for unlimited)
            ignore_case: Whether to ignore case in pattern matching

        Yields:
            Lines that match the pattern

        """
        ...

    def stream_section_content(
        self,
        start_pattern: str,
        end_pattern: str | None = None,
        *,
        include_markers: bool = False,
        ignore_case: bool = True,
    ) -> Generator[str, None, None]:
        """
        Stream content between start and end patterns.

        Args:
            start_pattern: Pattern that marks the beginning of the section
            end_pattern: Pattern that marks the end (None means to end of file)
            include_markers: Whether to include the start/end marker lines
            ignore_case: Whether to ignore case in pattern matching

        Yields:
            Lines between the start and end patterns

        """
        ...

    def stream_lines(self) -> Generator[str, None, None]:
        """
        Stream all lines in the file.

        Yields:
            All lines in the file, one at a time

        """
        ...

    def find_first_match(
        self,
        pattern: str,
        *,
        ignore_case: bool = True,
    ) -> str | None:
        """
        Find the first line that matches a pattern.

        Args:
            pattern: Regular expression pattern to match
            ignore_case: Whether to ignore case in pattern matching

        Returns:
            First matching line, or None if no match found

        """
        ...

    def search_multiple_patterns(
        self,
        patterns: dict[str, str],
        *,
        ignore_case: bool = True,
        early_termination: bool = True,
    ) -> dict[str, list[str]]:
        """Search for multiple patterns in a single file pass."""
        ...
