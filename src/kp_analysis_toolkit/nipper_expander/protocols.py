"""Protocol definitions for Nipper Expander services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import pandas as pd

    from kp_analysis_toolkit.models.types import PathLike


class RowExpanderService(Protocol):
    """Protocol for data expansion operations."""

    def expand_device_rows(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Expand the finding to one row per device."""
        ...


class NipperExporterService(Protocol):
    """Protocol for Nipper-specific Excel export operations."""

    def export_nipper_results(
        self,
        data_frame: pd.DataFrame,
        output_path: PathLike,
        *,
        sheet_name: str = "Expanded Nipper Results",
        title: str = "Nipper Expanded Report - One row per device/finding",
    ) -> None:
        """Write the expanded DataFrame to an Excel file."""
        ...


class NipperExpanderService(Protocol):
    """Protocol for the main Nipper Expander service orchestration."""

    def process_nipper_csv(self, input_path: PathLike, output_path: PathLike) -> None:
        """
        Process a single Nipper CSV file and export the expanded results to an Excel file.

        Args:
            input_path: Path to the input Nipper CSV file
            output_path: Path to the output Excel file

        Raises:
            FileNotFoundError: Input CSV file not found or output directory doesn't exist
            PermissionError: Insufficient permissions to read input or write output
            ValueError: Invalid CSV data, missing required columns, or data format issues
            pd.errors.ParserError: Malformed CSV file structure
            pd.errors.EmptyDataError: Input CSV file is empty
            UnicodeDecodeError: File encoding problems
            OSError: File system errors (disk space, invalid paths)
            MemoryError: Insufficient memory for processing large datasets

        """
        ...
