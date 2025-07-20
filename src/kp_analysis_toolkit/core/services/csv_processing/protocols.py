"""Protocol definitions for CSV processing services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd


class CSVProcessor(Protocol):
    """Protocol for CSV file processing with validation and error handling."""

    def read_csv_file(self, file_path: Path) -> pd.DataFrame:
        """Read and validate CSV file with encoding detection."""
        ...

    def validate_required_columns(
        self,
        df: pd.DataFrame,
        required_columns: list[str],
    ) -> None:
        """Validate that required columns exist in the DataFrame."""
        ...

    def read_and_validate_csv_file(
        self,
        file_path: Path,
        required_columns: list[str],
    ) -> pd.DataFrame:
        """Complete CSV processing pipeline with validation."""
        ...
