"""Discovery services for finding files in a directory based on a pattern."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from kp_analysis_toolkit.core.services.file_processing.protocols import (
    FileDiscoverer,
)

if TYPE_CHECKING:
    from kp_analysis_toolkit.models.types import PathLike


class FileDiscoveryService(FileDiscoverer):
    """Service for discovering files in a directory based on a pattern."""

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
            pattern: Glob pattern to match files (default: "*")
            recursive: If True, search subdirectories recursively (default: False)

        Returns:
            List of Path objects for all matching files

        Raises:
            ValueError: If base_path doesn't exist or is not a directory

        Examples:
            # Find all CSV files in current directory
            csv_files = discover_files_by_pattern("./", "*.csv")

            # Find all text files recursively
            txt_files = discover_files_by_pattern("./data", "*.txt", recursive=True)

        """
        base_path = Path(base_path).resolve()
        if not base_path.exists():
            message: str = f"Path does not exist: {base_path}"
            raise ValueError(message)
        if not base_path.is_dir():
            error_message: str = f"Path is not a directory: {base_path}"
            raise ValueError(error_message)

        if recursive:
            return [path for path in base_path.rglob(pattern) if path.is_file()]
        return [path for path in base_path.glob(pattern) if path.is_file()]
