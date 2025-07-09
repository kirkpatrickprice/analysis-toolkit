"""File validation utilities for dependency injection integration."""

from pathlib import Path


class PathLibFileValidator:
    """File validator using pathlib for DI integration."""

    def validate_file_exists(self, file_path: Path) -> bool:
        """
        Validate that a file exists and is accessible.

        Args:
            file_path: Path to validate

        Returns:
            True if file exists and is a file, False otherwise

        """
        return file_path.exists() and file_path.is_file()

    def validate_directory_exists(self, dir_path: Path) -> bool:
        """
        Validate that a directory exists and is accessible.

        Args:
            dir_path: Path to validate

        Returns:
            True if directory exists and is a directory, False otherwise

        """
        return dir_path.exists() and dir_path.is_dir()
