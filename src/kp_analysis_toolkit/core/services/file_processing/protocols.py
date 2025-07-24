"""Protocol definitions for file processing service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
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
        timestamp: str | None = None,
    ) -> Path:
        """
        Generate a timestamped file path.

        Args:
            base_path: Base directory for the file
            filename_prefix: Prefix for the filename
            extension: File extension
            timestamp: Timestamp string to include in the filename (default: current timestamp)

        Returns:
            A Path object representing the generated file path

        """
        ...
