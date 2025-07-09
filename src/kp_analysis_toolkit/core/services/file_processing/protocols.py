"""Protocol definitions for file processing service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path


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
